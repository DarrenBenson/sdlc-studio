"""US0450/US0451: the PRD and the persona registry must state one design target.

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
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
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
