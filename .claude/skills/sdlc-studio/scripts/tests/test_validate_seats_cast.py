"""`validate.py seats` warns when a seat card names a persona the cast does not declare, or
declares in a different role than the card claims.

A claim is read over whitespace-joined text (a wrapped sentence counts), reported at the line
where the name starts, and judged against the registry's declared role, falling back to the
persona card's Cast role only when there is no registry. Warnings only: the seat check's errors
are the team-generation floor, and a persona claim never fails it.

Driven through `validate.main`, the shipped entry point, in throwaway trees.
"""
from __future__ import annotations

import contextlib
import io
import json
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
        """Mutants: a pattern tuned to these fixtures that misreads the shipped cards' prose,
        either way: a false warning against a cast that has Sam, or none against one that
        does not."""
        cards = sorted(AMIGOS.glob("*.md"))
        self.assertEqual([p.name for p in cards], ["engineering.md", "product.md", "qa.md"])
        for cast, registry in (({"Sam Patel": "Primary"}, {"Primary": ["Sam Patel"]}),
                               ({"Sam Patel": "Primary"}, None)):
            with self.subTest(registry=registry is not None), \
                    tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _personas(root, cast, registry)
                sdir = root / "sdlc-studio" / "personas" / "seats"
                sdir.mkdir(parents=True)
                for p in cards:
                    shutil.copy(p, sdir / p.name)
                self.assertEqual(_seats(root)[1], [])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _personas(root, {"Maya Okafor": "Primary"}, {"Primary": ["Maya Okafor"]})
            sdir = root / "sdlc-studio" / "personas" / "seats"
            sdir.mkdir(parents=True)
            for p in cards:
                shutil.copy(p, sdir / p.name)
            found = _seats(root)[1]
            product = sdir / "product.md"
            self.assertEqual([(f["rule"], Path(f["file"]).name, f["line"]) for f in found],
                             [("seat-persona-unknown", "product.md",
                               _line_of(product, "Primary persona, Sam"))], found)
            self.assertIn("Sam", found[0]["message"])


if __name__ == "__main__":
    unittest.main()
