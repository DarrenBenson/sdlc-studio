"""US0450/US0451: the PRD and the persona registry must state one design target.
US1079: with two Primaries, one per interface (D0379), each states which interface it serves.
US1080: a story minted with no persona follows the paths those Interface rows declare.
US1081: the shipped skill's Primary and the Negative state the run as it now runs.
US1083: the index's history, Last updated line and seat links; the legacy file's Role fields and
maintainer link.
US1146: the head of engineering is the shipped skill's Primary (D0436, D0443) and the
founder-engineer moves to Secondary; the team lead's card changes only in its Primary line.
US1147: the change approver joins the cast as Served (D0437), and the Negative narrows to the
wants the skill still declines (D0436, D0446).

Two failures this guards:

* The PRD's Target Users section named four generated brownfield personas and sent the
  reader to `sdlc-studio/personas.md`, while `sdlc-studio/personas/index.md` declared a
  different Primary, Secondary and Negative. Two authorities, two answers.
* `sdlc-studio/personas.md` still read as current, so a reader could design against a
  superseded set without ever learning it had been superseded.

The expected persona names are **read from the registry at check time** and never written
down here, so adding, renaming or removing a registry entry fails this file until the PRD
is updated to match. The files scanned in the second suite are **listed from the repo**,
not enumerated by hand, so a new document cannot silently exempt itself.
"""
import datetime
import functools
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
PRD = REPO / "sdlc-studio" / "prd.md"
REGISTRY = REPO / "sdlc-studio" / "personas" / "index.md"
LEGACY = REPO / "sdlc-studio" / "personas.md"

ROLES = ("Primary", "Secondary", "Served", "Negative")


def _load_gitutil():
    """The shipped git-fixture helper, loaded rather than copied (LC-020)."""
    spec = importlib.util.spec_from_file_location("_persona_coherence_gitutil",
                                                  SCRIPTS / "tests" / "gitutil.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()
LEGACY_LABEL = re.compile(r"legacy|supersede|historical|deprecat", re.I)


def read_registry(index_path: Path) -> dict[str, list[str]]:
    """Persona names per role, parsed from a registry index. Never hardcoded."""
    found: dict[str, list[str]] = {}
    role = None
    for line in index_path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"##\s+(\w+)", line)
        if heading:
            role = heading.group(1) if heading.group(1) in ROLES else None
            if role:
                found.setdefault(role, [])
            continue
        if role:
            link = re.match(r"\s*-\s+\[([^\]]+)\]\(", line)
            if link:
                found[role].append(link.group(1).strip())
    return {r: names for r, names in found.items() if names}


def target_users_section(prd_text: str) -> str:
    """The PRD's Target Users section, heading excluded."""
    match = re.search(r"^###\s+Target Users\s*$(.*?)(?=^#{2,3}\s)", prd_text,
                      re.M | re.S)
    return match.group(1) if match else ""


def personas_missing_from(section: str, registry: dict[str, list[str]]) -> list[str]:
    """Registry entries the section fails to name, as `Role: Name`."""
    return [f"{role}: {name}"
            for role, names in registry.items()
            for name in names
            if name not in section]


#: A card's `| **Interface** | ... |` Quick Reference row (D0379: one Primary per interface).
INTERFACE_ROW = re.compile(r"^\|\s*\*\*Interface\*\*\s*\|\s*(.+?)\s*\|\s*$", re.M)
#: How a card says its interface is not the shipped skill.
NOT_SHIPPED = re.compile(r"does not ship", re.I)
#: An id a card may cite as evidence: a decision or a numbered artefact.
CITED_ID = re.compile(r"\b(D\d{4}|(?:BG|US|CR|EP|RV|RFC|LL|RETRO|RPT)\d{4})\b")
#: A card's `| **Cast role** | ... |` Quick Reference row.
CAST_ROLE_ROW = re.compile(r"^\|\s*\*\*Cast role\*\*\s*\|\s*(.+?)\s*\|\s*$", re.M)


def cards_under(role: str, index_path: Path = REGISTRY) -> list[tuple[str, Path]]:
    """Each linked bullet under the index's `## <role>` heading as (name, card path), in order."""
    out, in_role = [], False
    for line in index_path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"##\s+(\w+)", line)
        if heading:
            in_role = heading.group(1) == role
            continue
        link = re.match(r"\s*-\s+\[([^\]]+)\]\(([^)]+)\)", line) if in_role else None
        if link:
            out.append((link.group(1).strip(), index_path.parent / link.group(2)))
    return out


def primary_cards(index_path: Path = REGISTRY) -> list[tuple[str, Path]]:
    """Each `## Primary` bullet as (name, card path), in index order. Never hardcoded."""
    return cards_under("Primary", index_path)


