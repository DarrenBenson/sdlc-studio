"""BG0889: a padded table holding a wide or combining character is re-aligned by display width.

BG0867 re-aligned the table a write touched, but left any table holding a wide, combining or
format character exactly as written, because a character count is not what markdownlint's MD060
measures there. A padded index holding a CJK title therefore failed MD060 again after a status
transition rewrote one of its rows. The table is now measured as markdownlint's `string-width`
measures it: an east-asian wide or full-width character takes two columns, a combining mark or a
format character none.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402
REPO = SCRIPTS.parents[3]
MDL = REPO / "node_modules" / ".bin" / "markdownlint"
MDL_CONFIG = REPO / ".markdownlint.json"

_INDEX = """# Test Spec Registry

## All

| ID                       | Title       | Epic   | Status |
| ------------------------ | ----------- | ------ | ------ |
| [TS0001](TS0001-spec.md) | first spec  | EP0010 | Draft  |
| [TS0002](TS0002-spec.md) | 第二の仕様  | EP0010 | Draft  |
"""


def _md060(path: Path) -> str | None:
    """markdownlint's MD060 lines for `path` under this repository's config, or None when
    markdownlint is not installed."""
    if not MDL.is_file():                           # pragma: no cover - npm install not run
        return None
    proc = subprocess.run([str(MDL), "--config", str(MDL_CONFIG), str(path)],
                          capture_output=True, text=True, timeout=120)
    return "\n".join(ln for ln in (proc.stdout + proc.stderr).splitlines() if "MD060" in ln)


def _width(text: str) -> int:
    """Display width for these fixtures, written out here rather than borrowed from the code
    under test: a wide character two columns, a combining mark none, anything else one."""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F")
               else 0 if unicodedata.combining(ch) else 1 for ch in text)


def _display_pipes(line: str) -> list[int]:
    """Each unescaped pipe's display column, measured as MD060 measures it."""
    return [_width(line[:m.start()]) for m in re.finditer(r"(?<!\\)\|", line)]


class IndexWideAlignmentTests(unittest.TestCase):
    """AC1-AC2."""

    def test_a_cjk_table_is_realigned_after_a_rewrite(self) -> None:
        """AC1. MUTANT: HEAD's wide-character skip - the table is left alone, the rewritten row
        stays compact, and MD060 fails on it. MUTANT: pad by `len()` - the CJK row's pipes land
        five columns short."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            specs = root / "sdlc-studio" / "test-specs"
            specs.mkdir(parents=True)
            for n, title in ((1, "first spec"), (2, "第二の仕様")):
                (specs / f"TS000{n}-spec.md").write_text(
                    f"# TS000{n}: {title}\n\n> **Status:** Draft\n> **Epic:** EP0010\n",
                    encoding="utf-8")
            index = specs / "_index.md"
            index.write_text(_INDEX, encoding="utf-8")
            self.assertIn(_md060(index), ("", None), "the fixture is not lint-clean to begin with")
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / "transition.py"), "set", "--id", "TS0001",
                 "--status", "Complete", "--root", str(root)],
                capture_output=True, text=True, check=False, timeout=120)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            lines = index.read_text(encoding="utf-8").splitlines()
            start = lines.index(next(ln for ln in lines if ln.startswith("| ID")))
            table = lines[start:start + 4]
            self.assertIn("Complete", table[2])
            self.assertIn("第二の仕様", table[3])
            for ln in table[1:]:
                self.assertEqual(_display_pipes(table[0]), _display_pipes(ln), "\n".join(table))
            found = _md060(index)
            if found is None:                       # pragma: no cover - npm install not run
                self.skipTest(f"{MDL} not installed; the display-column check above still ran")
            self.assertEqual("", found, "\n".join(table))

    def test_a_combining_mark_is_measured_as_zero_width(self) -> None:
        """AC2. MUTANTS: HEAD returns the table unchanged; a width measured with `len()` puts the
        mark's row one column out. The control: a table none of whose rows changed is returned
        byte for byte."""
        mark = "é"                            # e + COMBINING ACUTE ACCENT: one column
        original = ("| Name    | Value |\n| ------- | ----- |\n"
                    f"| caf{mark}    | 1     |\n| plain   | 2     |\n")
        written = original.replace("| plain   | 2     |", "| plain | 22 |")
        out = sdlc_md.align_padded_tables(written, original)
        rows = out.splitlines()
        self.assertNotEqual(written, out, "the table was left as written")
        for ln in rows[1:]:
            self.assertEqual(_display_pipes(rows[0]), _display_pipes(ln), out)
        self.assertEqual(original, sdlc_md.align_padded_tables(original, original),
                         "an unchanged table was rewritten")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "table.md"
            path.write_text("# T\n\n" + out, encoding="utf-8")
            found = _md060(path)
            if found is None:                       # pragma: no cover - npm install not run
                self.skipTest(f"{MDL} not installed; the display-column check above still ran")
            self.assertEqual("", found, out)


if __name__ == "__main__":
    unittest.main()
