"""`validate.py seats` warns when a seat card names a persona the cast does not declare, or
declares in a different role than the card claims.

A claim is read over whitespace-joined text (a wrapped sentence counts), reported at the line
where the name starts, and judged against the registry's declared role, falling back to the
persona card's Cast role when the registry does not name them or there is none. A word that
opens a clause, asks a question or abbreviates is no name. Warnings only: the seat check's errors
are the team-generation floor, and a persona claim never fails it.

Driven through `validate.main`, the shipped entry point, in throwaway trees.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

validate = loader.load_script("validate")

AMIGOS = loader.SCRIPTS_DIR.parent / "templates" / "personas" / "amigos"
PERSONA_RULES = {"seat-persona-unknown", "seat-persona-role"}

_SEAT = """<!-- role: {role} -->

# {name} - {role} seat

## Who They Are

A reviewer with a long memory.

## Proficiency

{proficiency}

## Lens

{lens}

## Pushes Back When

- the contract is vague

## Shadow

Over-reaches when tired.
"""

_PERSONA = ("# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
            "| **Cast role** | {role} |\n\n## Who They Are\n\nSomebody.\n")


def _personas(root: Path, cards: dict[str, str], registry: dict[str, list[str]] | None) -> None:
    """Persona cards `{name: Cast role}`, and `personas/index.md` declaring `{role: [names]}`
    (None writes no registry)."""
    pdir = root / "sdlc-studio" / "personas"
    pdir.mkdir(parents=True, exist_ok=True)
    for name, role in cards.items():
        slug = name.lower().replace(" ", "-")
        (pdir / f"{slug}.md").write_text(_PERSONA.format(name=name, role=role), encoding="utf-8")
    if registry is not None:
        body = ["# Persona Index", ""]
        for role, names in registry.items():
            body += [f"## {role}", ""]
            body += [f"- [{n}]({n.lower().replace(' ', '-')}.md) - somebody." for n in names]
            body += [""]
        (pdir / "index.md").write_text("\n".join(body), encoding="utf-8")


def _seat(root: Path, role: str, name: str, *, proficiency: str = "- **Cold:** the contract.",
          lens: str = "- Does it hold?") -> Path:
    sdir = root / "sdlc-studio" / "personas" / "seats"
    sdir.mkdir(parents=True, exist_ok=True)
    path = sdir / f"{role}.md"
    path.write_text(_SEAT.format(role=role, name=name, proficiency=proficiency, lens=lens),
                    encoding="utf-8")
    return path


def _seats(root: Path) -> tuple[int, list[dict]]:
    """`validate.py seats --format json`: the exit code and every persona finding."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = validate.main(["seats", "--root", str(root), "--format", "json"])
    found = json.loads(out.getvalue())["violations"]
    return rc, [v for v in found if v["rule"] in PERSONA_RULES]


def _line_of(path: Path, needle: str) -> int:
    return next(i for i, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
                if needle in ln)


_CAST = {"Maya Okafor": "Primary", "Rowan Achterberg": "Primary", "Jonah Reyes": "Primary",
         "Trevor Hale": "Negative"}
_REGISTRY = {"Primary": ["Maya Okafor", "Rowan Achterberg"], "Secondary": ["Jonah Reyes"],
             "Negative": ["Trevor Hale"]}


