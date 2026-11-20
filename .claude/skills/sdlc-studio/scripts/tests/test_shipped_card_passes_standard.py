"""A project that takes the shipped amigo cards passes the persona standard with them.

`project_upgrade.py --apply --with-default-amigos` copies each shipped card verbatim into the
project's `personas/seats/`. The product card's worked example judges its story against the End
goal of the Primary for the interface without naming a Primary, so no copy names a persona the
project's cast lacks, and `persona_review.py check` finds nothing on the three copies that blocks.
A worked example that named one (the Primary persona, Sam Patel the new shopper) is a true
seat-persona-unknown, which blocks, in every project whose cast holds no Sam.

Driven through each script's `main`, the shipped entry points, in throwaway projects.
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

project_upgrade = loader.load_script("project_upgrade")
persona_review = loader.load_script("persona_review")
validate = loader.load_script("validate")

AMIGOS = loader.SCRIPTS_DIR.parent / "templates" / "personas" / "amigos"
CARDS = ["engineering.md", "product.md", "qa.md"]
PERSONA_RULES = {"seat-persona-unknown", "seat-persona-role"}

#: The worked example the product card shipped before it stopped naming a cast member.
OLD_SCENARIO = (
    'A "default list for first-time users" story is proposed with five acceptance criteria. Lena'
    ' checks it\nagainst the Primary persona, Sam Patel the new shopper, whose End goal is'
    ' "add my first'
    ' item in seconds."\nFour ACs serve that; the fifth - a configurable default-list naming scheme'
    ' - serves no persona. She\ncuts it to a follow-up, sharpens AC1 to "first run lands on a usable'
    ' list with a visible add box",\nand marks the story Ready against Sam\'s goal.\n\n')

_PERSONA = ("# {name}\n\n## Quick Reference\n\n| Attribute | Value |\n| --- | --- |\n"
            "| **Cast role** | {role} |\n\n## Who They Are\n\nSomebody.\n")

#: Casts with no persona named Sam: `({name: Cast role}, {role: [names]} or None for no
#: registry)`. The empty cast is a project that has written no persona yet.
CASTS = (({"Maya Okafor": "Primary", "Trevor Hale": "Negative"},
          {"Primary": ["Maya Okafor"], "Negative": ["Trevor Hale"]}),
         ({"Maya Okafor": "Primary"}, None),
         ({}, None))


def _cast(root: Path, cards: dict[str, str], registry: dict[str, list[str]] | None) -> None:
    pdir = root / "sdlc-studio" / "personas"
    pdir.mkdir(parents=True, exist_ok=True)
    for name, role in cards.items():
        (pdir / f"{name.lower().replace(' ', '-')}.md").write_text(
            _PERSONA.format(name=name, role=role), encoding="utf-8")
    if registry is not None:
        body = ["# Persona Index", ""]
        for role, names in registry.items():
            body += [f"## {role}", ""]
            body += [f"- [{n}]({n.lower().replace(' ', '-')}.md) - somebody." for n in names]
            body += [""]
        (pdir / "index.md").write_text("\n".join(body), encoding="utf-8")


def _upgrade(root: Path) -> Path:
    """`project_upgrade.py --apply --with-default-amigos`; the seats directory it fills."""
    with contextlib.redirect_stdout(io.StringIO()):
        rc = project_upgrade.main(["--root", str(root), "--apply", "--with-default-amigos"])
    assert rc == 0, rc
    return root / "sdlc-studio" / "personas" / "seats"


def _check(root: Path) -> tuple[int, list[dict]]:
    """`persona_review.py check --format json`: the exit code and every finding."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = persona_review.main(["check", "--root", str(root), "--format", "json"])
    return rc, json.loads(out.getvalue())["findings"]


