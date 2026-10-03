"""BG0934: with no `-Version`, install.ps1 installs the latest release, as install.sh does.

US0968 sent a plain `install.sh` to the latest published release, but install.ps1 still
defaulted to `main`, so a Windows user got unreleased, unverified code by default. install.ps1
now asks the same endpoint, accepts the same tag shape, and falls back to `main` with the same
line when the lookup fails; `-Version main` still installs `main`.

Where `pwsh` is on PATH, as it is on the CI runners, install.ps1 RUNS (a dry run) with
Invoke-RestMethod shadowed by a function in the invoking scope, as the BG0575 CI step shadows
Invoke-WebRequest: offline and deterministic, and only a run can tell a tag that is fetched and
then used from one that is fetched and discarded, or a lookup call that always throws into its
catch. Where pwsh is absent the same claims are read off the script's source instead, so the
Verify selector never passes on a skip. The endpoint, the tag check and the fallback line are
taken from install.sh, not restated.
"""
from __future__ import annotations

# test-census-subject: install.ps1
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_PS1 = REPO / "install.ps1"
INSTALL_SH = REPO / "install.sh"
PWSH = shutil.which("pwsh")

# Bodies for the stubbed Invoke-RestMethod. The stub declares the parameters install.ps1 passes,
# so a misspelt or mistyped one fails to bind and lands in install.ps1's catch, as a broken real
# call would; its first act is to print the endpoint it was asked for.
STUB_RELEASE = "return [pscustomobject]@{ tag_name = 'v9.9.9' }"
STUB_OFFLINE = "throw 'stubbed: no network'"
STUB_MARK = "stub-irm:"


def _ps_arg(arg: str) -> str:
    return arg if arg.startswith("-") else "'" + arg.replace("'", "''") + "'"


def run_install_ps1(argv, *, stub: str = STUB_RELEASE, home: Path, cwd: Path,
                    env: dict | None = None) -> subprocess.CompletedProcess:
    """Run install.ps1 with `argv` under pwsh, Invoke-RestMethod answered by `stub`, offline.

    The function is defined in the invoking script, so install.ps1 (a child scope) finds it
    ahead of the cmdlet - the BG0575 CI technique. `env` replaces the environment; HOME is
    always the caller's throwaway one."""
    run_dir = Path(tempfile.mkdtemp(prefix="irm_stub_"))
    try:
        runner = run_dir / "run.ps1"
        runner.write_text(
            "function Invoke-RestMethod {\n"
            "    [CmdletBinding()]\n"
            "    param([Parameter(Mandatory)][string]$Uri, [switch]$UseBasicParsing,\n"
            "          [int]$TimeoutSec)\n"
            f"    Write-Host \"{STUB_MARK} $Uri\"\n"
            f"    {stub}\n"
            "}\n"
            f"& {_ps_arg(str(INSTALL_PS1))} {' '.join(_ps_arg(a) for a in argv)}\n",
            encoding="utf-8")
        base = dict(os.environ) if env is None else dict(env)
        base.update({"HOME": str(home), "NO_COLOR": "1", "POWERSHELL_TELEMETRY_OPTOUT": "1",
                     "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"})
        return subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(runner)],
                              cwd=cwd, env=base, capture_output=True, text=True, timeout=120)
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)


