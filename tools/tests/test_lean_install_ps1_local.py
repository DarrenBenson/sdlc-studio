"""BG0821: `install.ps1 -Local` leaves the personal copies alone, as BG0809 made `install.sh
--local` do, and neither installer warns that a copy shadows itself.

A local install pins a version in ONE project; the personal copies are what every other project
loads, so its sweep must read the local scope only. Claude Code loads a personal skill ahead of a
project one of the same name, so a local install under a personal copy says so - unless the two
paths reach one directory (a local install run from the home directory), which shadows nothing.

install.ps1 runs for real (dry run, which is offline) wherever `pwsh` is on PATH, as it is on the
CI runners. Where it is not, the same claims are pinned on the script's source, so the Verify
selectors never pass on a skip.

MUTANTS: the -Local sweep walks both scopes; the sweep loses the global scope under -Global too;
the same-directory guard is dropped (either installer); the shadow note is never printed."""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

# test-census-subject: install.ps1

REPO =Path(__file__).resolve().parents[2]
INSTALL_PS1 = REPO / "install.ps1"
INSTALL_SH = REPO / "install.sh"
PWSH = shutil.which("pwsh")
NOTE = "ahead of"          # the shadow note's wording, shared by both installers


def _skill(path: Path, version: str) -> Path:
    """A minimal sdlc-studio skill tree: what the identity guard and version reader read."""
    (path / "templates").mkdir(parents=True)
    (path / "SKILL.md").write_text("---\nname: sdlc-studio\n---\n", encoding="utf-8")
    (path / "templates" / "version.yaml").write_text(f'skill_version: "{version}"\n',
                                                     encoding="utf-8")
    return path


def _ps1(home: Path, cwd: Path, *argv: str) -> str:
    """Run install.ps1 as a user would, in a throwaway HOME. A dry run: offline, writes nothing."""
    env = {**os.environ, "HOME": str(home), "NO_COLOR": "1", "POWERSHELL_TELEMETRY_OPTOUT": "1",
           "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"}
    cp = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(INSTALL_PS1),
                         "-Target", "claude", "-DryRun", *argv],
                        cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    out = cp.stdout + cp.stderr
    if cp.returncode != 0:
        raise AssertionError(f"install.ps1 {' '.join(argv)} exited {cp.returncode}:\n{out}")
    return out


def _sh(home: Path, cwd: Path, src: Path) -> str:
    cp = subprocess.run(["bash", str(INSTALL_SH), "--local", "--from", str(src),
                         "--target", "claude"],
                        cwd=cwd, env={"HOME": str(home), "PATH": "/usr/bin:/bin", "NO_COLOR": "1"},
                        capture_output=True, text=True, timeout=60)
    out = cp.stdout + cp.stderr
    if cp.returncode != 0:
        raise AssertionError(f"install.sh --local exited {cp.returncode}:\n{out}")
    return out


def _notes(out: str) -> list:
    return [ln for ln in out.splitlines() if NOTE in ln]


class InstallPs1LocalTests(unittest.TestCase):

    def setUp(self) -> None:
        base = Path(tempfile.mkdtemp(prefix="bg0821_"))
        self.addCleanup(shutil.rmtree, base, True)
        self.base = base.resolve()
        self.home, self.project = self.base / "home", self.base / "project"
        self.home.mkdir()
        self.project.mkdir()
        self.ps1 = INSTALL_PS1.read_text(encoding="utf-8")

    def test_local_sweeps_the_local_scope_only(self) -> None:
        # Source pin, always: the sweep iterates ONE scope list, and under -Local it is 'local'.
        loops = re.findall(r"foreach \(\$sweepScope in (\$\w+)\)", self.ps1)
        self.assertEqual(len(loops), 1, "install.ps1's sweep no longer iterates a scope list")
        pinned = re.escape(loops[0]) + (r" = if \(\$Local\) \{ @\('local'\) \} "
                                        r"else \{ @\('global', 'local'\) \}")
        self.assertEqual(len(re.findall(pinned, self.ps1)), 1,
                         f"{loops[0]} is not 'local' alone under -Local and both scopes otherwise")
        if not PWSH:
            return
        personal = [_skill(self.home / ".claude/skills/sdlc-studio", "1.0.0"),
                    _skill(self.home / ".gemini/skills/sdlc-studio", "1.0.0")]
        own = _skill(self.project / ".gemini/skills/sdlc-studio", "1.0.0")
        out = _ps1(self.home, self.project, "-Local")
        refreshed = [ln for ln in out.splitlines() if "would refresh" in ln]
        self.assertTrue(any(str(own) in ln for ln in refreshed),
                        f"-Local no longer sweeps this project's own stale copy:\n{out}")
        self.assertFalse([ln for ln in refreshed if str(self.home) in ln],
                         f"-Local would refresh a personal copy:\n{out}")
        # the positive control: a -Global install still sweeps the personal copies
        out = _ps1(self.home, self.project, "-Global")
        self.assertTrue(any(str(personal[1]) in ln for ln in out.splitlines()
                            if "would refresh" in ln), f"-Global stopped sweeping:\n{out}")

    def test_no_shadow_warning_for_one_directory(self) -> None:
        # install.sh, for real. The positive control first: a personal copy elsewhere is named.
        src = _skill(self.base / "src/sdlc-studio", "2.0.0")
        _skill(self.home / ".claude/skills/sdlc-studio", "1.5.0")
        self.assertEqual(len(_notes(_sh(self.home, self.project, src))), 1,
                         "install.sh no longer names a personal copy that shadows the project's")
        # run from the home directory: the project copy IS the personal copy
        out = _sh(self.home, self.home, src)
        self.assertEqual(_notes(out), [], f"install.sh warned the copy shadows itself:\n{out}")
        # the personal copy a link to the project copy: one directory by two names
        other = self.base / "linked"
        (other / ".claude/skills").mkdir(parents=True)
        (other / ".claude/skills/sdlc-studio").symlink_to(
            self.project / ".claude/skills/sdlc-studio", target_is_directory=True)
        out = _sh(other, self.project, src)
        self.assertEqual(_notes(out), [], f"install.sh warned through a link:\n{out}")

        # install.ps1. Source pin, always: the note returns before warning when the two paths
        # reach one directory.
        body = re.search(r"function Show-ShadowNote\b(.*?)\n    \}\n", self.ps1, re.S)
        self.assertIsNotNone(body, "install.ps1 has no Show-ShadowNote")
        before_warn = body.group(1).split("Write-Warn2")[0]
        self.assertIn("if ($project -eq $personal) { return }", before_warn,
                      "install.ps1's shadow note does not stand down for one directory")
        self.assertIn("Show-ShadowNote", self.ps1.split("function Show-ShadowNote")[1],
                      "install.ps1 never calls its shadow note")
        if not PWSH:
            return
        home2 = self.base / "home2"
        _skill(home2 / ".claude/skills/sdlc-studio", "1.5.0")
        notes = _notes(_ps1(home2, self.project, "-Local"))
        self.assertEqual(len(notes), 1, "install.ps1 does not name a shadowing personal copy")
        for part in (str(home2 / ".claude/skills/sdlc-studio"), "1.5.0",
                     str(self.project / ".claude/skills/sdlc-studio")):
            self.assertIn(part, notes[0], notes[0])
        out = _ps1(self.home, self.home, "-Local")
        self.assertEqual(_notes(out), [], f"install.ps1 warned the copy shadows itself:\n{out}")
        out = _ps1(other, self.project, "-Local")
        self.assertEqual(_notes(out), [], f"install.ps1 warned through a link:\n{out}")


