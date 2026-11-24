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
    # A finding whose provenance PROSE names an audit run, for the backfill writer's case.
    # Deliberately a CR, not a bug: the artifact.py and file_finding.py cases both MINT a bug and
    # declare `BG0001` as their target, so seeding the bugs directory would push their ids up and
    # break two unrelated cases. Nothing here mints a CR.
    (sd / "change-requests" / "CR0009-x.md").write_text(
        "# CR-0009: a finding from an audit\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
        "> **Raised-by:** Claude (adversarial audit wf_fixture1); agent\n", encoding="utf-8")
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

    def test_readiness_is_read_only(self) -> None:
        self._assert_read_only(["readiness.py", "check", "--stories", "Ready"])

    def test_validate_is_read_only(self) -> None:
        self._assert_read_only(["validate.py", "check"])

    def test_next_id_is_read_only(self) -> None:
        self._assert_read_only(["next_id.py", "scan", "--type", "story"])

    def test_critic_show_is_read_only(self) -> None:
        self._assert_read_only(["critic.py", "show"])


def _full_snapshot(root: Path) -> dict:
    """Every file under `root` by content hash, `.local/` included, and every directory by name,
    so a folder made and left empty is a change too."""
    snap = {}
    for p in sorted(root.rglob("*")):
        if "__pycache__" in p.parts:
            continue
        rel = str(p.relative_to(root))
        snap[rel + "/" if p.is_dir() else rel] = (
            "(directory)" if p.is_dir() else hashlib.sha256(p.read_bytes()).hexdigest())
    return snap


