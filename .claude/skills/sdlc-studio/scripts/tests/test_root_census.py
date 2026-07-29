"""Census guard: every script in the family carries one root-resolution classification.

The classification is MEASURED off the shipped scripts, never read from a list:
a script declares `--root` when its parser or its source says so, and it is
`anchored` only when a call site of `resolve_root` resolves to the shared
implementation in `lib/sdlc_md.py` (checked by object identity, not by name).
The recorded census is then held against that measurement, so a record claiming
an anchor it does not have fails, and a script added to the family with no entry
fails too - it cannot join unclassified.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
REPO = SCRIPTS.parents[3]
RECORD = REPO / "sdlc-studio" / "reviews" / "root-census.md"

# This module globs the whole artefact workspace to answer "does an artefact with this id
# exist" (`_artefact_on_disk`). That is a read of the tree's SHAPE: a file appearing, vanishing
# or being renamed changes the answer, and the words inside a file never can. Declared so
# `gate.listing_only_paths` can tell the two apart - without it this one glob made every
# artefact commit in the repo pay for both unit suites. The narrower reads this module also
# performs (RECORD, below) are measured separately and stay fully relevant.
#
# `ids` narrows it the rest of the way. The glob only ever asks about the follow-up ids the
# census record names, so every OTHER artefact filed under the workspace - which is most of
# what a sprint close writes - cannot change this module's answer. Left as a bare directory,
# one id's worth of dependency made every filing in the repository structural.
# `DeclaredIdsCoverTheCensusTests` holds this list against the record, so an id added to the
# census and not to this line fails rather than going quietly unprotected.
GATE_LISTING_ONLY = ({"path": "sdlc-studio", "ids": ("BG0288",)},)
# The census is a fact about the skill's OWN source tree, so it is only meaningful where that
# tree is under development - detected by the repo's guard directory sitting beside the
# workspace. A project that merely installed the skill has no census to hold, and holding it
# to one would fail a suite it never authored.
DEV_TREE = (REPO / "tools" / "check_budgets.py").exists()

sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402

CLASSES = ("anchored", "unanchored", "non-root")
_DECLARES_ROOT = re.compile(r"add_global_root\s*\(|add_argument\(\s*[\"']--root[\"']")
_RESOLVE_CALL = re.compile(r"(?:(\w+)\.)?resolve_root\s*\(")
_ARTEFACT_ID = re.compile(r"\b(?:BG|CR|RFC|US|EP)-?\d{3,4}\b")
_ROW = re.compile(r"^\|(?P<cells>.+)\|\s*$")
#: A summary row of the counts block, e.g. `| anchored | 10 |` or `| **total** | **69** |`.
_COUNT_ROW = re.compile(r"^\|\s*\**(?P<label>[a-z-]+)\**\s*\|\s*\**(?P<n>\d+)\**\s*\|\s*$")
#: A non-root reason claiming the script has no command-line surface at all.
_CLAIMS_NO_CLI = re.compile(r"no CLI", re.I)
#: A non-root reason claiming the only surface is a `--help` stub with no verbs behind it.
_CLAIMS_HELP_STUB = re.compile(r"`--help` stub")
#: An option a non-root reason names as the path surface the script takes instead of `--root`.
_NAMED_OPTION = re.compile(r"`(--[a-z][a-z-]*)`")


def _load(path: Path):
    """Import a shipped script under a private name, with its import-time output swallowed so a
    green suite prints nothing."""
    spec = importlib.util.spec_from_file_location("census_" + path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod


def _parser_declares_root(mod) -> bool:
    build = getattr(mod, "build_parser", None)
    if build is None:
        return False
    try:
        parser = build()
    except Exception:  # noqa: BLE001 - build_parser must not need runtime state; treat as silent
        return False
    stack = [parser]
    while stack:
        p = stack.pop()
        for action in p._actions:
            if isinstance(action, argparse._SubParsersAction):
                stack.extend(action.choices.values())
            elif "--root" in action.option_strings:
                return True
    return False


def _resolves_through_shared(mod, src: str) -> bool:
    """True when some `resolve_root(...)` call site in this source binds the SHARED resolver.

    Identity against `sdlc_md.resolve_root` is the whole point: a script may reach it bare (it
    aliased the name), through `sdlc_md.`, or through another module that aliased it, and any
    of those is anchored. A same-named local helper is not.
    """
    for m in _RESOLVE_CALL.finditer(src):
        qualifier = m.group(1)
        target = mod if qualifier is None else getattr(mod, qualifier, None)
        if target is None:
            continue
        if getattr(target, "resolve_root", None) is sdlc_md.resolve_root:
            return True
    return False


def measure() -> dict[str, str]:
    """Classify every shipped script by how it resolves the project root."""
    out: dict[str, str] = {}
    for path in sorted(SCRIPTS.glob("*.py")):
        if path.name == "__init__.py":
            continue
        src = path.read_text(encoding="utf-8")
        try:
            mod = _load(path)
        except Exception:  # noqa: BLE001 - a script that will not import cannot be classified
            continue
        declares = bool(_DECLARES_ROOT.search(src)) or _parser_declares_root(mod)
        if not declares:
            out[path.name] = "non-root"
        else:
            out[path.name] = "anchored" if _resolves_through_shared(mod, src) else "unanchored"
    return out


def read_record() -> list[tuple[str, str, str]]:
    """(script, classification, reason) for every row of the recorded census."""
    rows: list[tuple[str, str, str]] = []
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        m = _ROW.match(line.strip())
        if not m:
            continue
        cells = [c.strip().strip("`") for c in m.group("cells").split("|")]
        if len(cells) < 3:
            continue
        script = cells[0]
        if not script.endswith(".py"):
            continue
        rows.append((script, cells[1].strip("`"), cells[2]))
    return rows


def read_counts() -> dict[str, int]:
    """The recorded summary counts, `{classification: n}` plus `total`.

    These were previously never parsed, so the block could say anything - and did: it claimed
    5 anchored / 59 unanchored while the family measured otherwise, and no guard noticed. A
    count nobody reads is a claim nobody checks.
    """
    counts: dict[str, int] = {}
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        m = _COUNT_ROW.match(line.strip())
        if m and (m.group("label") in CLASSES or m.group("label") == "total"):
            counts[m.group("label")] = int(m.group("n"))
    return counts


def _artefact_on_disk(id_: str) -> bool:
    stem = sdlc_md.norm_id(id_)
    workspace = REPO / "sdlc-studio"
    return any(p.is_file() for p in workspace.glob(f"**/{stem}*.md"))


@unittest.skipUnless(DEV_TREE, "no skill source tree here, so there is no census to hold")
class RootCensusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(RECORD.exists(), f"the census record is missing: {RECORD}")
        self.measured = measure()
        self.rows = read_record()

    def test_every_root_declaring_script_is_classified_with_a_reason(self) -> None:
        self.assertTrue(self.measured, "the measurement found no scripts at all")
        recorded = [r[0] for r in self.rows]
        self.assertEqual(len(recorded), len(set(recorded)),
                         "a script is recorded twice, so it carries more than one classification")
        missing = sorted(set(self.measured) - set(recorded))
        self.assertFalse(missing, f"in the family but absent from the census: {missing}")
        stale = sorted(set(recorded) - set(self.measured))
        self.assertFalse(stale, f"recorded but no longer in the family: {stale}")
        for script, klass, reason in self.rows:
            with self.subTest(script=script):
                self.assertIn(klass, CLASSES, f"{script}: '{klass}' is not a classification")
                self.assertTrue(reason, f"{script}: classified with no reason")
                # EVERY row is held to the measurement, in both directions. The record used to
                # waive a row still saying `unanchored` after someone anchored the script, as
                # stale-not-false. That waiver is how the counts drifted unnoticed: five scripts
                # were anchored from a parallel branch, five rows kept saying otherwise, and the
                # guard called it acceptable. A census that tolerates a false half is not a
                # census, so a stale row now fails and has to be re-measured.
                self.assertEqual(
                    self.measured[script], klass,
                    f"{script}: recorded '{klass}' but measures '{self.measured[script]}'")

    def test_an_unanchored_entry_needs_a_fix_or_a_filed_follow_up(self) -> None:
        for script, klass, reason in self.rows:
            if klass != "unanchored":
                continue
            with self.subTest(script=script):
                if self.measured.get(script) == "anchored":
                    continue  # fixed since the record was written
                ids = _ARTEFACT_ID.findall(reason)
                self.assertTrue(
                    ids,
                    f"{script}: unanchored and names no follow-up - silence is not a "
                    f"classification")
                self.assertTrue(
                    any(_artefact_on_disk(i) for i in ids),
                    f"{script}: names {ids}, none of which exists on disk")

    def test_the_summary_counts_are_the_measured_counts(self) -> None:
        """The counts block is parsed and held, not decoration beside the table."""
        counts = read_counts()
        self.assertTrue(counts, "the census records no summary counts to check")
        measured = Counter(self.measured.values())
        for klass in CLASSES:
            with self.subTest(count=klass):
                self.assertIn(klass, counts, f"the summary block omits '{klass}'")
                self.assertEqual(counts[klass], measured[klass],
                                 f"the summary says {counts[klass]} {klass}, the family "
                                 f"measures {measured[klass]}")
        self.assertEqual(counts.get("total"), len(self.measured),
                         "the recorded total is not the number of scripts measured")

    def test_a_non_root_reason_is_true_of_the_code(self) -> None:
        """A `non-root` row states WHY the script has no project-root surface. That reason is
        held to the source, so 'deliberately out of scope' cannot become a place to park a
        script nobody wants to classify.

        Three checkable shapes, one per row: no command line at all; a `--help` stub with no
        verbs behind it; or an explicit path option named in the reason and declared by the
        script.
        """
        for script, klass, reason in self.rows:
            if klass != "non-root":
                continue
            with self.subTest(script=script):
                src = (SCRIPTS / script).read_text(encoding="utf-8")
                dispatches = "set_defaults(func=" in src
                has_main = "\ndef main(" in src
                if _CLAIMS_NO_CLI.search(reason):
                    self.assertFalse(
                        has_main,
                        f"{script}: recorded as having no CLI, but it defines main()")
                elif _CLAIMS_HELP_STUB.search(reason):
                    self.assertTrue(has_main,
                                    f"{script}: recorded as a `--help` stub, but defines no main()")
                    self.assertFalse(
                        dispatches,
                        f"{script}: recorded as a `--help` stub, but it dispatches to verbs")
                else:
                    named = _NAMED_OPTION.findall(reason)
                    self.assertTrue(
                        named,
                        f"{script}: non-root with a command line, and the reason names no path "
                        f"option it takes instead of --root")
                    for opt in named:
                        self.assertIn(f'"{opt}"', src,
                                      f"{script}: the census names {opt}, which it never declares")


@unittest.skipUnless(DEV_TREE, "no skill source tree here, so there is no census to hold")
class DeclaredIdsCoverTheCensusTests(unittest.TestCase):
    """US0554. `GATE_LISTING_ONLY` now names the ids this module's glob depends on, which makes
    every OTHER filing under the workspace irrelevant to it. That is only safe while the list
    stays true: an id added to the census record and not to the declaration would be an id
    whose artefact could vanish without the suite that checks it ever running. Held here so the
    omission fails loudly rather than becoming a silent hole in the narrowing."""

    @staticmethod
    def _declared_ids() -> set:
        ids: set = set()
        for entry in GATE_LISTING_ONLY:
            if isinstance(entry, dict):
                ids |= {str(i).replace("-", "").upper() for i in (entry.get("ids") or ())}
        return ids

    @staticmethod
    def _census_ids() -> set:
        """Every artefact id `_artefact_on_disk` can be asked about - the ids named in the
        reason of an unanchored row, which is the only place the glob is reached from."""
        return {i.replace("-", "").upper()
                for _script, klass, reason in read_record() if klass == "unanchored"
                for i in _ARTEFACT_ID.findall(reason)}

    def test_every_census_id_is_named_by_the_declaration(self) -> None:
        missing = sorted(self._census_ids() - self._declared_ids())
        self.assertFalse(
            missing,
            f"the census names {missing}, which GATE_LISTING_ONLY does not: a structural "
            f"change to one of those artefacts would not select this module. Add them to the "
            f"`ids` tuple, or drop the tuple to go back to the whole directory")

    def test_the_declaration_names_no_id_the_census_does_not(self) -> None:
        """The other direction is not a safety hole - a stale id only makes the narrowing less
        effective - but it is how the list rots into decoration nobody trusts."""
        stale = sorted(self._declared_ids() - self._census_ids())
        self.assertFalse(stale, f"declared but the census no longer names it: {stale}")

    def test_the_declaration_actually_narrows_this_module(self) -> None:
        """The point of the whole story, asserted against the real repository: filing an
        artefact this census never asks about must not select this module."""
        sys.path.insert(0, str(SCRIPTS))
        import gate  # noqa: PLC0415 - imported here so the module loads without the skill root
        # The CONTENT readers, from the rule's own subtraction. Deriving this from the raw read
        # map counted a module that only probes the workspace exists, so this test skipped
        # itself on a suspension that had already been repaired.
        readers = gate.content_readers(str(REPO)).get("sdlc-studio", set())
        scopes = gate.listing_only_scopes(str(REPO))
        undeclared = {m for m in readers
                      if "GATE_LISTING_ONLY" not in (REPO / m).read_text(encoding="utf-8")}
        if undeclared:
            # Another module reads this entry for CONTENT without declaring it, so unanimity
            # correctly withholds the narrowing. The declaration is still the right one to
            # hold; the SAVING is suspended, and that is a fact about the repository, not
            # about this module. Filed as a follow-up rather than asserted away.
            self.assertNotIn("sdlc-studio", scopes)
            self.skipTest(f"{sorted(undeclared)} read `sdlc-studio` for content; unanimity "
                          f"withholds the narrowing until each declares or stops reading it")
        self.assertIsNotNone(scopes.get("sdlc-studio"))
        filed = "sdlc-studio/bugs/BG9999-an-artefact-this-census-never-asks-about.md"
        self.assertFalse(gate.is_test_relevant([filed], str(REPO), structural={filed}))


if __name__ == "__main__":
    unittest.main()
