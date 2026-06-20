"""Unit tests for complexity.py (RFC0009 WS1). Hand-computed cognitive values pin
the SonarSource algorithm.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "complexity.py"


def _load():
    spec = importlib.util.spec_from_file_location("complexity", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["complexity"] = mod
    spec.loader.exec_module(mod)
    return mod


cx = _load()


def _cog(src: str, name: str) -> int:
    return next(f["cognitive"] for f in cx.analyse_source(src) if f["name"] == name)


def _cyc(src: str, name: str) -> int:
    return next(f["cyclomatic"] for f in cx.analyse_source(src) if f["name"] == name)


class CognitiveTests(unittest.TestCase):
    def test_two_flat_ifs(self) -> None:
        src = "def f(a, b):\n    if a:\n        return 1\n    if b:\n        return 2\n    return 0\n"
        self.assertEqual(_cog(src, "f"), 2)
        self.assertEqual(_cyc(src, "f"), 3)

    def test_nesting_else_and_boolop(self) -> None:
        src = ("def g(a, b, c):\n"
               "    if a:\n"
               "        if b and c:\n"
               "            return 1\n"
               "    else:\n"
               "        return 2\n"
               "    return 0\n")
        self.assertEqual(_cog(src, "g"), 5)   # if(1) + nested if(1+1) + boolop(1) + else(1)
        self.assertEqual(_cyc(src, "g"), 4)   # 1 + 2 ifs + 1 boolop branch

    def test_elif_chain_is_plus_one_each(self) -> None:
        src = ("def h(x):\n"
               "    if x == 1:\n        return 1\n"
               "    elif x == 2:\n        return 2\n"
               "    elif x == 3:\n        return 3\n"
               "    else:\n        return 0\n")
        self.assertEqual(_cog(src, "h"), 4)   # if + elif + elif + else, no nesting growth
        self.assertEqual(_cyc(src, "h"), 4)   # 1 + 3 If nodes

    def test_ternary(self) -> None:
        src = "def t(a):\n    return 1 if a else 2\n"
        self.assertEqual(_cog(src, "t"), 1)
        self.assertEqual(_cyc(src, "t"), 2)

    def test_same_operator_sequence_counts_once(self) -> None:
        src = "def b(a, b, c):\n    return a and b and c\n"
        self.assertEqual(_cog(src, "b"), 1)        # one boolean sequence
        src2 = "def b(a, b, c):\n    return a and b or c\n"
        self.assertEqual(_cog(src2, "b"), 2)       # two: alternation

    def test_nested_function_scored_separately(self) -> None:
        src = ("def outer(a):\n"
               "    def inner(b):\n"
               "        if b:\n            return b\n"
               "    if a:\n        return 1\n")
        self.assertEqual(_cog(src, "outer"), 1)        # inner not folded in
        self.assertEqual(_cog(src, "outer.inner"), 1)
        self.assertEqual(_cyc(src, "outer"), 2)        # only `if a`


class CognitiveSpecEdgeTests(unittest.TestCase):
    """Spec-deviation cases the critic flagged (RFC0009 - metric correctness)."""

    def test_comprehension_filter_counts(self) -> None:
        src = "def f(xs):\n    return [x for x in xs if x > 0]\n"
        self.assertEqual(_cog(src, "f"), 1)              # filter `if` = +1
        self.assertEqual(_cyc(src, "f"), 2)              # and consistent with cyclomatic

    def test_else_with_single_nested_if_is_not_an_elif(self) -> None:
        src = ("def f(a, b):\n"
               "    if a:\n        pass\n"
               "    else:\n"
               "        if b:\n            pass\n"
               "        else:\n            pass\n")
        self.assertEqual(_cog(src, "f"), 5)              # else nests; inner if/else one level deeper

    def test_real_elif_does_not_nest(self) -> None:
        src = ("def f(a, b):\n"
               "    if a:\n        pass\n"
               "    elif b:\n        pass\n"
               "    else:\n        pass\n")
        self.assertEqual(_cog(src, "f"), 3)              # if + elif + else, flat

    def test_nested_ternary_nests(self) -> None:
        src = "def f(a, b):\n    return 1 if a else (2 if b else 3)\n"
        self.assertEqual(_cog(src, "f"), 3)              # outer 1 + inner (1 + nesting 1)

    def test_match_guard_counts(self) -> None:
        src = ("def f(x):\n"
               "    match x:\n"
               "        case 1 if x > 0:\n            return 1\n"
               "        case _:\n            return 0\n")
        self.assertEqual(_cog(src, "f"), 2)              # match (1) + guard (1)


class FileAndDegradationTests(unittest.TestCase):
    def test_analyse_file_python(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.py"
            p.write_text("def f(a):\n    return 1 if a else 2\n", encoding="utf-8")
            out = cx.analyse_file(p)
            self.assertEqual(out[0]["name"], "f")
            self.assertEqual(out[0]["cognitive"], 1)

    def test_syntax_error_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bad.py"
            p.write_text("def f(:\n  pass\n", encoding="utf-8")
            self.assertEqual(cx.analyse_file(p), [])

    def test_non_python_without_lizard_is_unscored(self) -> None:
        # lizard is not a hard dep; absent, a .js file scores to [] (never raises).
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.js"
            p.write_text("function f(){ if(a){return 1} }\n", encoding="utf-8")
            try:
                import lizard  # noqa: F401
                self.skipTest("lizard installed - degradation path not exercised here")
            except ImportError:
                self.assertEqual(cx.analyse_file(p), [])


class ScanAndConfigTests(unittest.TestCase):
    def test_scan_tags_file_and_skips_ignored_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "pkg").mkdir()
            (root / "pkg" / "x.py").write_text("def f(a):\n    if a:\n        return 1\n", encoding="utf-8")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "junk.py").write_text("def z():\n    if 1:\n        pass\n", encoding="utf-8")
            files = {r["file"] for r in cx.scan(root)}
            self.assertIn("pkg/x.py", files)
            self.assertFalse(any("__pycache__" in f for f in files))

    def test_cognitive_high_default_and_override(self) -> None:
        self.assertEqual(cx.cognitive_high("/nonexistent-root-xyz"), cx.DEFAULT_COGNITIVE_HIGH)
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("config override needs PyYAML")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "complexity:\n  cognitive_high: 8\n", encoding="utf-8")
            self.assertEqual(cx.cognitive_high(root), 8)

    def test_cmd_scan_json_reports_hotspots(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # a deeply-nested function well over a low threshold
            (root / "deep.py").write_text(
                "def deep(a, b, c, d):\n"
                "    if a:\n        if b:\n            if c:\n                if d:\n"
                "                    return 1\n", encoding="utf-8")
            buf = io.StringIO()
            args = cx.build_parser().parse_args(["scan", "--root", str(root), "--threshold", "3", "--format", "json"])
            with redirect_stdout(buf):
                rc = args.func(args)
            self.assertEqual(rc, 0)
            data = json.loads(buf.getvalue())
            self.assertEqual(data["threshold"], 3)
            self.assertTrue(any(h["name"] == "deep" for h in data["hotspots"]))


class AssessTests(unittest.TestCase):
    """WS2: change blast-radius difficulty + refactor-first recommendation."""

    def _repo(self, d):
        root = Path(d)
        (root / "hot.py").write_text(
            "def deep(a, b, c, d):\n"
            "    if a:\n        if b:\n            if c:\n                if d:\n"
            "                    return 1\n", encoding="utf-8")
        (root / "simple.py").write_text("def s(a):\n    return a\n", encoding="utf-8")
        return root

    def test_hotspot_drives_high_difficulty_and_refactor_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            r = cx.assess(root, ["hot.py"], threshold=5)
            self.assertEqual(r["difficulty"], "high")
            self.assertTrue(r["refactor_first"])
            self.assertTrue(any("deep" in line for line in r["refactor_first"]))

    def test_simple_change_is_low_with_no_refactor_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            r = cx.assess(root, ["simple.py"], threshold=15)
            self.assertEqual(r["difficulty"], "low")
            self.assertEqual(r["refactor_first"], [])

    def test_missing_file_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            r = cx.assess(root, ["nope.py", "simple.py"], threshold=15)
            self.assertEqual(r["touched_functions"], 1)  # only simple.py's one function

    def test_recommendation_is_advisory_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            args = cx.build_parser().parse_args(
                ["assess", "--root", str(root), "--files", "hot.py", "--threshold", "5"])
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = args.func(args)
            self.assertEqual(rc, 0)  # never blocks (D3)
            self.assertIn("refactor-first", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
