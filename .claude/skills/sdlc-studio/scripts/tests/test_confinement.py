"""Workspace write-confinement test (CR0015).

The TSD asserts read-only scripts confine writes (contract rule 5), but nothing
exercised it. This snapshots a fixture workspace (paths + content hashes), runs a
read-only script against it, and asserts the tree outside `.local/` is byte
identical afterwards - the script wrote nothing it should not have.
"""
from __future__ import annotations

import ast
import hashlib
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _snapshot(root: Path) -> dict:
    snap = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and ".local" not in p.parts and "__pycache__" not in p.parts:
            snap[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return snap


def _fixture(root: Path) -> None:
    sd = root / "sdlc-studio"
    for sub in ("stories", "epics", "change-requests", "bugs"):
        (sd / sub).mkdir(parents=True)
    (sd / "prd.md").write_text("# PRD\n", encoding="utf-8")
    (sd / "epics" / "EP0001-x.md").write_text("# EP0001: e\n\n> **Status:** Ready\n", encoding="utf-8")
    (sd / "stories" / "US0001-x.md").write_text(
        "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001](../epics/EP0001-x.md)\n\n"
        "## Acceptance Criteria\n\n### AC1: x\n- **Verify:** file scripts/x\n", encoding="utf-8")
    (sd / "stories" / "_index.md").write_text(
        "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")


class ConfinementTests(unittest.TestCase):
    def _assert_read_only(self, argv: list[str]) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            before = _snapshot(root)
            subprocess.run([sys.executable, str(SCRIPTS / argv[0]), *argv[1:]],
                           capture_output=True, cwd=str(root))  # exit code irrelevant
            self.assertEqual(before, _snapshot(root), f"{argv[0]} mutated the workspace outside .local/")

    def test_status_is_read_only(self) -> None:
        self._assert_read_only(["status.py", "pillars"])

    def test_conformance_is_read_only(self) -> None:
        self._assert_read_only(["conformance.py", "check"])

    def test_integrity_is_read_only(self) -> None:
        self._assert_read_only(["integrity.py", "check"])

    def test_reconcile_detect_is_read_only(self) -> None:
        self._assert_read_only(["reconcile.py", "detect", "--scope", "stories"])

    def test_audit_is_read_only(self) -> None:
        self._assert_read_only(["audit.py", "check", "--stories", "Ready"])


class SideEffectConfinementTests(unittest.TestCase):
    def test_ledger_writes_only_its_named_target(self) -> None:
        # A side-effecting script must touch only its named target (here the
        # tranche decisions file), nothing else in the workspace.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            before = _snapshot(root)
            subprocess.run([sys.executable, str(SCRIPTS / "ledger.py"), "record",
                            "--tranche", "T1", "--decision", "x", "--rationale", "y"],
                           capture_output=True, cwd=str(root))
            after = _snapshot(root)
            changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}
            self.assertEqual(changed, {"sdlc-studio/decisions/T1.md"})


# --------------------------------------------------------------------------
# Major-writer confinement snapshots
# --------------------------------------------------------------------------

def _writer_fixture(root: Path, drift: bool = False) -> None:
    """The read-only fixture plus what a writer needs to run: the sibling indexes,
    a real file for `Affects` to resolve against, and a groomed story.

    `drift` leaves the story file ahead of its index row, so `reconcile apply` has
    a fix to make. Without drift it writes nothing and the snapshot proves nothing.
    """
    _fixture(root)
    sd = root / "sdlc-studio"
    for sub in ("rfcs", "retros", "reviews", "handoffs", "plans"):
        (sd / sub).mkdir(parents=True, exist_ok=True)
    (root / "scripts").mkdir(exist_ok=True)
    (root / "scripts" / "x.py").write_text("# a real path for Affects to resolve\n", encoding="utf-8")
    status = "In Progress" if drift else "Ready"
    (sd / "stories" / "US0001-x.md").write_text(
        f"# US0001: s\n\n> **Status:** {status}\n"
        "> **Epic:** [EP0001](../epics/EP0001-x.md)\n> **Points:** 2\n"
        "> **Affects:** scripts/x.py\n\n"
        "## Acceptance Criteria\n\n### AC1: x\n- **Verify:** file scripts/x.py\n", encoding="utf-8")
    for sub, hdr in (("bugs", "Bugs"), ("change-requests", "Change Requests"),
                     ("rfcs", "RFCs"), ("retros", "Retros"),
                     ("reviews", "Reviews"), ("handoffs", "Handoffs")):
        (sd / sub / "_index.md").write_text(
            f"# {hdr}\n\n| ID | Title | Status |\n| --- | --- | --- |\n", encoding="utf-8")
    (sd / "epics" / "_index.md").write_text(
        "# Epics\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [EP0001](EP0001-x.md) | e | Ready |\n", encoding="utf-8")
    (sd / "retros" / "RETRO0001-probe.md").write_text(
        "# RETRO0001: probe\n\n> **Status:** Complete\n\n## Lessons\n\n"
        "- A lesson worth keeping. It carries a second sentence so the title cuts cleanly.\n",
        encoding="utf-8")
    (sd / "retros" / "_index.md").write_text(
        "# Retros\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [RETRO0001](RETRO0001-probe.md) | probe | Complete |\n", encoding="utf-8")


