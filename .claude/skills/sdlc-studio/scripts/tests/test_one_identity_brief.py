"""A brief handed to an agent carries exactly one identity: one seat or one persona, never two.

The framing rules and the lesson say so; story creation, epic creation and the amigo panel seat
one agent per seat; and every brief the skill prints is read by one identity reader. The reader
counts the sentences that ask the reader of a brief to BE someone: a seat (`You are the qa review
seat`, `You are the qa amigo`, `adopt the work render of the engineering seat card`) or a persona
the project registers (`You are Abena Osei`). A mention (`Abena Osei (Primary):`) is not an
identity, and a line whose first non-space character is `>` is quoted text, never counted.

`GENERATORS` is the one table of the commands that print a brief, each row naming the identities
its stdout must read; the generators run in-process against one throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/persona_resolve.py
from __future__ import annotations

import contextlib
import io
import os
import re
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
persona_resolve = loader.load_script("persona_resolve")
sprint = loader.load_script("sprint")
from lib import run_state, sdlc_md  # noqa: E402

# parents: [0] tests [1] scripts [2] the shipped skill [5] this repository.
SKILL = Path(__file__).resolve().parents[2]
REPO = Path(__file__).resolve().parents[5]
TEMPLATE = SKILL / "reference-agent-prompt-template.md"
LESSON = SKILL / "lessons" / "LL0057-give-every-subagent-a-persona-a-seated-agent-beats-a-generic-one.md"
STORY_REF = SKILL / "reference-story.md"
EPIC_REF = SKILL / "reference-epic.md"
MODULE = "scripts/tests/test_one_identity_brief.py"
SEATS = ("engineering", "qa", "product")
UNIT = "US0101"
GOAL = "every story serves its persona"

#: A seat the brief asks its reader to be: the review seat sentence and the amigo framing, then
#: the lane brief's seat line.
SEAT_PATTERNS = (
    re.compile(r"\bYou are the ([a-z][a-z0-9-]*) (?:review seat|amigo)\b"),
    re.compile(r"\badopt the (?:work|build|review) render of the ([a-z][a-z0-9-]*) seat card\b"),
)


def _persona_pattern(root: Path) -> re.Pattern | None:
    """`You are <name>` for a name the project's persona registry holds, the longest name tried
    first so a registered name that prefixes another never reads in its place; None with no
    registered name, so an empty alternation never matches every `You are`."""
    names = sorted({e.name for e in sdlc_md.persona_registry(root).entries},
                   key=len, reverse=True)
    if not names:
        return None
    return re.compile(r"You are (" + "|".join(re.escape(n) for n in names) + r")\b")


def identities(text: str, root: Path) -> list[tuple[str, str]]:
    """The distinct identities `text` asks its reader to adopt, in order of appearance, each as
    `("seat", role)` or `("persona", name)`. A quoted line (first non-space character `>`) is
    skipped."""
    persona = _persona_pattern(root)
    patterns = [(rx, "seat") for rx in SEAT_PATTERNS]
    if persona is not None:
        patterns.append((persona, "persona"))
    found: list[tuple[str, str]] = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            continue
        hits = sorted((m.start(), kind, m.group(1))
                      for rx, kind in patterns for m in rx.finditer(line))
        for _start, kind, name in hits:
            if (kind, name) not in found:
                found.append((kind, name))
    return found


def _named(identity: tuple[str, str]) -> str:
    kind, name = identity
    return f"the {name} seat" if kind == "seat" else f"the {name} persona"


def assert_one_identity(text: str, root: Path) -> tuple[str, str]:
    """The one identity `text` reads; AssertionError naming every identity read otherwise."""
    found = identities(text, root)
    if len(found) != 1:
        raise AssertionError(f"the brief reads {len(found)} identities, not one: "
                             + (", ".join(_named(i) for i in found) or "none"))
    return found[0]


class Generator(NamedTuple):
    """One command that prints a brief: its script, its argv (`{unit}`, `{note}`, `{verdict}`
    and `{worklist}` filled from the fixture, `--root` appended) and the identities it reads."""
    label: str
    script: str
    argv: tuple[str, ...]
    reads: tuple[tuple[str, str], ...]


def _seat(role: str) -> tuple[tuple[str, str], ...]:
    return (("seat", role),)


GENERATORS: tuple[Generator, ...] = (
    Generator("lane brief", "sprint", ("lane", "brief", "--units", "{unit}"), _seat("engineering")),
    *(Generator(f"critic brief --seat {s}", "critic", ("brief", "--unit", "{unit}", "--seat", s),
                _seat(s)) for s in SEATS),
    Generator("critic brief --rejoinder", "critic",
              ("brief", "--unit", "{unit}", "--seat", "qa", "--rejoinder", "{verdict}"),
              _seat("qa")),
    *(Generator(f"approach brief --seat {s}", "critic",
                ("approach", "brief", "--unit", "{unit}", "--seat", s, "--note", "{note}"),
                _seat(s)) for s in SEATS),
    *(Generator(f"resolve --seat {s} --render {r}", "persona_resolve",
                ("resolve", "--seat", s, "--render", r), _seat(s))
      for s in SEATS for r in ("build", "review")),
    *(Generator(f"resolve-consult --role {s}", "persona_resolve", ("resolve-consult", "--role", s),
                _seat(s)) for s in SEATS),
    Generator("panel --ceremony refine", "persona_resolve",
              ("panel", "--ceremony", "refine", "--question", "X"), ()),
    *(Generator(f"goal-review brief --seat {s}", "sprint",
                ("goal-review", "brief", "--goal", GOAL, "--brief-worklist", "{worklist}",
                 "--seat", s), _seat(s)) for s in SEATS),
)

_SCRIPTS = {"sprint": sprint, "critic": critic, "persona_resolve": persona_resolve}

_PERSONAS = (("Abena Osei", "Primary"), ("Maya Okafor", "Secondary"))
_PERSONA_CARD = ("# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
                 "| **Cast role** | {role} |\n\n## Who They Are\n\nSomebody.\n")
_STORY = (f"# {UNIT}: a story with a persona\n\n> **Status:** Ready\n"
          f"> **Affects:** src/app.py, tests/test_app.py, changelog.d/{UNIT}.md\n"
          "> **Points:** 3\n> **Persona:** Abena Osei\n\n"
          "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/app.py\n\n"
          "### AC2: it still holds\n\n- **Verify:** file src/app.py\n")
_NOTE = (f"# {UNIT} approach\n\n## Reading\n\nAs written.\n\n## Design\n\nOne function.\n\n"
         "## What it may break\n\nNothing reads it.\n\n## Tests\n\nAC1 and AC2 each get a test.\n\n"
         "## Sentences\n\nThe fragment.\n")
_VERDICT = (f"UNIT: {UNIT}\nVERDICT: REJECT\nISSUES: [new] the guard is unpinned\n"
            "BLOCKING: [new] the guard is unpinned\n")


def _copy_seats(root: Path) -> None:
    """This repository's three seat cards, as the project's own."""
    seats = root / "sdlc-studio" / "personas" / "seats"
    seats.mkdir(parents=True, exist_ok=True)
    for card in sorted((REPO / "sdlc-studio" / "personas" / "seats").glob("*.md")):
        shutil.copy(card, seats / card.name)


def _registry(root: Path, names: tuple[tuple[str, str], ...]) -> None:
    pdir = root / "sdlc-studio" / "personas"
    pdir.mkdir(parents=True, exist_ok=True)
    lines = ["# Personas", ""]
    for name, role in names:
        slug = name.lower().replace(" ", "-")
        (pdir / f"{slug}.md").write_text(_PERSONA_CARD.format(name=name, role=role),
                                         encoding="utf-8")
        lines += [f"## {role}", "", f"- [{name}]({slug}.md) - a {role.lower()} persona", ""]
    (pdir / "index.md").write_text("\n".join(lines), encoding="utf-8")


def _fixture(root: Path) -> dict[str, str]:
    """Project seat cards, a persona registry, a 3-point story serving Abena Osei, a complete
    approach note, a prior qa verdict and an open run; returns the argv placeholders."""
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    _copy_seats(root)
    _registry(root, _PERSONAS)
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    (stories / f"{UNIT}-a-story.md").write_text(_STORY, encoding="utf-8")
    note = root / "approach.md"
    note.write_text(_NOTE, encoding="utf-8")
    verdict = root / "prior-verdict.txt"
    verdict.write_text(_VERDICT, encoding="utf-8")
    worklist = root / "worklist.txt"
    worklist.write_text(f"{UNIT}\n", encoding="utf-8")
    run_state.open_run(root, batch=[UNIT], goal=GOAL)
    return {"unit": UNIT, "note": str(note), "verdict": str(verdict), "worklist": str(worklist)}


def _main(script: str, argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
            unittest.mock.patch.object(sys, "stdin", io.StringIO("")):
        try:
            rc = _SCRIPTS[script].main(argv)
        except SystemExit as exc:  # argparse refusing a verb the script does not have
            rc = exc.code if isinstance(exc.code, int) else 1
    return rc, out.getvalue(), err.getvalue()


def _run(row: Generator, root: Path, slots: dict[str, str]) -> tuple[int, str, str]:
    return _main(row.script, [a.format(**slots) for a in row.argv] + ["--root", str(root)])


def _step(path: Path, title: str) -> str:
    """A numbered step's block: from its `N. **title**` line to the next top-level item, heading
    or rule, the rule the create-path review test cuts a step by."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, ln in enumerate(lines) if re.match(rf"^\d+\. \*\*{re.escape(title)}", ln))
    end = next((j for j in range(start + 1, len(lines))
                if re.match(r"^(\d+[a-z]?\. |#|---)", lines[j])), len(lines))
    return "\n".join(lines[start:end])


