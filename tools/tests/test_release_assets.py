"""BG0575: the release assets, and the verified install that consumes them.

README and the website offer `SDLC_STUDIO_REQUIRE_CHECKSUM=1` with a pinned tag as the path for a
reader who will not accept an unverified download. It could never complete: `install.sh` looked
for a `.sha256` beside GitHub's GENERATED source archive, and GitHub serves no such sidecar at any
version, so the digest resolved empty and the requirement made empty fatal.

WHY THESE TESTS INVOKE THE SCRIPT. A unit test of `verify_download` cannot see the defect - that
function is correct and always was, and the bug is the URL handed to it. The wiring is the part a
library test does not exercise, which is this repository's own scar, so the checks drive
`install.sh` end to end as a script.

WHY THEY READ THE WORKFLOW. Three things have to agree: the command the workflow builds an asset
with, the name it uploads it under, and the URL the installers fetch. A test that hardcodes its
own `git archive` asserts that git honours `--prefix` - a property of git, not of this repo - and
stays green while the workflow drifts. So `release_assets.build_commands` reads the real workflow
and the tests execute what it returns.

HOW THEY RUN OFFLINE. `install.sh` resolves its downloader with `command -v curl`, so a stub `curl`
earlier on PATH answers from a local origin keyed by URL. No base-URL argument is added to
production for a test's benefit: an override existing only to make a test passable is a hole in the
thing under test. The technique follows `test_install_atomic.py`, which shadows `cp` the same way.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import release_assets  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"
TAG = "v9.9.9"
BASE = "https://github.com/DarrenBenson/sdlc-studio"
ASSET_URL = f"{BASE}/releases/download/{TAG}/sdlc-studio-{TAG}.tar.gz"
ARCHIVE_URL = f"{BASE}/archive/refs/tags/{TAG}.tar.gz"

#: A stub `curl` answering from a directory of files named by their URL. It honours only the flags
#: install.sh passes, and reports an HTTP status the way real curl does under `-w`.
#: `HTTP_STATUS` lets a test say which status a given URL should answer with, so the difference
#: between 404 (absent, fall back) and 503 (a fault, refuse) is exercised rather than assumed.
CURL_STUB = r"""#!/usr/bin/env bash
url=""; dest=""; want_code=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -o) dest="$2"; shift 2 ;;
    -w) [[ "$2" == *http_code* ]] && want_code=1; shift 2 ;;
    -*) shift ;;
    *)  url="$1"; shift ;;
  esac
done
key="$ORIGIN/$(printf '%s' "$url" | tr -c 'A-Za-z0-9._-' '_')"
code=200
[[ -f "$key" ]] || code=404
if [[ -n "${FORCE_STATUS:-}" && "$url" == *"${FORCE_STATUS_URL:-/releases/download/}"* ]]; then
  code="$FORCE_STATUS"
fi
if [[ "${FORCE_TRANSPORT:-}" == 1 && "$url" == *"/releases/download/"* ]]; then exit 7; fi
if [[ "$code" == 200 ]]; then
  if [[ -n "$dest" ]]; then cp "$key" "$dest"; else cat "$key"; fi
