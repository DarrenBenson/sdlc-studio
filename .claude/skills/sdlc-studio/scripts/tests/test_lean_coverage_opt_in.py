"""US0922: line coverage is measured only when a project opts in.

A project that never sets `review.line_coverage` collects nothing at Done and prints nothing.
One that opts in to `block` has every unit judged: the dated cutoff that exempted older units
(`review.line_coverage_after`) is gone from the defaults and from every shipped reader.

AC1 and AC2 build a throwaway git repository holding one story whose own pytest selector passes
but never executes a line the story added, verify it with the shipped `verify_ac.py run`, then
move it to Done. AC4 reads this repository's own artefacts, because its criterion names them.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/transition.py
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
import unittest.mock  # a submodule: bare `import unittest` does not bind it
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
REPO = SCRIPTS.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import gitutil  # noqa: E402 - confined, hermetic git for the fixture repositories
import transition  # noqa: E402
import verify_ac  # noqa: E402
from lib import sdlc_md  # noqa: E402
import test_lean_no_two_role as stamps  # noqa: E402 - `shipped_source`, the shared reader scan

SID = "US0001"
PROD = "src/thing.py"
TEST = "tests/test_thing.py"
BASE_PROD = "def used():\n    return 1\n"
TEST_BODY = ("import sys, pathlib\n"
             "sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))\n"
             "from src import thing\n\n\nclass TestT:\n    def test_a(self):\n"
             "        assert thing.used() == 1\n")
#: The two CoverageGateTests nodes this story deletes, and the US0816 criteria stamped on them.
DELETED = ("test_units_created_before_the_cutoff_are_exempt", "test_the_shipped_default_is_report")
US0816_RETIRED = ("AC5", "AC7")


def _config(root: Path, review_lines: str) -> None:
    (root / "sdlc-studio" / ".config.yaml").write_text(f"review:\n{review_lines}",
                                                        encoding="utf-8")


def _project(tmp: str, review_lines: str = "") -> Path:
    """A committed repository, then a story commit adding `added_dead`, which the story's own
    selector never calls. An OPEN run whose batch names the story carries the base ref."""
    root = Path(tmp)
    for rel in ("src", "tests", "sdlc-studio/stories", "sdlc-studio/.local"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / "src" / "__init__.py").write_text("", encoding="utf-8")
    (root / PROD).write_text(BASE_PROD, encoding="utf-8")
    (root / TEST).write_text(TEST_BODY, encoding="utf-8")
    (root / "sdlc-studio" / "stories" / f"{SID}-cov.md").write_text(
        f"# {SID}: coverage opt-in fixture\n\n> **Status:** Review\n> **Created:** 2026-09-01\n"
        f"> **Affects:** {PROD}\n\n## Acceptance Criteria\n\n"
        f"- **AC1:** Given it, when it, then it.\n  - **Verify:** pytest {TEST}::TestT::test_a\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
        "| 2026-09-01 | t | Filed |\n", encoding="utf-8")
    _config(root, review_lines)
    gitutil.git(["init", "-q"], cwd=root)
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", "base"], cwd=root)
    base = gitutil.git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()
    (root / PROD).write_text(BASE_PROD + "\n\ndef added_dead():\n    return 2\n", encoding="utf-8")
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-qm", f"feat({SID}): the change"], cwd=root)
    (root / "sdlc-studio" / ".local" / "run-state.json").write_text(json.dumps(
        {"run_id": "RUN-TEST01", "batch": [SID], "base_ref": base}), encoding="utf-8")
    ran = subprocess.run([sys.executable, str(SCRIPTS / "verify_ac.py"), "run", "--id", SID,
                          "--dir", "sdlc-studio/stories", "--root", str(root)],
                         capture_output=True, text=True, env=gitutil.git_env(), timeout=300)
    if ran.returncode != 0:
        raise AssertionError("the fixture story's own selector must pass: "
                             + ran.stdout + ran.stderr)
    return root


def _done(root: Path) -> tuple[int, str]:
    """`transition.py set <story> Done` through its entry point, stdout and stderr merged."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = transition.main(["set", SID, "Done", "--root", str(root)])
    return code, buf.getvalue()


def _status(root: Path) -> str:
    text = (root / "sdlc-studio" / "stories" / f"{SID}-cov.md").read_text(encoding="utf-8")
    return sdlc_md.extract_field(text, "Status") or ""


def _live_stamps(label: str, lines: list[str]) -> list[str]:
    """`label:line` for each `Verified: yes` criterion whose Verify selector names a deleted node,
    as a node id or a `-k` keyword alike: the method name is the part either spelling carries."""
    live = []
    for i, line in enumerate(lines):
        vm = sdlc_md.VERIFY_RE.match(line)
        if not vm or not any(name in vm.group(2) for name in DELETED):
            continue
        for nxt in lines[i + 1:i + 4]:
            if sdlc_md.VERIFY_RE.match(nxt):
                break
            m = sdlc_md.VERIFIED_RE.match(nxt)
            if m and m.group(2).lower() == "yes":
                live.append(f"{label}:{i + 1}")
    return live


