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
"""
import os
import shutil
import tempfile

#: The private directory's name, set by whichever run owns it. A session that finds TMPDIR already
#: naming it - an xdist worker, or a pytest run nested in a confined run - uses it and leaves the
#: removal to the owner.
OWNER_VAR = "SDLC_TEST_TMPDIR"

_owned = None   # (private dir, TMPDIR before, marker before, tempfile.tempdir before)


def pytest_configure(config):
    global _owned
    current = os.environ.get("TMPDIR")
    if current and os.environ.get(OWNER_VAR) == current:
        tempfile.tempdir = current      # tempfile may have cached another directory before this ran
        return
    private = tempfile.mkdtemp(prefix="sdlc-tests-")
    _owned = (private, current, os.environ.get(OWNER_VAR), tempfile.tempdir)
    os.environ["TMPDIR"] = os.environ[OWNER_VAR] = private
    tempfile.tempdir = private


def pytest_unconfigure(config):
    global _owned
    if _owned is None:
        return
    private, env, owner, cached = _owned
    _owned = None
    tempfile.tempdir = cached
    for name, value in (("TMPDIR", env), (OWNER_VAR, owner)):
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
    shutil.rmtree(private, ignore_errors=True)