class InstallPs1DefaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ps1 = INSTALL_PS1.read_text(encoding="utf-8")
        sh = INSTALL_SH.read_text(encoding="utf-8")
        api = re.search(r'local api="(https://[^"]+/releases/latest)"', sh)
        tag = re.search(r'\[\[ "\$tag" =~ (\^\S+\$) \]\]', sh)
        warn = re.search(r'warn "(could not resolve the latest release[^"]*?) - installing', sh)
        for what, m in (("endpoint", api), ("tag check", tag), ("fallback line", warn)):
            self.assertIsNotNone(m, f"premise: install.sh's latest-release {what} moved")
        repo = re.search(r'^REPO="([^"]+)"', sh, re.M)
        self.assertIsNotNone(repo, "premise: install.sh's REPO moved")
        self.api = api.group(1)
        self.api_url = self.api.replace("$REPO", repo.group(1))
        self.tag_re = tag.group(1)
        self.warn = warn.group(1)

    def test_install_ps1_defaults_to_the_latest_release(self) -> None:
        """AC1. MUTANTS: HEAD~'s `[string]$Version = 'main'`; the resolved tag discarded
        (`$Version = $latest` -> `'main'`); a lookup call that always throws (a bad parameter on
        Invoke-RestMethod). The control: an explicit `-Version main` makes no lookup."""
        if PWSH:
            self._executed()
        else:
            # pwsh is not on PATH here, so install.ps1 cannot run; its source is read instead.
            # The executing arm runs wherever pwsh is installed, as on the CI runners.
            self._static()

    def _run(self, *argv: str, stub: str = STUB_RELEASE) -> str:
        base = Path(tempfile.mkdtemp(prefix="bg0934_")).resolve()
        self.addCleanup(shutil.rmtree, base, True)
        (base / "home").mkdir()
        (base / "project").mkdir()
        cp = run_install_ps1(["-Target", "claude", "-Local", "-NoSweep", "-DryRun", *argv],
                             stub=stub, home=base / "home", cwd=base / "project")
        out = cp.stdout + cp.stderr
        self.assertEqual(0, cp.returncode, out)
        return out

    def _version(self, out: str) -> str:
        found = re.findall(r"^==> Version: (\S+)\s*$", out, re.M)
        self.assertEqual(1, len(found), f"no single Version line:\n{out}")
        return found[0]

    def _executed(self) -> None:
        # A published release: its tag is what gets installed, asked of install.sh's endpoint.
        out = self._run()
        self.assertIn(f"{STUB_MARK} {self.api_url}", out,
                      f"the lookup never reached Invoke-RestMethod at install.sh's endpoint:\n{out}")
        self.assertEqual("v9.9.9", self._version(out),
                         f"the latest release was looked up but not installed:\n{out}")
        self.assertNotIn(self.warn, out)
        # The lookup fails (offline, rate-limited): main, and a line saying so.
        out = self._run(stub=STUB_OFFLINE)
        self.assertEqual("main", self._version(out), out)
        self.assertIn(self.warn, out, f"the fallback to main is silent:\n{out}")
        # A tag install.sh's check refuses is no answer either.
        out = self._run(stub="return [pscustomobject]@{ tag_name = 'v1/../x' }")
        self.assertIsNone(re.fullmatch(self.tag_re, "v1/../x"), "premise: the bad tag is valid")
        self.assertEqual("main", self._version(out), out)
        self.assertIn(self.warn, out)
        # An explicit main installs main and asks nothing.
        out = self._run("-Version", "main")
        self.assertNotIn(STUB_MARK, out, f"-Version main still looked up a release:\n{out}")
        self.assertEqual("main", self._version(out), out)
        self.assertNotIn(self.warn, out)

    def _static(self) -> None:
        param = re.search(r"^param\((.*?)^\)", self.ps1, re.S | re.M)
        self.assertIsNotNone(param, "install.ps1's param block moved")
        default = re.search(r"\[string\]\$Version(?:\s*=\s*'([^']*)')?", param.group(1))
        self.assertIsNotNone(default, "install.ps1 takes no -Version")
        self.assertEqual("", default.group(1) or "",
                         "with no -Version install.ps1 installs a fixed version, not the latest")

        body = self.ps1.split("function Invoke-Install", 1)[1]
        guard = re.search(r"if \(-not \$Uninstall -and -not \$Version\) \{(.*?)\n    \}\n",
                          body, re.S)
        self.assertIsNotNone(guard, "no latest-release lookup runs when no -Version is given")
        lookup = guard.group(1)
        self.assertIn(f'"{self.api.replace("$REPO", "$Repo")}"', lookup,
                      "not install.sh's latest-release endpoint")
        self.assertIn("tag_name", lookup)
        self.assertIn(f"-match '{self.tag_re}'", lookup, "not install.sh's tag check")
        self.assertIn("$Version = 'main'", lookup, "a failed lookup does not fall back to main")
        self.assertIn(self.warn, lookup, "the fallback to main is silent")

        at = body.index(guard.group(0))
        self.assertLess(at, body.index('Write-Info "Version: $Version"'),
                        "the version is printed before it is resolved")
        self.assertLess(at, body.index("$Url = "), "the download URL is built before it")
        # An explicit `main` never reaches the lookup (the guard reads an empty $Version) and
        # still takes the branch archive, with no release asset.
        self.assertIn("$Url = \"https://github.com/$Repo/archive/refs/heads/$Version.zip\"", body)
        self.assertIn("if ($Version -ne 'main') {", body)
        self.assertNotIn("(default: main)", self.ps1, "the help still names main the default")


if __name__ == "__main__":
    unittest.main()
