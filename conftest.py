"""Confine a pytest session's temporary files to one directory, removed when the session ends.

Tests call `tempfile.mkdtemp()` without removing what they made, and so do the subprocesses they
spawn: one run of both suites left 225 entries, about 1,900 inodes, and a sprint of runs used up
/tmp's inodes mid-commit (BG0753). Chasing each fixture is a dozen modules of edits that the next
fixture undoes, so the session owns the directory instead. For the whole run `tempfile.tempdir`
and `TMPDIR` name a private directory under the one the run was given, so the tests, their
subprocesses and pytest-xdist's workers (started after this, inheriting it) all write there, and
it is removed at unconfigure, green or red.

It lives at the repository root, the one conftest every session over either test tree loads. A
conftest inside each tree cannot work: both trees are packages named `tests`, so pytest resolves
both files to the module `tests.conftest` and refuses the second in any session that spans the
two, which is the push's full suite. `tools/skill-tests.sh` confines the unittest runner, which
never loads a conftest, the same way.

The session also turns git's automatic maintenance off (BG0782). Every `git commit` a fixture
makes starts `git maintenance run --auto --detach`, and from git 2.55 (CI's) that process outlives
the commit and writes into `.git` while the temporary directory is being removed, which fails a
green test on teardown (BG0711). The setting is appended through `GIT_CONFIG_COUNT`/`KEY`/`VALUE`,
so every git process under the session reads it whatever `GIT_CONFIG_GLOBAL` a fixture sets, and
an entry the caller already made stays in force.
"""
import os
import shutil
import tempfile

#: The private directory's name, set by whichever run owns it. A session that finds TMPDIR already
#: naming it - an xdist worker, or a pytest run nested in a confined run - uses it and leaves the
#: removal to the owner.
OWNER_VAR = "SDLC_TEST_TMPDIR"

_owned = None   # (private dir, TMPDIR before, marker before, tempfile.tempdir before)
_git_config_before = None   # the GIT_CONFIG_* variables this session set, as they were

MAINTENANCE_OFF = ("maintenance.auto", "false")


def _git_config_entries():
    count = int(os.environ.get("GIT_CONFIG_COUNT") or 0)
    return [(os.environ.get(f"GIT_CONFIG_KEY_{i}"), os.environ.get(f"GIT_CONFIG_VALUE_{i}"))
            for i in range(count)]


def _turn_git_maintenance_off():
    """Append `maintenance.auto=false` to the environment's git config after what is there. A
    session that inherits it (an xdist worker, a run nested in a confined one) adds nothing."""
    global _git_config_before
    entries = _git_config_entries()
    if MAINTENANCE_OFF in entries:
        return
    n = len(entries)
    names = ("GIT_CONFIG_COUNT", f"GIT_CONFIG_KEY_{n}", f"GIT_CONFIG_VALUE_{n}")
    _git_config_before = {name: os.environ.get(name) for name in names}
    os.environ.update(zip(names, (str(n + 1), *MAINTENANCE_OFF)))


def _restore(saved):
    for name, value in saved.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value


def pytest_configure(config):
    global _owned
    _turn_git_maintenance_off()
    current = os.environ.get("TMPDIR")
    if current and os.environ.get(OWNER_VAR) == current:
        tempfile.tempdir = current      # tempfile may have cached another directory before this ran
        return
    private = tempfile.mkdtemp(prefix="sdlc-tests-")
    _owned = (private, current, os.environ.get(OWNER_VAR), tempfile.tempdir)
    os.environ["TMPDIR"] = os.environ[OWNER_VAR] = private
    tempfile.tempdir = private


def pytest_unconfigure(config):
    global _owned, _git_config_before
    _restore(_git_config_before or {})
    _git_config_before = None
    if _owned is None:
        return
    private, env, owner, cached = _owned
    _owned = None
    tempfile.tempdir = cached
    _restore({"TMPDIR": env, OWNER_VAR: owner})
    shutil.rmtree(private, ignore_errors=True)
