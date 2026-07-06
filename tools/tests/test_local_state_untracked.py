"""US0079/CR0186: runtime `.local/` state must not be committed - it churns every session and
normalises shipping machine state. Guards that git tracks no `.local/` file."""
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class LocalStateUntracked(unittest.TestCase):
    def test_no_local_runtime_state_is_tracked(self) -> None:
        out = subprocess.run(["git", "ls-files"], cwd=str(REPO),
                             capture_output=True, text=True, timeout=30, check=False).stdout
        tracked = [ln for ln in out.splitlines() if "/.local/" in ln or ln.endswith("/.local")]
        self.assertEqual(tracked, [], f"runtime .local/ state is tracked: {tracked}")


if __name__ == "__main__":
    unittest.main()
