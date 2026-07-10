"""Regression test for CR0205: install.sh must not destroy a working install when the
copy fails. The old `rm -rf $dest; cp -r ...` left the user with nothing (or a half-copy)
if cp failed between the two. The fix stages into a temp sibling and swaps, so a failed
copy leaves the previous install byte-for-byte intact.
"""
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"

# Source the installer, point install_to at a source, but make `cp` fail. The previous
# install at $dest must survive unchanged, and install_to must report failure (non-zero).
DRIVER = r"""
source "__INSTALL_SH__"
set +e                                  # install.sh sets -e; relax it so we can inspect
DRY_RUN=false
SKILL_NAME="sdlc-studio"

ship_changelog() { :; }                 # no-op the changelog copy
cp() { command false; }                 # every cp fails

install_to "$PARENT" "$SRC"
echo "INSTALL_RC=$?"
cat "$PARENT/sdlc-studio/marker.txt" 2>/dev/null || echo "MARKER_GONE"
"""


class InstallAtomicSwap(unittest.TestCase):
    def test_swap_install_dest_tracks_the_arg_not_caller_scope(self) -> None:
        # Critic finding: dest="$parent/..." on the same `local` line as parent="$1" resolved
        # via caller dynamic scope (rm -rf on the install path riding on coincidence).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src" / "sdlc-studio"; src.mkdir(parents=True)
            (src / "x.txt").write_text("x\n")
            target = root / "target"; target.mkdir()
            driver = (
                'source "%s"\n' % INSTALL_SH
                + 'set +e\nDRY_RUN=false\nSKILL_NAME="sdlc-studio"\n'
                + 'ship_changelog() { :; }\n'
                + 'parent="/SHOULD_NOT_BE_USED"\n'   # a caller-scope decoy
                + 'swap_install "%s" "%s"\n' % (target, src)
                + 'echo "RC=$?"\n'
                + '[ -d "%s/sdlc-studio" ] && echo DEST_OK || echo DEST_WRONG\n' % target
            )
            proc = subprocess.run(["bash", "-c", driver], capture_output=True, text=True,
                                  env={"PATH": "/usr/bin:/bin"}, timeout=30)
            self.assertIn("DEST_OK", proc.stdout, msg=proc.stdout + proc.stderr)

    def test_failed_copy_leaves_previous_install_intact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            src = root / "src" / "sdlc-studio"
            src.mkdir(parents=True)
            (src / "new.txt").write_text("new\n")
            parent = root / "target"
            (parent / "sdlc-studio").mkdir(parents=True)
            (parent / "sdlc-studio" / "marker.txt").write_text("PREVIOUS-INSTALL\n")
            script = DRIVER.replace("__INSTALL_SH__", str(INSTALL_SH))
            proc = subprocess.run(
                ["bash", "-c", script],
                env={"SRC": str(src), "PARENT": str(parent), "PATH": "/usr/bin:/bin"},
                capture_output=True, text=True, timeout=30,
            )
            self.assertIn("PREVIOUS-INSTALL", proc.stdout,
                          msg="the previous install was destroyed by a failed copy:\n"
                          + proc.stdout + proc.stderr)
            self.assertNotIn("INSTALL_RC=0", proc.stdout,
                             msg="install_to reported success despite a failed copy")


if __name__ == "__main__":
    unittest.main()
