"""The persona standard: one table holds every rule a persona or seat card is held to, each
under one heading of `best-practices/persona.md` and marked blocks or reported, and
`persona_review.py check` reports each card against it."""
from __future__ import annotations

import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
PAGE = SKILL / "best-practices" / "persona.md"
sys.path.insert(0, str(SCRIPTS))

import persona_review  # noqa: E402
import validate  # noqa: E402

HEADINGS = ("Format", "Identity", "Evidence", "Testable goals", "Consistency with the cast",
            "Freshness", "Memory hygiene")
#: Where a rule name is minted: a finding's `"rule":` key, or a module constant naming one.
_MINTED_RE = re.compile(r'(?:"rule":\s*|^[A-Z_]+\s*=\s*)"((?:persona|seat)-[a-z-]+)"', re.M)

EVIDENCE_OK = "## Evidence\n\n- US0001: the story this card was drawn from\n"


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _persona(name: str, role: str | None, *, evidence: str | None = EVIDENCE_OK,
             goals: str = "1. Ship a change they can trust\n", drop: tuple[str, ...] = (),
             who: str = "") -> str:
    """A well-formed persona card, less the sections in `drop`."""
    rows = "| Attribute | Value |\n| --- | --- |\n"
    rows += f"| **Cast role** | {role} |\n" if role else ""
    sections = {"Who They Are": f"{name} is one specific person. {who}\n", "End Goals": goals,
                "Experience Goals": "- calm\n", "Behaviours & Context": "- at a desk\n",
                "Frustrations": "- slow reviews\n",
                "Scenario": "They open the tool and finish the job.\n"}
    body = f"# {name} - a user\n\n## Quick Reference\n\n{rows}\n"
    body += "".join(f"## {h}\n\n{t}\n" for h, t in sections.items() if h not in drop)
    return body + (evidence or "")


def _seat(role: str | None, name: str, *, extra: str = "", render: bool = True,
          evidence: str | None = EVIDENCE_OK) -> str:
    """A well-formed seat card: a role comment, the review render and an Evidence section."""
    body = (f"<!-- role: {role} -->\n" if role else "") + f"# {name} - reviewing seat\n\n"
    body += f"## Who They Are\n\n{name} reviews the work.{extra}\n\n"
    if render:
        body += "## Lens\n\n- x\n\n## Pushes Back When\n\n- x\n\n## Shadow\n\nx\n\n"
    return body + (evidence or "")


REGISTRY = ("# Persona Index\n\n## Primary\n\n- [Ada Lane](ada-lane.md) - the design target\n\n"
            "## Secondary\n\n- [Jonah Reyes](jonah-reyes.md) - a team lead\n")
STORY = "# US0001: A story on disk\n\n> **Status:** Draft\n"
DECISIONS = ("# Decisions\n\n| ID | Decision | Rationale | Status | Supersedes | Date |\n"
             "| --- | --- | --- | --- | --- | --- |\n"
             "| D0001 | a ruling | a reason | accepted | - | 2026-11-20 |\n")


def _base(root: Path) -> None:
    _write(root, "sdlc-studio/stories/US0001-a-story-on-disk.md", STORY)
    _write(root, "sdlc-studio/decisions.md", DECISIONS)


def _every_rule_fixture(root: Path) -> None:
    """A project whose cards each break one rule; the cast-level rules come from the whole."""
    _base(root)
    _write(root, "sdlc-studio/personas/index.md", REGISTRY)
    personas = {
        "ada-lane.md": _persona("Ada Lane", "Primary"),
        "jonah-reyes.md": _persona("Jonah Reyes", "Primary"),  # registry: Secondary
        "nora-quinn.md": _persona("Nora Quinn", None),
        "fay-moss.md": _persona("Fay Moss", "Secondary", drop=("Frustrations",)),
        "vic-hart.md": _persona("Vic Hart", "Secondary",
                                goals="1. Ship it\n   - **Verify:** npm test\n"),
        "sol-park.md": _persona("Sol Park", "Secondary", goals=(
            "1. Ship it\n   - **Verify:** pytest tests/test_x.py\n"
            "   - **Applies-to:** `src/**`\n")),
        "eve-ruiz.md": _persona("Eve Ruiz", "Secondary", evidence=None),
    }
    for name, text in personas.items():
        _write(root, f"sdlc-studio/personas/{name}", text)
    seats = {
        "a-wizard.md": _seat("wizard", "Wren Ash"),
        "b-roleless.md": _seat(None, "Bo Fenn"),
        "c-engineering.md": _seat("engineering", "Cal Dorn"),
        "d-engineering.md": _seat("engineering", "Dee Voss"),
        "e-security.md": _seat("security", "Eli Marsh", render=False),
        "f-sre.md": _seat("sre", "Fen Oak", extra=" She is married."),
        "g-data.md": _seat("data", "Gil Rowe") + "<!-- provenance: not a stamp -->\n",
        "h-ux.md": _seat("ux", "Hal Tor", extra=" The Primary persona is Zed Unknown."),
        "i-qa.md": _seat("qa", "Ivy Cole", extra=" Ada Lane (Secondary) is who we serve."),
    }
    for name, text in seats.items():
        _write(root, f"sdlc-studio/personas/seats/{name}", text)
    # A card the reader cannot open: a directory where a card should be.
    (root / "sdlc-studio" / "personas" / "seats" / "j-unreadable.md").mkdir()


