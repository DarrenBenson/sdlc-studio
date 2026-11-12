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

Each test also starts with no agent harness named or signalled (BG1197). The token meter reads
the store of the harness the environment names, so a suite run inside Cursor, Copilot CLI or
OpenCode chose that harness for tests whose fixture is a Claude transcript, and they failed. Before each test `_no_harness_selected` clears every variable
`token_meters.selection_variables()` names, read afresh, so a harness or a reader's signal added
later is cleared without an edit here, and puts back what it cleared after the test. A test that
sets one in `setUp` or its body keeps it; one set in `setUpClass` or `setUpModule` is cleared.

The session also gets a private home (BG1249). A meter's step-3 probe looks for a harness's store
under `HOME` and the XDG directories, so a session that kept the operator's opened the live
`~/.codex`, `~/.copilot` and `~/.local/share/opencode` stores, and a reviewer's mutant that wrote
would have written to them. The owning session points `HOME` and each of `XDG_DATA_HOME`,
`XDG_CONFIG_HOME`, `XDG_STATE_HOME` and `XDG_CACHE_HOME` at `PRIVATE_HOME`'s directories under the
private directory, unsets each of `HARNESS_HOMES`, and seeds the home's `.gitconfig` with a test
identity, since a fixture commit that sets none reads it from `HOME`. The seed's path is built
from the private directory, never from `HOME`, and the seed never replaces a file: a mutant that
left `HOME` unmoved wrote the identity over the operator's `~/.gitconfig` (BG1300), and a session
that finds a `.gitconfig` already there stops naming it and keeps its private directory. A child
Python derives its user site from `HOME`, and a base interpreter may find pytest only there
(BG0978), so `PYTHONUSERBASE` is pinned to the user base read before `HOME` moves. Workers and nested runs
inherit all of it, and `pytest_unconfigure` puts each variable back.
"""
import importlib
import os
import shutil
import site
import sys
import tempfile
from pathlib import Path

import pytest

#: The private directory's name, set by whichever run owns it. A session that finds TMPDIR already
#: naming it - an xdist worker, or a pytest run nested in a confined run - uses it and leaves the
#: removal to the owner.
OWNER_VAR = "SDLC_TEST_TMPDIR"

_owned = None   # (private dir, TMPDIR before, marker before, tempfile.tempdir before)
_git_config_before = None   # the GIT_CONFIG_* variables this session set, as they were
_home_before = None   # each variable `_move_home` set or unset, as it was
_refused = None   # the `.gitconfig` the seed found already there; its directory is not removed

#: Each variable the owning session points under the private directory, and where.
PRIVATE_HOME = {"HOME": "home", "XDG_DATA_HOME": "home/.local/share",
                "XDG_CONFIG_HOME": "home/.config", "XDG_STATE_HOME": "home/.local/state",
                "XDG_CACHE_HOME": "home/.cache"}
#: The harness homes that name a store outright, wherever `HOME` is; the session unsets them.
HARNESS_HOMES = ("CODEX_HOME", "COPILOT_HOME", "CLAUDE_CONFIG_DIR", "OPENCODE_DB")
USER_BASE_VAR = "PYTHONUSERBASE"
#: The private home's `.gitconfig`: an identity for a fixture commit that sets none.
TEST_IDENTITY = "[user]\n\tname = sdlc-studio tests\n\temail = tests@sdlc-studio.invalid\n"

MAINTENANCE_OFF = ("maintenance.auto", "false")

#: The skill's scripts directory, whose `lib.token_meters` names the variables that choose a meter.
SCRIPTS = Path(__file__).resolve().parent / ".claude" / "skills" / "sdlc-studio" / "scripts"
METERS = "lib.token_meters"


def harness_variables():
    """The variables `token_meters.selection_variables()` names, read now. `lib` is imported as
    the tests import it, from `SCRIPTS`, which is on `sys.path` only for that import. A copy of
    this file with no `lib/token_meters.py` under its `SCRIPTS`, and none imported, names none."""
    meters = sys.modules.get(METERS)
    if meters is None:
        if not (SCRIPTS / "lib" / "token_meters.py").is_file():
            return []
        sys.path.insert(0, str(SCRIPTS))
        try:
            meters = importlib.import_module(METERS)
        finally:
            sys.path.remove(str(SCRIPTS))
    return meters.selection_variables()


@pytest.fixture(autouse=True)
def _no_harness_selected(monkeypatch):
    """Clear each harness variable for one test; `monkeypatch` puts back what it cleared."""
    for name in harness_variables():
        monkeypatch.delenv(name, raising=False)


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


def _seed_identity(gitconfig):
    """Create `gitconfig` holding `TEST_IDENTITY`, never replacing a file already there. A file
    there is not the session's: it is left byte-identical, `_refused` keeps the private directory
    from removal, and the session stops naming the path (BG1300)."""
    global _refused
    try:
        with open(gitconfig, "x", encoding="utf-8") as seed:
            seed.write(TEST_IDENTITY)
    except FileExistsError:
        _refused = gitconfig
        pytest.exit(f"conftest.py: {gitconfig} already exists, so the session did not write its "
                    "test identity over it and leaves its private directory in place",
                    returncode=pytest.ExitCode.USAGE_ERROR)


def _move_home(private):
    """Point `PRIVATE_HOME`'s variables under `private`, unset `HARNESS_HOMES`, pin the user base
    and seed the home's `.gitconfig`. Only the session that owns `private` calls it. The seed's
    path is built from `private`, never read back from `HOME`: a mutant that left `HOME` unmoved
    wrote the test identity over the operator's `~/.gitconfig` (BG1300)."""
    global _home_before
    user_base = site.getuserbase()      # read before HOME moves, since it derives from HOME
    _home_before = {name: os.environ.get(name)
                    for name in (USER_BASE_VAR, *PRIVATE_HOME, *HARNESS_HOMES)}
    os.environ[USER_BASE_VAR] = user_base
    for name, relative in PRIVATE_HOME.items():
        path = Path(private, relative)
        path.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(path)
    for name in HARNESS_HOMES:
        os.environ.pop(name, None)
    _seed_identity(Path(private, PRIVATE_HOME["HOME"], ".gitconfig"))


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
    _move_home(private)


def pytest_unconfigure(config):
    global _owned, _git_config_before, _home_before, _refused
    _restore(_git_config_before or {})
    _git_config_before = None
    _restore(_home_before or {})
    _home_before = None
    if _owned is None:
        return
    private, env, owner, cached = _owned
    _owned = None
    tempfile.tempdir = cached
    _restore({"TMPDIR": env, OWNER_VAR: owner})
    if _refused is None:
        shutil.rmtree(private, ignore_errors=True)
    _refused = None
