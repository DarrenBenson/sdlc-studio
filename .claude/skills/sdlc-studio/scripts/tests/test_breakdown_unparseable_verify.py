"""BG0981: a Verify line `verify_ac` cannot parse leaves its unit ungroomed.

The grooming gate asked only whether a criterion HAS a Verify line, so a unit whose only Verify
line wraps its expression in backticks, or names a verb the runner does not know, was reported
groomed by `sprint.py breakdown`, `sprint.py plan --write` opened a run on it, and only
`verify_ac.py run` at build time refused it. Driven through the shipped `sprint.py breakdown` and
`sprint.py plan --write` against a throwaway project; the refusal quoted is the runner's own.

MUTANTS, each of which a test here fails on: (1) the grooming predicate does not ask the runner's
parser, so the unit is groomed; (2) the unit is ungroomed under a message of its own, not
`verify_ac`'s; (3) `plan --write` opens the run anyway; (4) a `manual` marker, `shell` or a DSL
verb is refused as unparseable; (5) only the first Verify line of a criterion is asked; (6) every
block in the file is asked, not only the criteria the runner judges, so a line under a later
heading the runner never runs refuses the unit; (7) a criteria reader that raises stops the gate
rather than leaving the unit to the legs that could read it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")

#: Each unparseable line, with the runner's own refusal of it.
UNPARSEABLE = {
    "US0001": ("`file src/app.py`", "unrecognised verifier '`file'"),
    "US0002": ("frobnicate src/app.py", "unrecognised verifier 'frobnicate'"),
    # The second line of one criterion is unparseable, the first is fine.
    "US0003": ("file src/app.py\n- **Verify:** `grep x src/app.py`",
               "unrecognised verifier '`grep'"),
}
PARSEABLE = {"US0011": "file src/app.py", "US0012": "shell true",
             "US0013": "manual - the operator reads the page"}


def _live(name: str):
    """The module the command resolves at call time; another test module may re-register it."""
    return sys.modules.get(name) or importlib.import_module(name)


def _call(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main(list(argv))
    return rc, out.getvalue(), err.getvalue()


def _project(d: str, units: dict[str, str]) -> Path:
    """One Ready story per unit, each with one criterion carrying the Verify line given, and a
    worklist naming them."""
    root = Path(d) / "repo"
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for uid, verify in units.items():
        (stories / f"{uid}-x.md").write_text(
            f"# {uid}: x\n\n> **Status:** Ready\n> **Affects:** src/app.py\n> **Points:** 2\n\n"
            f"## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** {verify}\n",
            encoding="utf-8")
    (root / "wl.md").write_text("".join(f"{u}\n" for u in units), encoding="utf-8")
    return root


def _breakdown(root: Path) -> dict:
    rc, out, err = _call("breakdown", "--worklist", str(root / "wl.md"), "--root", str(root),
                         "--format", "json")
    if rc not in (0, 1, 2):
        raise AssertionError(f"breakdown crashed ({rc}): {err}")
    return json.loads(out)


def _state(root: Path) -> Path:
    return root / "sdlc-studio" / ".local" / "run-state.json"


class UnparseableVerifyTests(unittest.TestCase):

    def test_unparseable_verify_is_ungroomed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, {u: line for u, (line, _msg) in UNPARSEABLE.items()})
            bd = _breakdown(root)
            self.assertEqual([], bd["groomed"], bd)
            rows = {row["id"]: row for row in bd["ungroomed"]}
            self.assertEqual(set(UNPARSEABLE), set(rows), bd)
            for uid, (_line, message) in UNPARSEABLE.items():
                with self.subTest(unit=uid):
                    said = " ".join(rows[uid]["missing"])
                    self.assertIn(message, said, "the runner's own message is not carried")
                    self.assertIn("AC1", said)
                    self.assertTrue(rows[uid]["ac_why"], rows[uid])
            rc, out, _err = _call("breakdown", "--worklist", str(root / "wl.md"),
                                  "--root", str(root))
            self.assertIn("3 ungroomed", out)
            self.assertIn(UNPARSEABLE["US0001"][1], out)
            # One parser, never a second: what the gate quotes is what the runner refuses with.
            va = _live("verify_ac")
            result = va.run_verifier(UNPARSEABLE["US0002"][0], 10, root)
            self.assertEqual("invalid", result.kind)
            self.assertIn(UNPARSEABLE["US0002"][1], result.stderr)
            self.assertIn("unparseable-verifier", _live("sprint").ac_miss_vocabulary())

    def test_plan_refuses_unparseable_verify(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, {"US0001": UNPARSEABLE["US0001"][0]})
            rc, out, err = _call("plan", "--worklist", str(root / "wl.md"), "--root", str(root),
                                 "--write", "--no-fetch", "--skip-personas")
            self.assertNotEqual(0, rc, out + err)
            self.assertIn("US0001", out + err)
            self.assertIn(UNPARSEABLE["US0001"][1], out + err)
            self.assertFalse(_state(root).exists(), "the plan opened a run on the unit")

    def test_parseable_verify_still_groomed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, PARSEABLE)
            bd = _breakdown(root)
            self.assertEqual([], bd["ungroomed"], bd)
            self.assertEqual(set(PARSEABLE), set(bd["groomed"]))
            rc, out, err = _call("plan", "--worklist", str(root / "wl.md"), "--root", str(root),
                                 "--write", "--no-fetch", "--skip-personas")
            self.assertEqual(0, rc, out + err)
            self.assertTrue(_state(root).exists(), "the control plan opened no run")
        # `eval` and `manually` are the runner's own too, handled before its parser is asked.
        va = _live("verify_ac")
        for line in ("eval 1 + 1 == 2", "manually - read the page", "`manual`", *PARSEABLE.values()):
            with self.subTest(line=line):
                self.assertIsNone(va.parse_refusal(line))
        self.assertIsNotNone(va.parse_refusal("evaluate 1 + 1"))

    def test_only_the_criteria_the_runner_judges_are_asked(self) -> None:
        """MUTANT: ask every block in the file (`verify_ac.parse_story`) rather than the criteria
        `verify_ac.py run` judges (`verify_ac.criteria_blocks`), so a backtick-wrapped line under
        a later heading, which the runner never runs, refuses a unit whose criterion parses."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, {"US0021": "shell true\n\n## Superseded criteria\n\n"
                                          "### AC2: it held once\n\n"
                                          "- **Verify:** `file src/app.py`"})
            text = next((root / "sdlc-studio" / "stories").glob("US0021-*.md")).read_text(
                encoding="utf-8")
            va = _live("verify_ac")
            self.assertEqual(["AC1"], [b.ac_id for b in va.criteria_blocks(text)])
            self.assertIn("AC2", [b.ac_id for b in va.parse_story(text)],
                          "premise: the later heading's line is not a block in the file")
            self.assertEqual([], _live("conformance").unparseable_verifiers(text))
            bd = _breakdown(root)
            self.assertEqual(["US0021"], bd["groomed"], bd)
            self.assertEqual([], bd["ungroomed"], bd)

    def test_a_criteria_reader_that_raises_fails_open(self) -> None:
        """MUTANT: re-raise from `unparseable_verifiers`, so a criteria reader that raises stops
        `unit_is_ungroomed`, and `sprint.py breakdown` with it, rather than leaving the unit to
        the legs that could read it."""
        import unittest.mock  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, {"US0022": UNPARSEABLE["US0001"][0]})
            text = next((root / "sdlc-studio" / "stories").glob("US0022-*.md")).read_text(
                encoding="utf-8")
            conformance = _live("conformance")
            self.assertEqual((True, "unparseable-verifier"),
                             conformance.unit_is_ungroomed("story", text), "premise")
            with unittest.mock.patch.object(_live("verify_ac"), "criteria_blocks",
                                            side_effect=RuntimeError("the reader broke")):
                self.assertEqual([], conformance.unparseable_verifiers(text))
                self.assertEqual((False, ""), conformance.unit_is_ungroomed("story", text))
                bd = _breakdown(root)
            self.assertEqual(["US0022"], bd["groomed"], bd)


if __name__ == "__main__":
    unittest.main()
