"""Drift guard: reference-schema.md must match what the code enforces.

The published artefact-schema contract (reference-schema.md) documents vocabularies that
live canonically in the code (lib/sdlc_md.py). If the two diverge, the contract has rotted
and a consumer that trusted it is misled. This guard parses the contract's declared
vocabularies and asserts set-equality with the code constants - the doc must match the code,
never the reverse.

The parsers refuse to extract nothing: an emptied, renamed or restructured contract surface
raises, so the guard fails loudly rather than passing vacuously against an empty set.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent.parent
SCHEMA_DOC = SKILL / "reference-schema.md"
# The version stamp new projects are seeded with (init copies this) - the current schema
# version the contract masthead declares.
CONFIG_TEMPLATE = SKILL / "templates" / "config.yaml"
# The skill's fallback default, applied to a project that declares no schema_version.
CONFIG_DEFAULTS = SKILL / "templates" / "config-defaults.yaml"


def _section(doc: str, heading: str) -> str:
    """The body of a `## <heading>` section, up to the next `## ` heading. Raises if the
    heading is absent - a renamed contract surface must fail, never silently return nothing."""
    lines = doc.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = i + 1
            break
    if start is None:
        raise ValueError(f"contract surface not found: no `## {heading}` heading in "
                         f"{SCHEMA_DOC.name} - the section was renamed or removed")
    body = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _is_separator(cells: list[str]) -> bool:
    return all(set(c) <= {"-", ":"} and c for c in cells)


def parse_status_table(doc: str) -> dict[str, dict[str, set[str]]]:
    """Parse the `## Status Vocabulary` table into {type: {statuses, terminal}}.

    Raises if the section or its table body cannot be located: extraction is asserted
    non-empty before any comparison, so the guard can never pass against an empty contract.
    """
    body = _section(doc, "Status Vocabulary")
    out: dict[str, dict[str, set[str]]] = {}
    for line in body.splitlines():
        if line.startswith("### "):
            break  # the base table ends where a subsection (e.g. Schema v3 additions) begins
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or _is_separator(cells):
            continue
        type_ = cells[0]
        if type_.lower() == "type":  # the table header row
            continue
        statuses = {s.strip() for s in cells[1].split(",") if s.strip()}
        terminal = {s.strip() for s in cells[2].split(",") if s.strip()}
        if not statuses:
            continue
        out[type_] = {"statuses": statuses, "terminal": terminal}
    if not out:
        raise ValueError(f"no status rows parsed from the Status Vocabulary table in "
                         f"{SCHEMA_DOC.name} - the table was emptied or restructured")
    return out


def parse_v3_inbox_types(doc: str) -> dict[str, set[str]]:
    """Parse the `### Schema v3 additions` table into {status: {types it applies to}}.

    Raises if the subsection or its table body is absent - the v3 vocabulary addition is a
    guarded contract surface, not free prose, so an emptied or renamed table must fail.
    """
    body = _section(doc, "Status Vocabulary")
    lines = body.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "### Schema v3 additions":
            start = i + 1
            break
    if start is None:
        raise ValueError("contract surface not found: no `### Schema v3 additions` subsection "
                         f"in {SCHEMA_DOC.name}")
    out: dict[str, set[str]] = {}
    for line in lines[start:]:
        if line.startswith("## ") or line.startswith("### "):
            break
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or _is_separator(cells) or cells[0].lower().startswith("v3-only"):
            continue
        types = {t.strip() for t in cells[1].split(",") if t.strip()}
        if types:
            out[cells[0]] = types
    if not out:
        raise ValueError(f"no rows parsed from the Schema v3 additions table in "
                         f"{SCHEMA_DOC.name} - the table was emptied or restructured")
    return out


def parse_masthead_version(doc: str) -> int:
    """The schema version stated in the masthead (`Schema version N`). Raises if absent."""
    m = re.search(r"Schema version\s+(\d+)", doc)
    if not m:
        raise ValueError(f"no `Schema version N` masthead in {SCHEMA_DOC.name}")
    return int(m.group(1))


def parse_yaml_schema_version(yaml_text: str, name: str) -> int:
    """The `schema_version` key value from a config YAML (the key line, not a comment)."""
    m = re.search(r"(?m)^schema_version:\s*(\d+)", yaml_text)
    if not m:
        raise ValueError(f"no `schema_version:` key in {name}")
    return int(m.group(1))


class StatusVocabularyContractTests(unittest.TestCase):
    """AC1: the status vocabulary in the doc matches the code, set-for-set."""

    def setUp(self) -> None:
        self.parsed = parse_status_table(SCHEMA_DOC.read_text(encoding="utf-8"))

    def test_documented_types_match_code(self) -> None:
        self.assertEqual(
            set(self.parsed), set(sdlc_md.STATUS_VOCAB),
            "the Status Vocabulary table documents a different set of types than the code "
            "enforces (STATUS_VOCAB)",
        )

    def test_each_type_status_set_matches(self) -> None:
        for type_, code_vocab in sdlc_md.STATUS_VOCAB.items():
            with self.subTest(type=type_):
                self.assertIn(type_, self.parsed, f"{type_} missing from the contract table")
                doc = self.parsed[type_]["statuses"]
                code = set(code_vocab)
                self.assertEqual(
                    doc, code,
                    f"{type_} status vocabulary drifted: doc-only={sorted(doc - code)}, "
                    f"code-only={sorted(code - doc)}",
                )

    def test_each_type_terminal_set_matches(self) -> None:
        for type_ in sdlc_md.STATUS_VOCAB:
            with self.subTest(type=type_):
                doc = self.parsed[type_]["terminal"]
                code = sdlc_md.terminal_statuses(type_)
                self.assertEqual(
                    doc, code,
                    f"{type_} terminal states drifted: doc-only={sorted(doc - code)}, "
                    f"code-only={sorted(code - doc)}",
                )


class V3InboxLaneContractTests(unittest.TestCase):
    """AC1 (v3 surface): the documented Schema v3 `inbox` addition matches the code - the one
    vocabulary the base table cannot carry, so binding rule #1 ("the guard covers the
    vocabularies below") holds for the v3 lane too, not just the base."""

    def setUp(self) -> None:
        self.parsed = parse_v3_inbox_types(SCHEMA_DOC.read_text(encoding="utf-8"))

    def test_added_status_is_the_code_inbox_status(self) -> None:
        self.assertIn(
            sdlc_md.INBOX_STATUS, self.parsed,
            f"the Schema v3 additions table does not document the code's INBOX_STATUS "
            f"({sdlc_md.INBOX_STATUS!r})",
        )

    def test_inbox_applies_to_exactly_the_finding_types(self) -> None:
        doc_types = self.parsed.get(sdlc_md.INBOX_STATUS, set())
        self.assertEqual(
            doc_types, set(sdlc_md.FINDING_TYPES),
            f"the v3 `inbox` lane is documented for {sorted(doc_types)} but the code applies "
            f"it to {sorted(sdlc_md.FINDING_TYPES)} (FINDING_TYPES)",
        )