@dataclass(frozen=True)
class WriterCase:
    """One writer, the command that drives it, and the paths it is allowed to touch.

    `targets` are fnmatch patterns (dated evidence logs carry the day in the name).
    A writer whose whole output lands in `.local/` declares `local_target` instead:
    the snapshot cannot see that tree, so without it an early exit would look
    identical to a clean run.
    """

    argv: tuple[str, ...]
    targets: frozenset[str] = field(default_factory=frozenset)
    local_target: str | None = None
    drift: bool = False


#: Every writer with a confinement snapshot. The roster sweep reads this as the
#: covered set, so a writer is "covered" only by having a case that actually runs it.
WRITER_CASES: dict[str, WriterCase] = {
    "artifact.py": WriterCase(
        argv=("new", "--type", "bug", "--title", "probe bug", "--severity", "Low",
              "--points", "1", "--affects", "scripts/x.py"),
        targets=frozenset({"sdlc-studio/bugs/BG0001-probe-bug.md", "sdlc-studio/bugs/_index.md"}),
    ),
    "file_finding.py": WriterCase(
        argv=("file", "--type", "bug", "--title", "probe finding", "--summary", "a probe finding",
              "--severity", "Low", "--points", "1", "--affects", "scripts/x.py",
              "--steps", "s", "--fix", "f"),
        targets=frozenset({"sdlc-studio/bugs/BG0001-probe-finding.md", "sdlc-studio/bugs/_index.md"}),
    ),
    "transition.py": WriterCase(
        argv=("set", "--id", "US0001", "--status", "In Progress", "--triaged-by", "tester;human;v1"),
        targets=frozenset({"sdlc-studio/stories/US0001-x.md", "sdlc-studio/stories/_index.md"}),
    ),
    "reconcile.py": WriterCase(
        argv=("apply", "--scope", "stories"),
        targets=frozenset({"sdlc-studio/stories/_index.md"}),
        drift=True,
    ),
    "telemetry.py": WriterCase(
        argv=("record", "--id", "US0001", "--type", "story", "--tokens", "10"),
        targets=frozenset({"sdlc-studio/retros/evidence/actuals-*.jsonl"}),
    ),
    "audit_cost.py": WriterCase(
        argv=("record", "--lenses", "7", "--rounds", "3", "--votes", "3",
              "--est-agents", "217", "--est-tokens", "7800000",
              "--actual-agents", "265", "--actual-tokens", "12400000"),
        targets=frozenset({"sdlc-studio/retros/evidence/audit-cost-*.jsonl"}),
    ),
    "critic.py": WriterCase(
        argv=("record", "--unit", "US0001", "--verdict", "approve",
              "--reviewer", "r", "--author", "a"),
        targets=frozenset({"sdlc-studio/reviews/critic-verdicts.md"}),
    ),
    "decisions.py": WriterCase(
        argv=("add", "--decision", "d", "--rationale", "r"),
        targets=frozenset({"sdlc-studio/decisions.md"}),
    ),
    "ledger.py": WriterCase(
        argv=("record", "--tranche", "T1", "--decision", "x", "--rationale", "y"),
        targets=frozenset({"sdlc-studio/decisions/T1.md"}),
    ),
    "handoff.py": WriterCase(
        argv=("generate", "--title", "probe run", "--outcome", "goal-reached", "--id", "US0001"),
        targets=frozenset({"sdlc-studio/handoffs/HO0001-probe-run.md",
                           "sdlc-studio/handoffs/_index.md"}),
    ),
    "retro.py": WriterCase(
        argv=("extract", "--id", "RETRO0001"),
        local_target="sdlc-studio/.local/lessons.md",
    ),
    "sprint.py": WriterCase(
        argv=("plan", "--write", "--stories", "Ready", "--no-fetch",
              "--sprint-goal", "probe the confinement"),
        targets=frozenset({"sdlc-studio/retros/evidence/forecasts-*.jsonl"}),
        local_target="sdlc-studio/.local/sprint-plan.json",
    ),
}


