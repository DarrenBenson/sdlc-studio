"""US1165: a project sets builder and reviewer reasoning effort; the plan stamps it on each unit,
the lane brief names it, and a reviewer below its builder is refused without a recorded decision.

`routing.effort` holds a `builder` and a `reviewer` value, each one of inherit, low, medium, high,
xhigh or max, with inherit (the session's own effort) the default. It applies whether or not
model-tier routing is enabled. Driven through the shipped `sprint.py plan` and
`sprint.py lane brief` entry points, in-process, against a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")
from lib import run_state  # noqa: E402

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:  # pragma: no cover - config is read through PyYAML
    HAVE_YAML = False

UID = "US0101"
ALLOWED = ("inherit", "low", "medium", "high", "xhigh", "max")


def _live(name: str):
    """The module the command resolves at call time; another test module may re-register it."""
    return sys.modules.get(name) or importlib.import_module(name)


def _project(d: str, config: str = "") -> Path:
    """One groomed Ready story, a worklist naming it, and the project config given."""
    root = Path(d) / "repo"
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (root / "src").mkdir()
    (root / "src" / "app.py").write_text("", encoding="utf-8")
    (stories / f"{UID}-x.md").write_text(
        f"# {UID}: x\n\n> **Status:** Ready\n> **Affects:** src/app.py\n> **Points:** 2\n\n"
        "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** shell true\n",
        encoding="utf-8")
    (root / "wl.md").write_text(f"{UID}\n", encoding="utf-8")
    if config:
        (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")
    return root


def _plan(root: Path) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main(["plan", "--worklist", str(root / "wl.md"), "--root", str(root),
                                   "--format", "json"])
    return rc, out.getvalue(), err.getvalue()


def _row(stdout: str) -> dict:
    [row] = json.loads(stdout)["batch"]
    return row


def _brief(root: Path) -> str:
    run_state.open_run(root, batch=[UID], goal="g")
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main(["lane", "brief", "--units", UID, "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"lane brief refused ({rc}): {err.getvalue()}")
    return out.getvalue()


def _effort_lines(brief: str) -> list[str]:
    return [line for line in brief.splitlines() if line.startswith("Effort:")]


def _effort(builder: str, reviewer: str, extra: str = "") -> str:
    return f"routing:\n  effort:\n    builder: {builder}\n    reviewer: {reviewer}\n{extra}"


@unittest.skipUnless(HAVE_YAML, "the project config is read through PyYAML")
class EffortSettingTests(unittest.TestCase):

    def test_the_default_inherits_the_session_effort(self) -> None:
        """AC1. MUTANTS: a default other than inherit; a plan row with no effort; a brief silent
        on effort when none is set."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            rc, out, err = _plan(root)
            self.assertEqual(rc, 0, err)
            self.assertEqual(_row(out).get("effort"), {"builder": "inherit", "reviewer": "inherit"})
            lines = _effort_lines(_brief(root))
            self.assertEqual(len(lines), 1, f"expected one effort line, got {lines}")
            self.assertIn("at the session's own effort", lines[0])
            for level in ALLOWED[1:]:
                self.assertNotIn(f"{level} effort", lines[0])

    def test_a_set_effort_reaches_the_plan_and_the_lane_brief(self) -> None:
        """AC2, with model routing OFF (the default): effort is stamped whether or not routing
        is enabled. MUTANTS: the stamp gated on `routing.enabled`; a brief silent on a set
        effort; the builder and reviewer values swapped."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, _effort("low", "medium"))
            rc, out, err = _plan(root)
            self.assertEqual(rc, 0, err)
            row = _row(out)
            self.assertNotIn("tier", row, "the fixture must plan with model routing off")
            self.assertEqual(row.get("effort"), {"builder": "low", "reviewer": "medium"})
            lines = _effort_lines(_brief(root))
            self.assertEqual(len(lines), 1, f"expected one effort line, got {lines}")
            self.assertRegex(lines[0], r"builder at low effort\b.*reviewer at medium effort\b")
            self.assertNotIn("session's own effort", lines[0])

    def test_a_reviewer_below_its_builder_is_refused_without_a_decision(self) -> None:
        """AC3. MUTANTS: a lower reviewer accepted silently; a decision id that does not exist
        accepted; the accepted id not printed."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, _effort("high", "low"))
            rc, out, err = _plan(root)
            self.assertEqual(rc, 2, f"a reviewer below its builder planned:\n{out}{err}")
            self.assertRegex(err, r"\blow\b")
            self.assertRegex(err, r"\bhigh\b")
            self.assertIn("routing.effort.reviewer_below_builder", err)
            self.assertEqual(out.strip(), "", "a refused plan printed a batch")

            # A decision id the ledger does not hold is refused too, and named.
            (root / "sdlc-studio" / ".config.yaml").write_text(
                _effort("high", "low", "    reviewer_below_builder: D0042\n"), encoding="utf-8")
            rc, out, err = _plan(root)
            self.assertEqual(rc, 2, f"an absent decision id was accepted:\n{out}{err}")
            self.assertIn("D0042", err)

            # The positive control: the decision recorded, the plan runs and prints the id.
            (root / "sdlc-studio" / "decisions.md").write_text(
                "# Decisions\n\n| ID | Decision |\n| --- | --- |\n"
                "| D0042 | The reviewer may reason below its builder on this project. |\n",
                encoding="utf-8")
            rc, out, err = _plan(root)
            self.assertEqual(rc, 0, err)
            self.assertIn("D0042", err)
            self.assertEqual(_row(out).get("effort", {}).get("reviewer"), "low")

            # The same id named elsewhere in the ledger (not as a decision row) does not count.
            (root / "sdlc-studio" / "decisions.md").write_text(
                "# Decisions\n\n| ID | Decision |\n| --- | --- |\n"
                "| D0001 | Supersedes nothing; D0042 is only mentioned. |\n", encoding="utf-8")
            rc, _out, err = _plan(root)
            self.assertEqual(rc, 2, "an id only mentioned in another row was accepted")

    def test_an_equal_or_inheriting_reviewer_is_not_below_its_builder(self) -> None:
        """AC3's boundary. MUTANT: the comparison `<=` refuses an equal reviewer; inherit ranked."""
        for builder, reviewer in (("high", "high"), ("high", "inherit"), ("inherit", "low"),
                                  ("low", "max")):
            with self.subTest(builder=builder, reviewer=reviewer), \
                    tempfile.TemporaryDirectory() as d:
                rc, out, err = _plan(_project(d, _effort(builder, reviewer)))
                self.assertEqual(rc, 0, err)
                self.assertEqual(_row(out)["effort"], {"builder": builder, "reviewer": reviewer})

    def test_an_unknown_effort_value_is_refused(self) -> None:
        """AC4. MUTANTS: an unknown value passed through to the plan or the brief; the refusal
        silent on the key or on an allowed value."""
        for key, config in (("builder", _effort("turbo", "low")),
                            ("reviewer", _effort("low", "extreme")),
                            ("builder", _effort("off", "low"))):
            with self.subTest(key=key, config=config), tempfile.TemporaryDirectory() as d:
                root = _project(d, config)
                rc, out, err = _plan(root)
                self.assertEqual(rc, 2, f"an unknown effort planned:\n{out}{err}")
                self.assertIn(f"routing.effort.{key}", err)
                for level in ALLOWED:
                    self.assertRegex(err, rf"\b{level}\b")
                self.assertEqual(out.strip(), "", "a refused plan printed a batch")
                bad = re.search(r"(turbo|extreme|off|False)", config).group(1)
                lines = _effort_lines(_brief(root))
                self.assertEqual(len(lines), 1, f"expected one effort line, got {lines}")
                self.assertNotIn(bad, lines[0], "the brief passed the unknown value through")
                self.assertIn("session's own effort", lines[0])


if __name__ == "__main__":
    unittest.main()
