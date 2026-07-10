"""Shared helper for git-invoking tests.

Runs git with the host's global/system config neutralised (`GIT_CONFIG_GLOBAL` and
`GIT_CONFIG_SYSTEM` -> /dev/null) and a fixed identity. Without this, a developer whose
global config sets `commit.gpgsign = true` (or any signing setup) makes every test that
creates a commit fail with "gpg failed to sign the data" or hang on a passphrase prompt -
the suite must be host-independent.
"""
from __future__ import annotations

import os
import subprocess


def git_env(**extra: str) -> dict:
    """`os.environ` with host git config neutralised and a deterministic identity.

    Pass `**extra` to add or override env keys for one call.
    """
    return {
        **os.environ,
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
        **extra,
    }


def git(args, cwd, check: bool = True, **kw):
    """Run `git <args>` in `cwd` with the neutralised env; captures output by default."""
    kw.setdefault("capture_output", True)
    return subprocess.run(["git", *args], cwd=str(cwd), check=check, env=git_env(), **kw)
