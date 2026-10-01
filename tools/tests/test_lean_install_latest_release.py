"""US0968: with no `--version`, install.sh installs the latest published release.

The default was `main`, which publishes no `.sha256`, so the README quick start installed
unverified. The installer now asks GitHub for the latest release and sends it down the tagged,
verified path; `--version main` keeps the old behaviour, and a failed lookup falls back to `main`
with one line saying so. Each test drives the real installer with a stub `curl` first on PATH
that answers the latest-release query and logs every URL it is asked for; nothing reaches the
network.
"""
from __future__ import annotations

# test-census-subject: install.sh
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALL_SH = REPO / "install.sh"
LATEST = "api.github.com/repos/DarrenBenson/sdlc-studio/releases/latest"

#: Logs each URL, answers the latest-release query from $LATEST_REPLY (or fails when it is
#: unset), and fails every other request.
CURL_STUB = """#!/bin/bash
url=""
for a in "$@"; do case "$a" in http*) url="$a" ;; esac; done
echo "$url" >> "$CURL_LOG"
case "$url" in
  *releases/latest*) [ -n "$LATEST_REPLY" ] && { printf '%s\\n' "$LATEST_REPLY"; exit 0; }; exit 22 ;;
esac
exit 22
"""


class InstallLatestReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        stubs = self.root / "bin"
        stubs.mkdir()
        curl = stubs / "curl"
        curl.write_text(CURL_STUB, encoding="utf-8")
        curl.chmod(0o755)
        self.log = self.root / "curl.log"
        self.home = self.root / "home"
        self.home.mkdir()
        self.path = f"{stubs}:{os.environ.get('PATH', '/usr/bin:/bin')}"

    def _install(self, *args: str, reply: str | None = '{"tag_name": "v9.9.9"}'
                 ) -> subprocess.CompletedProcess:
        env = {"PATH": self.path, "HOME": str(self.home), "CURL_LOG": str(self.log)}
        if reply is not None:
            env["LATEST_REPLY"] = reply
        return subprocess.run(["bash", str(INSTALL_SH), "--dry-run", "--no-sweep", *args],
                              capture_output=True, text=True, env=env, cwd=str(self.root),
                              timeout=60)

    def _queries(self) -> list[str]:
        if not self.log.exists():
            return []
        return [u for u in self.log.read_text(encoding="utf-8").split() if LATEST in u]

    def test_no_version_resolves_the_latest_release(self) -> None:
        """AC1. MUTANT: HEAD, which prints `Version: main` and asks nothing."""
        proc = self._install()
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("Version: v9.9.9", proc.stdout)
        self.assertEqual(1, len(self._queries()), "the latest release was not asked for once")

    def test_version_main_is_installed_only_when_asked(self) -> None:
        """AC2. MUTANT: resolve the latest release whatever `--version` says."""
        proc = self._install("--version", "main")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("Version: main", proc.stdout)
        self.assertEqual([], self._queries())

    def test_an_unresolvable_latest_falls_back_to_main(self) -> None:
        """AC3. MUTANT: abort the install when the lookup fails. MUTANT: fall back silently -
        the line saying the latest release could not be resolved is required. MUTANT: accept a
        reply that names no usable tag - a junk body must fall back too."""
        for reply in (None, '{"message": "API rate limit exceeded"}', '{"tag_name": "v1 ; rm"}'):
            with self.subTest(reply=reply):
                proc = self._install(reply=reply)
                out = proc.stdout + proc.stderr
                self.assertEqual(0, proc.returncode, out)
                self.assertIn("Version: main", proc.stdout)
                self.assertEqual(1, out.count("could not resolve the latest release"), out)

    def test_the_docs_no_longer_say_the_default_tracks_main(self) -> None:
        """AC4. MUTANT: HEAD's README.md:82 and docs/INSTALL.md:178."""
        for rel in ("README.md", "docs/INSTALL.md"):
            text = " ".join((REPO / rel).read_text(encoding="utf-8").split())
            with self.subTest(file=rel):
                self.assertFalse("default install tracks `main`" in text,
                                 f"{rel} still says the default install tracks main")


if __name__ == "__main__":
    unittest.main()
