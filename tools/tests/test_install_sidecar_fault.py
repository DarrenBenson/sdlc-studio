"""BG1543: a sha256 sidecar that cannot be fetched refuses the install; only a 404 is an absence.

install.sh fetched the digest with a best-effort reader that discarded every error, so a 503, a
rate-limiting 429 or a dropped connection on the sidecar of a release asset it had just
downloaded read as "no sha256 published" and the archive installed unverified. The sidecar is now
read with the same three-way status reader the asset is: a 2xx verifies, a 404 on the source
archive fallback (where nothing is published) warns and proceeds, and anything else refuses,
naming the fault.

HOW THEY RUN. A real HTTP server on 127.0.0.1 answers each path with the status a test sets, and
a `curl` first on PATH rewrites `https://github.com/` to that server and hands every argument on
to the real curl, so the installer's own status reading meets real responses. Nothing reaches
the network, and no base-URL switch is added to the installer for a test's benefit.
"""
from __future__ import annotations

# test-census-subject: install.sh
import hashlib
import http.server
import io
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import threading
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"
INSTALL_PS1 = REPO / "install.ps1"
INSTALL_MD = REPO / "docs" / "INSTALL.md"
TAG = "v9.9.9"
ASSET = f"/DarrenBenson/sdlc-studio/releases/download/{TAG}/sdlc-studio-{TAG}.tar.gz"
ARCHIVE = f"/DarrenBenson/sdlc-studio/archive/refs/tags/{TAG}.tar.gz"
ABSENCE = "No published sha256"
REFUSAL = "could not fetch the published sha256"
#: A route answered by closing the connection with no reply: a transport fault, not a status.
RESET = "reset"

PS_ASSET = f"https://github.com/DarrenBenson/sdlc-studio/releases/download/{TAG}/sdlc-studio-{TAG}.zip"
PS_ARCHIVE = f"https://github.com/DarrenBenson/sdlc-studio/archive/refs/tags/{TAG}.zip"
PS_MAIN = "https://github.com/DarrenBenson/sdlc-studio/archive/refs/heads/main.zip"
#: What install.ps1's sidecar refusal must decide, as (status, $Url, $AssetUrl, refuses). A
#: status of None is a fetch with no response (a dropped connection or an empty sidecar). Only
#: a 404 beside the source archive or `main`, where no sidecar is published, is an absence;
#: the release asset's sidecar is published with it, so even its 404 refuses.
SIDECAR_CASES = (
    (404, PS_ARCHIVE, PS_ASSET, False),
    (404, PS_MAIN, None, False),
    (404, PS_ASSET, PS_ASSET, True),
    (503, PS_ASSET, PS_ASSET, True),
    (503, PS_ARCHIVE, PS_ASSET, True),
    (429, PS_MAIN, None, True),
    (None, PS_ASSET, PS_ASSET, True),
    (None, PS_ARCHIVE, PS_ASSET, True),
)
_PS_TOKEN = re.compile(r"\s*(\$code|\$Url|\$AssetUrl|\$null|-ne|-eq|-or|-and|-not|\d+|[()])")
_PS_PYTHON = {"$code": "code", "$Url": "url", "$AssetUrl": "asset", "$null": "None",
              "-ne": "!=", "-eq": "==", "-or": "or", "-and": "and", "-not": "not"}


def ps_refuses(condition: str, code: int | None, url: str, asset: str | None) -> bool:
    """Decide install.ps1's PowerShell refusal condition for one case, its operators read as
    Python's. A token outside that small set, or `-and` beside `-or` (equal precedence in
    PowerShell, not in Python), fails the read rather than being guessed at."""
    tokens, pos = [], 0
    while pos < len(condition.rstrip()):
        m = _PS_TOKEN.match(condition, pos)
        if not m:
            raise AssertionError(f"install.ps1's refusal condition has a construct this read "
                                 f"does not model at {condition[pos:]!r}")
        tokens.append(m.group(1))
        pos = m.end()
    if "-and" in tokens and "-or" in tokens:
        raise AssertionError(f"install.ps1's refusal condition mixes -and and -or: {condition!r}")
    expr = " ".join(_PS_PYTHON.get(t, t) for t in tokens)
    return bool(eval(expr, {"__builtins__": {}}, {"code": code, "url": url, "asset": asset}))


def _tarball(marker: str) -> bytes:
    """A release asset shaped as the installer extracts it: one sdlc-studio-<ver>/ at the top."""
    files = {
        "sdlc-studio-9.9.9/.claude/skills/sdlc-studio/SKILL.md":
            f"---\nname: sdlc-studio\n---\n{marker}\n",
        "sdlc-studio-9.9.9/.claude/skills/sdlc-studio/templates/version.yaml":
            'skill_version: "9.9.9"\n',
    }
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, text in files.items():
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


