"""BG0934: with no `-Version`, install.ps1 installs the latest release, as install.sh does.

US0968 sent a plain `install.sh` to the latest published release, but install.ps1 still
defaulted to `main`, so a Windows user got unreleased, unverified code by default. install.ps1
now asks the same endpoint, accepts the same tag shape, and falls back to `main` with the same
line when the lookup fails; `-Version main` still installs `main`.

`pwsh` is not on every machine this suite runs on, and a real run would reach the network, so
the script's default resolution is read off its source, against what install.sh reads from its
own: the endpoint, the tag check and the fallback line are taken from install.sh, not restated.
"""
from __future__ import annotations

# test-census-subject: install.ps1
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_PS1 = REPO / "install.ps1"
INSTALL_SH = REPO / "install.sh"


class InstallPs1DefaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ps1 = INSTALL_PS1.read_text(encoding="utf-8")
        sh = INSTALL_SH.read_text(encoding="utf-8")
        api = re.search(r'local api="(https://[^"]+/releases/latest)"', sh)
        tag = re.search(r'\[\[ "\$tag" =~ (\^\S+\$) \]\]', sh)
        warn = re.search(r'warn "(could not resolve the latest release[^"]*?) - installing', sh)
        for what, m in (("endpoint", api), ("tag check", tag), ("fallback line", warn)):
            self.assertIsNotNone(m, f"premise: install.sh's latest-release {what} moved")
        self.api = api.group(1).replace("$REPO", "$Repo")
        self.tag_re = tag.group(1)
        self.warn = warn.group(1)

    def test_install_ps1_defaults_to_the_latest_release(self) -> None:
        """AC1. MUTANT: HEAD's `[string]$Version = 'main'`, which installs main and asks for
        no release. The control the criterion names: an explicit `-Version main` skips the
        lookup and still takes the branch archive, not a tag."""
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
        self.assertIn(f'"{self.api}"', lookup, "not install.sh's latest-release endpoint")
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
