"""BG1412: the builder agent card runs a unit's criteria with `verify_ac.py run --dry-run`.

A plain `verify_ac.py run` writes its results into the unit's own artefact, which the builder
does not stage, so the lane brief has carried `--dry-run` since BG1336. The builder card a lane
is spawned as still told it to run the bare command. These tests read the shipped card and this
repository's installed copy, each on its own, and refuse any `verify_ac` run either names
without `--dry-run`.
"""
# test-census-subject: .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md
from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
REPO = SKILL.parents[2]
CARDS = {"template": SKILL / "templates" / "agents" / "sdlc-builder.md",
         "installed copy": REPO / ".claude" / "agents" / "sdlc-builder.md"}
#: A `verify_ac` run as a card spells it, up to the end of its code span or its sentence.
RUN = re.compile(r"verify_ac(?:\.py)?\s+run\b[^`.;]*")


def bare_runs(text: str) -> tuple[list[str], list[str]]:
    """`(every verify_ac run the text names, those of them without --dry-run)`, read over the
    text with its wrapped lines joined, so a command split across two lines is still one run."""
    runs = [m.group(0).strip() for m in RUN.finditer(" ".join(text.split()))]
    return runs, [r for r in runs if "--dry-run" not in r]


class BuilderDryRunTests(unittest.TestCase):

    def test_each_card_runs_the_criteria_with_dry_run(self) -> None:
        """AC1. MUTANTS: `--dry-run` dropped from either card's run; a second, bare run added to
        either card; the run deleted from a card, so the check would pass on no run at all."""
        for label, path in CARDS.items():
            with self.subTest(card=label):
                self.assertTrue(path.is_file(), f"{path} is missing")
                runs, bare = bare_runs(path.read_text(encoding="utf-8"))
                self.assertTrue(runs, f"{path} names no verify_ac run")
                self.assertEqual([], bare, f"{path} names a verify_ac run without --dry-run")

    def test_the_reader_tells_a_bare_run_from_a_dry_one(self) -> None:
        """AC1, the reader's own controls. MUTANTS: the `--dry-run` match loosened to any text
        holding `dry`; the wrapped lines not joined; the run cut at the first space; the run
        carried past the end of its code span, its sentence or its clause; `.py` required."""
        dry = "Run them (`verify_ac.py run --id <unit>\n  --dry-run`) before you hand back."
        self.assertEqual((["verify_ac.py run --id <unit> --dry-run"], []), bare_runs(dry))
        for text in ("Run them (`verify_ac.py run --id <unit>`) first.",
                     "Run `verify_ac run --id BG0001 --no-dry-run`.",
                     "Run `verify_ac.py run --id BG0001` and `lint --dry-run` after.",
                     "Run verify_ac.py run --id BG0001. Then pass --dry-run to lint.",
                     "Run verify_ac.py run --id BG0001; pass --dry-run to lint."):
            with self.subTest(text=text):
                runs, bare = bare_runs(text)
                self.assertEqual(1, len(runs), runs)
                self.assertEqual(runs, bare, "a bare run read as a dry one")


if __name__ == "__main__":
    unittest.main()