class WritingHelperConfinementTests(unittest.TestCase):
    """BG1531: `critic brief`, `gate` and `review_prep close` are not read-only; each writes
    only the state the TRD (section 5 rule 5) names for it."""

    def _changed(self, argv: list[str], setup=None) -> tuple[set[str], int]:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            if setup:
                setup(root)
            before = _full_snapshot(root)
            done = subprocess.run([sys.executable, str(SCRIPTS / argv[0]), *argv[1:]],
                                  capture_output=True, text=True, cwd=str(root))
            after = _full_snapshot(root)
        return {k for k in set(before) | set(after) if before.get(k) != after.get(k)}, \
            done.returncode

    def test_each_writing_helper_writes_only_its_named_state(self) -> None:
        """Mutants: a helper writing outside its named paths (a `LATEST.md` from `prep`, a
        tracked file from `brief`, a stray file under `.local/` from `close`); a named path the
        helper no longer writes (`close` adding no index row, or no `LATEST.md` given
        `--latest-body`, or not backfilling a meta index that lacks a record)."""
        def review(root: Path) -> None:
            (root / "sdlc-studio" / "reviews").mkdir()
            (root / "sdlc-studio" / "reviews" / "RV0001-x.md").write_text(
                "# RV0001: a review\n\n> **Status:** Complete\n", encoding="utf-8")

        def unindexed_retro(root: Path) -> None:
            review(root)
            (root / "sdlc-studio" / "retros").mkdir()
            (root / "sdlc-studio" / "retros" / "RETRO0001-x.md").write_text(
                "# RETRO0001: a retro\n\n> **Status:** Complete\n", encoding="utf-8")

        brief, rc = self._changed(["critic.py", "brief", "--unit", "US0001", "--seat",
                                   "engineering"])
        self.assertEqual(0, rc)
        self.assertEqual({"sdlc-studio/.local/briefs.jsonl", "sdlc-studio/.local/",
                          "sdlc-studio/reviews/", "sdlc-studio/reviews/verdicts/",
                          "sdlc-studio/reviews/verdicts/US0001/"}, brief)

        gate, _ = self._changed(["gate.py"])
        named = {"sdlc-studio/.local/", "sdlc-studio/.local/gate-cost.json",
                 "sdlc-studio/.local/gate-suite-verdict.json",
                 "sdlc-studio/.local/boundary-suite-last.log",
                 "sdlc-studio/.local/gate-timings.json"}
        self.assertLessEqual(gate, named)
        self.assertIn("sdlc-studio/.local/gate-cost.json", gate)

        prep, rc = self._changed(["review_prep.py", "prep"], review)
        self.assertEqual((set(), 0), (prep, rc))

        # The state file, and through `reconcile.apply_meta` the `_index.md` of each meta folder
        # holding a record its index lacks: the review's own, and here a retro's.
        state = {"sdlc-studio/.local/", "sdlc-studio/.local/review-state.json",
                 "sdlc-studio/reviews/_index.md"}
        close, rc = self._changed(["review_prep.py", "close", "--rv", "RV0001"], review)
        self.assertEqual((state, 0), (close, rc))
        close, rc = self._changed(["review_prep.py", "close", "--rv", "RV0001"], unindexed_retro)
        self.assertEqual((state | {"sdlc-studio/retros/_index.md"}, 0), (close, rc))
        def anchor_body(root: Path) -> None:
            review(root)
            (root / "latest.md").write_text("See RV0001.\n", encoding="utf-8")

        close, rc = self._changed(["review_prep.py", "close", "--rv", "RV0001", "--latest-body",
                                   "latest.md"], anchor_body)
        self.assertEqual((state | {"sdlc-studio/reviews/LATEST.md"}, 0), (close, rc))


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
    identical to a clean run. `seed` adds `(path, text)` files to the fixture before the
    snapshot, for a writer whose input the shared fixture does not carry.
    """

    argv: tuple[str, ...]
    targets: frozenset[str] = field(default_factory=frozenset)
    local_target: str | None = None
    drift: bool = False
    seed: tuple[tuple[str, str], ...] = ()


#: A generated engineering seat card still carrying its provisional stamp, clean against the
#: persona standard (its Evidence cites the fixture's US0001), for `persona_review.py record`.
_PROVISIONAL_SEAT = (
    "<!-- role: engineering -->\n"
    "<!-- provenance: generated provisional-unverified hash=sha256:0123456789abcdef -->\n"
    "# Cal Dorn - engineering seat\n\n## Who They Are\n\nCal reviews the work.\n\n"
    "## Lens\n\n- x\n\n## Pushes Back When\n\n- x\n\n## Shadow\n\nx\n\n"
    "## Evidence\n\n- US0001: the story this card was drawn from\n")


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
    "backfill_audit_runs.py": WriterCase(
        # A real confinement case rather than an allowlist entry: this script rewrites tracked
        # ARTEFACTS, which is the write worth confining. The fixture story carries a run id in
        # its Raised-by line, so `apply` stamps that one file and seeds the register - and
        # nothing else in the tree may move.
        argv=("apply",),
        targets=frozenset({"sdlc-studio/change-requests/CR0009-x.md",
                           "sdlc-studio/retros/evidence/audit-cost-*.jsonl"}),
    ),
    "audit_cost.py": WriterCase(
        argv=("record", "--lenses", "7", "--rounds", "3", "--votes", "3",
              "--est-agents", "217", "--est-tokens", "7800000",
              "--actual-agents", "265", "--actual-tokens", "12400000"),
        targets=frozenset({"sdlc-studio/retros/evidence/audit-cost-*.jsonl"}),
    ),
    "critic.py": WriterCase(
        # `--brief` is required to record a verdict at all now (US0578); this case is about
        # WHERE critic writes, so it supplies one as a briefed reviewer would.
        argv=("record", "--unit", "US0001", "--verdict", "approve",
              "--reviewer", "r", "--author", "a", "--brief", "abcdef123456"),
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
    "retro.py": WriterCase(
        # BG0989: the project lessons log is committed, beside the summary built from it.
        argv=("extract", "--id", "RETRO0001"),
        targets=frozenset({"sdlc-studio/retros/LESSONS.md"}),
    ),
    "gate.py": WriterCase(
        # The gate is otherwise read-only by design (a pre-commit hook runs it). Its two
        # writes are runtime state under `.local/`: the suite verdict an unchanged surface
        # reuses, and the cost baseline the next run states its direction against. Neither
        # may reach a tracked file - a gate that edits the tree it is judging is not a gate.
        argv=("--record-suite-verdict", "RUN-PROBE"),
        local_target="sdlc-studio/.local/gate-suite-verdict.json",
    ),
    "sprint.py": WriterCase(
        argv=("plan", "--write", "--stories", "Ready", "--no-fetch",
              "--sprint-goal", "probe the confinement"),
        targets=frozenset({"sdlc-studio/retros/evidence/forecasts-*.jsonl"}),
        local_target="sdlc-studio/.local/sprint-plan.json",
    ),
    "persona_review.py": WriterCase(
        # `record` writes the review ledger and, on a PASS of a provisional card, that card's
        # provenance line; `brief` and `check` are read-only. A PASS by another seat touches
        # both, and nothing else in the tree may move.
        argv=("record", "--card", "sdlc-studio/personas/seats/engineering.md",
              "--outcome", "pass", "--reviewer", "Lena Marsh (product)", "--run-by", "Dana Fox"),
        targets=frozenset({"sdlc-studio/reviews/persona-reviews.md",
                           "sdlc-studio/personas/seats/engineering.md"}),
        seed=(("sdlc-studio/personas/seats/engineering.md", _PROVISIONAL_SEAT),),
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
            for rel, text in case.seed:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(text, encoding="utf-8")
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
#: The names in the set above that a MAINSTREAM non-filesystem type also carries at the same
#: arity, so arity cannot separate them: `list.remove(x)` and `set.remove(x)` are exactly as
#: shaped as `os.remove(p)`. For these, and ONLY these, the receiver must be a filesystem
#: module. Over-inclusion is the right default everywhere else in this detector - a false
#: positive costs one allowlist line - but here it cost a read-only module a place on the
#: writer roster, and the remedy the sweep offers is an allowlist entry, so an exemption
#: claiming a write that does not exist would be recorded as if it were real. The roster's
#: meaning erodes one honest-looking line at a time (BG0454).
_AMBIGUOUS_MUTATORS = frozenset({"remove"})
#: The modules whose `remove` IS a filesystem call.
_FS_MODULES = frozenset({"os", "shutil", "pathlib"})
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


def _fs_receiver(node: ast.AST) -> bool:
    """True when this receiver is a filesystem module - `os`, `shutil`, `pathlib`, or a dotted
    form ending in one. Used only for the names a mainstream non-filesystem type shares at the
    same arity, so `ids.remove(uid)` on a plain list is not read as `os.remove`."""
    if isinstance(node, ast.Name):
        return node.id in _FS_MODULES
    if isinstance(node, ast.Attribute):
        return node.attr in _FS_MODULES
    return False


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
                and len(node.args) <= 1 and not node.keywords
                and (name not in _AMBIGUOUS_MUTATORS or _fs_receiver(func.value))):
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
    "engagement_floor.py": ("with --write-trailers, writes only the commit-message file git hands "
                            "the commit-msg hook, never a workspace artefact; the hook tests pin it"),
    "init.py": "seeds a whole project tree, so every path it writes is its target",
    "project_upgrade.py": "rewrites the tree it migrates; covered by the upgrade suite",
    "migrate_v3.py": "renames artefacts wholesale as its purpose",
    "migrate.py": ("removes retired tags and keys from the DoR/DoD and .config.yaml it upgrades, "
                   "line by line; test_lean_migrate_config holds that the first --apply changes "
                   "those files and .version only, and a second changes nothing"),
    "archive.py": "moves index rows between live and archive indexes",
    "refine.py": "rewrites the artefacts it decomposes",
    "triage.py": "rewrites the artefacts it dispositions",
    "rfc.py": "writes the RFC it is asked to amend",
    "lessons.py": "writes the lessons store it owns",
    "persona_memory.py": ("writes only the memory files it owns, sdlc-studio/personas/memory/"
                          "<persona>.md, each through atomic_write, and refuses a write the "
                          "repository would ignore; test_persona_memory_store holds that a "
                          "refused add writes no file"),
    "docgen.py": "writes only between generation markers in the targets it owns, and refuses any file that carries none - the marker is the confinement",
    "digest.py": "writes the digest it owns",
    "sprint_report.py": ("writes the report of record it owns - the JSON and its Markdown twin "
                         "under sdlc-studio/reports/, both named by an id the shared allocator "
                         "minted - plus the CI answer it caches under .local/ so a re-derivation "
                         "is offline rather than a second network call with a different answer. "
                         "Not a WriterCase because a report cannot be built without a run "
                         "record and a retro, and this fixture seeds neither"),
    "changelog.py": "writes the changelog it owns",
    "release_cut.py": "writes the CHANGELOG section it cuts (via changelog.compose) and the "
                      "release-gate green marker it owns under .local",
    "evidence_pack.py": ("writes only the evidence pack it builds, sdlc-studio/reports/"
                         "evidence-pack-<version>.md, plus a scratch copy of the committed "
                         "verdict ledger in a temporary directory it removes. Not a WriterCase "
                         "because a pack needs a git repository of committed signed reports, "
                         "which this fixture is not; test_evidence_pack_build snapshots its own "
                         "fixture around a build and holds the pack to be the one file changed"),
    "escape.py": ("with trace --confirm, writes only the Escaped-via and Escaped-verdict lines "
                  "of the bug it traces. Not a WriterCase because a trace needs a git repository "
                  "with a tagged release, which this fixture is not; test_escape_trace snapshots "
                  "its own fixture around a confirm and holds the bug to be the one file "
                  "changed. With to-class, writes only sdlc-studio/lessons.jsonl, through "
                  "lessons.class_add; test_escape_class snapshots its fixture around a to-class "
                  "and holds the store to be the one file changed"),
    "provenance.py": "writes the provenance record it owns",
    "close_owed.py": "writes the close-owed report it owns",
    "loop_guard.py": "writes the loop-guard state it owns",
    "resume.py": "writes the resume record it owns",
    "review_prep.py": "writes the review-prep record it owns",
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

    def test_a_list_remove_is_not_a_filesystem_write(self) -> None:
        """BG0454. `remove` keyed on the bare attribute name, so `ids.remove(uid)` on a plain
        list reported the write surface `{'remove'}` and a read-only module was censused onto
        the writer roster. The remedy the sweep offers is an allowlist entry - and an entry for
        a module that writes nothing is a false exemption that reads exactly like a real one,
        so the roster's meaning erodes one honest-looking line at a time."""
        self.assertEqual(_write_surface("ids = [1]\nids.remove(1)"), set())
        self.assertEqual(_write_surface("seen = set()\nseen.remove(x)"), set())

    def test_a_QUALIFIED_remove_is_still_detected(self) -> None:
        """The control that keeps the narrowing honest: over-inclusion is the right default for
        this detector, and relaxing it for one name must not lose the real filesystem call."""
        self.assertEqual(_write_surface("import os\nos.remove(p)"), {"remove"})
        self.assertEqual(_write_surface("import shutil\nshutil.rmtree(p)"), {"rmtree"})
        self.assertEqual(_write_surface("p.unlink()"), {"unlink"},
                         "`unlink` has no mainstream non-filesystem meaning and must stay "
                         "over-included")

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


