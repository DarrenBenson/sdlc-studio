"""BG0939: install.ps1 verifies a release asset whose `.sha256` sidecar arrives as bytes.

GitHub serves the sidecar as application/octet-stream, for which Invoke-WebRequest's `.Content`
is a byte array, not a string. install.ps1 split that array on whitespace and took the first
byte's decimal value as the digest, so every release install threw 'Checksum mismatch' before
extraction (main's windows-smoke step, once BG0934 made the latest release the default). The
sidecar is now read as text whatever its shape; the check itself stays.

Where `pwsh` is on PATH, as it is on the CI runners, install.ps1 RUNS a real local install with
Invoke-WebRequest and Invoke-RestMethod shadowed by functions in the invoking scope (the BG0575 CI
technique, as BG0934's test does): the asset download writes a small real zip, the sidecar answers
an object whose Content is a byte array, and nothing touches the network. Where pwsh is absent the
sidecar read is pinned on the script's source instead, so the Verify selector never passes on a
skip; that arm catches the raw `.Content` split coming back, but it cannot tell a decode that is
present from one that works.
"""
from __future__ import annotations

# test-census-subject: install.ps1
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_PS1 = REPO / "install.ps1"
PWSH = shutil.which("pwsh")
TAG = "v9.9.9"
MARK = "stub-iwr:"
REFUSAL = "Checksum mismatch"


