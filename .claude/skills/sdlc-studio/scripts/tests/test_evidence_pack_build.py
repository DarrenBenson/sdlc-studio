"""`release_cut.py evidence-pack` writes one release's evidence pack from committed records.

Every test drives the shipped entry point in a throwaway git repository holding its own signed
report JSON, stories and verdict ledger; none reads this repository's real reports.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/evidence_pack.py
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
RELEASE_CUT = SCRIPTS / "release_cut.py"
PACK_REL = "sdlc-studio/reports/evidence-pack-6.4.0.md"

LEDGER_HEAD = ("# Critic Verdicts\n\n"
               "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Source | Issues |\n"
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")

US0001 = """# US0001: Widgets carry a colour

> **Status:** Done
> **Points:** 3

## Acceptance Criteria

- [x] **AC1:** Given a widget, when it is drawn, then it carries its colour.
  - **Verify:** pytest tests/test_widget.py::ColourTests::test_colour
- [ ] **AC2:** Given a grey widget, when it is drawn, then it is grey.
  - **Verify:** pytest tests/test_widget.py::ColourTests::test_grey
"""

US0002 = """# US0002: Gadgets report their size

> **Status:** Done
> **Points:** 2

## Acceptance Criteria

- **AC1:** Given a gadget, when asked, then it reports its size.
  - **Verify:** pytest tests/test_gadget.py::SizeTests::test_size
  - **Verified:** yes (2026-11-01)
- **AC2:** Given an empty gadget, when asked, then it reports zero.
  - **Verify:** pytest tests/test_gadget.py::SizeTests::test_zero
"""


def unit_file(unit: str, title: str) -> str:
    return (f"# {unit}: {title}\n\n> **Status:** Done\n> **Points:** 1\n\n"
            "## Acceptance Criteria\n\n"
            f"- [x] **AC1:** Given {title.lower()}, when built, then it holds.\n"
            f"  - **Verify:** pytest tests/test_{unit.lower()}.py\n")


def verdict_row(unit: str, verdict: str, reviewer: str, author: str, date: str,
                source: str = "-") -> str:
    return (f"| {unit} | {verdict} | {reviewer} | {author} | {date} | abcdef123456 | full "
            f"| {source} | none |\n")


def fig(key: str, value, source: str = "sdlc-studio/reports/runs/RUN-X.json") -> dict:
    return {"key": key, "value": value, "source": source}


def signature(rid: str, principal: str = "Dana Reviewer",
              signed_at: str = "2026-11-10T09:00:00Z") -> dict:
    return {"principal": principal, "signed_at": signed_at, "report": rid,
            "fingerprint": "0123456789abcdef"}


def report(rid: str, units, sig, known=()) -> dict:
    """A schema-2 report: `units` as (unit, path, points, outcome), `known` as (id, priority,
    detail)."""
    delivered = [{"unit_id": fig("unit_id", u, path), "unit_points": fig("unit_points", pts, path),
                  "unit_outcome": fig("unit_outcome", outcome), "unit_rounds": fig("unit_rounds", 1)}
                 for u, path, pts, outcome in units]
    issues = [{"issue_id": fig("issue_id", i), "issue_priority": fig("issue_priority", p),
               "issue_detail": fig("issue_detail", d)} for i, p, d in known]
    return {"schema": 2, "report_id": rid, "run_id": "RUN-X", "signature": sig,
            "sections": [
                {"key": "delivered", "title": "Delivered to plan", "figures": {},
                 "not_measured": None, "rows": delivered},
                {"key": "known_issues", "title": "Known issues handed over", "figures": {},
                 "not_measured": None, "rows": issues}]}


def write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_report(root: Path, data: dict) -> None:
    write(root, f"sdlc-studio/reports/{data['report_id']}.json", json.dumps(data, indent=2) + "\n")


S1 = "sdlc-studio/stories/US0001-widgets-carry-a-colour.md"
S2 = "sdlc-studio/stories/US0002-gadgets-report-their-size.md"
B3 = "sdlc-studio/bugs/BG0003-a-dropped-fix.md"
S4 = "sdlc-studio/stories/US0004-an-unsigned-unit.md"
S5 = "sdlc-studio/stories/US0005-an-unnamed-report-s-unit.md"


def project(root: Path, rpt1_known=(), rpt2_known=(), rpt1_sig=None, rpt2_sig=None) -> None:
    """A committed project: RPT0001 and RPT0002 signed, RPT0003 unsigned, RPT0004 signed but
    never named on the command line."""
    gitutil.git(["init", "-q"], root)
    write(root, S1, US0001)
    write(root, S2, US0002)
    write(root, B3, unit_file("BG0003", "A dropped fix"))
    write(root, S4, unit_file("US0004", "An unsigned unit"))
    write(root, S5, unit_file("US0005", "An unnamed report's unit"))
    write(root, "sdlc-studio/reviews/critic-verdicts.md", LEDGER_HEAD
          + verdict_row("US0001", "REJECT", "eng-seat", "builder-a", "2026-11-01")
          + verdict_row("US0001", "APPROVE", "eng-seat", "builder-a", "2026-11-02")
          + verdict_row("US0001", "APPROVE", "builder-a", "builder-a", "2026-11-02")
          + verdict_row("US0001", "APPROVE", "qa-seat", "builder-a", "2026-11-03")
          + verdict_row("US0005", "APPROVE", "eng-seat", "builder-b", "2026-11-04"))
    write_report(root, report("RPT0001", [
        ("US0001", S1, 3, "delivered"),
        ("BG0003", B3, 2, "dropped - carried at the review cap: BG0009")],
        rpt1_sig or signature("RPT0001"), rpt1_known))
    write_report(root, report("RPT0002", [("US0002", S2, 2, "delivered")],
                              rpt2_sig or signature("RPT0002", "Lee Operator",
                                                    "2026-11-12T16:30:00Z"), rpt2_known))
    write_report(root, report("RPT0003", [("US0004", S4, 1, "delivered")], None))
    write_report(root, report("RPT0004", [("US0005", S5, 1, "delivered")], signature("RPT0004")))
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "-m", "fixture"], root)


def run_pack(root: Path, *reports: str, version: str = "6.4.0") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(RELEASE_CUT), "--root", str(root), "evidence-pack",
         "--version", version, "--reports", ",".join(reports)],
        cwd=str(root), capture_output=True, text=True, env=gitutil.git_env())


def snapshot(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(root).parts}


def section(pack: str, unit: str) -> list[str]:
    """The lines of one unit's entry, from its heading to the next heading."""
    lines = pack.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith(f"### {unit}:"))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("#")), len(lines))
    return lines[start:end]


