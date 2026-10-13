"""BG0976: the pre-push hook prints its ssh keepalive advice only when no keepalive is in force.

It printed on every push, including from a clone where `enable-hooks.sh` had just set
`core.sshCommand` with `ServerAliveInterval=60`, and advice that prints whether or not it applies
is advice people learn to skip. The hook now stays silent when `core.sshCommand` carries a
keepalive at any scope, or when `ssh -G <host>` resolves one for an ssh remote.

Each test drives the hook through `test_pre_push_hook._Clone`, whose PATH holds only git, bash,
python3 and a `gh` stub, and whose git config is the clone's own (the global and system files
are pointed at /dev/null), so this machine's own `core.sshCommand` cannot decide anything. The
`ssh -G` case puts a stub `ssh` on that PATH that answers a fixed resolved configuration, so the
machine's own `~/.ssh/config` cannot answer either.

MUTANTS: the advice printed unconditionally again (AC1); the advice never printed (AC2); the
`core.sshCommand` read dropped, or the `ssh -G` read dropped (AC1, one each).
"""
# test-census-subject: .githooks/pre-push
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_pre_push_hook as hook  # noqa: E402 - the hook's fixture, shared

ADVICE = "the connection must stay up across the gate"

#: The git locations the hook's environment is scrubbed of, held equal to every other hook
#: fixture's list by test_skill_tests_env.ScrubListsAgreeTests.
_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)

#: `ssh -G <host>` as a stub: the resolved configuration the test chooses, nothing else.
STUB_SSH = """#!/bin/sh
if [ "$1" = "-G" ]; then
  echo "hostname $2"
  echo "serveraliveinterval ${STUB_SSH_INTERVAL:-0}"
  exit 0
fi
exit 1
"""


class KeepaliveAdviceTests(unittest.TestCase):
    def _clone(self) -> hook._Clone:
        fx = hook._Clone()
        self.addCleanup(fx.cleanup)
        return fx

    def _hook(self, fx: hook._Clone, url: str, interval: str | None = None) -> str:
        """The hook run directly for one branch row, with `url` as the remote it pushes to, and
        with a stub `ssh` on its PATH resolving `serveraliveinterval` to `interval` when given."""
        path = fx.stub_path()
        if interval is not None:
            (path / "ssh").write_text(STUB_SSH, encoding="utf-8")
            (path / "ssh").chmod(0o755)
        env = {k: v for k, v in os.environ.items()
               if k not in _GIT_ENV_VARS and k not in ("SDLC_PUSH_ACK_RED", hook.BOUNDARY_MARKER)}
        env.update({"STUB_ARGV": str(fx.argv), "STUB_RC": "0", "PATH": str(path),
                    "STUB_GH_MODE": "empty", "STUB_GH_ARGV": str(fx.tmp / "gh-argv.txt"),
                    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                    "STUB_SSH_INTERVAL": interval or "0"})
        sha = hook._git(fx.clone, "rev-parse", "HEAD").stdout.strip()
        rows = f"refs/heads/main {sha} refs/heads/main {'0' * 40}\n"
        r = subprocess.run(["bash", ".githooks/pre-push", "origin", url], cwd=fx.clone,
                           input=rows, capture_output=True, text=True, env=env, timeout=300)
        return r.stderr

    def test_keepalive_warning_silent_when_configured(self) -> None:
        fx = self._clone()
        hook._git(fx.clone, "config", "core.sshCommand",
                  "ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=10")
        self.assertNotIn(ADVICE, self._hook(fx, str(fx.remote)),
                         "the advice printed though core.sshCommand carries a keepalive")

    def test_keepalive_warning_silent_when_ssh_resolves_one(self) -> None:
        fx = self._clone()
        self.assertNotIn(ADVICE, self._hook(fx, "git@example.invalid:o/r.git", interval="60"),
                         "the advice printed though `ssh -G` resolves a keepalive for the host")

    def test_keepalive_warning_when_absent(self) -> None:
        fx = self._clone()
        for url, interval in ((str(fx.remote), None), ("git@example.invalid:o/r.git", "0"),
                              ("ssh://git@example.invalid:22/o/r.git", "0")):
            with self.subTest(url=url):
                err = self._hook(fx, url, interval=interval)
                self.assertIn(ADVICE, err, f"no keepalive is in force and the advice is gone:\n{err}")
                self.assertIn("enable-hooks.sh", err)


if __name__ == "__main__":
    unittest.main()
