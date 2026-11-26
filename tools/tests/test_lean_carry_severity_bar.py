"""This repository's `review.blocking_priority` stays in step with the release bar it is cut to.

The shipped skill reads a project's release bar from `review.blocking_priority`: the close's
goal judgement rules an open defect at or above it BLOCKING, and the severity a unit carried at
the review cap is filed at (`critic.carry_severity`) reads it too. This repository's bar is the
BARS row in `tools/known_issues.py` that the known-issues page names, which no shipped script can
read. Left apart, the two drift: with
the setting unset it reads `high`, so a carry here was filed at Medium while the v6.5 bar barred
Medium, and a unit whose own criterion checks that bar could not close its own carry.

The bar is read by the name the heading of `docs/known-issues.md` gives it
(`known_issues.held_to`), never by its position in BARS: a bar recorded above it in BARS moves
this pin only once the page is re-cut to name that bar, and until then the pin stays on the bar
the page names.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import known_issues as ki  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

CONFIG_REL = "sdlc-studio/.config.yaml"
#: The bug severities, the vocabulary both the bar and the filer use.
SEVERITIES = ("Critical", "High", "Medium", "Low")
#: The setting's own line, which the drift probe removes from a copy of the config.
_SETTING = re.compile(r"^\s*blocking_priority:.*\n", re.M)
UNIT = "US0001"


def _barred_by_setting(root: Path) -> set[str]:
    """The severities `review.blocking_priority` under `root` bars, in the bug vocabulary."""
    floor = critic.blocking_priorities(root)
    return {s for s in SEVERITIES if s.lower() in floor}


class CarrySeverityBarTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        transcripts = self.tmp / "transcripts"
        transcripts.mkdir()
        saved = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = str(transcripts)
        self.addCleanup(lambda: os.environ.pop(run_state.TRANSCRIPTS_ENV, None) if saved is None
                        else os.environ.__setitem__(run_state.TRANSCRIPTS_ENV, saved))

    def test_the_setting_bars_what_the_named_bar_bars(self) -> None:
        """The setting bars exactly the severities the bar the page names bars. MUTANTS: the
        setting removed (reads `high`, barring no Medium); set to `high`; set to `low` (bars Low
        too, so the close's goal judgement would rule every open Low BLOCKING)."""
        named = ki._named_bar(REPO)
        self.assertIsNotNone(named, "premise: docs/known-issues.md names no bar")
        self.assertEqual(set(ki.held_to(REPO)), _barred_by_setting(REPO),
                         f"review.blocking_priority in {CONFIG_REL} is out of step with the "
                         f"{named[1]} bar the known-issues page names")

    def test_a_new_bar_moves_the_pin_only_once_the_page_names_it(self) -> None:
        """A bar recorded in BARS above the one the page names, barring only Critical and High,
        leaves the pin on the named bar; a page re-cut to name the new bar moves the pin to it,
        and this repository's setting is then out of step. A bar read by its position in BARS,
        the first row, fails the first assertion."""
        page = (REPO / ki.PAGE_REL).read_text(encoding="utf-8")
        named = ki._BAR_HEADING.search(page)
        self.assertIsNotNone(named, "premise: docs/known-issues.md names no bar")
        major, minor = int(named[1]), int(named[2]) + 1
        newer = ((major, minor), f"v{major}.{minor}", ki.BARRED, None, "a newer bar\n")
        recut = self.tmp / "recut"
        (recut / "docs").mkdir(parents=True)
        (recut / ki.PAGE_REL).write_text(
            ki._BAR_HEADING.sub(f"## The bar v{major}.{minor} is held to", page, count=1),
            encoding="utf-8")
        with unittest.mock.patch.object(ki, "BARS", (newer,) + ki.BARS):
            self.assertEqual(set(ki.held_to(REPO)), _barred_by_setting(REPO))
            self.assertEqual(ki.BARRED, ki.held_to(recut))
            self.assertNotEqual(set(ki.held_to(recut)), _barred_by_setting(REPO))

    def _fixture(self, name: str, config: str) -> Path:
        """A project holding this repository's config and known-issues page, one unit in Review
        and an open run holding it."""
        root = self.tmp / name
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / CONFIG_REL).write_text(config, encoding="utf-8")
        shutil.copy(REPO / ki.PAGE_REL, root / ki.PAGE_REL)
        (root / "src").mkdir()
        (root / "src" / "unit.py").write_text("x = 1\n", encoding="utf-8")
        (root / "sdlc-studio" / "stories" / f"{UNIT}-a-unit.md").write_text(
            f"# {UNIT}: a unit\n\n> **Status:** Review\n> **Epic:** EP0001\n> **Points:** 2\n"
            "> **Affects:** src/unit.py\n\n## Acceptance Criteria\n\n"
            "- [ ] **AC1** the parser keeps every row\n"
            "  - **Verify:** pytest tests/test_unit.py::UnitTests::test_rows_kept\n",
            encoding="utf-8")
        run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
        return root

    def _carry(self, root: Path) -> tuple[str, str]:
        """Carry the unit at the cap: the carried bug's Severity and its text."""
        bug = critic.carry_at_cap(root, UNIT, {"issues": "[new] the parser drops a row",
                                              "round": 2, "reviewer": "rev-a"})
        self.assertTrue(bug, "premise: no open run held the unit, so nothing was carried")
        text = sdlc_md.read_text_safe(sdlc_md.find_by_id(root, bug)[0])
        return sdlc_md.extract_field(text, "Severity"), text

    def test_a_carry_here_is_filed_at_a_level_this_bar_allows(self) -> None:
        """Carried at the cap under this repository's own config, the bug is filed at Low with
        the rule that set it, and the bar the page names finds nothing barred open. The control:
        the same config with the setting removed files Medium, which that bar reports barred.
        MUTANTS: as above; the carry's severity read from anything but the setting."""
        config = (REPO / CONFIG_REL).read_text(encoding="utf-8")
        here = self._fixture("here", config)
        severity, text = self._carry(here)
        self.assertEqual("Low", severity, text)
        self.assertIn("Filed at Low rather than the carry's default Medium: the release bar "
                      "(`review.blocking_priority`) bars Medium", text)
        self.assertEqual({}, ki.barred_open(here))
        unset = self._fixture("unset", _SETTING.sub("", config))
        severity, text = self._carry(unset)
        self.assertEqual("Medium", severity, text)
        self.assertEqual(["Medium"], list(ki.barred_open(unset).values()))


if __name__ == "__main__":
    unittest.main()
