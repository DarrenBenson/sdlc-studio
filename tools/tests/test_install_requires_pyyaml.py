"""US1296: both installers refuse on a machine that cannot import PyYAML, naming it and how to
install it (CR0731).

PyYAML is required: without it a project's configuration cannot be read and every gate it
switched on falls back to the shipped default. So `install.sh` and `install.ps1` check that
Python imports `yaml` before they look anything up, download or copy, and refuse with the
command that installs it.

HOW THEY RUN. The interpreter the installer finds is a stub first on PATH that hands its
arguments to this test's own Python with a `yaml` module of the test's making in front: one that
raises ImportError, or an empty one that imports. So each case means the same on a host with or
without PyYAML. The no-Python case runs the installer with a PATH holding every command of the
caller's PATH except the `python*` ones. install.ps1 runs under pwsh where pwsh is installed (as
on the CI runners), with its downloaders shadowed; its source is read in every case.
"""
from __future__ import annotations

# test-census-subject: install.sh
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"
INSTALL_PS1 = REPO / "install.ps1"
INSTALL_MD = REPO / "docs" / "INSTALL.md"
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
PWSH = shutil.which("pwsh")
BASH = shutil.which("bash") or "/bin/bash"
INSTALL_CMD = "pip install pyyaml"
MARK = "stub-net:"


class InstallRequiresPyYamlTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.home.mkdir()
        self.project.mkdir()

    def _python_stub(self, importable: bool) -> Path:
        """A bin dir whose python3, python and py run this test's Python with a `yaml` module
        that imports (`importable`) or raises ImportError."""
        mods = self.root / ("yaml-ok" if importable else "yaml-broken")
        mods.mkdir()
        (mods / "yaml.py").write_text(
            "" if importable else "raise ImportError(\"No module named 'yaml'\")\n",
            encoding="utf-8")
        stubs = self.root / ("bin-ok" if importable else "bin-broken")
        stubs.mkdir()
        for name in ("python3", "python", "py"):
            stub = stubs / name
            stub.write_text(f'#!/bin/sh\nPYTHONPATH="{mods}" exec "{sys.executable}" "$@"\n',
                            encoding="utf-8")
            stub.chmod(0o755)
        return stubs

    def _path_without_python(self) -> str:
        """Every command on the caller's PATH except the python* ones, linked into one dir."""
        linked = self.root / "bin-nopython"
        linked.mkdir()
        for d in os.environ.get("PATH", "/usr/bin:/bin").split(os.pathsep):
            if not os.path.isdir(d):
                continue
            for entry in os.scandir(d):
                if entry.name.startswith("python") or (linked / entry.name).exists():
                    continue
                if os.access(entry.path, os.X_OK) and not entry.is_dir():
                    (linked / entry.name).symlink_to(entry.path)
        return str(linked)

    def _install_sh(self, path: str) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        env.update({"PATH": path, "HOME": str(self.home)})
        return subprocess.run(
            [BASH, str(INSTALL_SH), "--from", str(SKILL), "--local", "--target", "claude",
             "--no-sweep"],
            capture_output=True, text=True, env=env, cwd=str(self.project), timeout=120)

    def _skill_files(self) -> list[Path]:
        return [p for base in (self.project, self.home) for p in base.rglob("SKILL.md")]

    def test_install_sh_refuses_when_pyyaml_cannot_be_imported(self) -> None:
        """AC1. MUTANT: no check, so the install completes without PyYAML. MUTANT: a check of
        `command -v python3` alone, which the broken interpreter passes. MUTANT: the check
        placed after the copy, which refuses but leaves the copy behind."""
        broken = f"{self._python_stub(importable=False)}:{os.environ.get('PATH', '')}"
        for case, path in (("python3 cannot import yaml", broken),
                           ("no python3 on PATH", self._path_without_python())):
            with self.subTest(case=case):
                proc = self._install_sh(path)
                out = proc.stdout + proc.stderr
                self.assertNotEqual(0, proc.returncode, out)
                self.assertIn("PyYAML", proc.stderr, out)
                self.assertIn(INSTALL_CMD, proc.stderr, out)
                self.assertEqual([], self._skill_files(), f"a refusal left a copy behind:\n{out}")

    def test_install_sh_installs_when_pyyaml_imports(self) -> None:
        """AC2, the control. MUTANT: a check that refuses every machine."""
        path = f"{self._python_stub(importable=True)}:{os.environ.get('PATH', '')}"
        proc = self._install_sh(path)
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        self.assertNotIn("PyYAML", out, out)
        self.assertTrue((self.project / ".claude" / "skills" / "sdlc-studio" / "SKILL.md")
                        .is_file(), out)

    def test_install_ps1_checks_pyyaml_before_its_first_copy(self) -> None:
        """AC3. MUTANT: no check in install.ps1, so the PowerShell install completes where the
        shell install refuses. MUTANT: the check after the first download or copy. MUTANT: a
        failed check that warns and carries on instead of stopping the script."""
        src = INSTALL_PS1.read_text(encoding="utf-8")
        body = src[src.index("function Invoke-Install"):]
        checks = [m for m in re.finditer(r"function (Test-\w+) \{(.*?)\n    \}\n", body, re.S)
                  if "import yaml" in m.group(2)]
        self.assertEqual(1, len(checks), "install.ps1 has no check that Python imports yaml")
        name = checks[0].group(1)
        call = re.search(rf"if \([^\n]*-not \({name}\)\) \{{\s*throw \"([^\"]*)\"", body)
        self.assertIsNotNone(call, f"a failed {name} does not stop the script with a throw")
        self.assertIn("PyYAML", call.group(1))
        self.assertIn(INSTALL_CMD, call.group(1))
        for step in ("Invoke-RestMethod -Uri", "Invoke-WebRequest -Uri $AssetUrl",
                     "Invoke-WebRequest -Uri $Url", "Copy-Item -Path $SourceDir"):
            self.assertLess(call.start(), body.index(step), f"the check comes after {step}")
        if PWSH:
            self._ps1_executed()

    def _ps1_executed(self) -> None:
        stubs = self._python_stub(importable=False)
        runner = self.root / "run.ps1"
        runner.write_text(
            "function Invoke-RestMethod { param([string]$Uri, [switch]$UseBasicParsing,"
            " [int]$TimeoutSec)\n"
            f"    Write-Host \"{MARK} $Uri\"; throw 'stubbed: no network' }}\n"
            "function Invoke-WebRequest { param([string]$Uri, [string]$OutFile,"
            " [switch]$UseBasicParsing)\n"
            f"    Write-Host \"{MARK} $Uri\"; throw 'stubbed: no network' }}\n"
            f"try {{ & '{INSTALL_PS1}' -Target claude -Local -NoSweep -Version v9.9.9 }}\n"
            "catch { Write-Host \"install failed: $($_.Exception.Message)\"; exit 1 }\n",
            encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        env.update({"PATH": f"{stubs}:{env.get('PATH', '')}", "HOME": str(self.home),
                    "NO_COLOR": "1", "POWERSHELL_TELEMETRY_OPTOUT": "1",
                    "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"})
        proc = subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(runner)],
                              cwd=str(self.project), env=env, capture_output=True, text=True,
                              timeout=180)
        out = proc.stdout + proc.stderr
        self.assertNotEqual(0, proc.returncode, out)
        self.assertIn("PyYAML", out, out)
        self.assertIn(INSTALL_CMD, out, out)
        self.assertNotIn(MARK, out, f"install.ps1 reached the network before the check:\n{out}")
        self.assertEqual([], self._skill_files(), out)

    def test_the_install_page_names_pyyaml_as_required(self) -> None:
        """AC4. MUTANT: the page at grooming, which lists PyYAML as an optional dependency the
        scripts degrade without, and calls them standard library only."""
        page = " ".join(INSTALL_MD.read_text(encoding="utf-8").split())
        sentences = re.split(r"(?<=[.!?;])\s+", page)
        self.assertTrue(any("PyYAML" in s and "required" in s for s in sentences),
                        "no sentence names PyYAML as required")
        self.assertIn(INSTALL_CMD, page, "the page gives no command that installs PyYAML")
        for s in sentences:
            if "PyYAML" in s:
                self.assertNotIn("optional", s.lower(), s)
        lowered = page.lower()
        for claim in ("degrade to the built-in defaults", "degrade to built-in defaults",
                      "standard library only", "pure standard library", "pure-stdlib", "stdlib only"):
            self.assertNotIn(claim, lowered, f"the page still says: {claim}")


if __name__ == "__main__":
    unittest.main()