def passed_ids(entry: list[str]) -> list[str]:
    """The criterion ids listed under an entry's `Criteria passed:` line."""
    at = next(i for i, ln in enumerate(entry) if ln.startswith("- Criteria passed:"))
    out = []
    for ln in entry[at + 1:]:
        if not ln.startswith("  - "):
            break
        out.append(ln[4:].split(":", 1)[0])
    return out


class BuildPackTests(unittest.TestCase):
    def test_pack_lists_delivered_units_of_signed_reports(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root)
            before = snapshot(root)
            proc = run_pack(root, "RPT0001", "RPT0002")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            after = snapshot(root)
            changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
            self.assertEqual(changed, [PACK_REL], "the pack is the one file the build writes")
            pack = (root / PACK_REL).read_text(encoding="utf-8")
            headings = [ln for ln in pack.splitlines() if ln.startswith("### ")]
            self.assertEqual(headings, ["### US0001: Widgets carry a colour",
                                        "### US0002: Gadgets report their size"])
            self.assertNotIn("BG0003", pack, "a dropped unit is not a delivered change")
            self.assertNotIn("US0005", pack, "a report not named contributes nothing")
            self.assertNotIn("US0004", pack)
            self.assertTrue(pack.startswith("# Evidence pack: release 6.4.0\n"))
            self.assertIn(PACK_REL, proc.stdout)

    def test_unsigned_or_unknown_report_is_refused(self) -> None:
        for bad, says in (("RPT0003", "not signed"), ("RPT0099", "no committed report")):
            with self.subTest(report=bad), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                project(root)
                before = snapshot(root)
                proc = run_pack(root, "RPT0001", bad)
                self.assertNotEqual(proc.returncode, 0, proc.stdout)
                self.assertIn(bad, proc.stderr)
                self.assertIn(says, proc.stderr)
                self.assertNotIn("RPT0001", proc.stderr, "only the refused report is named")
                self.assertEqual(snapshot(root), before, "a refusal writes no pack")
                self.assertFalse((root / PACK_REL).exists())


class CommittedOnlyTests(unittest.TestCase):
    def test_working_tree_edits_do_not_change_the_pack(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root)
            self.assertEqual(run_pack(root, "RPT0001", "RPT0002").returncode, 0)
            first = (root / PACK_REL).read_bytes()
            (root / PACK_REL).unlink()
            # Dirty the unit's file, the verdict ledger and the report, uncommitted.
            write(root, S1, US0001.replace("- [x] **AC1:**", "- [ ] **AC1:**")
                  .replace("- [ ] **AC2:**", "- [x] **AC2:**")
                  .replace("Widgets carry a colour", "A dirty title"))
            with (root / "sdlc-studio/reviews/critic-verdicts.md").open("a", encoding="utf-8") as fh:
                fh.write(verdict_row("US0002", "APPROVE", "dirty-seat", "builder-c", "2026-11-09"))
            write_report(root, report("RPT0002", [("US0002", S2, 9, "delivered"),
                                                  ("US0005", S5, 1, "delivered")],
                                      signature("RPT0002", "Someone Else")))
            proc = run_pack(root, "RPT0001", "RPT0002")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual((root / PACK_REL).read_bytes(), first)
            self.assertFalse((root / "sdlc-studio/.local").exists(),
                             "the build needs and makes no local state")
            # A report only the working tree holds is unknown to the committed record.
            write_report(root, report("RPT0006", [("US0005", S5, 1, "delivered")],
                                      signature("RPT0006")))
            proc = run_pack(root, "RPT0001", "RPT0006")
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("RPT0006", proc.stderr)
            self.assertEqual((root / PACK_REL).read_bytes(), first)