class CoverageOptInTests(unittest.TestCase):

    def test_coverage_is_off_by_default(self) -> None:
        """AC1. MUTANT: restore `report` as the fallback literal - the never-set project then
        collects coverage and prints the uncovered line."""
        with tempfile.TemporaryDirectory() as t:
            root = _project(t)
            calls = []
            real = verify_ac.coverage_report
            with unittest.mock.patch.object(
                    verify_ac, "coverage_report",
                    lambda *a, **k: (calls.append(1), real(*a, **k))[1]):
                code, out = _done(root)
            self.assertEqual(code, 0, out)
            self.assertEqual(_status(root), "Done", out)
            self.assertEqual(calls, [], "a project that never opted in collects no coverage")
            self.assertNotIn("coverage", out.lower(), out)
        with tempfile.TemporaryDirectory() as t:
            # the control: the same fixture, opted in to `report`, measures and names the line
            root = _project(t, "  line_coverage: report\n")
            code, out = _done(root)
            self.assertEqual(code, 0, out)
            self.assertIn("coverage: 1 uncovered added line(s)", out)
            self.assertIn(f"{PROD}: 6", out)

    def test_block_still_refuses_with_no_date_cutoff(self) -> None:
        """AC2. MUTANT: restore the cutoff comparison that exempts a unit created before
        `review.line_coverage_after`. Driven through the shipped CLI."""
        with tempfile.TemporaryDirectory() as t:
            root = _project(t, "  line_coverage: block\n  line_coverage_after: \"2026-09-20\"\n")
            proc = subprocess.run([sys.executable, str(SCRIPTS / "transition.py"), "set", SID,
                                   "Done", "--root", str(root)],
                                  capture_output=True, text=True, env=gitutil.git_env(),
                                  timeout=300)
            out = proc.stdout + proc.stderr
            self.assertNotEqual(proc.returncode, 0, out)
            self.assertIn("uncovered added line", out)
            self.assertIn(f"{PROD}: 6", out)
            self.assertEqual(_status(root), "Review", out)

    def test_the_cutoff_key_is_retired(self) -> None:
        """AC3. MUTANTS: leave `line_coverage: report` in the defaults; keep
        `line_coverage_after: null` there; keep `transition.line_coverage_cutoff` reading it."""
        defaults = (SCRIPTS.parent / "templates" / "config-defaults.yaml").read_text(
            encoding="utf-8")
        review = re.search(r"^review:\n((?:[ #].*\n|\n)*)", defaults, re.MULTILINE)
        self.assertIsNotNone(review, "config-defaults.yaml has a review block")
        self.assertRegex(review.group(1), r"(?m)^  line_coverage: off\s*(#.*)?$")
        self.assertNotIn("line_coverage_after", defaults)
        readers = [str(p.relative_to(SCRIPTS)) for p in sorted(SCRIPTS.rglob("*.py"))
                   if "tests" not in p.relative_to(SCRIPTS).parts
                   and "line_coverage_after" in stamps.shipped_source(p)]
        self.assertEqual(readers, [], "a shipped script still reads review.line_coverage_after")

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC4. MUTANTS: keep a deleted node in CoverageGateTests; leave US0816 AC5 or AC7
        stamped `Verified: yes` on it."""
        tree = ast.parse((HERE / "test_transition.py").read_text(encoding="utf-8"))
        gate = next(n for n in tree.body
                    if isinstance(n, ast.ClassDef) and n.name == "CoverageGateTests")
        methods = {n.name for n in gate.body if isinstance(n, ast.FunctionDef)}
        self.assertEqual(methods & set(DELETED), set(), "the retired nodes are deleted")
        # the reader catches a node id and a `-k` keyword, and passes the retired shape
        node = f"pytest tests/test_transition.py::CoverageGateTests::{DELETED[0]}"
        controls = {
            "node": ([f"- **Verify:** {node}", "- **Verified:** yes (2026-09-08)"], ["node:1"]),
            "k": ([f"- **Verify:** pytest tests/test_transition.py -k {DELETED[1]}",
                   "- **Verified:** yes (2026-09-08)"], ["k:1"]),
            "retired": (["- **Verify:** manual - retired by US0922: gone",
                         "- **Verified:** manual (2026-09-25) - retired, superseded by US0922"],
                        []),
        }
        for label, (lines, want) in controls.items():
            self.assertEqual(_live_stamps(label, lines), want, label)
        artefacts = REPO / "sdlc-studio"
        if not artefacts.is_dir():
            self.skipTest("no sdlc-studio/ artefacts in this checkout")
        live = [s for p in sorted(artefacts.rglob("*.md"))
                for s in _live_stamps(str(p.relative_to(REPO)), p.read_text(
                    encoding="utf-8", errors="replace").splitlines())]
        self.assertEqual(live, [], "a Verified: yes selector names a deleted test node")
        # US0816's two criteria carry the D0259 retirement, not merely a missing stamp
        story = next((artefacts / "stories").glob("US0816-*.md")).read_text(encoding="utf-8")
        for ac in US0816_RETIRED:
            block = re.search(rf"\*\*{ac}\*\*.*?\n((?:  .*\n)+)", story)
            self.assertIsNotNone(block, f"US0816 {ac}")
            self.assertRegex(block.group(1), r"\*\*Verify:\*\* manual - retired by US0922: \S")
            self.assertRegex(block.group(1), r"\*\*Verified:\*\* manual \(\d{4}-\d\d-\d\d\) - "
                                             r"retired, superseded by US0922")


if __name__ == "__main__":
    unittest.main()
