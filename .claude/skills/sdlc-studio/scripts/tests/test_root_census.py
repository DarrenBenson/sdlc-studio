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
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
REPO = SCRIPTS.parents[3]
RECORD = REPO / "sdlc-studio" / "reviews" / "root-census.md"
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
                if klass in ("anchored", "non-root"):
                    # A claim of a fix, or of being out of scope, is held to the measurement.
                    # The reverse is not: a record still saying `unanchored` after someone
                    # anchored the script is stale, not false, and the follow-up check below
                    # already passes it.
                    self.assertEqual(
                        self.measured[script], klass,
                        f"{script}: recorded '{klass}' but measures "
                        f"'{self.measured[script]}'")

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


if __name__ == "__main__":
    unittest.main()
