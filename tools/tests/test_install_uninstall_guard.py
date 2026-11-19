"""BG1547: `install.sh --uninstall` removes only a folder that is an sdlc-studio copy or is empty.

`uninstall_from` checked only that the folder existed, then removed it recursively and reported
it removed, so a folder named sdlc-studio holding the user's own files was deleted with no
warning, while every install path skips such a folder as the user's. The uninstall now applies
the same identity guard, removes a symbolic link without following it, and its closing line says
when nothing was removed. Each run uses a scratch HOME; nothing outside it is touched.

BG1631 (InstallPs1UninstallGuardTests): install.ps1's -Uninstall had the same unguarded removal.
It runs under pwsh where pwsh is installed, as on the CI runners; its uninstall branch is read in
every case.
"""
from __future__ import annotations

# test-census-subject: install.sh
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"
INSTALL_MD = REPO / "docs" / "INSTALL.md"
INSTALL_PS1 = REPO / "install.ps1"
PWSH = shutil.which("pwsh")
SKILL_MD = "---\nname: sdlc-studio\n---\n"


class UninstallGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.home = self.root / "home"
        self.dest = self.home / ".claude" / "skills" / "sdlc-studio"
        self.dest.parent.mkdir(parents=True)

    def _uninstall(self) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", str(INSTALL_SH), "--uninstall", "--target", "claude"],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              env={**os.environ, "HOME": str(self.home)}, cwd=str(self.root),
                              timeout=60)

    @staticmethod
    def _closing(out: str) -> str:
        lines = [ln for ln in out.splitlines() if ln.strip()]
        return lines[-1] if lines else ""

    def test_a_foreign_folder_is_left_alone_and_said_so(self) -> None:
        """AC1. MUTANT: HEAD's unguarded `rm -rf "$dest"`. MUTANT: a guard that keeps the folder
        but still closes with 'Uninstall complete.' as though it were removed."""
        self.dest.mkdir()
        (self.dest / "notes.txt").write_text("mine\n", encoding="utf-8")
        proc = self._uninstall()
        out = proc.stdout
        self.assertEqual(0, proc.returncode, out)
        self.assertTrue(any("not an sdlc-studio copy" in ln and str(self.dest) in ln
                            for ln in out.splitlines() if ln.startswith("Warning:")),
                        f"no warning naming the folder as not an sdlc-studio copy:\n{out}")
        self.assertEqual("mine\n", (self.dest / "notes.txt").read_text(encoding="utf-8"))
        self.assertNotIn(f"removed: {self.dest}", out, out)
        self.assertIn("Nothing was removed", self._closing(out), out)

    def test_a_real_copy_and_an_empty_folder_are_removed(self) -> None:
        """AC2, the control. MUTANT: a guard that refuses the installer's own copy. MUTANT: a
        guard that refuses an empty folder, which holds nothing of the user's."""
        for case in ("a real copy", "an empty folder"):
            with self.subTest(case=case):
                self.dest.mkdir()
                if case == "a real copy":
                    (self.dest / "templates").mkdir()
                    (self.dest / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
                    (self.dest / "templates" / "version.yaml").write_text(
                        'skill_version: "9.9.9"\n', encoding="utf-8")
                proc = self._uninstall()
                out = proc.stdout
                self.assertEqual(0, proc.returncode, out)
                self.assertFalse(os.path.lexists(self.dest), f"{case} was not removed:\n{out}")
                self.assertIn(f"removed: {self.dest}", out, out)
                self.assertNotIn("Nothing was removed", out, out)
                self.assertEqual("Uninstall complete.", self._closing(out).split("==> ")[-1], out)

    def test_a_symbolic_link_is_removed_and_its_target_kept(self) -> None:
        """AC3. MUTANT: `rm -rf "$dest/"`, which follows the link and empties the copy it points
        at. MUTANT: a guard that leaves the link in place."""
        elsewhere = self.root / "checkout" / "sdlc-studio"
        (elsewhere / "templates").mkdir(parents=True)
        (elsewhere / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
        (elsewhere / "templates" / "version.yaml").write_text('skill_version: "9.9.9"\n',
                                                               encoding="utf-8")
        self.dest.symlink_to(elsewhere, target_is_directory=True)
        proc = self._uninstall()
        out = proc.stdout
        self.assertEqual(0, proc.returncode, out)
        self.assertFalse(os.path.lexists(self.dest), f"the link was not removed:\n{out}")
        self.assertIn(f"removed: {self.dest}", out, out)
        self.assertEqual(SKILL_MD, (elsewhere / "SKILL.md").read_text(encoding="utf-8"),
                         f"the uninstall followed the link and deleted its target:\n{out}")
        self.assertTrue((elsewhere / "templates" / "version.yaml").is_file(), out)

    def test_the_install_page_states_the_uninstall_guard(self) -> None:
        """AC4. MUTANT: HEAD's uninstall bullet, silent on the guard."""
        page = INSTALL_MD.read_text(encoding="utf-8")
        bullet = re.search(r"^- \*\*Uninstall\*\*:(.*?)(?=^\S|^- |\Z)", page, re.S | re.M)
        self.assertIsNotNone(bullet, "docs/INSTALL.md has no Uninstall bullet")
        text = " ".join(bullet.group(1).split())
        self.assertIn("removes only a folder that is an sdlc-studio copy or is empty", text, text)


class InstallPs1UninstallGuardTests(unittest.TestCase):
    def test_ps1_uninstall_removes_only_a_folder_whose_skill_md_names_the_skill(self) -> None:
        """BG1631 AC1. MUTANT: HEAD's unguarded `Remove-Item -Path $dest -Recurse -Force`.
        MUTANT: a guard placed after the removal. MUTANT: a guard that warns and still removes.
        MUTANT: a guard on something other than the SKILL.md check (Test-SkillCopy)."""
        src = INSTALL_PS1.read_text(encoding="utf-8")
        branch = re.search(r"\n    if \(\$Uninstall\) \{\n(.*?)\n    \}\n", src, re.S)
        self.assertIsNotNone(branch, "install.ps1's uninstall branch moved")
        body = branch.group(1)
        removals = [m.start() for m in re.finditer(r"Remove-Item\b", body)]
        self.assertEqual(1, len(removals), "the uninstall branch should remove in one place")
        guard = re.search(r"if \(-not \(Test-SkillCopy \$dest\)[^\n]*\) \{(.*?)\n\s*\}", body,
                          re.S)
        self.assertIsNotNone(guard, "the removal is not guarded by the SKILL.md check")
        self.assertLess(guard.start(), removals[0], "the guard comes after the removal")
        self.assertIn("continue", guard.group(1), "a guarded folder is not skipped")
        self.assertIn("not an sdlc-studio copy", guard.group(1), "the skip is not reported")
        self.assertNotIn("Remove-Item", guard.group(1))
        if PWSH:
            self._executed()

    def _executed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "home"
            dest = home / ".claude" / "skills" / "sdlc-studio"
            dest.mkdir(parents=True)
            (dest / "notes.txt").write_text("mine\n", encoding="utf-8")

            def uninstall() -> subprocess.CompletedProcess:
                env = {**os.environ, "HOME": str(home), "NO_COLOR": "1",
                       "POWERSHELL_TELEMETRY_OPTOUT": "1", "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
                       "DOTNET_NOLOGO": "1"}
                return subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File",
                                       str(INSTALL_PS1), "-Uninstall", "-Target", "claude"],
                                      capture_output=True, text=True, env=env, cwd=d,
                                      timeout=180)

            proc = uninstall()
            out = proc.stdout + proc.stderr
            self.assertEqual("mine\n", (dest / "notes.txt").read_text(encoding="utf-8"), out)
            self.assertIn("not an sdlc-studio copy", out, out)
            (dest / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")   # now the skill's copy
            proc = uninstall()
            out = proc.stdout + proc.stderr
            self.assertFalse(dest.exists(), f"a folder naming the skill was not removed:\n{out}")


if __name__ == "__main__":
    unittest.main()