class MajorWriterConfinementTests(unittest.TestCase):
    """Each shipped writer touches its named target and nothing else.

    Both directions are asserted. Extra paths mean the writer escaped its target;
    a missing target means the writer no-opped, and a snapshot over a writer that
    did nothing is the vacuous pass this suite exists to prevent.
    """

    def _assert_confined(self, script: str, case: WriterCase) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _writer_fixture(root, drift=case.drift)
            before = _snapshot(root)
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / script), *case.argv],
                capture_output=True, cwd=str(root), text=True)
            self.assertEqual(
                proc.returncode, 0,
                f"{script} did not run, so its snapshot proves nothing:\n"
                f"{(proc.stderr or proc.stdout).strip()[:600]}")
            after = _snapshot(root)
            changed = {k for k in set(before) | set(after) if before.get(k) != after.get(k)}

            escaped = sorted(p for p in changed
                             if not any(fnmatch(p, pat) for pat in case.targets))
            self.assertEqual(escaped, [], f"{script} wrote outside its named target: {escaped}")

            missing = sorted(pat for pat in case.targets
                             if not any(fnmatch(p, pat) for p in changed))
            self.assertEqual(missing, [], f"{script} never wrote its named target: {missing}")

            if case.local_target is not None:
                self.assertTrue(
                    (root / case.local_target).is_file(),
                    f"{script} left {case.local_target} unwritten, so the untouched "
                    "workspace is inaction rather than confinement")


def _bind_writer_cases() -> None:
    """One test method per writer, so a failure names the writer that escaped."""
    for script, case in WRITER_CASES.items():
        def method(self, script=script, case=case):
            self._assert_confined(script, case)

        method.__name__ = f"test_{script[:-3]}_confines_its_writes"
        setattr(MajorWriterConfinementTests, method.__name__, method)


_bind_writer_cases()


# --------------------------------------------------------------------------
# Roster sweep: a new writer cannot arrive without a snapshot
# --------------------------------------------------------------------------

#: Content writes on a path object.
_CONTENT_WRITES = frozenset({"write_text", "write_bytes"})
#: Shared write helpers in `lib/`. Most scripts never call `write_text` directly,
#: so a detector that looked only for the builtins would miss nearly every writer.
_WRITE_HELPERS = frozenset({"atomic_write", "roll_jsonl", "insert_after_status", "write_decomposed"})
#: Filesystem mutators that take a single positional argument as a method. The arity
#: is what separates `path.replace(other)` from `text.replace(old, new)`.
_UNARY_MUTATORS = frozenset({"replace", "rename", "unlink", "remove"})
_SHUTIL_MUTATORS = frozenset({"copy", "copy2", "copyfile", "copytree", "move", "rmtree"})


#: The characters a Python file mode is built from. A mode is short and drawn only from these,
#: which is what separates it from a literal path in the same argument position.
_MODE_CHARS = set("rwaxbt+U")


def _looks_like_mode(value: object) -> bool:
    """True for a string shaped like a file mode (`'w'`, `'rb'`, `'a+'`), false for a path.

    Needed because the mode's argument position depends on the call form, so both positions
    are examined and `open('notes.md', 'w')` must not read its literal path as a mode.
    """
    return (isinstance(value, str) and 0 < len(value) <= 4
            and set(value) <= _MODE_CHARS)


