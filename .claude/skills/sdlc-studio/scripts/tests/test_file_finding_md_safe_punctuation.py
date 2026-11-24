"""The filer's identifier wrapper leaves a sentence's closing punctuation outside the code span.

`_md_safe` backtick-wraps a bare identifier; the parenthesis that closes a parenthetical and the
full stop that ends a sentence are the sentence's, so they stay outside the span, while a call
keeps the parentheses it opens and closes itself.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding_md_safe_punctuation.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "file_finding.py"
sys.path.insert(0, str(SCRIPT.parent))
_spec = importlib.util.spec_from_file_location("file_finding", SCRIPT)
ff = importlib.util.module_from_spec(_spec)
sys.modules["file_finding"] = ff
_spec.loader.exec_module(ff)


class MdSafePunctuationTests(unittest.TestCase):
    def test_trailing_punctuation_outside_span(self) -> None:
        self.assertEqual(ff._md_safe("keys carry digits (API_KEY_2, TOKEN_V2) is reported"),
                         "keys carry digits (`API_KEY_2`, `TOKEN_V2`) is reported")
        self.assertEqual(ff._md_safe("ends with keep_alive."), "ends with `keep_alive`.")
        self.assertEqual(ff._md_safe("two stops: keep_alive.."), "two stops: `keep_alive`..")
        self.assertEqual(ff._md_safe("(see keep_alive)."), "(see `keep_alive`).")
        self.assertEqual(ff._md_safe("a leading one (_check) or _check."),
                         "a leading one (`_check`) or `_check`.")

    def test_balanced_call_keeps_its_parentheses(self) -> None:
        self.assertEqual(ff._md_safe("uses resolve_canonical(x) and f(a_b)."),
                         "uses `resolve_canonical(x)` and f(`a_b`).")
        self.assertEqual(ff._md_safe("calls run_it(a_b(c))."), "calls `run_it(a_b(c))`.")
        self.assertEqual(ff._md_safe("(see run_it(x))"), "(see `run_it(x)`)")

    def test_an_inner_dot_stays_in_the_span(self) -> None:
        self.assertEqual(ff._md_safe("open __init__.py. Then a_b.c and x_."),
                         "open `__init__.py`. Then `a_b.c` and `x_`.")


if __name__ == "__main__":
    unittest.main()
