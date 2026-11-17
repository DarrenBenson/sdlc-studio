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
sys.path.insert(0, str(SCRIPTS))
import sprint_report  # noqa: E402 - the fingerprint `sprint sign` stamps, the one digest

RELEASE_CUT = SCRIPTS / "release_cut.py"
PACK_REL = "sdlc-studio/reports/evidence-pack-6.4.0.md"
RUNS_REL = "sdlc-studio/reports/runs"

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
              signed_at: str = "2026-11-10T09:00:00Z", **extra) -> dict:
    """A signature block; `report` stamps the report's own fingerprint on it, as `sprint sign`
    does, unless one is given."""
    return {"principal": principal, "signed_at": signed_at, "report": rid,
            "fingerprint": "", **extra}


def run_of(rid: str) -> str:
    """The run a fixture report belongs to: one run per report."""
    return f"RUN-{rid}"


def report(rid: str, units, sig, known=()) -> dict:
    """A schema-2 report: `units` as (unit, path, points, outcome), `known` as (id, priority,
    detail). Its fingerprint is the digest of its figures, and a signature that carries none
    is stamped with it, as `sprint sign` stamps the report it signs."""
    delivered = [{"unit_id": fig("unit_id", u, path), "unit_points": fig("unit_points", pts, path),
                  "unit_outcome": fig("unit_outcome", outcome), "unit_rounds": fig("unit_rounds", 1)}
                 for u, path, pts, outcome in units]
    issues = [{"issue_id": fig("issue_id", i), "issue_priority": fig("issue_priority", p),
               "issue_detail": fig("issue_detail", d)} for i, p, d in known]
    data = {"schema": 2, "report_id": rid, "run_id": run_of(rid), "signature": sig,
            "sections": [
                {"key": "delivered", "title": "Delivered to plan", "figures": {},
                 "not_measured": None, "rows": delivered},
                {"key": "known_issues", "title": "Known issues handed over", "figures": {},
                 "not_measured": None, "rows": issues}]}
    data["fingerprint"] = sprint_report.fingerprint(data)
    if isinstance(sig, dict) and not sig.get("fingerprint"):
        data["signature"] = {**sig, "fingerprint": data["fingerprint"]}
    return data


def write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_report(root: Path, data: dict) -> None:
    write(root, f"sdlc-studio/reports/{data['report_id']}.json", json.dumps(data, indent=2) + "\n")


def run_record_rel(rid: str) -> str:
    return f"{RUNS_REL}/{run_of(rid)}.json"


def seal(root: Path, data: dict) -> None:
    """Write a report and the tracked run record `sprint sign` leaves beside it: the record holds
    the same signature, or none for an unsigned report."""
    write_report(root, data)
    record = {"run_id": data["run_id"]}
    if data.get("signature"):
        record["signature"] = dict(data["signature"])
    write(root, run_record_rel(data["report_id"]), json.dumps(record, indent=2) + "\n")


