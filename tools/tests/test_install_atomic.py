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


class ResolveTargetsAuto(unittest.TestCase):
    """CR0208: `--target auto` must not select copilot on a GLOBAL install (copilot is
    repo-scoped only, so it would write .github/skills into the current directory)."""

    def _auto(self, mode: str) -> str:
        # source install.sh, pretend gh (copilot) and claude are both detected, then resolve
        driver = (
            'source "%s"\n' % INSTALL_SH
            + 'set +e\n'
            + 'is_detected() { case "$1" in copilot|claude) return 0;; *) return 1;; esac; }\n'
            + 'INSTALL_MODE="%s"\n' % mode
            + 'resolve_targets auto\n'
        )
        proc = subprocess.run(["bash", "-c", driver], capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent"}, timeout=30)
        return proc.stdout.strip()

    def test_global_auto_excludes_copilot(self) -> None:
        out = self._auto("global")
        self.assertIn("claude", out)
        self.assertNotIn("copilot", out)

    def test_local_auto_keeps_copilot(self) -> None:
        out = self._auto("local")
        self.assertIn("copilot", out)


class DowngradeGuard(unittest.TestCase):
    """BG0100: install/sweep must refuse to overwrite a copy that is NEWER than the version being
    installed, so an install from an older published release cannot silently revert newer local
    work (a dev checkout ahead of the frozen remote)."""

    def _dest(self, root: Path, version: str) -> Path:
        d = root / "sdlc-studio"
        (d / "templates").mkdir(parents=True)
        (d / "SKILL.md").write_text("name: sdlc-studio\n", encoding="utf-8")
        (d / "templates" / "version.yaml").write_text(
            'skill_version: "%s"\n' % version, encoding="utf-8")
        return d

    def _would_downgrade(self, dest: Path, incoming: str, allow: str = "false") -> int:
        driver = (
            'source "%s"\n' % INSTALL_SH
            + 'set +e\nwarn() { echo "WARN: $*" >&2; }\n'
            + 'ALLOW_DOWNGRADE=%s\n' % allow
            + 'would_downgrade "%s" "%s"; echo "RC=$?"\n' % (dest, incoming)
        )
        proc = subprocess.run(["bash", "-c", driver], capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin", "HOME": "/nonexistent"}, timeout=30)
        return proc.stdout + proc.stderr

    def test_refuses_downgrade_of_newer_copy(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0-rc.1")
            out = self._would_downgrade(dest, "3.6.0")
            self.assertIn("RC=0", out)          # 0 = would downgrade -> caller skips
            self.assertIn("refusing to downgrade", out)

    def test_allows_downgrade_with_flag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0-rc.1")
            self.assertIn("RC=1", self._would_downgrade(dest, "3.6.0", allow="true"))

    def test_allows_upgrade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "3.6.0")
            self.assertIn("RC=1", self._would_downgrade(dest, "4.0.0-rc.1"))

    def test_branch_name_is_not_a_false_downgrade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            dest = self._dest(Path(d), "4.0.0")
            self.assertIn("RC=1", self._would_downgrade(dest, "main"))  # non-semver -> not older


class LocalSourceInstall(unittest.TestCase):
    """CR0214: --from DIR installs the LOCAL tree (the dev-testing path) instead of
    downloading the published release; a non-skill dir refuses before any write."""

    def _run(self, home: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", str(INSTALL_SH), *args],
                              env={"PATH": "/usr/bin:/bin", "HOME": str(home)},
                              capture_output=True, text=True, timeout=60)

    def _src(self, root: Path, version: str = "9.9.9") -> Path:
        src = root / "src" / "sdlc-studio"
        (src / "templates").mkdir(parents=True)
        (src / "SKILL.md").write_text("name: sdlc-studio\n", encoding="utf-8")
        (src / "templates" / "version.yaml").write_text(
            'skill_version: "%s"\n' % version, encoding="utf-8")
        (src / "marker.txt").write_text("LOCAL-TREE\n", encoding="utf-8")
        return src

    def test_from_installs_the_local_tree_without_downloading(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"; home.mkdir()
            src = self._src(Path(d))
            proc = self._run(home, "--from", str(src), "--no-sweep")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            dest = home / ".claude" / "skills" / "sdlc-studio"
            self.assertEqual((dest / "marker.txt").read_text(encoding="utf-8"), "LOCAL-TREE\n")
            self.assertNotIn("Downloading", proc.stdout)  # no network path taken

    def test_from_refuses_a_non_skill_dir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"; home.mkdir()
            junk = Path(d) / "junk"; junk.mkdir()
            proc = self._run(home, "--from", str(junk), "--no-sweep")
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertFalse((home / ".claude" / "skills" / "sdlc-studio").exists())

    def test_from_still_respects_the_downgrade_guard(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"
            dest = home / ".claude" / "skills" / "sdlc-studio"
            (dest / "templates").mkdir(parents=True)
            (dest / "SKILL.md").write_text("name: sdlc-studio\n", encoding="utf-8")
            (dest / "templates" / "version.yaml").write_text(
                'skill_version: "9.9.9"\n', encoding="utf-8")
            src = self._src(Path(d), version="1.0.0")   # older local tree
            proc = self._run(home, "--from", str(src), "--no-sweep")
            self.assertIn("refusing to downgrade", proc.stdout + proc.stderr)
            self.assertEqual((dest / "templates" / "version.yaml").read_text(encoding="utf-8"),
                             'skill_version: "9.9.9"\n')  # newer install untouched


if __name__ == "__main__":
    unittest.main()
