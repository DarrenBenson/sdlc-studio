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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
from test_retro_seat_evidence import (  # noqa: E402
    BUILDER, CRITIC, PRODUCT, QA, SCRIPTS, _git, _project, _seats, _write)

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


if __name__ == "__main__":
    unittest.main()
