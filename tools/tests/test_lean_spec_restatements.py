"""US0933: the TRD and TSD stop restating lists and counts the code derives.

Seven units of rework (BG0332, BG0401, BG0420, BG0457, BG0571, CR0302, US0766) went into keeping
the specs' copies of code lists in step, each copy held by a test that pinned the prose to the
code. D0266 cuts the copies with their pins: a spec says what only a person decides and points
at the code for what the code derives. This module checks the cut, not the prose - it reads each
list from the code and refuses a passage that restates it, so nothing here needs updating when
a lane, a drift kind or a type is added.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import importlib.util
import inspect
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
TRD = REPO / "sdlc-studio" / "trd.md"
TSD = REPO / "sdlc-studio" / "tsd.md"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "lib"))

#: The pin modules this story deletes, as its AC3 names them.
DELETED = ("test_trd_surface_derivation", "test_trd_freshness", "test_spec_counts_are_not_pinned")
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0933: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0933\b")

#: The most members of one code-held list a single paragraph or table row may name. Two lets a
#: passage say "`reconcile` and `validate`" about a pair; three is the start of a restated list.
MAX_NAMED = 2
#: The router's types are ordinary command words (`story`, `bug`, `plan`, `status`), and the
#: TRD's data architecture names the ten types its two backlogs split, a decision rather than a
#: copy. So a passage restates the Type Reference table when it names MORE THAN HALF of it.
TYPES_SHARE = 0.5

#: A stated count of components: "60+ scripts", "(6 modules)", "well over 2,500 tests",
#: "six-module lib/", "2000-plus-test run", with up to two words between the number and the
#: noun ("(40+ help files)", "70+ shipped Python scripts"). "one" is left out: "one test" is a
#: sentence, not an inventory.
_NUMBER = (r"(?:~?\d[\d,]*\+?|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
           r"dozens?|hundreds?|thousands?)")
_COUNT = re.compile(rf"\b{_NUMBER}(?:[\s-]*plus)?(?:[\s-]+[a-z]\w*){{0,2}}[\s-]+"
                    rf"(?:scripts?|modules?|files?|tests?)\b", re.I)
_MEASURED = re.compile(r"<!--\s*measured:", re.I)
_HISTORY = re.compile(r"^##+\s*Revision History\b", re.M)
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
#: An ADR records the decision as it stood when it was made, its sizes included, so its counts
#: stay (D0266): the ADR section and each `ADR-NNN` heading are skipped to their section end.
_ADR = re.compile(r"\bADR-\d+|\bArchitecture Decision Records?\b", re.I)


def _mod(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_us0933", SCRIPTS / f"{name}.py")
    assert spec and spec.loader, f"cannot load {name}.py"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}_us0933"] = mod
    spec.loader.exec_module(mod)
    return mod


def _live(text: str) -> str:
    """The document above its Revision History: a row naming what WAS true is a record."""
    m = _HISTORY.search(text)
    return text[:m.start()] if m else text


def _passages(text: str) -> list[str]:
    """Every paragraph, with each table row a passage of its own."""
    out: list[str] = []
    for para in re.split(r"\n\s*\n", _live(text)):
        rows = [ln for ln in para.splitlines() if ln.lstrip().startswith("|")]
        rest = [ln for ln in para.splitlines() if not ln.lstrip().startswith("|")]
        out.extend(rows)
        if any(ln.strip() for ln in rest):
            out.append("\n".join(rest))
    return out


def _named(passage: str, members: set[str]) -> set[str]:
    """The members a passage names: in backticks or bold, any case, and a hyphenated member
    (`duplicate-id`, `missing-row`) even as a plain word, since no sentence uses it otherwise."""
    marked = {n.lower() for n in re.findall(r"`([A-Za-z][\w-]*)`", passage)}
    marked |= {n.lower() for n in re.findall(r"\*\*([A-Za-z][\w-]*)\*\*", passage)}
    plain = {m for m in members if "-" in m
             and re.search(rf"(?<![\w-]){re.escape(m)}(?![\w-])", passage, re.I)}
    return (marked & members) | plain


def _router_types() -> set[str]:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^## Type Reference\n(.*?)(?=^## )", text, re.S | re.M)
    assert m, "SKILL.md has no `## Type Reference` section - the router table moved"
    return set(re.findall(r"^\| `([a-z][a-z-]*)` \|", m.group(1), re.M))


def _restatements(text: str, lists: dict[str, tuple[set[str], int]]) -> list[str]:
    found = []
    for passage in _passages(text):
        for label, (members, cap) in lists.items():
            hit = _named(passage, members)
            if len(hit) > cap:
                found.append(f"{label} x{len(hit)}: {passage.strip()[:100]!r}")
    return found


def _outside_adrs(text: str) -> str:
    """`text` without its ADR sections: each runs from its heading to the next heading at the
    same or a higher level."""
    kept, pos, skip = [], 0, None
    for m in _HEADING.finditer(text):
        level = len(m.group(1))
        if skip is not None and level > skip:
            continue
        if skip is None:
            kept.append(text[pos:m.start()])
        skip = level if _ADR.search(m.group(2)) else None
        pos = m.start()
    if skip is None:
        kept.append(text[pos:])
    return "".join(kept)


def _census_blanked(text: str, doc: Path | None) -> str:
    """`text` with every claim `doc_freshness`'s census checks blanked out, when `doc` is the
    document the census reads. Both the claim patterns and the document come from the reader
    itself, so a census claim added or dropped there moves this exemption with it (D0266)."""
    df = _mod("doc_freshness")
    census_doc = inspect.signature(df.census_claims).parameters["doc"].default
    if doc is None or doc.resolve() != (REPO / census_doc).resolve():
        return text
    body = df._current_body(text)
    for pattern in df._CENSUS_CLAIMS.values():
        body = pattern.sub(lambda m: " " * len(m.group(0)), body)
    return body + text[len(body):]


def _counts(text: str, doc: Path | None = None) -> list[str]:
    """The component counts `text` states outside its Revision History, its ADRs and the
    claims the census reads."""
    body = _outside_adrs(_live(_census_blanked(text, doc)))
    return [m.group(0) for m in _COUNT.finditer(body)]


class SpecRestatementTests(unittest.TestCase):

    def _lists(self) -> dict[str, tuple[set[str], int]]:
        types = _router_types()
        lists = {"gate.DEFAULT_CHECKS": (set(_mod("gate").DEFAULT_CHECKS), MAX_NAMED),
                 "reconcile.DRIFT_KINDS": (set(_mod("reconcile").DRIFT_KINDS), MAX_NAMED),
                 "SKILL.md Type Reference": (types, int(len(types) * TYPES_SHARE))}
        for label, (members, _) in lists.items():
            self.assertGreater(len(members), 10, f"{label} parsed to almost nothing")
        return lists

    def test_the_trd_enumerates_no_list_the_code_derives(self) -> None:
        """AC1. MUTANTS: put the twelve-lane sentence, the forty-type run or the drift-kind run
        back; drop the pointer at the code that holds the list; read only backticked names."""
        lists = self._lists()
        trd = TRD.read_text(encoding="utf-8")
        self.assertEqual([], _restatements(trd, lists),
                         "the TRD restates a list the code holds - name the code instead")
        live = _live(trd)
        for pointer in ("gate.DEFAULT_CHECKS", "reconcile.DRIFT_KINDS", "Type Reference"):
            self.assertIn(pointer, live, f"the TRD no longer names {pointer} as the list")
        # The discriminator on a synthetic passage, so a reader that sees nothing cannot pass.
        lanes = lists["gate.DEFAULT_CHECKS"][0]
        self.assertEqual(3, len(_named("It runs **conformance**, `Window` and duplicate-id.",
                                       lanes & {"conformance", "window", "duplicate-id"})))
        self.assertTrue(_restatements("| lanes | `reconcile`, `validate`, `integrity` |\n",
                                      lists))
        self.assertEqual([], _restatements("Runs `reconcile` and `validate`.\n", lists))

    def test_no_spec_states_a_component_count(self) -> None:
        """AC2. MUTANTS: restore "(6 modules)", "well over 2,500 tests" or the TSD's "90+
        modules"; restore a `measured:` marker; allow one qualifying word only; skip no ADR, or
        every ADR-like heading's whole document; exempt a census claim by a hand list."""
        for path in (TRD, TSD):
            text = path.read_text(encoding="utf-8")
            with self.subTest(spec=path.name):
                self.assertEqual([], _counts(text, path), f"{path.name} states a component count")
                self.assertIsNone(_MEASURED.search(text),
                                  f"{path.name} carries a `measured:` marker nothing reads")
        for claim in ("the 60+ scripts", "(6 modules)", "well over 2,500 tests",
                      "across 90+ modules", "a six-module `lib/`", "(40+ files)", "~20 files",
                      "a 2000-plus-test run", "(40+ help files)", "70+ shipped Python scripts"):
            with self.subTest(claim=claim):
                self.assertTrue(_counts(f"Intro {claim} here.\n"), f"{claim!r} is not seen")
        self.assertEqual([], _counts("Body.\n\n## Revision History\n\nWas 58 scripts.\n"))
        # An ADR's counts stay, and only the ADR's: the section after it is read again.
        adr = ("## 11. Architecture Decision Records\n\n### ADR-001: Router\n\n"
               "Large (50+ reference files, 40+ help files).\n\n#### Consequences\n\n"
               "Still 60+ scripts.\n\n## 12. Next\n\n")
        self.assertEqual([], _counts(adr))
        self.assertEqual(["90+ modules"], _counts(adr + "Across 90+ modules.\n"))
        # A claim the census reads stays in the document it reads, and nowhere else.
        census = "Covers the 60+ scripts, (40+ help files) and 70+ shipped Python scripts.\n"
        self.assertEqual(["70+ shipped Python scripts"], _counts(census, TRD))
        self.assertEqual(3, len(_counts(census, TSD)))

    def test_no_stamp_names_a_deleted_pin(self) -> None:
        """AC3. MUTANTS: restore a pin module; leave one criterion's `Verify:` naming it;
        retire one without its `Verified: manual` stamp."""
        for name in DELETED:
            self.assertFalse((REPO / "tools" / "tests" / f"{name}.py").exists(),
                             f"{name}.py still exists")
        live, retired = [], 0
        for path in sorted((REPO / "sdlc-studio").rglob("*.md")):
            if ".local" in path.parts:
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(lines):
                if "**Verify:**" in line and any(n in line for n in DELETED):
                    live.append(f"{path.relative_to(REPO)}:{i + 1}")
                if RETIRED_VERIFY.search(line):
                    stamp = next((ln for ln in lines[i + 1:i + 3] if "Verified:" in ln), "")
                    self.assertRegex(stamp, RETIRED_STAMP,
                                     f"{path.name}:{i + 1} is retired without its stamp")
                    retired += 1
        self.assertEqual([], live, "a criterion's selector still names a deleted pin")
        self.assertTrue(retired, "no criterion reads `retired by US0933` - the reader saw nothing")

    def test_the_tsd_test_levels_still_drive_the_strategy(self) -> None:
        """AC4, over a copy of the real TSD in a fixture root so the unit is hermetic.
        MUTANTS: drop `## Test Levels`; rename it; strip the backticked paths from its levels."""
        sprint = _mod("sprint")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / "tsd.md").write_text(TSD.read_text(encoding="utf-8"),
                                                         encoding="utf-8")
            (root / "sdlc-studio" / "stories" / "US0001-touches-sprint.md").write_text(
                "# US0001: touches sprint\n\n> **Status:** Draft\n"
                "> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py\n",
                encoding="utf-8")
            levels = sprint.tsd_levels(root)
            self.assertTrue(any(paths for paths in levels.values()),
                            "no TSD test level carries a path")
            strategy = sprint.test_strategy(root, ["US0001"])
            self.assertTrue(strategy["available"], strategy.get("why"))
            self.assertTrue(strategy["units"].get("US0001"),
                            f"a unit affecting sprint.py owes no proof band: {strategy}")


if __name__ == "__main__":
    unittest.main()
