"""No tracked skill file documents an option the gate no longer accepts.

US0479. `--verify-batch` was parsed, handed to `run_gate` and read by nothing. Removing the
code is half the job: an option that survives in `help/` is one an operator still chooses, and
discovers is ignored only by reading the source.

Repo-only, like every other workspace-state check here - a `shell` verifier is unresolvable to
`verify_ac`'s staleness sweep, so a claim about the tree belongs in a pytest node id.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = ".claude/skills/sdlc-studio"

#: The option string that must appear nowhere an operator could read it as an offer.
REMOVED = "--verify-batch"

#: The one file allowed to name it: US0485's dead-flag detector pins gate.py's three
#: `verify_batch` lines VERBATIM as its fixture, because the defence has to be provable against
#: the shape that motivated it after the flag is gone. A test fixture is not an offer to run the
#: flag, which is what this guard is about. Held to that: the file must still contain the fixture
#: (below), so the allowance cannot decay into a blanket exemption once the fixture changes.
PINNED_FIXTURE = f"{SKILL}/scripts/tests/test_command_audit.py"
#: A string that IS present, asserted alongside. A scan that silently matched nothing would
#: otherwise read exactly like a scan that found the tree clean.
CONTROL = "--allow-external"


def _tracked_text_files() -> list[Path]:
    """Every tracked file under the skill tree. `git ls-files`, so an untracked scratch file
    or a build artefact cannot make the answer come out either way."""
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", SKILL],
                         capture_output=True, text=True, check=False)
    return [REPO / line for line in out.stdout.splitlines() if line.strip()]


class VerifyBatchDocsTests(unittest.TestCase):
    def test_no_tracked_skill_file_mentions_the_removed_flag(self) -> None:
        files = _tracked_text_files()
        self.assertTrue(files, "git ls-files returned nothing - this scan proves nothing")
        offenders, saw_control = [], False
        for path in files:
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if REMOVED in text and str(path.relative_to(REPO)) != PINNED_FIXTURE:
                offenders.append(str(path.relative_to(REPO)))
            if CONTROL in text:
                saw_control = True
        self.assertTrue(
            saw_control,
            f"the scan never found {CONTROL}, which IS present - so a clean result here is "
            f"the scan failing, not the tree being clean")
        self.assertFalse(
            offenders,
            f"{REMOVED} was removed from the gate but is still documented in: {offenders}")

    def test_the_one_exempt_file_is_exempt_for_the_reason_claimed(self) -> None:
        """The allowance is not a hole. It stands only while that file really is pinning the
        removed flag as a detector fixture; the moment it is not, this fails and the exemption
        comes out rather than quietly covering a fresh mention of the flag."""
        text = (REPO / PINNED_FIXTURE).read_text(encoding="utf-8")
        self.assertIn(REMOVED, text,
                      f"{PINNED_FIXTURE} no longer pins {REMOVED}, so its exemption above is "
                      f"covering nothing and must be removed")
        self.assertIn("GATE_FIXTURE", text,
                      "the exemption is for a pinned dead-flag fixture; that fixture is gone")


if __name__ == "__main__":
    unittest.main()
