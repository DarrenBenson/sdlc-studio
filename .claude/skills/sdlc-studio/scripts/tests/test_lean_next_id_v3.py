"""BG0872: `next_id.py allocate` mints the project's own id schema.

On a schema v3 project `artifact.py new` mints a ULID id (`US-01...`), so an allocator that
still printed the next sequential `US0001` handed agents a second id schema for the same
project. A v2 project keeps its sequential ids.

Every test drives the shipped entry points in a throwaway project that cleans itself up; none
reads this repository.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/next_id.py
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
#: The shape `artifact.py new` mints on a v3 project (`sdlc_md.mint_v3_id`).
_V3_STORY = re.compile(r"^US-[0-9A-HJKMNP-TV-Z]{8,}$")


def _cli(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(_SCRIPTS / script), *args, "--root", str(root)],
        cwd=root, env=gitutil.git_env(), capture_output=True, text=True, timeout=300)


def _init(root: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], env=gitutil.git_env(),
                   check=True, capture_output=True)
    proc = _cli(root, "init.py", "run")
    if proc.returncode != 0:
        raise AssertionError(f"init.py run exited {proc.returncode}:\n{proc.stdout}\n{proc.stderr}")


def _set_schema(root: Path, version: int) -> None:
    cfg = root / "sdlc-studio" / ".config.yaml"
    text = cfg.read_text(encoding="utf-8")
    new, n = re.subn(r"(?m)^schema_version:\s*\d+", f"schema_version: {version}", text)
    if n != 1:
        raise AssertionError(f"the fixture config holds {n} schema_version lines:\n{text}")
    cfg.write_text(new, encoding="utf-8")


class NextIdV3Tests(unittest.TestCase):
    def test_a_v3_project_gets_no_sequential_id(self) -> None:
        """AC1. MUTANT: HEAD's `cmd_allocate` formats `f"{prefix}{next_num:04d}"` whatever the
        schema, so it prints `US0001` and exits 0 on the fresh v3 project."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _init(root)
            cfg = (root / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8")
            self.assertRegex(cfg, r"(?m)^schema_version:\s*3\b",
                             "the premise: a fresh init run project is at schema v3")
            proc = _cli(root, "next_id.py", "allocate", "--type", "story")
            out = proc.stdout.strip()
            self.assertNotIn("US0001", proc.stdout + proc.stderr)
            if proc.returncode == 0:
                self.assertRegex(out, _V3_STORY, f"not the v3 shape artifact.py mints: {out!r}")
            else:
                self.assertIn("artifact.py new", proc.stdout + proc.stderr)

    def test_a_v2_project_keeps_sequential_ids(self) -> None:
        """AC2, the positive control. MUTANT: a fix that mints a v3 id, or refuses, whatever the
        project's schema - this project is at v2 and must still get `US0001`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _init(root)
            _set_schema(root, 2)
            proc = _cli(root, "next_id.py", "allocate", "--type", "story")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip(), "US0001")


if __name__ == "__main__":
    unittest.main()
