"""Regression test for BG0054: install.sh must not abort under `set -e` after a
successful stale-copy sweep.

`sweep_stale` ends by reporting whether any other copy was found. When it *did*
refresh a copy (`found=true`), a trailing `[[ ... ]] && info` compound returns 1,
and `set -e` then kills the installer before the success banner prints. This test
sources install.sh (which only runs `main` when executed, not when sourced),
stubs the environment probes, and asserts `sweep_stale` exits 0 in the
found-a-copy case.
"""
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"

# Source the installer, stub the filesystem/version probes so the sweep believes
# it found one stale copy to refresh, run in dry-run (no rm/cp), and surface the
# function's exit code. `set -e` is enabled to mirror the real script.
DRIVER = r"""
set -e
source "__INSTALL_SH__"

DRY_RUN=true
ALL_TARGETS="gemini"          # a single location to probe
VERSION="9.9.9"

# Stub the environment probes: pretend a stale sdlc-studio copy exists at $STALE.
target_dir() { [[ "$2" == global ]] && echo "$STALE_PARENT" || echo ""; }
is_skill_copy() { return 0; }
installed_version() { echo "0.0.1"; }

sweep_stale "/nonexistent/src" ""
echo "SWEEP_RC=$?"
"""


class InstallSweepExitCode(unittest.TestCase):
    def test_sweep_returns_zero_when_a_copy_is_refreshed(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            parent = Path(d)
            (parent / "sdlc-studio").mkdir()  # the "stale copy" the sweep finds
            script = DRIVER.replace("__INSTALL_SH__", str(INSTALL_SH))
            proc = subprocess.run(
                ["bash", "-c", script],
                env={"STALE_PARENT": str(parent), "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=30,
            )
            # The whole point: `set -e` must not have aborted the sweep.
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertIn("SWEEP_RC=0", proc.stdout)


if __name__ == "__main__":
    unittest.main()
