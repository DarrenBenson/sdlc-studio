"""US0390: the no-batch-selected error on the plan's hottest path shows a usable example status
per selector, so the first retry is a working invocation rather than two more failed round-trips."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "sprint.py"
sys.path.insert(0, str(SCRIPT.parent))
from lib import sdlc_md  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("sprint", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod


class BatchSelectionError(unittest.TestCase):
    def test_message_shows_example_status_per_selector(self) -> None:
        msg = _load().batch_selection_message()
        # each status-taking selector appears WITH an example value, not bare
        self.assertIn("--bugs Open", msg)
        self.assertIn("--crs Proposed", msg)
        self.assertIn("--stories Ready", msg)

    def test_valid_status_value_present_in_message(self) -> None:
        """A value in the message must be a real status for its type, so copying it works - not a
        plausible-looking word that the vocab would reject."""
        msg = _load().batch_selection_message()
        self.assertIn("Open", sdlc_md.status_vocab("bug"))
        self.assertIn("Proposed", sdlc_md.status_vocab("cr"))
        self.assertIn("Ready", sdlc_md.status_vocab("story"))
        # and each of those valid values is the one the message actually shows
        for status in ("Open", "Proposed", "Ready"):
            self.assertIn(status, msg)


if __name__ == "__main__":
    unittest.main()