fi
[[ "$want_code" == 1 ]] && printf '%s' "$code"
exit 0
"""


def _url_key(url: str) -> str:
    """The stub's filename for a URL, mirroring its `tr -c 'A-Za-z0-9._-' '_'` exactly.

    If the two ever drift the origin serves nothing and every fetch 404s. That failure is caught
    rather than silent: `test_the_origin_actually_serves` asserts the mapping round-trips, so a
    drift reddens THERE instead of quietly turning every other test vacuous.
    """
    return "".join(c if (c.isalnum() or c in "._-") else "_" for c in url)


class ReleaseAssetNaming(unittest.TestCase):
    """The names the workflow uploads must be the names the installers fetch."""

    def test_the_installers_fetch_exactly_the_names_the_workflow_publishes(self) -> None:
        """AC6. Mutant: change the asset filename in release.yml (or in either installer).
        Must redden.

        A rename breaks nothing visibly - the install just 404s, falls back to the generated
        archive, finds no digest and refuses. Nothing else in the suite would notice.
        """
        names = release_assets.asset_names(TAG)
        self.assertEqual(
            names,
            [f"sdlc-studio-{TAG}.tar.gz", f"sdlc-studio-{TAG}.tar.gz.sha256",
             f"sdlc-studio-{TAG}.zip", f"sdlc-studio-{TAG}.zip.sha256"])

        sh = INSTALL_SH.read_text(encoding="utf-8")
        ps = (REPO / "install.ps1").read_text(encoding="utf-8")
        # The URL each installer builds, with its shell/PowerShell variables resolved.
        self.assertIn("releases/download/$VERSION/sdlc-studio-$VERSION.tar.gz", sh)
        self.assertIn("releases/download/$Version/sdlc-studio-$Version.zip", ps)

        # Taken from each build command's own `-o` path, NOT from anywhere the name appears in
        # the workflow: the filename is repeated on the digest line, so a rename in the `-o`
        # alone leaves the string present and an "it is mentioned" assertion green while the
        # build writes something the installers will never find.
        self.assertEqual(
            release_assets.built_names(TAG),
            [f"sdlc-studio-{TAG}.tar.gz", f"sdlc-studio-{TAG}.zip"])


class WorkflowBuildCommands(unittest.TestCase):
    """The workflow's own build commands must produce what the installers extract."""

    def setUp(self) -> None:
        if not shutil.which("git"):
            self.skipTest("git not available")
        self.commands = release_assets.build_commands()

    def test_the_workflow_declares_a_build_command_per_published_format(self) -> None:
        """AC5a. Mutant: delete the zip build line from release.yml. Must redden."""
        self.assertEqual(len(self.commands), len(release_assets.FORMATS),
                         f"expected one git archive per format, got: {self.commands}")

    def test_each_workflow_command_builds_the_layout_the_installers_extract(self) -> None:
        """AC5b. Mutant: drop `--prefix` from either git archive line in release.yml.
        Must redden.

        The commands are READ FROM THE WORKFLOW and executed, not restated here. install.sh finds
        the tree with `find -maxdepth 1 -type d -name 'sdlc-studio-*'` and ship_changelog reads
        CHANGELOG.md as its sibling; install.ps1 does the equivalent with Get-ChildItem. A
        prefix-less archive explodes into the temp directory with no such directory and the
        install dies at the user with 'Failed to find extracted directory'.
        """
        with tempfile.TemporaryDirectory() as d:
            for command in self.commands:
                # The workflow's own line, with only the output path and the revision rewritten:
                # a fixture tag does not exist, and `dist/` is not this test's to write.
                resolved = release_assets.expand(command, TAG, outdir=d, ref="HEAD")
                self.assertIn("--prefix", resolved,
                              "expand() dropped the prefix, so this test would pass vacuously")
                proc = subprocess.run(["bash", "-c", resolved], cwd=str(REPO),
                                      capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, f"{resolved}\n{proc.stderr}")

            built = sorted(Path(d).iterdir())
            self.assertEqual(len(built), len(release_assets.FORMATS), f"built: {built}")
            for path in built:
                names = (tarfile.open(path).getnames() if path.name.endswith(".tar.gz")
                         else zipfile.ZipFile(path).namelist())
                tops = {n.split("/")[0] for n in names if n.strip("/")}
                self.assertEqual(tops, {f"sdlc-studio-{TAG.lstrip('v')}"},
                                 f"{path.name} must hold exactly one top directory")
                joined = "\n".join(names)
                self.assertIn(f"sdlc-studio-{TAG.lstrip('v')}/CHANGELOG.md", joined)
                self.assertIn(
                    f"sdlc-studio-{TAG.lstrip('v')}/.claude/skills/sdlc-studio/SKILL.md", joined)


