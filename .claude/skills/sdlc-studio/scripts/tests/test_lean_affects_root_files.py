"""BG0811: a root-level file with no listed extension stays in a unit's Affects.

`sdlc_md.affects_files` kept a token only when it held a `/` or ended in .py, .md, .yaml, .yml or
.sh, so a root `package.json`, `astro.config.mjs`, `pyproject.toml` or `Makefile` dropped out of
the review brief's diff scope and the plan's shared-file checks. A slash-free token is now kept
when it has the shape of a file - an extension, a dotfile, or a known extension-less name - and
prose (`none`, `-`, a parenthetical note, a sentence) is still not a path.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from lib import sdlc_md  # noqa: E402

CRITIC = HERE.parent / "critic.py"


def _unit(affects: str) -> str:
    return f"# US0001: a unit\n\n> **Status:** Ready\n> **Affects:** {affects}\n"


class AffectsRootFilesTests(unittest.TestCase):
    def test_root_files_are_kept(self) -> None:
        """AC1. MUTANTS: HEAD's extension list - only `src/x.ts` survives; an existence check
        alone - a root file the unit will create is dropped; a known-name list without the
        extension rule - `astro.config.mjs` and `pyproject.toml` are dropped."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Makefile").write_text("all:\n", encoding="utf-8")
            text = _unit("astro.config.mjs, package.json, pyproject.toml, Makefile, src/x.ts")
            self.assertEqual(["astro.config.mjs", "package.json", "pyproject.toml", "Makefile",
                              "src/x.ts"], sdlc_md.affects_files(text))
        # The other root shapes the finding names, a dotfile, and a backticked token with a note.
        text = _unit("tsconfig.json, go.mod, Cargo.toml, Dockerfile, .gitignore, "
                     "`vite.config.ts` (new)")
        self.assertEqual(["tsconfig.json", "go.mod", "Cargo.toml", "Dockerfile", ".gitignore",
                          "vite.config.ts"], sdlc_md.affects_files(text))

    def test_prose_is_not_a_path(self) -> None:
        """AC2. MUTANTS: every comma-separated token is a path - `none`, `-`, `TBD`, a sentence,
        a version string and the halves of a parenthetical note all come back; split on every
        comma - a note holding a comma cuts its path in two, the root file is lost and the
        slashed path keeps the note's opening words (`src/a.py (reads b`)."""
        for affects in ("none", "-", "TBD", "n.a.", "v1.2", "a new archive helper",
                        "e.g. the config", "(none yet)",
                        "a sentence ending in config.json"):
            with self.subTest(affects=affects):
                self.assertEqual([], sdlc_md.affects_files(_unit(affects)))
        text = _unit("package.json (the scripts block, and the lockfile), src/x.ts, "
                     "src/a.py (reads b, and c)")
        self.assertEqual(["package.json", "src/x.ts", "src/a.py"], sdlc_md.affects_files(text))

    def test_the_review_brief_scopes_a_root_file(self) -> None:
        """The soak's own failure through the shipped entry point: `critic.py brief` names a
        root config file the unit declares in its bounded diff scope."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0001-a-unit.md").write_text(
                _unit("astro.config.mjs, src/pages/index.astro")
                + "\n## Acceptance Criteria\n\n- [ ] **AC1** Given a page, then it builds\n",
                encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(CRITIC), "brief", "--unit", "US0001", "--seat", "qa",
                 "--root", str(root)], capture_output=True, text=True, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stderr)
        lines = proc.stdout.splitlines()
        at = next(i for i, ln in enumerate(lines) if ln.startswith("Diff scope"))
        self.assertEqual("astro.config.mjs, src/pages/index.astro", lines[at + 1])


if __name__ == "__main__":
    unittest.main()
