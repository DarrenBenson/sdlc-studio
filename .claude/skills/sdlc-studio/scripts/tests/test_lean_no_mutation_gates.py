"""US0920: the gate runs no evidence-drift lane and the close names no mutation-evidence mode.

The pre-commit `evidence-drift` lane refused any commit that moved a delivered unit's registered
mutant row, and the sprint close stated (and refused on a typo in) `review.mutation_evidence`.
Both are deleted. AC1 drives the shipped `gate.py` over a throwaway git workspace whose staged
change drifts a registered row under `block`. AC2 drives `sprint close` through `sprint.main`
with the real checklist step and a typo'd mode. AC3 reads this repository's artefacts, because
its criterion is about this repository's stamped criteria.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import gitutil  # noqa: E402 - confined git for the fixture repos
import loader  # noqa: E402
import workspace  # noqa: E402

REPO = workspace.REPO
LANE = "evidence-drift"

BUG = ("# BG0001: fixture\n\n> **Status:** Fixed\n> **Severity:** Medium\n> **Points:** 1\n"
       "> **Affects:** src/x.py\n\n## Acceptance Criteria\n\n- [x] **AC1** Given a, when b, then c\n"
       "  - **Verify:** pytest tests/test_x.py::T::test_c\n")


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _drifting_workspace(root: Path) -> None:
    """A repo whose delivered BG0001 holds a registered row on `src/x.py` at HEAD's bytes, under
    `review.mutation_evidence: block`, with a staged edit that moves the row's own site - the
    commit HEAD's lane refused."""
    import mutation  # noqa: PLC0415 - the ledger writer, used only to seed the fixture
    _write(root, "src/x.py", "alpha = 1\n")
    _write(root, "sdlc-studio/bugs/BG0001-fixture.md", BUG)
    _write(root, "sdlc-studio/.config.yaml", "review:\n  mutation_evidence: block\n")
    _write(root, ".gitignore", "sdlc-studio/.local/\n")
    (root / "sdlc-studio" / ".local").mkdir(parents=True)
    gitutil.git(["init", "-q", "-b", "main"], cwd=root)
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", "seed"], cwd=root)
    mutation.register_mutant(root, root / "src" / "x.py", "flip alpha", "pytest t", "killed",
                             unit="BG0001", criterion="AC1", line=1, anchor="alpha = 1", row=0)
    _write(root, "src/x.py", "alpha = 2\n")
    gitutil.git(["add", "src/x.py"], cwd=root)


def _gate(root: Path, *argv: str) -> tuple[int, dict]:
    r = subprocess.run([sys.executable, str(SCRIPTS / "gate.py"), "--root", str(root),
                        "--format", "json", *argv], capture_output=True, text=True,
                       env=gitutil.git_env(), timeout=300)
    try:
        return r.returncode, json.loads(r.stdout)
    except ValueError:
        raise AssertionError(f"gate.py printed no JSON (rc {r.returncode}):\n"
                             f"{r.stdout}\n{r.stderr}") from None


def _live(name: str):
    """The module the close resolves at call time (see test_lean_close)."""
    return sys.modules.get(name) or importlib.import_module(name)


def _close_fixture(root: Path) -> None:
    """An open run with one Review story, its retro filed, and a typo'd evidence mode."""
    state = {"schema": 1, "run_id": "RUN-LEAN0920", "started_at": "2026-09-25T00:00:00Z",
             "ended_at": None, "outcome": "running", "goal": "done", "batch": ["US0101"],
             "handoff": None, "appetite": {"minutes": 240.0, "units": 8},
             "sprint_goal": "the close names no evidence mode",
             "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"}}
    _write(root, "sdlc-studio/.local/run-state.json", json.dumps(state))
    _write(root, "sdlc-studio/.config.yaml", "review:\n  mutation_evidence: blcok\n")
    _write(root, "src/widget.py", "x = 1\n")
    _write(root, "sdlc-studio/stories/US0101-widget.md",
           "# US0101: widget\n\n> **Status:** Review\n> **Points:** 3\n> **Epic:** EP0001\n"
           "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")
    _write(root, "sdlc-studio/retros/RETRO0001-lean.md",
           "# RETRO-0001: lean\n\n> **Date:** 2026-09-25\n\n## Delivered\n\n- US0101 - shipped\n\n"
           "## Lessons\n\n- learned a thing\n")


#: A checklist with every compulsory item answered, so the step's verdict turns on the mode.
_ANSWERED = {"items": [{"id": "retro-filed", "title": "the retro is filed", "value": "yes",
                        "detail": ""}],
             "outstanding": [], "expired": [], "stop_ship": [], "pending_in_close": []}

_MODE_WORDS = re.compile(r"blcok|mutation[ _-]evidence", re.IGNORECASE)

#: The test nodes this story deletes, by the selector text a `Verify:` line names them with.
DELETED_NODES = ("test_gate.py::EvidenceDriftTests",
                 "test_lean_mutation_off.py::EvidenceDriftTests",
                 "test_sprint.py::MutationEvidenceModeTests")

