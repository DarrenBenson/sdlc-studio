"""Unit tests for tools/check_action_pins.sh (supply-chain pin guard).

The script takes an optional scan-root argument so these tests can point it at a
fixture tree with its own .github/workflows/.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "check_action_pins.sh"
SHA = "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"  # any 40-hex


def _run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), str(root)],
                          capture_output=True, text=True)


def _wf(root: Path, body: str) -> Path:
    d = root / ".github" / "workflows"
    d.mkdir(parents=True)
    (d / "ci.yml").write_text(body, encoding="utf-8")
    return root


class ActionPinTests(unittest.TestCase):
    def test_tag_ref_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(_wf(Path(d), "steps:\n  - uses: actions/checkout@v7\n"))
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("actions/checkout@v7", r.stderr)

    def test_sha_pin_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(_wf(Path(d), f"steps:\n  - uses: actions/checkout@{SHA} # v7\n"))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_branch_ref_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(_wf(Path(d), "steps:\n  - uses: some/action@main\n"))
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("some/action@main", r.stderr)

    def test_short_sha_flagged(self) -> None:
        # a truncated (7-hex) ref is still mutable-adjacent; only a full 40-hex passes
        with tempfile.TemporaryDirectory() as d:
            r = _run(_wf(Path(d), "steps:\n  - uses: actions/checkout@9c091bb # v7\n"))
            self.assertEqual(r.returncode, 1, r.stdout)

    def test_no_workflows_dir_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = _run(Path(d))
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