class SeatCastTests(unittest.TestCase):

    def test_unknown_primary_named_with_card_and_line(self) -> None:
        """Mutants: extract no name after the role phrase; drop the line number; raise the
        finding to an error that fails the generation flow."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, _CAST, _REGISTRY)
            card = _seat(root, "product", "Lena Park", proficiency=(
                "- **Cold:** requirements fidelity, the primary persona (Darren) and his\n"
                "  goals, ruthless scope-cutting."))
            rc, found = _seats(root)
            self.assertEqual(rc, 0, found)
            self.assertEqual([(f["rule"], Path(f["file"]).name, f["line"]) for f in found],
                             [("seat-persona-unknown", card.name,
                               _line_of(card, "primary persona (Darren)"))], found)
            self.assertEqual(found[0]["severity"], "warning")
            self.assertIn("Darren", found[0]["message"])
            self.assertIn(f"line {found[0]['line']}", found[0]["message"])
            # The text output names the card and the line too.
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                validate.main(["seats", "--root", str(root)])
            row = next(ln for ln in out.getvalue().splitlines() if "seat-persona-unknown" in ln)
            self.assertIn(str(card), row)
            self.assertIn(f"line {found[0]['line']}", row)

    def test_role_the_registry_does_not_declare_warns(self) -> None:
        """Mutants: never compare the claimed role; compare it with the card's Cast role while
        the registry is there to read."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, _CAST, _REGISTRY)   # Jonah's card says Primary; the registry, Secondary
            card = _seat(root, "engineering", "Dani Okafor", lens=(
                "- Judges each design against the Primary persona, Jonah Reyes, and his goals."))
            rc, found = _seats(root)
            self.assertEqual(rc, 0, found)
            self.assertEqual([(f["rule"], Path(f["file"]).name, f["line"]) for f in found],
                             [("seat-persona-role", card.name,
                               _line_of(card, "Primary persona, Jonah"))], found)
            self.assertIn("Jonah Reyes", found[0]["message"])
            self.assertIn("Secondary", found[0]["message"])
            # With no registry to read, the card's own Cast role (Primary) is the declared one.
            (root / "sdlc-studio" / "personas" / "index.md").unlink()
            self.assertEqual(_seats(root)[1], [])

    def test_consistent_cards_draw_no_persona_warning(self) -> None:
        """Mutants: read 'End' after "persona's" as a name; match within one line only, so the
        wrapped claim goes unread; resolve a name on its full form only; read fenced code; drop
        the `Name (Role)` form; read a capitalised article (`persona: The one`) as a name."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, _CAST, _REGISTRY)
            product = _seat(root, "product", "Lena Park", proficiency=(
                "- **Cold:** judging every story against the Primary\n"
                "  design persona is Maya Okafor, and against a Primary design persona's End\n"
                "  goal whichever interface it touches."), lens=(
                "- Does it serve Rowan Achterberg (Primary) for the tooling interface?\n"
                "- Or the Secondary persona: Jonah, never at a Primary's expense?\n"
                "- Never the Negative persona: The one the product declines."))
            _seat(root, "qa", "Sam Eriksson", lens=(
                "- Would the Negative persona, Trevor, be pleased? Then decline it.\n\n"
                "```text\nan example claim, never read: the Primary persona is Darren\n```"))
            self.assertEqual(_seats(root), (0, []))
            # Positive controls: the wrapped claim IS read - an unknown name in it is reported
            # at the line where the name starts - and so is the `Name (Role)` form.
            product.write_text(product.read_text(encoding="utf-8").replace(
                "is Maya Okafor", "is Darren Cole").replace(
                "Achterberg (Primary)", "Achterberg (Secondary)"), encoding="utf-8")
            found = _seats(root)[1]
            self.assertEqual([(f["rule"], f["line"]) for f in found],
                             [("seat-persona-unknown", _line_of(product, "is Darren Cole")),
                              ("seat-persona-role", _line_of(product, "(Secondary)"))])


class ShippedCardTests(unittest.TestCase):

    def test_shipped_amigo_cards_read_without_false_positives(self) -> None:
        """The shipped cards name no cast member, so a project copying them into its own
        `personas/seats/` draws no persona warning whatever its cast. Mutants: a pattern tuned
        to these fixtures that misreads the shipped cards' prose as a claim; a worked example
        naming a persona."""
        cards = sorted(AMIGOS.glob("*.md"))
        self.assertEqual([p.name for p in cards], ["engineering.md", "product.md", "qa.md"])
        for cast, registry in (({"Sam Patel": "Primary"}, {"Primary": ["Sam Patel"]}),
                               ({"Sam Patel": "Primary"}, None),
                               ({"Maya Okafor": "Primary"}, {"Primary": ["Maya Okafor"]}),
                               ({}, None)):
            with self.subTest(cast=sorted(cast), registry=registry is not None), \
                    tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _personas(root, cast, registry)
                sdir = root / "sdlc-studio" / "personas" / "seats"
                sdir.mkdir(parents=True)
                for p in cards:
                    shutil.copy(p, sdir / p.name)
                self.assertEqual(_seats(root)[1], [])

    def test_a_copy_carrying_the_old_worked_example_names_sam(self) -> None:
        """The true positive the shipped cards no longer carry: a copy of the product card whose
        Scenario still judges the story against `the Primary persona, Sam the new shopper` warns
        at the line where Sam is named in every cast holding no Sam, and draws nothing where
        Sam is a Primary. The example names Sam in full, as a lone first name outside brackets
        is no name. Mutants: a pattern that reads no worked example at all, so the shipped
        cards' clean run proves nothing."""
        old = ('A "default list for first-time users" story is proposed with five acceptance'
               ' criteria. Lena checks it\nagainst the Primary persona, Sam Patel the new shopper,'
               ' whose End goal is "add my first item in seconds."\nFour ACs serve that, and'
               ' the story is marked Ready against Sam\'s goal.\n\n')
        for cast, registry, warns in (
                ({"Maya Okafor": "Primary"}, {"Primary": ["Maya Okafor"]}, True),
                ({"Maya Okafor": "Primary"}, None, True),
                ({}, None, True),
                ({"Sam Patel": "Primary"}, {"Primary": ["Sam Patel"]}, False),
                ({"Sam Patel": "Primary"}, None, False)):
            with self.subTest(cast=sorted(cast), registry=registry is not None), \
                    tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _personas(root, cast, registry)
                sdir = root / "sdlc-studio" / "personas" / "seats"
                sdir.mkdir(parents=True)
                for p in sorted(AMIGOS.glob("*.md")):
                    shutil.copy(p, sdir / p.name)
                card = sdir / "product.md"
                text = card.read_text(encoding="utf-8")
                card.write_text(re.sub(r"(?ms)^(## Scenario\n\n).*?(?=^## )",
                                       lambda m: m.group(1) + old, text, count=1),
                                encoding="utf-8")
                rc, found = _seats(root)
                self.assertEqual(rc, 0, found)
                want = ([("seat-persona-unknown", card.name, _line_of(card, "persona, Sam"))]
                        if warns else [])
                self.assertEqual([(f["rule"], Path(f["file"]).name, f["line"]) for f in found],
                                 want, found)
                if warns:
                    self.assertIn("Sam", found[0]["message"])


