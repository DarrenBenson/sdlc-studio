"""The per-commit gate budget must only ever compare LIKE with LIKE (RFC0048 D6).

Found by the adversarial review of RUN-01KY1WCR. The hook recorded a `total` on every commit,
but it skips the ~85s unit suites on a docs-only commit and on any commit where a cheaper lane
already failed. Those 9-14s runs landed in the same series the budget reads, and because the
budget deliberately reads the LATEST run rather than a median, one docs commit made the next
report say `-85% since`. The gate had not got faster; it had just not run.

That failure is OPEN, which is what makes it worth a test: alternate a docs commit with a code
commit and the ratchet the budget exists to expose is invisible forever.

These tests RUN THE REAL HOOK in a throwaway repo rather than grepping it. A grep would pin the
shape of today's fix; only running it pins the behaviour, and the behaviour is the claim.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".githooks" / "pre-commit"


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True)


class BudgetRecordingTests(unittest.TestCase):
    """Only a commit that actually paid for the unit suites may enter the budget series."""

    def _repo(self, tmp: Path) -> Path:
        """A throwaway repo carrying just enough of this one to run the hook to its end."""
        root = tmp / "r"
        (root / "tools").mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        (root / ".githooks").mkdir(parents=True)
        (root / ".githooks" / "pre-commit").write_text(
            HOOK.read_text(encoding="utf-8"), encoding="utf-8")
        (root / ".githooks" / "pre-commit").chmod(0o755)
        for f in ("gate_timing.py",):
            (root / "tools" / f).write_text(
                (REPO / "tools" / f).read_text(encoding="utf-8"), encoding="utf-8")
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "gate_budget:\n  seconds: 120\n  baseline_seconds: 93.1\n"
            "  baseline_date: 2026-07-21\n", encoding="utf-8")
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        _git(root, "config", "core.hooksPath", ".githooks")
        return root

    def _totals(self, root: Path) -> list[float]:
        p = root / "sdlc-studio" / ".local" / "gate-timings.json"
        if not p.exists():
            return []
        return json.loads(p.read_text(encoding="utf-8")).get("total", [])

    def _commit(self, root: Path, rel: str, body: str) -> subprocess.CompletedProcess:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        _git(root, "add", "-A")
        env = dict(os.environ)
        env.pop("GIT_INDEX_FILE", None)
        return subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "x"],
                              capture_output=True, text=True, env=env)

    def test_a_docs_only_commit_does_not_enter_the_budget_series(self) -> None:
        """The exact regression: a commit that SKIPPED the suites must not be recorded as this
        gate's cost. Recorded, it made the next report read `-85% since`."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self._commit(root, "README.md", "hello\n")
            self.assertEqual(self._totals(root), [],
                             "a docs-only commit was recorded as a gate cost")

    def test_the_budget_line_is_not_printed_when_the_suites_were_skipped(self) -> None:
        """A budget line printed off a run that did not pay for the suites is a number about
        nothing, and it is worse than silence because it reads as a measurement."""
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            out = self._commit(root, "README.md", "hello\n")
            self.assertNotIn("gate-budget:", out.stdout + out.stderr)


if __name__ == "__main__":
    unittest.main()