def _seats(root: Path) -> tuple[int, dict]:
    """`validate.py seats --format json`: the exit code and the whole report."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = validate.main(["seats", "--root", str(root), "--format", "json"])
    return rc, json.loads(out.getvalue())


def _section(text: str, heading: str) -> str:
    """The body under `## <heading>`, up to the next level-two heading or the end."""
    m = re.search(rf"^## {re.escape(heading)}\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def _with_old_scenario(text: str) -> str:
    """The card with its Scenario body replaced by the worked example that named Sam."""
    body = _section(text, "Scenario")
    assert body.strip(), "the card has no Scenario to replace"
    return text.replace(body, "\n" + OLD_SCENARIO, 1)


def _review_render_headings(card: Path) -> list[str]:
    """The headings a card marks `*(review render)*`, by their name alone."""
    return [m.group(1).strip() for m in re.finditer(
        r"^##+\s+(.+?)\s*\*\(review render\)\*\s*$", card.read_text(encoding="utf-8"), re.M)]


class ShippedCardStandardTests(unittest.TestCase):

    def test_an_upgraded_projects_copied_cards_trip_no_blocking_rule(self) -> None:
        """AC1. Mutants: the shipped scenario names in full a persona the cast lacks;
        a check that never reads the copies (the old-sentence control); an upgrade that copies
        some other card than the shipped one."""
        for cast, registry in CASTS:
            with self.subTest(cast=sorted(cast), registry=registry is not None), \
                    tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root / "sdlc-studio").mkdir()
                _cast(root, cast, registry)
                seats = _upgrade(root)
                self.assertEqual(sorted(p.name for p in seats.glob("*.md")), CARDS)
                for name in CARDS:
                    self.assertEqual((seats / name).read_text(encoding="utf-8"),
                                     (AMIGOS / name).read_text(encoding="utf-8"), name)
                rc, found = _check(root)
                on_seats = [f for f in found if Path(f["file"]).parent == seats.resolve()]
                blocking = [(Path(f["file"]).name, f["rule"]) for f in on_seats
                            if f["severity"] == persona_review.BLOCKS]
                self.assertEqual(blocking, [], on_seats)
                self.assertEqual(rc, 0, found)
                # Positive control: the copy carrying the old worked example is read, and its
                # naming of Sam blocks in a cast that holds no Sam.
                product = seats / "product.md"
                product.write_text(_with_old_scenario(product.read_text(encoding="utf-8")),
                                   encoding="utf-8")
                rc, found = _check(root)
                blocking = [(Path(f["file"]).name, f["rule"]) for f in found
                            if f["severity"] == persona_review.BLOCKS]
                self.assertEqual(blocking, [("product.md", "seat-persona-unknown")], found)
                self.assertIn("Sam", next(f["message"] for f in found
                                          if f["rule"] == "seat-persona-unknown"))
                self.assertEqual(rc, 1)

    def test_the_reworded_card_keeps_its_scenario_and_review_render(self) -> None:
        """AC2. Mutants: the reword drops the Scenario, or empties it, or stops judging the
        story against the Primary's End goal; it drops a review-render heading (Lens, Pushes
        Back When, Shadow, Hand-back) or unmarks one; it names Sam again."""
        shipped = AMIGOS / "product.md"
        text = shipped.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _cast(root, {"Maya Okafor": "Primary"}, {"Primary": ["Maya Okafor"]})
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir()
            shutil.copy(shipped, seats / "product.md")
            rc, report = _seats(root)
            self.assertEqual(rc, 0, report)
            self.assertEqual(report["summary"]["errors"], 0, report)
            self.assertEqual([v for v in report["violations"] if v["rule"] in PERSONA_RULES],
                             [], report)
        # The worked example is still there, and still judges the story against the End goal
        # of the Primary, naming no one.
        scenario = " ".join(_section(text, "Scenario").split())
        self.assertIn("End goal of the Primary", scenario)
        self.assertIn("add my first item in seconds", scenario)
        self.assertIn("marks the story Ready against that goal", scenario)
        self.assertNotIn("Sam", scenario)
        # Every review-render section: the floor validate holds a seat to, each with a body,
        # and each heading the sibling cards mark as the review render, marked so here too.
        for heading in validate._SEAT_REVIEW_SECTIONS:
            with self.subTest(heading=heading):
                self.assertTrue(_section(text, heading).strip(), heading)
        siblings = {h for name in ("engineering.md", "qa.md")
                    for h in _review_render_headings(AMIGOS / name)}
        self.assertEqual(siblings, {"Lens", "Hand-back"})
        self.assertEqual(set(_review_render_headings(shipped)), siblings)
        for heading in siblings:
            with self.subTest(heading=heading):
                self.assertTrue(_section(text, heading).strip(), heading)


if __name__ == "__main__":
    unittest.main()
