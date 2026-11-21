"""`sprint plan` shows each unit's risk class and flags a unit whose files outrank its tag.

The class is the story's refine-time `Risk-class` tag; a bug carries none, so its class is read
from its Affects through the declared `risk.components` map. A unit tagged lower than a
component its Affects touch is flagged, naming the file, the component and both classes, for
the operator to confirm at plan approval. Nothing here refuses: the plan exits 0 either way.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import sprint  # noqa: E402

_MAP = "risk:\n  components:\n    src/ui: elevated\n    src/pay: high\n"
_AC = ("## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n"
       "- **Given** the recorded state\n- **Verify:** shell true\n\n")


def _src(root: Path, rel: str) -> str:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("def f():\n    return 1\n", encoding="utf-8")
    return rel


def _story(root: Path, num: int, affects: str, cls: str | None) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    tag = f"> **Risk-class:** {cls}\n" if cls else ""
    (d / f"US{num:04d}-s.md").write_text(
        f"# US{num:04d}: s\n\n> **Status:** Ready\n> **Affects:** {affects}\n"
        f"> **Points:** 2\n{tag}{_AC}", encoding="utf-8")


def _bug(root: Path, num: int, affects: str) -> None:
    d = root / "sdlc-studio" / "bugs"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"BG{num:04d}-b.md").write_text(
        f"# BG{num:04d}: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
        f"> **Affects:** {affects}\n> **Points:** 2\n{_AC}", encoding="utf-8")


def _tree(root: Path, config: str | None) -> None:
    if config is not None:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")


def _plan(root: Path, *extra: str) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(["plan", "--stories", "Ready", "--bugs", "Open", "--root", str(root),
                          "--no-fetch", "--skip-personas", *extra])
    return rc, out.getvalue() + err.getvalue()


def _risk_lines(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if "risk class" in ln.lower()]


class PlanShowsClassTests(unittest.TestCase):
    def test_plan_lists_class_per_unit_and_second_seat(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, _MAP)
            _story(root, 1, _src(root, "src/pay/charge.py"), "high")
            # Tagged elevated at refine, touching nothing the map names now: the plan lists the
            # tag, never a recomputed standard.
            _story(root, 2, _src(root, "src/core/a.py"), "elevated")
            _story(root, 3, _src(root, "src/core/b.py"), "standard")
            # A bug carries no tag: its class is read from its Affects through the map.
            _bug(root, 4, _src(root, "src/ui/view.py"))
            rc, text = _plan(root, "--write")
            self.assertEqual(0, rc, text)
            lines = _risk_lines(text)
            unit_line = {u: [ln for ln in lines if u in ln] for u in
                         ("US0001", "US0002", "US0003", "BG0004")}
            self.assertTrue(all(unit_line.values()), lines)
            self.assertIn("high", unit_line["US0001"][0])
            self.assertIn("second review seat: product", unit_line["US0001"][0])
            self.assertIn("elevated", unit_line["US0002"][0])
            self.assertIn("standard", unit_line["US0003"][0])
            self.assertIn("elevated", unit_line["BG0004"][0])
            self.assertIn("from Affects", unit_line["BG0004"][0])
            for u in ("US0002", "US0003", "BG0004"):
                self.assertNotIn("second review seat", unit_line[u][0])
            plan = json.loads((root / "sdlc-studio" / ".local" / "sprint-plan.json")
                              .read_text(encoding="utf-8"))
            units = plan["risk_classes"]["units"]
            self.assertEqual({"US0001": "high", "US0002": "elevated", "US0003": "standard",
                              "BG0004": "elevated"},
                             {u: v["class"] for u, v in units.items()})
            self.assertEqual("product", units["US0001"]["second_seat"])
            self.assertIsNone(units["US0003"]["second_seat"])
            self.assertEqual([], plan["risk_classes"]["flags"])

    def test_second_seat_differs_from_the_first_review_seat(self) -> None:
        self.assertNotEqual(sprint.FIRST_REVIEW_SEAT, sprint.second_review_seat("."))


class PlanFlagsHigherClassTests(unittest.TestCase):
    def test_flag_names_file_component_and_classes_and_never_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, _MAP)
            _story(root, 1, f"{_src(root, 'src/core/a.py')}, {_src(root, 'src/pay/x.py')}",
                   "standard")
            # Positive controls: a tag equal to, or above, what the files touch is not flagged.
            _story(root, 2, _src(root, "src/pay/y.py"), "high")
            _story(root, 3, _src(root, "src/ui/z.py"), "high")
            rc, text = _plan(root)
            self.assertEqual(0, rc, text)
            flags = [ln for ln in _risk_lines(text) if "FLAG" in ln]
            self.assertEqual(1, len(flags), flags)
            flag = flags[0]
            for want in ("US0001", "src/pay/x.py", "under src/pay (high)", "tagged standard"):
                self.assertIn(want, flag)
            self.assertNotIn("src/core/a.py", flag)
            self.assertNotIn("REFUSED", text)
            self.assertNotIn("sign-off", text.lower())
            self.assertNotIn("confirm each", text.lower())


class PlanNoMapTests(unittest.TestCase):
    def test_no_map_prints_one_line(self) -> None:
        for config in (None, "risk:\n  components: {}\n"):
            with self.subTest(config=config), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _tree(root, config)
                _story(root, 1, _src(root, "src/pay/charge.py"), "high")
                _bug(root, 2, _src(root, "src/ui/view.py"))
                rc, text = _plan(root)
                self.assertEqual(0, rc, text)
                lines = _risk_lines(text)
                self.assertEqual(1, len(lines), lines)
                self.assertIn("every unit is standard", lines[0])
                self.assertNotIn("US0001", lines[0])


if __name__ == "__main__":
    unittest.main()
