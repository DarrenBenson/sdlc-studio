"""A project's approach panel: the seats that review a unit's approach note, each recording in
its own rounds, and the approach agreed only when every seat on the panel has a GO on the note as
it stands.

Every record goes through the shipped `critic.py approach record` CLI against a throwaway
project; the readers other scripts call (`solution_review_panel`, `effective_panel`,
`panel_state`, `approach_agreed`) are called directly on the ledger the CLI wrote.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
REFERENCE = SKILL / "reference-config.md"
LEDGER = Path("sdlc-studio") / "reviews" / "solution-reviews.md"
KEY = "`review.solution_review.panel`"
AUTHOR = "Dani Okafor (engineering)"
QA, PRODUCT, ABENA = "Sam Eriksson (qa)", "Lena Marsh (product)", "Abena Osei (persona)"
ROSTER = "the seats it has a card for are engineering, qa, product (the shipped seats and the " \
         "project's own seat cards)"
CARDS = {"dani-okafor": ("Dani Okafor", "engineering"), "sam-eriksson": ("Sam Eriksson", "qa"),
         "lena-marsh": ("Lena Marsh", "product")}
UNITS = {  # id: (folder, points, Persona or None)
    "US0001": ("stories", 3, "Abena Osei"), "US0002": ("stories", 3, "Maya Okafor"),
    "US0004": ("stories", 3, "Abena Osei"), "US0005": ("stories", 2, "Abena Osei"),
    "BG0001": ("bugs", 3, None),
}
REGISTRY = ("# Personas\n\n## Primary\n\n- **Abena Osei** - engineering lead\n\n"
            "## Secondary\n\n- **Maya Okafor** - developer\n")


def _unit_text(uid: str, points: int, persona: str | None) -> str:
    who = f"> **Persona:** {persona}\n" if persona else ""
    return (f"# {uid}: A unit\n\n> **Status:** Ready\n> **Points:** {points}\n{who}"
            f"> **Affects:** src/a.py\n\n## Acceptance Criteria\n\n### AC1: it works\n")


class SolutionReviewPanelTests(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="srpanel-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.env = dict(os.environ, HOME=str(self.tmp / "home"), TMPDIR=str(self.tmp),
                        XDG_CONFIG_HOME=str(self.tmp / "xdg"), PYTHONDONTWRITEBYTECODE="1")
        self.root = self._project("proj")
        self.note = self.tmp / "US0001-approach.md"
        self.note.write_text("# approach\n\n## Tests\n\nAC1: a test\n", encoding="utf-8")
        self.changes = self.tmp / "changes.txt"
        self.changes.write_text("Pin the per-seat rounds.\n", encoding="utf-8")

    # -- the fixture -------------------------------------------------------------------------

    def _project(self, name: str, cards: bool = True) -> Path:
        root = self.tmp / name
        for uid, (folder, points, persona) in UNITS.items():
            d = root / "sdlc-studio" / folder
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{uid}-a-unit.md").write_text(_unit_text(uid, points, persona),
                                                encoding="utf-8")
        if cards:
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            for stem, (holder, role) in CARDS.items():
                self._card(root, "seats", stem, holder, role)
            (root / "sdlc-studio" / "personas" / "index.md").write_text(REGISTRY,
                                                                       encoding="utf-8")
        return root

    @staticmethod
    def _card(root: Path, sub: str, stem: str, holder: str, role: str) -> None:
        d = root / "sdlc-studio" / "personas" / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{stem}.md").write_text(f"# {holder} - A seat\n\n<!-- role: {role} -->\n",
                                      encoding="utf-8")

    @staticmethod
    def _config(root: Path, panel: str | None) -> None:
        text = "review:\n  solution_review:\n    min_points: 3\n"
        text += f"    panel: {panel}\n" if panel is not None else ""
        (root / "sdlc-studio" / ".config.yaml").write_text(text, encoding="utf-8")

    def _record(self, root: Path, unit: str, reviewer: str, verdict: str = "go",
                note: Path | None = None) -> subprocess.CompletedProcess:
        argv = [sys.executable, "-B", str(SCRIPTS / "critic.py"), "--root", str(root),
                "approach", "record", "--unit", unit, "--verdict", verdict,
                "--note", str(note or self.note), "--reviewer", reviewer, "--author", AUTHOR]
        argv += ["--changes", str(self.changes)] if verdict == "changes" else []
        return subprocess.run(argv, capture_output=True, text=True, env=self.env, timeout=120)

    def _ok(self, proc: subprocess.CompletedProcess, rnd: int | None = None) -> None:
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        if rnd is not None:
            self.assertIn(f" at round {rnd} against note digest ", proc.stdout)

    def _refused(self, proc: subprocess.CompletedProcess, *words: str) -> None:
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("Nothing was written.", proc.stderr)
        for w in words:
            self.assertIn(w, proc.stderr)

    @staticmethod
    def _ledger(root: Path) -> bytes | None:
        path = root / LEDGER
        return path.read_bytes() if path.is_file() else None

    def _revise(self, note: Path | None = None) -> None:
        note = note or self.note
        note.write_text(note.read_text(encoding="utf-8") + "\nRevised.\n", encoding="utf-8")

    # -- the criteria ------------------------------------------------------------------------

    def test_the_panel_names_who_may_record(self) -> None:
        """AC1. MUTANTS: the `if panel` gate inverted, the no-seat guard, the on-panel check, the
        persona-name check or the roster check dropped."""
        self._config(self.root, "[qa, product, persona]")
        for reviewer in (QA, PRODUCT, ABENA):
            with self.subTest(reviewer):
                self._ok(self._record(self.root, "US0001", reviewer), 1)
        before = self._ledger(self.root)
        for reviewer, words in (
                ("Ola Ade (engineering)",
                 ("the reviewer 'Ola Ade (engineering)' sits as engineering, and "
                  f"{KEY} is [qa, product, persona], which seats qa, product, persona on "
                  "US0001",)),
                ("Sam Eriksson", ("the reviewer 'Sam Eriksson' names no `(<seat>)`", KEY)),
                ("Maya Okafor (persona)",
                 ("the reviewer 'Maya Okafor (persona)' sits as persona, and US0001's Persona "
                  "is Abena Osei",))):
            with self.subTest(reviewer):
                self._refused(self._record(self.root, "US0001", reviewer), *words)
                self.assertEqual(self._ledger(self.root), before)
        self._config(self.root, "[qa, nobody]")
        self._refused(self._record(self.root, "US0001", QA),
                      f"{KEY} is ['qa', 'nobody'], and 'nobody' is not a seat the project has a "
                      f"card for, or `persona`: {ROSTER}")
        self.assertEqual(self._ledger(self.root), before)
        self._config(self.root, None)
        self._ok(self._record(self.root, "US0001", "Ola Ade (engineering)"), 4)
        self.assertEqual([r["round"] for r in critic.read_solution_reviews(self.root, "US0001")],
                         [1, 1, 1, 4])

    def test_each_seat_numbers_its_own_rounds(self) -> None:
        """AC2. MUTANTS: the per-seat count replaced by the unit's rows plus one; the seat filter
        dropped; the unset path routed through the per-seat count."""
        self._config(self.root, "[qa, product, persona]")
        self._ok(self._record(self.root, "US0001", QA, verdict="changes"), 1)
        self._ok(self._record(self.root, "US0001", PRODUCT), 1)
        self._ok(self._record(self.root, "US0001", ABENA), 1)
        self._revise()
        self._ok(self._record(self.root, "US0001", QA), 2)
        rows = critic.read_solution_reviews(self.root, "US0001")
        self.assertEqual([(r["round"], r["verdict"], critic.recorded_seat(r["reviewer"]))
                          for r in rows],
                         [(1, "CHANGES", "qa"), (1, "GO", "product"), (1, "GO", "persona"),
                          (2, "GO", "qa")])
        other = self._project("unset")
        self._config(other, None)
        self._ok(self._record(other, "US0001", QA, verdict="changes"), 1)
        self._ok(self._record(other, "US0001", PRODUCT), 2)
        self.assertEqual([r["round"] for r in critic.read_solution_reviews(other, "US0001")],
                         [1, 2])

    def test_the_approach_is_agreed_only_when_every_seat_has_a_go(self) -> None:
        """AC3. MUTANTS: the last-row read restored under a panel; the digest compare dropped;
        the persona skip or the building-seat skip dropped; the set-but-empty state read as
        unset; the empty-panel record guard dropped; `recorded_seat` swapped for
        `verdict_seat`; the unset messages changed."""
        root = self.root
        self._config(root, "[qa, product, persona]")
        self.assertEqual(critic.effective_panel(root, "US0001"),
                         (["qa", "product", "persona"], {}))
        self._ok(self._record(root, "US0001", QA, verdict="changes"))
        self._ok(self._record(root, "US0001", PRODUCT))
        ok, why = critic.approach_agreed(root, "US0001", self.note)
        self.assertFalse(ok, why)
        self.assertIn("qa seat: latest verdict CHANGES at round 1", why)
        self.assertIn("persona seat (Abena Osei): no verdict recorded", why)
        self.assertNotIn("product seat", why)
        self._ok(self._record(root, "US0001", ABENA))
        d1 = critic.note_digest(self.note)
        self._revise()
        d2 = critic.note_digest(self.note)
        self._ok(self._record(root, "US0001", QA))
        ok, why = critic.approach_agreed(root, "US0001", self.note)
        self.assertFalse(ok, why)
        self.assertIn(f"product seat: GO at round 1 on note digest {d1}", why)
        self.assertIn(f"persona seat (Abena Osei): GO at round 1 on note digest {d1}", why)
        self.assertIn(f"the note's digest now is {d2}", why)
        self.assertNotIn("qa seat", why)
        self._ok(self._record(root, "US0001", PRODUCT), 2)
        self._ok(self._record(root, "US0001", ABENA), 2)
        self.assertEqual(critic.approach_agreed(root, "US0001", self.note),
                         (True, f"every seat on {KEY} has a GO against note digest {d2}: qa at "
                                f"round 2, product at round 2, persona (Abena Osei) at round 2"))
        # a bug that names no Persona: no stakeholder sits
        no_persona = "BG0001 names no Persona, so no stakeholder sits"
        self.assertEqual(critic.effective_panel(root, "BG0001"),
                         (["qa", "product"], {"persona": no_persona}))
        self._ok(self._record(root, "BG0001", QA))
        self._ok(self._record(root, "BG0001", PRODUCT))
        self.assertEqual(critic.approach_agreed(root, "BG0001", self.note),
                         (True, f"every seat on {KEY} has a GO against note digest {d2}: qa at "
                                f"round 1, product at round 1; persona is skipped: {no_persona}"))
        # the seat that builds the unit is skipped for it, not refused
        self._config(root, "[qa, engineering]")
        builds = "the engineering seat builds US0004"
        self.assertEqual(critic.effective_panel(root, "US0004"), (["qa"], {"engineering": builds}))
        self._ok(self._record(root, "US0004", QA), 1)
        self.assertEqual(critic.approach_agreed(root, "US0004", self.note),
                         (True, f"every seat on {KEY} has a GO against note digest {d2}: qa at "
                                f"round 1; engineering is skipped: {builds}"))
        # a set panel the skips leave empty agrees nothing, and records nobody
        self._config(root, "[engineering]")
        before = self._ledger(root)
        empty = (f"{KEY} is [engineering], which seats nobody on BG0001; engineering is skipped: "
                 f"the engineering seat builds BG0001")
        self._refused(self._record(root, "BG0001", QA),
                      f"the reviewer 'Sam Eriksson (qa)' sits as qa, and {empty}")
        self.assertEqual(self._ledger(root), before)
        self.assertEqual(critic.approach_agreed(root, "BG0001", self.note), (False, empty))
        state = critic.panel_state(root, "BG0001", self.note)
        self.assertEqual((state["set"], state["seats"], state["agreed"]), (True, [], False))
        self._config(root, "[persona]")
        self.assertEqual(critic.approach_agreed(root, "BG0001", self.note),
                         (False, f"{KEY} is [persona], which seats nobody on BG0001; persona is "
                                 f"skipped: {no_persona}"))
        # the seat is read from the `(<role>)` group: Maya Okafor is not the engineering holder
        self._config(root, "[qa, persona]")
        self._ok(self._record(root, "US0002", QA))
        self._ok(self._record(root, "US0002", "Maya Okafor (persona)"))
        self.assertEqual(critic.approach_agreed(root, "US0002", self.note),
                         (True, f"every seat on {KEY} has a GO against note digest {d2}: qa at "
                                f"round 1, persona (Maya Okafor) at round 1"))
        # unset: US1344's messages, byte for byte
        other = self._project("unset")
        self._config(other, None)
        note = self.tmp / "unset-approach.md"
        note.write_text("# approach\n", encoding="utf-8")
        gone = self.tmp / "gone.md"
        self.assertEqual(critic.approach_agreed(other, "US0001", gone),
                         (False, f"the note {gone} names no file"))
        self.assertEqual(critic.approach_agreed(other, "US0001", note),
                         (False, "no solution review is recorded for US0001 in "
                                 "sdlc-studio/reviews/solution-reviews.md"))
        self._ok(self._record(other, "US0001", QA, verdict="changes", note=note))
        self.assertEqual(critic.approach_agreed(other, "US0001", note),
                         (False, "the latest solution review of US0001 is CHANGES at round 1: "
                                 "revise the note and record a new verdict"))
        self._ok(self._record(other, "US0001", PRODUCT, note=note))
        e1 = critic.note_digest(note)
        self._revise(note)
        e2 = critic.note_digest(note)
        self.assertEqual(critic.approach_agreed(other, "US0001", note),
                         (False, f"the GO at round 2 was recorded against note digest {e1}, and "
                                 f"the note's digest now is {e2}"))
        self._ok(self._record(other, "US0001", QA, note=note), 3)
        self.assertEqual(critic.approach_agreed(other, "US0001", note),
                         (True, f"GO at round 3 against note digest {e2}"))
        self.assertFalse(critic.panel_state(other, "US0001", note)["set"])

    def test_the_reference_says_what_the_panel_does(self) -> None:
        """AC4. MUTANTS: the default changed in config-defaults.yaml; a statement cut from the
        row; a second `skipped` or `its own review`, or an `as before`, written into it."""
        bare = self.tmp / "bare"
        (bare / "sdlc-studio").mkdir(parents=True)
        show = subprocess.run([sys.executable, "-B", str(SCRIPTS / "config.py"), "--root",
                               str(bare), "show", "--sources"], capture_output=True, text=True,
                              env=self.env, timeout=120)
        self.assertEqual(show.returncode, 0, show.stderr)
        self.assertIn("default review.solution_review.panel = []", show.stdout.splitlines())
        rows = REFERENCE.read_text(encoding="utf-8").splitlines()
        row = [r for r in rows if r.startswith("| `review.solution_review.panel` |")]
        self.assertEqual(len(row), 1)
        row = row[0]
        self.assertTrue(row.startswith("| `review.solution_review.panel` | `[]` |"), row)
        for phrase in ("Empty means one seat's GO agrees the approach",
                       "names the seats, each its own agent and its own review",
                       "each seat on the panel adds one review a round",
                       "`persona` sits only for a unit that names a Persona",
                       "the seat that builds a unit is skipped for that unit"):
            with self.subTest(phrase):
                self.assertIn(phrase, row)
        self.assertEqual(row.count("as before"), 0)
        self.assertEqual(row.count("its own review"), 1)
        self.assertEqual(row.count("skipped"), 1)
        self.assertLessEqual(len(rows), 732)

    # -- a reviewer cell's seat ---------------------------------------------------------------

    def test_a_persona_with_a_parenthetical_sits_as_the_persona(self) -> None:
        """BG1780 AC1: a stakeholder whose Persona carries a parenthetical, written
        `Sam Eriksson (QA) (persona)`, sits as the persona, so no qa GO is read where no qa
        seat reviewed. MUTANTS: the first group of a reviewer read rather than its last; the
        persona's name sliced at the cell's first group."""
        (self.root / "sdlc-studio" / "stories" / "US0006-a-unit.md").write_text(
            _unit_text("US0006", 3, "Sam Eriksson (QA)"), encoding="utf-8")
        self._config(self.root, "[qa, persona]")
        for reviewer, rnd in (("Sam Eriksson (QA) (persona)", 1),
                              ("Sam Eriksson QA (persona)", 2)):
            self._ok(self._record(self.root, "US0006", reviewer), rnd)
        state = critic.panel_state(self.root, "US0006", self.note)
        self.assertIsNone(state["latest"]["qa"])
        self.assertEqual(state["latest"]["persona"]["reviewer"], "Sam Eriksson QA (persona)")
        ok, why = critic.approach_agreed(self.root, "US0006", self.note)
        self.assertFalse(ok)
        self.assertIn("qa seat: no verdict recorded", why)

    def test_the_seat_is_the_first_reviewer_s_last_role_group(self) -> None:
        """BG1780 AC2: the last `(<role>)` group of the cell's first reviewer, reviewers joined
        by a `+` with a space each side, so the ledger's three-seat cells (CR0227's and
        EP0030's in critic-verdicts.md) read as they did. MUTANTS: the join read as any `+`;
        the first part read even when it holds no group; the first group read; the join
        ignored."""
        cases = {
            "Sam Eriksson (QA) (persona)": "persona",
            "Lena Marsh (Product) + Dani Okafor (Engineering) + Sam Eriksson (QA)": "product",
            "Sam Eriksson (QA) + Lena Marsh (Product) + Dani Okafor (Engineering)": "qa",
            "Bo (qa) + Ann (Product) (persona)": "qa",
            "Ann + Bo (qa)": "qa",
            "Pat (QA)+Ops (persona)": "persona",
            "subagents:aab20a54+ae6208e8 (builders)": "builders",
            "Claude (engineering seat)": "engineering",
            "Claude (run thirteen grooming, D0479)": None,
            "": None,
        }
        for cell, role in cases.items():
            self.assertEqual(critic.recorded_seat(cell), role, cell)
        self.assertIsNone(critic.recorded_seat(None))

    def test_an_unreadable_note_is_refused_in_words(self) -> None:
        """BG1780 AC3: a note that cannot be read is refused naming it, the OS's reason in its
        own words or `it is not UTF-8 text`, exit 2 and nothing written; the digest the other
        readers take of the same note is unchanged. MUTANTS: the UTF-8 check dropped; the
        refusal's wrapper dropped; the reason lower-cased."""
        self._config(self.root, None)
        bad = self.tmp / "bad.md"
        bad.write_bytes(b"# approach\n\xff\xfe\n")
        cases = [(bad, "it is not UTF-8 text")]
        if os.geteuid() != 0:  # root reads a file of mode 000
            locked = self.tmp / "locked.md"
            locked.write_text("# approach\n", encoding="utf-8")
            locked.chmod(0)
            self.addCleanup(locked.chmod, 0o600)
            cases.append((locked, "Permission denied"))
        for note, why in cases:
            with self.subTest(note.name):
                proc = self._record(self.root, "US0001", QA, note=note)
                self._refused(proc, f"approach record refused: the note {note} cannot be "
                                    f"read: {why}. Nothing was written.")
                self.assertNotIn("Errno", proc.stderr)
                self.assertIsNone(self._ledger(self.root))
        self.assertRegex(critic.note_digest(bad), r"\A[0-9a-f]{12}\Z")
        bad.write_text("# approach\n", encoding="utf-8")
        self._ok(self._record(self.root, "US0001", QA, note=bad), 1)

    # -- the guards beside them --------------------------------------------------------------

    def test_a_malformed_panel_is_refused_by_name_before_the_rule_and_the_seat(self) -> None:
        """A unit that takes the review is refused naming the panel, before its seat is read; a
        unit that takes none is refused for that, the bad panel named on a warning line.
        MUTANTS: the list check, the string-entry check or the roster check dropped; the
        panel's refusal raised by the settings read again, so every unit is refused for it; a
        seat refusal put before the rule's."""
        for panel, words in (
                ("qa", f"{KEY} is 'qa', which is not a list of seats, each a seat the project "
                       f"has a card for, or `persona`"),
                ("[qa, 3]", f"{KEY} is ['qa', 3], and 3 is not a seat the project has a card "
                            f"for, or `persona`: {ROSTER}")):
            with self.subTest(panel):
                self._config(self.root, panel)
                self._refused(self._record(self.root, "US0001", QA), words)
                ok, why = critic.approach_agreed(self.root, "US0001", self.note)
                self.assertFalse(ok)
                self.assertIn(words, why)
        self._config(self.root, "[qa, nobody]")
        proc = self._record(self.root, "US0005", QA)
        self._refused(proc, "US0005 takes no solution review")
        self.assertIn(f"warning: {KEY} is ['qa', 'nobody']", proc.stderr)
        self._refused(self._record(self.root, "US0001", QA),
                      f"approach record refused: {KEY} is ['qa', 'nobody']")
        self._config(self.root, "[qa, product, persona]")
        proc = self._record(self.root, "US0005", "Ola Ade (engineering)")
        self._refused(proc, "US0005 takes no solution review")
        self.assertNotIn("sits as", proc.stderr)
        self.assertIsNone(self._ledger(self.root))
        self.assertEqual(critic.approach_agreed(self.root, "US0999", self.note),
                         (False, "no unit US0999 is found in this project"))

    def test_entries_are_normalised_and_every_card_counts(self) -> None:
        """MUTANTS: the strip/lower dropped; duplicates kept; the legacy amigos roles or the
        shipped seats left out of the roster."""
        self._config(self.root, '["QA ", qa, product]')
        self.assertEqual(critic.solution_review_panel(self.root), ["qa", "product"])
        self._card(self.root, "amigos", "security", "Ira Shah", "security")
        self._card(self.root, "seats", "uma-lee", "Uma Lee", "ux")
        self._config(self.root, "[security, ux, qa]")
        self.assertEqual(critic.solution_review_panel(self.root), ["security", "ux", "qa"])
        self._config(self.root, "[nobody]")
        with self.assertRaises(ValueError) as cm:
            critic.solution_review_panel(self.root)
        self.assertIn("the seats it has a card for are engineering, qa, product, security, ux "
                      "(", str(cm.exception))
        bare = self._project("bare", cards=False)
        self._config(bare, "[qa]")
        self.assertEqual(critic.solution_review_panel(bare), ["qa"])
        self._config(bare, None)
        self.assertEqual(critic.solution_review_panel(bare), [])

    def test_persona_is_reserved_only_when_the_panel_names_it(self) -> None:
        """MUTANTS: the reserved check dropped; widened to every set panel."""
        self._card(self.root, "seats", "pat-doe", "Pat Doe", "persona")
        self._config(self.root, "[qa]")
        self.assertEqual(critic.solution_review_panel(self.root), ["qa"])
        self._config(self.root, "[qa, persona]")
        words = (f"{KEY} names `persona`, which is ambiguous here: a project seat card declares "
                 f"the role `persona`; rename that card's role, or drop `persona` from the panel")
        with self.assertRaises(ValueError) as cm:
            critic.solution_review_panel(self.root)
        self.assertIn(words, str(cm.exception))
        self._refused(self._record(self.root, "US0001", QA), words)
        self.assertIsNone(self._ledger(self.root))

    def test_the_persona_seat_follows_the_units_persona(self) -> None:
        """MUTANTS: the name match made exact; the persona skip dropped at record; a persona row
        counted after the Persona changed."""
        self._config(self.root, "[qa, product, persona]")
        self._ok(self._record(self.root, "US0001", "abena-osei (persona)"), 1)
        self._ok(self._record(self.root, "US0001", "Abena  Osei (persona)"), 2)
        self._refused(self._record(self.root, "BG0001", ABENA),
                      "the reviewer 'Abena Osei (persona)' sits as persona",
                      "persona is skipped: BG0001 names no Persona, so no stakeholder sits")
        self._ok(self._record(self.root, "US0001", QA))
        self._ok(self._record(self.root, "US0001", PRODUCT))
        self.assertTrue(critic.approach_agreed(self.root, "US0001", self.note)[0])
        story = self.root / "sdlc-studio" / "stories" / "US0001-a-unit.md"
        story.write_text(_unit_text("US0001", 3, "Maya Okafor"), encoding="utf-8")
        ok, why = critic.approach_agreed(self.root, "US0001", self.note)
        self.assertFalse(ok)
        self.assertIn("persona seat (Maya Okafor): no verdict recorded", why)
        self._ok(self._record(self.root, "US0001", "Maya Okafor (persona)"), 1)

    def test_the_building_seat_is_read_from_the_lane(self) -> None:
        """MUTANT: the lane's seat ignored for `BUILD_SEAT`."""
        self._config(self.root, "[qa, product, persona]")
        with mock.patch.object(critic.run_state, "lane_seat", return_value="qa"):
            self.assertEqual(critic.effective_panel(self.root, "US0001"),
                             (["product", "persona"], {"qa": "the qa seat builds US0001"}))

    def test_panel_state_without_a_note(self) -> None:
        """MUTANTS: the one-digest check dropped; the unset state read through the panel; a row
        in a seat off the panel taken into `latest`."""
        self._config(self.root, None)
        self._ok(self._record(self.root, "US0001", "Ola Ade (engineering)"), 1)
        self._config(self.root, "[qa, product]")
        self._ok(self._record(self.root, "US0001", QA))
        self._ok(self._record(self.root, "US0001", PRODUCT))
        d1 = critic.note_digest(self.note)
        state = critic.panel_state(self.root, "US0001")
        self.assertEqual((state["set"], state["seats"], state["skipped"], state["agreed"]),
                         (True, ["qa", "product"], {}, True))
        self.assertEqual(state["why"], f"every seat on {KEY} has a GO against note digest {d1}: "
                                       f"qa at round 1, product at round 1")
        self.assertEqual(state["latest"]["qa"]["round"], 1)
        self.assertEqual(sorted(state["latest"]), ["product", "qa"])
        self._revise()
        self._ok(self._record(self.root, "US0001", QA), 2)
        d2 = critic.note_digest(self.note)
        state = critic.panel_state(self.root, "US0001")
        self.assertFalse(state["agreed"])
        self.assertIn(f"the GOs are on more than one note digest: qa {d2}, product {d1}",
                      state["why"])
        other = self._project("unset")
        self._config(other, None)
        self._ok(self._record(other, "US0001", QA))
        state = critic.panel_state(other, "US0001")
        self.assertEqual((state["set"], state["seats"], state["agreed"], state["why"]),
                         (False, [], True, f"GO at round 1 against note digest {d2}"))


if __name__ == "__main__":
    unittest.main()