class InstallPs1CopilotTests(unittest.TestCase):
    """BG0855: install.ps1 treats Copilot as BG0852 made install.sh do - a global install goes to
    the personal `~/.agents/skills` folder Copilot CLI reads, auto-detection selects copilot by
    the `copilot` binary (gh and a .github folder are repo signals, counted only for -Local),
    and the post-install note names `~/.agents/skills`.

    The note prints only after a real install, so it is pinned on the source in every run; the
    plan and the detection run for real wherever pwsh is on PATH, and are pinned on the source
    where it is not, so the selector never passes on a skip."""

    def setUp(self) -> None:
        base = Path(tempfile.mkdtemp(prefix="bg0855_"))
        self.addCleanup(shutil.rmtree, base, True)
        self.base = base.resolve()
        self.home, self.project = self.base / "home", self.base / "project"
        self.home.mkdir()
        self.project.mkdir()
        self.ps1 = INSTALL_PS1.read_text(encoding="utf-8")

    def _run(self, *argv: str) -> str:
        """install.ps1 as a user runs it, with a PATH holding a `copilot` and no `gh`."""
        stubs = self.base / "bin"
        stubs.mkdir(exist_ok=True)
        copilot = stubs / "copilot"
        copilot.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        copilot.chmod(0o755)
        env = {**os.environ, "HOME": str(self.home), "PATH": str(stubs), "NO_COLOR": "1",
               "POWERSHELL_TELEMETRY_OPTOUT": "1", "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
               "DOTNET_NOLOGO": "1"}
        cp = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(INSTALL_PS1),
                             "-DryRun", *argv], cwd=self.project, env=env,
                            capture_output=True, text=True, timeout=120)
        out = cp.stdout + cp.stderr
        self.assertEqual(0, cp.returncode, out)
        return out

    def test_auto_selects_a_copilot_personal_folder(self) -> None:
        """AC1. MUTANTS: HEAD's empty copilot global target (the install falls back to
        .github/skills); detection by `gh` or a .github folder (a host with only `copilot` is not
        detected); the repo-only note."""
        entry = re.search(r"^\s*copilot\s*=\s*@\{\s*global\s*=\s*(.*?);", self.ps1, re.M)
        self.assertIsNotNone(entry, "install.ps1 has no copilot map entry")
        self.assertEqual("(Join-Path $HOME '.agents\\skills')", entry.group(1).strip())
        detect = re.search(r"^\s*'copilot'\s*\{(.*)\}\s*$",
                           self.ps1.split("function Test-Detected")[1].split("function ")[0], re.M)
        self.assertIsNotNone(detect, "Test-Detected has no copilot case")
        self.assertIn("Get-Command copilot", detect.group(1))
        for repo_signal in ("Get-Command gh", "Test-Path '.github'"):
            if repo_signal in detect.group(1):
                self.assertRegex(detect.group(1), r"\$Scope -eq 'local'.*" + re.escape(repo_signal),
                                 f"{repo_signal} selects copilot for a global install")
        note = re.search(r"^\s*'copilot'\s*\{\s*'([^']*)'",
                         self.ps1.split("function Invoke-Note")[1], re.M)
        self.assertIsNotNone(note, "Invoke-Note has no copilot note")
        self.assertIn("~/.agents/skills", note.group(1))
        if not PWSH:
            return
        out = self._run("-Target", "copilot", "-Global")
        self.assertIn(f"would install to: {self.home / '.agents/skills/sdlc-studio'}", out)
        out = self._run("-Target", "auto")
        self.assertRegex(out, re.compile(r"Targets: copilot\s*$", re.M),
                         "auto did not select copilot, and copilot alone, by its binary")


if __name__ == "__main__":
    unittest.main()