def _run(mod, argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = mod.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _page_rules() -> dict[str, list[tuple[str, str]]]:
    """`{rule: [(heading, severity), ...]}`: every rule row on the standard page, with the
    standard heading it sits under."""
    found: dict[str, list[tuple[str, str]]] = {}
    heading = None
    for line in PAGE.read_text(encoding="utf-8").splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            heading = h.group(1) if h.group(1) in HEADINGS else None
            continue
        row = re.match(r"^\|\s*`((?:persona|seat)-[a-z-]+)`\s*\|\s*(blocks|reported)\s*\|", line)
        if row and heading:
            found.setdefault(row.group(1), []).append((heading, row.group(2)))
    return found


def _findings(root: Path, *extra: str) -> tuple[int, list[dict]]:
    rc, out, err = _run(persona_review, ["check", "--root", str(root), "--format", "json",
                                         *extra])
    return rc, json.loads(out)["findings"]


class PersonaStandardTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_every_printed_rule_is_on_the_standard_page_and_back(self) -> None:
        """AC1. Mutants: a rule added to validate.py or persona_review.py with no line on the
        page; a page line naming a rule nothing prints; a rule under two headings."""
        _every_rule_fixture(self.root)
        rc, findings = _findings(self.root)
        self.assertEqual(rc, 1)
        printed: dict[str, set[str]] = {}
        for f in findings:
            printed.setdefault(f["rule"], set()).add(f["severity"])
        page = _page_rules()
        headings = re.findall(r"^##\s+(.+?)\s*$", PAGE.read_text(encoding="utf-8"), re.M)
        self.assertLessEqual(set(HEADINGS), set(headings))
        for rule, sevs in printed.items():
            with self.subTest(printed=rule):
                self.assertEqual(1, len(page.get(rule, [])),
                                 f"{rule} is printed but sits under {page.get(rule, [])}")
                self.assertEqual({page[rule][0][1]}, sevs)
        self.assertEqual(set(page), set(printed), "a page rule no fixture card prints")
        # The table is the one source: every rule a check can mint is in it, or named as
        # outside the card standard.
        sources = [SCRIPTS / "validate.py", SCRIPTS / "persona_review.py",
                   SCRIPTS / "lib" / "persona_goals.py"]
        minted = {m for p in sources for m in _MINTED_RE.findall(p.read_text(encoding="utf-8"))}
        self.assertEqual(minted - set(persona_review.OUTSIDE), set(persona_review.RULES))
        self.assertEqual({r: [(h, s)] for r, (h, s) in persona_review.RULES.items()}, page)
        # A rule the table lacks is still printed, unclassified, so the page comparison sees it.
        with mock.patch.dict(persona_review.RULES):
            del persona_review.RULES["seat-cast-size"]
            _, findings = _findings(self.root)
        self.assertIn(("seat-cast-size", persona_review.UNCLASSIFIED, "reported"),
                      {(f["rule"], f["heading"], f["severity"]) for f in findings})

    def test_blocking_and_reported_rules_are_told_apart_from_one_table(self) -> None:
        """AC2. Mutants: every finding read as blocking (a card missing only its Evidence
        exits 1) or none; validate keeping its own idea of which rules block."""
        _base(self.root)
        seat = _write(self.root, "sdlc-studio/personas/seats/qa.md",
                      _seat("qa", "Quinn Lake", extra=" Quinn is married."))
        card = _write(self.root, "sdlc-studio/personas/eve-ruiz.md",
                      _persona("Eve Ruiz", "Primary", evidence=None))
        rc, out, _ = _run(persona_review, ["check", "--root", str(self.root),
                                           "--card", str(seat)])
        self.assertEqual(rc, 1, out)
        line = next(ln for ln in out.splitlines() if "seat-demographic-fluff" in ln)
        self.assertTrue(line.startswith("blocks "), line)
        self.assertNotIn("persona-evidence", out)  # --card reads that card alone
        rc, out, _ = _run(persona_review, ["check", "--root", str(self.root),
                                           "--card", str(card)])
        self.assertEqual(rc, 0, out)
        line = next(ln for ln in out.splitlines() if "persona-evidence" in ln)
        self.assertTrue(line.startswith("reported "), line)
        self.assertFalse([ln for ln in out.splitlines() if ln.startswith("blocks ")], out)

        def labels() -> tuple[int, dict[str, bool]]:
            rc, out, _ = _run(validate, ["seats", "--root", str(self.root)])
            rows = {m.group(1): "blocks resolve" in ln for ln in out.splitlines()
                    for m in [re.search(r"\[((?:persona|seat)-[a-z-]+)\]", ln)] if m}
            return rc, rows

        rc, rows = labels()
        self.assertEqual(rc, 1)
        self.assertEqual({"seat-demographic-fluff": True, "seat-core-missing": False}, rows)
        heading = persona_review.RULES["seat-core-missing"][0]
        flipped = {"seat-demographic-fluff": (heading, persona_review.REPORTED),
                   "seat-core-missing": (heading, persona_review.BLOCKS)}
        with mock.patch.dict(persona_review.RULES, flipped):
            rc, rows = labels()
        self.assertEqual(rc, 1, "validate keeps its own exit code")
        self.assertEqual({"seat-demographic-fluff": False, "seat-core-missing": True}, rows)

    def test_evidence_must_cite_something_that_resolves(self) -> None:
        """AC3. Mutants: the rule checks only that an Evidence heading exists; it reads ids
        anywhere on the card; a decisions row or a skill lesson does not resolve."""
        _base(self.root)
        cards = {
            "ada": _persona("Ada Lane", "Primary",
                            evidence="## Evidence\n\n- US0001 drew this card\n- D9999 ruled\n"),
            "ben": _persona("Ben Cole", "Secondary", who="US0001 is cited outside it.",
                            evidence="## Evidence\n\n- US9999, D9999 and LL9999\n"),
            "cy": _persona("Cy Dent", "Secondary", evidence="## Evidence\n\n- D0001\n"),
            "di": _persona("Di Eng", "Secondary", evidence="## Evidence\n\n- LL0001\n"),
            "ed": _persona("Ed Fox", "Secondary", evidence="## Evidence\n\n- an interview\n"),
        }
        for k, t in cards.items():
            _write(self.root, f"sdlc-studio/personas/{k}.md", t)
        _, findings = _findings(self.root)
        evidence = {Path(f["file"]).stem: f for f in findings if f["rule"] == "persona-evidence"}
        self.assertEqual({"ben", "ed"}, set(evidence))
        self.assertEqual("reported", evidence["ben"]["severity"])
        for unresolved in ("US9999", "D9999", "LL9999"):
            self.assertIn(unresolved, evidence["ben"]["message"])
        self.assertNotIn("US0001", evidence["ben"]["message"])

    def test_a_card_contradicting_the_registry_blocks(self) -> None:
        """AC4. Mutants: the Cast role compared with the other cards (persona-one-primary)
        and never with the registry."""
        _base(self.root)
        _write(self.root, "sdlc-studio/personas/index.md", REGISTRY)
        _write(self.root, "sdlc-studio/personas/ada-lane.md", _persona("Ada Lane", "Primary"))
        jonah = _write(self.root, "sdlc-studio/personas/jonah-reyes.md",
                       _persona("Jonah Reyes", "Primary"))
        rc, findings = _findings(self.root)
        self.assertEqual(rc, 1)
        hits = [f for f in findings if f["rule"] == "persona-registry-role"]
        self.assertEqual(1, len(hits), findings)
        self.assertEqual(jonah.resolve(), Path(hits[0]["file"]).resolve())
        self.assertEqual("blocks", hits[0]["severity"])
        self.assertIn("Primary", hits[0]["message"])
        self.assertIn("Secondary", hits[0]["message"])
        # Positive control: the card agreeing with the registry draws nothing that blocks.
        jonah.write_text(_persona("Jonah Reyes", "Secondary"), encoding="utf-8")
        rc, findings = _findings(self.root)
        self.assertEqual(rc, 0, findings)
        self.assertFalse([f for f in findings if f["rule"] == "persona-registry-role"])

    def test_each_shipped_amigo_card_copied_into_a_project_blocks_nothing(self) -> None:
        """Copying a shipped card into `personas/seats/` is how a project customises a seat.
        Mutants: a worked example naming a persona the copying project's cast lacks; a card
        with no Evidence section, or one citing a lesson the skill does not hold."""
        shipped = sorted((SKILL / "templates" / "personas" / "amigos").glob("*.md"))
        self.assertEqual(["engineering.md", "product.md", "qa.md"], [p.name for p in shipped])
        for card in shipped:
            with self.subTest(card=card.name), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _write(root, f"sdlc-studio/personas/seats/{card.name}",
                       card.read_text(encoding="utf-8"))
                rc, findings = _findings(root)
                self.assertEqual(0, rc, findings)
                self.assertFalse([f for f in findings if f["severity"] == "blocks"], findings)
                self.assertFalse([f for f in findings if f["rule"] == "persona-evidence"],
                                 findings)
                self.assertTrue(evidence := persona_review.evidence_ids(card.read_text(
                    encoding="utf-8")), card.name)
                for cited in evidence:  # every id, not only the one the rule needs
                    self.assertTrue(list((SKILL / "lessons").glob(f"{cited}-*.md")),
                                    f"{card.name} cites {cited}, which no skill lesson holds")


if __name__ == "__main__":
    unittest.main()
