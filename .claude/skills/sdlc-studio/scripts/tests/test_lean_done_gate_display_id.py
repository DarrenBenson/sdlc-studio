"""BG0886: the Done gate's refusal names a v3 story in its file's spelling on every line.

BG0825 and BG0877 moved the refusal's prefix to the display id (`US-01ABCDEF`), but the inner
line built by `transition._unanswered_delivery_reject` was handed the hyphenless comparison key
and printed `US01ABCDEF carries an unanswered delivery REJECT` - an id no file carries.

Driven through `critic.py record` and `transition.py set`, the shipped entry points, in a
throwaway `init run` project (schema v3) that cleans itself up.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/transition.py
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

_SCRIPTS = Path(__file__).resolve().parent.parent
_ID = re.compile(r"created (\S+)")


def _cli(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(_SCRIPTS / script), *args, "--root", str(root)],
        cwd=root, env=gitutil.git_env(), capture_output=True, text=True, timeout=300)


def _ok(root: Path, script: str, *args: str) -> str:
    proc = _cli(root, script, *args)
    if proc.returncode != 0:
        raise AssertionError(f"{script} {' '.join(args)} exited {proc.returncode}:\n"
                             f"{proc.stdout}\n{proc.stderr}")
    return proc.stdout


class DoneGateDisplayIdTests(unittest.TestCase):
    def test_the_reject_refusal_names_the_file_spelling(self) -> None:
        """AC1. MUTANT: HEAD passes `sdlc_md.norm_id(artifact_id)` into
        `_unanswered_delivery_reject`, whose message opens on that key, so the inner line reads
        `US01... carries an unanswered delivery REJECT`. The control: the refusal does name the
        REJECT, so a gate that stopped reporting it cannot pass by printing nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", "-b", "main", str(root)],
                           env=gitutil.git_env(), check=True, capture_output=True)
            _ok(root, "init.py", "run")
            epic = _ID.search(_ok(root, "artifact.py", "new", "--type", "epic",
                                  "--title", "Widgets")).group(1)
            story = _ID.search(_ok(
                root, "artifact.py", "new", "--type", "story", "--title", "A widget",
                "--epic", epic, "--points", "1", "--affects", "src/widget.py",
                "--ac", "the widget exists", "--verify", "shell true")).group(1)
            self.assertRegex(story, r"^US-[0-9A-Z]{8,}$", "premise: a v3 story id")
            key = story.replace("-", "")
            _ok(root, "critic.py", "record", "--unit", story, "--verdict", "REJECT",
                "--reviewer", "qa seat", "--author", "engineering seat",
                "--issues", "[new] the widget is missing")
            proc = _cli(root, "transition.py", "set", "--id", story, "--status", "Done")
            said = proc.stdout + proc.stderr
            self.assertNotEqual(0, proc.returncode, said)
            self.assertIn("unanswered delivery REJECT", said)
            self.assertIn(f"{story} carries an unanswered delivery REJECT", said)
            for line in said.splitlines():
                self.assertIsNone(re.search(rf"(?<![A-Za-z0-9-]){key}(?![A-Za-z0-9])", line),
                                  f"a line names the hyphenless key {key}: {line!r}")


if __name__ == "__main__":
    unittest.main()