#: The criteria that named a deleted node, by artefact, and how many each carried. BG0747's
#: class-level selector named the deleted class too, so it is retired with US0882's two -
#: US0882 AC3 re-points to its surviving test instead of retiring.
RETIRED = {"BG0651": 2, "US0660": 1, "US0822": 1, "US0882": 2, "BG0747": 1}

#: The D0259 pattern, naming this story as the retirer.
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0920: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0920\b")


class MutationGatesGoneTests(unittest.TestCase):

    def test_no_evidence_drift_lane(self) -> None:
        """AC1. MUTANTS: leave `evidence-drift` in DEFAULT_CHECKS; keep it registered but out of
        the plain run (the `--only` probe still finds it); keep `_evidence_drift` defined."""
        import gate  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _drifting_workspace(root)
            _rc, plain = _gate(root)
            ran = [c.get("check") for c in plain.get("checks") or []]
            self.assertTrue(ran, f"the plain gate ran no lane at all: {plain}")
            self.assertNotIn(LANE, ran, "the plain gate still runs the evidence-drift lane")
            for check in plain["checks"]:
                self.assertNotIn("mutant", str(check.get("detail") or ""),
                                 f"a lane still judges the drifted mutant row: {check}")
            rc, named = _gate(root, "--only", LANE)
            self.assertNotEqual(0, rc, "naming the deleted lane was not refused")
            detail = named["checks"][0]["detail"]
            self.assertIn(f"unknown check name(s): {LANE}", detail,
                          f"the gate still knows the lane: {named}")
            valid = detail.split("valid:", 1)[1]
            self.assertNotIn(LANE, valid, "the gate's lane list still names the lane")
        for table in ("DEFAULT_CHECKS", "ON_DEMAND_CHECKS", "BLOCKING_ON_ERROR"):
            self.assertNotIn(LANE, getattr(gate, table), f"gate.{table} names the lane")
        self.assertFalse(hasattr(gate, "_evidence_drift"), "gate._evidence_drift survives")

    def test_the_close_names_no_mutation_evidence_mode(self) -> None:
        """AC2. MUTANTS: keep the close's refusal of an unrecognised mode; keep the note and
        drop only its refusal (the typo is then named in the pass line); keep the function."""
        loader.load_script("sprint")
        mod = _live("sprint")
        report = _live("sprint_report")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _close_fixture(root)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.ExitStack() as stack:
                stack.enter_context(unittest.mock.patch.object(
                    report, "checklist", lambda *a, **k: _ANSWERED))
                stack.enter_context(unittest.mock.patch.object(
                    mod, "_report_holds", lambda *a, **k: []))
                for name in mod._CLOSE_CHAIN:
                    if name != "checklist":
                        stack.enter_context(unittest.mock.patch.object(
                            mod, "_close_" + name.replace("-", "_"),
                            lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
                # the step itself, as the chain calls it, so its verdict is read directly
                ok, detail, _remedy = mod._close_checklist(root, "RETRO0001", {})
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(root)])
            self.assertTrue(ok, f"the checklist step refused on the evidence mode: {detail}")
            self.assertIsNone(_MODE_WORDS.search(detail),
                              f"the checklist step names a mutation-evidence mode: {detail}")
            said = out.getvalue() + err.getvalue()
            self.assertEqual(0, rc, said)
            self.assertIsNone(_MODE_WORDS.search(said),
                              f"the close names a mutation-evidence mode:\n{said}")
            state = json.loads((root / "sdlc-studio/.local/run-state.json").read_text())
            self.assertIsNone(_MODE_WORDS.search(json.dumps(state)),
                              "the closed run records a mutation-evidence mode")
        self.assertFalse(hasattr(mod, "mutation_evidence_note"),
                         "sprint.mutation_evidence_note survives")

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC3. MUTANTS: leave any criterion's `Verify:` naming a deleted node; retire one
        without its `Verified:` stamp; name another story as the retirer; keep a deleted class
        in its test module."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        tests = SCRIPTS / "tests"
        for node in DELETED_NODES:
            module, cls = node.split("::")
            self.assertFalse(f"class {cls}(" in (tests / module).read_text(encoding="utf-8"),
                             f"{node} was not deleted")
        live, retired = [], {}
        for path in sorted((REPO / "sdlc-studio").rglob("*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            unit = path.name.split("-")[0]
            for i, line in enumerate(lines):
                if "**Verify:**" in line and any(n in line for n in DELETED_NODES):
                    stamp = next((ln for ln in lines[i + 1:i + 3] if "Verified:" in ln), "")
                    if re.search(r"\*\*Verified:\*\*\s*yes\b", stamp):
                        live.append(f"{path.relative_to(REPO)}:{i + 1}")
                if RETIRED_VERIFY.search(line):
                    stamp = next((ln for ln in lines[i + 1:i + 3] if "Verified:" in ln), "")
                    self.assertRegex(stamp, RETIRED_STAMP,
                                     f"{path.name}:{i + 1} is retired without its stamp")
                    retired[unit] = retired.get(unit, 0) + 1
        self.assertEqual([], live, "a `Verified: yes` selector still names a deleted test node")
        self.assertEqual(RETIRED, retired)


if __name__ == "__main__":
    unittest.main()