class _Origin(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - the stdlib's name
        self.server.hits.append(self.path)
        status, body = self.server.routes.get(self.path, (404, b"Not Found"))
        if status == RESET:
            self.close_connection = True
            return
        self.send_response(status)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args) -> None:
        pass


class InstallSidecarFaultTests(unittest.TestCase):
    def setUp(self) -> None:
        real_curl = shutil.which("curl")
        self.assertIsNotNone(real_curl, "these tests drive the real curl through a local server")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Origin)
        self.server.routes = {}
        self.server.hits = []
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        port = self.server.server_address[1]
        stubs = self.root / "bin"
        stubs.mkdir()
        shim = stubs / "curl"
        shim.write_text(
            "#!/usr/bin/env bash\nargs=()\nfor a in \"$@\"; do\n"
            f"  case \"$a\" in https://github.com/*) a=\"http://127.0.0.1:{port}/${{a#https://github.com/}}\" ;; esac\n"
            "  args+=(\"$a\")\ndone\n"
            f"exec {real_curl} \"${{args[@]}}\"\n", encoding="utf-8")
        shim.chmod(0o755)
        self.path = f"{stubs}:{os.environ.get('PATH', '/usr/bin:/bin')}"
        self.asset = _tarball("MARKER-FROM-THE-ASSET")
        self.digest = hashlib.sha256(self.asset).hexdigest()
        self.archive = _tarball("MARKER-FROM-THE-ARCHIVE")
        self.runs = 0

    def serve(self, path: str, status, body: bytes | str = b"") -> None:
        self.server.routes[path] = (status, body.encode() if isinstance(body, str) else body)

    def install(self) -> tuple[subprocess.CompletedProcess, Path]:
        """Run the default (unpinned, not required) verified install of TAG into a fresh HOME."""
        self.runs += 1
        home = self.root / f"home{self.runs}"
        home.mkdir()
        env = {k: v for k, v in os.environ.items()
               if k not in ("SDLC_STUDIO_SHA256", "SDLC_STUDIO_REQUIRE_CHECKSUM")
               and not k.lower().endswith("_proxy")}
        env.update({"PATH": self.path, "HOME": str(home), "NO_PROXY": "127.0.0.1"})
        proc = subprocess.run(
            ["bash", str(INSTALL_SH), "--version", TAG, "--target", "claude", "--no-sweep"],
            capture_output=True, text=True, env=env, cwd=str(self.root), timeout=120)
        return proc, home / ".claude" / "skills" / "sdlc-studio" / "SKILL.md"

    def test_a_faulted_sidecar_beside_a_good_asset_refuses_the_install(self) -> None:
        """AC1. MUTANT: HEAD's best-effort sidecar read, which takes a 503 for an absence, warns
        and installs. MUTANT: a refusal that does not name the fault (each status is asserted,
        and a dropped connection is named as a transport error). MUTANT: warn and proceed on a
        404 beside the release asset, whose sidecar the release workflow always publishes."""
        for fault, named in (("503", "HTTP 503"), ("429", "HTTP 429"), ("403", "HTTP 403"),
                             (RESET, "transport error")):
            with self.subTest(sidecar=fault):
                self.serve(ASSET, 200, self.asset)
                self.serve(ASSET + ".sha256", RESET if fault == RESET else int(fault),
                           f"{self.digest}  sdlc-studio-{TAG}.tar.gz\n")
                proc, skill = self.install()
                out = proc.stdout + proc.stderr
                self.assertIn(ASSET + ".sha256", self.server.hits, "the sidecar was never asked for")
                self.assertNotEqual(0, proc.returncode, out)
                self.assertIn(REFUSAL, proc.stderr.lower(), out)
                self.assertIn(named, proc.stderr, out)
                self.assertNotIn(ABSENCE, out, f"a fault was read as an absence:\n{out}")
                self.assertNotIn("Extracting", out, out)
                self.assertFalse(skill.exists(), f"a faulted sidecar still installed:\n{out}")
        with self.subTest(sidecar="404 beside the release asset"):
            self.serve(ASSET + ".sha256", 404, b"Not Found")
            proc, skill = self.install()
            out = proc.stdout + proc.stderr
            self.assertNotEqual(0, proc.returncode, out)
            self.assertIn("HTTP 404", proc.stderr, out)
            self.assertNotIn("installing unverified", out, out)
            self.assertFalse(skill.exists(), out)

    def test_a_true_absence_still_warns_and_a_good_sidecar_verifies(self) -> None:
        """AC2. MUTANT: refuse every non-2xx sidecar, a 404 on the fallback included. MUTANT:
        print the absence warning for a fault on the fallback's sidecar. MUTANT: drop the digest
        read from a 2xx, so a good sidecar no longer verifies."""
        with self.subTest(case="404 on the source archive fallback"):
            self.serve(ARCHIVE, 200, self.archive)          # no asset, no sidecar anywhere
            proc, skill = self.install()
            out = proc.stdout + proc.stderr
            self.assertIn(ARCHIVE + ".sha256", self.server.hits, out)
            self.assertEqual(0, proc.returncode, out)
            self.assertIn(f"{ABSENCE} for {TAG} - installing unverified", proc.stdout, out)
            self.assertIn("MARKER-FROM-THE-ARCHIVE", skill.read_text(encoding="utf-8"))
        with self.subTest(case="503 on the source archive fallback"):
            self.serve(ARCHIVE + ".sha256", 503, b"busy")
            proc, skill = self.install()
            out = proc.stdout + proc.stderr
            self.assertNotEqual(0, proc.returncode, out)
            self.assertIn("HTTP 503", proc.stderr, out)
            self.assertNotIn(ABSENCE, out, f"the absence warning named a 503:\n{out}")
            self.assertFalse(skill.exists(), out)
        with self.subTest(case="a correct sidecar beside the release asset"):
            self.serve(ASSET, 200, self.asset)
            self.serve(ASSET + ".sha256", 200, f"{self.digest}  sdlc-studio-{TAG}.tar.gz\n")
            proc, skill = self.install()
            out = proc.stdout + proc.stderr
            self.assertEqual(0, proc.returncode, out)
            self.assertIn(f"Checksum verified (sha256 {self.digest})", proc.stdout, out)
            self.assertNotIn(ABSENCE, out, out)
            self.assertIn("MARKER-FROM-THE-ASSET", skill.read_text(encoding="utf-8"))

    def test_install_ps1_and_the_install_page_tell_a_fault_from_an_absence(self) -> None:
        """AC3. MUTANT: HEAD's `catch { $expected = $null }`, which reads any failure as no
        sidecar. MUTANT: a catch that refuses a 404 on the fallback too. MUTANT: the page's
        claim that, without REQUIRE_CHECKSUM, an unverifiable download warns and proceeds.
        MUTANT: the refusal's `-or $Url -eq $AssetUrl` as `-and $Url -ne $AssetUrl`, as
        `-and $Url -eq $AssetUrl`, or as `-or $Url -ne $AssetUrl`."""
        src = INSTALL_PS1.read_text(encoding="utf-8")
        read = re.search(r'Invoke-WebRequest -Uri "\$Url\.sha256".*?\} catch \{(.*?)'
                         r'\n\s*if \(\$expected\) \{', src, re.S)
        self.assertIsNotNone(read, "install.ps1's sidecar read moved")
        catch = read.group(1)
        self.assertIn("$_.Exception.Response.StatusCode", catch, "the sidecar's status is not read")
        refusal = re.search(r"if \((?P<cond>[^\n]*)\)\s*\{\s*throw \(?\"Could not fetch the "
                            r"published sha256", catch)
        self.assertIsNotNone(refusal, "a failed sidecar fetch is not refused")
        self.assertIn("$expected = $null", catch[refusal.end():],
                      "a 404 on the fallback no longer reads as an absence")
        # The whole condition is decided, case by case, rather than matched by its first
        # clause: a regex on `$code -ne 404` passed `-and $Url -ne $AssetUrl`, which reads a
        # 503 on the release asset's own sidecar as no digest and installs unverified.
        for code, url, asset, refuses in SIDECAR_CASES:
            with self.subTest(status=code, sidecar_of=url, asset=asset):
                self.assertEqual(refuses, ps_refuses(refusal.group("cond"), code, url, asset),
                                 f"install.ps1 `if ({refusal.group('cond')})` decides a "
                                 f"{code or 'transport fault'} on the {url} sidecar wrongly")

        page = " ".join(INSTALL_MD.read_text(encoding="utf-8").split())
        sentences = re.split(r"(?<=[.!?])\s+", page)
        self.assertTrue(any("cannot be fetched" in s and "refuses the install" in s
                            for s in sentences),
                        "docs/INSTALL.md does not say a digest that cannot be fetched refuses")
        self.assertNotIn("an unverifiable download warns and proceeds", page,
                         "the page still says any unverifiable download warns and proceeds")


if __name__ == "__main__":
    unittest.main()