def _write_surface(source: str) -> set[str]:
    """The write calls a module makes, by name. Empty means no write surface.

    Deliberately over-inclusive: a false positive costs one allowlist line, whereas
    a false negative is a writer that slips past the sweep unnoticed.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name is None:
            continue
        if name in _CONTENT_WRITES or name in _WRITE_HELPERS or name in _SHUTIL_MUTATORS:
            found.add(name)
        if (isinstance(func, ast.Attribute) and name in _UNARY_MUTATORS
                and len(node.args) <= 1 and not node.keywords):
            found.add(name)
        if name == "open":
            mode = None
            # The mode sits at a different argument depending on the call:
            #   open(p, 'a')        - the builtin takes the path first, so mode is args[1]
            #   path.open('a')      - the Path method is bound to its path, so mode is args[0]
            #   io.open(p, 'a')     - an attribute call that is NOT a bound path: args[1] again
            # Keying on the call form alone gets the third case wrong, so BOTH positions are
            # read. Taking the first STRING argument would break `open('notes.md', 'w')`,
            # whose args[0] is a literal path, so only a mode-shaped value counts.
            #
            # A WRITE mode wins outright; anything else keeps looking. Breaking on the first
            # mode-shaped value instead lost `open('rt', 'w')` - args[0] is mode-shaped but
            # carries no write character, so the real mode at args[1] was never examined and a
            # demonstrable write reported an EMPTY surface. That is the same failure as the
            # bug this detector was fixed for. Over-inclusion is safe here and under-inclusion
            # is not: `open('txt', 'w')` yielding `open:txt` still reports a write surface and
            # still catches the module, which is all the sweep needs.
            for idx in (0, 1):
                if len(node.args) > idx and isinstance(node.args[idx], ast.Constant) \
                        and _looks_like_mode(node.args[idx].value):
                    mode = node.args[idx].value
                    if any(c in mode for c in "wax+"):
                        break
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = kw.value.value
            if isinstance(mode, str) and any(c in mode for c in "wax+"):
                found.add(f"open:{mode}")
    return found


def _writers_on_disk() -> dict[str, set[str]]:
    return {p.name: surface for p in sorted(SCRIPTS.glob("*.py"))
            if (surface := _write_surface(p.read_text(encoding="utf-8")))}


#: Writers deliberately without a confinement snapshot, each with the reason.
#: This is the only way past the sweep, and it is a debt list: an entry here says
#: the writer is unproven, not that it is safe.
CONFINEMENT_ALLOWLIST: dict[str, str] = {
    "init.py": "seeds a whole project tree, so every path it writes is its target",
    "project_upgrade.py": "rewrites the tree it migrates; covered by the upgrade suite",
    "migrate_v3.py": "renames artefacts wholesale as its purpose",
    "archive.py": "moves index rows between live and archive indexes",
    "refine.py": "rewrites the artefacts it decomposes",
    "triage.py": "rewrites the artefacts it dispositions",
    "rfc.py": "writes the RFC it is asked to amend",
    "lessons.py": "writes the lessons store it owns",
    "digest.py": "writes the digest it owns",
    "changelog.py": "writes the changelog it owns",
    "provenance.py": "writes the provenance record it owns",
    "close_owed.py": "writes the close-owed report it owns",
    "loop_guard.py": "writes the loop-guard state it owns",
    "resume.py": "writes the resume record it owns",
    "review_prep.py": "writes the review-prep record it owns",
    "plan_review.py": "writes the plan-review record it owns",
    "repair_plan.py": "writes the repair-plan record it owns under .local/repair-plans/",
    "plan.py": "moves plan files between the live and archived plan directories",
    "persona_gen.py": "writes the personas it generates",
    "persona_resolve.py": "writes the resolved persona record",
    "backfill_authorship.py": "stamps authorship across artefacts by design",
    "lite_profile.py": "writes the profile it owns",
    "command_audit.py": "writes the command-audit report it owns",
    "deploy.py": "writes deploy readiness output it owns",
    "github_sync.py": "writes the sync record it owns",
    "repo_map.py": "writes the repo map under .local/",
    "version_check.py": "writes the version-check record it owns",
    "triage_noise.py": "writes the triage-noise report it owns",
    "triage_sampling.py": "writes the triage-sampling report it owns",
    "conformance.py": "removes only its own scratch file; snapshotted read-only above",
    "mutation.py": "mutates a working copy under a scratch tree by design",
    "pvd.py": "writes scratch artefacts under .local/",
    "verify_ac.py": "copies the tree under test into a scratch dir by design",
}


class ConfinementRosterSweepTests(unittest.TestCase):
    """A writer arriving without a snapshot fails here, by name.

    The roster is read off disk rather than pinned, so this stays true as scripts
    are added. The detector is self-tested below: a sweep whose detector silently
    stopped detecting would pass over every writer in the tree.
    """

    def test_detector_finds_a_direct_write(self) -> None:
        self.assertEqual(_write_surface("p.write_text('x')"), {"write_text"})

    def test_detector_finds_a_shared_helper_write(self) -> None:
        # Most writers only ever call the helper, so this is the load-bearing case.
        self.assertEqual(_write_surface("sdlc_md.atomic_write(p, 'x')"), {"atomic_write"})

    def test_detector_finds_an_open_for_writing(self) -> None:
        self.assertEqual(_write_surface("open(p, 'w')"), {"open:w"})

    def test_detector_finds_a_path_open_for_writing(self) -> None:
        # The Path method form puts the mode at args[0], not args[1] as the builtin
        # does. Reading only args[1] reports NO write surface for a module that
        # demonstrably appends, and an uncovered writer then passes the sweep silently.
        self.assertEqual(_write_surface("with p.open('a') as fh:\n    fh.write(1)"), {"open:a"})

    def test_detector_finds_a_path_open_with_a_keyword_mode(self) -> None:
        self.assertEqual(_write_surface("p.open(mode='w')"), {"open:w"})

    def test_detector_finds_a_module_qualified_open_for_writing(self) -> None:
        # io.open / codecs.open are ATTRIBUTE calls that are not bound to a path, so their
        # mode is at args[1] like the builtin's. Keying the index on the call form alone
        # missed these - a new blind spot introduced by the fix for the Path form.
        self.assertEqual(_write_surface("io.open(p, 'w')"), {"open:w"})
        self.assertEqual(_write_surface("codecs.open(p, 'a')"), {"open:a"})

    def test_detector_keeps_looking_past_a_mode_shaped_path_with_no_write_char(self) -> None:
        # A path of 1-4 characters drawn only from the non-write mode chars (r, b, t, U) is
        # mode-SHAPED. Breaking on it left the real mode at args[1] unread, so a write
        # reported an empty surface - under-inclusion, the one direction that actually bites.
        self.assertEqual(_write_surface("open('rt', 'w')"), {"open:w"})
        self.assertEqual(_write_surface("open('bt', 'a')"), {"open:a"})
        self.assertEqual(_write_surface("open('rb', 'w')"), {"open:w"})

    def test_detector_does_not_read_a_literal_path_as_a_mode(self) -> None:
        # Reading both argument positions must not turn `open('notes.md', 'w')` into a
        # missed write by taking args[0] as the mode.
        self.assertEqual(_write_surface("open('notes.md', 'w')"), {"open:w"})
        self.assertEqual(_write_surface("open('notes.md')"), set())

    def test_detector_ignores_a_path_open_for_reading(self) -> None:
        # The over-inclusive principle stops at modes that cannot write: a read is a read
        # in either form, and flagging it would cost an allowlist line for nothing.
        self.assertEqual(_write_surface("p.open('r')"), set())

    def test_detector_ignores_reads_and_string_replace(self) -> None:
        self.assertEqual(_write_surface("t = p.read_text().replace('a', 'b')\nopen(p)"), set())

    def test_roster_is_not_empty(self) -> None:
        # A detector returning nothing would make every assertion below vacuously true.
        roster = _writers_on_disk()
        self.assertGreater(len(roster), 20, "the write detector has stopped detecting")
        for known in ("artifact.py", "ledger.py", "transition.py"):
            self.assertIn(known, roster, f"{known} writes, but the detector missed it")

    def test_every_writer_is_covered_or_allowlisted(self) -> None:
        roster = _writers_on_disk()
        uncovered = sorted(set(roster) - set(WRITER_CASES) - set(CONFINEMENT_ALLOWLIST))
        self.assertEqual(
            uncovered, [],
            "these scripts write to the workspace with no confinement snapshot: "
            f"{uncovered}. Add a case to WRITER_CASES, or an entry to "
            "CONFINEMENT_ALLOWLIST saying why it is exempt.")

    def test_covered_writers_still_write(self) -> None:
        # A case naming a script that no longer writes is dead weight the sweep hides behind.
        roster = _writers_on_disk()
        stale = sorted(set(WRITER_CASES) - set(roster))
        self.assertEqual(stale, [], f"WRITER_CASES names scripts with no write surface: {stale}")

    def test_allowlist_has_no_rotted_entries(self) -> None:
        roster = _writers_on_disk()
        stale = sorted(set(CONFINEMENT_ALLOWLIST) - set(roster))
        self.assertEqual(stale, [], f"allowlisted scripts no longer write: {stale}")

    def test_allowlist_entries_carry_a_reason(self) -> None:
        blank = sorted(k for k, v in CONFINEMENT_ALLOWLIST.items() if not v.strip())
        self.assertEqual(blank, [], f"allowlist entries without a reason: {blank}")


if __name__ == "__main__":
    unittest.main()
