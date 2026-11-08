"""US1138 (EP0301): the PRD, TRD and TSD describe what 6.3 ships.

The network table is held to a scan of the shipped scripts' imports, so a reader that opens a
connection fails here until the TRD names it. The state files, the cost model's harness switch
and the price and lane features are read from the modules that define them. Typed here are the
unit ids, since no code enumerates which units built a feature, and the phrases each row must say.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_specs_v63.py
"""
# test-census-subject: sdlc-studio/trd.md
from __future__ import annotations

import ast
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
SPECS = {name: REPO / "sdlc-studio" / f"{name}.md" for name in ("prd", "trd", "tsd")}
STORIES = REPO / "sdlc-studio" / "stories"

sys.path.insert(0, str(SCRIPTS))
from lib import lanes, meter_cursor, run_state, token_meters  # noqa: E402

#: A statement that the skill handles no secret, in either word order, across a line break.
NO_SECRETS = re.compile(r"\bhandles?\s+no\s+secrets?\b|\bno\s+secrets?\s+(?:are\s+)?handled\b",
                        re.I)
#: The cost model's retired premise, in the two phrasings the TRD has used.
SUPPLIED = re.compile(r"supplied,?\s+(?:rather\s+than|not)\s+observed", re.I)
#: Each 6.3 feature: what its inventory row must name (a location the code holds, a phrase) and
#: the units that built it.
FEATURES = {
    "multi-harness token meter": (("scripts/lib/token_meters.py", token_meters.HARNESS_ENV),
                                  ("US0986", "US0987", "US0988", "US0989", "US0990", "US1127")),
    "price table and dollar cost": (("scripts/lib/prices.py", "templates/model-prices.json",
                                     "Dollar cost"), ("US1122", "US1123", "US1135")),
    "cost anatomy": (("scripts/lib/cost_anatomy.py", "--anatomy"), ("US1124",)),
    "headless lane run and landing": (("scripts/lib/lanes.py", "lane run", "lane land"),
                                      ("US1118", "US1119", "US1120", "US1126")),
    "lean agent definitions": (("templates/agents/", "sdlc-builder", "sdlc-reviewer"),
                               ("US1131", "US1132")),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _body(text: str) -> str:
    """A spec without its Revision History, whose rows record what earlier versions said."""
    return text.split("\n## Revision History", 1)[0]


def _section(text: str, heading: str) -> str:
    """The body under the one heading titled `heading`, to the next of the same or a higher level."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if re.fullmatch(rf"#+\s+{re.escape(heading)}\s*", line)]
    if len(starts) != 1:
        raise AssertionError(f"{len(starts)} headings titled {heading!r}, expected one")
    level = len(lines[starts[0]].split()[0])
    out = []
    for line in lines[starts[0] + 1:]:
        m = re.match(r"^(#+)\s", line)
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def _rows(text: str, first: str) -> list[list[str]]:
    """The body rows of every table in `text` whose header's first cell is `first`."""
    out, header = [], None
    for line in text.splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = cells
        elif header[0] == first and not set(cells[0]) <= set("-: "):
            out.append(cells)
    return out


def _spans(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def _imports_urllib_request(source: str) -> bool:
    """Whether `source` imports `urllib.request`, as a module or a name from it, anywhere."""
    for node in ast.walk(ast.parse(source)):
        names = ([a.name for a in node.names] if isinstance(node, ast.Import) else
                 [f"{node.module}.{a.name}" for a in node.names]
                 if isinstance(node, ast.ImportFrom) and node.module else [])
        if any(n == "urllib.request" or n.startswith("urllib.request.") for n in names):
            return True
    return False


def _urllib_importers() -> set[str]:
    """Each shipped script, relative to `scripts/`, whose code imports `urllib.request`."""
    return {p.relative_to(SCRIPTS).as_posix() for p in SCRIPTS.rglob("*.py")
            if not {"tests", "__pycache__"} & set(p.relative_to(SCRIPTS).parts)
            and _imports_urllib_request(_read(p))}


def _under_local(rel: Path) -> str:
    """`rel`, a path the code joins under `sdlc-studio/.local/`, as the state table writes it."""
    parts = rel.parts
    if parts[:2] != ("sdlc-studio", ".local"):
        raise AssertionError(f"{rel} is not under sdlc-studio/.local/")
    return "/".join(parts[2:])


def _names_state(span: str, path: str, directory: bool) -> bool:
    """Whether a state-table span names `path`: the file itself, or the directory alone or
    followed by a `<placeholder>` component, so `lane/landed/<worktree>/` names `lane/landed/`
    and not `lane/`."""
    if not directory:
        return span == path
    rest = span[len(path) + 1:] if span.startswith(path + "/") else None
    return rest is not None and (rest == "" or rest.startswith("<"))


class SpecsV63Tests(unittest.TestCase):
    """US1138: what the three specs say 6.3 ships."""

    def test_every_network_path_and_the_one_credential_are_named(self) -> None:
        """AC1. Mutants: the Cursor row dropped, or given another script, function, override
        variable, timeout or redirect rule; rule 6 not naming `meter_cursor.py`; 'handles no
        secrets' or 'No secrets handled' left in any of the three specs; a spec not saying it
        stores none and sends `CURSOR_API_KEY`. The import reader is checked first on a sample of
        each import form and its near misses, and the scan on its two known importers."""
        for source, imports in (("import urllib.request\n", True),
                                ("from urllib import request\n", True),
                                ("def f():\n    from urllib.request import urlopen\n", True),
                                ("import urllib.parse\n", False),
                                ("from urllib import parse\n", False),
                                ("# import urllib.request\nx = 'urllib.request'\n", False)):
            with self.subTest(source=source):
                self.assertIs(imports, _imports_urllib_request(source))
        for text, says in (("No secrets handled by the skill", True), ("it handles no secrets", True),
                           ("The skill stores no secret", False)):
            self.assertIs(says, NO_SECRETS.search(text) is not None, text)
        importers = _urllib_importers()
        self.assertLessEqual({"version_check.py", "lib/meter_cursor.py"}, importers)
        trd = _body(_read(SPECS["trd"]))
        rows = _rows(_section(trd, "Network paths"), "Path")
        self.assertGreaterEqual(len(rows), 5, "premise: the Network paths table moved")
        by_script = {r[1].strip("`"): r for r in rows}
        self.assertEqual(set(), importers - set(by_script),
                         "a shipped script imports urllib.request and has no Network paths row")
        row = by_script["lib/meter_cursor.py"]
        self.assertIn(row[2].strip("`"), {n.name for n in ast.walk(ast.parse(
            _read(SCRIPTS / "lib" / "meter_cursor.py"))) if isinstance(n, ast.FunctionDef)})
        endpoint = row[3]
        self.assertIn(meter_cursor.API_BASE, endpoint)
        self.assertIn(f"`{meter_cursor.API_ENV}`", endpoint)
        self.assertIn(f"{meter_cursor.TIMEOUT_SECONDS:g} s timeout", endpoint)
        self.assertRegex(endpoint, r"redirect refused")
        self.assertIn(f"`{meter_cursor.KEY_ENV}`", " ".join(row))
        rule6 = re.search(r"^6\. (.*?)(?=^\d+\. )", _section(trd, "5. API Contracts"), re.M | re.S)
        self.assertIsNotNone(rule6, "section 5 has no rule 6")
        self.assertIn("meter_cursor.py", rule6.group(1))
        for name, path in SPECS.items():
            with self.subTest(spec=name):
                text = _flat(_read(path))
                self.assertIsNone(NO_SECRETS.search(text), NO_SECRETS.search(text))
                self.assertRegex(text, r"stores no secret")
                self.assertIn(f"`{meter_cursor.KEY_ENV}`", text)

    def test_the_trd_cost_model_and_state_files_match_63(self) -> None:
        """AC2. Mutants: the cost model keeping 'supplied, not observed', or not naming the
        harness switch or `includes_subagents`; the Won't Have line keeping 'supplied rather
        than observed'; any of the six 6.3 state paths missing from the `.local/` table, or
        named only inside another's path, or given a writer cell citing no shipped script."""
        trd = _body(_read(SPECS["trd"]))
        self.assertIsNone(SUPPLIED.search(_flat(trd)), SUPPLIED.search(_flat(trd)))
        model = _flat(_section(trd, "10. Performance Requirements"))
        model = model.split("**The cost model, and how it is recorded.**", 1)
        self.assertEqual(2, len(model), "premise: the cost model paragraph moved")
        model = model[1]
        self.assertIn("store of the harness running the session", model)
        self.assertIn(f"`{token_meters.HARNESS_ENV}`", model)
        self.assertIn("`includes_subagents`", model)
        self.assertIn("delegated agents' spend", model)
        table = _rows(_section(trd, "JSON state files (under `.local/`)"), "File")
        self.assertGreaterEqual(len(table), 13, "premise: the .local table moved")
        wanted = {_under_local(run_state.METER_MEMO_REL): False,
                  _under_local(meter_cursor.LEDGER_REL): False,
                  _under_local(lanes.RUN_RECORDS): True, _under_local(lanes.HAND_IN): True,
                  _under_local(lanes.LANDED): True, _under_local(lanes.BRIEFS): True}
        self.assertEqual(6, len(wanted))
        for path, directory in wanted.items():
            with self.subTest(state=path):
                hits = [r for r in table if any(_names_state(s, path, directory)
                                                for s in _spans(r[0]))]
                self.assertEqual(1, len(hits), f"{path}: {len(hits)} rows name it")
                cited = re.findall(r"`([\w/.-]+\.py)`", hits[0][1])
                self.assertTrue(cited and all((SCRIPTS / c).is_file() for c in cited), hits[0])

    def test_the_prd_inventory_names_63s_features(self) -> None:
        """AC3. Mutants: any 6.3 feature's row dropped, or not naming its location, its phrase
        or one of its units, or not Complete; `release_strategy` missing from the flags table or
        given a default other than the shipped one."""
        prd = _body(_read(SPECS["prd"]))
        rows = _rows(_section(prd, "3. Feature Inventory"), "Feature")
        self.assertGreaterEqual(len(rows), 40, "premise: the Feature Inventory moved")
        for feature, (marks, units) in FEATURES.items():
            with self.subTest(feature=feature):
                for mark in (m for m in marks if m.startswith(("scripts/", "templates/"))):
                    self.assertTrue((SKILL / mark).is_dir() if mark.endswith("/")
                                    else (SKILL / mark).is_file(), f"premise: {mark} moved")
                for unit in units:
                    self.assertTrue(list(STORIES.glob(f"{unit}-*.md")), unit)
                hits = [r for r in rows if all(m in " | ".join(r) for m in marks)]
                self.assertEqual(1, len(hits), f"{feature}: {len(hits)} rows name {marks}")
                self.assertEqual("Complete", hits[0][2])
                self.assertEqual([], [u for u in units if not re.search(
                    rf"\b{u}\b", " | ".join(hits[0]))])
        default = re.search(r"^release_strategy:\s*(\S+)",
                            _read(SKILL / "templates" / "config-defaults.yaml"), re.M)
        self.assertEqual("trunk", default.group(1) if default else None)
        flags = {r[0]: r for r in _rows(_section(prd, "Feature Flags"), "Key")}
        self.assertIn("`release_strategy`", flags)
        self.assertEqual(f"`{default.group(1)}`", flags["`release_strategy`"][1])


if __name__ == "__main__":
    unittest.main()