# --------------------------------------------------------------------------
# Shared-file sweep: a tracked file rewritten whole goes through atomic_write
# --------------------------------------------------------------------------

#: The kinds of target a rewrite site may have. SCRATCH is a temporary directory or scratch copy
#: the call made; UNTRACKED is under a gitignored `.local/`, or a directory the operator names for
#: an export; NEW creates a file only where none exists, so a torn write loses no previous
#: content; OUTSIDE rewrites a tracked file whole and is a writer TRD §5 rule 5 lists as left
#: outside the atomic-write guarantee by design, with its reason.
SCRATCH, UNTRACKED, NEW, OUTSIDE = "scratch", "untracked", "new", "outside"

#: Every rewrite site in the shipped scripts (`_rewrite_sites`) but those in `NOT_YET_MOVED`, as
#: `<script>::<function>::<target>`, with the kind of its target and why. A shared file, any
#: tracked workspace file a script rewrites whole, is rewritten through `sdlc_md.atomic_write`,
#: so no site writing one is here except as OUTSIDE.
SHARED_WRITE_ALLOWLIST: dict[str, tuple[str, str]] = {
    "critic.py::_replay_author_mutants::edits": (SCRATCH, "the edits file in a mkdtemp directory"),
    "critic.py::_set_aside::Path(scratch) / name": (SCRATCH, "a merge side in a TemporaryDirectory"),
    "file_finding.py::grooming_gaps::preview": (SCRATCH, "a preview in a TemporaryDirectory"),
    "verify_ac.py::_phase_plugins::tmp / f'_sdlc_batch_{phase}.py'": (
        SCRATCH, "a pytest plugin module in the batch run's temporary directory"),
    "verify_ac.py::coverage_report::rc": (SCRATCH, "a coveragerc in a TemporaryDirectory"),
    "gate.py::_full_suite::log": (UNTRACKED, "sdlc-studio/.local/boundary-suite-last.log"),
    "gate.py::record_gate_cost::path": (UNTRACKED, "sdlc-studio/.local/gate-cost.json"),
    "gate.py::record_suite_verdict::path": (UNTRACKED,
                                            "sdlc-studio/.local/gate-suite-verdict.json"),
    "github_sync.py::save_state::path": (UNTRACKED,
                                         "sdlc-studio/.local/github-sync-state.json"),
    "lib/lanes.py::_commit::log": (UNTRACKED, "the hook output in the lane's kept .local folder"),
    "lib/lanes.py::_landed_affects_in::scratch / rel": (SCRATCH, "a staged file in the scratch "
                                                                 "checkout the caller made"),
    "lib/sdlc_md.py::allocation_lock::lock_file": (UNTRACKED,
                                                   "sdlc-studio/.local/allocation.lock"),
    "mutation.py::_restore_scratch::p": (SCRATCH, "an edited file in the run's scratch copy"),
    "mutation.py::run_edits::target": (SCRATCH, "an edited file in the run's scratch copy"),
    "verify_ac.py::_run_phase::sink": (SCRATCH, "a phase's output in the batch run's "
                                                "temporary directory"),
    "verify_ac.py::_report_lock::path.with_name(path.name + '.lock')": (
        UNTRACKED, "the lock beside sdlc-studio/.local/verify-report.json"),
    "mutation.py::applied::sidecar": (UNTRACKED, "the in-flight mutant record under .local"),
    "mutation.py::run_gate::out": (UNTRACKED, "sdlc-studio/.local/mutation-report.json"),
    "reconcile.py::cmd_detect::out_path": (UNTRACKED, "sdlc-studio/.local/reconcile-report.json"),
    "release_cut.py::record_green::p": (UNTRACKED, "the release-gate marker under .local"),
    "repo_map.py::write_index::out_path": (UNTRACKED, "--out, sdlc-studio/.local/repo-map.json "
                                                      "unless the operator names another"),
    "sprint.py::_write_lane_worklists::p": (UNTRACKED, "the worklist export directory the "
                                                       "operator names, handed to a team"),
    "sprint.py::cmd_plan::out": (UNTRACKED, "sdlc-studio/.local/sprint-plan.json"),
    "sprint.py::record_execution_run::path": (UNTRACKED,
                                              "sdlc-studio/.local/test-execution.json"),
    "triage_noise.py::record_creation::p": (UNTRACKED, "sdlc-studio/.local/triage-session.json"),
    "triage_sampling.py::record_sample::p": (UNTRACKED,
                                             "sdlc-studio/.local/triage-sampled.json"),
    "verify_ac.py::cmd_lane_check::path": (UNTRACKED, "sdlc-studio/.local/lane-check-yield.json"),
    "version_check.py::_write_cache::p": (UNTRACKED, "the skill's .local version-check cache"),
    "deploy.py::record::log": (NEW, "the deploy log's header, written only when the log is "
                                    "absent; rows are appended"),
    "ledger.py::append_decision::path": (NEW, "the tranche ledger's header, written only when "
                                              "the ledger is absent; rows are appended"),
    "triage_noise.py::_new_consolidation_cr::path": (NEW, "a CR file under a freshly "
                                                          "allocated id"),
    "init.py::_seed_singleton::dst": (NEW, "a seed copied only where the target is absent"),
    "backfill_audit_runs.py::apply::path": (OUTSIDE, "a one-off backfill of audit fields"),
    "docgen.py::_write::path": (OUTSIDE, "generated pages, re-derived by a rerun"),
    "init.py::_write_definition::path": (OUTSIDE, "seeds the project it initialises"),
    "init.py::stage_agents::p": (OUTSIDE, "seeds the project it initialises"),
    "init.py::init._write::p": (OUTSIDE, "seeds the project it initialises, --force rewrites"),
    "init.py::init::doc": (OUTSIDE, "adds a criterion to a seeded definition document"),
    "migrate_v3.py::_stamp_schema_v3::ver": (OUTSIDE, "a one-off migration"),
    "migrate_v3.py::migrate::e['old_path']": (OUTSIDE, "a one-off migration"),
    "mutation.py::applied::path": (OUTSIDE, "a mutant written in place so the tests import it, "
                                            "the original first kept in a .local sidecar"),
    "mutation.py::_restore_applied::Path(p)": (OUTSIDE, "puts back the original bytes"),
    "mutation.py::_recover_stranded::Path(p)": (OUTSIDE, "puts back the original bytes a cut "
                                                         "short run kept in its sidecar"),
    "project_upgrade.py::apply::cfg": (OUTSIDE, "the upgrade migration"),
    "project_upgrade.py::apply::ver": (OUTSIDE, "the upgrade migration"),
    "project_upgrade.py::apply::root / seed['target']": (OUTSIDE, "the upgrade migration"),
    "project_upgrade.py::apply::target": (OUTSIDE, "the upgrade migration"),
    "project_upgrade.py::apply::dest / name": (OUTSIDE, "the upgrade migration"),
    "project_upgrade.py::rebaseline_apply::p": (OUTSIDE, "the upgrade migration"),
    "provenance.py::remake::p": (OUTSIDE, "a one-off provenance remake over the artefacts"),
    "pvd.py::sync::dest": (OUTSIDE, "a read-only copy of the master PVD in a target repository, "
                                    "copied again by a rerun"),
}

