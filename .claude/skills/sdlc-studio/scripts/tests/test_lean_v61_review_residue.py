"""BG0936: the v6.1 review residue (D0326, D0333).

Four low findings the v6.1 reviews raised that no unit carried:

- `goal-review record`'s two "no seat" refusals were pinned only on a shared word, so either
  could print the other's text; and a fields-file `seats` entry that is not an object was
  dropped, so `["qa|yes|x|yes"]` was refused as a list that "holds none" (BG0933).
- nothing pinned that the newest transcript is chosen by time rather than by listing order
  (BG0932).
- the goal-note ratio parser backtracked quadratically on a long punctuation run straight
  after a measure name, about 2.5 s on 8,000 characters (BG0922).
- the TRD's `.local` table named writers no reader could find: `project orchestration` and
  `review workflow`, for files the agent writes while running a shipped workflow (US0984).

Each is driven through what the user meets: `sprint.py goal-review record`, the token meter
`run_state.session_tokens`, the real close, and the TRD as committed.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_goal_note_ratio_numeric as numeric  # noqa: E402 - by module, not re-collected
from test_lean_goal_review_fields_keys import _sprint  # noqa: E402

SKILL = Path(__file__).resolve().parents[2]
REPO = Path(__file__).resolve().parents[5]
TRD = REPO / "sdlc-studio" / "trd.md"
SEAT = {"seat": "qa", "achievable": "yes", "done_means": "the page is signed",
        "one_increment": "yes"}


def _local_rows(text: str) -> list[tuple[str, str]]:
    """(file, writer cell) for every row of each table under a heading naming `.local`."""
    parts = re.split(r"(?m)^(#+ .*)$", text)
    rows = []
    for i in range(1, len(parts), 2):
        if ".local" not in parts[i]:
            continue
        for row in parts[i + 1].splitlines():
            cells = row.split("|")
            first = re.fullmatch(r"\s*`([\w.-]+\.\w+)`\s*", cells[1]) if len(cells) > 3 else None
            if first:
                rows.append((first.group(1), cells[2]))
    return rows


class V61ReviewResidueTests(unittest.TestCase):
    setUp = numeric.GoalNoteRatioNumericTests.setUp
    _close = numeric.GoalNoteRatioNumericTests._close
    named = staticmethod(numeric.GoalNoteRatioNumericTests.named)

    def _record(self, root: Path, fields: dict | None, *argv: str) -> tuple[int, str]:
        args = ["goal-review", "record", *argv, "--root", str(root)]
        if fields is not None:
            doc = root / "fields.json"
            doc.write_text(json.dumps(fields), encoding="utf-8")
            args += ["--fields-file", str(doc)]
        return _sprint(*args)

    def test_goal_review_refusals_are_distinct_and_name_a_bad_seat(self) -> None:
        """AC1. MUTANTS: either refusal printing the other's text (BG0933's test, which reads
        only the word 'seats' and the flag, passes both); the filter that drops an entry that
        is not an object, so `["qa|yes|x|yes"]` is refused as holding none and a list of one
        good seat and one string records the good one silently. The control: one good seat
        object still records."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            rc, no_file = self._record(root, None, "--goal", "one page is signed")
            self.assertEqual(2, rc, no_file)
            rc, no_seats = self._record(root, {"goal": "one page is signed", "seats": []})
            self.assertEqual(2, rc, no_seats)
            self.assertIn("pass --seat or a --fields-file 'seats' list", no_file)
            self.assertNotIn("holds none", no_file)
            self.assertIn("the --fields-file 'seats' list holds none and no --seat was given",
                          no_seats)
            self.assertNotIn("pass --seat or", no_seats)

            for seats in (["qa|yes|x|yes"], [SEAT, "qa|yes|x|yes"], [SEAT, 7]):
                with self.subTest(seats=seats):
                    rc, said = self._record(root, {"goal": "one page is signed", "seats": seats})
                    self.assertEqual(2, rc, said)
                    self.assertNotIn("holds none", said)
                    self.assertIn("refused", said)
                    self.assertIn(repr(seats[-1]), said, "the bad entry is not named")
                    self.assertIn("is not an object", said)
            self.assertFalse((root / "sdlc-studio" / ".local" / "goal-review.json").exists(),
                             "a seats list holding a bad entry recorded a round")

            rc, said = self._record(root, {"goal": "one page is signed", "seats": [SEAT]})
            self.assertEqual(0, rc, said)

    def test_the_newest_transcript_is_chosen_by_time(self) -> None:
        """AC2. MUTANTS: the last (or the first) entry in listing order, unsorted; the
        greatest name. The folder lists the newest in the middle and its name sorts first, so
        each of those reads a different file, and each file's total names which one was read."""
        run_state = lean._live("lib.run_state")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            spec = (("b-old", 10, 1_000), ("a-new", 3_000, 3_000), ("c-mid", 200, 2_000))
            files = []
            for name, tokens, mtime in spec:
                f = folder / f"{name}.jsonl"
                f.write_text(json.dumps({"message": {"usage": {"input_tokens": tokens}}}) + "\n",
                             encoding="utf-8")
                os.utime(f, (mtime, mtime))
                files.append(f)
            listing = unittest.mock.patch.object(
                type(folder), "glob",
                lambda self, pattern: iter(files) if self == folder else iter(()))
            with listing:
                got = run_state.session_tokens(tmp, transcripts_dir=folder)
            self.assertEqual(3_000, got.get("tokens"), got)

    def test_the_note_parser_is_linear(self) -> None:
        """AC3. MUTANT: HEAD's pattern, whose lazy run after the name and the punctuation lead
        before the number both claim the same characters, so 8,000 of them straight after
        `tokens` with no ratio after them cost about 2.5 s. Timed around the close's own check,
        in the real close. The control: a wrong ratio earlier in the note is still named, so a
        check that reads nothing also fails."""
        mod = lean._live("sprint")
        real = mod.goal_note_contradiction
        spent: list[float] = []

        def timed(*a, **k):
            t = time.perf_counter()
            try:
                return real(*a, **k)
            finally:
                spent.append(time.perf_counter() - t)

        for i, run in enumerate(("(" * 8_000, "-" * 8_000, ":~" * 4_000)):
            with self.subTest(run=run[:2]), \
                    unittest.mock.patch.object(mod, "goal_note_contradiction", timed):
                spent.clear()
                rc, lines, ratio = self._close(f"long{i}", f"Tokens 1.4x over plan; tokens{run}")
                self.assertEqual("1.7x", ratio, "premise: the filed page derives 1.7x")
                self.assertEqual(0, rc, "\n".join(lines))
                self.assertEqual(1, len(spent), "the close did not check the note")
                self.assertLess(spent[0], 0.25, f"the note check took {spent[0]:.2f}s")
                named = self.named(lines)
                self.assertEqual(1, len(named), lines)
                self.assertIn("1.4x", named[0])

    def test_every_local_row_has_a_writer(self) -> None:
        """AC4. MUTANTS: HEAD's rows for project-state.json and review-queue.json, whose writer
        cells (`project orchestration`, `review workflow`) name nothing that writes them; a
        writer cell naming a script or workflow page that never mentions the file. A row's
        writer is a backticked shipped script whose source names the file, or the backticked
        reference page whose workflow the agent runs and which names the file."""
        rows = _local_rows(TRD.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(rows), 10, "premise: the TRD's .local table moved")
        scripts = {p.name: p for p in (SKILL / "scripts").rglob("*.py")
                   if "tests" not in p.parts}
        pages = {p.name: p for p in list(SKILL.glob("reference-*.md"))
                 + list((SKILL / "help").glob("*.md"))}
        for name, writer in rows:
            with self.subTest(file=name):
                cited = re.findall(r"`([\w/.-]+\.(?:py|md))`", writer)
                sources = [scripts.get(Path(c).name) or pages.get(Path(c).name) for c in cited]
                self.assertTrue(cited and all(sources),
                                f"{name}: the writer cell {writer.strip()!r} names no shipped "
                                f"script or workflow page")
                self.assertTrue(any(name in s.read_text(encoding="utf-8") for s in sources),
                                f"{name}: nothing the writer cell names mentions the file")


if __name__ == "__main__":
    unittest.main()