class SeatClaimNameTests(unittest.TestCase):
    """A claim's name is a cast member's, or a capitalised name the cast lacks; a word that
    opens a clause, asks a question or abbreviates is no name."""

    def test_a_word_after_the_role_that_is_no_name_is_not_read_as_one(self) -> None:
        """AC1. Mutants: a stop list of the criterion's three words, so another question word
        (`Does`), another acronym (`API`) or another word opening a clause after a colon
        (`Everything`) is still read as a name; no name read at all, or none after a colon (the
        Zed Quill controls, one after a comma and one after a colon)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, {"Maya Okafor": "Primary"}, {"Primary": ["Maya Okafor"]})
            _seat(root, "product", "Lena Park", lens=(
                "- Ask the Primary persona: Is it simpler?\n"
                "- Meet the Primary persona: When they arrive, the list is ready.\n"
                "- Serve the CLI (Primary) before the web UI.\n"
                "- Ask the Primary persona, Does it hold up offline?\n"
                "- Ship the API (Primary) first.\n"
                "- Weigh the Primary persona: Everything else waits."))
            self.assertEqual(_seats(root), (0, []))
            card = _seat(root, "qa", "Sam Eriksson",
                         lens="- Would the Primary persona, Zed Quill, approve?")
            rc, found = _seats(root)
            self.assertEqual(rc, 0)
            self.assertEqual([(f["rule"], Path(f["file"]).name, f["line"]) for f in found],
                             [("seat-persona-unknown", card.name, _line_of(card, "Zed Quill"))])
            self.assertIn("Zed Quill", found[0]["message"])
            card.write_text(card.read_text(encoding="utf-8").replace(
                "Primary persona, Zed Quill,", "Primary persona: Zed Quill, then"),
                encoding="utf-8")
            self.assertEqual([(f["rule"], f["line"]) for f in _seats(root)[1]],
                             [("seat-persona-unknown", _line_of(card, "persona: Zed Quill"))])

    def test_a_first_name_with_the_wrong_surname_is_unknown(self) -> None:
        """AC2. Mutants: any first-name match passing whatever surname follows; a bare first
        name or the full name no longer resolving."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, {"Maya Okafor": "Primary"}, {"Primary": ["Maya Okafor"]})
            card = _seat(root, "product", "Lena Park",
                         lens="- Judge it as the Primary persona is Maya Smith would.")
            rc, found = _seats(root)
            self.assertEqual(rc, 0)
            self.assertEqual([(f["rule"], f["line"]) for f in found],
                             [("seat-persona-unknown", _line_of(card, "Maya Smith"))])
            self.assertIn("Maya Smith", found[0]["message"])
            for named in ("Maya", "Maya Okafor"):
                with self.subTest(named=named):
                    card.write_text(card.read_text(encoding="utf-8").replace(
                        "is Maya Smith", f"is {named}").replace("is Maya Okafor", f"is {named}"),
                        encoding="utf-8")
                    self.assertEqual(_seats(root), (0, []))

    def test_only_a_cast_name_or_a_full_name_run_is_read_as_a_name(self) -> None:
        """AC4. A run that names no cast member is a name only when it is two or more
        capitalised words, or one word alone in brackets straight after the role. Mutants: a
        rule reading every lone word (the pronoun, conjunction and `Not` lines warn); a rule
        skipping every name after a colon (Zed Quill goes silent); the bracket form dropped
        (Darren goes silent) or not held to a closing bracket (`Speed matters` warns); the
        not-name word read at the run's end (`The Admin Team` warns); the acronym guard dropped
        (`Web UI` warns) or a lone initial taken for an acronym (`Zed J Quill` goes silent);
        the bracket form read for a lone word before `(Primary)` (`the Admin (Primary)`)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, {"Maya Okafor": "Primary", "Jonah Reyes": "Primary"},
                      {"Primary": ["Maya Okafor", "Jonah Reyes"]})
            _seat(root, "product", "Lena Park", lens=(
                "- As the Primary persona, I want a quick start.\n"
                "- Lead with the Primary persona, She decides.\n"
                "- Ask the Primary persona, If pressed, what goes first?\n"
                "- Serve the Primary persona, Then the rest.\n"
                "- The Secondary persona is Not yet chosen.\n"
                "- Weigh the Primary persona (Speed matters most) first.\n"
                "- Ask the Primary persona: The Admin Team decides.\n"
                "- Serve the Web UI (Primary) before the rest.\n"
                "- Ship the Admin (Primary) view first."))
            self.assertEqual(_seats(root), (0, []))
            card = _seat(root, "qa", "Sam Eriksson", lens=(
                "- Primary persona: Zed Quill\n"
                "- Ask the Primary persona: Zed Quill would refuse this.\n"
                "- Cold on the primary persona (Darren) and his goals.\n"
                "- The Primary persona is Zed J Quill, not the rest."))
            rc, found = _seats(root)
            self.assertEqual(rc, 0, found)
            self.assertEqual([(f["rule"], f["line"]) for f in found],
                             [("seat-persona-unknown", _line_of(card, "Primary persona: Zed")),
                              ("seat-persona-unknown", _line_of(card, "Ask the Primary")),
                              ("seat-persona-unknown", _line_of(card, "(Darren)")),
                              ("seat-persona-unknown", _line_of(card, "Zed J Quill"))], found)
            for f, name in zip(found, ("Zed Quill", "Zed Quill", "Darren", "Zed J Quill")):
                self.assertIn(f"calls {name} the", f["message"])

    def test_a_card_the_registry_omits_is_role_checked_against_its_card(self) -> None:
        """AC3. Mutants: a name the registry omits skipping the role check; the omitted
        name's card role read for a name the registry does declare."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, {"Maya Okafor": "Primary", "Hana Ito": "Primary"},
                      {"Secondary": ["Maya Okafor"]})
            card = _seat(root, "ux", "Uma Reed",
                         lens="- Serve the Secondary persona, Hana, after the rest.")
            rc, found = _seats(root)
            self.assertEqual(rc, 0)
            self.assertEqual([(f["rule"], f["line"]) for f in found],
                             [("seat-persona-role", _line_of(card, "persona, Hana"))])
            for role in ("Hana Ito", "Primary", "Secondary"):
                self.assertIn(role, found[0]["message"])
            # Maya's card says Primary, but the registry, which declares her, wins.
            card.write_text(card.read_text(encoding="utf-8").replace(
                "Secondary persona, Hana", "Secondary persona, Maya"), encoding="utf-8")
            self.assertEqual(_seats(root), (0, []))
            # A cast member whose name is also a question word is read as the cast member.
            _personas(root, {"Will Ito": "Primary"}, None)
            card.write_text(card.read_text(encoding="utf-8").replace(
                "persona, Maya", "persona, Will"), encoding="utf-8")
            self.assertEqual([f["rule"] for f in _seats(root)[1]], ["seat-persona-role"])


