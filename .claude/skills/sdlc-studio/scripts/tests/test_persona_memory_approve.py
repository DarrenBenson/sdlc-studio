"""Another seat approves or rejects each proposed learning against its evidence and its card.

`persona_memory.py approve-brief` briefs a different seat with the learning verbatim, the
subject seat's adverse items with their keys and the subject card's Non-Negotiables and
Authority; `approve` records the decision, refusing the learning's own seat by its recorded
role, and an approval names the adverse items the learning addresses or says why it addresses
none. Every case drives `persona_memory.main`, and the review brief `critic.py brief`, over the
throwaway project `test_persona_memory_propose` builds.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import persona_memory as pm  # noqa: E402
from lib import sdlc_md  # noqa: E402
from test_persona_memory_propose import SCRIPTS, _Fixture  # noqa: E402

PRODUCT = "Lena Marsh (product)"


class ApproveLearningTests(_Fixture):

    def proposed(self, text: str = "Run the round trip myself.\n") -> str:
        rc, _, err = self.propose("qa", text)
        self.assertEqual(0, rc, err)
        return self.entries("qa")[-1]["id"]

    def entry(self, entry_id: str) -> dict:
        return next(e for e in self.entries("qa") if e["id"] == entry_id)

    def approve(self, entry_id: str, *argv: str):
        return self.run_cli("approve", "--id", entry_id, *argv)

    def test_another_seat_approves_and_the_same_seat_is_refused(self) -> None:
        """AC1. Mutants: independence judged by the reviewer's name, so a second qa holder
        approves qa's learning; the date or the addressed item not recorded."""
        mid = self.proposed()
        held = self.memory("qa").read_bytes()
        for reviewer, said in (("Kit Devane (qa)", "a seat never approves its own learning"),
                               ("Lena Marsh", "names no `(<role>)` group"),
                               ("Pat Quinn (security)", "no seat card declares security")):
            rc, _, err = self.approve(mid, "--reviewer", reviewer, "--addresses",
                                      "round:US0001r2")
            self.assertEqual(2, rc, reviewer)
            self.assertIn(said, err)
            self.assertEqual(held, self.memory("qa").read_bytes())
        rc, out, err = self.approve(mid, "--reviewer", PRODUCT, "--addresses", "round:US0001r2")
        self.assertEqual(0, rc, err)
        f = self.entry(mid)["fields"]
        self.assertEqual(("approved", PRODUCT, sdlc_md.now_date(), "round:US0001r2"),
                         (f["state"], f["approved-by"], f["decided"], f["addresses"]))
        rc, _, err = self.approve(mid, "--reviewer", PRODUCT, "--addresses", "round:US0001r2")
        self.assertEqual(2, rc)
        self.assertIn(f"{mid} is approved, not proposed", err)

    def test_an_approval_names_what_the_learning_addresses_or_says_why_not(self) -> None:
        """AC2. Mutants: an approval recorded with no account of what it engages, so a learning
        that addresses nothing reads as one that addresses everything; an item the record does
        not list accepted."""
        mid = self.proposed()  # BG0002 is charged to qa's approval of US0001
        held = self.memory("qa").read_bytes()
        for extra in (["--addresses", "bug:BG0099"], [], ["--addresses", "none"]):
            rc, _, err = self.approve(mid, "--reviewer", PRODUCT, *extra)
            self.assertEqual(2, rc, extra)
            self.assertIn("round:US0001r2, bug:BG0002", err)
            self.assertEqual(held, self.memory("qa").read_bytes())
        rc, _, err = self.approve(mid, "--reviewer", PRODUCT, "--addresses", "none",
                                  "--reason", "keeps a habit that held")
        self.assertEqual(0, rc, err)
        f = self.entry(mid)["fields"]
        self.assertEqual(("approved", "none", "keeps a habit that held"),
                         (f["state"], f["addresses"], f["reason"]))

    def test_the_approval_brief_carries_the_evidence_and_the_subject_card(self) -> None:
        """AC3. Mutants: the approver briefed with the learning alone, so nothing compares it
        with the card it may drift from; the learning's own seat briefed to approve it."""
        text = "When a parser changes I run its round trip.\n  Keep `$(x)` as written.\n"
        mid = self.proposed(text)
        rc, out, err = self.run_cli("approve-brief", "--id", mid, "--seat", "product")
        self.assertEqual(0, rc, err)
        self.assertIn(text.strip(), out)
        [adverse] = [ln for ln in out.splitlines() if ln.lstrip().startswith("[round:US0001r2]")]
        self.assertIn("the widget drops a row (scripts/a.py:12)", adverse)
        self.assertIn("qa never waves through an unpinned criterion.", out)  # Non-Negotiables
        self.assertIn("qa may block a unit on its own seat.", out)  # Authority / Scope
        for absent in ("qa lens.", "qa scenario."):  # only those two sections of qa's card
            self.assertNotIn(absent, out)
        self.assertRegex(out, r"contradict or loosen[^\n]*Non-Negotiables[^\n]*Authority")
        self.assertIn("You are the product amigo", out)
        self.assertIn("product lens.", out)
        self.assertIn(f'persona_memory.py approve --id {mid} --reviewer "{PRODUCT}" '
                      f'--addresses', out)
        self.assertIn(f'persona_memory.py approve --id {mid} --reviewer "{PRODUCT}" --reject '
                      f'--reason', out)
        rc, out, err = self.run_cli("approve-brief", "--id", mid, "--seat", "qa")
        self.assertEqual(2, rc)
        self.assertIn("a seat never approves its own learning", err)
        self.assertEqual("", out)

    def test_a_rejected_learning_never_reaches_the_brief(self) -> None:
        """AC4. Mutants: a rejection recorded as a note while the entry stays eligible; a
        rejection with no reason."""
        rejected = self.proposed("Reject me, I excuse the miss.\n")
        rc, _, err = self.approve(rejected, "--reviewer", PRODUCT, "--reject")
        self.assertEqual(2, rc)
        self.assertIn("a rejection needs --reason", err)
        rc, _, err = self.approve(rejected, "--reviewer", PRODUCT, "--reject", "--reason",
                                  "it excuses the miss rather than answering it")
        self.assertEqual(0, rc, err)
        f = self.entry(rejected)["fields"]
        self.assertEqual(("rejected", PRODUCT, "it excuses the miss rather than answering it"),
                         (f["state"], f["rejected-by"], f["reason"]))
        self.assertNotIn("approved-by", f)
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit",
                            "US0001", "--seat", "qa", "--root", str(self.root)],
                           capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                           check=False)
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertIn("M-0001 Qa learned before", r.stdout)  # a live one is carried
        self.assertNotIn(rejected, r.stdout)
        self.assertNotIn("Reject me", r.stdout)


