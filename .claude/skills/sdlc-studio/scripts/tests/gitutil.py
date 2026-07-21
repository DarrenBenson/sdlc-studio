"""Shared helper for git-invoking tests.

Two jobs, and the second one is the load-bearing one.

**Hermeticity.** Git runs with the host's global/system config neutralised
(`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` -> /dev/null) and a fixed identity. Without
this, a developer whose global config sets `commit.gpgsign = true` (or any signing setup)
makes every test that creates a commit fail with "gpg failed to sign the data" or hang on a
passphrase prompt - the suite must be host-independent.

**Confinement.** A fixture git call must act on the fixture and nowhere else. The suites build
throwaway repos in temp directories, so the only thing that ever decided WHICH repo git acted
on was the ambient environment - and this helper used to pass `os.environ` straight through.
An inherited `GIT_DIR` / `GIT_WORK_TREE` / `GIT_INDEX_FILE` pointing at the surrounding
checkout therefore redirected every fixture git call onto the real repository. That is not a
theoretical exposure: it emptied this repository's index once, staging all 1845 tracked files
as deletions, and recurred later when a fixture ran git under `git commit -a`. The pre-commit
hook is not the only source either - a CI runner, a developer's shell, or a test of git
behaviour itself can export the same variables, which is why the defence has to sit here at
the fixture rather than only at the caller.

Two escape routes are closed, because closing one leaves the other open:

1. `REPO_LOCATING_GIT_VARS` are dropped from the child environment, so an inherited value
   cannot name a repository, index, object store, namespace or path prefix. Git then resolves
   the repository by discovery from `cwd`, which is the fixture.
2. Discovery itself is fenced. With the variables gone, a fixture that has not yet run
   `git init` walks UP from `cwd` until it finds a repository. That is harmless while temp
   directories sit under `/tmp`, and not harmless at all when `TMPDIR` points inside a
   checkout, which CI runners and agent harnesses do set. `GIT_CEILING_DIRECTORIES` is
   therefore set to the temp root, so the walk stops there instead of reaching the checkout.

An explicit `**extra` still wins over both: what the helper refuses is an INHERITED value, not
a deliberate one.

`tests/test_gitutil.py` pins all of this behaviourally, against throwaway victim repos.
`tools/tests/test_skill_tests_env.py` pins `REPO_LOCATING_GIT_VARS` against the other places
the same list is written out, so the copies cannot drift apart.
"""
from __future__ import annotations

import os
import subprocess
import tempfile

#: Every environment variable that can point git at a different repository, index, object
#: store, namespace or path prefix: the "The Git Repository" set in `git help git` ENVIRONMENT
#: VARIABLES, plus `GIT_PREFIX`, which git sets for hooks only. Three of them were checked one
#: at a time, by removing that name alone and re-running the fixture tests: `GIT_DIR` and
#: `GIT_INDEX_FILE` each make a fixture's `git add` write the OTHER repository's index, and
#: `GIT_WORK_TREE` runs the harm the other way, pulling the other repository's files into the
#: fixture's index. Either direction is a fixture that has stopped talking about itself. The
#: remaining names are carried because a shell or a CI runner can export them, not because
#: each was reproduced. Widen this list, never shorten it, if a future git gains another.
#:
#: Deliberately absent: `GIT_CONFIG_GLOBAL` / `GIT_CONFIG_SYSTEM` (set below for hermeticity)
#: and `GIT_AUTHOR_*` / `GIT_COMMITTER_*` (identity, not repository location). Dropping those
#: would weaken the fixtures rather than protect them.
REPO_LOCATING_GIT_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)


def git_env(**extra: str) -> dict:
    """`os.environ` confined to the fixture, with host git config neutralised.

    Every variable in `REPO_LOCATING_GIT_VARS` is dropped, discovery is fenced at the temp
    root, and a deterministic identity is set. Pass `**extra` to add or override env keys for
    one call; an explicit value wins, including for a variable that would otherwise be dropped.
    """
    env = {k: v for k, v in os.environ.items() if k not in REPO_LOCATING_GIT_VARS}
    env.update({
        # Fences upward repository discovery. Git does not chdir up into a ceiling directory,
        # so a fixture under the temp root cannot reach a repository above it. Repositories
        # BELOW the ceiling are still discovered normally, which is every real fixture.
        "GIT_CEILING_DIRECTORIES": tempfile.gettempdir(),
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
    })
    env.update(extra)
    return env


def git(args, cwd, check: bool = True, **kw):
    """Run `git <args>` in `cwd` with the confined env; captures output by default."""
    kw.setdefault("capture_output", True)
    return subprocess.run(["git", *args], cwd=str(cwd), check=check, env=git_env(), **kw)