REFERENCE = loader.SCRIPTS_DIR.parent / "reference-persona.md"


def _row_examples(cell: str) -> list[tuple[str, bool]]:
    """Each backticked example in a rule's Fires-when cell, and whether the row says it warns:
    an example in a clause (split at a semicolon or a full stop) that says `silent` stays
    silent, and any other fires, as the column's heading says."""
    spans = re.findall(r"`([^`]*)`", cell)
    numbers = iter(range(len(spans)))
    masked = re.sub(r"`[^`]*`", lambda _m: f"<{next(numbers)}>", cell)
    return [(spans[int(i)], "silent" not in clause)
            for clause in re.split(r"[;.](?:\s|$)", masked)
            for i in re.findall(r"<(\d+)>", clause)]


class ReferenceRowTests(unittest.TestCase):
    """The reference page's `seat-persona-unknown` row is where the rule is defined, so each
    example it gives is run through the check against the cast the row names."""

    def test_the_seat_persona_unknown_row_examples_behave_as_stated(self) -> None:
        """AC1. Every backticked example in the row, written alone on a seat card with Maya
        Okafor the only cast member, warns or stays silent as the row's clause says; the row
        states the three ways a run reads as a name and no longer says a word after a colon is
        no name. Mutants: an example moved into the other clause; the old row restored (its
        `the Primary persona, Sam` and `Sam (Primary)` fire nothing); a stated rule cut; the
        examples dropped from one clause."""
        row = next(ln for ln in REFERENCE.read_text(encoding="utf-8").splitlines()
                   if ln.startswith("| `seat-persona-unknown` |"))
        cell = row.strip().strip("|").split(" | ")[2]
        examples = _row_examples(cell)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, {"Maya Okafor": "Primary"}, {"Primary": ["Maya Okafor"]})
            for example, warns in examples:
                with self.subTest(example=example, row_says="warns" if warns else "silent"):
                    _seat(root, "product", "Lena Park", lens=f"- {example}")
                    found = _seats(root)[1]
                    self.assertEqual([f["rule"] for f in found],
                                     ["seat-persona-unknown"] if warns else [], found)
        stated = [warns for _, warns in examples]
        self.assertGreaterEqual(stated.count(True), 3, examples)
        self.assertGreaterEqual(stated.count(False), 3, examples)
        for rule in ("Maya Okafor the only cast member", "resolves to a cast member",
                     "two or more capitalised words",
                     "one word alone in brackets straight after the role"):
            self.assertIn(rule, cell)
        self.assertNotIn("after a colon is no name", cell)


if __name__ == "__main__":
    unittest.main()