class UnitEntryTests(unittest.TestCase):
    def test_entry_has_change_criteria_and_independent_reviewer(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root)
            self.assertEqual(run_pack(root, "RPT0001", "RPT0002").returncode, 0)
            pack = (root / PACK_REL).read_text(encoding="utf-8")

            one = section(pack, "US0001")
            self.assertIn("- What changed: Widgets carry a colour (3 points).", one)
            self.assertEqual(passed_ids(one), ["AC1"], "only the ticked criterion passed")
            self.assertIn("  - AC1: Given a widget, when it is drawn, then it carries its colour. "
                          "Verify: `pytest tests/test_widget.py::ColourTests::test_colour`", one)
            self.assertIn("- Criteria not ticked: AC2.", one)
            review = [ln for ln in one if ln.startswith("- Independent review:")]
            self.assertEqual(review, ["- Independent review: eng-seat APPROVE (2026-11-02); "
                                      "qa-seat APPROVE (2026-11-03)."])

            two = section(pack, "US0002")
            self.assertIn("- What changed: Gadgets report their size (2 points).", two)
            self.assertEqual(passed_ids(two), ["AC1"], "a Verified yes line ticks a criterion")
            self.assertIn("  - AC1: Given a gadget, when asked, then it reports its size. "
                          "Verify: `pytest tests/test_gadget.py::SizeTests::test_size`", two)
            self.assertIn("- Criteria not ticked: AC2.", two)
            self.assertIn("- Independent review: none recorded.", two)


class IndependenceAuthorityTests(unittest.TestCase):
    """The pack's independent reviewers are the ones the project's one authority,
    `critic.independence`, calls independent: never a self-review or the pre-gate sentinel."""

    def test_self_review_and_pre_gate_rows_are_not_independent(self) -> None:
        sys.path.insert(0, str(SCRIPTS))
        import critic  # noqa: PLC0415 - the authority the fixture rows are judged by
        rows = (("ctx-seat", "builder-b", f"self-review:{S2}"),
                ("old-seat", "pre-gate", "-"),
                ("qa-seat", "builder-b", "-"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root)
            with (root / "sdlc-studio/reviews/critic-verdicts.md").open("a", encoding="utf-8") as fh:
                for reviewer, author, source in rows:
                    fh.write(verdict_row("US0002", "APPROVE", reviewer, author, "2026-11-05",
                                         source))
            gitutil.git(["commit", "-qam", "more verdicts"], root)
            self.assertEqual([critic.independence(r, a, s)[0] for r, a, s in rows],
                             [False, False, True], "the fixture holds two rows the authority "
                             "refuses and one it accepts")
            proc = run_pack(root, "RPT0001", "RPT0002")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            two = section((root / PACK_REL).read_text(encoding="utf-8"), "US0002")
            self.assertEqual([ln for ln in two if ln.startswith("- Independent review:")],
                             ["- Independent review: qa-seat APPROVE (2026-11-05)."])


class SeatSpellingTests(unittest.TestCase):
    """One reviewing seat recorded under two spellings that `critic.same_identity` reads as one
    identity is one reviewer, shown by its latest verdict; two seats stay two."""

    def test_two_spellings_of_one_seat_are_one_reviewer(self) -> None:
        sys.path.insert(0, str(SCRIPTS))
        import critic  # noqa: PLC0415 - the authority the two spellings are judged by
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root)
            with (root / "sdlc-studio/reviews/critic-verdicts.md").open("a", encoding="utf-8") as fh:
                fh.write(verdict_row("US0002", "REJECT", "QA\\_Seat", "builder-b", "2026-11-05"))
                fh.write(verdict_row("US0002", "APPROVE", "qa_seat", "builder-b", "2026-11-06"))
                fh.write(verdict_row("US0002", "APPROVE", "eng-seat", "builder-b", "2026-11-07"))
            gitutil.git(["commit", "-qam", "two spellings of one seat"], root)
            self.assertTrue(critic.same_identity("QA\\_Seat", "qa_seat"))
            proc = run_pack(root, "RPT0001", "RPT0002")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            two = section((root / PACK_REL).read_text(encoding="utf-8"), "US0002")
            self.assertEqual([ln for ln in two if ln.startswith("- Independent review:")],
                             ["- Independent review: qa_seat APPROVE (2026-11-06); "
                              "eng-seat APPROVE (2026-11-07)."])


if __name__ == "__main__":
    unittest.main()