#: The rewrites of a tracked file that bypass `sdlc_md.atomic_write` for no reason but that
#: nobody has moved them yet, each `<script>::<function>::<target>` with what it rewrites. They
#: are no scratch, untracked or new target, so they are kept apart from `SHARED_WRITE_ALLOWLIST`,
#: and TRD §5 rule 5 lists each as not yet moved.
NOT_YET_MOVED: dict[str, str] = {
    "artifact.py::_WriteJournal.rollback::p": "restores a file a failed retitle touched",
    "close_owed.py::stamp_baseline::root / BASELINE_FILE": "the close-owed baseline",
    "command_audit.py::file_coverage_findings::path": "stamps the bug it just filed",
    "refine.py::_fill_user_story::story_path": "fills the story refine just created",
    "retro.py::cmd_cost_baseline::path": "the cost-baseline history row",
    "sprint.py::record_charter_review::path": "the charter's seat review section",
    "triage_noise.py::_append_finding::path": "a bullet on a consolidation CR",
    "verify_ac.py::revert_check::root / rel": "reverts a unit's change in a working tree file",
    "verify_ac.py::revert_check.restore::target": "writes the working tree file back",
}

#: The whole-file rewrites of committed files that went onto `sdlc_md.atomic_write`, each
#: `(script, function)`; the first four are the ones the TRD's guarantee was found false for.
NOW_ATOMIC = (("verify_ac.py", "verify_story"), ("lessons.py", "write_project_file"),
              ("artifact.py", "_wire_story_to_epic"), ("github_sync.py", "set_github_issue_field"),
              ("artifact.py", "cmd_revision"), ("lessons.py", "cmd_add"),
              ("lessons.py", "cmd_summary"), ("verify_ac.py", "cmd_scaffold"),
              ("sprint_report.py", "cmd_render"))


