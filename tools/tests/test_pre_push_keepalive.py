"""BG0976: the pre-push hook prints its ssh keepalive advice only when no keepalive is in force.

It printed on every push, including from a clone where `enable-hooks.sh` had just set
`core.sshCommand` with `ServerAliveInterval=60`, and advice that prints whether or not it applies
is advice people learn to skip. The hook now stays silent when the ssh command git will use
(GIT_SSH_COMMAND, else `core.sshCommand` at any scope) carries a positive keepalive, or when
`ssh -G <host>` resolves one for an ssh remote.

Each test drives the hook through `test_pre_push_hook._Clone`, whose PATH holds only git, bash,
python3 and a `gh` stub, and whose git config is the clone's own (the global and system files
are pointed at /dev/null, and configuration injected through the environment is dropped), so
this machine's own ssh settings cannot decide anything. The
`ssh -G` case puts a stub `ssh` on that PATH that answers a fixed resolved configuration, so the
machine's own `~/.ssh/config` cannot answer either.

MUTANTS, each failing a test AC1's or AC2's selector runs: the advice printed unconditionally
again, or never; the `core.sshCommand` read dropped, or GIT_SSH_COMMAND (which overrides it)
ignored; the `ssh -G` read dropped, its key test dropped (a real `ssh -G` prints `port 22`), its
host taken with the port or as the whole URL, or `git+ssh://` remotes not read as ssh; an interval
of zero read as a keepalive.
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

#: `ssh -G <host>` as a stub keyed on the host it is asked about: the keepalive the test chooses
#: for KEEPALIVE_HOST, none for any other host, and the `port 22` a real `ssh -G` prints, so a
#: check that reads any positive number instead of the keepalive key reads the port.
KEEPALIVE_HOST = "keepalive.example.invalid"
STUB_SSH = """#!/bin/sh
[ "$1" = "-G" ] || exit 1
shift
[ "$1" = "--" ] && shift
echo "hostname $1"
echo "port 22"
if [ "$1" = "keepalive.example.invalid" ]; then
  echo "serveraliveinterval ${STUB_SSH_INTERVAL:-0}"
else
  echo "serveraliveinterval 0"
fi
exit 0
"""

#: Configuration git injects through the environment (`git -c`, GIT_CONFIG_COUNT), dropped so a
#: suite run beneath an outer `git -c core.sshCommand=...` cannot decide these rows.
_GIT_CONFIG_ENV = ("GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT", "GIT_SSH_COMMAND", "GIT_SSH")


class KeepaliveAdviceTests(unittest.TestCase):
    def _clone(self) -> hook._Clone:
        fx = hook._Clone()
        self.addCleanup(fx.cleanup)
        return fx

    def _hook(self, fx: hook._Clone, url: str, interval: str | None = None,
              **extra: str) -> str:
        """The hook run directly for one branch row, with `url` as the remote it pushes to, and
        with a stub `ssh` on its PATH resolving `serveraliveinterval` to `interval` when given."""
        path = fx.stub_path()
        if interval is not None:
            (path / "ssh").write_text(STUB_SSH, encoding="utf-8")
            (path / "ssh").chmod(0o755)
        env = {k: v for k, v in os.environ.items()
               if k not in _GIT_ENV_VARS and k not in _GIT_CONFIG_ENV
               and not k.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
               and k not in ("SDLC_PUSH_ACK_RED", hook.BOUNDARY_MARKER)}
        env.update({"STUB_ARGV": str(fx.argv), "STUB_RC": "0", "PATH": str(path),
                    "STUB_GH_MODE": "empty", "STUB_GH_ARGV": str(fx.tmp / "gh-argv.txt"),
                    "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                    "STUB_SSH_INTERVAL": interval or "0", **extra})
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
        self.assertNotIn(ADVICE, self._hook(fx, str(fx.remote),
                                            GIT_SSH_COMMAND="ssh -o ServerAliveInterval=30"),
                         "the advice printed though GIT_SSH_COMMAND carries a keepalive")

    def test_keepalive_warning_silent_when_configured_for_the_ssh_host(self) -> None:
        fx = self._clone()
        for url in (f"git@{KEEPALIVE_HOST}:o/r.git", f"ssh://git@{KEEPALIVE_HOST}:2222/o/r.git",
                    f"git+ssh://git@{KEEPALIVE_HOST}/o/r.git", f"ssh+git://{KEEPALIVE_HOST}/o/r.git"):
            with self.subTest(url=url):
                self.assertNotIn(ADVICE, self._hook(fx, url, interval="60"),
                                 "the advice printed though `ssh -G` resolves a keepalive")

    def test_keepalive_warning_when_absent(self) -> None:
        fx = self._clone()
        rows = (("a local remote", str(fx.remote), None, {}),
                ("another ssh host", "git@other.example.invalid:o/r.git", "60", {}),
                ("an ssh:// host with no keepalive", f"ssh://git@{KEEPALIVE_HOST}:22/o/r.git", "0", {}),
                ("an interval of zero", str(fx.remote), None, {"_SSH_CMD": "ssh -o ServerAliveInterval=0"}),
                ("GIT_SSH_COMMAND over a keepalive core.sshCommand", str(fx.remote), None,
                 {"_SSH_CMD": "ssh -o ServerAliveInterval=60", "GIT_SSH_COMMAND": "ssh -i k"}))
        for name, url, interval, extra in rows:
            with self.subTest(row=name):
                extra = dict(extra)
                ssh_cmd = extra.pop("_SSH_CMD", None)
                if ssh_cmd:
                    hook._git(fx.clone, "config", "core.sshCommand", ssh_cmd)
                else:
                    hook._git(fx.clone, "config", "--unset-all", "core.sshCommand", check=False)
                err = self._hook(fx, url, interval=interval, **extra)
                self.assertIn(ADVICE, err, f"no keepalive is in force and the advice is gone:\n{err}")
                self.assertIn("enable-hooks.sh", err)

if __name__ == "__main__":
    unittest.main()
