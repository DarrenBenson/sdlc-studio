"""US0923: a review verdict records with or without `--brief`, and the value is never judged.

`critic.py record` no longer refuses an absent brief, refuses a value that is not 12 hex
characters, or marks a fingerprint that matches no brief `unmatched`; the
`review.require_brief_provenance` key is gone. `critic.py brief` still briefs the seat. The
READER of the mark stays: historical rows carry `<fp> unmatched`, and `_brief_key` reading them
as unbriefed is what stops two of them pairing to answer a REJECT.

AC1 and AC2 drive the shipped entry point in throwaway workspaces. AC3 and AC4 read this
repository, because their criteria name its config defaults, its scripts and its stamps.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILL = SCRIPTS.parent
SCRIPT = SCRIPTS / "critic.py"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import workspace  # noqa: E402
import critic  # noqa: E402
import verify_ac  # noqa: E402
import test_lean_no_two_role as stamps  # noqa: E402 - the derived deleted-node check (US0916)

REPO = workspace.REPO
KEY = "require_brief_provenance"
#: A 12-hex value no brief in any fixture here renders.
UNMATCHED_HEX = "0123456789ab"
NOT_HEX = "hand-written-prompt"

#: The criteria whose selector named a test this story deletes, each retired in the D0259
#: pattern: the refusal and stand-down tests of `BriefProvenanceTests` (stamped by US0578) and
#: all of `UnmatchedBriefFingerprintTests` (BG0672).
RETIRED = {"US0578": ("AC1", "AC3"),
           "BG0672": ("AC1", "AC2", "AC3", "AC4", "AC5")}
#: Deleted nodes the derivation must find, as (class, test) - a whole class as (class, "").
DELETED = {("BriefProvenanceTests", "test_a_verdict_without_provenance_is_refused"),
           ("BriefProvenanceTests", "test_the_stand_down_is_stated_not_silent"),
           ("UnmatchedBriefFingerprintTests", "")}
#: Nodes that stay: BG0625's brief-key rule survives, and so does what US0577 and US0578 AC2
#: stamp on the fingerprint being printed, recorded and stable.
KEPT = {("AbsentBriefTests", ""),
        ("BriefProvenanceTests", "test_a_verdict_records_the_brief_it_was_given"),
        ("BriefProvenanceTests", "test_the_fingerprint_identifies_the_brief"),
        ("BriefProvenanceTests", "test_a_hand_written_prompt_records_no_provenance"),
        ("BriefProvenanceTests", "test_the_fingerprint_is_stable_across_calls"),
        ("BriefProvenanceTests", "test_a_briefed_verdict_records_cleanly")}


def _project(root: Path, *, seats: bool) -> None:
    """A unit at Review in a project that still asks for provenance; seat cards optional, as a
    fresh `init run` project has none."""
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / "US0001-x.md").write_text(
        "# US0001: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
        "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n"
        "### AC1: the widget spins\n\n- **Then** the widget spins clockwise\n",
        encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(
        f"review:\n  {KEY}: true\n", encoding="utf-8")
    if seats:
        _seat_cards(root)


def _seat_cards(root: Path) -> None:
    cards = root / "sdlc-studio" / "personas" / "seats"
    cards.mkdir(parents=True, exist_ok=True)
    for role in ("engineering", "product", "qa"):
        (cards / f"{role}.md").write_text(
            f"<!-- role: {role} -->\n# The {role} seat\n\n## Lens\n\nJudge as {role}.\n",
            encoding="utf-8")


def _cli(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *argv, "--root", str(root)],
                          capture_output=True, text=True, check=False, timeout=300)


def _record(root: Path, *extra: str) -> subprocess.CompletedProcess:
    return _cli(root, "record", "--unit", "US0001", "--verdict", "APPROVE",
                "--reviewer", "qa seat", "--author", "dev", *extra)


class BriefProvenanceGoneTests(unittest.TestCase):
    def test_record_needs_no_brief(self) -> None:
        """AC1. MUTANTS: restore the `if required: return 2` refusal (red on the exit); restore
        the stand-down NOTE (red on the output); delete the `brief` verb with the refusal (red on
        the control). The record runs before any seat card exists, as on a fresh project."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, seats=False)
            r = _record(root)
            out = r.stdout + r.stderr
            self.assertEqual(0, r.returncode, out)
            self.assertNotIn("provenance", out.lower(), out)
            self.assertNotIn("NOTE", out, out)
            rows = critic.read_verdicts(root)
            self.assertEqual([("US0001", "APPROVE", "-")],
                             [(x["unit"], x["verdict"], x["brief"]) for x in rows])
            # The control: the brief verb still briefs the seat.
            _seat_cards(root)
            b = _cli(root, "brief", "--unit", "US0001", "--seat", "qa")
            self.assertEqual(0, b.returncode, b.stderr)
            charter = root / "sdlc-studio" / "personas" / "seats" / "qa.md"
            self.assertIn("You are the qa review seat", b.stdout)
            self.assertIn(str(charter), b.stdout, "the brief does not point at the seat charter")
            self.assertIn("Diff scope", b.stdout)
            self.assertIn("src/widget.py", b.stdout, "the bounded diff scope is missing")
            self.assertIn("the widget spins clockwise", b.stdout, "the criteria are missing")
            self.assertRegex(b.stderr, r"brief fingerprint: [0-9a-f]{12}")

    def test_a_brief_value_is_stored_not_judged(self) -> None:
        """AC2. MUTANTS: restore the 12-hex refusal (red on the non-hex value); restore the
        unmatched writer (red on the 12-hex value); delete `_brief_key`'s mark test with its
        writer (red on the historical pair, which then answers the REJECT)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, seats=True)
            for value in (NOT_HEX, UNMATCHED_HEX):
                with self.subTest(brief=value):
                    r = _record(root, "--brief", value)
                    out = r.stdout + r.stderr
                    self.assertEqual(0, r.returncode, out)
                    self.assertNotIn("refused", out, out)
                    self.assertNotIn(critic.UNMATCHED_MARK, out, out)
                    self.assertEqual(value, critic.read_verdicts(root)[-1]["brief"],
                                     "the value was not stored as given")

        # History: two rows marked by the retired writer, dated before the round rule, when a
        # shared fingerprint still paired rounds. Marked, they are unbriefed and do not pair;
        # the same pair unmarked does, the control that the fixture can pair at all.
        head = ("# Critic Verdicts\n\n"
                "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n")
        date = "2026-09-01"
        self.assertLess(date, critic.ROUND_RULE_SHIPPED, "the fixture is not historical")
        for cell, want in ((f"{UNMATCHED_HEX} {critic.UNMATCHED_MARK}", "REJECT"),
                           (UNMATCHED_HEX, "APPROVE")):
            with self.subTest(cell=cell), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                ledger = root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
                ledger.parent.mkdir(parents=True)
                ledger.write_text(
                    head
                    + f"| US0001 | REJECT | qa seat r1 | dev | {date} | {cell} | full | [new] x |\n"
                    + f"| US0001 | APPROVE | qa seat r2 | dev | {date} | {cell} | full | none |\n",
                    encoding="utf-8")
                self.assertEqual(want, critic.verdict_for(root, "US0001")["verdict"])

    def test_the_provenance_key_is_retired(self) -> None:
        """AC3. MUTANTS: leave the key in config-defaults.yaml; keep a script reading it."""
        defaults = SKILL / "templates" / "config-defaults.yaml"
        self.assertFalse(KEY in defaults.read_text(encoding="utf-8"),
                         f"{defaults.name} still carries review.{KEY}")
        readers = [p.relative_to(SKILL).as_posix() for p in sorted(SCRIPTS.rglob("*.py"))
                   if "tests" not in p.relative_to(SCRIPTS).parts
                   and KEY in p.read_text(encoding="utf-8", errors="replace")]
        self.assertEqual([], readers, "a shipped script still reads the retired key")

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC4. MUTANTS: leave a retired criterion's `Verified: yes` stamp in place; retire one
        in a shape other than D0259's; delete `AbsentBriefTests` or a kept provenance test.

        The deleted nodes are DERIVED, as US0916's check derives them: every class and `test_`
        function a changed test module defined at the base and no longer defines, the base being
        the parent of the commit that added this module (HEAD while it is uncommitted)."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        for uid, acs in RETIRED.items():
            kind = "bugs" if uid.startswith("BG") else "stories"
            path = next((REPO / "sdlc-studio" / kind).glob(f"{uid}-*.md"))
            blocks = {b.ac_id: b for b in verify_ac.criteria_blocks(
                path.read_text(encoding="utf-8"))}
            for ac in acs:
                with self.subTest(unit=uid, ac=ac):
                    block = blocks.get(ac)
                    self.assertIsNotNone(block, f"{uid} has no {ac}")
                    self.assertTrue((block.verifier or "").startswith(
                        "manual - retired by US0923: "), block.verifier)
                    self.assertEqual("manual", block.verified_state, block)
                    self.assertEqual("retired, superseded by US0923", block.verified_reason,
                                     block)
        now = stamps._test_nodes((HERE / "test_critic.py").read_text(encoding="utf-8"))
        for node in KEPT:
            self.assertIn(node, now, f"test_critic.py::{node} was to stay")
        for cls, test in DELETED:
            self.assertNotIn((cls, test), now, f"test_critic.py::{cls}::{test} was to go")
        base = _base_ref()
        if base is None:
            self.skipTest("no git history here to derive the deleted tests from")
        deleted = stamps._deleted_nodes(base)
        gone = deleted.get("test_critic.py", {}).get("gone", set())
        for node in DELETED:
            self.assertIn(node, gone, f"test_critic.py::{node} was to be deleted ({base})")
        live = stamps._live_stamps(((path.relative_to(REPO), path.read_text(
            encoding="utf-8", errors="replace").splitlines())
            for path in sorted((REPO / "sdlc-studio").rglob("*.md"))), deleted)
        self.assertEqual([], live, "a live stamp selects only deleted test nodes")


def _base_ref() -> str | None:
    """The parent of the commit that added this module, or HEAD while it is uncommitted."""
    rel = Path(__file__).resolve().relative_to(REPO).as_posix()
    added = stamps._git("log", "--diff-filter=A", "--format=%H", "--", rel)
    if added is None:
        return None
    ref = f"{added.split()[0]}^" if added.split() else "HEAD"
    return ref if stamps._git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") else None


if __name__ == "__main__":
    unittest.main()
