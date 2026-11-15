"""US1062: `retro.py seats` scores each seat on its own verdicts and authored units.

A row is attributed to a seat by `critic.recorded_seat` on its Reviewer and Author cells, never
by a name heuristic; a row naming no seat is counted and named. A blocking finding of a later
round whose `file:line` no earlier round cites is charged only to a seat whose earlier verdict
on the unit approved. A superseded row is recorded in error, never a verdict that stood.

Every case drives `retro.py` through its entry point over a throwaway project's ledger.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
RETRO = SCRIPTS / "retro.py"
CRITIC = SCRIPTS / "critic.py"

QA = "Sam Eriksson (qa)"
PRODUCT = "Lena Marsh (product)"
BUILDER = "Dani Okafor (engineering)"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, rows: list[tuple]) -> None:
    """Two stories, three seat cards, a retro over both and a ledger of `rows`, each
    (unit, verdict, reviewer, author, date, issues)."""
    for role, holder in (("engineering", "Dani Okafor"), ("qa", "Sam Eriksson"),
                         ("product", "Lena Marsh")):
        _write(root, f"sdlc-studio/personas/seats/{role}.md",
               f"<!-- role: {role} -->\n# {holder} - {role} seat\n\ncharter\n")
    for uid in ("US0001", "US0002"):
        _write(root, f"sdlc-studio/stories/{uid}-widget.md",
               f"# {uid}: widget\n\n> **Status:** Done\n> **Points:** 2\n"
               "> **Affects:** scripts/a.py\n")
    _write(root, "sdlc-studio/retros/RETRO0001-run.md",
           "# RETRO0001: run\n\n> **Batch:** US0001, US0002\n")
    _write(root, "sdlc-studio/reviews/critic-verdicts.md",
           "# Critic Verdicts\n\n"
           "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Source | Issues |\n"
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
           + "".join(f"| {u} | {v} | {r} | {a} | {d} | - | full | - | {i} |\n"
                     for u, v, r, a, d, i in rows))


def _seats(root: Path, fmt: str = "json") -> subprocess.CompletedProcess:
    r = subprocess.run([sys.executable, "-B", str(RETRO), "--root", str(root), "seats", "--id",
                        "RETRO0001", "--format", fmt], capture_output=True, text=True,
                       timeout=300, env=gitutil.git_env(), check=False)
    assert r.returncode == 0, r.stderr
    return r


def _git(root: Path, *args: str, when: str | None = None) -> None:
    extra = {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when} if when else {}
    subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True,
                   timeout=60, env=gitutil.git_env(**extra))


class SeatEvidenceTests(unittest.TestCase):

    def test_each_seat_is_scored_on_the_rows_that_name_it(self) -> None:
        """AC1. Mutants: rows attributed through `critic.seat_for`, which gives the qa row
        that mentions the product finding to product; unattributed rows dropped, not counted."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rechecking = f"{QA} re-checking the product finding"
            _project(root, [
                ("US0001", "REJECT", rechecking, BUILDER, "2026-10-01", "[new] w is wrong (scripts/a.py:3)"),
                ("US0001", "APPROVE", rechecking, BUILDER, "2026-10-02", "none"),
                ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-01", "none"),
                ("US0002", "APPROVE", "independent-critic", BUILDER, "2026-10-02", "none"),
            ])
            out = json.loads(_seats(root).stdout)
            qa, product = out["seats"]["qa"], out["seats"]["product"]
            self.assertEqual((1, 1), (qa["reject"], qa["approve"]))
            self.assertEqual([{"unit": "US0001", "rounds": 2}], qa["converged"])
            self.assertEqual((0, 1), (product["reject"], product["approve"]))
            self.assertEqual(["US0002"], [v["unit"] for v in product["verdicts"]])
            self.assertEqual(4, out["rows"])
            self.assertEqual(["independent-critic"], [r["reviewer"] for r in out["unattributed"]])
            text = _seats(root, "text").stdout
            self.assertIn("1 of 4 verdict row(s) name no seat", text)
            self.assertIn("independent-critic", text)
            self.assertRegex(text, r"(?m)^  qa: 1 APPROVE, 1 REJECT")
            self.assertIn("reviewed US0001: converged in 2 round(s)", text)
            self.assertRegex(text, r"(?m)^  engineering: no verdict of its own$")

    def test_only_an_earlier_approval_is_charged_with_a_later_rounds_defect(self) -> None:
        """AC2. Mutant: a later-round finding charged to every earlier verdict, the seat's own
        REJECT included, so qa is blamed for US0002's round-2 finding."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [
                ("US0001", "APPROVE", PRODUCT, BUILDER, "2026-10-01", "none"),
                ("US0001", "REJECT", QA, BUILDER, "2026-10-05",
                 "[new] the guard reads the wrong field (scripts/a.py:12)"),
                ("US0002", "REJECT", QA, BUILDER, "2026-10-01",
                 "[new] the count is off by one (scripts/a.py:40)"),
                ("US0002", "REJECT", QA, BUILDER, "2026-10-05",
                 "[new] the repair drops the header (scripts/a.py:7)"),
            ])
            _git(root, "init", "-q")
            _write(root, "scripts/a.py", "x = 1\n")
            _git(root, "add", "scripts/a.py")
            _git(root, "commit", "-qm", "a", when="2026-09-20T12:00:00")
            _write(root, "scripts/a.py", "x = 2\n")
            _git(root, "commit", "-qam", "b", when="2026-10-03T12:00:00")
            out = json.loads(_seats(root).stdout)
            charged = out["seats"]["product"]["found_after_approval"]
            self.assertEqual(1, len(charged), charged)
            self.assertEqual(("US0001", 2, "scripts/a.py:12", 1, "changed"),
                             (charged[0]["unit"], charged[0]["round"], charged[0]["cites"],
                              charged[0]["approved_round"], charged[0]["file_changed"]))
            self.assertEqual("round:US0001r2", charged[0]["key"])
            self.assertEqual([], out["seats"]["qa"]["found_after_approval"])
            text = _seats(root, "text").stdout
            self.assertIn("scripts/a.py changed between 2026-10-01 and 2026-10-05", text)

    def _charged_file(self, approved: str, found: str, commits: tuple,
                      cite: str = "scripts/a.py:12") -> str:
        """The `file_changed` answer for a product APPROVE then a qa REJECT citing `cite`, over
        a repository committing scripts/a.py on each of `commits` (no repository at all when
        `commits` is empty)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [
                ("US0001", "APPROVE", PRODUCT, BUILDER, approved, "none"),
                ("US0001", "REJECT", QA, BUILDER, found, f"[regression] w breaks ({cite})"),
            ])
            if commits:
                _git(root, "init", "-q")
            for n, day in enumerate(commits):
                _write(root, "scripts/a.py", f"x = {n}\n")
                _git(root, "add", "scripts/a.py")
                _git(root, "commit", "-qm", f"c{n}", when=f"{day}T12:00:00")
            charged = json.loads(_seats(root).stdout)["seats"]["product"]["found_after_approval"]
            self.assertEqual(1, len(charged), charged)
            return charged[0]["file_changed"]

    def test_a_file_whose_change_cannot_be_read_says_so(self) -> None:
        """No history to read, two rows on one day, or a commit only on a boundary day: the
        record says it cannot be told, never that the file was unchanged or changed."""
        for approved, found, commits in (("2026-10-01", "2026-10-05", ()),
                                         ("2026-10-05", "2026-10-05", ("2026-09-20",)),
                                         ("2026-10-01", "2026-10-05", ("2026-09-20", "2026-10-01"))):
            with self.subTest(approved=approved, found=found, commits=commits):
                self.assertEqual("cannot be told", self._charged_file(approved, found, commits))
        # a path the history never tracked says nothing about the file the finding meant
        self.assertEqual("cannot be told", self._charged_file(
            "2026-10-01", "2026-10-05", ("2026-09-20",), cite="lib/b.py:3"))

    def test_a_file_untouched_between_the_rows_is_unchanged(self) -> None:
        """History that holds no commit to the file across both rows' days reads unchanged."""
        self.assertEqual("unchanged", self._charged_file("2026-10-01", "2026-10-05",
                                                         ("2026-09-20",)))

    def test_a_finding_an_earlier_round_cited_is_not_charged(self) -> None:
        """A round-2 finding at a `file:line` round 1 already cited is not new to round 2."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [
                ("US0001", "REJECT", QA, BUILDER, "2026-10-01", "[new] w is wrong (scripts/a.py:12)"),
                ("US0001", "APPROVE", PRODUCT, BUILDER, "2026-10-02", "none"),
                ("US0001", "REJECT", QA, BUILDER, "2026-10-03", "[new] still wrong (scripts/a.py:12)"),
            ])
            out = json.loads(_seats(root).stdout)
            self.assertEqual([], out["seats"]["product"]["found_after_approval"])

    def test_a_superseded_row_is_recorded_in_error_not_overturned(self) -> None:
        """AC3. Mutant: a superseded row read as an overturned finding, or counted as a verdict
        that stood."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [
                ("US0001", "APPROVE", QA, BUILDER, "2026-10-01", "none"),
                ("US0001", "APPROVE", PRODUCT, BUILDER, "2026-10-02", "none"),
            ])
            reason = "recorded against the wrong reviewer"
            r = subprocess.run([sys.executable, "-B", str(CRITIC), "supersede", "--unit", "US0001",
                                "--date", "2026-10-01", "--reviewer", QA, "--verdict", "APPROVE",
                                "--reason", reason, "--authorised-by", "operator", "--boundary",
                                "operator console", "--root", str(root)],
                               capture_output=True, text=True, timeout=300,
                               env=gitutil.git_env(), check=False)
            self.assertEqual(0, r.returncode, r.stderr)
            out = json.loads(_seats(root).stdout)
            qa = out["seats"]["qa"]
            self.assertEqual([], qa["verdicts"])
            self.assertEqual((0, 0), (qa["approve"], qa["reject"]))
            self.assertEqual([("US0001", "APPROVE", reason)],
                             [(e["unit"], e["verdict"], e["reason"]) for e in qa["recorded_in_error"]])
            self.assertEqual(1, out["rows"])
            self.assertIn(f"recorded in error: US0001 APPROVE 2026-10-01 ({reason})",
                          _seats(root, "text").stdout)

    def test_an_authoring_seat_is_scored_on_the_rounds_its_units_took(self) -> None:
        """AC4. Mutant: the Author cell never read, so rounds to converge reach no seat."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [
                ("US0001", "REJECT", QA, BUILDER, "2026-10-01", "[new] w is wrong (scripts/a.py:3)"),
                ("US0001", "REJECT", QA, BUILDER, "2026-10-02",
                 "[regression] the repair broke v (scripts/a.py:9); [pre-existing] BG0001 slow"),
                ("US0001", "APPROVE", QA, BUILDER, "2026-10-03", "none"),
            ])
            out = json.loads(_seats(root).stdout)
            built = out["seats"]["engineering"]["built"]
            self.assertEqual(1, len(built), built)
            self.assertEqual(("US0001", 3, True), (built[0]["unit"], built[0]["rounds"],
                                                   built[0]["converged"]))
            self.assertEqual([[ "w is wrong (scripts/a.py:3)"], ["the repair broke v (scripts/a.py:9)"],
                              []], [r["blocking"] for r in built[0]["rounds_detail"]])
            text = _seats(root, "text").stdout
            self.assertIn("built US0001: converged in 3 round(s)", text)
            self.assertIn("round 2 blocking: the repair broke v (scripts/a.py:9)", text)


if __name__ == "__main__":
    unittest.main()
