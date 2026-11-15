"""Each change in a release's evidence pack states what is known wrong with it and who is
accountable for it.

The known issues are the signed reports' own `known_issues` rows; the accountable person is the
principal on the report's signature, with its date, since no per-unit accountable field exists.
Every test drives `release_cut.py evidence-pack` in a throwaway git repository of its own.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/evidence_pack.py
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
from test_evidence_pack_build import (  # noqa: E402
    PACK_REL, project, run_pack, section, signature, snapshot, verdict_row, write)

RPT1_KNOWN = (
    ("BG0010", "High", "US0001's colour fades after a restart"),
    ("BG0011", "Medium", "The release notes omit the upgrade step"),
    ("US0001", "Low", "Carried: a follow-up the close could not settle"),
    ("BG0013", "Low", "US00010 is a different unit from the first story"),
)
RPT2_KNOWN = (
    ("BG0012", "Medium", "Size is off by one for US0002 on an empty gadget"),
)

SELF_CHECKS_REL = "sdlc-studio/reviews/author-self-checks.md"


def record_identities(root: Path) -> None:
    """Commit the ids the project's own ledgers record: builder agents as authors (one only in
    the verdict ledger, one only in the self-check ledger, one as a typed `agent` triple) and
    the operator as a reviewer and as a typed `human` author."""
    with (root / "sdlc-studio/reviews/critic-verdicts.md").open("a", encoding="utf-8") as fh:
        fh.write(verdict_row("US0099", "APPROVE", "eng-seat", "Claude Opus 5.5 (builder)",
                             "2026-11-05"))
        fh.write(verdict_row("US0098", "APPROVE", "eng-seat", "sdlc-studio; agent; v1",
                             "2026-11-05"))
        fh.write(verdict_row("US0097", "APPROVE", "Darren Benson (operator, reviewer of record)",
                             "Darren Benson; human; n/a", "2026-11-05"))
        fh.write(verdict_row("US0096", "APPROVE", "Darren Benson", "builder-a", "2026-11-05"))
    write(root, SELF_CHECKS_REL, "# Author Self-Checks\n\n"
          "| Unit | Author | Date | Claims | Mutants | Digest |\n"
          "| --- | --- | --- | --- | --- | --- |\n"
          "| US0099 | Claude Sonnet 5.5 (builder) | 2026-11-05 | 1 | 1 | abc123 |\n")
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-qm", "recorded identities"], root)


def known_lines(entry: list[str]) -> list[str]:
    """The issue lines listed under an entry's `Known issues:` line, or its inline value."""
    at = next(i for i, ln in enumerate(entry) if ln.startswith("- Known issues:"))
    inline = entry[at][len("- Known issues:"):].strip()
    if inline:
        return [inline]
    out = []
    for ln in entry[at + 1:]:
        if not ln.startswith("  - "):
            break
        out.append(ln[4:])
    return out


def release_list(pack: str) -> list[str]:
    """The release-level known issues: the list under its own heading."""
    lines = pack.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln == "## Known issues not tied to one change")
    out = []
    for ln in lines[start + 1:]:
        if ln.startswith("#"):
            break
        if ln.startswith("- "):
            out.append(ln[2:])
    return out


class KnownWrongTests(unittest.TestCase):
    def test_known_issues_listed_per_change_and_for_the_release(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root, rpt1_known=RPT1_KNOWN, rpt2_known=RPT2_KNOWN)
            proc = run_pack(root, "RPT0001", "RPT0002")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            pack = (root / PACK_REL).read_text(encoding="utf-8")

            self.assertEqual(known_lines(section(pack, "US0001")), [
                "BG0010 (High): US0001's colour fades after a restart.",
                "US0001 (Low): Carried: a follow-up the close could not settle."])
            self.assertEqual(known_lines(section(pack, "US0002")), [
                "BG0012 (Medium): Size is off by one for US0002 on an empty gadget."])
            self.assertEqual(release_list(pack), [
                "BG0011 (Medium): The release notes omit the upgrade step.",
                "BG0013 (Low): US00010 is a different unit from the first story."])

    def test_a_change_no_issue_names_reads_none_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root, rpt1_known=RPT1_KNOWN)
            self.assertEqual(run_pack(root, "RPT0001", "RPT0002").returncode, 0)
            pack = (root / PACK_REL).read_text(encoding="utf-8")
            self.assertEqual(known_lines(section(pack, "US0002")), ["none recorded."])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root)
            self.assertEqual(run_pack(root, "RPT0001").returncode, 0)
            pack = (root / PACK_REL).read_text(encoding="utf-8")
            self.assertEqual(release_list(pack), ["None recorded."])


class AccountableTests(unittest.TestCase):
    def test_each_change_names_the_signing_principal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project(root)
            proc = run_pack(root, "RPT0001", "RPT0002")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            pack = (root / PACK_REL).read_text(encoding="utf-8")
            one = [ln for ln in section(pack, "US0001") if ln.startswith("- Accountable:")]
            two = [ln for ln in section(pack, "US0002") if ln.startswith("- Accountable:")]
            self.assertEqual(one, ["- Accountable: Dana Reviewer, who signed its report on "
                                   "2026-11-10."])
            self.assertEqual(two, ["- Accountable: Lee Operator, who signed its report on "
                                   "2026-11-12."])
            for ln in one + two:
                self.assertNotIn("builder-a", ln, "the author is never the accountable person")
                self.assertNotIn("seat", ln, "a reviewer is never the accountable person")

    def test_agent_or_blank_principal_is_refused(self) -> None:
        # The listed spellings, any principal holding the word agent, and an id the project's
        # own ledgers record as an author: an agent wrote that unit, so it is no person.
        for principal in ("", "   ", "-", "the agent", "The Agent", "agent", "an agent",
                          "agent-a6eab1e6", "Agent-7F3C", "subagent-12", "agent:builder",
                          "sub-agent", "an AI agent", "Agent (builder)", "Claude Opus 5.5 (builder)",
                          "claude opus 5.5 (builder)", "Claude Sonnet 5.5 (builder)",
                          "sdlc-studio", "builder-a"):
            with self.subTest(principal=principal), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                project(root, rpt2_sig=signature("RPT0002", principal, "2026-11-12T16:30:00Z"))
                record_identities(root)
                before = snapshot(root)
                proc = run_pack(root, "RPT0001", "RPT0002")
                self.assertNotEqual(proc.returncode, 0, proc.stdout)
                self.assertIn("RPT0002", proc.stderr)
                self.assertIn("accountable", proc.stderr)
                self.assertEqual(snapshot(root), before, "a refusal leaves no pack on disk")
        # Positive control: a person whose name begins like the word is a person, and so is the
        # operator the ledgers record as a reviewer and as a typed human author.
        for person in ("Agnes", "Agentha Ruiz", "Darren Benson"):
            with self.subTest(principal=person), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                project(root, rpt2_sig=signature("RPT0002", person, "2026-11-12T16:30:00Z"))
                record_identities(root)
                proc = run_pack(root, "RPT0001", "RPT0002")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                pack = (root / PACK_REL).read_text(encoding="utf-8")
                self.assertIn(f"- Accountable: {person}, who signed its report on 2026-11-12.",
                              section(pack, "US0002"))


if __name__ == "__main__":
    unittest.main()
