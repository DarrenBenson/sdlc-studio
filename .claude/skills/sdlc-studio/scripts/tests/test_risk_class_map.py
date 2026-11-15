"""A declared component map gives each refined story a risk class.

The map is `risk.components` in the project's `sdlc-studio/.config.yaml`: path prefixes to one of
an ordered vocabulary, standard < elevated < high. `refine apply` stamps each story with the
highest class its Affects touch; with no map every story is standard and one line says so; an
entry naming an unknown class is reported in one line and read as standard. Nothing refuses.

The criteria are driven through the shipped entry point (`refine.main`) in throwaway trees.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import refine  # noqa: E402
from lib import risk_class, sdlc_md  # noqa: E402

_CR = ("# CR0001: a request\n\n> **Status:** Approved\n> **Priority:** P1\n"
       "> **Type:** Improvement\n> **Size:** L\n{affects}\n## Summary\n\ns\n\n"
       "## Acceptance Criteria\n\n- [ ] the request is satisfied\n\n## Impact\n\ni\n")

_FILES = ("src/ui/view.py", "src/pay/charge.py", "src/payroll.py", "docs/readme.md")


def _tree(root: Path, config: str | None, cr_affects: str | None = "src/pay/charge.py") -> None:
    for rel in _FILES:
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("x = 1\n", encoding="utf-8")
    crs = root / "sdlc-studio" / "change-requests"
    crs.mkdir(parents=True)
    line = f"> **Affects:** {cr_affects}\n" if cr_affects else ""
    (crs / "CR0001-a-request.md").write_text(_CR.format(affects=line), encoding="utf-8")
    if config is not None:
        (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")


def _apply(root: Path, stories: list[dict]) -> tuple[int, str]:
    """(exit code, everything `refine apply` printed), both streams captured."""
    spec = root / "breakdown.json"
    spec.write_text(json.dumps({"epic-title": "A slice", "stories": stories}), encoding="utf-8")
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = refine.main(["apply", "--request", "CR0001", "--breakdown", str(spec),
                          "--skip-personas", "--root", str(root)])
    return rc, out.getvalue() + err.getvalue()


def _classes(root: Path) -> dict[str, str | None]:
    """Each minted story's title -> its `Risk-class` field (None when it carries none)."""
    got = {}
    for p in sorted((root / "sdlc-studio" / "stories").glob("US*.md")):
        text = p.read_text(encoding="utf-8")
        title = sdlc_md.extract_h1_title(text).split(": ", 1)[1]
        got[title] = sdlc_md.extract_field(text, sdlc_md.RISK_CLASS_FIELD)
    return got


# The lower class comes first, in the map and in the 'Pay and UI' Affects, on purpose: a
# first-match reader then reads elevated where the highest class is high.
_MAP = ("risk:\n  components:\n    src/ui: elevated\n    src/pay/: high\n"
        "    docs: standard\n")