def interface_of(card: Path) -> str:
    match = INTERFACE_ROW.search(card.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else ""


def shipped_and_tooling() -> tuple[str, list[tuple[str, Path]]]:
    """The shipped skill's Primary by name, and every Primary whose interface does not ship."""
    cards = primary_cards()
    shipped = [n for n, path in cards if interface_of(path) and not NOT_SHIPPED.search(interface_of(path))]
    tooling = [(n, path) for n, path in cards if NOT_SHIPPED.search(interface_of(path))]
    return (shipped[0] if len(shipped) == 1 else ""), tooling


def card_section(text: str, heading: str) -> str:
    match = re.search(rf"^##\s+{heading}\s*$(.*?)(?=^##?\s|^---\s*$|\Z)", text, re.M | re.S)
    return match.group(1) if match else ""


def id_resolves(cited: str) -> bool:
    if re.fullmatch(r"D\d{4}", cited):
        decisions = (REPO / "sdlc-studio" / "decisions.md").read_text(encoding="utf-8")
        return f"| {cited} |" in decisions
    if cited.startswith("LL"):
        return any((SCRIPTS.parent / "lessons").glob(f"{cited}-*.md"))
    return any((REPO / "sdlc-studio").glob(f"**/{cited}-*.md"))


def first_name(name: str) -> str:
    return name.split()[0]


def flat(text: str) -> str:
    return " ".join(text.split())


#: Two cards read by file name rather than by role (US1146): US1081's End goal pins are the
#: founder-engineer's whichever cast role she holds, and the team lead's card is held to
#: GOALS_BASE. No persona name is written here: each one a check compares is read at check
#: time, from the index or from a card's own heading.
FOUNDER_CARD = REGISTRY.parent / "maya-okafor-founder-engineer.md"
TEAM_LEAD_CARD = REGISTRY.parent / "jonah-reyes-team-lead.md"
#: The change approver's card, read by the file name US1147 AC1 fixes. The name it is headed with
#: is the one that file name spells (`slug_name`), so no persona name is written here either.
CHANGE_APPROVER_CARD = REGISTRY.parent / "graham-doyle-change-approver.md"
#: The change approver's Quick Reference rows and End goals as US1147 AC1 states them (D0437).
CHANGE_APPROVER_ROWS = {
    "Cast role": "Served",
    "Role": "Chairs the change approval board in an audited organisation",
    "Context": "Approves each release from the evidence put in front of him; never runs the tool or "
               "opens a terminal",
}
CHANGE_APPROVER_END_GOALS = (
    "Approve a change from one document showing what changed, which criteria passed, who reviewed "
    "it independently, what is known to be wrong, and who is accountable",
    "Trust that the evidence came from the process, not written after the fact",
    "See fewer surprises in production over time",
)
#: The index's Served heading, the text its bullet carries after the link, and the PRD's Served
#: bullet after the name (US1147 AC3).
SERVED_HEADING = "Served (affected by the product without using it)"
SERVED_INDEX_LINE = ("chairs the change approval board; approves a release from the evidence it "
                     "carries and never runs the tool (D0437).")
SERVED_PRD_LINE = ("who chairs the change approval board and approves a release from the evidence "
                   "it carries, without running the tool.")
#: The Negative's excluded End goals, Quick Reference rows and one-line summary as US1147 AC5
#: states them (D0436, D0446).
NEGATIVE_END_GOALS = (
    "Drive delivery from a rich GUI with boards, swimlanes, and portfolio dashboards",
    "Enforce multi-stage human approval and sign-off gates on every change",
    "Have non-technical staff operate the tool",
    "Sync the work to Jira, Azure Boards or another enterprise tracker",
)
NEGATIVE_ROWS = {
    "Cast role": "Negative",
    "Role": "GUI-first delivery manager",
    "Context": "Runs delivery from a GUI work-tracker and wants non-technical staff operating the "
               "tool and a human approval on every change",
}
NEGATIVE_SUMMARY = ("a GUI-first operator wanting non-technical staff to run the tool and a human "
                    "approval on every change. A signal to decline, not a backlog.")
#: The three wants the Negative's Scenario still declines (US1147 AC7).
DECLINED_WANTS = ("a human approval on every change", "non-technical staff running the tool",
                  "sync to an enterprise tracker")
#: A clause that declines: from the verb to the colon or the end of its sentence.
DECLINING_CLAUSE = re.compile(r"\bdeclines?\b[^:.!?]*")
#: All a declining clause may hold once the declined wants are taken out of it: the verb, commas
#: and "and". Any other word offers, inverts or qualifies a want, whatever that word is: "and C
#: is offered", "and ships C", "declines none of", "declines, then accepts" (BG1318).
DECLINING_REST = re.compile(r"\Adeclines?(?:[\s,]|\band\b)*\Z")
#: A negation that inverts the verb ahead of it in its sentence: "does not decline".
NEGATION = re.compile(r"(?i)\b(?:not|never|no longer)\b|n't\b")
#: The Sprint Goal US1147 AC4 plans for the change approver.
APPROVER_GOAL = "Approve a release from one document"


def slug_name(card: Path) -> str:
    """The name a card's file name spells: `jane-roe-some-role.md` reads `Jane Roe`."""
    return " ".join(word.capitalize() for word in card.stem.split("-")[:2])


def quick_reference(text: str) -> dict[str, str]:
    """A card's Quick Reference rows as {attribute: value}, the bold stripped from each attribute."""
    return {row[0].strip("*").strip(): row[1] for row in
            table_rows(card_section(text, "Quick Reference")) if len(row) > 1}


def the_negative() -> tuple[str, Path]:
    """The one persona the index lists under `## Negative`, as (name, card path)."""
    negatives = cards_under("Negative")
    if len(negatives) != 1:
        raise AssertionError(f"the index lists {len(negatives)} Negative personas, not one")
    return negatives[0]


def card_heading(card: Path) -> str:
    """A card's `# ` heading: the person's name as the card states it."""
    match = re.search(r"^#\s+(.+?)\s*$", card.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else ""


def opening_quote(text: str) -> str:
    """The `> ` quote a card opens with, above its first section, its lines joined into one."""
    match = re.search(r"^(?:>.*(?:\n|$))+", text.split("\n## ", 1)[0], re.M)
    return flat(re.sub(r"^>\s?", "", match.group(0), flags=re.M)) if match else ""


def bullet_items(section: str) -> list[str]:
    """A section's `- ` bullets, each with its wrapped lines joined onto it."""
    items: list[str] = []
    for line in section.splitlines():
        if re.match(r"-\s+", line):
            items.append(line[1:].strip())
        elif items and line.startswith("  ") and line.strip():
            items[-1] += " " + line.strip()
    return items


class PrdTargetUsersTests(unittest.TestCase):
    """AC1/AC2 of US0450."""

    def setUp(self) -> None:
        self.registry = read_registry(REGISTRY)
        self.section = target_users_section(PRD.read_text(encoding="utf-8"))

    def test_target_users_names_every_declared_persona(self) -> None:
        self.assertTrue(self.section.strip(),
                        "the PRD has no ### Target Users section to check")
        self.assertTrue(self.registry, f"no personas parsed from {REGISTRY}")

        missing = personas_missing_from(self.section, self.registry)
        self.assertEqual(missing, [],
                         f"Target Users does not name declared persona(s): {missing}")

        for role in self.registry:
            self.assertIn(role, self.section,
                          f"Target Users does not state the {role} role")

        self.assertIn("sdlc-studio/personas/index.md", self.section,
                      "Target Users does not point at the persona registry")
        self.assertNotIn("sdlc-studio/personas.md", self.section,
                         "Target Users still designates the superseded personas.md "
                         "as the authority")

    def test_target_users_says_which_interface_each_primary_serves(self) -> None:
        """US1079 AC3, both halves. Mutants: the PRD's bold label for the tooling Primary saying
        Secondary, or losing 'does not ship'; the shipped Primary's label losing 'shipped
        skill'; the index preamble or the tooling Primary's index bullet losing 'does not ship';
        the index bullet naming paths the card's Interface row does not; a PRD outcome citing
        the tooling Primary by full or first name (D0380 rules none)."""
        shipped, tooling = shipped_and_tooling()
        self.assertTrue(shipped and tooling, "the registry declares no shipped-skill Primary "
                        "beside a tooling Primary, so there is nothing to check")
        section = flat(self.section)
        self.assertRegex(section, rf"\*\*Primary for the shipped skill[^*]*:\*\* {re.escape(shipped)}\b")
        index = REGISTRY.read_text(encoding="utf-8")
        preamble = flat(index.split("\n## ", 1)[0]).lower()
        self.assertIn("two interfaces", preamble)
        self.assertIn("does not ship", preamble)
        outcomes = re.search(r"^## Outcomes\s*$(.*?)(?=^##\s)", PRD.read_text(encoding="utf-8"),
                             re.M | re.S)
        self.assertIsNotNone(outcomes, "the PRD has no ## Outcomes section")
        for name, card in tooling:
            self.assertRegex(section, rf"\*\*Primary for [^*]*does not ship:\*\* {re.escape(name)}\b",
                             f"Target Users does not label {name} Primary for an interface that does not ship")
            bullet = re.search(rf"^- \[{re.escape(name)}\]\(.*?(?=^- \[|^## |\Z)", index, re.M | re.S)
            self.assertIsNotNone(bullet, f"the index has no bullet for {name}")
            self.assertIn("does not ship", flat(bullet.group(0)))
            for path in re.findall(r"`([^`]+/)`", interface_of(card)):
                self.assertIn(path, bullet.group(0),
                              f"the index bullet for {name} omits {path} from the card's Interface row")
            self.assertNotRegex(outcomes.group(1), rf"\b(?:{re.escape(name)}|{re.escape(first_name(name))})\b",
                                f"a PRD outcome cites {name}, whose interface does not ship (D0380)")

    def test_target_users_names_the_secondaries_in_index_order(self) -> None:
        """US1146 AC5. Mutants: the shipped-skill label naming a Secondary (the founder-engineer
        left there); the Secondary label missing a Secondary, or naming them out of the order the
        index lists them."""
        secondaries = [name for name, _ in cards_under("Secondary")]
        self.assertTrue(secondaries, "the index lists no Secondary")
        section = flat(self.section)
        label = re.search(r"\*\*Secondary \(served, never at the shipped skill's Primary's "
                          r"expense\):\*\* (.*?)(?= - \*\*|$)", section)
        self.assertIsNotNone(label, "Target Users has no Secondary bullet with its label")
        where = [label.group(1).find(name) for name in secondaries]
        self.assertNotIn(-1, where, f"the Secondary bullet omits one of {secondaries}")
        self.assertEqual(where, sorted(where), "the Secondary bullet does not follow the index's order")
        shipped = re.search(r"\*\*Primary for the shipped skill[^*]*:\*\* (.*?)(?= - \*\*|$)", section)
        self.assertIsNotNone(shipped, "Target Users has no shipped-skill Primary bullet")
        self.assertEqual([n for n in secondaries if n in shipped.group(1)], [],
                         "the shipped-skill Primary bullet names a Secondary")

    def test_the_served_change_approver_sits_between_the_secondaries_and_the_negative(self) -> None:
        """US1147 AC3. Mutants: `Served` dropped from ROLES, so the registry parse reads past the
        Served heading (this test and the derived-names fixture each fail); the index's Served
        heading moved out from between Secondary and Negative, renamed, or its bullet reworded or
        naming someone other than the card's file name spells; the PRD's Served bullet dropped while the index lists him, reworded, or not straight after
        the Secondary bullet."""
        index = REGISTRY.read_text(encoding="utf-8")
        cast = [h for h in headings(index) if h.split()[0] in ROLES]
        self.assertEqual([h.split()[0] for h in cast], ["Primary", "Secondary", "Served", "Negative"],
                         f"the index's role headings are not Primary, Secondary, Served, Negative: {cast}")
        self.assertIn(SERVED_HEADING, cast, "the index's Served heading is not the criterion's")
        served = cards_under("Served")
        self.assertEqual(self.registry.get("Served"), [n for n, _ in served] or None,
                         "the registry parse does not read the index's Served entries")
        approver = [(n, c) for n, c in served if c.resolve() == CHANGE_APPROVER_CARD.resolve()]
        self.assertEqual(len(approver), 1, "## Served does not list the change approver's card once")
        name = slug_name(approver[0][1])
        self.assertIn(f"[{name}]({CHANGE_APPROVER_CARD.name}) - {SERVED_INDEX_LINE}",
                      bullet_items(card_section(index, re.escape(SERVED_HEADING))),
                      "the index's Served bullet is not the criterion's")
        items = bullet_items(self.section)
        line = f"**{SERVED_HEADING}:** {name}, {SERVED_PRD_LINE}"
        self.assertIn(line, items, "Target Users has no Served bullet naming the change approver")
        at = items.index(line)
        self.assertTrue(at and items[at - 1].startswith("**Secondary"),
                        "Target Users does not put the Served bullet straight after the Secondary one")

    def test_expected_names_are_derived_from_the_registry_not_hardcoded(self) -> None:
        # 1. The parser reads whatever the registry says, rather than knowing an answer.
        stub = REPO / "sdlc-studio" / "personas" / "index.md"  # shape only; body below
        fabricated = (
            "# Persona Index\n\n"
            "## Primary (the design target)\n\n"
            "- [Quimby Vantablack](quimby.md) - stub\n\n"
            "## Secondary (served)\n\n"
            "- [Rowan Fitzhubbard](rowan.md) - stub\n\n"
            "## Served (affected by the product without using it)\n\n"
            "- [Odile Pemberthwaite](odile.md) - stub\n\n"
            "## Negative (not designed for)\n\n"
            "- [Sable Wintergreen](sable.md) - stub\n"
        )
        tmp = REPO / "sdlc-studio" / "personas" / ".stub-registry.md"
        try:
            tmp.write_text(fabricated, encoding="utf-8")
            parsed = read_registry(tmp)
        finally:
            tmp.unlink(missing_ok=True)
        self.assertEqual(parsed, {"Primary": ["Quimby Vantablack"],
                                  "Secondary": ["Rowan Fitzhubbard"],
                                  "Served": ["Odile Pemberthwaite"],
                                  "Negative": ["Sable Wintergreen"]},
                         "the registry parser did not return the registry's own names")
        self.assertTrue(stub.exists(), f"registry moved from {stub}")

        # 2. A registry the PRD does not match fails the check, so a rename cannot pass.
        self.assertNotEqual(
            personas_missing_from(self.section, parsed), [],
            "the check passes against a registry the PRD never mentions, so it is not "
            "reading the registry")

        # 3. No registry name is written down in this file, so nothing here can go stale.
        source = Path(__file__).read_text(encoding="utf-8")
        baked = [name for names in self.registry.values() for name in names
                 if name in source]
        self.assertEqual(baked, [],
                         f"persona name(s) hardcoded in the test: {baked}")


class TwoPrimaryCastTests(unittest.TestCase):
    """US1079 (D0379): two Primaries, one per interface, read from the registry and the cards."""

    def test_each_primary_declares_a_distinct_interface(self) -> None:
        """AC1. Mutants: either card's Interface row removed; both declaring the same interface;
        no Primary left for the shipped skill; `validate.py personas` reporting a problem."""
        cards = primary_cards()
        self.assertGreaterEqual(len(cards), 2, "fewer than two Primaries - the two-interface "
                                "cast this checks is not there")
        interfaces = {name: interface_of(path) for name, path in cards}
        self.assertEqual([n for n, i in interfaces.items() if not i], [],
                         "a Primary card declares no Interface row")
        roles = {name: (CAST_ROLE_ROW.search(path.read_text(encoding="utf-8")) or [None, ""])[1]
                 for name, path in cards}
        self.assertEqual({n: r for n, r in roles.items() if r.strip().lower() != "primary"}, {},
                         "a card the index lists under ## Primary declares another Cast role")
        self.assertEqual(len(set(interfaces.values())), len(interfaces),
                         f"two Primaries declare the same interface: {interfaces}")
        shipped, tooling = shipped_and_tooling()
        self.assertTrue(shipped, "no single Primary declares the shipped skill as its interface")
        self.assertTrue(tooling, "no Primary declares an interface that does not ship")
        run = subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), "--root", str(REPO),
                              "personas"], capture_output=True, text=True, cwd=str(REPO))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("well-formed", run.stdout, run.stdout + run.stderr)
        self.assertNotIn("Interface", run.stdout + run.stderr,
                         "validate personas warns about the Primaries' interfaces")

    def test_an_unnamed_mint_still_defaults_to_the_shipped_skills_primary(self) -> None:
        """AC2, through the shipped CLI. Mutant: the tooling Primary listed first under
        `## Primary`, which makes every unnamed mint whose Affects picks no interface his
        (US1080: here, a mint with no Affects at all)."""
        shipped, _ = shipped_and_tooling()
        self.assertTrue(shipped, "no shipped-skill Primary to expect")
        home = Path(tempfile.mkdtemp(prefix="us1079-"))
        try:
            dest = home / "sdlc-studio" / "personas"
            shutil.copytree(REGISTRY.parent, dest, ignore=shutil.ignore_patterns("seats"))
            artifact = [sys.executable, str(SCRIPTS / "artifact.py"), "--root", str(home), "new"]
            for argv in (["--type", "epic", "--title", "Fixture epic"],
                         ["--type", "story", "--epic", "EP0001", "--title", "Unnamed mint"]):
                made = subprocess.run(artifact + argv, capture_output=True, text=True)
                self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
            story = next((home / "sdlc-studio" / "stories").glob("US0001-*.md"))
            persona = re.search(r"^> \*\*Persona:\*\*\s*(.+)$", story.read_text(encoding="utf-8"),
                                re.M)
            self.assertIsNotNone(persona, "the minted story carries no Persona field")
            self.assertEqual(persona.group(1).strip(), shipped)
        finally:
            shutil.rmtree(home, ignore_errors=True)

    def test_a_mint_follows_the_live_interface_rows(self) -> None:
        """US1080 AC5: a dry-run mint with no `--persona` against this repository's own cards,
        through the shipped CLI. Mutants: the tooling row's prose read as one path, or only its
        first code span read (`.githooks/` is its second), so a hooks unit mints the shipped
        Primary; the interface default dropped, so every unit does."""
        shipped, tooling = shipped_and_tooling()
        self.assertTrue(shipped and len(tooling) == 1, "no shipped and tooling Primary pair")
        home = Path(tempfile.mkdtemp(prefix="us1080-"))
        try:
            shutil.copytree(REGISTRY.parent, home / "sdlc-studio" / "personas",
                            ignore=shutil.ignore_patterns("seats"))
            artifact = [sys.executable, str(SCRIPTS / "artifact.py"), "--root", str(home), "new"]
            made = subprocess.run(artifact + ["--type", "epic", "--title", "Fixture epic"],
                                  capture_output=True, text=True)
            self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
            for affects, want in ((".githooks/pre-commit", tooling[0][0]),
                                  (".claude/skills/sdlc-studio/scripts/artifact.py", shipped)):
                run = subprocess.run(artifact + ["--type", "story", "--epic", "EP0001",
                                                 "--title", "Unnamed mint", "--affects", affects,
                                                 "--dry-run", "--format", "json"],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertEqual(json.loads(run.stdout).get("persona"), want, affects)
            self.assertFalse((home / "sdlc-studio" / "stories").exists(), "a dry-run wrote")
        finally:
            shutil.rmtree(home, ignore_errors=True)

    def test_the_maintainer_cards_evidence_resolves_and_states_the_boundary(self) -> None:
        """AC4. Mutants: an id anywhere on the card (Evidence, Frustrations or prose) that resolves
        to nothing, lessons included; an End goal with no Evidence line; the boundary rule
        reversed (a shipped path judged against the tooling Primary, the shipped Primary's want
        met in repository-only surface) or half-removed. Whether each End goal is an outcome
        rather than machinery is AC5, a declared manual criterion: no test tells them apart."""
        shipped, tooling = shipped_and_tooling()
        self.assertTrue(shipped and tooling, "no shipped and tooling Primaries to check")
        for name, path in tooling:
            text = path.read_text(encoding="utf-8")
            goals = re.findall(r"^(\d+)\.\s", card_section(text, "End Goals"), re.M)
            self.assertTrue(goals, f"{name}'s card states no numbered End goals")
            evidence = card_section(text, "Evidence")
            self.assertTrue(evidence.strip(), f"{name}'s card has no Evidence section")
            for number in goals:
                self.assertRegex(evidence, rf"End goal {number}:",
                                 f"{name}'s End goal {number} cites no evidence")
            cited = CITED_ID.findall(text)
            self.assertTrue(cited, f"{name}'s card cites no id")
            self.assertEqual([c for c in cited if not id_resolves(c)], [],
                             f"{name}'s card cites id(s) that resolve to nothing")
            boundary = flat(card_section(text, "Boundaries"))
            judged = rf"(?:{re.escape(shipped)}|{re.escape(first_name(shipped))})"
            self.assertRegex(boundary, rf"touches a shipped path \(`\.claude/skills/sdlc-studio/`\) "
                                       rf"is judged against {judged}\.",
                             f"{name}'s card does not judge a shipped-path unit against {shipped}")
            self.assertRegex(boundary, rf"{re.escape(first_name(name))}'s want is met in "
                                       rf"repository-only surface, never by shipped surface",
                             f"{name}'s card does not keep his want to repository-only surface")

    def test_the_shipped_primary_leads_the_cast_and_the_founder_leads_the_secondaries(self) -> None:
        """US1146 AC2 and AC3. Mutants: the tooling Primary listed first under `## Primary`; the
        founder-engineer's card still declaring `Primary`, or keeping an `Interface` row, beside
        the shipped Primary; the team lead listed above her under `## Secondary`; the tooling
        Primary's index bullet sending every other unnamed mint to anyone but the shipped
        Primary; his card's opening quote naming anyone else as the shipped skill's Primary."""
        shipped, tooling = shipped_and_tooling()
        self.assertTrue(shipped and len(tooling) == 1, "no shipped and tooling Primary pair")
        self.assertEqual([n for n, _ in primary_cards()][:2], [shipped, tooling[0][0]],
                         "## Primary does not list the shipped skill's Primary first and the "
                         "tooling Primary second")
        secondaries = cards_under("Secondary")
        listed = [c.resolve() for _, c in secondaries]
        self.assertIn(FOUNDER_CARD.resolve(), listed, "## Secondary does not list the founder-engineer")
        self.assertIn(TEAM_LEAD_CARD.resolve(), listed, "## Secondary does not list the team lead")
        self.assertLess(listed.index(FOUNDER_CARD.resolve()), listed.index(TEAM_LEAD_CARD.resolve()),
                        "## Secondary lists the team lead above the founder-engineer")
        for name, card in secondaries:
            role = CAST_ROLE_ROW.search(card.read_text(encoding="utf-8"))
            self.assertEqual(role.group(1).strip() if role else "", "Secondary",
                             f"{name}'s card, listed under ## Secondary, declares another Cast role")
            self.assertEqual(interface_of(card), "", f"{name}'s card, a Secondary, declares an Interface row")
        index = REGISTRY.read_text(encoding="utf-8")
        name, card = tooling[0]
        bullet = re.search(rf"^- \[{re.escape(name)}\]\(.*?(?=^- \[|^## |\Z)", index, re.M | re.S)
        self.assertIsNotNone(bullet, f"the index has no bullet for {name}")
        self.assertIn(f"every other unnamed mint names {first_name(shipped)}.", flat(bullet.group(0)),
                      f"{name}'s index bullet does not send every other unnamed mint to {shipped}")
        self.assertIn(f"{shipped} is Primary for the shipped skill",
                      opening_quote(card.read_text(encoding="utf-8")),
                      f"{name}'s card does not open by naming {shipped} as the shipped skill's Primary")

    def test_jonahs_cast_lines_name_the_declared_primary_and_nothing_else_changes(self) -> None:
        """US1146 AC7 (D0446: the product seat's dissent). Mutants: the team lead's `- **Primary:**`
        line still pointing at the founder-engineer's card, or naming her; his served or
        ceremony clause naming anyone but the shipped Primary; any other line of his card
        changed from GOALS_BASE, End goals included, so O6-O9 keep their citations."""
        shipped, _ = shipped_and_tooling()
        self.assertTrue(shipped, "no shipped-skill Primary to expect")
        primary_card = dict(primary_cards())[shipped]
        base = committed_text(GOALS_BASE, TEAM_LEAD_CARD).splitlines()
        now = TEAM_LEAD_CARD.read_text(encoding="utf-8").splitlines()
        self.assertEqual(end_goal_items("\n".join(now)), end_goal_items("\n".join(base)),
                         f"the team lead's End goals differ from {GOALS_BASE}")
        cast = [i for i, line in enumerate(now) if line.startswith("- **Primary:**")]
        was = [i for i, line in enumerate(base) if line.startswith("- **Primary:**")]
        self.assertEqual((len(cast), len(was)), (1, 1), "not one `- **Primary:**` line before and after")
        self.assertEqual(now[:cast[0]] + now[cast[0] + 1:], base[:was[0]] + base[was[0] + 1:],
                         f"a line of the team lead's card other than its Primary line differs "
                         f"from {GOALS_BASE}")
        line, lead, primary = now[cast[0]], first_name(card_heading(TEAM_LEAD_CARD)), first_name(shipped)
        self.assertEqual([s for s in CODE_SPAN.findall(line) if s.endswith(".md")], [primary_card.name],
                         "the Primary line does not point at the shipped Primary's card alone")
        self.assertIn(shipped, line, f"the Primary line does not name {shipped}")
        self.assertIn(f"{lead} is served, but never at {primary}'s expense", line)
        self.assertIn(f"a feature that helps {lead} by adding ceremony for {primary} is declined", line)
        others = [card_heading(c) for _, c in cards_under("Primary") + cards_under("Secondary")
                  if c.resolve() not in (primary_card.resolve(), TEAM_LEAD_CARD.resolve())]
        self.assertEqual([n for n in others if first_name(n) in line], [],
                         "the Primary line names another persona")


#: The commit the founder-engineer's End goals 1 to 4 are held to, word for word (US1081 AC1),
#: and the team lead's whole card but its Primary line (US1146 AC7).
GOALS_BASE = "7f3e91a9"
#: End goal 5 as US1081 AC1 states it (D0383), so the test holds the criterion's words.
END_GOAL_5 = ("Keep the process small enough to serve the work - every check earns its keep, "
              "and one that catches nothing is retired")
#: The opening quote of the founder-engineer's card once she is Secondary (US1146 AC4).
FOUNDER_QUOTE = ("A specific person, not a type. The Secondary is served fully, but never at the "
                 "Primary's expense.")
#: The shipped Primary's six End goals as US1146 AC1 states them (D0436, D0443), in order, each
#: held word for word as END_GOAL_5 holds the founder-engineer's fifth.
SHIPPED_PRIMARY_END_GOALS = (
    "Every release passes the change board on the evidence the run produced, with no separate "
    "write-up",
    "Every specification and every change names an accountable person, not 'the agent'",
    "Know what each team's delivery costs per point and hold it to a monthly budget, whichever "
    "harness a team uses",
    "A defect that escapes to production is traced to where it got through, and the mistake is "
    "not repeated",
    "People who never open a terminal can follow progress without someone translating for them",
    "The process stays small enough to serve the work; every step earns its place",
)
#: The shipped Primary's Quick Reference rows as US1146 AC1 states them.
SHIPPED_PRIMARY_ROWS = {
    "Cast role": "Primary",
    "Role": "Head of engineering in an audited organisation",
    "Context": "Leads several three-person teams (product owner, engineer, QA) directing agents the "
               "organisation already licenses; every release passes a change approval board",
}
#: The ids each of the shipped Primary's `End goal N:` Evidence lines cites, and no others, with
#: the phrase a line carries beside its RFC0063 workstream (US1146 AC1).
SHIPPED_PRIMARY_EVIDENCE = {
    "1": ({"D0436", "EP0275", "EP0276"}, ""),
    "2": ({"D0436", "RFC0063"}, "RFC0063 WS2, the owner field"),
    "3": ({"D0436", "CR0685", "CR0690"}, ""),
    "4": ({"D0436", "RFC0061", "RFC0063"}, "RFC0063 WS6, the escape loop"),
    "5": ({"D0436", "D0441"}, ""),
    "6": ({"D0443"}, ""),
}
#: The ids the card's own closing Evidence line cites.
SHIPPED_PRIMARY_CARD_EVIDENCE = {"D0436", "D0443", "RFC0063"}
#: The sprint run the shipped Primary's Scenario has one of her teams make (US1146 AC4).
SHIPPED_PRIMARY_RUN = "/sdlc-studio sprint --crs Proposed --goal done"
CODE_SPAN = re.compile(r"`([^`\n]+)`")
#: A `script.py verb` span: an optional `python3` and directory, the script, then a word that is
#: not a flag.
SCRIPT_VERB = re.compile(r"^(?:python3\s+)?(?:\S*/)?([\w-]+\.py)\s+([^\s-]\S*)")
#: A skill command span such as `/sdlc-studio gate`.
SKILL_COMMAND = re.compile(r"^/sdlc-studio\s+([a-z][\w-]*)")
#: A sprint run: the skill's `sprint` command with flags only, so `sprint plan` is not one.
SPRINT_RUN = re.compile(r"^/sdlc-studio\s+sprint(?:\s+--|$)")
SIGN_SPAN = re.compile(r"^sprint\.py\s+sign(?:\s|$)")


def end_goal_items(text: str, heading: str = "End Goals") -> dict[str, list[str]]:
    """A card's End goals by number, each as the lines it is written on. `heading` is a pattern,
    so a Negative card's `End Goals (stated to exclude)` is read by passing it escaped (US1147)."""
    items: dict[str, list[str]] = {}
    current = None
    for line in card_section(text, heading).splitlines():
        numbered = re.match(r"^(\d+)\.\s+(.*\S)\s*$", line)
        if numbered:
            current = items.setdefault(numbered.group(1), [])
            current.append(numbered.group(2))
        elif current is not None and line.strip():
            current.append(line.strip())
        else:
            current = None
    return items


def committed_text(commit: str, path: Path) -> str:
    run = subprocess.run(["git", "show", f"{commit}:{path.relative_to(REPO).as_posix()}"],
                         cwd=str(REPO), capture_output=True, text=True, env=gitutil.git_env())
    if run.returncode:
        raise AssertionError(f"cannot read {path.name} at {commit}: {run.stderr.strip()}")
    return run.stdout


@functools.lru_cache(maxsize=None)
def verb_accepted(script: str, verb: str) -> bool:
    """Does the shipped script take `verb` as a subcommand? Asked of its own `--help`."""
    if not (SCRIPTS / script).is_file():
        return False
    run = subprocess.run([sys.executable, str(SCRIPTS / script), verb, "--help"],
                         capture_output=True, text=True, cwd=str(REPO))
    return run.returncode == 0 and run.stdout.startswith(f"usage: {script} {verb}")


def interface_paths(card: Path) -> list[str]:
    """The paths a card's Interface row declares: its code spans holding no whitespace."""
    return re.findall(r"`([^`\s]+)`", interface_of(card))


def names_path(span: str, path: str) -> bool:
    """Does a code span name `path`, at a path boundary rather than inside another path?"""
    bare = path.removeprefix("./").rstrip("/")
    span = re.sub(r"(?:^|(?<=\s))\./", "", span)
    return re.search(rf"(?<![\w./-]){re.escape(bare)}(?![\w.-])", span) is not None


def interface_name(card: Path) -> str:
    """A card's interface as its Interface row names it: the row's text before its first colon."""
    return interface_of(card).split(":", 1)[0].strip()


#: A markdown table's separator row.
TABLE_RULE = re.compile(r"\|(?:\s*:?-+:?\s*\|)+")


def table_rows(section: str) -> list[list[str]]:
    """The body rows of the markdown tables in a section, each as its cells: no header, no rule."""
    lines = [line.strip() for line in section.splitlines()] + [""]
    return [[cell.strip() for cell in line.strip("|").split("|")]
            for line, below in zip(lines, lines[1:])
            if line.startswith("|") and not TABLE_RULE.fullmatch(line)
            and not TABLE_RULE.fullmatch(below)]


def links_from(card: Path, text: str) -> set[Path]:
    return {(card.parent / href.split("#", 1)[0]).resolve()
            for href in re.findall(r"\]\(([^)\s]+)\)", text)}


class CardsStateTheRunTests(unittest.TestCase):
    """US1081: the shipped skill's Primary and the Negative state the run as it now runs."""

    def setUp(self) -> None:
        self.shipped, self.tooling = shipped_and_tooling()
        self.assertTrue(self.shipped and self.tooling, "no shipped and tooling Primaries")
        self.card = dict(primary_cards())[self.shipped]
        self.text = self.card.read_text(encoding="utf-8")
        # US1146: the founder-engineer's card and the shipped Primary's, each checked once.
        self.both = list(dict.fromkeys([FOUNDER_CARD.resolve(), self.card.resolve()]))

    def test_mayas_end_goals_keep_their_numbers_and_gain_the_fifth(self) -> None:
        """US1081 AC1, read from the founder-engineer's card by file name (US1146). Mutants: End
        goal 1 to 4 reworded or renumbered; End goal 5 missing, reworded or wrapped onto a second
        line, which BG1107 truncates; her opening quote still calling her the Primary (US1146
        AC4)."""
        text = FOUNDER_CARD.read_text(encoding="utf-8")
        base = end_goal_items(committed_text(GOALS_BASE, FOUNDER_CARD))
        self.assertEqual(sorted(base), ["1", "2", "3", "4"], f"the {GOALS_BASE} baseline moved")
        now = end_goal_items(text)
        self.assertEqual({n: now.get(n) for n in base}, base,
                         f"End goals 1 to 4 differ from {GOALS_BASE}")
        self.assertEqual(now.get("5"), [END_GOAL_5], "End goal 5 is not the criterion's one line")
        self.assertEqual(opening_quote(text), FOUNDER_QUOTE,
                         "the founder-engineer's card does not open with the Secondary's quote")

    def test_the_shipped_primarys_six_end_goals_stand_with_evidence(self) -> None:
        """US1146 AC1. Mutants: an End goal reworded, reordered, wrapped onto a second line or
        missing; an End goal with no `End goal N:` Evidence line, or one citing other ids; the
        card's own closing Evidence line gone; any id on the card that resolves to nothing; a
        Quick Reference row reworded; the heading not the name the index gives."""
        self.assertEqual(card_heading(self.card), self.shipped,
                         "the card's heading is not the name the index lists")
        rows = {row[0].strip("*").strip(): row[1] for row in
                table_rows(card_section(self.text, "Quick Reference")) if len(row) > 1}
        self.assertEqual({k: rows.get(k) for k in SHIPPED_PRIMARY_ROWS}, SHIPPED_PRIMARY_ROWS,
                         "a Quick Reference row is not the criterion's")
        self.assertEqual(end_goal_items(self.text),
                         {str(n): [goal] for n, goal in enumerate(SHIPPED_PRIMARY_END_GOALS, 1)},
                         "the End goals are not the criterion's six, in order, one line each")
        items = bullet_items(card_section(self.text, "Evidence"))
        lines = {m.group(1): item for item in items if (m := re.match(r"End goal (\d+):", item))}
        self.assertEqual(sorted(lines, key=int), sorted(SHIPPED_PRIMARY_EVIDENCE, key=int),
                         "not one `End goal N:` Evidence line per End goal")
        for number, (ids, phrase) in SHIPPED_PRIMARY_EVIDENCE.items():
            self.assertEqual(set(CITED_ID.findall(lines[number])), ids,
                             f"End goal {number}'s Evidence line cites other ids")
            self.assertIn(phrase, lines[number], f"End goal {number}'s Evidence line omits {phrase!r}")
        itself = [item for item in items if item.startswith("The card itself:")]
        self.assertEqual(len(itself), 1, "the Evidence section has no one line for the card itself")
        self.assertEqual(set(CITED_ID.findall(itself[0])), SHIPPED_PRIMARY_CARD_EVIDENCE,
                         "the card's own Evidence line cites other ids")
        cited = CITED_ID.findall(self.text)
        self.assertEqual([c for c in cited if not id_resolves(c)], [],
                         "the card cites id(s) that resolve to nothing")

    def test_mayas_card_names_shipped_commands_and_the_sign_step(self) -> None:
        """AC2, each `script.py verb` span asked of that script's own `--help`. Mutants: a span
        naming a verb the script does not take (`sprint.py sigh`) or a script that does not ship;
        a span naming a path in the tooling Primary's Interface row (`.githooks/pre-push`); the
        Scenario naming no `sprint` run (an autosprint), or naming `sprint.py sign` before it.
        US1146 AC4: checked on the founder-engineer's card and the shipped Primary's; the shipped
        Primary's Scenario runs SHIPPED_PRIMARY_RUN, then signs, then passes the change approval
        board with no separate write-up, in that order."""
        paths = [p for _, card in self.tooling for p in interface_paths(card)]
        self.assertTrue(paths, "the tooling Primary's Interface row declares no path")
        for card in self.both:
            text = card.read_text(encoding="utf-8")
            spans = CODE_SPAN.findall(text)
            verbs = [m.groups() for m in map(SCRIPT_VERB.match, spans) if m]
            self.assertTrue(verbs, f"{card.name} names no `script.py verb` span")
            self.assertEqual([f"{s} {v}" for s, v in verbs if not verb_accepted(s, v)], [],
                             f"a span on {card.name} names a verb the shipped scripts do not accept")
            commands = [m.group(1) for m in map(SKILL_COMMAND.match, spans) if m]
            self.assertEqual([c for c in commands
                              if not (SCRIPTS.parent / "help" / f"{c}.md").is_file()], [],
                             f"a span on {card.name} names a skill command with no help file")
            self.assertEqual([s for s in spans if any(names_path(s, p) for p in paths)], [],
                             f"a span on {card.name} names a path in the tooling Primary's interface")
            scenario = CODE_SPAN.findall(card_section(text, "Scenario"))
            runs = [i for i, s in enumerate(scenario) if SPRINT_RUN.match(s)]
            signs = [i for i, s in enumerate(scenario) if SIGN_SPAN.match(s)]
            self.assertTrue(runs, f"{card.name}'s Scenario names no `sprint` run: {scenario}")
            self.assertTrue(signs, f"{card.name}'s Scenario names no `sprint.py sign`: {scenario}")
            self.assertLess(runs[0], signs[0], f"{card.name}'s Scenario signs before it runs the sprint")
        scenario = flat(card_section(self.text, "Scenario"))
        run = scenario.find(f"`{SHIPPED_PRIMARY_RUN}`")
        sign = scenario.find("`sprint.py sign`", max(run, 0))
        board = scenario.find("change approval board", max(sign, 0))
        self.assertGreaterEqual(run, 0, f"the shipped Primary's Scenario never runs {SHIPPED_PRIMARY_RUN}")
        self.assertGreater(sign, run, "the shipped Primary's Scenario does not sign after the sprint runs")
        self.assertGreater(board, sign, "the release does not pass the change approval board after the "
                                        "signature")
        self.assertIn("no separate write-up", scenario[board:],
                      "the board's approval is not on the signed report's evidence alone")

    def test_mayas_boundaries_table_the_primary_for_each_interface(self) -> None:
        """AC3, with the mixed row also asked of the shipped mint. Mutants: no link to another
        Primary's card; the mixed row naming the tooling Primary (the rule reversed); an
        interface cell that is not the name the card's Interface row gives; the index listing
        the tooling Primary first, which moves both the reading and the mint.
        US1146 AC4: checked on the founder-engineer's card and the shipped Primary's, so neither
        table names the founder-engineer for the shipped skill or for both."""
        cards = primary_cards()
        mixed = []
        for card in self.both:
            boundary = card_section(card.read_text(encoding="utf-8"), "Boundaries")
            self.assertTrue(boundary.strip(), f"{card.name} has no Boundaries section")
            links = links_from(card, boundary)
            self.assertEqual([n for n, c in cards if c.resolve() != card.resolve()
                              and c.resolve() not in links], [],
                             f"{card.name}'s Boundaries does not link every other Primary's card")
            rows = table_rows(boundary)
            expected = [[interface_name(c), n] for n, c in cards]
            self.assertEqual([e for e in expected if e not in rows], [],
                             f"no row on {card.name} maps each interface to its Primary: {rows}")
            both = [r for r in rows if r not in expected]
            self.assertEqual(len(both), 1, f"want one row for a unit touching both: {rows}")
            self.assertRegex(both[0][0], r"(?i)\bboth\b")
            self.assertEqual(both[0][1:], [cards[0][0]],
                             f"on {card.name}, a unit touching both is not the Primary the index "
                             f"lists first")
            mixed = both
        home = Path(tempfile.mkdtemp(prefix="us1081-"))
        try:
            shutil.copytree(REGISTRY.parent, home / "sdlc-studio" / "personas",
                            ignore=shutil.ignore_patterns("seats"))
            artifact = [sys.executable, str(SCRIPTS / "artifact.py"), "--root", str(home), "new"]
            made = subprocess.run(artifact + ["--type", "epic", "--title", "Fixture epic"],
                                  capture_output=True, text=True)
            self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
            affects = ",".join(f"{interface_paths(c)[0].rstrip('/')}/probe.md" for _, c in cards)
            run = subprocess.run(artifact + ["--type", "story", "--epic", "EP0001", "--title",
                                             "Mixed unit", "--affects", affects, "--dry-run",
                                             "--format", "json"], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual(json.loads(run.stdout).get("persona"), mixed[0][1], affects)
        finally:
            shutil.rmtree(home, ignore_errors=True)

    def test_trevors_card_names_the_one_signature_and_each_primary(self) -> None:
        """AC4. Mutants: the card left without the `sprint.py sign` span or without D0213; an id
        it cites that resolves to nothing; a Primary's card not linked from its Boundaries, or the
        shipped skill's Primary not named there by a link to her card (US1146 AC4)."""
        negatives = cards_under("Negative")
        self.assertTrue(negatives, "the index lists no Negative persona")
        for name, card in negatives:
            text = card.read_text(encoding="utf-8")
            self.assertTrue([s for s in CODE_SPAN.findall(text) if SIGN_SPAN.match(s)],
                            f"{name}'s card names no `sprint.py sign`")
            self.assertTrue(verb_accepted("sprint.py", "sign"))
            cited = CITED_ID.findall(text)
            self.assertIn("D0213", cited, f"{name}'s card does not cite D0213")
            self.assertEqual([c for c in cited if not id_resolves(c)], [],
                             f"{name}'s card cites id(s) that resolve to nothing")
            boundary = card_section(text, "Boundaries")
            links = links_from(card, boundary)
            self.assertEqual([n for n, c in primary_cards() if c.resolve() not in links], [],
                             f"{name}'s Boundaries does not link each Primary's card")
            self.assertIn(f"[{self.shipped}]({self.card.name})", boundary,
                          f"{name}'s Boundaries does not name {self.shipped} as the shipped "
                          f"skill's Primary")


class ServedAndNegativeTests(unittest.TestCase):
    """US1147: the change approver is Served (D0437), and the Negative wants only what the skill
    still declines (D0436, D0446)."""

    def test_the_change_approvers_card_states_the_three_ruled_end_goals(self) -> None:
        """AC1. Mutants: an End goal reworded, reordered, wrapped onto a second line or missing; a
        Cast role other than Served; an Interface row; a Quick Reference row reworded; the heading
        not the name the card's file name spells."""
        self.assertTrue(CHANGE_APPROVER_CARD.is_file(), f"no card at {CHANGE_APPROVER_CARD.name}")
        text = CHANGE_APPROVER_CARD.read_text(encoding="utf-8")
        self.assertEqual(card_heading(CHANGE_APPROVER_CARD), slug_name(CHANGE_APPROVER_CARD),
                         "the card is not headed with the name its file name spells")
        rows = quick_reference(text)
        self.assertEqual({k: rows.get(k) for k in CHANGE_APPROVER_ROWS}, CHANGE_APPROVER_ROWS,
                         "a Quick Reference row is not the criterion's")
        self.assertNotIn("Interface", rows, "the change approver's card carries an Interface row")
        self.assertEqual(interface_of(CHANGE_APPROVER_CARD), "",
                         "the change approver's card carries an Interface row")
        self.assertEqual(end_goal_items(text),
                         {str(n): [goal] for n, goal in enumerate(CHANGE_APPROVER_END_GOALS, 1)},
                         "the End goals are not the criterion's three, in order, one line each")

    def test_a_goal_serving_the_change_approver_is_not_flagged(self) -> None:
        """AC4, through the shipped `sprint.py plan` on copies of the PRD and the cards. Mutants:
        the change approver's card missing, headed with another name, or its Cast role not Served;
        the Negative control not printing NONE. The name served is the one the card's file name
        spells, so the CLI, not a read of the card, says whether the card is there."""
        approver, negative = slug_name(CHANGE_APPROVER_CARD), the_negative()[0]
        home = Path(tempfile.mkdtemp(prefix="us1147-"))
        try:
            root = home / "root"
            (root / "sdlc-studio").mkdir(parents=True)
            shutil.copy2(PRD, root / "sdlc-studio" / "prd.md")
            shutil.copytree(REGISTRY.parent, root / "sdlc-studio" / "personas")
            env = gitutil.git_env(HOME=str(home), XDG_DATA_HOME=str(home / ".local" / "share"),
                                  CLAUDE_CONFIG_DIR=str(home / ".claude"))

            def plan(serves: str) -> tuple[list[str], str]:
                run = subprocess.run([sys.executable, str(SCRIPTS / "sprint.py"), "plan", "--root",
                                      str(root), "--stories", "Ready", "--sprint-goal", APPROVER_GOAL,
                                      "--serves", serves, "--no-fetch"],
                                     capture_output=True, text=True, cwd=str(root), env=env)
                said = run.stdout + run.stderr
                return [ln for ln in said.splitlines() if ln.startswith("goal serves:")], said

            lines, said = plan(approver)
            self.assertIn(f"goal serves: {approver} (Served)", lines, said)
            self.assertEqual([ln for ln in lines if ln.startswith("goal serves: NONE")], [], said)
            lines, said = plan(negative)
            self.assertTrue([ln for ln in lines if ln.startswith("goal serves: NONE")],
                            f"a goal serving only {negative} is not flagged NONE:\n{said}")
        finally:
            shutil.rmtree(home, ignore_errors=True)

    def test_trevor_is_narrowed_to_the_three_wants_the_skill_declines(self) -> None:
        """AC5. Mutants: a fifth excluded End goal left (the corporate stack, or governing many
        teams centrally); tracker sync missing; a Quick Reference row not the criterion's; the
        Why-not naming the founder-engineer, or not the shipped Primary, or not saying audit
        evidence and the running of several teams are served through her (D0436); the index's or
        the PRD's line still saying central governance; D0213, `sprint.py sign` or a Primary's
        link gone."""
        name, card = the_negative()
        text = card.read_text(encoding="utf-8")
        self.assertEqual(end_goal_items(text, r"End Goals \(stated to exclude\)"),
                         {str(n): [goal] for n, goal in enumerate(NEGATIVE_END_GOALS, 1)},
                         "the excluded End goals are not the criterion's four, in order")
        rows = quick_reference(text)
        self.assertEqual({k: rows.get(k) for k in NEGATIVE_ROWS}, NEGATIVE_ROWS,
                         "a Quick Reference row is not the criterion's")
        shipped, _ = shipped_and_tooling()
        founder = card_heading(FOUNDER_CARD)
        why = flat(card_section(text, "Why We Are Not Designing For Him"))
        self.assertIn(shipped, why, f"the Why-not does not name {shipped} as the Primary it would cost")
        self.assertNotRegex(why, rf"\b(?:{re.escape(founder)}|{re.escape(first_name(founder))})\b",
                            f"the Why-not still names {founder}")
        self.assertRegex(why, r"[Aa]udit evidence and the running of several teams are served "
                              r"through her \(D0436\)")
        index = REGISTRY.read_text(encoding="utf-8")
        negative_heading = next(h for h in headings(index) if h.split()[0] == "Negative")
        self.assertIn(f"[{name}]({card.name}) - {NEGATIVE_SUMMARY} Well-formed.",
                      bullet_items(card_section(index, re.escape(negative_heading))),
                      "the index's Negative bullet is not the criterion's")
        self.assertIn(f"**Negative (deliberately not designed for):** {name}, {NEGATIVE_SUMMARY}",
                      bullet_items(target_users_section(PRD.read_text(encoding="utf-8"))),
                      "the PRD's Negative bullet is not the criterion's")
        self.assertIn("D0213", CITED_ID.findall(text), "the card no longer cites D0213")
        self.assertTrue([s for s in CODE_SPAN.findall(text) if SIGN_SPAN.match(s)],
                        "the card no longer names `sprint.py sign`")
        links = links_from(card, card_section(text, "Boundaries"))
        self.assertEqual([n for n, c in primary_cards() if c.resolve() not in links], [],
                         "the Boundaries no longer link each Primary's card")

    def test_trevors_scenario_points_boards_and_dashboards_at_the_read_only_companion_dashboard(
            self) -> None:
        """AC7. Mutants: the Scenario still naming an enterprise tool; the companion dashboard
        named as anything but read-only, or not over the committed record; one of the three
        declined wants dropped, named anywhere outside a clause that declines it ("offers A and
        declines B and C"), declined under a negation ("does not decline"), or put on the
        companion dashboard; a declining clause holding any word besides its verb, the three
        wants, commas and "and", so a want offered inside it fails whatever the offering word
        ("but offers C", "and C is offered", "and ships C", "declines none of A, B and C",
        "declines, then accepts, A, B and C"). The wants are matched in the criterion's own
        wording, so a want offered in other words ("It offers him Jira sync.") is not caught."""
        name, card = the_negative()
        scenario = flat(card_section(card.read_text(encoding="utf-8"), "Scenario"))
        self.assertTrue(scenario, f"{name}'s card has no Scenario")
        self.assertNotRegex(scenario, r"(?i)enterprise tool", "the Scenario still names an enterprise tool")
        before = re.findall(r"(\S+) companion dashboard", scenario)
        self.assertTrue(before, "the Scenario names no companion dashboard")
        self.assertEqual([w for w in before if w != "read-only"], [],
                         "the Scenario names the companion dashboard as something other than read-only")
        sentences = re.split(r"(?<=[.!?])\s+", scenario)
        pointed = [s for s in sentences if "read-only companion dashboard over the committed record" in s]
        self.assertTrue([s for s in pointed if "boards and dashboards" in s and "RFC0063 D6" in s],
                        "no sentence points his boards and dashboards at the read-only companion "
                        "dashboard over the committed record (RFC0063 D6)")
        clauses = list(DECLINING_CLAUSE.finditer(scenario))
        self.assertTrue(clauses, "the Scenario has no clause that declines his wants")
        for clause in clauses:
            lead = re.split(r"[.!?:]", scenario[:clause.start()])[-1]
            self.assertNotRegex(lead, NEGATION, f"a negation inverts the clause: {lead}{clause[0]}")
            rest = clause[0]
            for want in DECLINED_WANTS:
                rest = rest.replace(want, "")
            self.assertRegex(rest, DECLINING_REST,
                             f"the declining clause holds more than its verb and the wants: {clause[0]}")
        outside = DECLINING_CLAUSE.sub(" | ", scenario)
        for want in DECLINED_WANTS:
            self.assertTrue([c for c in clauses if want in c[0]], f"the Scenario does not decline {want}")
            self.assertNotIn(want, outside, f"the Scenario names {want} outside the clause declining it")
            self.assertEqual([s for s in sentences if want in s and "companion dashboard" in s], [],
                             f"a sentence puts {want} on the companion dashboard")


#: The seats `persona_resolve.py resolve --seat` takes, each named by US1083 AC3.
SEATS = ("engineering", "product", "qa")
#: A `Last updated` line, bold or plain: `**Last updated:** 2026-11-01`.
LAST_UPDATED = re.compile(r"^(?:\*\*)?Last updated:(?:\*\*)?\s*(\S+)\s*$", re.M | re.I)
#: A legacy persona section's `**Role:**` field.
ROLE_FIELD = re.compile(r"^\*\*Role:\*\*\s*(.+)$", re.M)
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def persona_registry(root: Path):
    """What the shipped registry reader, `sdlc_md.persona_registry`, reads under `root`."""
    lib = str(SCRIPTS / "lib")
    if lib not in sys.path:
        sys.path.insert(0, lib)
    import sdlc_md  # noqa: PLC0415 - deferred: only the tests that read the registry import it
    return sdlc_md.persona_registry(root)


def headings(text: str) -> list[str]:
    """Each `## ` heading's text, in order."""
    return re.findall(r"^##\s+(.+?)\s*$", text, re.M)


def history_dates(text: str) -> list[str]:
    """The Date cell of each Revision History row, in the order written."""
    return [row[0] for row in table_rows(card_section(text, "Revision History"))]


def role_vocabulary() -> set[str]:
    """The roles the shipped reader takes from the index's role headings, lower-cased."""
    return {entry.role for entry in persona_registry(REPO).entries}


def registry_entries(root: Path) -> list[tuple]:
    """Each persona the reader returns under `root`, as (name, role, card file name)."""
    return [(e.name, e.role, e.card and Path(e.card).name) for e in persona_registry(root).entries]


def names_a_role(text: str, roles: set[str]) -> bool:
    """Does the text name a role as a word, in any case?"""
    return any(re.search(rf"\b{re.escape(role)}\b", text, re.I) for role in roles)


def is_role_heading(heading: str, roles: set[str]) -> bool:
    """Does a heading open with a role word, as the reader's role headings do?"""
    return any(re.match(rf"{re.escape(role)}\b", heading, re.I) for role in roles)


class RegistryRecordTests(unittest.TestCase):
    """US1083: the index's history is complete and ordered, it links the seat cards in force, and
    the legacy personas.md agrees with its banner."""

    def setUp(self) -> None:
        self.text = REGISTRY.read_text(encoding="utf-8")

    def test_the_index_history_is_ordered_and_complete(self) -> None:
        """AC1. Mutants: a history row moved out of date order; the 2026-07-29 row (cec10acc,
        BG0307) dropped, or the row for any other date a commit to the index carries."""
        dates = history_dates(self.text)
        self.assertTrue(dates, "the index has no Revision History rows")
        self.assertEqual([d for d in dates if not ISO_DATE.fullmatch(d)], [],
                         "a history date is not YYYY-MM-DD, so string order is not date order")
        self.assertEqual(dates, sorted(dates), "the index's Revision History is not in date order")
        log = subprocess.run(["git", "log", "--date=short", "--format=%ad", "--",
                              REGISTRY.relative_to(REPO).as_posix()],
                             cwd=str(REPO), capture_output=True, text=True, check=True)
        committed = set(log.stdout.split())
        self.assertTrue(committed, "git log names no commit to the index: is this a shallow clone?")
        self.assertEqual(sorted(committed - set(dates)), [],
                         "a commit to the index carries a date its Revision History has no row for")

    def test_the_index_carries_its_last_updated_date(self) -> None:
        """AC2. Mutants: the Last updated line dropped, doubled, or left behind the latest row."""
        dates = history_dates(self.text)
        self.assertTrue(dates, "the index has no Revision History rows")
        stated = LAST_UPDATED.findall(self.text)
        self.assertEqual(len(stated), 1, f"the index carries {len(stated)} Last updated lines")
        self.assertEqual(stated[0], max(dates), "Last updated is not the latest history date")

    def test_the_index_records_the_served_approver_and_the_narrowed_negative(self) -> None:
        """US1147 AC6. Mutants: the row dropped or its Change reworded; the row dated other than
        the day the commit adding the change approver's card carries (today, while uncommitted).
        Date order and Last updated are the two tests above."""
        change = (f"{slug_name(CHANGE_APPROVER_CARD)} added as Served, the change approver "
                  f"(D0437); {the_negative()[0]} narrowed to a GUI-first operator, non-technical "
                  f"staff running the tool and a human approval on every change (D0436)")
        rows = [row for row in table_rows(card_section(self.text, "Revision History"))
                if len(row) > 2 and row[2] == change]
        self.assertEqual(len(rows), 1, "the Revision History has no one row recording US1147's change")
        log = subprocess.run(["git", "log", "--diff-filter=A", "--date=short", "--format=%ad", "--",
                              CHANGE_APPROVER_CARD.relative_to(REPO).as_posix()],
                             cwd=str(REPO), capture_output=True, text=True, check=True,
                             env=gitutil.git_env())
        added = log.stdout.split()
        self.assertEqual(rows[0][0], added[-1] if added else datetime.date.today().isoformat(),
                         "the row is not dated the day the change approver's card is committed")

    def test_the_index_links_the_seat_cards_in_force(self) -> None:
        """AC3, the paths asked of the shipped CLI. Mutants: a seat card linked under a role
        heading, which the reader registers as a persona; a seat left unlinked, or linked to the
        shipped template its override replaces."""
        in_force = set()
        for seat in SEATS:
            run = subprocess.run([sys.executable, str(SCRIPTS / "persona_resolve.py"), "resolve",
                                  "--seat", seat, "--path-only", "--root", str(REPO)],
                                 capture_output=True, text=True, cwd=str(REPO))
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            in_force.add(Path(run.stdout.strip()).resolve())
        holding = [h for h in headings(self.text)
                   if links_from(REGISTRY, card_section(self.text, re.escape(h))) & in_force]
        self.assertEqual(len(holding), 1, f"the seat cards are linked under {holding}, not one "
                                          f"heading")
        self.assertFalse(is_role_heading(holding[0], role_vocabulary()),
                         f"the seat cards are linked under a role heading: {holding[0]}")
        self.assertEqual(links_from(REGISTRY, card_section(self.text, re.escape(holding[0]))),
                         in_force, "the seat heading's links are not exactly the cards in force")
        home = Path(tempfile.mkdtemp(prefix="us1083-"))
        try:
            unlinked = home / "sdlc-studio" / "personas" / "index.md"
            unlinked.parent.mkdir(parents=True)
            unlinked.write_text("\n".join(line for line in self.text.splitlines()
                                          if not links_from(REGISTRY, line) & in_force),
                                encoding="utf-8")
            self.assertTrue(registry_entries(REPO), "the registry reader returns nobody")
            self.assertEqual(registry_entries(REPO), registry_entries(home),
                             "the seat links change the personas the registry reader returns")
        finally:
            shutil.rmtree(home, ignore_errors=True)

    def test_the_legacy_file_agrees_with_its_banner(self) -> None:
        """AC4. Mutants: line 46's Role field left calling the operator the primary user; the
        skill-maintainer section left without the tooling Primary's card, or linking another."""
        text = LEGACY.read_text(encoding="utf-8")
        roles = role_vocabulary()
        self.assertTrue(roles, "the index declares no role the reader reads")
        sections = {h: card_section(text, re.escape(h)) for h in headings(text)}
        fields = {h: ROLE_FIELD.findall(body) for h, body in sections.items()}
        self.assertEqual([h for h, found in fields.items() if len(found) != 1], [],
                         "a legacy persona section does not carry exactly one Role field")
        self.assertEqual({h: f[0] for h, f in fields.items() if names_a_role(f[0], roles)}, {},
                         f"a legacy Role field names a registry role ({sorted(roles)})")
        _, tooling = shipped_and_tooling()
        self.assertEqual(len(tooling), 1, "not exactly one tooling Primary to link")
        maintainer = [h for h in sections if re.search(r"\bmaintainer\b", h, re.I)]
        self.assertEqual(len(maintainer), 1, f"not one skill-maintainer section: {maintainer}")
        self.assertIn(tooling[0][1].resolve(), links_from(LEGACY, sections[maintainer[0]]),
                      f"the {maintainer[0]} section does not link {tooling[0][0]}'s card")


def tracked_markdown() -> list[Path]:
    """Every tracked markdown file, listed from the repo rather than enumerated."""
    out = subprocess.run(["git", "ls-files", "-z", "--", "*.md"],
                         cwd=str(REPO), capture_output=True, text=True, check=True)
    files = [REPO / p for p in out.stdout.split("\0") if p]
    if not files:
        raise AssertionError("no tracked markdown listed - the scan would pass vacuously")
    return files


def _roots_holding(files: list[Path], marker: str) -> set[Path]:
    return {f.parent for f in files if f.name == marker}


def live_documents(files: list[Path]) -> list[Path]:
    """Tracked markdown that speaks for the project as it stands now.

    Two kinds of file are excluded, both discovered rather than listed:

    * the shipped skill payload (any directory holding a `SKILL.md`) - it documents the
      generic per-project workspace layout, in which `personas.md` is a real artefact
      path for a consuming project, not a route to this repo's superseded set;
    * artefact records (any directory holding a derived `_index.md`) - a bug, story, CR
      or RFC is a dated record of what was true when it was filed, not a live route.
    """
    excluded = _roots_holding(files, "SKILL.md") | _roots_holding(files, "_index.md")
    return [f for f in files
            if f != LEGACY and not any(root in f.parents for root in excluded)]


def routes_to_legacy(path: Path, line: str) -> bool:
    """Does this line send a reader to `sdlc-studio/personas.md`?"""
    if "sdlc-studio/personas.md" in line:
        return True
    for target in re.findall(r"\]\(([^)]+)\)", line):
        candidate = (path.parent / target.split("#")[0]).resolve()
        if candidate == LEGACY.resolve():
            return True
    return False


class LegacyAppendixTests(unittest.TestCase):
    """AC1/AC2 of US0451."""

    def test_personas_md_declares_itself_superseded_by_the_registry(self) -> None:
        lines = LEGACY.read_text(encoding="utf-8").splitlines()
        body = [(i, ln) for i, ln in enumerate(lines)
                if ln.strip() and not ln.lstrip().startswith(("<!--", "Template:",
                                                              "File:", "Source:",
                                                              "Generated:", "Confidence:",
                                                              "Status values:", "Related:",
                                                              "-->"))]
        self.assertTrue(body, "personas.md is empty")

        pointer = next((i for i, ln in body if "personas/index.md" in ln), None)
        self.assertIsNotNone(pointer,
                             "personas.md never points at the persona registry")

        labelled = next((i for i, ln in body if LEGACY_LABEL.search(ln)), None)
        self.assertIsNotNone(labelled,
                             "personas.md does not declare itself legacy or superseded")

        first_persona = next((i for i, ln in body if ln.startswith("## ")), None)
        self.assertIsNotNone(first_persona, "personas.md has no persona sections")
        self.assertLess(pointer, first_persona,
                        "the registry pointer sits below persona content, so a reader "
                        "meets the superseded personas first")
        self.assertLess(labelled, first_persona,
                        "the legacy label sits below persona content")

    def test_no_live_document_routes_to_the_superseded_set(self) -> None:
        offenders = []
        for path in live_documents(tracked_markdown()):
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            for i, line in enumerate(lines):
                if not routes_to_legacy(path, line):
                    continue
                context = " ".join(lines[max(0, i - 1):i + 2])
                if LEGACY_LABEL.search(context):
                    continue  # explicitly marked as the superseded set
                offenders.append(f"{path.relative_to(REPO)}:{i + 1}: {line.strip()}")
        self.assertEqual(offenders, [],
                         "live document(s) route a reader to the superseded personas: "
                         + "; ".join(offenders))


if __name__ == "__main__":
    unittest.main()