class VerifiedInstall(unittest.TestCase):
    """Drive the real install.sh with REQUIRE_CHECKSUM=1 against a local origin."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

        self.origin = self.root / "origin"
        self.origin.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        self.tar_marker = self.root / "tar-was-called"

        self.asset = self._payload("MARKER-FROM-THE-ASSET", "asset.tar.gz")
        self.digest = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        # A DIFFERENT payload behind the generated-archive URL, so "what was installed came from
        # the asset" is proven directly rather than inferred from a missing sidecar.
        self.decoy = self._payload("MARKER-FROM-THE-GENERATED-ARCHIVE", "decoy.tar.gz")
        self.decoy_digest = hashlib.sha256(self.decoy.read_bytes()).hexdigest()

        stub_dir = self.root / "bin"
        stub_dir.mkdir()
        (stub_dir / "curl").write_text(CURL_STUB)
        (stub_dir / "curl").chmod(0o755)
        # A `tar` that records that it ran, then delegates. This is what makes "aborts BEFORE
        # extraction" observable: install.sh removes its temp directory on exit, so the absence of
        # an extracted tree proves nothing on its own.
        real_tar = shutil.which("tar")
        (stub_dir / "tar").write_text(
            f'#!/usr/bin/env bash\nprintf ran >> "{self.tar_marker}"\nexec {real_tar} "$@"\n')
        (stub_dir / "tar").chmod(0o755)
        self.stub_dir = stub_dir

    def _payload(self, marker: str, name: str) -> Path:
        stage = self.root / f"stage-{name}" / f"sdlc-studio-{TAG.lstrip('v')}"
        skill = stage / ".claude" / "skills" / "sdlc-studio"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"name: sdlc-studio\n{marker}\n")
        (stage / "CHANGELOG.md").write_text("# Changelog\n")
        out = self.root / name
        with tarfile.open(out, "w:gz") as tar:
            tar.add(stage, arcname=stage.name)
        return out

    def serve(self, url: str, payload) -> None:
        data = payload.encode() if isinstance(payload, str) else payload
        (self.origin / _url_key(url)).write_bytes(data)

    def serve_asset(self) -> None:
        self.serve(ASSET_URL, self.asset.read_bytes())
        self.serve(ASSET_URL + ".sha256", f"{self.digest}  sdlc-studio-{TAG}.tar.gz\n")

    def serve_decoy_archive(self) -> None:
        """The generated archive, with a VALID sidecar of its own.

        A fallback that reached this would succeed, so a test asserting only 'the install worked'
        cannot tell the two apart. That is the point.
        """
        self.serve(ARCHIVE_URL, self.decoy.read_bytes())
        self.serve(ARCHIVE_URL + ".sha256", f"{self.decoy_digest}\n")

    def run_install(self, require: str = "1", **extra_env) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env.update({"PATH": f"{self.stub_dir}:{env['PATH']}", "ORIGIN": str(self.origin),
                    "HOME": str(self.home), "SDLC_STUDIO_REQUIRE_CHECKSUM": require})
        env.pop("SDLC_STUDIO_SHA256", None)
        env.update({k: str(v) for k, v in extra_env.items()})
        return subprocess.run(
            ["bash", str(INSTALL_SH), "--version", TAG, "--target", "claude", "--no-sweep"],
            capture_output=True, text=True, env=env, cwd=str(self.root))

    @property
    def installed(self) -> Path:
        return self.home / ".claude" / "skills" / "sdlc-studio" / "SKILL.md"

    # ---------------------------------------------------------------- the criteria

    def test_the_origin_actually_serves(self) -> None:
        """Guards the harness itself: if CURL_STUB and _url_key drift, every fetch 404s and the
        tests below would pass for the wrong reason. This reddens instead."""
        self.serve_asset()
        proc = subprocess.run(["bash", str(self.stub_dir / "curl"), "-fsSL", ASSET_URL + ".sha256"],
                              capture_output=True, text=True,
                              env={**os.environ, "ORIGIN": str(self.origin)})
        self.assertIn(self.digest, proc.stdout, "the stub and _url_key disagree on the filename")

    def test_the_documented_verified_install_completes_from_the_release_asset(self) -> None:
        """AC1. Mutant: drop the release-asset branch from prepare_source. Must redden.

        Asserts three things, because 'Checksum verified' alone also passes when the installer
        verified the WRONG bytes correctly: exit 0, the digest printed is the ASSET's, and the
        installed file carries the asset's marker rather than the decoy's.
        """
        self.serve_asset()
        self.serve_decoy_archive()

        proc = self.run_install()

        self.assertEqual(proc.returncode, 0, f"{proc.stdout}\n{proc.stderr}")
        self.assertIn(f"Checksum verified (sha256 {self.digest})", proc.stdout)
        self.assertIn("MARKER-FROM-THE-ASSET", self.installed.read_text())
        self.assertNotIn("GENERATED-ARCHIVE", self.installed.read_text())

    def test_a_transport_error_on_the_asset_never_downgrades_to_the_unverified_archive(self) -> None:
        """AC2. Mutant: fall back on any non-zero from the asset fetch instead of only on absence.
        Must redden. The decoy is served WITH a valid sidecar, so a wrong fallback succeeds."""
        self.serve_asset()
        self.serve_decoy_archive()

        proc = self.run_install(FORCE_TRANSPORT=1)

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("transport error", (proc.stdout + proc.stderr).lower())
        self.assertFalse(self.installed.exists())

    def test_a_server_error_on_the_asset_is_not_read_as_a_missing_asset(self) -> None:
        """AC2b. Mutant: treat any HTTP status >= 400 as absence. Must redden.

        `curl -f` exits 22 for 403, 429, 500 and 503 as well as 404, so a rate limit or a CDN
        blip would otherwise be read as 'no asset published' and silently take the unverified
        archive. This is the difference between a fault and an absence.
        """
        self.serve_asset()
        self.serve_decoy_archive()

        proc = self.run_install(FORCE_STATUS=503)

        self.assertNotEqual(proc.returncode, 0, f"a 503 was treated as absence:\n{proc.stdout}")
        self.assertFalse(self.installed.exists())

    def test_a_tag_with_no_asset_falls_back_and_then_refuses_honestly(self) -> None:
        """AC3. Mutant: make the missing-digest branch warn and proceed. Must redden.

        Tags cut before the release workflow have no assets and no digest. A 404 SHOULD fall back;
        what must not happen is inventing verification for what it finds there.
        """
        self.serve(ARCHIVE_URL, self.decoy.read_bytes())   # no sidecar beside it

        proc = self.run_install()

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("No published sha256", proc.stderr)
        self.assertFalse(self.installed.exists())

    def test_a_corrupted_sidecar_aborts_before_extraction(self) -> None:
        """AC4. Mutant: remove the digest comparison, OR verify AFTER extraction. Must redden.

        The second mutant is the reason for the `tar` stub. install.sh deletes its temp directory
        on exit, so 'nothing was installed' cannot distinguish 'never extracted' from 'extracted
        then cleaned up' - and a docstring naming a mutant its test cannot kill is exactly the
        defect this repository blocks on.
        """
        self.serve(ASSET_URL, self.asset.read_bytes())
        self.serve(ASSET_URL + ".sha256", "deadbeef\n")

        proc = self.run_install()

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Checksum mismatch", proc.stderr)
        self.assertFalse(self.tar_marker.exists(),
                         "tar ran despite a digest mismatch - verification is not before extraction")
        self.assertFalse(self.installed.exists())

    def test_the_positive_control_does_reach_tar(self) -> None:
        """Without this, the assertion above passes for a build where tar is never called at all,
        which would make AC4 vacuous."""
        self.serve_asset()
        self.assertEqual(self.run_install().returncode, 0)
        self.assertTrue(self.tar_marker.exists(), "the successful install never invoked tar")


class WgetBranch(unittest.TestCase):
    """The wget half of `download_to`, which the curl-stubbed tests above never reach.

    A wget-only host is an ordinary minimal Linux image. This exercises the function directly
    rather than end to end: `command -v curl` is shadowed so install.sh takes the wget path. That
    is a NARROWER claim than the install-level tests above and is stated as such - it pins the
    status mapping and the partial-file cleanup, not the whole install.
    """

    def _run(self, script: str, **env) -> subprocess.CompletedProcess:
        with tempfile.TemporaryDirectory() as d:
            stub = Path(d) / "wget"
            stub.write_text(
                '#!/usr/bin/env bash\n'
                'dest=""\n'
                'while [[ $# -gt 0 ]]; do case "$1" in -O) dest="$2"; shift 2 ;; '
                '-*) shift ;; *) shift ;; esac; done\n'
                '[[ -n "$dest" ]] && printf partial > "$dest"\n'
                'echo "  HTTP/1.1 ${WGET_STATUS:-404} Not Found" >&2\n'
                'exit "${WGET_RC:-8}"\n')
            stub.chmod(0o755)
            driver = (
                f'source "{INSTALL_SH}"\n'
                'set +e\n'
                # Report curl as absent so download_to takes the wget branch.
                'command() { if [[ "$1" == "-v" && "$2" == "curl" ]]; then return 1; fi\n'
                '            builtin command "$@"; }\n'
                f'{script}\n')
            return subprocess.run(
                ["bash", "-c", driver], capture_output=True, text=True,
                env={**os.environ, "PATH": f"{d}:{os.environ['PATH']}", **{k: str(v) for k, v in env.items()}})

    def test_wget_reports_absence_as_absence_and_leaves_no_partial_file(self) -> None:
        """Mutant: drop the `rm -f "$dest"` from the wget branch. Must redden.

        wget -O writes a zero-length or partial file even when it fails; leaving it behind means a
        later `tar` reads a corrupt archive rather than seeing the absence it is.
        """
        proc = self._run(
            'd=$(mktemp -d); download_to "http://x/a.tar.gz" "$d/f"; echo "RC=$?"; '
            '[[ -e "$d/f" ]] && echo LEFTOVER || echo CLEAN', WGET_STATUS=404, WGET_RC=8)
        self.assertIn("RC=22", proc.stdout, proc.stdout + proc.stderr)
        self.assertIn("CLEAN", proc.stdout, "a partial file survived a failed wget")

    def test_wget_does_not_report_a_server_error_as_absence(self) -> None:
        """Mutant: return 22 for any wget exit 8. Must redden."""
        proc = self._run(
            'd=$(mktemp -d); download_to "http://x/a.tar.gz" "$d/f"; echo "RC=$?"',
            WGET_STATUS=503, WGET_RC=8)
        self.assertIn("RC=1", proc.stdout, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
