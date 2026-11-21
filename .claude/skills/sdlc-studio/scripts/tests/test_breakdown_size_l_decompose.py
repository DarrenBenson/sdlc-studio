"""BG1021: a CR declared Size L or XL is listed for decomposition before the plan opens.

The grooming gate sizes a CR by T-shirt, and Size L is the top of that scale, yet the decompose
list read only Points at the split ceiling or five declared files. A Size L CR touching one file
was certified groomed and first priced after refine. Driven through `sprint.py breakdown --crs
Proposed --format json`, the shipped entry point, in a throwaway tree.

MUTANTS, each of which the test fails on: (1) the T-shirt is never read, as before (L and XL are
not listed); (2) every declared Size is read as large (S and M are listed); (3) only one of L and
XL is read as large.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")

_AC = ("\n## Acceptance Criteria\n\n### AC1: it behaves as recorded\n\n"
       "- **Given** the recorded state\n- **Verify:** shell true\n")


def _cr(root: Path, num: int, size: str) -> str:
    """A Proposed CR declared `size`, naming one file that exists, with no Points."""
    src = root / "src" / f"cr{num:04d}.py"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("x = 1\n", encoding="utf-8")
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"CR{num:04d}-x.md").write_text(
        f"# CR-{num:04d}: c\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
        f"> **Affects:** src/cr{num:04d}.py\n> **Size:** {size}\n{_AC}", encoding="utf-8")
    return f"CR{num:04d}"


class SizeLDecomposeTests(unittest.TestCase):

    def test_a_size_l_cr_is_flagged_for_decomposition(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ids = {size: _cr(root, n, size) for n, size in enumerate(("S", "M", "L", "XL"), 1)}
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = sprint.main(["breakdown", "--crs", "Proposed", "--root", str(root),
                                  "--format", "json"])
        self.assertEqual(0, rc, err.getvalue())
        data = json.loads(out.getvalue())
        self.assertEqual(sorted(ids.values()), sorted(data["groomed"]),
                         "the fixture CRs must all be groomed, or this tests the gate")
        listed = {u["id"]: u["why"] for u in data["decompose"]}
        self.assertEqual({ids["L"], ids["XL"]}, set(listed),
                         f"Size L and XL are the decompose signal, S and M are not: {listed}")
        self.assertIn("Size L", listed[ids["L"]])
        self.assertIn("Size XL", listed[ids["XL"]])


if __name__ == "__main__":
    unittest.main()
