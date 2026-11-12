"""A Keep/Stop/Try retro that also carries a `## Actions raised` table has its rows read.

`validate` judges each row as it does in a retro of the older shape, so an undecided row fails
the content gate by name, and `dispose` reports the rows `validate` read rather than saying no
finding was recorded. A three-line retro with no such table is judged as before.

MUTANTS this must fail on: the three-line branch returning `findings: []` again; the rows read
but the undecided-row errors not raised; the rows read under another section; `dispose` reading
anything other than `validate`'s findings.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import retro  # noqa: E402

RID = "RETRO0001"
UNDECIDED = "the meter misses lane builders"
DECIDED = ("| the gate passed a stale page | BG0123 |",
           "| a flaky timing test | fixed-in: US0456 |",
           "| a doc nit | declined: cosmetic, no reader is misled |")


def _retro(root: Path, rows: tuple[str, ...] | None) -> Path:
    """A three-line retro; with `rows`, an Actions raised table holding them."""
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    body = ["# RETRO-0001: a sprint", "", "> **Date:** 2026-11-12", "> **Batch:** US0101", "",
            "## Keep", "", "- small units", "", "## Stop", "", "- plan review", "",
            "## Try", "", "- one more check", ""]
    if rows is not None:
        body += ["## Actions raised", "", "| Finding | Disposition |", "| --- | --- |",
                 *rows, ""]
    path = d / f"{RID}-a-sprint.md"
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def _cli(root: Path, *argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = retro.main(["--root", str(root), *argv, "--id", RID])
    return rc, out.getvalue()


class ThreeLineActionsRaisedTests(unittest.TestCase):
    def test_an_undecided_row_fails_validate_naming_the_row(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _retro(root, (*DECIDED, f"| {UNDECIDED} | |"))
            self.assertTrue(retro.is_three_line(
                (root / "sdlc-studio" / "retros" / f"{RID}-a-sprint.md").read_text("utf-8")),
                "premise: the retro is a three-line one")
            res = retro.validate(root, RID)
            rc, out = _cli(root, "validate")
            self.assertFalse(res["ok"])
            self.assertEqual(1, len(res["errors"]), res["errors"])
            self.assertIn(UNDECIDED, res["errors"][0])
            self.assertIn("not dispositioned", res["errors"][0])
            self.assertEqual(1, rc, out)
            self.assertIn("FAIL", out)
            self.assertIn(UNDECIDED, out)
            self.assertNotIn("all dispositioned", out)
            # The positive control: the same row decided, and the retro passes, counting all four.
            _retro(root, (*DECIDED, f"| {UNDECIDED} | declined: the lane reads it now |"))
            rc, out = _cli(root, "validate")
            self.assertEqual(0, rc, out)
            self.assertIn("4 finding(s) all dispositioned (1 filed, 1 fixed in-sprint, "
                          "2 declined)", out)
            # A three-line retro with no table is judged as it was: nothing to disposition.
            _retro(root, None)
            res = retro.validate(root, RID)
        self.assertTrue(res["ok"], res["errors"])
        self.assertEqual([], res["findings"])

    def test_validate_and_dispose_agree_on_the_findings(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _retro(root, (*DECIDED, f"| {UNDECIDED} | |"))
            direct = retro.dispositions_in(path.read_text(encoding="utf-8"))
            v_rc, v_out = _cli(root, "validate", "--format", "json")
            d_rc, d_out = _cli(root, "dispose", "--format", "json")
            t_rc, t_out = _cli(root, "dispose")
        self.assertEqual(4, len(direct), "premise: the table holds four rows")
        self.assertEqual(direct, json.loads(v_out)["findings"])
        self.assertEqual(direct, json.loads(d_out)["findings"])
        self.assertEqual((1, 1), (v_rc, d_rc), "both refuse while a row is undecided")
        self.assertEqual(["filed", "fixed", "declined", "undecided"],
                         [r["state"] for r in direct])
        self.assertEqual(1, t_rc, t_out)
        self.assertNotIn("no findings recorded", t_out)
        self.assertIn(f"[UNDECIDED] {UNDECIDED}", t_out)
        self.assertIn("4 finding(s): 1 filed, 1 fixed in-sprint, 1 declined, 1 undecided", t_out)


if __name__ == "__main__":
    unittest.main()
