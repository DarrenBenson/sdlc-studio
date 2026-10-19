"""US0450/US0451: the PRD and the persona registry must state one design target.
US1079: with two Primaries, one per interface (D0379), each states which interface it serves.

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


def primary_cards(index_path: Path = REGISTRY) -> list[tuple[str, Path]]:
    """Each `## Primary` bullet as (name, card path), in index order. Never hardcoded."""
    out, in_primary = [], False
    for line in index_path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"##\s+(\w+)", line)
        if heading:
            in_primary = heading.group(1) == "Primary"
            continue
        link = re.match(r"\s*-\s+\[([^\]]+)\]\(([^)]+)\)", line) if in_primary else None
        if link:
            out.append((link.group(1).strip(), index_path.parent / link.group(2)))
    return out


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
        `## Primary`, which silently makes every unnamed mint his until US1080."""
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
