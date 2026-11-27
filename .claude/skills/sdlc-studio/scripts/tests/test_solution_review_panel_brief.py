"""`critic.py approach panel` names one brief and one reply file per seat, and `approach brief
--seat persona` frames the unit's stakeholder persona from its registered card.

Each test builds a throwaway project: this repository's three seat cards, a persona registry,
3-point stories and a complete approach note, with `review.solution_review` set in its config.
The verbs run in-process through `critic.main`, so each case costs no interpreter start.
"""

from __future__ import annotations

import contextlib
import io
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
REPO = SKILL.parents[2]
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import critic  # noqa: E402
import persona_resolve  # noqa: E402
import persona_review  # noqa: E402
from test_one_identity_brief import assert_one_identity  # noqa: E402

UNIT, BUG, ROWAN = "US0001", "BG0001", "US0002"
QA, PRODUCT, PERSONA = "Sam Eriksson (qa)", "Lena Marsh (product)", "Abena Osei (persona)"
AUTHOR = "Dani Okafor (engineering)"
PANEL = "review:\n  solution_review:\n    min_points: 3\n    panel: [qa, product, persona]\n"
_CARD = ("# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
         "| **Cast role** | {role} |\n\n## Who They Are\n\nSomebody who upgrades the tool.\n")
_STORY = ("# {uid}: a story for the panel\n\n> **Status:** Ready\n> **Affects:** src/app.py\n"
          "> **Points:** 3\n{persona}\n## Acceptance Criteria\n\n### AC1: it holds\n\n"
          "- **Given** a thing\n- **Verify:** file src/app.py\n")
_NOTE = ("# approach\n\n## Reading\n\nAs written.\n\n## Design\n\nOne function.\n\n"
         "## May break\n\nNothing reads it.\n\n## Tests\n\nAC1 gets a test.\n\n"
         "## Sentences\n\nThe fragment.\n")
SECTIONS = ("Boundaries", "End Goals", "Frustrations")
REMEDY = "register it in sdlc-studio/personas/index.md, correct the story's Persona field"


def _config(panel: str | None, low: int = 3) -> str:
    rule = f"review:\n  solution_review:\n    min_points: {low}\n"
    return rule + (f"    panel: {panel}\n" if panel is not None else "")


def _main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = critic.main(argv)
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else 1
    return rc, out.getvalue(), err.getvalue()


def _tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


class SolutionReviewPanelBriefTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.root = self.project("main")

    def project(self, name: str, config: str = PANEL, registry: bool = True,
                role: str = "Primary") -> Path:
        root = self.tmp / name
        (root / "src").mkdir(parents=True)
        (root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        for card in sorted((REPO / "sdlc-studio" / "personas" / "seats").glob("*.md")):
            shutil.copy(card, seats / card.name)
        (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")
        pdir = root / "sdlc-studio" / "personas"
        if registry:
            template = (SKILL / "templates" / "personas" / "persona-template.md").read_text(
                encoding="utf-8")
            rowan = re.sub(r"\{\{[^}]*\}\}", "Rowan Test", template)
            rowan = re.sub(r"(\*\*Cast role\*\* \|)[^|\n]*", r"\1 Secondary ", rowan)
            (pdir / "rowan-test.md").write_text(rowan, encoding="utf-8")
            (pdir / "abena-osei.md").write_text(_CARD.format(name="Abena Osei", role=role),
                                                encoding="utf-8")
            (pdir / "index.md").write_text(
                "# Personas\n\n## Primary\n\n- [Abena Osei](abena-osei.md) - the lead\n"
                "- [Ghost Card](ghost-card.md) - a card never written\n\n## Secondary\n\n"
                "- [Rowan Test](rowan-test.md) - from the template\n", encoding="utf-8")
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for uid, who in ((UNIT, "Abena Osei"), (ROWAN, "Rowan Test"), ("US0003", "Ghost Card"),
                         ("US0004", "Dani (Engineering)")):
            (stories / f"{uid}-a-story.md").write_text(
                _STORY.format(uid=uid, persona=f"> **Persona:** {who}\n"), encoding="utf-8")
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (bugs / f"{BUG}-a-bug.md").write_text(_STORY.format(uid=BUG, persona=""),
                                              encoding="utf-8")
        (root / "note.md").write_text(_NOTE, encoding="utf-8")
        return root

    def run_cli(self, *argv: str, root: Path | None = None) -> tuple[int, str, str]:
        return _main([*argv, "--root", str(root or self.root)])

    def brief(self, seat: str, unit: str = UNIT, root: Path | None = None):
        root = root or self.root
        return self.run_cli("approach", "brief", "--unit", unit, "--seat", seat, "--note",
                            str(root / "note.md"), root=root)

    def panel(self, unit: str = UNIT, root: Path | None = None):
        root = root or self.root
        return self.run_cli("approach", "panel", "--unit", unit, "--note",
                            str(root / "note.md"), root=root)

    def record(self, reviewer: str, verdict: str, changes: str | None = None,
               unit: str = UNIT, root: Path | None = None) -> None:
        root = root or self.root
        argv = ["approach", "record", "--unit", unit, "--verdict", verdict, "--note",
                str(root / "note.md"), "--reviewer", reviewer, "--author", AUTHOR]
        if changes is not None:
            path = self.tmp / f"changes-{len(list(self.tmp.iterdir()))}.md"
            path.write_text(changes, encoding="utf-8")
            argv += ["--changes", str(path)]
        rc, _out, err = self.run_cli(*argv, root=root)
        self.assertEqual(rc, 0, err)

    def refused(self, run, *words: str) -> None:
        rc, out, err = run
        self.assertEqual((rc, out), (2, ""), err)
        for word in words:
            self.assertIn(word, err)

    def test_the_panel_names_one_brief_and_one_reply_file_per_seat(self) -> None:
        self.record(QA, "changes", "VERDICT: CHANGES\n1. name the guard\n2. pin it")
        before = _tree(self.root)
        rc, out, err = self.panel()
        self.assertEqual(rc, 0, err)
        self.assertEqual(_tree(self.root), before, "the panel writes nothing")
        note = str((self.root / "note.md").resolve())
        lines = [ln for ln in out.splitlines() if ln.startswith("- ")]
        expect = [(QA, "qa", 2, "latest CHANGES at round 1"),
                  (PRODUCT, "product", 1, "no verdict yet"),
                  (PERSONA, "persona", 1, "no verdict yet")]
        self.assertEqual(len(lines), 3, out)
        for line, (who, seat, rnd, latest) in zip(lines, expect):
            self.assertEqual(line, f"- {who} at round {rnd} ({latest}): critic.py approach brief "
                                   f"--unit {UNIT} --seat {seat} --note {note}; reply file "
                                   f"sdlc-studio/.local/solution-review/{UNIT}-{seat}-r{rnd}.md")
        for sentence in ("Each brief goes to its own agent, never two in one brief.",
                         "resumes that seat's own agent where the host can, and otherwise "
                         "briefs a fresh agent for that seat",
                         f"through `sprint.py lane brief --units {UNIT}`",
                         "agreed when every seat has a GO on the note's digest now",
                         "The agent that reviewed the approach does not review the code"):
            self.assertIn(sentence, out)
        for word in ("SendMessage", "subagent_type", "Task("):
            self.assertNotIn(word, out)
        unset = self.project("unset", config="review:\n  solution_review:\n    min_points: 3\n")
        rc, out, err = self.panel(root=unset)
        self.assertEqual(rc, 0, err)
        self.assertIn("is unset, so one seat's GO on the note's digest now agrees", out)
        self.assertIn(f"critic.py approach brief --unit {UNIT} --seat <seat> --note", out)
        self.assertNotIn("reply file", out)

    def test_the_stakeholder_brief_frames_the_persona_and_no_seat(self) -> None:
        reg = critic.sdlc_md.persona_registry(self.root)
        for unit, name, rnd in ((UNIT, "Abena Osei", 1), (ROWAN, "Rowan Test", 1)):
            card = Path(reg.find(name).card)
            self.assertEqual(persona_review.blocking(self.root, card), [], name)
            rc, out, err = self.brief("persona", unit)
            self.assertEqual(rc, 0, err)
            self.assertTrue(out.startswith(f"You are {name}, the stakeholder persona {unit} "
                                           f"serves"), out[:200])
            self.assertIn(f"Read your card at\n{card}, whole, and speak from it.", out)
            self.assertIn("- **Given** a thing", out)
            self.assertIn(_NOTE.rstrip(), out)
            for ask in ("meet when they upgrade", "defend each sentence the plan states",
                        "work or spend in the plan they would not sign off"):
                self.assertIn(ask, out)
            for word in (*SECTIONS, "personas/seats", "review seat", "review render"):
                self.assertNotIn(word, out)
            self.assertIn(f"--reviewer '{name} (persona)'", out)
            self.assertIn(f"solution-review/{unit}-persona-r{rnd}.md", out)
            self.assertIn(QA, out)
            self.assertIn(PRODUCT, out)
        rc, out, err = self.brief("qa")
        self.assertEqual(rc, 0, err)
        self.assertIn(f"seats {PRODUCT}, {PERSONA} as separate reviewers", out)
        self.assertIn("adopt none of them", out)
        self.assertIn(f"--reviewer '{QA}'", out)
        self.assertIn(f"--changes {self.root.resolve()}/sdlc-studio/.local/solution-review/"
                      f"{UNIT}-qa-r1.md", out)

    def test_a_later_round_quotes_the_seat_s_own_changes(self) -> None:
        self.record(QA, "changes", "VERDICT: CHANGES\n1. see line 12. Then guard it\n2. pin it")
        self.record(PRODUCT, "go")
        (self.root / "note.md").write_text(_NOTE + "\nRevised.\n", encoding="utf-8")
        _rc, qa, _err = self.brief("qa")
        self.assertIn("Round 2 of your review.", qa)
        self.assertIn("> 1. see line 12. Then guard it\n> 2. pin it\n", qa)
        self.assertIn("check each is answered in the note", qa)
        for seat in ("product", "persona"):
            _rc, out, _err = self.brief(seat)
            self.assertNotIn("guard it", out)
            self.assertNotIn("\n> ", out)
        _rc, product, _err = self.brief("product")
        self.assertIn("Your GO at round 1 was on note digest", product)
        for out in (qa, product, self.brief("persona")[1]):
            assert_one_identity(out, self.root)
        unset = self.project("unset", config="review:\n  solution_review:\n    min_points: 3\n")
        first = self.brief("qa", root=unset)
        self.record(QA, "changes", "1. one\n2. two", root=unset)
        self.assertEqual(self.brief("qa", root=unset), first)
        self.assertNotIn("Round", first[1])
        self.assertEqual(critic._quoted_changes(r"1. a\_b 2) c 10. d 3. e"),
                         ["> 1. a_b", "> 2) c 10. d", "> 3. e"])
        self.assertEqual(critic._quoted_changes("no items here"), ["> no items here"])

    def test_a_persona_that_cannot_be_framed_is_refused(self) -> None:
        remedy = "register it in sdlc-studio/personas/index.md, correct the story's Persona field"
        for verb in (self.brief, self.panel):
            args = ("persona", "US0004") if verb == self.brief else ("US0004",)
            self.refused(verb(*args), "Dani (Engineering)", "sdlc-studio/personas/index.md",
                         remedy)
            args = ("persona", "US0003") if verb == self.brief else ("US0003",)
            self.refused(verb(*args), "ghost-card.md", "names no file", remedy)
        bare = self.project("bare", registry=False)
        self.refused(self.brief("persona", root=bare), "index.md",
                     "`persona` on `review.solution_review.panel`", remedy)
        self.refused(self.panel(root=bare), "index.md", remedy)
        held = self.project("held", role="Secondary")
        for run in (self.brief("persona", root=held), self.panel(root=held)):
            self.refused(run, "abena-osei.md", "persona-registry-role", "persona_review.py brief",
                         remedy)
        report = self.project("report", config=PANEL + "personas:\n  standard: report\n",
                              role="Secondary")
        for rc, out, err in (self.brief("persona", root=report), self.panel(root=report)):
            self.assertEqual(rc, 0, err)
            self.assertTrue(out)
            self.assertEqual(len(err.splitlines()), 1, err)
            self.assertIn("abena-osei.md", err)
        self.refused(self.brief("persona", BUG), "names no Persona")
        rc, out, err = self.panel(BUG)
        self.assertEqual(rc, 0, err)
        self.assertEqual([ln.split(" at round")[0] for ln in out.splitlines()
                          if " at round " in ln], [f"- {QA}", f"- {PRODUCT}"])
        self.assertIn("no stakeholder sits", out)
        self.assertEqual(self.brief("persona")[0], 0)
        self.assertEqual(self.panel()[0], 0)

    def test_the_code_review_stays_independent_and_the_runbook_names_the_panel(self) -> None:
        story = self.root / "sdlc-studio" / "stories" / f"{UNIT}-a-story.md"
        story.write_text(story.read_text(encoding="utf-8").replace("Abena Osei", "Maya Okafor"),
                         encoding="utf-8")
        index = self.root / "sdlc-studio" / "personas" / "index.md"
        index.write_text(index.read_text(encoding="utf-8") + "- [Maya Okafor](abena-osei.md) - "
                         "a second\n", encoding="utf-8")
        seats = ("qa", "product", "engineering")
        before = {s: self.run_cli("brief", "--unit", UNIT, "--seat", s) for s in seats}
        reply = "VERDICT: CHANGES\n1. the reply line nobody else reads"
        self.record(QA, "changes", reply)
        self.record(PRODUCT, "go")
        self.record("Maya Okafor (persona)", "go")
        for seat in seats:
            rc, out, err = self.run_cli("brief", "--unit", UNIT, "--seat", seat)
            self.assertEqual(rc, 0, err)
            for word in ("solution-review/", "the reply line nobody else reads", "Maya Okafor"):
                self.assertNotIn(word, out, seat)
            for word in ("GO", "CHANGES"):
                self.assertEqual(out.count(word), before[seat][1].count(word), (seat, word))
            self.assertEqual("fresh context that has not read the note" in err,
                             seat != "engineering", (seat, err))
        runbook = (SKILL / "reference-sprint-toolchain.md").read_text(encoding="utf-8")
        row = next(ln for ln in runbook.splitlines() if ln.startswith("| Review a builder's"))
        self.assertEqual(len(row.strip("|").split(" | ")), 3, row)
        for cmd in ("critic.py approach panel", "critic.py approach brief",
                    "critic.py approach record"):
            self.assertIn(cmd, row)
        page = (SKILL / "reference-scripts-review.md").read_text(encoding="utf-8")
        entry = re.search(r"(?ms)^### `critic\.py`\n(.*?)(?=^### )", page).group(1)
        for word in ("approach panel", "--seat persona", "solution-review/",
                     "the reviewing seat's rows for the unit so far plus one",
                     "no roster names a persona brief that would be refused"):
            self.assertIn(word, entry)
        rc, out, err = _docgen_check()
        self.assertEqual(rc, 0, out + err)


    def seat_lines(self, out: str) -> list[str]:
        return [ln.split(" at round")[0] for ln in out.splitlines() if " at round " in ln]

    def test_a_panel_without_the_persona_prints_whatever_the_persona(self) -> None:
        two = self.project("two", config=_config("[qa, product]"))
        held = self.project("held", config=_config("[qa, product]"), role="Secondary")
        for unit, root in (("US0004", two), ("US0003", two), (UNIT, held)):
            rc, out, err = self.panel(unit, root=root)
            self.assertEqual(rc, 0, err)
            self.assertEqual(self.seat_lines(out), [f"- {QA}", f"- {PRODUCT}"], unit)
            for word in ("(persona)", "abena-osei.md", "ghost-card.md", "Dani (Engineering)"):
                self.assertNotIn(word, out + err, unit)

    def test_a_seat_s_go_after_its_changes_quotes_nothing(self) -> None:
        self.record(QA, "changes", "VERDICT: CHANGES\n1. name the guard")
        self.record(QA, "go")
        rc, out, err = self.panel()
        self.assertEqual(rc, 0, err)
        self.assertIn(f"- {QA} at round 3 (latest GO at round 2): ", out)
        self.assertIn(f"solution-review/{UNIT}-qa-r3.md", out)
        then = critic.note_digest(self.root / "note.md")
        _rc, qa, _err = self.brief("qa")
        self.assertIn("Round 3 of your review.", qa)
        self.assertNotIn("name the guard", qa)
        self.assertNotIn("\n> ", qa)
        self.assertIn(f"Your GO at round 2 is on the note as it stands (digest {then}).", qa)
        self.assertNotIn("has changed since", qa)
        (self.root / "note.md").write_text(_NOTE + "\nRevised.\n", encoding="utf-8")
        now = critic.note_digest(self.root / "note.md")
        _rc, qa, _err = self.brief("qa")
        self.assertIn(f"Your GO at round 2 was on note digest {then}, and the note has changed "
                      f"since (digest now {now}), so judge it again.", qa)
        self.assertNotIn("as it stands", qa)

    def test_a_seat_off_the_panel_gets_the_one_seat_brief_and_a_warning(self) -> None:
        two = self.project("two", config=_config("[qa, product]"))
        rc, out, err = self.brief("persona", root=two)
        self.assertEqual(rc, 0, err)
        self.assertTrue(out.startswith("You are Abena Osei, the stakeholder persona"), out[:120])
        for word in ("Panel:", "Round ", "solution-review/", QA, PRODUCT):
            self.assertNotIn(word, out)
        self.assertIn("a file under $TMPDIR (REVIEW.md below)", out)
        self.assertIn("--changes REVIEW.md --note", out)
        self.assertIn(f"will refuse this seat's verdict on {UNIT}: `review.solution_review.panel` "
                      f"is [qa, product], which seats qa, product on {UNIT}", err)
        off = self.project("off", config=_config("[product, persona]"))
        unset = self.project("unset", config=_config(None))
        rc, out, err = self.brief("qa", root=off)
        self.assertEqual(rc, 0, err)
        base = self.brief("qa", root=unset)[1]
        self.assertIn(critic._APPROACH_SEAT_QUESTIONS, out)
        self.assertEqual(out.replace(str(off.resolve()), "R").replace(str(off), "R"),
                         base.replace(str(unset.resolve()), "R").replace(str(unset), "R"))
        self.assertIn(f"will refuse this seat's verdict on {UNIT}: `review.solution_review.panel` "
                      f"is [product, persona], which seats product, persona on {UNIT}", err)
        for root in (self.root, two, unset):
            self.refused(self.brief("persona", BUG, root=root), "names no Persona", REMEDY)

    def test_the_persona_brief_without_a_panel_is_the_one_seat_shape(self) -> None:
        unset = self.project("unset", config=_config(None))
        rc, out, err = self.brief("persona", root=unset)
        self.assertEqual((rc, err), (0, ""))
        self.assertTrue(out.startswith("You are Abena Osei, the stakeholder persona"), out[:120])
        for word in ("Panel:", "Round ", "solution-review/", "creating", QA, PRODUCT):
            self.assertNotIn(word, out)
        self.assertIn("Rules: read-only on the repository.\n", out)
        self.assertIn("a file under $TMPDIR (REVIEW.md below)", out)
        self.assertIn("--verdict changes --changes REVIEW.md --note", out)
        self.assertIn("--reviewer 'Abena Osei (persona)'", out)
        self.assertIn(f"--author '{AUTHOR}'", out)
        self.assertNotIn("- Reading: does the note read", out)
        bare = self.project("bare", config=_config(None), registry=False)
        self.refused(self.brief("persona", root=bare), "need the registry at "
                     "sdlc-studio/personas/index.md.")
        for unit, word in (("US0004", "'Dani (Engineering)' is not registered in "
                                      "sdlc-studio/personas/index.md."), ("US0003", "ghost-card.md"),
                           (BUG, "names no Persona")):
            self.refused(self.brief("persona", unit, root=unset), word, REMEDY)
        _rc, qa, _err = self.brief("qa")
        self.assertIn("Rules: read-only on the repository, except your reply file, creating\n"
                      "sdlc-studio/.local/solution-review/ if it is absent.", qa)

    def test_a_project_persona_seat_card_keeps_the_seat_brief(self) -> None:
        root = self.project("card", config=_config(None) + "personas:\n  standard: report\n")
        seats = root / "sdlc-studio" / "personas" / "seats"
        text = (seats / "qa.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("<!-- role: qa -->"), 1)
        (seats / "persona.md").write_text(text.replace("<!-- role: qa -->",
                                                       "<!-- role: persona -->"),
                                          encoding="utf-8")
        rc, out, err = self.brief("persona", root=root)
        self.assertEqual(rc, 0, err)
        self.assertIn("seat-unknown-role", err)
        self.assertTrue(out.startswith("You are the persona review seat, reviewing a builder's "
                                       "APPROACH"), out[:120])
        self.assertIn("personas/seats/persona.md (the review render)", out)
        self.assertNotIn("Abena Osei", out)

    def test_a_mistyped_persona_standard_refuses_the_held_card(self) -> None:
        typo = self.project("typo", config=PANEL + "personas:\n  standard: reprot\n",
                            role="Secondary")
        for run in (self.brief("persona", root=typo), self.panel(root=typo)):
            self.refused(run, "personas.standard is 'reprot'", "read as block",
                         "persona-registry-role", REMEDY)

    def test_the_panel_resolves_no_seat_card(self) -> None:
        with mock.patch.object(persona_resolve, "review_card",
                               side_effect=AssertionError("the panel resolved a seat card")):
            rc, out, err = self.panel()
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.seat_lines(out), [f"- {QA}", f"- {PRODUCT}", f"- {PERSONA}"])

    def test_the_panel_refuses_what_every_brief_refuses(self) -> None:
        mal = self.project("mal", config=_config("qa"))
        self.refused(self.panel(root=mal), "`review.solution_review.panel` is 'qa', which is not "
                                           "a list")
        rc, out, err = self.brief("qa", root=mal)
        self.assertEqual(rc, 0, err)
        for word in ("Panel:", "Round ", "solution-review/"):
            self.assertNotIn(word, out)
        self.assertIn("is 'qa', which is not a list", err)
        self.refused(self.panel("US9999"), "no artefact with id 'US9999'")
        self.refused(self.run_cli("approach", "panel", "--unit", UNIT, "--note",
                                  str(self.tmp / "absent.md")), "absent.md names no file")
        (self.root / "note.md").write_text("# approach\n\n## Reading\n\nAs written.\n",
                                           encoding="utf-8")
        self.refused(self.panel(), "is not complete")

    def test_the_panel_warns_on_a_unit_that_takes_no_review(self) -> None:
        for panel in ("[qa, product, persona]", None):
            root = self.project(f"low-{bool(panel)}", config=_config(panel, low=5))
            rc, out, err = self.panel(root=root)
            self.assertEqual(rc, 0, err)
            self.assertEqual(err.strip(), f"note: `critic.py approach record` will refuse a "
                                          f"verdict on {UNIT}: it takes no solution review "
                                          f"(3 points, below `review.solution_review.min_points` "
                                          f"5; `review.solution_review.risk_classes` is empty, "
                                          f"so no unit takes it by risk class)", panel)
        self.assertEqual(self.panel()[2], "")

    def test_a_panel_that_seats_nobody_says_the_approach_cannot_be_agreed(self) -> None:
        nobody = (f"`review.solution_review.panel` seats nobody on {UNIT}, so its approach "
                  f"cannot be agreed until the panel names a seat that sits on it.")
        root = self.project("eng", config=_config("[engineering]"))
        rc, out, err = self.panel(root=root)
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.seat_lines(out), [])
        self.assertIn(f"- engineering is skipped: the engineering seat builds {UNIT}", out)
        self.assertIn(nobody, out)
        self.assertNotIn("agreed when every seat has a GO", out)
        self.assertFalse(critic.approach_agreed(root, UNIT, root / "note.md")[0])
        rc, out, err = self.panel()
        self.assertEqual(rc, 0, err)
        self.assertNotIn("seats nobody", out)
        self.assertEqual(critic._quoted_changes("see a1. b 1.5 c 1. d 2. e"),
                         ["> see a1. b 1.5 c", "> 1. d", "> 2. e"])


    def record_as(self, reviewer: str, root: Path | None = None) -> tuple[int, str, str]:
        root = root or self.root
        return self.run_cli("approach", "record", "--unit", UNIT, "--verdict", "go", "--note",
                            str(root / "note.md"), "--reviewer", reviewer, "--author", AUTHOR,
                            root=root)

    def test_an_unset_panel_reads_no_seat_card(self) -> None:
        for panel in (None, "[qa]"):
            root = self.project(f"bad-{bool(panel)}", config=_config(panel))
            (root / "sdlc-studio" / "personas" / "seats" / "bad.md").write_bytes(
                b"<!-- role: data -->\n# \xff\xfe a card saved in another encoding\n")
            with mock.patch.object(critic, "_UNDECODABLE_CARDS", set()):
                rc, _out, err = self.record_as(QA, root=root)
            self.assertEqual(rc, 0, err)
            self.assertEqual("bad.md is not valid UTF-8" in err, panel is not None, (panel, err))
            if panel is None:
                self.assertEqual(critic.solution_review_panel(root), [])
                self.assertEqual(critic.effective_panel(root, UNIT), ([], {}))

    def test_only_the_unit_s_own_persona_sits_in_the_persona_seat(self) -> None:
        for name in ("Abena Osei-Ward", "Not Abena Osei"):
            rc, out, err = self.record_as(f"{name} (persona)")
            self.assertEqual((rc, out), (2, ""), err)
            self.assertIn("only the unit's own Persona sits in the persona seat", err)
        self.assertEqual(critic.read_solution_reviews(self.root, UNIT), [])
        rc, _out, err = self.record_as("abena osei (persona)")
        self.assertEqual(rc, 0, err)
        self.assertIn(f"- {PERSONA} at round 2 (latest GO at round 1): ", self.panel()[1])

def _docgen_check() -> tuple[int, str, str]:
    import docgen  # noqa: PLC0415 - sibling; the surface page's own check
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = docgen.main(["surface", "--check", "--root", str(REPO)])
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else 1
    return rc, out.getvalue(), err.getvalue()


if __name__ == "__main__":
    unittest.main()