#: The modules whose `open` the sweep reads as the builtin `open`, its file the first argument
#: and its mode `mode=` or the second: `io.open` is `builtins.open` and `codecs.open` wraps it.
#: An `open` called on a name is read so only where an `import` in the same file binds that
#: name to one of them (`_open_modules`). Any other `open` on a receiver is read as a method, its
#: mode `mode=` or the first argument, a mode given second unread. `gzip`, `bz2`, `lzma` and
#: `tarfile` take `(file, mode)` too but are not listed, so `gzip.open(path, 'wt')` is not
#: named, as TRD rule 5 says.
_OPEN_MODULES = ("builtins", "codecs", "io")


def _open_modules(tree: ast.AST) -> frozenset[str]:
    """The names an `import` statement anywhere in `tree` binds to a module in `_OPEN_MODULES`:
    the module's own name, or its `as` alias. A `from` import is not read."""
    return frozenset(alias.asname or alias.name for node in ast.walk(tree)
                     if isinstance(node, ast.Import) for alias in node.names
                     if alias.name in _OPEN_MODULES)


def _rewritten(call: ast.Call, modules: frozenset[str] = frozenset()) -> ast.AST | None:
    """The target `call` truncates and writes whole, or None: the receiver of a `write_text` or
    `write_bytes` method; the first argument of the builtin `open` (the call itself when it has
    none), called as `open` or on a name in `modules` (`_open_modules` of the call's file), its
    mode the second; or the receiver of an `open` method on any other receiver, its mode the
    first. Either `open` is counted only in a literal mode, positional or `mode=`, holding `w`.
    An append, a read, a create-only `x` and an `r+` update truncate nothing."""
    func = call.func
    if isinstance(func, ast.Attribute) and func.attr in _CONTENT_WRITES:
        return func.value
    dotted = isinstance(func, ast.Attribute) and func.attr == "open"
    builtin = (isinstance(func, ast.Name) and func.id == "open"
               or dotted and isinstance(func.value, ast.Name) and func.value.id in modules)
    if not (builtin or dotted):
        return None
    at = 1 if builtin else 0
    modes = [kw.value for kw in call.keywords if kw.arg == "mode"] + call.args[at:at + 1]
    if not (modes and isinstance(modes[0], ast.Constant) and "w" in str(modes[0].value)):
        return None
    if not builtin:
        return func.value
    return call.args[0] if call.args else call    # `open(file=p, mode='w')` names the call