def _ps_str(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def _release_zip(path: Path) -> str:
    """A minimal release asset: the tree install.ps1 extracts, copies and reads a version from.
    Returns its sha256 as sha256sum prints it (lower-case hex)."""
    root = f"sdlc-studio-{TAG}/.claude/skills/sdlc-studio"
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(f"{root}/SKILL.md", "---\nname: sdlc-studio\n---\n")
        zf.writestr(f"{root}/templates/version.yaml", 'skill_version: "9.9.9"\n')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_install(*, zip_path: Path, sidecar: str, as_bytes: bool, home: Path,
                cwd: Path) -> subprocess.CompletedProcess:
    """Run `install.ps1 -Target claude -Local -NoSweep` (no -Version, so the latest release) under
    pwsh, offline. The release lookup answers `TAG`; the asset download copies `zip_path`; the
    sidecar answers `sidecar` as the Content of an object, as a byte array when `as_bytes` (what
    GitHub's octet-stream gives) else a string. Any other URL throws."""
    run_dir = Path(tempfile.mkdtemp(prefix="iwr_stub_"))
    try:
        if as_bytes:
            content = f"[System.Text.Encoding]::UTF8.GetBytes({_ps_str(sidecar)})"
        else:
            content = _ps_str(sidecar)
        runner = run_dir / "run.ps1"
        runner.write_text(
            "function Invoke-RestMethod {\n"
            "    [CmdletBinding()]\n"
            "    param([Parameter(Mandatory)][string]$Uri, [switch]$UseBasicParsing,\n"
            "          [int]$TimeoutSec)\n"
            f"    return [pscustomobject]@{{ tag_name = '{TAG}' }}\n"
            "}\n"
            "function Invoke-WebRequest {\n"
            "    [CmdletBinding()]\n"
            "    param([Parameter(Mandatory)][string]$Uri, [string]$OutFile,\n"
            "          [switch]$UseBasicParsing)\n"
            f"    Write-Host \"{MARK} $Uri\"\n"
            "    if ($Uri -like '*.sha256') {\n"
            f"        return [pscustomobject]@{{ StatusCode = 200; Content = {content} }}\n"
            "    }\n"
            f"    if ($Uri -like '*/releases/download/{TAG}/sdlc-studio-{TAG}.zip' -and $OutFile) {{\n"
            f"        Copy-Item -LiteralPath {_ps_str(str(zip_path))} -Destination $OutFile\n"
            "        return\n"
            "    }\n"
            "    throw \"stubbed: no network for $Uri\"\n"
            "}\n"
            # A refusal is printed whole, on one line, rather than through pwsh's wrapped view.
            f"try {{ & {_ps_str(str(INSTALL_PS1))} -Target claude -Local -NoSweep }}\n"
            "catch { Write-Host \"install failed: $($_.Exception.Message)\"; exit 1 }\n",
            encoding="utf-8")
        env = dict(os.environ)
        env.pop("SDLC_STUDIO_SHA256", None)
        env.pop("SDLC_STUDIO_REQUIRE_CHECKSUM", None)
        env.update({"HOME": str(home), "NO_COLOR": "1", "POWERSHELL_TELEMETRY_OPTOUT": "1",
                    "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"})
        return subprocess.run([PWSH, "-NoProfile", "-NonInteractive", "-File", str(runner)],
                              cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)


class InstallPs1ChecksumBytesTests(unittest.TestCase):
    def test_a_byte_array_sidecar_verifies(self) -> None:
        """AC1. MUTANT: the sidecar's raw `.Content` split on whitespace (HEAD~'s read), which
        takes the first byte's decimal value as the digest and aborts on the matching sidecar.
        The control: a byte-array sidecar naming another digest still aborts before extraction,
        so a read that drops the check (or always passes it) fails too."""
        if PWSH:
            self._executed()
        else:
            # pwsh is not on PATH here, so install.ps1 cannot run; its source is read instead.
            # The executing arm runs wherever pwsh is installed, as on the CI runners.
            self._static()

    def _install(self, sidecar: str, *, as_bytes: bool = True):
        base = Path(tempfile.mkdtemp(prefix="bg0939_")).resolve()
        self.addCleanup(shutil.rmtree, base, True)
        for d in ("home", "project"):
            (base / d).mkdir()
        zip_path = base / "asset.zip"
        digest = _release_zip(zip_path)
        cp = run_install(zip_path=zip_path, sidecar=sidecar.format(digest=digest),
                         as_bytes=as_bytes, home=base / "home", cwd=base / "project")
        skill = base / "project" / ".claude" / "skills" / "sdlc-studio" / "SKILL.md"
        return cp, cp.stdout + cp.stderr, skill, digest

    def _executed(self) -> None:
        # The shape GitHub serves: the real digest, then the file name, as sha256sum writes it.
        cp, out, skill, digest = self._install(f"{{digest}}  sdlc-studio-{TAG}.zip\n")
        self.assertIn(f"{MARK} https://github.com/", out, f"the stub was never reached:\n{out}")
        self.assertIn(f"/releases/download/{TAG}/sdlc-studio-{TAG}.zip.sha256", out,
                      f"the asset's sidecar was never asked for:\n{out}")
        self.assertNotIn(REFUSAL, out, f"a matching byte-array sidecar was refused:\n{out}")
        self.assertEqual(0, cp.returncode, out)
        self.assertIn(f"Checksum verified (sha256 {digest.upper()})", out, out)
        self.assertTrue(skill.is_file(), f"the install did not complete:\n{out}")

        # The neighbour: a sidecar that arrives as a string (a text/plain answer) still verifies.
        cp, out, skill, _ = self._install(f"{{digest}}  sdlc-studio-{TAG}.zip\n", as_bytes=False)
        self.assertEqual(0, cp.returncode, out)
        self.assertNotIn(REFUSAL, out, out)
        self.assertTrue(skill.is_file(), f"a string sidecar no longer installs:\n{out}")

        # The control: a byte-array sidecar naming another digest aborts before extraction.
        other = hashlib.sha256(b"not the asset").hexdigest()
        cp, out, skill, digest = self._install(f"{other}  sdlc-studio-{TAG}.zip\n")
        self.assertNotEqual(0, cp.returncode, f"a wrong digest installed:\n{out}")
        self.assertIn(f"{REFUSAL} for {TAG}: expected {other}, got {digest.upper()}", out, out)
        self.assertNotIn("Extracting...", out, f"the zip was extracted before the check:\n{out}")
        self.assertFalse(skill.exists(), f"a wrong digest still installed:\n{out}")

    def _static(self) -> None:
        src = INSTALL_PS1.read_text(encoding="utf-8")
        read = re.search(r"if \(-not \$expected\) \{\s*try \{(.*?)\} catch \{", src, re.S)
        self.assertIsNotNone(read, "install.ps1's sidecar read moved")
        body = read.group(1)
        self.assertIn('Invoke-WebRequest -Uri "$Url.sha256"', body, "the sidecar is not fetched")
        held = re.search(r"\$(\w+) = \(?Invoke-WebRequest -Uri \"\$Url\.sha256\"[^\n]*\)?"
                         r"\.Content\s*\n", body)
        self.assertIsNotNone(held, "the sidecar's Content is not held")
        name = held.group(1)
        decode = re.search(rf"if \(\${name} -is \[byte\[\]\]\) \{{ \${name} = "
                           rf"\[System\.Text\.Encoding\]::UTF8\.GetString\(\${name}\) \}}", body)
        self.assertIsNotNone(decode, "a byte-array sidecar is split without being decoded")
        split = re.search(rf"\$expected = \(\"\${name}\"\.Trim\(\) -split '\\s\+'\)\[0\]", body)
        self.assertIsNotNone(split, "the digest is not the first field of the decoded text")
        self.assertLess(decode.start(), split.start(), "the sidecar is split before decoding")
        self.assertIn("if ($actual -ine $expected) {", src, "the checksum check is gone")


if __name__ == "__main__":
    unittest.main()