class VersionStampContractTests(unittest.TestCase):
    """AC2: the masthead version and the shipped new-project stamp agree - a one-sided bump
    fails. The masthead declares the current schema version; new projects are stamped from
    templates/config.yaml, so those two must match. The fallback default (config-defaults.yaml)
    may lag (it is what an un-stamped legacy project reads) but must never lead the current."""

    def setUp(self) -> None:
        self.masthead = parse_masthead_version(SCHEMA_DOC.read_text(encoding="utf-8"))

    def test_masthead_matches_new_project_seed(self) -> None:
        seed = parse_yaml_schema_version(
            CONFIG_TEMPLATE.read_text(encoding="utf-8"), CONFIG_TEMPLATE.name)
        self.assertEqual(
            self.masthead, seed,
            f"schema version stamp drift: reference-schema.md masthead says {self.masthead}, "
            f"but new projects are stamped {seed} (templates/config.yaml) - a version bump "
            f"must move both",
        )

    def test_fallback_default_does_not_lead_current(self) -> None:
        fallback = parse_yaml_schema_version(
            CONFIG_DEFAULTS.read_text(encoding="utf-8"), CONFIG_DEFAULTS.name)
        self.assertLessEqual(
            fallback, self.masthead,
            f"config-defaults.yaml fallback ({fallback}) is ahead of the current schema "
            f"version ({self.masthead}) - the fallback is for legacy projects and cannot "
            f"exceed the current",
        )


class ParserHonestyTests(unittest.TestCase):
    """AC3: the guard cannot pass vacuously - a degraded contract surface raises."""

    def test_renamed_section_raises(self) -> None:
        doc = SCHEMA_DOC.read_text(encoding="utf-8").replace(
            "## Status Vocabulary", "## Status Words")
        with self.assertRaises(ValueError):
            parse_status_table(doc)

    def test_emptied_table_raises(self) -> None:
        # Keep the heading, strip every table row: the parser must find nothing and refuse.
        body_gone = re.sub(r"(?ms)^## Status Vocabulary.*?(?=^## )",
                           "## Status Vocabulary\n\n(table removed)\n\n",
                           SCHEMA_DOC.read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            parse_status_table(body_gone)

    def test_missing_masthead_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_masthead_version("# A doc with no version stamp\n\nbody\n")

    def test_removed_v3_additions_raises(self) -> None:
        doc = SCHEMA_DOC.read_text(encoding="utf-8").replace(
            "### Schema v3 additions", "### Schema v3 notes")
        with self.assertRaises(ValueError):
            parse_v3_inbox_types(doc)


if __name__ == "__main__":
    unittest.main()