class RefineStampsClassTests(unittest.TestCase):
    def test_story_takes_highest_class_of_its_affects(self) -> None:
        """AC1. MUTANT: first match (map order or Affects order) -> 'Pay and UI' reads elevated.
        MUTANT: an unmapped-only story left unstamped or given a mapped class -> 'Unmapped'
        is not standard. MUTANT: stamp a story whose Affects is empty -> 'Bare' carries a field.
        MUTANT: plain string prefix -> src/payroll.py matches `src/pay/` and reads high."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, _MAP)
            rc, out = _apply(root, [
                {"title": "Pay and UI", "points": 2, "affects": "src/ui/view.py, src/pay/charge.py"},
                {"title": "UI only", "points": 1, "affects": "src/ui/view.py"},
                {"title": "Unmapped", "points": 1, "affects": "src/payroll.py"},
                {"title": "Inherited", "points": 1, "affects": "inherit"},
                {"title": "Seeded", "points": 1},
            ])
            self.assertEqual(0, rc, out)
            self.assertEqual({"Pay and UI": "high", "UI only": "elevated", "Unmapped": "standard",
                              "Inherited": "high", "Seeded": "high"}, _classes(root))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, _MAP + "sprint:\n  breakdown: judgement\n", cr_affects=None)
            rc, out = _apply(root, [{"title": "Bare", "points": 1}])
            self.assertEqual(0, rc, out)
            self.assertEqual({"Bare": None}, _classes(root),
                             "a story with no Affects touches no component and carries no class")


class NoMapTests(unittest.TestCase):
    def test_no_map_means_standard_one_line_exit_zero(self) -> None:
        """AC2. MUTANT: refuse or exit non-zero without a map. MUTANT: the note printed once per
        story -> two lines. MUTANT: no field when no map is declared -> a story reads None."""
        for config in (None, "sprint:\n  points_split_above: 8\n", "risk:\n  components: {}\n"):
            with self.subTest(config=config), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _tree(root, config)
                rc, out = _apply(root, [
                    {"title": "Pay", "points": 2, "affects": "src/pay/charge.py"},
                    {"title": "UI", "points": 1, "affects": "src/ui/view.py"},
                ])
                self.assertEqual(0, rc, out)
                self.assertEqual({"Pay": "standard", "UI": "standard"}, _classes(root))
                said = [ln for ln in out.splitlines() if "no component map" in ln]
                self.assertEqual(1, len(said), out)


class BadMapTests(unittest.TestCase):
    def test_unknown_class_is_reported_not_refused(self) -> None:
        """AC3. MUTANT: raise on the bad entry -> non-zero exit, nothing minted. MUTANT: drop it
        silently -> no line names it. MUTANT: keep the unknown class -> 'Pay' reads critical."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, "risk:\n  components:\n    src/pay: critical\n    src/ui: elevated\n")
            rc, out = _apply(root, [
                {"title": "Pay", "points": 2, "affects": "src/pay/charge.py"},
                {"title": "UI", "points": 1, "affects": "src/ui/view.py"},
            ])
            self.assertEqual(0, rc, out)
            self.assertEqual({"Pay": "standard", "UI": "elevated"}, _classes(root))
            said = [ln for ln in out.splitlines() if "critical" in ln]
            self.assertEqual(1, len(said), out)
            self.assertIn("src/pay", said[0])
            self.assertNotIn("no component map", out)

    def test_a_map_that_is_not_a_mapping_is_reported_and_read_as_none(self) -> None:
        """MUTANT: iterate a list as if it were the map -> an exception, or a story stamped from
        it. MUTANT: say nothing about it, or say only that no map is declared -> no line says
        the declared value is not a mapping."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, "risk:\n  components:\n    - src/pay\n")
            rc, out = _apply(root, [{"title": "Pay", "points": 2, "affects": "src/pay/charge.py"}])
            self.assertEqual(0, rc, out)
            self.assertEqual({"Pay": "standard"}, _classes(root))
            said = [ln for ln in out.splitlines() if "risk.components" in ln]
            self.assertEqual(1, len(said), out)
            self.assertIn("not a mapping", said[0])


class ClassifyTests(unittest.TestCase):
    """The order and the matcher the later readers (plan, review) import."""

    def test_the_vocabulary_is_fixed_and_ordered(self) -> None:
        self.assertEqual(("standard", "elevated", "high"), risk_class.CLASSES)
        self.assertLess(risk_class.rank("standard"), risk_class.rank("elevated"))
        self.assertLess(risk_class.rank("elevated"), risk_class.rank("high"))

    def test_highest_class_wins_and_names_the_components_touched(self) -> None:
        comps = {"src": "elevated", "src/pay": "high", "src/pay/legacy": "standard"}
        self.assertEqual(("high", ["src", "src/pay", "src/pay/legacy"]),
                         risk_class.classify(["src/pay/legacy/x.py"], comps))
        self.assertEqual(("elevated", ["src"]), risk_class.classify(["./src/a.py"], comps))

    def test_untouched_or_empty_reads_standard(self) -> None:
        comps = {"src/pay/": "high"}
        self.assertEqual(("standard", []), risk_class.classify(["src/payroll.py"], comps))
        self.assertEqual(("standard", []), risk_class.classify([], comps))
        self.assertEqual(("high", ["src/pay"]), risk_class.classify(["src/pay"], comps))

    def test_load_map_reads_the_config_key_and_folds_case(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "risk:\n  components:\n    ./src/pay/: High\n    src/pay: standard\n", encoding="utf-8")
            rmap = risk_class.load_map(root)
            self.assertEqual({"src/pay": "high"}, rmap.components)
            self.assertEqual((), rmap.notes)
            self.assertEqual(("high", ["src/pay"]),
                             rmap.classify_affects("src/pay/charge.py (the charge path)"))


if __name__ == "__main__":
    unittest.main()
