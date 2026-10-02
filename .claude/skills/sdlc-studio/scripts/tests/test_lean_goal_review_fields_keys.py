"""BG0914: `goal-review --fields-file` help names the seat keys the code reads.

The help showed only `{"seats": [{...}]}` while the flag form documents a positional
`role|achievable|...` order, so an agent writing the document keyed each seat `role` and the
seat name was lost: the code reads `seat`. The help now names each seat key; no validation or
refusal is added.

Driven through `sprint.py goal-review`, the shipped entry point.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

#: The keys `_seat_from_dict` reads from one seat object.
SEAT_KEYS = ("seat", "achievable", "done_means", "one_increment", "note")


def _live(name: str):
    """The module the command resolves at call time (see `test_lean_close._live`)."""
    return sys.modules.get(name) or importlib.import_module(name)


def _sprint(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            rc = _live("sprint").main(list(argv))
        except SystemExit as exc:                 # --help exits through argparse
            rc = exc.code
    return rc, out.getvalue()


def _fields_file_help(text: str) -> str:
    """The `--fields-file` entry of the help, its wrapped lines joined."""
    m = re.search(r"^\s+--fields-file FIELDS\.json\n?(.*?)(?=^\s+--|\Z)", text, re.M | re.S)
    if m is None:
        raise AssertionError(f"no --fields-file entry in:\n{text}")
    return " ".join(m.group(1).split())


class GoalReviewFieldsKeysTests(unittest.TestCase):
    def test_help_names_the_seat_keys(self) -> None:
        """AC1. Each key is matched quoted, as the help writes a key, so the prose words "seat"
        and "note" do not stand in for it. MUTANT: HEAD, whose entry shows only
        `{"seats": [{...}]}`; a help naming `role`, the flag form's word, which the code does not
        read; a help keying "name" in place of "seat"; or one naming no seat key at all."""
        rc, text = _sprint("goal-review", "--help")
        self.assertEqual(0, rc, text)
        entry = _fields_file_help(text)
        for key in SEAT_KEYS:
            with self.subTest(key=key):
                self.assertIn(f'"{key}"', entry)
        self.assertNotRegex(entry, r"\brole\b", entry)

    def test_a_document_keyed_as_the_help_says_records_the_seat(self) -> None:
        """The control: the keys the help names are the keys the code reads. MUTANT: a help
        naming a key `_seat_from_dict` ignores, so the seat name is lost again."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            goal = "the close finishes in one pass"
            doc = root / "fields.json"
            doc.write_text(json.dumps({"goal": goal, "seats": [dict(zip(SEAT_KEYS, (
                "qa", "yes", "one page is signed", "yes", "read it whole")))]}),
                encoding="utf-8")
            rc, out = _sprint("goal-review", "record", "--fields-file", str(doc),
                              "--root", str(root))
            self.assertEqual(0, rc, out)
            rc, out = _sprint("goal-review", "show", "--root", str(root))
            self.assertEqual(0, rc, out)
            self.assertIn("qa", out)
            self.assertIn("one page is signed", out)


if __name__ == "__main__":
    unittest.main()