def _paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n[ \t]*\n", text) if p.strip()]


class OneIdentityBriefTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls._tmp.cleanup)
        base = Path(cls._tmp.name)
        home = base / "home"
        home.mkdir()
        env = unittest.mock.patch.dict(os.environ, {
            "HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_DATA_HOME": str(home / ".local" / "share"),
            "XDG_STATE_HOME": str(home / ".local" / "state"),
            "XDG_CACHE_HOME": str(home / ".cache"), "CLAUDE_CONFIG_DIR": str(home / ".claude"),
            "TMPDIR": str(base)})
        env.start()
        cls.addClassCleanup(env.stop)
        cls.root = base / "repo"
        cls.slots = _fixture(cls.root)
        # a root with no persona registry, and one whose registered names prefix each other
        cls.bare = base / "bare"
        _copy_seats(cls.bare)
        cls.prefixed = base / "prefixed"
        _registry(cls.prefixed, (("Maya Okafor", "Primary"), ("Maya Okafor-Smith", "Secondary")))

    def _brief(self, label: str) -> str:
        row = next(r for r in GENERATORS if r.label == label)
        rc, out, err = _run(row, self.root, self.slots)
        self.assertEqual(0, rc, f"{label} refused: {err}")
        return out

    def test_the_framing_rules_say_one_identity_per_brief(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        lines = text.splitlines()
        opening = [i for i, ln in enumerate(lines) if "rules govern the framing" in ln]
        self.assertEqual(1, len(opening), "the framing list's opening line")
        self.assertEqual("Five rules govern the framing, none negotiable:", lines[opening[0]])
        item, inside = [], False
        for ln in lines[opening[0] + 1:]:
            if re.match(r"^\d+\. ", ln):
                inside = ln.startswith("5. ")
                if not inside and item:
                    break
            elif not ln.strip():
                if item:
                    break
                continue
            if inside:
                item.append(ln.strip())
        rule = " ".join(item)
        self.assertTrue(rule, "the framing list has no fifth rule")
        body = re.sub(r"^5\.\s+(\*\*[^*]+\*\*\s*)?", "", rule)
        first = re.split(r"(?<=\.)\s", body, maxsplit=1)[0]
        for phrase in ("brief handed to an agent", "exactly one identity",
                       "one seat or one persona", "never two"):
            self.assertIn(phrase, first, f"the fifth rule's first sentence: {first!r}")
        for phrase in ("several agents", "one brief each", "recorded files",
                       "the orchestrator passes on", "no agent speaks for another",
                       f"`{MODULE}`", "the lane, review, approach and seat briefs the skill prints"):
            self.assertIn(phrase, rule, f"the fifth rule: {rule!r}")
        self.assertNotIn("generator", rule)
        self.assertNotIn("every shipped", rule)
        paras = _paragraphs(text)
        self.assertEqual(1, sum("fresh builder" in p for p in paras))
        self.assertEqual(1, sum("without subagents" in p and "lane run" in p for p in paras))
        lesson = LESSON.read_text(encoding="utf-8")
        apply = next(p for p in _paragraphs(lesson) if p.startswith("**How to apply.**"))
        for phrase in ("one seat or one persona", "never two", "no agent speaks for another"):
            self.assertIn(phrase, apply, "LL0057's How to apply")
        guard = next(p for p in _paragraphs(lesson) if p.startswith("**Guard.**"))
        self.assertIn(f"`{MODULE}`", guard)
        self.assertNotIn("None yet", guard)
        # `lessons.is_guarded` demotes a lesson on a `**Guard:**` field; this guard covers one
        # part of the lesson, so the spelling stays `**Guard.**`
        self.assertNotIn("**Guard:**", lesson)

    def test_the_create_workflows_and_the_panel_seat_one_agent_per_seat(self) -> None:
        story = _step(STORY_REF, "Three Amigos Consultation (Default)")
        epic = _step(EPIC_REF, "Three Amigos + Stakeholder Assessment (Default)")
        flat_story, flat_epic = " ".join(story.split()), " ".join(epic.split())
        for phrase in ("Each seat is its own agent", "three agents in parallel, one per seat",
                       "each reviewing the stories the run generated",
                       "more than one agent only when its stories will not fit in one"):
            self.assertIn(phrase, flat_story, "reference-story.md step 9")
        for gone in ("one agent per epic", "Per-epic batch"):
            self.assertNotIn(gone, flat_story)
        self.assertIn("Each seat is its own agent with its own brief", flat_epic)
        self.assertIn("each affected stakeholder persona as its own agent with its own brief",
                      flat_epic)
        command = re.compile(r"persona_resolve\.py resolve --seat <product\|engineering\|qa> "
                             r"--render review")
        for name, block, flat in (("story", story, flat_story), ("epic", epic, flat_epic)):
            with self.subTest(step=name):
                self.assertEqual([], [ln for ln in block.splitlines()
                                      if "perspective" in ln.lower()])
                self.assertRegex(block, command)
                self.assertIn("seats ship with the skill", flat)
                self.assertIn("needs no project user personas", flat)
        self.assertLessEqual(len(EPIC_REF.read_text(encoding="utf-8").splitlines()), 1106)
        rc, out, err = _main("persona_resolve", ["panel", "--ceremony", "refine", "--question",
                                                 "Is the panel fixed?", "--root", str(self.root)])
        self.assertEqual(0, rc, err)
        lines = out.splitlines()
        self.assertTrue(lines[0].startswith("refine amigo panel (Dani Okafor leads): "), out)
        self.assertEqual("brief one agent per seat with `persona_resolve.py resolve --seat <role> "
                         "--render review` and take these 1 question(s) to each:", lines[1])
        self.assertEqual("  - Is the panel fixed?", lines[2])

    def test_a_merged_brief_reads_two_identities(self) -> None:
        lane = self._brief("lane brief")
        qa_first = self._brief("critic brief --seat qa").splitlines()[0]
        self.assertIn("You are the qa review seat", qa_first)
        persona = "You are Abena Osei, the persona this unit serves."
        cases = (
            (lane, [("seat", "engineering")]),
            (f"{lane}\n{qa_first}\n", [("seat", "engineering"), ("seat", "qa")]),
            (f"{lane}\n{persona}\n", [("seat", "engineering"), ("persona", "Abena Osei")]),
            (f"{lane}\n> You are the qa review seat.\n", [("seat", "engineering")]),
        )
        for i, (text, expected) in enumerate(cases, 1):
            with self.subTest(case=i):
                self.assertEqual(expected, identities(text, self.root))
        self.assertEqual(("seat", "engineering"), assert_one_identity(cases[0][0], self.root))
        self.assertEqual(("seat", "engineering"), assert_one_identity(cases[3][0], self.root))
        for text, second in ((cases[1][0], "the qa seat"), (cases[2][0], "the Abena Osei persona")):
            with self.assertRaises(AssertionError) as caught:
                assert_one_identity(text, self.root)
            self.assertIn("reads 2 identities", str(caught.exception))
            self.assertIn("the engineering seat", str(caught.exception))
            self.assertIn(second, str(caught.exception))

    def test_every_brief_the_skill_prints_carries_one_identity(self) -> None:
        # the note the approach brief embeds verbatim reads none, so its rows read the brief's own
        self.assertEqual([], identities(_NOTE, self.root))
        for row in GENERATORS:
            with self.subTest(generator=row.label):
                rc, out, err = _run(row, self.root, self.slots)
                self.assertEqual(0, rc, f"{row.label} refused: {err}")
                self.assertEqual(list(row.reads), identities(out, self.root), out[-3000:])
                if row.script == "sprint" and row.argv[0] == "goal-review":
                    # both registered personas are named, as mentions, never as identities
                    self.assertIn("Abena Osei", out)
                    self.assertIn("Maya Okafor", out)
                if "--rejoinder" in row.argv:
                    self.assertIn("RE-REVIEW", out)

    def test_the_reader_keeps_the_order_of_appearance(self) -> None:
        seat = "Seat: adopt the work render of the qa seat card x.md - it frames how you build."
        self.assertEqual([("persona", "Maya Okafor"), ("seat", "qa")],
                         identities(f"You are Maya Okafor, a persona.\n{seat}\n", self.root))
        self.assertEqual([("persona", "Abena Osei"), ("seat", "qa")],
                         identities("You are Abena Osei. You are the qa amigo.", self.root))
        twice = f"{seat}\n{seat}\nYou are the qa review seat."
        self.assertEqual([("seat", "qa")], identities(twice, self.root))

    def test_quoted_and_near_miss_lines_read_none(self) -> None:
        for text in ("    > You are the qa review seat.", "> Seat: adopt the work render of the "
                     "qa seat card x.md", "Abena Osei (Primary): ships the release.",
                     "You are Ravi Unknown, the persona this unit serves.",
                     "You are Abena Oseiwa, a persona.", "XYou are the qa review seat.",
                     "You are the qa review seats.", "You are the qa amigos.",
                     "readopt the work render of the qa seat card x.md",
                     "adopt the work render of the qa seat cards"):
            with self.subTest(text=text):
                self.assertEqual([], identities(text, self.root))
        with self.assertRaises(AssertionError) as caught:
            assert_one_identity("nobody is named here", self.root)
        self.assertIn("reads 0 identities, not one: none", str(caught.exception))

    def test_the_registry_bounds_a_persona(self) -> None:
        self.assertEqual([("persona", "Maya Okafor-Smith")],
                         identities("You are Maya Okafor-Smith, a persona.", self.prefixed))
        self.assertEqual([("persona", "Maya Okafor")],
                         identities("You are Maya Okafor, a persona.", self.prefixed))
        # no registry: a seat still reads, and no `You are` reads as an empty persona name
        self.assertEqual([("seat", "qa")],
                         identities("You are the qa review seat. You are someone.", self.bare))

    def test_the_panel_without_a_question_or_with_unframed_seats(self) -> None:
        rc, out, err = _main("persona_resolve", ["panel", "--ceremony", "refine",
                                                 "--root", str(self.root)])
        self.assertEqual(0, rc, err)
        self.assertEqual(1, len(out.splitlines()), out)
        self.assertTrue(out.startswith("refine amigo panel (Dani Okafor leads): "), out)
        rc, out, err = _main("persona_resolve", ["panel", "--ceremony", "triage", "--question",
                                                 "Is it real?", "--skip-personas",
                                                 "--root", str(self.root)])
        self.assertEqual(0, rc, err)
        lines = out.splitlines()
        self.assertTrue(lines[0].startswith("triage amigo panel (Qa leads): "), out)
        self.assertEqual("brief one agent per seat and take these 1 question(s) to each:",
                         lines[1])
        self.assertEqual(["  - Is it real?"], lines[2:])
        self.assertEqual([], identities(out, self.root))


if __name__ == "__main__":
    unittest.main()
