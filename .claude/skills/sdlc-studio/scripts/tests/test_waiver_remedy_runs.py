"""Every checklist waiver remedy the close prints runs, as printed, and records the waiver.

`decisions.py waive` refuses a checklist waiver that names nobody as its authoriser, so a
remedy printed without `--authorised-by` is a command its reader runs and is refused by. The
three places that print one (the close's checklist step, the close pre-flight's checklist rows
and the report's checklist section) are each asked for their remedy over one outstanding item,
and each printed command is run through the real `decisions.py`, its placeholders filled.
"""
from __future__ import annotations

import importlib
import json
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

sprint = loader.load_script("sprint")
sprint_report = loader.load_script("sprint_report")

SCRIPTS = Path(__file__).resolve().parent.parent

#: One compulsory item left outstanding, in the shape `sprint_report.checklist` returns. Its
#: detail is empty, so the pre-flight's row prints the waiver remedy rather than the detail.
_ITEM = "closing-review"
_CK = {
    "items": [{"id": _ITEM, "title": "Closing full-diff review", "value": "none recorded",
               "detail": "", "state": sprint_report.UNANSWERED}],
    "outstanding": [_ITEM], "expired": [], "stop_ship": [], "pending_in_close": [],
}

_FILLED = {"<item>": _ITEM, "<why>": "the batch changed no code",
           "<the operator>": "Pat Operator"}


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


def _commands(text: str) -> list[str]:
    """Each `decisions.py waive ...` command a remedy prints, between its backticks."""
    return re.findall(r"`(decisions\.py waive [^`]*)`", text)


def _remedies(root: Path) -> dict[str, str]:
    """The waiver remedy each of the three surfaces prints over `_CK`."""
    mod, rep = _live("sprint"), _live("sprint_report")
    state = json.loads((root / "sdlc-studio" / ".local" / "run-state.json").read_text())
    with unittest.mock.patch.object(rep, "checklist", lambda *a, **k: _CK), \
            unittest.mock.patch.object(mod, "unanswered_units",
                                       lambda *a, **k: {"unanswered": [], "rulings_from": ""}):
        step = mod._close_checklist(root, "RETRO0001", state)
        rows = mod._checklist_blockers(root, "RETRO0001", state)
    return {"close checklist step": step[2],
            "close pre-flight": "\n".join(r["remedy"] for r in rows),
            "report checklist": rep.render_checklist(_CK)}


def _fixture(root: Path) -> None:
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"schema": 1, "run_id": "RUN-WAIVE001", "outcome": "running",
                             "batch": [], "started_at": "2026-11-24T00:00:00Z"}),
                 encoding="utf-8")


class WaiverRemedyTests(unittest.TestCase):

    def test_each_printed_remedy_records_as_printed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            remedies = _remedies(root)
        for surface, text in remedies.items():
            with self.subTest(surface=surface):
                commands = _commands(text)
                self.assertEqual(1, len(commands), text)
                command = commands[0]
                for placeholder, value in _FILLED.items():
                    command = command.replace(placeholder, value)
                self.assertNotIn("<", command)          # every placeholder was filled
                argv = shlex.split(command)
                with tempfile.TemporaryDirectory() as d:
                    root = Path(d)
                    (root / "sdlc-studio").mkdir()
                    res = subprocess.run(
                        [sys.executable, str(SCRIPTS / argv[0]), *argv[1:]], cwd=root,
                        capture_output=True, text=True, timeout=60, env=gitutil.git_env())
                    self.assertEqual(0, res.returncode, res.stderr)
                    log = (root / "sdlc-studio" / "decisions.md").read_text(encoding="utf-8")
                    self.assertIn(f"waiver: {sprint_report.WAIVER_SUBJECT}:{_ITEM}", log)
                    self.assertIn("[authorised by: Pat Operator]", log)


if __name__ == "__main__":
    unittest.main()
