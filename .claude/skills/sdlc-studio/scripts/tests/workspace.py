"""The one authority for "am I running inside the artefact-bearing dev repo?" (BG0209).

Some tests read the dogfooded `sdlc-studio/` workspace by path - a real story, a real
index - because that is the only place the behaviour under test is observable. Those
tests are correct in the dev repo and meaningless from an installed copy
(`~/.claude/skills/sdlc-studio/`), where `parents[5]` is the home directory and the
files simply are not there.

They must SKIP there, visibly, not fail: a consuming project running the shipped suite
otherwise sees errors that say nothing about its own install (BG0069, BG0209).

    import workspace
    if not workspace.in_dev_repo():
        self.skipTest(workspace.SKIP_REASON)

The check is deliberately two-sided. A `sdlc-studio/` directory alone is not enough - a
consuming project has one of those too. This skill must also sit under `<repo>/.claude/
skills/`, which is true of the dev checkout and false of an install.
"""
from __future__ import annotations

from pathlib import Path

#: <repo>/ - five levels above tests/, i.e. the checkout root in the dev repo.
REPO = Path(__file__).resolve().parents[5]

SKIP_REASON = ("dev-repo-only test: no sdlc-studio/ workspace at the expected root "
               "(running from an installed copy)")


def in_dev_repo(repo: Path = REPO) -> bool:
    """True only when `repo` is the artefact-bearing dev repo.

    Both halves are load-bearing: `repo/sdlc-studio/` must exist AND this file must live
    under `repo/.claude/skills/`. Dropping the second half would make an installed copy
    sitting next to any project workspace look like the dev repo.
    """
    skills = repo / ".claude" / "skills"
    return (repo / "sdlc-studio").is_dir() and skills.is_dir() \
        and str(Path(__file__).resolve()).startswith(str(skills.resolve()))