def _rewrite_sites(scripts: Path = SCRIPTS) -> dict[str, list[int]]:
    """Every call in the Python files under `scripts`, at any depth, that rewrites its target
    whole (`_rewritten`), as `<script>::<function>::<target>` mapped to the lines it is made on,
    the script named by its path under `scripts`. A nested function is named by its dotted path
    and a module-level call by `<module>`. The tests are not shipped, so `tests/` is not read."""
    sites: dict[str, list[int]] = {}

    def visit(node: ast.AST, rel: str, qual: str, modules: frozenset[str]) -> None:
        for child in ast.iter_child_nodes(node):
            inner = qual
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                inner = f"{qual}.{child.name}" if qual else child.name
            target = _rewritten(child, modules) if isinstance(child, ast.Call) else None
            if target is not None:
                key = f"{rel}::{qual or '<module>'}::{ast.unparse(target)}"
                sites.setdefault(key, []).append(child.lineno)
            visit(child, rel, inner, modules)

    for p in sorted(scripts.rglob("*.py")):
        rel = p.relative_to(scripts)
        if rel.parts[0] != "tests":
            tree = ast.parse(p.read_text(encoding="utf-8"))
            visit(tree, rel.as_posix(), "", _open_modules(tree))
    return sites


def _unlisted_writes(scripts: Path = SCRIPTS, allowlist=SHARED_WRITE_ALLOWLIST,
                     not_yet_moved=NOT_YET_MOVED) -> list[str]:
    """The rewrite sites under `scripts` that neither `allowlist` nor `not_yet_moved` names,
    with their lines."""
    return sorted(f"{site} (line {', '.join(map(str, lines))})"
                  for site, lines in _rewrite_sites(scripts).items()
                  if site not in allowlist and site not in not_yet_moved)


