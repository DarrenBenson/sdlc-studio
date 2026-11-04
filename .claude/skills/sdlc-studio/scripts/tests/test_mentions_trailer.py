"""US1115: a `Mentions:` trailer accounts for an id a commit subject only mentions.

`check-commit-msg --strict` refuses a subject naming several judged ids unless a trailer
accounts for each one. `Refs: <id>` says the id owns the commit's files; `Mentions: <id>` says
it owns none of them. The git leg reads `Refs:` alone, so a mentioned id in a multi-id subject
is attributed no files, by both of the functions that must agree (`_git_touched_by_id` and
`_git_touched_source_files`).
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/engagement_floor.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repos below
import loader  # noqa: E402

ef = loader.load_script("engagement_floor")
SCRIPT = Path(ef.__file__)

SUBJECT_TWO = "feat(US1110): repair the lane, which BG0989 raised"
SUBJECT_THREE = "feat(US1110): repair the lane BG0989 raised, beside BG1000"


def _check_cli(message: str) -> subprocess.CompletedProcess:
    """`engagement_floor.py check-commit-msg --strict` on `message`, the way the hook runs it.
    `--root` names a directory that is not a git repository, so the attribution advisory has
    nothing staged to read and the output is the multi-id rule's alone."""
    with tempfile.TemporaryDirectory() as d:
        msg = Path(d) / "COMMIT_EDITMSG"
        msg.write_text(message, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "check-commit-msg", "--strict", str(msg),
             "--root", d], capture_output=True, text=True, cwd=d, timeout=60)


def _commit_two_files(root: Path, message: str) -> None:
    gitutil.git(["init", "-q"], cwd=root, text=True)
    (root / "src").mkdir()
    for name in ("lane.py", "reader.py"):
        (root / "src" / name).write_text("x = 1\n", encoding="utf-8")
    gitutil.git(["add", "-A"], cwd=root, text=True)
    gitutil.git(["commit", "-q", "-m", message], cwd=root, text=True)


class MentionsTrailerTests(unittest.TestCase):

    def test_a_mentions_trailer_accounts_for_a_mentioned_id(self):
        # AC1. Must fail on: the Mentions reader returning an empty set (the CLI then exits 1),
        # or Mentions lines parsed as Refs (the reader assertions below then differ).
        message = f"{SUBJECT_TWO}\n\nRefs: US1110\nMentions: BG0989\n"
        r = _check_cli(message)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stderr, "")
        self.assertEqual(ef._refs_ids(message), {"US1110"})
        self.assertEqual(ef._mentions_ids(message), {"BG0989"})
        # Positive control: the same message with the `Mentions:` line removed is refused.
        r = _check_cli(f"{SUBJECT_TWO}\n\nRefs: US1110\n")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("trailer: BG0989.", r.stderr)

    def test_a_mentioned_id_is_attributed_no_files(self):
        # AC2. Must fail on: `_refs_ids` also reading `Mentions:` (BG0989 then gets both files).
        # Both functions are asserted, since they must agree. The `Refs: BG0989` leg is the
        # positive control: the same fixture CAN attribute files to BG0989, so the empty set
        # under `Mentions:` is the trailer's doing, not a fixture that cannot see the id.
        files = {"src/lane.py", "src/reader.py"}
        cases = (("Mentions: BG0989", set()), ("Refs: BG0989", files))
        for trailer, bg_files in cases:
            with self.subTest(trailer=trailer), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _commit_two_files(root, f"{SUBJECT_TWO}\n\nRefs: US1110\n{trailer}\n")
                by_id = ef._git_touched_by_id(root)
                self.assertEqual(by_id.get("US1110"), files)
                self.assertEqual(by_id.get("BG0989", set()), bg_files)
                self.assertEqual(ef._git_touched_source_files(root, "US1110"), files)
                self.assertEqual(ef._git_touched_source_files(root, "BG0989"), bg_files)

    def test_an_unaccounted_id_is_named_with_both_remedies(self):
        # AC3. Must fail on: the warning offering only `Refs:`, or one `Mentions:` line counted
        # as accounting for every id (the CLI then exits 0).
        r = _check_cli(f"{SUBJECT_THREE}\n\nRefs: US1110\nMentions: BG0989\n")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("trailer: BG1000.", r.stderr)
        self.assertNotIn("US1110", r.stderr)
        self.assertNotIn("BG0989", r.stderr)
        self.assertIn("`Refs: BG1000` if it owns the commit's files", r.stderr)
        self.assertIn("`Mentions: BG1000` if it owns none of them", r.stderr)

    def test_mentions_reads_the_refs_grammar(self):
        # The help and reference say `Mentions:` takes the grammar `Refs:` does. Sampled: a
        # comma list, a whitespace list, repeated lines, a lowercase key, a dashed spelling and
        # an indented line. A non-id word on the line names nothing.
        cases = {
            "Mentions: BG0989, BG1000": {"BG0989", "BG1000"},
            "Mentions: BG0989 BG1000": {"BG0989", "BG1000"},
            "Mentions: BG0989\nMentions: BG1000": {"BG0989", "BG1000"},
            "mentions: BG0989": {"BG0989"},
            "MENTIONS: BG0989": {"BG0989"},
            "Mentions: BG-0989": {"BG0989"},
            "  Mentions: BG0989": {"BG0989"},
            "Mentions: the lane": set(),
            "See Mentions: BG0989": set(),
        }
        for body, want in cases.items():
            with self.subTest(body=body):
                self.assertEqual(ef._mentions_ids(f"{SUBJECT_TWO}\n\n{body}\n"), want)
                self.assertEqual(ef._refs_ids(f"{SUBJECT_TWO}\n\n{body}\n"), set())

    def test_an_id_in_both_trailers_keeps_its_files(self):
        # `Refs:` wins over `Mentions:` for one id: the git leg reads `Refs:` alone.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _commit_two_files(root, f"{SUBJECT_TWO}\n\nRefs: US1110, BG0989\nMentions: BG0989\n")
            files = {"src/lane.py", "src/reader.py"}
            self.assertEqual(ef._git_touched_by_id(root).get("BG0989"), files)
            self.assertEqual(ef._git_touched_source_files(root, "BG0989"), files)

    def test_a_commit_whose_every_id_is_a_mention_is_skipped(self):
        # Disclosed, not refused: the rule passes it and the floor attributes it to no id.
        message = f"{SUBJECT_TWO}\n\nMentions: US1110, BG0989\n"
        self.assertEqual(_check_cli(message).returncode, 0)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _commit_two_files(root, message)
            self.assertEqual(ef._git_touched_by_id(root), {})
            for rid in ("US1110", "BG0989"):
                self.assertEqual(ef._git_touched_source_files(root, rid), set())

    def test_a_solo_subject_still_gives_a_mentioned_id_its_files(self):
        # The disclosed limit: the trailer is read by the rule, never by the attribution, so a
        # one-id subject attributes its files to every id the message names, as before.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _commit_two_files(root, "feat(US1110): repair the lane\n\nMentions: BG0989\n")
            files = {"src/lane.py", "src/reader.py"}
            self.assertEqual(ef._git_touched_by_id(root).get("BG0989"), files)
            self.assertEqual(ef._git_touched_source_files(root, "BG0989"), files)


if __name__ == "__main__":
    unittest.main()