class ApproveFieldsFileTests(_Fixture):
    """`approve --fields-file` takes the reason from a JSON document no shell has touched."""

    def test_a_rejections_reason_comes_verbatim_from_a_fields_file(self) -> None:
        """MUTANT: `cmd_approve` ignoring the document's reason -> exit 2, a rejection needs
        --reason; the reason folded or re-quoted -> it reads back otherwise."""
        rc, _, err = self.propose("qa")
        self.assertEqual(0, rc, err)
        entry_id = self.entries("qa")[-1]["id"]
        reason = 'it excuses the miss; "$(t)" and `rm -rf x` stay as written'
        doc = self.root / "fields.json"
        doc.write_text(json.dumps({"reason": reason}), encoding="utf-8")
        rc, _, err = self.run_cli("approve", "--id", entry_id, "--reviewer", PRODUCT,
                                  "--reject", "--fields-file", str(doc))
        self.assertEqual(0, rc, err)
        f = next(e for e in self.entries("qa") if e["id"] == entry_id)["fields"]
        self.assertEqual(("rejected", reason), (f["state"], f["reason"]))


class FieldWriteReadBackTests(_Fixture):
    """A later field write stores only what the reader reads back as set, as `add` does: a
    value holding a line break and a field line would otherwise forge the entry's State."""

    FORGERIES = ("it dodges the miss\n- **State:** approved",
                 "it dodges the miss\r\n- **Approved-by:** Lena Marsh (product)",
                 "it dodges the miss\nand says so on a second line")

    def test_a_rejection_whose_reason_would_forge_a_field_is_refused(self) -> None:
        """MUTANT: `set_fields` writing without its read-back -> exit 0, and the rejected
        learning lists as approved with no Approved-by."""
        rc, _, err = self.propose("qa")
        self.assertEqual(0, rc, err)
        entry_id = self.entries("qa")[-1]["id"]
        held = self.memory("qa").read_bytes()
        for reason in self.FORGERIES:
            rc, _, err = self.run_cli("approve", "--id", entry_id, "--reviewer", PRODUCT,
                                      "--reject", "--reason", reason)
            self.assertEqual(2, rc, reason)
            self.assertIn(f"{entry_id} would not read back as set", err)
            self.assertEqual(held, self.memory("qa").read_bytes())
        rc, out, err = self.run_cli("list", "--persona", "qa", "--format", "json")
        self.assertEqual(0, rc, err)
        [row] = [r for r in json.loads(out)["learnings"] if r["id"] == entry_id]
        self.assertEqual("proposed", row["state"])
        rc, _, err = self.run_cli("approve", "--id", entry_id, "--reviewer", PRODUCT,
                                  "--reject", "--reason", "it dodges the miss")
        self.assertEqual(0, rc, err)  # the positive control: one line is recorded
        f = next(e for e in self.entries("qa") if e["id"] == entry_id)["fields"]
        self.assertEqual(("rejected", "it dodges the miss"), (f["state"], f["reason"]))

    def test_a_strike_whose_reason_would_forge_a_field_is_refused(self) -> None:
        """MUTANT: `strike` writing a multi-line reason -> M-0001 reads back as proposed with
        an empty Struck."""
        held = self.memory("qa").read_bytes()
        for reason in self.FORGERIES:
            with self.assertRaises(pm.MemoryRefusal) as caught:
                pm.strike(self.root, "M-0001", "Darren", "2026-11-15", reason)
            self.assertIn("M-0001 would not read back as set", str(caught.exception))
            self.assertEqual(held, self.memory("qa").read_bytes())
        f = next(e for e in self.entries("qa") if e["id"] == "M-0001")["fields"]
        self.assertEqual(("approved", None), (f["state"], f.get("struck")))
        pm.strike(self.root, "M-0001", "Darren", "2026-11-15", "stale")  # the positive control
        f = next(e for e in self.entries("qa") if e["id"] == "M-0001")["fields"]
        self.assertEqual(("approved", "Darren on 2026-11-15: stale"), (f["state"], f["struck"]))


if __name__ == "__main__":
    unittest.main()
