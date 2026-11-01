"""US0450/US0451: the PRD and the persona registry must state one design target.
US1079: with two Primaries, one per interface (D0379), each states which interface it serves.
US1080: a story minted with no persona follows the paths those Interface rows declare.
US1081: the shipped skill's Primary and the Negative state the run as it now runs.

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
import functools
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

ROLES = ("Primary", "Secondary", "Negative")
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

    def test_expected_names_are_derived_from_the_registry_not_hardcoded(self) -> None:
        # 1. The parser reads whatever the registry says, rather than knowing an answer.
        stub = REPO / "sdlc-studio" / "personas" / "index.md"  # shape only; body below
        fabricated = (
            "# Persona Index\n\n"
            "## Primary (the design target)\n\n"
            "- [Quimby Vantablack](quimby.md) - stub\n\n"
            "## Secondary (served)\n\n"
            "- [Rowan Fitzhubbard](rowan.md) - stub\n\n"
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


#: The commit the shipped Primary's End goals 1 to 4 are held to, word for word (US1081 AC1).
GOALS_BASE = "7f3e91a9"
#: End goal 5 as US1081 AC1 states it (D0383), so the test holds the criterion's words.
END_GOAL_5 = ("Keep the process small enough to serve the work - every check earns its keep, "
              "and one that catches nothing is retired")
CODE_SPAN = re.compile(r"`([^`\n]+)`")
#: A `script.py verb` span: an optional `python3` and directory, the script, then a word that is
#: not a flag.
SCRIPT_VERB = re.compile(r"^(?:python3\s+)?(?:\S*/)?([\w-]+\.py)\s+([^\s-]\S*)")
#: A skill command span such as `/sdlc-studio gate`.
SKILL_COMMAND = re.compile(r"^/sdlc-studio\s+([a-z][\w-]*)")
#: A sprint run: the skill's `sprint` command with flags only, so `sprint plan` is not one.
SPRINT_RUN = re.compile(r"^/sdlc-studio\s+sprint(?:\s+--|$)")
SIGN_SPAN = re.compile(r"^sprint\.py\s+sign(?:\s|$)")


def end_goal_items(text: str) -> dict[str, list[str]]:
    """A card's End goals by number, each as the lines it is written on."""
    items: dict[str, list[str]] = {}
    current = None
    for line in card_section(text, "End Goals").splitlines():
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
                         cwd=str(REPO), capture_output=True, text=True)
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

    def test_mayas_end_goals_keep_their_numbers_and_gain_the_fifth(self) -> None:
        """AC1. Mutants: End goal 1 to 4 reworded or renumbered; End goal 5 missing, reworded
        or wrapped onto a second line, which BG1107 truncates."""
        base = end_goal_items(committed_text(GOALS_BASE, self.card))
        self.assertEqual(sorted(base), ["1", "2", "3", "4"], f"the {GOALS_BASE} baseline moved")
        now = end_goal_items(self.text)
        self.assertEqual({n: now.get(n) for n in base}, base,
                         f"End goals 1 to 4 differ from {GOALS_BASE}")
        self.assertEqual(now.get("5"), [END_GOAL_5], "End goal 5 is not the criterion's one line")

    def test_mayas_card_names_shipped_commands_and_the_sign_step(self) -> None:
        """AC2, each `script.py verb` span asked of that script's own `--help`. Mutants: a span
        naming a verb the script does not take (`sprint.py sigh`) or a script that does not ship;
        a span naming a path in the tooling Primary's Interface row (`.githooks/pre-push`); the
        Scenario naming no `sprint` run (an autosprint), or naming `sprint.py sign` before it."""
        spans = CODE_SPAN.findall(self.text)
        verbs = [m.groups() for m in map(SCRIPT_VERB.match, spans) if m]
        self.assertTrue(verbs, "the card names no `script.py verb` span")
        self.assertEqual([f"{s} {v}" for s, v in verbs if not verb_accepted(s, v)], [],
                         "a span names a verb the shipped scripts do not accept")
        commands = [m.group(1) for m in map(SKILL_COMMAND.match, spans) if m]
        self.assertEqual([c for c in commands
                          if not (SCRIPTS.parent / "help" / f"{c}.md").is_file()], [],
                         "a span names a skill command with no help file")
        paths = [p for _, card in self.tooling for p in interface_paths(card)]
        self.assertTrue(paths, "the tooling Primary's Interface row declares no path")
        self.assertEqual([s for s in spans if any(names_path(s, p) for p in paths)], [],
                         "a span names a path in the tooling Primary's interface")
        scenario = CODE_SPAN.findall(card_section(self.text, "Scenario"))
        runs = [i for i, s in enumerate(scenario) if SPRINT_RUN.match(s)]
        signs = [i for i, s in enumerate(scenario) if SIGN_SPAN.match(s)]
        self.assertTrue(runs, f"the Scenario names no `sprint` run: {scenario}")
        self.assertTrue(signs, f"the Scenario names no `sprint.py sign`: {scenario}")
        self.assertLess(runs[0], signs[0], "the Scenario signs before it runs the sprint")

    def test_mayas_boundaries_table_the_primary_for_each_interface(self) -> None:
        """AC3, with the mixed row also asked of the shipped mint. Mutants: no link to another
        Primary's card; the mixed row naming the tooling Primary (the rule reversed); an
        interface cell that is not the name the card's Interface row gives; the index listing
        the tooling Primary first, which moves both the reading and the mint."""
        cards = primary_cards()
        boundary = card_section(self.text, "Boundaries")
        self.assertTrue(boundary.strip(), "the card has no Boundaries section")
        links = links_from(self.card, boundary)
        self.assertEqual([n for n, c in cards if c.resolve() != self.card.resolve()
                          and c.resolve() not in links], [],
                         "Boundaries does not link every other Primary's card")
        rows = table_rows(boundary)
        expected = [[interface_name(c), n] for n, c in cards]
        self.assertEqual([e for e in expected if e not in rows], [],
                         f"no row maps each interface to its Primary: {rows}")
        mixed = [r for r in rows if r not in expected]
        self.assertEqual(len(mixed), 1, f"want one row for a unit touching both: {rows}")
        self.assertRegex(mixed[0][0], r"(?i)\bboth\b")
        self.assertEqual(mixed[0][1:], [cards[0][0]],
                         "a unit touching both is not the Primary the index lists first")
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
        it cites that resolves to nothing; a Primary's card not linked."""
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
            links = links_from(card, text)
            self.assertEqual([n for n, c in primary_cards() if c.resolve() not in links], [],
                             f"{name}'s card does not link each Primary's card")


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