def edit_json(root: Path, rel: str, change) -> None:
    """Apply `change` to the JSON file at `rel` in place."""
    data = json.loads((root / rel).read_text(encoding="utf-8"))
    change(data)
    write(root, rel, json.dumps(data, indent=2) + "\n")


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
    seal(root, report("RPT0001", [
        ("US0001", S1, 3, "delivered"),
        ("BG0003", B3, 2, "dropped - carried at the review cap: BG0009")],
        rpt1_sig or signature("RPT0001"), rpt1_known))
    seal(root, report("RPT0002", [("US0002", S2, 2, "delivered")],
                      rpt2_sig or signature("RPT0002", "Lee Operator", "2026-11-12T16:30:00Z"),
                      rpt2_known))
    seal(root, report("RPT0003", [("US0004", S4, 1, "delivered")], None))
    seal(root, report("RPT0004", [("US0005", S5, 1, "delivered")], signature("RPT0004")))
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

    def test_a_delegated_signature_is_disclosed_with_its_decision(self) -> None:
        """US1292 AC2: a change from a report signed under delegation says so on its Accountable
        line and names the decision; a change from the report the operator signed says nothing
        of delegation."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root, rpt1_sig=signature("RPT0001", delegated=True, decision="D0123"))
            proc = run_pack(root, "RPT0001", "RPT0002")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            pack = (root / PACK_REL).read_text(encoding="utf-8")
            held = {rid: json.loads((root / run_record_rel(rid)).read_text(encoding="utf-8"))[
                "signature"]["fingerprint"] for rid in ("RPT0001", "RPT0002")}
            lines = {unit: [ln for ln in section(pack, unit) if ln.startswith("- Accountable:")]
                     for unit in ("US0001", "US0002")}
            self.assertEqual(lines["US0001"], [
                "- Accountable: Dana Reviewer, whose signature on its report was entered under "
                "delegation, authorised by decision D0123, on 2026-11-10 over fingerprint "
                f"{held['RPT0001']}."])
            self.assertEqual(lines["US0002"], [
                "- Accountable: Lee Operator, who signed its report on 2026-11-12 over "
                f"fingerprint {held['RPT0002']}."])

    def test_a_delegation_the_run_record_does_not_hold_refuses_the_pack(self) -> None:
        """US1292: the disclosure is the run record's, so a report whose own signature drops or
        changes the delegation, or a delegated signature naming no decision, is no evidence."""
        for label, rpt1_sig, rel, change, says in (
                ("dropped from the report", signature("RPT0001", delegated=True,
                                                      decision="D0123"),
                 "sdlc-studio/reports/RPT0001.json",
                 lambda data: [data["signature"].pop(k) for k in ("delegated", "decision")],
                 "disagree on delegation"),
                ("another decision on the report", signature("RPT0001", delegated=True,
                                                             decision="D0123"),
                 "sdlc-studio/reports/RPT0001.json",
                 lambda data: data["signature"].update(decision="D0999"),
                 "disagree on delegation"),
                ("no decision", signature("RPT0001", delegated=True), None, None,
                 "names no authorising decision")):
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                project(root, rpt1_sig=rpt1_sig)
                if rel:
                    edit_json(root, rel, change)
                    gitutil.git(["commit", "-qam", "edited after signing"], root)
                before = snapshot(root)
                proc = run_pack(root, "RPT0001", "RPT0002")
                self.assertNotEqual(proc.returncode, 0, proc.stdout)
                self.assertIn("RPT0001", proc.stderr)
                self.assertIn(says, proc.stderr)
                self.assertNotIn("RPT0002", proc.stderr, "only the refused report is named")
                self.assertEqual(snapshot(root), before, "a refusal writes no pack")


class SignedReportIsVerifiedTests(unittest.TestCase):
    """BG1524: a report is evidence only when its figures still re-derive the fingerprint its
    committed run record signed, and that run record holds a signature that agrees with the
    report's on who signed. The untouched project is the passing control beside each refusal."""

    def refused(self, edit, *named: str) -> subprocess.CompletedProcess:
        """Commit `edit` over a signed project, build over both signed reports, and assert the
        build refuses, writes nothing and names each of `named`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root)
            self.assertEqual(run_pack(root, "RPT0001", "RPT0002").returncode, 0,
                             "the untouched project builds")
            (root / PACK_REL).unlink()
            edit(root)
            gitutil.git(["add", "-A"], root)
            gitutil.git(["commit", "-qm", "edited after signing"], root)
            before = snapshot(root)
            proc = run_pack(root, "RPT0001", "RPT0002")
            self.assertNotEqual(proc.returncode, 0, proc.stdout)
            self.assertEqual(snapshot(root), before, "a refusal writes no pack")
            self.assertFalse((root / PACK_REL).exists())
            for text in named:
                self.assertIn(text, proc.stderr)
            return proc

    def test_a_report_edited_after_signing_refuses_the_pack(self) -> None:
        def figure(data: dict) -> None:
            data["sections"][0]["rows"][0]["unit_points"]["value"] = 9

        def restamped(data: dict) -> None:
            # The figure moved and both fingerprints on the report were re-stamped to match it:
            # only the run record still holds what was signed.
            figure(data)
            data["fingerprint"] = data["signature"]["fingerprint"] = (
                sprint_report.fingerprint(data))

        for label, change in (("a figure", figure), ("a figure, re-stamped", restamped)):
            with self.subTest(label):
                proc = self.refused(
                    lambda root, change=change: edit_json(
                        root, "sdlc-studio/reports/RPT0001.json", change),
                    "RPT0001", "no longer re-derives its signed fingerprint")
                self.assertNotIn("RPT0002", proc.stderr, "only the edited report is named")

    def test_an_edited_principal_refuses_the_pack(self) -> None:
        proc = self.refused(
            lambda root: edit_json(root, "sdlc-studio/reports/RPT0002.json",
                                   lambda data: data["signature"].update(principal="Kim Other")),
            "RPT0002", "disagree on principal", "'Kim Other'", "'Lee Operator'")
        self.assertNotIn("RPT0001", proc.stderr, "only the edited report is named")

    def test_a_signature_the_run_record_does_not_hold_refuses_the_pack(self) -> None:
        """The report's own signature re-pointed at another fingerprint, its figures untouched,
        and a run record that signs another report: neither is the run's signature of it."""
        for label, rel, change, says in (
                ("re-pointed fingerprint", "sdlc-studio/reports/RPT0002.json",
                 lambda data: data["signature"].update(fingerprint="feedfacefeedface"),
                 "disagree on fingerprint"),
                ("re-dated", "sdlc-studio/reports/RPT0002.json",
                 lambda data: data["signature"].update(signed_at="2026-11-30T09:00:00Z"),
                 "disagree on signed_at"),
                ("another report signed", run_record_rel("RPT0002"),
                 lambda rec: rec["signature"].update(report="RPT0009"),
                 "signs RPT0009, not RPT0002")):
            with self.subTest(label):
                proc = self.refused(lambda root, rel=rel, change=change: edit_json(
                    root, rel, change), "RPT0002", says)
                self.assertNotIn("RPT0001", proc.stderr, "only the edited report is named")

    def test_a_report_with_no_signature_in_the_run_record_refuses_the_pack(self) -> None:
        rel = run_record_rel("RPT0002")
        for label, edit in (
                ("no signature", lambda root: edit_json(root, rel,
                                                        lambda rec: rec.pop("signature"))),
                ("an empty signature", lambda root: edit_json(
                    root, rel, lambda rec: rec.update(signature={}))),
                ("no run record", lambda root: (root / rel).unlink()),
                # The report itself, reached through a run id that leaves the runs folder,
                # would carry the very signature it is checked against.
                ("a run id outside the runs folder", lambda root: edit_json(
                    root, "sdlc-studio/reports/RPT0002.json",
                    lambda data: data.update(run_id="../RPT0002")))):
            with self.subTest(label):
                proc = self.refused(edit, "RPT0002", "unsigned in the run record")
                self.assertNotIn("RPT0001", proc.stderr, "only the unsigned report is named")


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