def _function(script: str, name: str) -> ast.AST:
    tree = ast.parse((SCRIPTS / script).read_text(encoding="utf-8"))
    found = [n for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    if len(found) != 1:
        raise AssertionError(f"{len(found)} functions named {name} in {script}, expected one")
    return found[0]


def _calls(node: ast.AST) -> set[str]:
    return {n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
            for n in ast.walk(node) if isinstance(n, ast.Call)}


class SharedFileWriteSweepTests(unittest.TestCase):
    """A shared file is any tracked workspace file a script rewrites whole, and a truncating
    write of one can leave it half-written. Every `write_text` and `write_bytes` site, and
    every `open` given a literal mode holding `w` (as `mode=` or the builtin's second argument
    when it is called as `open` or on a name an `import` in its file binds to a module in
    `_OPEN_MODULES`, or a method's first on any other receiver, `gzip.open` among them), is
    named here with the kind of its target, so a new one fails until it is moved
    onto `sdlc_md.atomic_write`, its target is shown to be scratch, untracked, new or a listed
    exception, or it is listed apart in `NOT_YET_MOVED`."""

    def test_no_tracked_workspace_file_is_rewritten_with_write_text(self) -> None:
        sites = _rewrite_sites()
        self.assertGreater(len(sites), 20, "the sweep has stopped finding rewrite calls")
        self.assertEqual(_unlisted_writes(), [],
                         "these rewrites are on no list: move a shared file's rewrite onto "
                         "sdlc_md.atomic_write, or list the site with its kind")
        self.assertEqual(sorted(set(SHARED_WRITE_ALLOWLIST) & set(NOT_YET_MOVED)), [],
                         "a site not yet moved onto atomic_write is no allowlisted target")
        stale = sorted((set(SHARED_WRITE_ALLOWLIST) | set(NOT_YET_MOVED)) - set(sites))
        self.assertEqual(stale, [], f"listed sites that no longer rewrite: {stale}")
        for site, (kind, reason) in SHARED_WRITE_ALLOWLIST.items():
            with self.subTest(site=site):
                self.assertIn(kind, (SCRATCH, UNTRACKED, NEW, OUTSIDE))
                self.assertTrue(reason.strip(), "an allowlisted site carries no reason")
        for site, what in NOT_YET_MOVED.items():
            with self.subTest(not_yet_moved=site):
                self.assertTrue(what.strip(), "a site not yet moved says nothing of its target")
        for script, name in NOW_ATOMIC:
            with self.subTest(moved=f"{script}::{name}"):
                self.assertFalse([s for s in (*SHARED_WRITE_ALLOWLIST, *NOT_YET_MOVED)
                                  if s.startswith(f"{script}::{name}::")])
                calls = _calls(_function(script, name))
                self.assertIn("atomic_write", calls)
                self.assertNotIn("write_text", calls)

    def test_the_sweep_catches_a_planted_truncating_write(self) -> None:
        """A planted rewrite of a story file is named, through `write_text`, `write_bytes`
        and each `open` form given a literal `w` mode (the builtin as `open`, and as `io.open`,
        `builtins.open`, `codecs.open` and an `as` alias where an `import` statement in the file
        binds the module, at module level or in a function, and a method on a name, on an
        attribute and on a Path named `io` where only a `from` import names `io`), in a script
        and in any folder under it, in a nested function and at module level; the same call to
        a scratch path on the allowlist is not, nor is one in the tests, one through
        atomic_write, nor an `open` that truncates nothing (a read, an append, a create-only
        `x`, an `r+` update, a mode in a name), nor `gzip.open`, `bz2.open`, `lzma.open` or
        `tarfile.open` given its mode second, each read as a method."""
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "lib").mkdir()
            (d / "tests").mkdir()
            (d / "planted.py").write_text(
                "def stamp(root):\n"
                "    story = root / 'sdlc-studio' / 'stories' / 'US0001.md'\n"
                "    story.write_text('half', encoding='utf-8')\n"
                "def scratch(tmp):\n"
                "    rc = tmp / 'coveragerc'\n"
                "    rc.write_text('x')\n"
                "def safe(story):\n"
                "    sdlc_md.atomic_write(story, 'whole')\n"
                "def outer(root):\n"
                "    def inner():\n"
                "        rc.write_text('x')\n"
                "ROOT.write_text('x')\n"
                "def as_bytes(story):\n"
                "    story.write_bytes(b'half')\n"
                "def builtin(story):\n"
                "    open(story, 'w').close()\n"
                "def keyword(story):\n"
                "    open(story, mode='wb').close()\n"
                "def by_file(story):\n"
                "    open(file=story, mode='w').close()\n"
                "def method(story):\n"
                "    story.open('w').close()\n"
                "def method_keyword(story):\n"
                "    story.open(mode='w').close()\n"
                "def on_attribute(self):\n"
                "    self.story.open('w').close()\n"
                "def untruncated(story, m):\n"
                "    open(story).close()\n"
                "    open(story, 'a').close()\n"
                "    open(story, 'x').close()\n"
                "    open(story, 'r+').close()\n"
                "    open(story, m).close()\n"
                "    story.open().close()\n"
                "    story.open('a').close()\n"
                "    story.open(mode='rb').close()\n", encoding="utf-8")
            (d / "shadow.py").write_text("from compat import io\n"
                                         "def path_named_io(io):\n    io.open('w').close()\n",
                                         encoding="utf-8")
            (d / "with_imports.py").write_text(
                "import io\n"
                "import builtins, codecs\n"
                "import gzip, bz2, lzma, tarfile\n"
                "def by_io(story):\n"
                "    io.open(story, 'w').close()\n"
                "def by_builtins(story):\n"
                "    builtins.open(story, 'w').close()\n"
                "def by_codecs(story):\n"
                "    codecs.open(story, 'w', 'utf-8').close()\n"
                "def io_keyword(story):\n"
                "    io.open(story, mode='w').close()\n"
                "def by_alias(story):\n"
                "    import io as stream\n"
                "    stream.open(story, 'w').close()\n"
                "def by_gzip(story):\n"
                "    gzip.open(story, 'wt').close()\n"
                "def by_bz2(story):\n"
                "    bz2.open(story, 'wt').close()\n"
                "def by_lzma(story):\n"
                "    lzma.open(story, 'wt').close()\n"
                "def by_tarfile(story):\n"
                "    tarfile.open(story, 'w').close()\n"
                "def untruncated(story):\n"
                "    io.open(story, 'a').close()\n"
                "    builtins.open(story).close()\n"
                "    codecs.open(story, 'r', 'utf-8').close()\n"
                "    stream.open(story).close()\n", encoding="utf-8")
            (d / "lib" / "shared.py").write_text("def put(p):\n    p.write_text('x')\n",
                                                 encoding="utf-8")
            (d / "hooks" / "deep").mkdir(parents=True)
            (d / "hooks" / "deep" / "guard.py").write_text("def g(p):\n    p.write_text('x')\n",
                                                           encoding="utf-8")
            (d / "tests" / "test_planted.py").write_text("def t(p):\n    p.write_text('x')\n",
                                                         encoding="utf-8")
            allowlist = {"planted.py::scratch::rc": (SCRATCH, "a temporary directory")}
            self.assertEqual(_unlisted_writes(d, allowlist, {}), [
                "hooks/deep/guard.py::g::p (line 2)",
                "lib/shared.py::put::p (line 2)",
                "planted.py::<module>::ROOT (line 12)",
                "planted.py::as_bytes::story (line 14)",
                "planted.py::builtin::story (line 16)",
                "planted.py::by_file::open(file=story, mode='w') (line 20)",
                "planted.py::keyword::story (line 18)",
                "planted.py::method::story (line 22)",
                "planted.py::method_keyword::story (line 24)",
                "planted.py::on_attribute::self.story (line 26)",
                "planted.py::outer.inner::rc (line 11)",
                "planted.py::stamp::story (line 3)",
                "shadow.py::path_named_io::io (line 3)",
                "with_imports.py::by_alias::story (line 14)",
                "with_imports.py::by_builtins::story (line 7)",
                "with_imports.py::by_codecs::story (line 9)",
                "with_imports.py::by_io::story (line 5)",
                "with_imports.py::io_keyword::story (line 11)"])
            self.assertEqual(_unlisted_writes(d, allowlist, {"lib/shared.py::put::p": "x"})[1],
                             "planted.py::<module>::ROOT (line 12)",
                             "a site listed as not yet moved is not named")
            self.assertIn("planted.py::scratch::rc", _rewrite_sites(d),
                          "the allowlisted scratch write must still be found, then excused")


if __name__ == "__main__":
    unittest.main()
