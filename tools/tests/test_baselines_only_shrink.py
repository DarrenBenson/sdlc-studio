"""A grandfathering baseline may only SHRINK (BG0367).

`validate.py` documents both baselines as "captured from the checker's own output, never
hand-written, and removing a line is one-way, so the recorded count can only fall" - and
nothing enforced it. The baselines are read as plain sets, so adding an id to one is a
supported way to bypass the floor entirely: the exemption they exist to TIME-BOX becomes
permanent and extensible, which is the opposite of a baseline.

Compared against the committed version in git, which is where the previous state lives - a
high-water mark written into the repo would itself be a number someone could edit.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASELINES = ("sdlc-studio/.criteria-baseline.txt", "sdlc-studio/.placeholder-baseline.txt",
             # A JSON baseline the line-splitting reader below could not parse, so it was left
             # out of the tuple entirely and NOTHING held it to shrink-only. A baseline nobody
             # ratchets is a permanent, extensible exemption - the opposite of a baseline.
             "sdlc-studio/.verify-lint-baseline.json",
             "sdlc-studio/.unjudged-flags-baseline.txt")


def _entries(text: str) -> set[str]:
    """The baseline's entries, whatever shape the file is written in.

    A line-splitting reader over a JSON document returns its punctuation as "entries", which
    compares equal to itself and to nothing useful - so the guard would have passed while
    ratcheting nothing. The format is read from the content rather than the extension, because
    a file renamed is a file this guard would otherwise stop understanding.
    """
    stripped = text.lstrip()
    if stripped.startswith("{"):
        import json
        try:
            data = json.loads(text)
        except ValueError:
            return set()
        groups = data.get("groups") if isinstance(data, dict) else None
        if isinstance(groups, dict):
            return set(groups)
        return {str(k) for k in data} if isinstance(data, dict) else set()
    return {ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")}


def _committed(rel: str, ref: str = "HEAD") -> set[str] | None:
    """The baseline as `ref` holds it, or None when `ref` does not carry the file.

    None is "no previous state to compare against" - a baseline being introduced, which is the
    one commit where growth is legitimate."""
    out = subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{rel}"],
                         capture_output=True, text=True, check=False)
    return _entries(out.stdout) if out.returncode == 0 else None


class BaselinesOnlyShrinkTests(unittest.TestCase):
    def test_no_baseline_has_grown_against_the_last_commit(self) -> None:
        checked = 0
        for rel in BASELINES:
            path = REPO / rel
            if not path.is_file():
                continue
            previous = _committed(rel)
            if previous is None:
                continue        # being introduced: no previous state to shrink from
            checked += 1
            added = sorted(_entries(path.read_text(encoding="utf-8")) - previous)
            with self.subTest(baseline=rel):
                self.assertFalse(
                    added,
                    f"{rel} gained {added}. A baseline grandfathers what ALREADY existed when a "
                    f"rule was introduced; adding to it exempts new work, which turns a "
                    f"time-boxed exemption into a permanent and extensible one. Fix the unit, "
                    f"or record the decision deliberately rather than in a baseline file")
        self.assertGreater(checked, 0,
                           "no baseline was compared at all - the files are missing or git "
                           "could not read them, so a clean result here is the check failing")

    def test_the_comparison_reads_the_committed_state(self) -> None:
        """Guard the guard: if `git show` stops resolving, every assertion above passes vacuously
        by taking the `previous is None` branch."""
        for rel in BASELINES:
            if (REPO / rel).is_file():
                with self.subTest(baseline=rel):
                    self.assertIsNotNone(
                        _committed(rel),
                        f"git cannot read {rel} at HEAD, so the shrink check is inert")


class JsonBaselineReaderTests(unittest.TestCase):
    """A JSON baseline is parsed, not line-split.

    `.verify-lint-baseline.json` was absent from BASELINES because the reader could not have
    parsed it if added - so nothing held it to shrink-only, and a permanent extensible
    exemption sat where a ratcheted one was documented.
    """

    def test_the_json_baseline_is_parsed_into_real_entries(self) -> None:
        """MUTANT: restore the line-splitting reader for every file.

        Asserted against the LINE COUNT, because that is the failure mode: line-splitting a
        JSON document returns its punctuation, which compares equal to itself and ratchets
        nothing while the guard reports green.
        """
        text = (REPO / "sdlc-studio" / ".verify-lint-baseline.json").read_text(encoding="utf-8")
        entries = _entries(text)
        self.assertTrue(entries, "the JSON baseline parsed to nothing")
        line_split = {ln.strip() for ln in text.splitlines()
                      if ln.strip() and not ln.startswith("#")}
        self.assertNotEqual(entries, line_split,
                            "the reader is still line-splitting the JSON document")
        for entry in entries:
            self.assertNotIn('"', entry,
                             f"{entry!r} is a fragment of JSON, not a baseline entry")

    def test_every_declared_baseline_is_readable(self) -> None:
        """MUTANT: add a baseline to the tuple that the reader cannot parse.

        A file in BASELINES that parses to an empty set passes every comparison and holds
        nothing - which is exactly the state this bug found.
        """
        for rel in BASELINES:
            path = REPO / rel
            if not path.is_file():
                continue
            with self.subTest(baseline=rel):
                self.assertTrue(_entries(path.read_text(encoding="utf-8")),
                                f"{rel} is declared a baseline but parses to no entries, so "
                                f"it ratchets nothing")


if __name__ == "__main__":
    unittest.main()
