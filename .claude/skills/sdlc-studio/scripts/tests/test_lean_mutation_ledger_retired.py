"""US0936: the mutation ledger verbs are retired and a mutation run reports its yield only.

`mutation.py register`, `retract`, `retractions` and `audit` are refused by name, and a run keeps
no per-target ledger (`mutation-runs.json`): it appends its series row and nothing else, and
`yield` reads that row back. Nothing downstream reads a ledger - not the seat brief, not the
close's proof-gap reader - and `verify_ac.py coverage` holds its own reason floor.

AC1, AC2 and AC5 drive the shipped entry points as subprocesses in throwaway trees. AC3 drives
`critic.py brief` and `sprint close` over two identical trees, one holding a ledger. AC4 and AC6
read this repository, because their criteria name its derived surface and its stamped criteria.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/mutation.py
from __future__ import annotations

import ast
import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TESTS))
import gitutil  # noqa: E402
import loader  # noqa: E402
from lib import sdlc_md  # noqa: E402
# The stamp derivation US0916 built, reused so the retirement checks cannot disagree about what a
# selector reaches.
from test_lean_no_two_role import (REPO, _deleted_nodes, _git, _live_stamps,  # noqa: E402
                                   _selects_only_deleted)

MUTATION = SCRIPTS / "mutation.py"
RETIRED = ("register", "retract", "retractions", "audit")
LIVE = {"run", "yield", "window", "prefilter"}

#: The criteria AC6 names, which must each carry a US0936 retirement.
AC6_UNITS = ("BG0245", "BG0614", "BG0651", "BG0747", "US0660", "US0661", "US0818", "US0822")
#: The classes AC6 names, which the derivation must see deleted - proof it reads the right base.
AC6_CLASSES = {"test_mutation.py": (
    "LedgerTests", "RegisterTests", "StalenessHashTests", "LedgerSummaryVocabularyTests",
    "RegisterRunAttributionRefusalTests", "MeasuredAttributionTests", "RegisteredLineTests",
    "UnreadableLedgerTests", "RunUnitAttributionCLITests", "RegisterEvidenceIntegrityTests",
    "RetractWithdrawsAVerdictOnTheRecord", "RegisterKeepsOtherUnitsRowsTests", "DuplicateKeyTests",
    "AuditRemedyTests", "RegisterReplacesTests", "AnchoredStalenessTests",
    "AnchorIsRequiredTests"),
    "test_sprint_report.py": ("MutationSurvivorCountTests",)}
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0936: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0936\b")

TARGET = ("def classify(x):\n    if x > 0:\n        label = \"positive\"\n    else:\n"
          "        label = \"other\"\n    return label\n")
KILLING_TEST = ("import unittest\nimport target\n\n\nclass T(unittest.TestCase):\n"
                "    def test_classify(self):\n"
                "        self.assertEqual(target.classify(1), \"positive\")\n"
                "        self.assertEqual(target.classify(-1), \"other\")\n")

#: The reason a withdrawn row carried; HEAD's brief printed it under a WITHDRAWN heading.
WITHDRAWN_REASON = "the mutant was typed against the wrong line entirely"


def _run(script: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(script), *argv], capture_output=True,
                          text=True, timeout=300, env=gitutil.git_env(), check=False)


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _base_ref() -> str | None:
    """The parent of the commit that added this module, or HEAD while it is uncommitted."""
    try:
        rel = Path(__file__).resolve().relative_to(REPO).as_posix()
    except ValueError:
        return None
    added = _git("log", "--diff-filter=A", "--format=%H", "--", rel)
    if added is None:
        return None
    ref = f"{added.split()[0]}^" if added.split() else "HEAD"
    return ref if _git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") else None


def _project(root: Path) -> None:
    """A unit whose Affects the TSD's mutation band covers, with a seat card and an open run."""
    _write(root, "src/gate.py", "def g(a):\n    if a:\n        return 1\n    return 0\n")
    _write(root, "sdlc-studio/tsd.md",
           "# TSD\n\n## Test Levels\n\n### Mutation Testing (assertion integrity)\n\n"
           "Covers `gate.py`.\n\n## Next Section\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "# Sam - QA amigo\n\ncharter\n")
    _write(root, "sdlc-studio/stories/US0101-widget.md",
           "# US0101: widget\n\n> **Status:** Review\n> **Points:** 3\n> **Epic:** EP0001\n"
           "> **Affects:** src/gate.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")
    _write(root, "sdlc-studio/retros/RETRO0001-lean.md",
           "# RETRO-0001: lean\n\n> **Date:** 2026-09-25\n\n## Delivered\n\n- US0101 - shipped\n\n"
           "## Lessons\n\n- learned a thing\n")
    _write(root, "sdlc-studio/.local/run-state.json", json.dumps({
        "schema": 1, "run_id": "RUN-LEAN0936", "started_at": "2026-09-25T00:00:00Z",
        "ended_at": None, "outcome": "running", "goal": "done", "batch": ["US0101"],
        "handoff": None, "appetite": {"minutes": 240.0, "units": 8},
        "sprint_goal": "the close reads no ledger",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"}}))


def _ledger(root: Path) -> None:
    """The ledger in the shapes HEAD read: a registered row withdrawn for the unit, which its
    brief rendered, and an entry naming the unit's file, which its proof-gap reader counted."""
    _write(root, "sdlc-studio/.local/mutation-runs.json", json.dumps({
        "version": 1, "dropped": 0, "entries": [
            "src/gate.py",
            {"target": "src/gate.py", "provenance": "registered", "hash": "0" * 64,
             "summary": {"applied": 0, "killed": 0, "survived": 0, "retracted": 1},
             "mutants": [{"unit": "US0101", "criterion": "AC1", "line": 2, "row": 0,
                          "mutant": "inverted the guard", "test": "shell true",
                          "verdict": "survived",
                          "withdrawn": {"reason": WITHDRAWN_REASON, "verdict": "survived",
                                        "at": "2026-09-25T00:00:00Z"}}]}]}))


def _live(name: str):
    return sys.modules.get(name) or loader.load_script(name)


def _close(root: Path) -> tuple[int, str]:
    """`sprint close` through its entry point, the checklist and handoff steps real and every
    other chain step stubbed green, as `test_lean_close` drives it."""
    mod = _live("sprint")
    out, err = io.StringIO(), io.StringIO()
    with contextlib.ExitStack() as stack:
        stack.enter_context(unittest.mock.patch.object(mod, "_report_holds", lambda *a, **k: []))
        for name in mod._CLOSE_CHAIN:
            if name not in ("checklist", "handoff"):
                stack.enter_context(unittest.mock.patch.object(
                    mod, "_close_" + name.replace("-", "_"),
                    lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
        stack.enter_context(contextlib.redirect_stdout(out))
        stack.enter_context(contextlib.redirect_stderr(err))
        rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
    said = (out.getvalue() + err.getvalue()).replace(str(root), "<root>")
    # The filed report's fingerprint covers its own generation time and the open run's elapsed
    # minutes, so two closes a second apart differ there and nowhere else.
    return rc, re.sub(r"fingerprint [0-9a-f]{16}", "fingerprint <fp>", said)


def _ledger_reads(path: Path) -> list[str]:
    """Every place a module reaches the ledger: an attribute of `mutation` naming a ledger
    reader, or the ledger's file name as a string it can read."""
    names = {"ledger_path", "_load_ledger", "ledger_entries", "retractions", "audit_duplicates",
             "register_mutant", "retract_mutant", "entry_staleness", "row_staleness",
             "LedgerUnreadable", "_RETRACT_REASON_MIN"}
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits = [f"{path.name}:{n.lineno} mutation.{n.attr}" for n in ast.walk(tree)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
            and n.value.id in ("mutation", "_mut", "mut") and n.attr in names]
    hits += [f"{path.name}:{n.lineno} {n.value!r}" for n in ast.walk(tree)
             if isinstance(n, ast.Constant) and isinstance(n.value, str)
             and "mutation-runs.json" in n.value]
    return hits


class MutationLedgerRetiredTests(unittest.TestCase):

    def test_the_ledger_verbs_are_retired(self) -> None:
        """AC1. MUTANT: delete the four parsers and nothing else - each verb then exits 2 with
        argparse's `invalid choice`, which names neither the retirement nor `mutation.py run`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            for verb in RETIRED:
                for argv in ((verb, "--root", d, "--unit", "US0101"), ("--root", d, verb)):
                    with self.subTest(argv=argv):
                        r = _run(MUTATION, *argv)
                        out = r.stdout + r.stderr
                        self.assertEqual(2, r.returncode, out)
                        self.assertIn(f"`mutation.py {verb}` is retired", out)
                        self.assertIn("mutation.py run", out)
                        self.assertNotIn("invalid choice", out)
            self.assertFalse((root / "sdlc-studio" / ".local").exists(),
                             "a retired verb wrote something")
        h = _run(MUTATION, "--help")
        self.assertEqual(0, h.returncode, h.stderr)
        listed = re.search(r"\{([a-z,]+)\}", h.stdout)
        self.assertIsNotNone(listed, h.stdout)
        self.assertEqual(LIVE, set(listed.group(1).split(",")), h.stdout)
        for verb in RETIRED:
            self.assertIsNone(re.search(rf"\b{verb}\b", h.stdout), f"--help names {verb}")

    def test_run_and_yield_work_without_a_ledger(self) -> None:
        """AC2. MUTANT: HEAD's `run`, which writes `mutation-runs.json` beside the series row."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "target.py", TARGET)
            _write(root, "test_good.py", KILLING_TEST)
            (root / "sdlc-studio").mkdir()
            r = _run(MUTATION, "run", "--root", d, "--files", "target.py",
                     "--test", f"{sys.executable} -B -m unittest test_good")
            out = r.stdout + r.stderr
            counts = re.search(r"mutation: (\d+) applied, (\d+) killed", out)
            self.assertIsNotNone(counts, out)
            self.assertGreater(int(counts.group(2)), 0, f"the run reported no kill:\n{out}")
            local = root / "sdlc-studio" / ".local"
            self.assertFalse((local / "mutation-runs.json").exists(), "the run wrote a ledger")
            report = json.loads((local / "mutation-report.json").read_text(encoding="utf-8"))
            self.assertNotIn("ledger", report, "the run reports a ledger it no longer keeps")
            rows = [json.loads(ln) for ln in (local / "mutation-series.jsonl").read_text(
                encoding="utf-8").splitlines() if ln.strip()]
            self.assertEqual(1, len(rows), rows)
            self.assertEqual(int(counts.group(2)), rows[0]["killed"])
            y = _run(MUTATION, "yield", "--run", rows[0]["run_id"], "--root", d,
                     "--format", "json")
            self.assertEqual(0, y.returncode, y.stdout + y.stderr)
            got = json.loads(y.stdout)
            self.assertTrue(got["found"], got)
            self.assertEqual(rows[0]["run_id"], got["run"])
            self.assertEqual(rows[0]["survived"], got["survivors"])
            # the control: a run nobody recorded is still refused, so `found` is read, not assumed
            self.assertEqual(2, _run(MUTATION, "yield", "--run", "MRUN-ghost-000000",
                                     "--root", d).returncode)

    def test_brief_and_close_read_no_ledger(self) -> None:
        """AC3. MUTANT: remove the brief's WITHDRAWN section while `sprint.claimed_proof_gaps`
        still reads the ledger - it then counts the ledger's entry for `src/gate.py` as mutation
        evidence, so the tree holding a ledger reports no gap and the tree without one does."""
        critic = SCRIPTS / "critic.py"
        sprint = _live("sprint")
        seen: dict[str, dict] = {}
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for label, d in (("ledger", a), ("none", b)):
                root = Path(d)
                _project(root)
                if label == "ledger":
                    _ledger(root)
                r = _run(critic, "brief", "--unit", "US0101", "--seat", "qa", "--root", d)
                self.assertEqual(0, r.returncode, r.stdout + r.stderr)
                gaps = sprint.claimed_proof_gaps(root, ["US0101"])
                rc, said = _close(root)
                seen[label] = {"brief": r.stdout.replace(d, "<root>"), "gaps": gaps,
                               "rc": rc, "close": said}
        with_ledger, without = seen["ledger"], seen["none"]
        self.assertNotIn("WITHDRAWN", with_ledger["brief"])
        self.assertNotIn(WITHDRAWN_REASON, with_ledger["brief"])
        self.assertEqual(without["brief"], with_ledger["brief"], "the brief reads the ledger")
        self.assertEqual(["US0101"], without["gaps"], "the fixture's unit owes no mutation proof")
        self.assertEqual(without["gaps"], with_ledger["gaps"], "the proof-gap reader reads it")
        self.assertEqual(without["rc"], with_ledger["rc"], with_ledger["close"])
        self.assertEqual(without["close"], with_ledger["close"], "the close reads the ledger")
        shipped = sorted([*SCRIPTS.glob("*.py"), *(SCRIPTS / "lib").glob("*.py")])
        self.assertGreater(len(shipped), 20, "the scan is looking in the wrong place")
        self.assertEqual([], [h for p in shipped for h in _ledger_reads(p)],
                         "a shipped script still reaches the mutation ledger")

    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC4. MUTANT: retire the verbs without rerunning `docgen.py surface`, so the derived
        surface still lists all four and `--check` counts them as drift."""
        surface = (SCRIPTS.parent / "reference-scripts-surface.md").read_text(encoding="utf-8")
        self.assertIn("`mutation.py run`", surface, "the surface lost the verb that stays")
        for verb in RETIRED:
            self.assertNotIn(f"`mutation.py {verb}`", surface)
        r = _run(SCRIPTS / "docgen.py", "surface", "--check", "--root", str(REPO))
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("docgen surface: 0 drift item(s)", r.stdout)

    def test_the_coverage_ruling_floor_survives_the_retract_verb(self) -> None:
        """AC5. MUTANT: delete `retract` and `_RETRACT_REASON_MIN` while `add_coverage_ruling`
        still reads `mutation._RETRACT_REASON_MIN` - the ruling then dies on the AttributeError
        instead of being refused naming the floor."""
        verify_ac = _live("verify_ac")
        mutation = _live("mutation")
        floor = verify_ac.COVERAGE_REASON_MIN
        self.assertEqual(20, floor, "the floor moved rather than relocated")
        self.assertFalse(hasattr(mutation, "_RETRACT_REASON_MIN"), "the old constant survives")
        self.assertEqual([], _ledger_reads(SCRIPTS / "verify_ac.py"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "src/x.py", "x = 1\n")
            story = _write(root, "sdlc-studio/stories/US0101-x.md",
                           "# US0101: x\n\n> **Status:** In Progress\n> **Affects:** src/x.py\n\n"
                           "## Acceptance Criteria\n\n### AC1: x\n\n- **Verify:** shell true\n")
            before = story.read_text(encoding="utf-8")
            base = ("coverage", "--id", "US0101", "--file", "src/x.py", "--line", "1",
                    "--root", d)
            for action in ("rule", "withdraw"):
                with self.subTest(action=action):
                    r = _run(SCRIPTS / "verify_ac.py", base[0], action, *base[1:],
                             "--reason", "r" * (floor - 1))
                    out = r.stdout + r.stderr
                    self.assertEqual(2, r.returncode, out)
                    self.assertIn(f"floor of {floor}", out)
                    self.assertNotIn("retract", out, "the refusal names a retired verb")
                    self.assertEqual(before, story.read_text(encoding="utf-8"))
            # the control: a reason AT the floor is written
            r = _run(SCRIPTS / "verify_ac.py", base[0], "rule", *base[1:], "--reason", "r" * floor)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("## Coverage Rulings", story.read_text(encoding="utf-8"))

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC6. MUTANTS: leave one retired criterion's `Verified: yes` stamp (as a node id or a
        `-k` naming a deleted method); retire one without its `Verified:` stamp; keep a deleted
        class in `test_mutation.py`."""
        base = _base_ref()
        if base is None:
            self.skipTest("no git history here to derive the deleted tests from")
        deleted = _deleted_nodes(base)
        for module, classes in AC6_CLASSES.items():
            gone = deleted.get(module, {}).get("gone", set())
            for cls in classes:
                self.assertIn((cls, ""), gone, f"{module}::{cls} was to be deleted ({base})")
        self.assertFalse((TESTS / "test_lean_mutation_off.py").exists(),
                         "test_lean_mutation_off.py was to be emptied and deleted")
        artefacts = REPO / "sdlc-studio"
        if not artefacts.is_dir():
            self.skipTest("no sdlc-studio/ artefacts in this checkout")
        sources = [(path.relative_to(REPO), path.read_text(encoding="utf-8",
                                                          errors="replace").splitlines())
                   for path in sorted(artefacts.rglob("*.md"))]
        self.assertEqual([], _live_stamps(sources, deleted),
                         "a `Verified: yes` selector still names a deleted test node")
        retired: set[str] = set()
        for label, lines in sources:
            for i, line in enumerate(lines):
                if RETIRED_VERIFY.search(line):
                    stamp = next((ln for ln in lines[i + 1:i + 3] if "Verified:" in ln), "")
                    self.assertRegex(stamp, RETIRED_STAMP, f"{label}:{i + 1} has no stamp")
                    retired.add(Path(label).name.split("-")[0])
        self.assertLessEqual(set(AC6_UNITS), retired, "a criterion AC6 names is not retired")
        # BG0245's selectors carry no `Verified:` stamp at all, so the stamp check cannot see them;
        # an executable selector that reaches only deleted nodes is refused whatever its stamp.
        selecting = [f"{label}:{i + 1}" for label, lines in sources
                     for i, line in enumerate(lines)
                     if (m := sdlc_md.VERIFY_RE.match(line))
                     and not m.group(2).lower().startswith("manual")
                     and _selects_only_deleted(m.group(2), deleted)]
        self.assertEqual([], selecting, "an executable selector reaches only deleted nodes")


if __name__ == "__main__":
    unittest.main()
