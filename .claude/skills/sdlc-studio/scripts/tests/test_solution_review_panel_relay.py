"""The lane brief relays each panel seat's reply by seat and round, and says the approach is
agreed only when every seat has a GO on one note text; an unset panel keeps the one-seat brief.
"""
from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402
import test_solution_review_report as tsrr  # noqa: E402 - the report's fixture run
import test_sprint_report as tsr  # noqa: E402
from lib import sdlc_md  # noqa: E402

critic = loader.load_script("critic")
sprint = loader.load_script("sprint")

REPO = Path(__file__).resolve().parents[5]
SCRIPTS = Path(__file__).resolve().parents[1]
HELP = Path(__file__).resolve().parents[2] / "help" / "sprint.md"
UNIT = "US0101"
NOTE = f"sdlc-studio/.local/lane/{UNIT}-approach.md"
AUTHOR = "Dani Okafor (engineering)"
QA, PRODUCT, PERSONA = "Sam Eriksson (qa)", "Lena Marsh (product)", "Abena Osei (persona)"
PANEL = ("review:\n  solution_review:\n    min_points: 2\n"
         "    panel: [qa, product, persona]\n")
UNSET = "review:\n  solution_review:\n    min_points: 2\n"
STORY = (f"# {UNIT}: a story with a persona\n\n> **Status:** Ready\n"
         f"> **Affects:** src/app.py, changelog.d/{UNIT}.md\n"
         "> **Points:** 3\n> **Persona:** {persona}\n\n"
         "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/app.py\n")
NOTE_TEXT = ("# approach\n\n## Reading\n\nAs written.\n\n## Design\n\nOne function.\n\n"
             "## May break\n\nNothing.\n\n## Tests\n\nAC1 gets a test.\n\n## Sentences\n\nNone.\n")
TWO_ITEMS = "1. Pin the exact reason. 2. Say what the guard refuses."


def block(out: str) -> str:
    """The brief's solution review section, up to the next blank line."""
    start = out.index("--- SOLUTION REVIEW ---")
    end = out.find("\n\n", start)
    return out[start:end if end != -1 else len(out)]


def lanes_sentences() -> list[str]:
    """help/sprint.md's Lanes section, whitespace folded, split into sentences at ". "."""
    text = HELP.read_text(encoding="utf-8")
    lanes = text[text.index("## Lanes"):]
    lanes = lanes[:lanes.index("\n## ", 4)]
    return " ".join(lanes.split()).split(". ")


class SolutionReviewPanelRelayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="sr-relay-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        home = self.tmp / "home"
        home.mkdir()
        env = unittest.mock.patch.dict(os.environ, {
            "HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_DATA_HOME": str(home / "share"), "CLAUDE_CONFIG_DIR": str(home / ".claude"),
            "TMPDIR": str(self.tmp)})
        env.start()
        self.addCleanup(env.stop)
        self.root = self.tmp / "repo"
        seats = self.root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        for card in sorted((REPO / "sdlc-studio" / "personas" / "seats").glob("*.md")):
            shutil.copy(card, seats / card.name)
        pdir = self.root / "sdlc-studio" / "personas"
        for name in ("Abena Osei", "Maya Okafor"):
            slug = name.lower().replace(" ", "-")
            (pdir / f"{slug}.md").write_text(f"# {name}\n\nSomebody.\n", encoding="utf-8")
        (pdir / "index.md").write_text(
            "# Personas\n\n## Primary\n\n- [Abena Osei](abena-osei.md) - primary\n\n"
            "## Secondary\n\n- [Maya Okafor](maya-okafor.md) - secondary\n", encoding="utf-8")
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        self.story = self.root / "sdlc-studio" / "stories" / f"{UNIT}-a-story.md"
        self.story.parent.mkdir(parents=True)
        self.persona("Abena Osei")
        self.note = self.root / NOTE
        self.note.parent.mkdir(parents=True)
        self.note.write_text(NOTE_TEXT, encoding="utf-8")
        self.config(PANEL)

    def persona(self, name: str) -> None:
        self.story.write_text(STORY.replace("{persona}", name), encoding="utf-8")

    def config(self, text: str) -> None:
        (self.root / "sdlc-studio" / ".config.yaml").write_text(text, encoding="utf-8")

    def record(self, reviewer: str, verdict: str, changes: str | None = None) -> str:
        cf = None
        if changes is not None:
            cf = self.tmp / "changes.md"
            cf.write_text(changes, encoding="utf-8")
        _, row, _ = critic.record_solution_review(self.root, UNIT, verdict, self.note,
                                                  reviewer, AUTHOR, changes_file=cf)
        return row["digest"]

    def revise(self) -> None:
        self.note.write_text(self.note.read_text(encoding="utf-8") + "\nRevised.\n",
                             encoding="utf-8")

    def brief(self) -> str:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["lane", "brief", "--units", UNIT, "--root", str(self.root)])
        self.assertEqual(0, rc, err.getvalue())
        return out.getvalue()

    # --- the criteria -------------------------------------------------------------------------

    def test_a_mixed_round_is_relayed_seat_by_seat(self) -> None:
        """AC1. MUTANTS: the panel test inverted; seats sorted; the item numbers dropped from
        the revise list; the persona's name dropped; agreement counted from the seated rows."""
        d1 = self.record(QA, "changes", TWO_ITEMS)
        self.record(PRODUCT, "go")
        sec = block(self.brief())
        lines = sec.splitlines()
        qa = lines.index(f"- qa: CHANGES at round 1 on note digest {d1}:")
        self.assertEqual(["> 1. Pin the exact reason.", "> 2. Say what the guard refuses."],
                         lines[qa + 1:qa + 3])
        self.assertEqual(f"- product: GO at round 1 on note digest {d1}", lines[qa + 3])
        self.assertEqual("- Abena Osei (persona): awaiting a review", lines[qa + 4])
        self.assertIn(f"Revise {NOTE} to answer, under the heading each changes, qa 1, qa 2, "
                      f"naming the seat and the item", sec)
        self.assertIn(f"write sdlc-studio/.local/lane/HANDOFF.md", sec)
        self.assertIn("hand back HANDOFF.", sec)
        self.assertNotIn("agreed", sec)
        self.assertNotIn("Build to", sec)

    def test_the_brief_says_agreed_only_on_one_note_text(self) -> None:
        """AC2. MUTANTS: the digest compare dropped; agreement counted from the seated rows
        rather than read from `critic.panel_state`; the agreed line's build step and its void
        sentence each dropped."""
        d1 = self.record(QA, "changes", TWO_ITEMS)
        self.record(PRODUCT, "go")
        self.record(PERSONA, "go")
        self.revise()
        d2 = self.record(QA, "go")
        sec = block(self.brief())
        self.assertIn(f"- product: GO at round 1 against an earlier note digest, {d1}; asked "
                      f"for again on {d2}", sec)
        self.assertIn(f"- Abena Osei (persona): GO at round 1 against an earlier note digest, "
                      f"{d1}; asked for again on {d2}", sec)
        self.assertIn(f"The note at digest {d2} awaits the review of: product, Abena Osei "
                      f"(persona).", sec)
        self.assertNotIn("agreed", sec)
        self.record(PRODUCT, "go")
        self.record(PERSONA, "go")
        sec = block(self.brief())
        self.assertIn(f"The approach is agreed: every seat on the panel has a GO against note "
                      f"digest {d2} (qa at round 2, product at round 2, Abena Osei (persona) at "
                      f"round 2). Build to {NOTE} as agreed.", sec)
        self.assertIn(f"Editing the note voids every GO: each is bound to {d2}, and `sprint lane "
                      f"land` refuses a note whose digest is not {d2}.", sec)
        self.assertNotIn("Do none of the steps", sec)

    def test_a_note_edited_after_the_last_go_is_not_agreed_and_the_latest_row_names_the_note(
            self) -> None:
        """The note's latest text is the note the latest seated row names. MUTANTS: the note on
        disk ignored; the first seated row's note read instead of the latest's."""
        alt = self.tmp / "alt-note.md"
        alt.write_text(NOTE_TEXT, encoding="utf-8")
        _, row, _ = critic.record_solution_review(self.root, UNIT, "go", alt, QA, AUTHOR)
        self.record(PRODUCT, "go")
        self.record(PERSONA, "go")
        self.assertIn("The approach is agreed", block(self.brief()))
        self.revise()  # the latest seated row names NOTE, not alt-note.md
        sec = block(self.brief())
        self.assertNotIn("The approach is agreed", sec)
        self.assertIn("against an earlier note digest", sec)
        self.assertIn("read from the note the ledger names", sec)
        self.assertIn(f"- qa: GO at round 1 against an earlier note digest, {row['digest']}", sec)

    def test_an_unset_panel_keeps_the_one_seat_brief_and_this_repository_seats_the_panel(
            self) -> None:
        """AC3. MUTANTS: `panel_state` read with the panel unset; the `> ` quote dropped; this
        repository's panel line removed; a phrase of the help sentence cut."""
        self.config(UNSET)
        self.record(QA, "go")
        before = self.brief()
        with unittest.mock.patch.object(critic, "panel_state", side_effect=AssertionError):
            self.assertEqual(before, self.brief())
        self.assertIn("The approach is agreed: GO at round 1", before)
        # this repository seats the panel
        shown = subprocess.run(
            [sys.executable, str(SCRIPTS / "config.py"), "show", "--key",
             "review.solution_review.panel", "--root", str(REPO)],
            capture_output=True, text=True, timeout=60)
        self.assertEqual(0, shown.returncode, shown.stderr)
        for seat in ("qa", "product", "persona"):
            self.assertIn(seat, shown.stdout)
        # a relayed reply holding an identity sentence stays quoted: one identity read
        import test_one_identity_brief as one  # noqa: PLC0415 - the identity reader
        self.config(PANEL)
        self.record(QA, "changes", "1. You are the qa review seat, so say so. 2. Pin it.")
        out = self.brief()
        self.assertIn("> 1. You are the qa review seat, so say so.", out)
        self.assertEqual(("seat", "engineering"), one.assert_one_identity(out, self.root))
        bare = out.replace("> 1. You are", "1. You are")
        self.assertEqual(2, len(one.identities(bare, self.root)))
        self.assertTrue(any(r.fixture == "relayed" for r in one.GENERATORS))
        # the Lanes section's one sentence naming the key
        said = [s for s in lanes_sentences() if "review.solution_review.panel" in s]
        self.assertEqual(1, len(said), said)
        for phrase in ("its own agent", "its own review",
                       "agreed only when every seat has a GO on the note as it stands"):
            self.assertIn(phrase, said[0])

    def test_a_note_revised_after_a_changes_awaits_review_and_is_not_sent_back_to_revise(
            self) -> None:
        """The after-revision state: qa's CHANGES and product's GO stand on the first note and
        the note is revised, so every seat's review of the revised note is awaited and the
        builder is not told to revise it again. MUTANTS: the CHANGES-on-an-earlier-digest wait
        deleted."""
        d1 = self.record(QA, "changes", TWO_ITEMS)
        self.record(PRODUCT, "go")
        self.revise()
        d2 = critic.note_digest(self.note)
        self.assertNotEqual(d1, d2)
        sec = block(self.brief())
        self.assertIn(f"- qa: CHANGES at round 1 against an earlier note digest, {d1}; its "
                      f"review of the note at {d2} is awaited:", sec)
        self.assertIn(f"The note at digest {d2} awaits the review of: qa, product, Abena Osei "
                      f"(persona).", sec)
        self.assertNotIn("Revise", sec)
        self.assertNotIn("agreed", sec)
        self.assertIn("hand back HANDOFF.", sec)

    def test_the_first_brief_tells_the_builder_to_write_the_note_under_its_five_headings(
            self) -> None:
        """The first brief: no seat has a verdict, so the builder is told to write the note
        under its five headings, every seat awaits a review and the build steps are held.
        MUTANTS: the no-verdict branch turned off."""
        self.assertEqual(5, len(critic.APPROACH_HEADINGS))
        sec = block(self.brief())
        headings = ", ".join(f"`## {h}`" for h in critic.APPROACH_HEADINGS)
        self.assertIn(f"Before any code or test, write your approach note to {NOTE} under five "
                      f"headings, {headings}:", sec)
        for who in ("qa", "product", "Abena Osei (persona)"):
            self.assertIn(f"- {who}: awaiting a review", sec)
        self.assertNotIn("awaits the review of", sec)
        self.assertNotIn("digest None", sec)
        self.assertIn("Do none of the steps below this section", sec)
        self.assertIn("hand back HANDOFF.", sec)

    def test_the_building_seat_and_a_persona_less_unit_s_persona_are_skipped(self) -> None:
        """help/sprint.md's skipped-seat sentence, run against the land's own call
        (`critic.approach_agreed`) and the lane brief: the seat building the unit, and `persona`
        for a story naming no Persona, do not sit, so under `[qa, product, persona]` a unit with
        no Persona is agreed on a qa GO and a product GO alone. MUTANTS: the sentence's building
        seat and its persona seat each cut; the land's "every seat that sits" read back as
        "every seat the panel names"."""
        self.record(QA, "go")
        self.record(PRODUCT, "go")
        # positive control: a unit naming a Persona needs that persona's GO
        ok, why = critic.approach_agreed(self.root, UNIT, self.note)
        self.assertFalse(ok, why)
        self.assertIn("persona seat (Abena Osei): no verdict recorded", why)
        self.story.write_text(STORY.replace("> **Persona:** {persona}\n", ""), encoding="utf-8")
        ok, why = critic.approach_agreed(self.root, UNIT, self.note)
        self.assertTrue(ok, why)
        self.assertIn(f"persona is skipped: {UNIT} names no Persona", why)
        sec = block(self.brief())
        self.assertIn(f"- persona: skipped, {UNIT} names no Persona, so no stakeholder sits", sec)
        self.assertIn("The approach is agreed", sec)
        # the building seat: engineering, unless the unit's lane brief recorded another seat
        self.config(PANEL.replace("[qa, product, persona]", "[engineering, qa, product, persona]"))
        ok, why = critic.approach_agreed(self.root, UNIT, self.note)
        self.assertTrue(ok, why)
        self.assertIn(f"engineering is skipped: the engineering seat builds {UNIT}", why)
        self.assertIn(f"- engineering: skipped, the engineering seat builds {UNIT}",
                      block(self.brief()))
        with unittest.mock.patch.object(critic.run_state, "lane_seat", return_value="qa"):
            ok, why = critic.approach_agreed(self.root, UNIT, self.note)
        self.assertFalse(ok, why)  # qa builds, so engineering sits and has no GO
        self.assertIn("engineering seat: no verdict recorded", why)
        self.assertIn(f"qa is skipped: the qa seat builds {UNIT}", why)
        # the help's Lanes section says so in one sentence
        said = [s for s in lanes_sentences() if "names no Persona" in s]
        self.assertEqual(1, len(said), said)
        for phrase in ("the seat building the unit (the seat its lane brief recorded, else "
                       "engineering)", "`persona` and the unit's story names no Persona",
                       "under `[qa, product, persona]` a unit with no Persona is agreed on a qa "
                       "GO and a product GO alone", "the lane brief names each seat skipped and "
                       "why"):
            self.assertIn(phrase, said[0])
        self.assertTrue(any("needs a GO from every seat that sits on the unit" in s
                            for s in lanes_sentences()))

    def test_the_report_counts_a_unit_s_highest_round(self) -> None:
        """AC4. MUTANTS (by hand, in sprint_report.py and critic.py): `max` read as `sum`, and
        the rounds counted per row; the revised round dropped from the fixture below."""
        h = tsrr.SolutionReviewReportTests("test_the_two_groups_stand_side_by_side")
        h.setUp()
        self.addCleanup(h.doCleanups)
        cfg = h.root / "sdlc-studio" / ".config.yaml"
        cfg.write_text(PANEL.replace("min_points: 2", "min_points: 1"), encoding="utf-8")
        pdir = h.root / "sdlc-studio" / "personas"
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "abena-osei.md").write_text("# Abena Osei\n\nSomebody.\n", encoding="utf-8")
        (pdir / "index.md").write_text(
            "# Personas\n\n## Primary\n\n- [Abena Osei](abena-osei.md) - primary\n",
            encoding="utf-8")
        for uid in ("US0101", "US0102", "US0103"):
            for f in (h.root / "sdlc-studio" / "stories").glob(f"{uid}-*.md"):
                f.write_text(f.read_text(encoding="utf-8").replace(
                    "> **Points:**", "> **Persona:** Abena Osei\n> **Points:**", 1),
                    encoding="utf-8")
        h.delivery([("US0101", "APPROVE"), ("US0102", "APPROVE"), ("US0103", "APPROVE")])
        reviewers = {"qa": "Sam Eriksson (qa)", "product": "Lena Marsh (product)",
                     "persona": "Abena Osei (persona)"}

        def solution(uid, seat, verdict, day=tsrr.DAY):
            with unittest.mock.patch.object(sdlc_md, "now_date", return_value=day):
                critic.record_solution_review(
                    h.root, uid, verdict, h.note, reviewers[seat], AUTHOR,
                    changes_file=h.changes if verdict == "changes" else None)

        def read():
            return tsrr.values(tsrr.section(h.build()))[0]["sr_solution_rounds"]

        for seat in ("qa", "product", "persona"):  # three rows, all at round 1
            solution("US0101", seat, "go")
        self.assertEqual(1.0, read())
        solution("US0102", "qa", "changes")
        solution("US0102", "product", "go")
        h.note.write_text("the revised approach\n", encoding="utf-8")
        for seat in ("qa", "product", "persona"):  # five rows, the highest Round cell 2
            solution("US0102", seat, "go")
        self.assertEqual(1.5, read())
        for uid, alone in (("US0101", 1.0), ("US0102", 2.0)):  # never 3.0 or 5.0
            h.delivery([(uid, "APPROVE")])
            self.assertEqual(alone, read(), uid)
        h.delivery([("US0101", "APPROVE"), ("US0102", "APPROVE"), ("US0103", "APPROVE")])
        # a unit carried in: its qa round 1 is dated before the run, so the run holds round 2 only
        solution("US0103", "qa", "changes", tsrr.EARLIER)
        solution("US0103", "qa", "go")
        self.assertEqual(round(4 / 3, 1), read())  # 1.0, 2.0 and the carried unit's 1.0


if __name__ == "__main__":
    unittest.main()
