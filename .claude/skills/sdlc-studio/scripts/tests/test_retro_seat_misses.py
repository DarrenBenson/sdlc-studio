"""US1064: `retro.py seats` charges a later bug to the APPROVE that missed it, by the narrow rule.

A bug created inside the retro's window (after the previous retro's Date, on or before this
retro's) is charged to every seat whose latest verdict on a unit it cites approved, but only when
the bug shares an Affects file with that unit and cites three US, BG or CR ids or fewer beside
its own, and never when its title reads `<unit> did not converge in review`. A bug carrying an
`Escaped-via` unit is charged to that unit's approver on the recorded link alone. A bug whose
Evidence names the unit's review, where the approving row carried a finding, reads as approved
over the seat's own finding, not as a miss. A seat is charged even when it reviewed nothing in
the batch.

Every case drives `retro.py` through its entry point over a throwaway project, with the seat
fixtures shared with the seat evidence tests.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
from test_retro_seat_evidence import (  # noqa: E402
    BUILDER, CRITIC, PRODUCT, QA, SCRIPTS, _git, _project, _seats, _write)

sys.path.insert(0, str(SCRIPTS))

RETROS = (("RETRO0001", "2026-10-01", "US0002"), ("RETRO0002", "2026-10-08", "US0002"))


def _bug(root: Path, bid: str, created: str, title: str, affects: str, body: str = "",
         evidence: str = "", escaped: str = "", shipped: str = "") -> None:
    """A bug artefact with the fields the record reads: title, Affects, Created, and optionally
    Evidence, Escaped-via and Shipped-in; `body` is its Summary."""
    fields = (f"> **Status:** Open\n> **Affects:** {affects}\n"
              + (f"> **Shipped-in:** {shipped}\n" if shipped else "")
              + (f"> **Evidence:** {evidence}\n" if evidence else "")
              + (f"> **Escaped-via:** {escaped}\n" if escaped else "")
              + f"> **Created:** {created}\n")
    _write(root, f"sdlc-studio/bugs/{bid}-defect.md",
           f"# {bid}: {title}\n\n{fields}\n## Summary\n\n{body}\n\n"
           "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
           f"| {created} | sdlc-studio | Created; see US0999, CR0901, CR0902 and CR0903 |\n")


def _record(root: Path) -> tuple[dict, str]:
    return json.loads(_seats(root, retro="RETRO0002").stdout), \
        _seats(root, "text", retro="RETRO0002").stdout


class SeatMissTests(unittest.TestCase):

    def test_a_later_bug_is_charged_by_the_narrow_rule(self) -> None:
        """AC1. Each excluded bug fails exactly one test, so dropping any of the shared-file
        test, the citation test, the three-id cap, the carried exclusion or the previous retro's
        window charges it. BG0002 sits on the window's upper day and cites exactly three ids, so
        a strict upper bound or a cap of fewer than three loses it; BG0012 cites four and BG0013
        sits on the previous retro's day."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0001", "APPROVE", PRODUCT, BUILDER, "2026-09-20", "none"),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-05", "none")],
                     retros=RETROS)
            a = "scripts/a.py"
            _bug(root, "BG0002", "2026-10-08", "the widget drops a row", a,
                 "US0001 drops the last row; the totals from CR0001 and CR0002 are short.")
            _bug(root, "BG0003", "2026-10-03", "the widget page is stale", "docs/x.md",
                 "The page US0001 changed is stale.")
            _bug(root, "BG0004", "2026-10-03", "the widget is slow", a, "It is slow.")
            _bug(root, "BG0006", "2026-10-03", "the sweep is wrong", a,
                 "US0001, BG0010, BG0011, CR0001 and CR0002 all read the sweep.")
            _bug(root, "BG0012", "2026-10-03", "the sweep is short", a,
                 "US0001, BG0010, CR0001 and CR0002 read it.")
            _bug(root, "BG0007", "2026-10-03",
                 "US0001 did not converge in review: round 2 REJECT findings", a,
                 "Carried from the review.")
            _bug(root, "BG0005", "2026-09-25", "the widget drops a column", a,
                 "US0001 drops a column.")
            _bug(root, "BG0013", "2026-10-01", "the widget drops a header", a,
                 "US0001 drops the header.")
            out, text = _record(root)
            missed = out["seats"]["product"]["missed"]
            self.assertEqual(["BG0002"], [m["bug"] for m in missed], missed)
            m = missed[0]
            self.assertEqual(("US0001", "2026-09-20", "narrow", ["scripts/a.py"], 3),
                             (m["unit"], m["approved"], m["rule"], m["shared"], m["ids"]))
            self.assertEqual({"since": "2026-10-01", "until": "2026-10-08"},
                             {k: out["window"][k] for k in ("since", "until")})
            self.assertIn("missed BG0002 after its 2026-09-20 approval of US0001: cites US0001 "
                          "among 3 id(s) and shares scripts/a.py", text)
            for bid in ("BG0003", "BG0004", "BG0005", "BG0006", "BG0007", "BG0012", "BG0013"):
                self.assertNotIn(bid, text)
            self.assertIn("bugs created after 2026-10-01 and on or before 2026-10-08", text)

    def test_a_bug_the_approver_raised_reads_approved_over_its_own_finding(self) -> None:
        """AC2. Mutants: every later bug read as a miss; every bug whose Evidence names a review
        read as the approver's own, though the approving row raised nothing (US0002) or the
        Evidence names another seat's review (US0003)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            finding = "[pre-existing] the header is slow to read (scripts/a.py:4)"
            _project(root, [("US0001", "APPROVE", PRODUCT, BUILDER, "2026-09-20", finding),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-09-20", "none"),
                            ("US0003", "APPROVE", PRODUCT, BUILDER, "2026-09-20", finding),
                            ("US0003", "APPROVE", QA, BUILDER, "2026-09-21", "none")],
                     units=("US0001", "US0002", "US0003"), retros=RETROS)
            a = "scripts/a.py"
            _bug(root, "BG0008", "2026-10-04", "the header is slow", a, "US0001 is slow.",
                 evidence="US0001 product review round 1")
            _bug(root, "BG0014", "2026-10-04", "the footer is slow", a, "US0002 is slow.",
                 evidence="US0002 product review round 1")
            _bug(root, "BG0015", "2026-10-04", "the sidebar is slow", a, "US0003 is slow.",
                 evidence="US0003 qa review round 1")
            out, text = _record(root)
            product = out["seats"]["product"]
            own = product["approved_over_own_finding"]
            self.assertEqual([("BG0008", "US0001")], [(o["bug"], o["unit"]) for o in own], own)
            self.assertEqual("the header is slow to read (scripts/a.py:4)", own[0]["finding"])
            self.assertEqual(["BG0014", "BG0015"], [m["bug"] for m in product["missed"]])
            self.assertEqual(["BG0015"], [m["bug"] for m in out["seats"]["qa"]["missed"]])
            self.assertIn("approved US0001 on 2026-09-20 over its own finding, later filed as "
                          "BG0008: the header is slow to read (scripts/a.py:4)", text)
            self.assertNotIn("missed BG0008", text)

    def test_a_seat_outside_the_batch_is_charged_its_misses(self) -> None:
        """AC3. Mutant: the record limited to the seats that reviewed this batch, so qa, which
        approved US0003 in an earlier run, is never charged BG0009. A recorded Escaped-via link
        is charged as it stands, past the narrow rule it would fail (five ids cited). A seat
        whose latest verdict before the bug rejects (US0005), or whose approval came after the
        bug (US0006), is not charged."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0003", "APPROVE", QA, BUILDER, "2026-09-10", "none"),
                            ("US0004", "APPROVE", QA, BUILDER, "2026-09-10", "none"),
                            ("US0005", "APPROVE", QA, BUILDER, "2026-09-10", "none"),
                            ("US0005", "REJECT", QA, BUILDER, "2026-09-12",
                             "[new] the total is wrong (scripts/a.py:9)"),
                            ("US0006", "APPROVE", QA, BUILDER, "2026-10-07", "none"),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-05", "none")],
                     units=("US0002", "US0003", "US0004", "US0005", "US0006"), retros=RETROS)
            _bug(root, "BG0009", "2026-10-06", "the export drops a field", "scripts/a.py",
                 "US0003 drops the field.")
            _bug(root, "BG0016", "2026-10-06", "the import drops a field", "scripts/a.py",
                 "US0004, BG0010, BG0011, CR0001 and CR0002 all read it.", escaped="US0004")
            _bug(root, "BG0017", "2026-10-06", "the total is still wrong", "scripts/a.py",
                 "US0005 totals wrongly.")
            _bug(root, "BG0018", "2026-10-06", "the count is wrong", "scripts/a.py",
                 "US0006 counts wrongly.")
            out, text = _record(root)
            self.assertEqual(["US0002"], out["units"])
            qa = out["seats"]["qa"]
            self.assertEqual([], qa["verdicts"])
            self.assertEqual([("BG0009", "US0003", "narrow"), ("BG0016", "US0004", "escaped-via")],
                             [(m["bug"], m["unit"], m["rule"]) for m in qa["missed"]])
            self.assertRegex(text, r"(?m)^  qa: no verdict of its own$")
            self.assertIn("missed BG0009 after its 2026-09-10 approval of US0003", text)
            self.assertIn("missed BG0016 after its 2026-09-10 approval of US0004: recorded as "
                          "Escaped-via US0004", text)

    def test_an_escaped_via_unit_with_no_live_verdict_is_charged_to_no_seat(self) -> None:
        """`escape.py trace --confirm` records a unit no review approved, since a proposal with
        no verdict can still be confirmed. The record names that bug as charged to no seat, with
        the reason, and goes on charging the rest of the window. Mutants: the unit looked up in
        the ledger unguarded (KeyError, exit 1); the bug dropped silently; the walk stopped at
        it, so BG0002 is never charged."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0001", "APPROVE", PRODUCT, BUILDER, "2026-09-20", "none")],
                     units=("US0001", "US0002", "US0007"), retros=RETROS)
            _git(root, "init", "-q")
            _git(root, "add", "-A")
            _git(root, "commit", "-q", "-m", "feat(US0007): round the total")
            _git(root, "tag", "v1.0.0")
            _bug(root, "BG0019", "2026-10-06", "the total rounds wrongly", "scripts/a.py",
                 "The total rounds wrongly.", shipped="v1.0.0")
            _bug(root, "BG0020", "2026-10-07", "the widget drops a row", "scripts/a.py",
                 "US0001 drops a row.")
            r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "escape.py"), "trace",
                                "--bug", "BG0019", "--confirm", "US0007", "--root", str(root)],
                               capture_output=True, text=True, timeout=300,
                               env=gitutil.git_env(), check=False)
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertIn("> **Escaped-via:** US0007",
                          (root / "sdlc-studio/bugs/BG0019-defect.md").read_text("utf-8"))
            out, text = _record(root)
            self.assertEqual([("BG0019", "US0007", "escaped-via")],
                             [(u["bug"], u["unit"], u["rule"]) for u in out["uncharged"]])
            self.assertIn("BG0019 is charged to no seat: recorded as Escaped-via US0007, but "
                          "US0007 has no live verdict in the ledger", text)
            self.assertEqual(["BG0020"], [m["bug"] for m in out["seats"]["product"]["missed"]])

    def test_a_bug_is_charged_once_and_never_through_a_superseded_approval(self) -> None:
        """Two retros dated one day are ordered by id, so a bug on that day is charged by the
        first alone; and an APPROVE recorded in error charges nobody. Mutants: the tie left
        unordered, so both retros charge BG0002; superseded rows read as verdicts that stood."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0001", "APPROVE", PRODUCT, BUILDER, "2026-09-20", "none"),
                            ("US0003", "APPROVE", QA, BUILDER, "2026-09-20", "none")],
                     units=("US0001", "US0003"),
                     retros=RETROS + (("RETRO0003", "2026-10-08", "US0001"),))
            _bug(root, "BG0002", "2026-10-08", "the widget drops a row", "scripts/a.py",
                 "US0001 drops a row.")
            _bug(root, "BG0009", "2026-10-06", "the export drops a field", "scripts/a.py",
                 "US0003 drops the field.")
            r = subprocess.run([sys.executable, "-B", str(CRITIC), "supersede", "--unit", "US0003",
                                "--date", "2026-09-20", "--reviewer", QA, "--verdict", "APPROVE",
                                "--reason", "recorded against the wrong unit", "--authorised-by",
                                "operator", "--boundary", "operator console", "--root", str(root)],
                               capture_output=True, text=True, timeout=300,
                               env=gitutil.git_env(), check=False)
            self.assertEqual(0, r.returncode, r.stderr)
            out, _text = _record(root)
            self.assertEqual(["BG0002"], [m["bug"] for m in out["seats"]["product"]["missed"]])
            self.assertEqual([], out["seats"].get("qa", {}).get("missed", []))
            later = json.loads(_seats(root, retro="RETRO0003").stdout)
            self.assertEqual("2026-10-08", later["window"]["since"])
            self.assertEqual([], later["seats"]["product"]["missed"])


    def _uncharged(self, out: dict) -> dict:
        return {u["bug"]: u for u in out["uncharged"]}

    def test_an_escaped_via_unit_with_only_a_reject_is_named_uncharged(self) -> None:
        """BG1463 AC1. US0004's only live verdict rejects, so no seat approved it. MUTANT: HEAD -
        BG0021 is on no line of the record."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0004", "REJECT", QA, BUILDER, "2026-09-10",
                             "[new] the total is wrong (scripts/a.py:9)"),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-05", "none")],
                     units=("US0002", "US0004"), retros=RETROS)
            _bug(root, "BG0021", "2026-10-06", "the import drops a field", "scripts/a.py",
                 "It drops a field.", escaped="US0004")
            out, text = _record(root)
            u = self._uncharged(out)["BG0021"]
            self.assertEqual(("US0004", "escaped-via"), (u["unit"], u["rule"]))
            self.assertIn("no review approved US0004", u["reason"])
            self.assertIn("BG0021 is charged to no seat: recorded as Escaped-via US0004, but no "
                          "review approved US0004", text)

    def test_an_escaped_via_unit_whose_approval_names_no_seat_is_named_uncharged(self) -> None:
        """BG1463 AC2. The live APPROVE on US0004 was recorded by a reviewer naming no seat.
        MUTANT: HEAD - the approval charges no seat and the bug drops silently. MUTANT: read the
        seatless approval as no approval - the reason says no review approved it. On US0011 a
        seated qa REJECT stands beside the APPROVE naming no seat. MUTANT: take the seat from
        every live row rather than the approvals - the REJECT's seat hides the seatless approval
        and the reason says no seat's latest verdict approves it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0004", "APPROVE", "general-purpose agent", BUILDER,
                             "2026-09-10", "none"),
                            ("US0011", "REJECT", QA, BUILDER, "2026-09-12",
                             "[new] the field is dropped (scripts/a.py:4)"),
                            ("US0011", "APPROVE", "general-purpose agent", BUILDER,
                             "2026-09-14", "none"),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-05", "none")],
                     units=("US0002", "US0004", "US0011"), retros=RETROS)
            _bug(root, "BG0022", "2026-10-06", "the import drops a field", "scripts/a.py",
                 "It drops a field.", escaped="US0004")
            _bug(root, "BG0030", "2026-10-06", "the export drops a field", "scripts/a.py",
                 "It drops a field.", escaped="US0011")
            out, text = _record(root)
            uncharged = self._uncharged(out)
            self.assertIn("the approval of US0004 names no seat", uncharged["BG0022"]["reason"])
            self.assertEqual("the approval of US0011 names no seat",
                             uncharged["BG0030"]["reason"])
            self.assertIn("BG0022 is charged to no seat", text)
            self.assertNotIn("BG0022", json.dumps(out["seats"]))
            self.assertNotIn("BG0030", json.dumps(out["seats"]))

    def test_an_approval_after_the_bug_is_named_uncharged_and_a_charged_bug_is_not(self) -> None:
        """BG1463 AC3. qa approved US0006 the day after BG0023 was created and US0003 before
        BG0024 was; US0009's only dated approval is after BG0028, beside an undated one. MUTANT: HEAD - BG0023 is dropped. MUTANT: name every escaped bug uncharged -
        BG0024, charged to qa, is listed beside it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0006", "APPROVE", QA, BUILDER, "2026-10-07", "none"),
                            ("US0009", "APPROVE", QA, BUILDER, "", "none"),
                            ("US0009", "APPROVE", QA, BUILDER, "2026-10-08", "none"),
                            ("US0003", "APPROVE", QA, BUILDER, "2026-09-10", "none"),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-05", "none")],
                     units=("US0002", "US0003", "US0006", "US0009"), retros=RETROS)
            _bug(root, "BG0023", "2026-10-06", "the count is wrong", "scripts/a.py",
                 "It counts wrongly.", escaped="US0006")
            _bug(root, "BG0028", "2026-10-06", "the sum is wrong", "scripts/a.py",
                 "It sums wrongly.", escaped="US0009")
            _bug(root, "BG0024", "2026-10-06", "the export drops a field", "scripts/a.py",
                 "It drops a field.", escaped="US0003")
            out, text = _record(root)
            uncharged = self._uncharged(out)
            self.assertEqual(["BG0023", "BG0028"], sorted(uncharged))
            self.assertIn("post-dates the bug: its earliest dated approval is 2026-10-08",
                          uncharged["BG0028"]["reason"], "an undated approval places nothing")
            self.assertIn("the approval of US0006 post-dates the bug", uncharged["BG0023"]["reason"])
            self.assertIn("2026-10-07", uncharged["BG0023"]["reason"])
            self.assertEqual(["BG0024"], [m["bug"] for m in out["seats"]["qa"]["missed"]])
            self.assertNotIn("BG0024 is charged to no seat", text)

    def test_the_post_dates_reason_reads_the_earliest_dated_approval(self) -> None:
        """qa approved US0010 before BG0029 was created and rejected it the day after; product
        approved it only after the bug. A seat did approve before the bug, so the approval does
        not post-date it, and the reason says no seat's latest verdict approves it. MUTANT: read
        the latest dated approval - product's 2026-10-08 - and the reason says the approval
        post-dates the bug while naming 2026-09-10, a day before it, as the earliest. Only a
        seated approval places a seat's approval: on US0012 a reviewer naming no seat approved
        before BG0031 and qa only after it, so qa's approval post-dates the bug. MUTANT: read the
        days of every approval, seated or not - the seatless 2026-09-10 comes first and the
        reason says no seat's latest verdict on US0012 approves it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0010", "APPROVE", QA, BUILDER, "2026-09-10", "none"),
                            ("US0010", "REJECT", QA, BUILDER, "2026-09-12",
                             "[new] the total is wrong (scripts/a.py:9)"),
                            ("US0010", "APPROVE", PRODUCT, BUILDER, "2026-10-08", "none"),
                            ("US0012", "APPROVE", "general-purpose agent", BUILDER,
                             "2026-09-10", "none"),
                            ("US0012", "APPROVE", QA, BUILDER, "2026-10-08", "none"),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-05", "none")],
                     units=("US0002", "US0010", "US0012"), retros=RETROS)
            _bug(root, "BG0029", "2026-10-06", "the total is wrong again", "scripts/a.py",
                 "It totals wrongly.", escaped="US0010")
            _bug(root, "BG0031", "2026-10-06", "the sum is wrong again", "scripts/a.py",
                 "It sums wrongly.", escaped="US0012")
            out, _text = _record(root)
            uncharged = self._uncharged(out)
            self.assertEqual("no seat's latest verdict on US0010 on or before 2026-10-06 "
                             "approves it", uncharged["BG0029"]["reason"])
            self.assertEqual("the approval of US0012 post-dates the bug: its earliest dated "
                             "approval is 2026-10-08, after the bug was created on 2026-10-06",
                             uncharged["BG0031"]["reason"])

    def test_an_escaped_via_unit_no_seat_still_approves_is_named_uncharged(self) -> None:
        """The rest of the uncharged cases: qa approved US0005 and then rejected it before the
        bug, a seat's approval of US0007 carries no date, and qa approved and then rejected US0008
        on the bug's own day. Each is named with its reason, so no escaped bug the record charges
        no seat goes unmentioned. MUTANT: read an undated seated approval as post-dating the bug
        (it dies indexing an empty list of days). MUTANT: an approval on the bug's day post-dates
        it - US0008 reads as approved late."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0005", "APPROVE", QA, BUILDER, "2026-09-10", "none"),
                            ("US0005", "REJECT", QA, BUILDER, "2026-09-12",
                             "[new] the total is wrong (scripts/a.py:9)"),
                            ("US0007", "APPROVE", QA, BUILDER, "", "none"),
                            ("US0008", "APPROVE", QA, BUILDER, "2026-10-06", "none"),
                            ("US0008", "REJECT", QA, BUILDER, "2026-10-06",
                             "[new] the round is wrong (scripts/a.py:3)"),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-05", "none")],
                     units=("US0002", "US0005", "US0007", "US0008"), retros=RETROS)
            _bug(root, "BG0025", "2026-10-06", "the total is still wrong", "scripts/a.py",
                 "It totals wrongly.", escaped="US0005")
            _bug(root, "BG0026", "2026-10-06", "the round is wrong", "scripts/a.py",
                 "It rounds wrongly.", escaped="US0007")
            _bug(root, "BG0027", "2026-10-06", "the floor is wrong", "scripts/a.py",
                 "It floors wrongly.", escaped="US0008")
            out, _text = _record(root)
            uncharged = self._uncharged(out)
            for bid, unit in (("BG0025", "US0005"), ("BG0026", "US0007"), ("BG0027", "US0008")):
                self.assertIn(f"no seat's latest verdict on {unit} on or before 2026-10-06 "
                              f"approves it", uncharged[bid]["reason"])

    def test_a_narrow_rule_bug_no_seat_approved_is_not_named_uncharged(self) -> None:
        """Only an Escaped-via link is named when it charges no seat: a bug read by the narrow
        rule whose unit's seat approved only after it (US0006) is weaker evidence and stays off
        the record, as before. MUTANT: name every unit that charges no seat."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, [("US0006", "APPROVE", QA, BUILDER, "2026-10-07", "none"),
                            ("US0002", "APPROVE", PRODUCT, BUILDER, "2026-10-05", "none")],
                     units=("US0002", "US0006"), retros=RETROS)
            _bug(root, "BG0018", "2026-10-06", "the count is wrong", "scripts/a.py",
                 "US0006 counts wrongly.")
            out, text = _record(root)
            self.assertEqual([], out["uncharged"])
            self.assertNotIn("BG0018", text)

    def _window_of_many(self, root: Path) -> None:
        """Twelve bugs in RETRO0002's window that each cite US0001 and US0002, which affect
        different files, with one Escaped-via unit no review approved, and two bugs citing a
        reviewed unit whose file is gone (US0008), which shares nothing and charges no seat."""
        _project(root, [("US0001", "APPROVE", PRODUCT, BUILDER, "2026-09-20", "none"),
                        ("US0002", "APPROVE", QA, BUILDER, "2026-09-21", "none"),
                        ("US0008", "APPROVE", QA, BUILDER, "2026-09-21", "none")],
                 units=("US0001", "US0002", "US0007"), retros=RETROS)
        _bug(root, "BG0197", "2026-10-04", "the gone gadget", "scripts/b.py",
             "US0008 wrote it.")
        _bug(root, "BG0198", "2026-10-04", "the gone widget", "scripts/a.py",
             "US0008 read it.")
        _write(root, "sdlc-studio/stories/US0002-widget.md",
               "# US0002: widget\n\n> **Status:** Done\n> **Points:** 2\n"
               "> **Affects:** scripts/b.py\n")
        for n in range(12):
            affects = ("scripts/a.py", "scripts/b.py", "scripts/a.py, scripts/b.py")[n % 3]
            _bug(root, f"BG01{n:02d}", "2026-10-04", f"defect {n}", affects,
                 "US0001 and US0002 both read it.")
        _bug(root, "BG0199", "2026-10-04", "the total rounds wrongly", "scripts/a.py",
             "It rounds wrongly.", escaped="US0007")

    def test_each_cited_unit_is_resolved_once_per_call(self) -> None:
        """BG1465 AC1. MUTANT: HEAD - one `find_by_id` per bug per cited unit, 12 for US0001.
        MUTANT: remember only a unit that has Affects - US0008, whose file is gone, is looked up
        again for each of the two bugs citing it."""
        import retro  # noqa: PLC0415 - in process, so the lookup can be counted
        from collections import Counter  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._window_of_many(root)
            real, seen = retro.sdlc_md.find_by_id, Counter()

            def counted(r, uid, *a, **k):
                seen[retro.sdlc_md.norm_id(uid)] += 1
                return real(r, uid, *a, **k)

            with mock.patch.object(retro.sdlc_md, "find_by_id", side_effect=counted):
                res = retro.seat_misses(root, root / "sdlc-studio/retros/RETRO0002-run.md")
            self.assertEqual(1, seen["US0001"], seen)
            self.assertEqual(1, seen["US0002"], seen)
            self.assertEqual(1, seen["US0008"], seen)
            self.assertEqual(1, max(seen.values()), seen)
            self.assertEqual(8, len(res["seats"]["product"]["missed"]))

    def test_the_charges_are_unchanged_by_the_single_lookup(self) -> None:
        """BG1465 AC2. `retro.py seats` charges what a lookup made per bug charges: product the
        eight bugs sharing scripts/a.py with US0001, qa the eight sharing scripts/b.py with
        US0002, each naming the file it shares, and BG0199 uncharged. MUTANT: cache by the bug
        rather than the unit, or one Affects set for every unit - a.py bugs are charged to qa."""
        import retro  # noqa: PLC0415 - in process, for the per-bug reference lookup
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._window_of_many(root)
            out, _text = _record(root)
            real = retro._charged_units

            def per_bug(r, text, own, reviewed, affects=None):
                return real(r, text, own, reviewed)

            with mock.patch.object(retro, "_charged_units", side_effect=per_bug):
                ref = retro.seat_misses(root, root / "sdlc-studio/retros/RETRO0002-run.md")
            self.assertEqual(json.loads(json.dumps(ref["seats"])),
                             {r: {k: out["seats"][r][k] for k in ref["seats"][r]}
                              for r in ref["seats"]})
            self.assertEqual(json.loads(json.dumps(ref["uncharged"])), out["uncharged"])
            shared = {r: sorted({(m["bug"], tuple(m["shared"])) for m in s["missed"]})
                      for r, s in ref["seats"].items()}
            a_bugs = [f"BG01{n:02d}" for n in range(12) if n % 3 != 1]
            b_bugs = [f"BG01{n:02d}" for n in range(12) if n % 3 != 0]
            self.assertEqual(sorted((b, ("scripts/a.py",)) for b in a_bugs), shared["product"])
            self.assertEqual(sorted((b, ("scripts/b.py",)) for b in b_bugs), shared["qa"])
            self.assertEqual(["BG0199"], [u["bug"] for u in out["uncharged"]])
            self.assertNotIn("BG0198", json.dumps(out["seats"]))
            self.assertNotIn("BG0197", json.dumps(out["seats"]))

    def test_the_tree_is_walked_once_however_many_units_the_window_cites(self) -> None:
        """BG1465. Over an unbounded window the stall was the walk, not the repeat: each unit's
        first lookup walked every artefact type, and this repository's window cites hundreds of
        reviewed units. One corpus cache over the call walks each type once, however many units
        are looked up, and the charges are unchanged. MUTANT: look each unit up outside the
        cache - the story tree is walked once per unit, twenty times."""
        import retro  # noqa: PLC0415 - in process, so the walks can be counted
        from collections import Counter  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            units = tuple(f"US01{n:02d}" for n in range(20))
            _project(root, [(u, "APPROVE", QA, BUILDER, "2026-09-21", "none") for u in units],
                     units=units, retros=RETROS)
            for n, uid in enumerate(units):
                _bug(root, f"BG02{n:02d}", "2026-10-04", f"defect {n}", "scripts/a.py",
                     f"{uid} read it.")
            real, walks = retro.sdlc_md._walk_artifact_files, Counter()

            def counted(type_, *a, **k):
                walks[type_] += 1
                return real(type_, *a, **k)

            with mock.patch.object(retro.sdlc_md, "_walk_artifact_files", side_effect=counted):
                res = retro.seat_misses(root, root / "sdlc-studio/retros/RETRO0002-run.md")
            self.assertEqual(sorted(f"BG02{n:02d}" for n in range(20)),
                             sorted(m["bug"] for m in res["seats"]["qa"]["missed"]))
            self.assertEqual(1, walks["story"], walks)
            self.assertEqual(1, max(walks.values()), walks)
            self.assertFalse(retro.sdlc_md.corpus_cache_active(), "the cache closes with the call")

if __name__ == "__main__":
    unittest.main()
