"""`sprint lane land`: land builders' staged lanes on the branch the root has checked out.

A builder works in its own git worktree, stages its unit's Affects and stops, leaving a commit
message and its self-check files at the hand-in path `sdlc-studio/.local/lane/`. Landing that
lane is then one command, so the minutes the commit hook takes are paid in no agent's context:

1. copy the hand-in files out of the worktree, to `sdlc-studio/.local/lane/landed/<worktree>/`
   under the root, since removing the worktree removes them, emptying that directory first so
   nothing an earlier landing of the same worktree name left there survives, and removing each
   unit's QA brief, so a brief found after the landing is one this landing wrote;
2. discard the unstaged edit `verify_ac.py run` leaves in each unit's own story or bug, which no
   commit of the Affects carries and the root's verify rewrites, put back what a builder's own
   `self-check record` left out of the index (the ledger and its mutants file), which step 6
   records on the root, and replay the staged change onto the root's branch, still staged, so the hooks judge
   it on the code it lands on; then commit it in the worktree through the repository's hooks,
   never a bypass. Any other unstaged edit or untracked file outside the hand-in path is
   refused, each named, before any commit and before any hook runs, and nothing is discarded;
3. rebase the worktree's branch onto the root's branch, aborting and naming the files on a
   conflict;
4. fast-forward the root's branch to it;
5. remove the worktree and delete its branch;
6. record each unit's self-check on the root with `critic.py self-check record`, under
   `--author` when given, else the building seat the unit's lane brief recorded, in its
   `<holder> (<role>)` form, else the worktree's directory name;
7. write each unit's QA brief with `critic.py brief --seat qa` to
   `sdlc-studio/.local/briefs/<unit>-qa.txt`, printing its review tier and fingerprint. A unit
   whose latest verdict is an unanswered REJECT has its brief open with a line naming that
   reviewer, to be resumed for round two, and the landing prints the line beside the path. A unit
   left with no brief has `<unit>-qa.none` beside it instead, naming this landing and why it
   wrote none;
8. from a worktree named `agent-<id>`, the harness's name for a builder agent's worktree,
   record each unit's return priced from that agent's transcript through the `price` the
   caller hands in (`sprint lane land` hands in what `lane return --agent <id>` records), and
   name each unit it could not price.

Several worktrees named together land as one commit, so the hooks run once for them all. Each
unit belongs to the worktree whose hand-in carries its claims or mutants file, and keeps that
worktree's kept hand-in, self-check author and transcript. Each staged change is replayed onto
the root's branch in its own worktree, the later ones are added to the first's staged change,
and the first commits with its own subject, its scope naming every landed unit, the later
messages as body, and a `Refs:` trailer per unit. The later worktrees are brought to the landed
commit before they are removed. A file two of them stage with different content, a unit whose
hand-in is in none or several of them, a worktree named twice, and a worktree after the first
holding commits ahead of the root's branch, which landing only its staged change would leave
behind, are refused before anything moves; a change that will not apply beside the first's, or a commit
the hooks refuse, takes the added changes back out, so every worktree holds its own staged
change and nothing landed. The commit's output is kept in every worktree's kept hand-in, so a
refusal reaches each unit's repair brief.

Before step 1, each unit's self-check its hand-in carries is judged as step 6 would record it,
by the critic's own `check_self_check`, against the unit's Affects as the landing leaves them on
the root: the staged copy of whichever worktree of the landing changes them, the unit's own or
another's, and the root's where none does. One it would
refuse, a required surface missing above all, stops the landing with exit 2 and nothing moved:
the worktree, its staged change and the root's branch are as they were, so the builder repairs
the hand-in in place. Each worktree's staged markdown is then linted, each file under the
markdownlint config nearest above it in the worktree (a dot-directory's page with none of its
own there under the one config that dot-directory tracks, as the commit hook lints `.claude/`),
and a lint failure stops the landing the same way, naming the file and the rule; a file no
config governs is not linted, and a linter that cannot be found is said, never read as a pass.

A failure in steps 2 to 4 stops the landing there and names the worktree to resume in. A hook
refusal leaves the staged change, the worktree and the root's branch as they were; a conflict
aborts the rebase and leaves the root's branch as it was. Re-running after a repair starts the
landing again: a branch with nothing staged but commits ahead is rebased and landed without a
second commit. After the fast-forward nothing stops: a worktree that cannot be removed unforced
is left in place, and a unit whose self-check or brief is refused is named while the others are
briefed.

Every landing keeps a land record, `landed/<worktree>.land.json` for the first worktree named:
its worktrees, their paths and branches, and units, the worktree each unit was built in
(`owners`) and the author its self-check was recorded under (`authors`), the steps of
`LAND_STEPS` it completed, the step it stopped at, the units it briefed and, once the root's
branch moved, the commit.
`--resume` runs only the steps the record does not name as completed: the hand-in it kept is
read, never emptied or copied again, a unit already briefed keeps its brief, and a worktree the
removal step took away is not looked for. A resume with no record, or with one whose landing
completed, is refused. A repair's `sprint lane brief` reads the record to recreate the worktree
the removal step took away (`restore_for_repair`), so the builder that built the unit can be
resumed where it worked.

Exit 2 is a refusal before anything was committed, 1 a landing that stopped part way or a unit
whose self-check or brief was not written, 0 a landed lane with every unit briefed, priced or
not.

`sprint lane accept` finishes the unit once its reviewer has answered that brief: it records the
verdict file with `critic.py record` against the brief's fingerprint and tier (a file whose
`BRIEF:` line names one a later `critic.py brief` issued, a second seat's or a rejoinder's,
against that brief's, and one naming no brief of the unit is refused), and on an APPROVE
runs `verify_ac.py run`, moves the unit with `transition.py set` and returns its lane with
`sprint.py lane return`, each through its own entry point. A unit in the top risk class takes
two independent seats: an APPROVE that leaves it without a second seat's is recorded and held
for that seat (`critic.hold_for_second_seat`), whose verdict shares its round, and the unit is
moved only on the APPROVE that completes the pair. Under `review.author_self_check:
block` it refuses an APPROVE on a unit with no current self-check (`critic.self_check_gap`, the
check `critic.py brief` applies), as after a commit to its Affects that no `lane land` checked,
and records a REJECT, which moves nothing, with that gap named. Exit 2
is a refusal before anything was recorded, 1 a verdict recorded and the unit not moved (a REJECT,
an APPROVE held for a second seat, a red criterion or a refused transition) or a return that
exited non-zero, 0 a unit moved and its lane returned.

`sprint lane run` runs one lane's brief headless in a supported CLI (`headless_command`), in the
lane's worktree and under a timeout, and keeps one lane record per session under
`RUN_RECORDS/<unit>/`: the session id, model and usage `harness_usage.parse` normalised from what
the CLI printed, with each model's own counts where the CLI names its models, or the reason
the lane is unmetered. `run_readings` is what `lane return` prices the lane from, one reading per
session, so a repair's session adds to the builder's.
"""
from __future__ import annotations

import contextlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from lib import sdlc_md

HAND_IN = Path("sdlc-studio") / ".local" / "lane"
LANDED = HAND_IN / "landed"
BRIEFS = Path("sdlc-studio") / ".local" / "briefs"
#: beside a unit whose latest landing wrote no brief: that landing, and why it wrote none
NO_BRIEF = "{unit}-qa.none"
#: a builder agent's worktree as the harness names it, `agent-<id>`: the id names its transcript
AGENT_WORKTREE = re.compile(r"agent-([A-Za-z0-9_-]+)")
COMMIT_MSG = "commit-msg.txt"
SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
#: The commit runs the repository's hooks, which may run test suites: minutes, not seconds.
COMMIT_TIMEOUT = 1800
GIT_TIMEOUT = 120
CRITIC_TIMEOUT = 600
#: Lines of a failed step's own output that are printed; the commit's whole output is kept.
TAIL = 40


class LandError(Exception):
    """A landing that stopped. `code` is the exit status: 2 before anything moved, else 1."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


def _git(cwd: Path, *args: str, timeout: int = GIT_TIMEOUT) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                          timeout=timeout, check=False)


def _say(text: str, err: bool = False) -> None:
    """One step's line, flushed, so a piped reader sees stdout and stderr in the order run."""
    print(text, file=sys.stderr if err else sys.stdout, flush=True)


def _tail(text: str) -> str:
    return "\n".join((text or "").strip().splitlines()[-TAIL:])


def _top(path: Path, what: str) -> Path:
    top = _git(path, "rev-parse", "--show-toplevel")
    if top.returncode:
        raise LandError(f"{what} {path} is not a git checkout: {top.stderr.strip()}", 2)
    return Path(top.stdout.strip()).resolve()


def _common_dir(top: Path) -> Path:
    return (top / _git(top, "rev-parse", "--git-common-dir").stdout.strip()).resolve()


def _branch(top: Path, what: str) -> str:
    ref = _git(top, "symbolic-ref", "--quiet", "--short", "HEAD")
    if ref.returncode:
        raise LandError(f"{what} {top} has no branch checked out (a detached HEAD), so there is "
                        f"no branch to land", 2)
    return ref.stdout.strip()


def _resolve(root: Path, worktree: Path) -> tuple[Path, Path, str, str]:
    """(root top, worktree top, the worktree's branch, the root's branch), refusing a worktree
    that is not one of the root's own or that is the root checkout itself."""
    if not worktree.is_dir():
        raise LandError(f"no worktree at {worktree}", 2)
    root_top, wt_top = _top(root, "the root"), _top(worktree, "the worktree")
    if wt_top == root_top:
        raise LandError(f"{wt_top} is the root checkout itself - name the builder's worktree", 2)
    if _common_dir(root_top) != _common_dir(wt_top):
        raise LandError(f"{wt_top} is not a worktree of {root_top}", 2)
    branch, target = _branch(wt_top, "the worktree"), _branch(root_top, "the root")
    if branch == target:
        raise LandError(f"the worktree and the root both have {target} checked out", 2)
    return root_top, wt_top, branch, target


def _bounded(cmd: list[str], timeout: float, grace: float | None = None,
             **popen) -> subprocess.CompletedProcess:
    """`cmd` run to its end as `subprocess.run(cmd, timeout=timeout, text=True, ...)` would run
    it, in a session of its own: past `timeout`, or on any exit that interrupts the wait (a
    Ctrl-C), its whole process group is ended (`_kill_group`: SIGTERM, up to `grace` seconds,
    KILL_GRACE when None, then SIGKILL) before `subprocess.TimeoutExpired` or the interruption
    propagates. `subprocess.run` kills only `cmd`, so what it had started, a commit's hooks and
    the suites they run, or the mutation runner a brief replays, ran on after the bound said it
    stopped. Its own session puts the group out of reach of a kill sent to this process's
    group, so a watchdog (`_watchdog`) ends it the same way, with the same grace, if this
    process dies while `cmd` runs (a `timeout` around `lane land`, a harness ending it)."""
    with _watchdog(grace) as arm:
        with subprocess.Popen(cmd, text=True, start_new_session=True, **popen) as proc:
            try:
                arm(proc.pid)
                out, err = proc.communicate(timeout=timeout)
            except BaseException:
                _kill_group(proc, grace)
                raise
    return subprocess.CompletedProcess(proc.args, proc.returncode, out, err)


def _critic(root: Path, *args: str) -> subprocess.CompletedProcess:
    """`critic.py` through its own entry point, the command an operator would run by hand,
    bounded at CRITIC_TIMEOUT; a brief at critic's own BRIEF_TIMEOUT, which leaves the replay
    of the author's mutants in it room to end at its own bound, so a long replay is said in the
    brief rather than this bound killing the brief with it. Past its bound the brief's whole
    process group is sent SIGTERM and given critic's REPLAY_STOP_GRACE, the time critic gives
    the runner to stop, so the runner stops its tests and removes its scratch copy (`_bounded`)."""
    timeout, grace = CRITIC_TIMEOUT, None
    if args[:1] == ("brief",):
        import critic  # noqa: PLC0415 - sibling; its replay sets the brief's bound
        timeout, grace = critic.BRIEF_TIMEOUT, critic.REPLAY_STOP_GRACE
    return _bounded([sys.executable, str(CRITIC), *args, "--root", str(root)], timeout, grace,
                    cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _commit(wt_top: Path, msg: Path, log: Path, target: str, where: str) -> str:
    """Commit the staged change in `wt_top` through the hooks with the message at `msg`; the
    short sha, or a LandError carrying the hook's own output. `where` names the worktrees a
    refusal leaves to resume in. Past COMMIT_TIMEOUT the commit's whole process group, git, its
    hooks and what they started, is stopped before the LandError is raised (`_bounded`)."""
    try:
        done = _bounded(["git", "-C", str(wt_top), "commit", "-F", str(msg)], COMMIT_TIMEOUT,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired:
        raise LandError(f"the commit's hooks ran past {COMMIT_TIMEOUT}s and were stopped, so "
                        f"nothing was committed and {target} is as it was. Resume in "
                        f"{where}.") from None
    log.write_text(done.stdout or "", encoding="utf-8")
    if done.returncode:
        raise LandError(f"the commit was refused (exit {done.returncode}). The staged change, "
                        f"the worktree and {target} are as they were. Resume in {where}, then "
                        f"re-run lane land; with --resume it reads the hand-in it kept rather "
                        f"than copying it again. The whole output is in {log}; its last "
                        f"lines:\n{_tail(done.stdout)}")
    return _git(wt_top, "rev-parse", "--short", "HEAD").stdout.strip()


def _own_artefacts(wt_top: Path, units: list[str]) -> dict[str, str]:
    """Each unit's own story or bug in the worktree, as {its path from the worktree's top: the
    unit}; a unit with no file there, or one outside the worktree, has none."""
    out: dict[str, str] = {}
    for unit in units:
        hit = sdlc_md.find_by_id(wt_top, unit)
        try:
            rel = Path(hit[0]).resolve().relative_to(wt_top).as_posix() if hit else None
        except ValueError:
            rel = None
        if rel:
            out[rel] = unit
    return out


def _discard_own_artefacts(wt_top: Path, units: list[str]) -> None:
    """Drop the unstaged edit `verify_ac.py run` makes to each unit's own story or bug in the
    worktree, so it cannot stop the rebase. That file is outside the Affects the builder staged,
    so no commit of the lane carries it, and the root's own verify rewrites it after the
    landing. Only the unstaged part goes: what the builder staged of it is committed as staged,
    and an unstaged edit to any other file is refused before the commit (`_refuse_leftovers`)."""
    edited = set(_git(wt_top, "diff", "--name-only", "-z").stdout.split("\0"))
    for rel, unit in _own_artefacts(wt_top, units).items():
        if rel in edited and not _git(wt_top, "checkout", "--", rel).returncode:
            _say(f"discarded {rel}: the unstaged edit verify_ac leaves in {unit}'s own "
                 f"artefact, which the root's verify rewrites")


def _loose(wt_top: Path) -> dict[str, str]:
    """Each path in the worktree that no commit of the lane would carry, as {path: "unstaged"
    or "untracked"}: a change to a tracked file left out of the index, or a file git does not
    track and does not ignore, from `git status`. Each path is decoded from the filesystem
    encoding with its surrogate escapes (`os.fsdecode`), so a path that is not UTF-8 is named
    rather than stopping the land. A rename or copy, staged or made in the work tree, names its
    source after its target, and that source is never read as an entry of its own. Only a
    rename made in the work tree stands for its source's unstaged deletion, so only there is
    the source named too. A copy's source that changed in the work tree has an entry of its
    own, unless it was deleted there and git reports one of the paths added there as its
    rename, whose entry names it; and a staged rename stands for its source's deletion in the
    index, which the commit carries."""
    out: dict[str, str] = {}
    listing = _raw(wt_top, "status", "--porcelain=v1", "-z", "--untracked-files=all").stdout
    parts, n = [os.fsdecode(raw) for raw in listing.split(b"\0") if raw], 0
    while n < len(parts):
        entry, n = parts[n], n + 1
        index, tree, path = entry[0], entry[1], entry[3:]  # `XY <path>`, as git prints each
        if index in "RC" or tree in "RC":
            source, n = parts[n], n + 1
            if tree == "R":
                out[source] = "unstaged"
        if index == "?":
            out[path] = "untracked"
        elif tree != " ":
            out[path] = "unstaged"
    return out


def _record_writes(wt_top: Path, units: list[str]) -> list[str]:
    """The files `critic.py self-check record` writes for `units`, from the worktree's top: the
    self-check ledger and each unit's recorded mutants. The land records each self-check on the
    root from the hand-in, so a builder's own record of it in the worktree is redundant."""
    import critic  # noqa: PLC0415 - sibling; its own paths name what its record writes
    paths = [critic.self_checks_path(wt_top),
             *(critic.author_mutants_path(wt_top, unit) for unit in units)]
    return [path.relative_to(wt_top).as_posix() for path in paths]


def _put_back_record(wt_top: Path, units: list[str], target: str) -> None:
    """Undo a builder's own `self-check record` in the worktree, left unstaged or untracked
    beside the staged change: the ledger is restored and a new mutants file removed, so neither
    stops the rebase or the worktree's removal. A part the builder staged is left as staged."""
    loose = _loose(wt_top)
    for rel in _record_writes(wt_top, units):
        how = loose.get(rel)
        if how == "unstaged":
            if _git(wt_top, "checkout", "--", rel).returncode:
                continue
        elif how == "untracked":
            (wt_top / rel).unlink(missing_ok=True)
        else:
            continue
        _say(f"put back {rel}: the builder's own self-check record, which the land records on "
             f"{target} from the hand-in")


def _refuse_leftovers(lanes_: list[_Lane], code: int) -> None:
    """Refuse, before any commit, a worktree holding a change no commit of the lane carries: an
    unstaged edit or an untracked file outside the hand-in path, naming each. Exempt are what
    the commit step clears itself, each unit's own artefact (`_discard_own_artefacts`) and the
    builder's own self-check record (`_put_back_record`). Nothing is discarded here: a leftover
    is the builder's to stage or remove."""
    hand_in = HAND_IN.as_posix() + "/"
    for lane in lanes_:
        exempt = {*_own_artefacts(lane.top, lane.units), *_record_writes(lane.top, lane.units)}
        left = {path: how for path, how in _loose(lane.top).items()
                if path not in exempt and not path.startswith(hand_in)}
        if left:
            named = ", ".join(f"{path} ({how})" for path, how in sorted(left.items()))
            raise LandError(f"{lane.top} holds unstaged changes or untracked files no commit "
                            f"of the lane carries: {named}. "
                            f"Nothing was committed and no hook ran: stage what the unit's "
                            f"Affects declares, remove the rest, then land again", code)


def _paths(top: Path, *args: str) -> list[str]:
    """The NUL-separated paths a `git -z` listing prints, each decoded as the filesystem names
    it (`os.fsdecode`), so a path that is not UTF-8 is named rather than stopping the land."""
    done = subprocess.run(["git", "-C", str(top), *args], capture_output=True,
                          timeout=GIT_TIMEOUT, check=False)
    return [os.fsdecode(raw) for raw in done.stdout.split(b"\0") if raw]


def _carry(wt_top: Path, target: str) -> bool:
    """Replay the staged change onto `target` before it is committed, leaving it staged, so the
    hooks judge it on the code it lands on, not the base the builder started from. The replay
    goes through a scratch commit that nothing lands: it is unwound to a staged change again,
    and the commit after it, the one the hooks judge, takes its place. A replay git refuses, a
    conflict above all (an unstaged edit the commit step does not clear itself is refused before
    it, `_refuse_leftovers`), is undone, leaving the staged change on its old base, and refused
    with its conflicting files named before the commit is made, so the commit's hooks never
    run: the rebase after the commit would refuse on the same conflict once they had. A
    generated page the replayed change carries is regenerated over the tree it now lands on
    (`_regenerate`). The builder's own commits are replayed as the rebase after the commit
    replays them: one that `target` already holds, or that its change leaves empty, is dropped,
    never kept as an empty commit. Whether a change is still staged: none is when `target`
    already holds it."""
    if not _git(wt_top, "merge-base", "--is-ancestor", target, "HEAD").returncode:
        return True
    head = _git(wt_top, "rev-parse", "HEAD").stdout.strip()
    tree = _git(wt_top, "write-tree").stdout.strip()
    # the scratch commit is told from a builder commit after the rebase by its author, which a
    # rebase keeps whatever a `prepare-commit-msg` hook it runs does to the message
    mark = f"lane-land-replay-{uuid.uuid4().hex}@lane-land.invalid"
    scratch = subprocess.run(
        ["git", "-C", str(wt_top), "commit-tree", tree, "-p", head, "-m",
         "lane land: the staged change, replayed"], capture_output=True, text=True,
        timeout=GIT_TIMEOUT, check=False,
        env={**os.environ, "GIT_AUTHOR_NAME": "lane land", "GIT_AUTHOR_EMAIL": mark},
    ).stdout.strip()
    if not scratch or _git(wt_top, "reset", "--soft", scratch).returncode:
        return True
    replay = _git(wt_top, "rebase", target)
    if replay.returncode:
        conflicts = _paths(wt_top, "diff", "--name-only", "--diff-filter=U", "-z")
        _git(wt_top, "rebase", "--abort")
        _git(wt_top, "reset", "--soft", head)
        named = ", ".join(conflicts) if conflicts else "none reported by git"
        # git's own hints say to continue a rebase this has just aborted, so they are dropped
        said = "\n".join(ln for ln in (replay.stdout + replay.stderr).splitlines()
                         if not ln.startswith("hint:"))
        raise LandError(f"rebasing the staged change onto {target}, to replay it before the "
                        f"commit, failed, so the rebase was undone: nothing was committed, so "
                        f"the commit's hooks never ran, and {target} is as it was. Conflicting "
                        f"files: {named}. The lane stays staged in {wt_top} on its old base: "
                        f"rebase it onto {target} there and resolve it, then re-run lane land.\n"
                        f"{_tail(said)}")
    # the rebase drops the scratch commit when `target` holds its change, so it is taken back
    # out only when it is the commit the rebase ended on
    if _git(wt_top, "log", "-1", "--format=%ae", "HEAD").stdout.strip() == mark:
        _git(wt_top, "reset", "--soft", "HEAD~1")
    if _git(wt_top, "diff", "--cached", "--quiet").returncode == 0:
        _say(f"the staged change is already on {target}: nothing is left to commit")
        return False
    _say(f"replayed the staged change onto {target} before the commit")
    _regenerate(wt_top)
    return True


#: The skill's directory in a checkout, and the generator of the pages under it.
SKILL_DIR = ".claude/skills/sdlc-studio/"
DOCGEN = SKILL_DIR + "scripts/docgen.py"
#: A generator run walks every script's parser: seconds in a large tree, bounded here.
DOCGEN_TIMEOUT = 600


def _generated_verbs(staged: list[str]) -> list[str]:
    """The `docgen.py` verbs that regenerate a page among the `staged` paths, in that order:
    `surface` for the command surface page, `references` for the reference index and
    `reading-guides` for any reference page at the top of the skill directory, the surface page
    among them. They are chosen by the generated page the lane staged, not by the sources the
    pre-commit hook's drift checks are chosen by (a script, a reference page or a `help/`
    file): a lane that staged a script and no surface page gets no `surface` run here."""
    verbs = []
    if SKILL_DIR + "reference-scripts-surface.md" in staged:
        verbs.append("surface")
    if SKILL_DIR + "help/references.md" in staged:
        verbs.append("references")
    if any(re.fullmatch(re.escape(SKILL_DIR) + r"reference-[^/]*\.md", path) for path in staged):
        verbs.append("reading-guides")
    return verbs


def _regenerate(wt_top: Path) -> None:
    """Each generated page the replayed change carries, regenerated over the tree it now lands
    on with the worktree's own `docgen.py` and staged again: a merge of two lanes' regenerated
    pages keeps both lanes' rows under one lane's count, which the hook's drift check refuses
    after its whole run. Only a page the lane staged is staged again; anything else a run
    rewrites is put back, so the commit carries no path the lane did not stage. Nothing is done
    where the worktree has no `docgen.py`, and a run that fails is said and left to the hook."""
    staged = _paths(wt_top, "diff", "--cached", "--name-only", "-z")
    verbs, docgen = _generated_verbs(staged), wt_top / DOCGEN
    if not verbs or not docgen.is_file():
        return
    for verb in verbs:
        try:
            done = _bounded([sys.executable, str(docgen), verb, "--root", str(wt_top)],
                            DOCGEN_TIMEOUT, cwd=str(wt_top), stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        except subprocess.TimeoutExpired:
            _say(f"WARNING docgen.py {verb} ran past {DOCGEN_TIMEOUT}s and was stopped, so the "
                 f"replayed pages were not regenerated; the hook judges them", err=True)
            break
        if done.returncode:
            _say(f"WARNING docgen.py {verb} failed (exit {done.returncode}), so its page was not "
                 f"regenerated; the hook judges it: {_tail(done.stdout)}", err=True)
    rewritten = _paths(wt_top, "diff", "--name-only", "-z")
    if put_back := [p for p in rewritten if p not in staged]:
        _git(wt_top, "checkout", "--", *put_back)
    if again := [p for p in rewritten if p in staged]:
        _git(wt_top, "add", "--", *again)
        _say(f"regenerated {', '.join(again)} over the replayed change (docgen.py "
             f"{', '.join(verbs)})")


def _rebase(wt_top: Path, branch: str, target: str) -> None:
    rebased = _git(wt_top, "rebase", target)
    if not rebased.returncode:
        return
    conflicts = _paths(wt_top, "diff", "--name-only", "--diff-filter=U", "-z")
    _git(wt_top, "rebase", "--abort")
    named = ", ".join(conflicts) if conflicts else "none reported by git"
    # git's own hints say to continue a rebase this has just aborted, so they are dropped
    said = "\n".join(ln for ln in (rebased.stdout + rebased.stderr).splitlines()
                     if not ln.startswith("hint:"))
    raise LandError(f"rebasing {branch} onto {target} failed, so the rebase was aborted and "
                    f"{target} is as it was. Conflicting files: {named}. The lane stays "
                    f"committed on {branch}: resolve it in {wt_top}, then re-run lane land.\n"
                    f"{_tail(said)}")


def _remove(root_top: Path, wt_top: Path, branch: str) -> str | None:
    """Remove the worktree and delete its branch; None, or why either was left in place. Never
    forced: a worktree holding a change no commit carries is reported, not deleted with it."""
    _git(root_top, "worktree", "unlock", str(wt_top))
    removed = _git(root_top, "worktree", "remove", str(wt_top))
    if removed.returncode:
        return (f"the worktree {wt_top} was left in place: {_tail(removed.stderr)}. Its branch "
                f"{branch} is kept with it.")
    deleted = _git(root_top, "branch", "-d", branch)
    if deleted.returncode:
        return f"the branch {branch} was left in place: {_tail(deleted.stderr)}"
    return None


def hand_in_names(unit: str) -> tuple[str, str]:
    """The claims and mutants file names `unit` hands in, keyed by `sdlc_md.norm_id`: the lane
    brief names them and the landing reads them through this one function, so both agree
    whichever spelling of the id `--units` was given (`US-01M6XQJF` and `US01M6XQJF` alike)."""
    key = sdlc_md.norm_id(unit)
    return f"{key}-claims.json", f"{key}-mutants.json"


def report_hand_in_name(unit: str) -> str:
    """The name `unit` hands the mutation runner's report in under, keyed as `hand_in_names`
    keys the other two: the lane brief points the runner's `--report` there and the landing
    records it through `--mutants-from`."""
    return f"{sdlc_md.norm_id(unit)}-mutation-edits.json"


def saved_brief_fingerprint(text: str) -> str:
    """The fingerprint of a saved QA brief as `critic.py brief` noted it, hashed by
    `critic.saved_brief_fingerprint` as `critic.py record --brief-file` hashes it."""
    import critic  # noqa: PLC0415 - sibling; only a brief reader needs it
    return critic.saved_brief_fingerprint(text)


def _reviewer_line(root_top: Path, unit: str) -> str | None:
    """The line telling the orchestrator which reviewer to resume for `unit`'s repair, or None
    when the unit has no unanswered REJECT (a first round) or the ledger cannot be read."""
    import critic  # noqa: PLC0415 - sibling; only a brief writer needs it
    try:
        row = critic.verdict_for(root_top, unit)
    except (OSError, ValueError):
        return None
    if not row or not str(row.get("verdict") or "").upper().startswith(critic.REJECT):
        return None
    who = str(row.get("reviewer") or "").strip()
    if not who:
        return None
    return (f"{critic.REVIEWER_LINE}{who} - this repair answers {who}'s REJECT: resume {who} "
            f"for round two rather than spawning a new reviewer, since a round-two verdict from "
            f"any other reviewer is refused at record")


def _building_seat(root_top: Path, unit: str) -> str | None:
    """The seat the unit's lane brief recorded as building it (`run_state.lane_seat`), in the
    `<holder> (<role>)` form `critic.seat_signature` gives; None when no brief recorded one."""
    import critic  # noqa: PLC0415 - sibling; its seat signature is the form a verdict carries
    from lib import run_state  # noqa: PLC0415 - only the self-check step reads the run
    role = run_state.lane_seat(root_top, unit)
    return critic.seat_signature(root_top, role) if role else None


def _record_and_brief(root_top: Path, keep: Path, unit: str, author: str) -> tuple[bool, str]:
    """Record one unit's self-check on the root and write its QA brief; (ok, the unit's line).
    A hand-in carrying the runner's report (`report_hand_in_name`) is recorded through
    `--mutants-from`, so its whole list is kept; its mutants file, when there is one beside it,
    through `--mutants` with it, so a mutant listed by hand is judged with the report's rows.
    One without the report is recorded through its mutants file alone."""
    claims, mutants = (keep / name for name in hand_in_names(unit))
    report = keep / report_hand_in_name(unit)
    missing = [p.name for p in (claims, mutants)
               if not p.is_file() and not (p == mutants and report.is_file())]
    if missing:
        nor = f" (nor the runner report {report.name})" if mutants.name in missing else ""
        return False, (f"{unit}: self-check NOT RECORDED and no brief written - the hand-in "
                       f"carries no {' or '.join(missing)}{nor}")
    given = [*(("--mutants-from", str(report)) if report.is_file() else ()),
             *(("--mutants", str(mutants)) if mutants.is_file() else ())]
    rec = _critic(root_top, "self-check", "record", "--unit", unit, "--claims", str(claims),
                  *given, "--author", author)
    if rec.returncode:
        return False, f"{unit}: self-check REFUSED and no brief written - {_tail(rec.stderr)}"
    try:
        brief = _critic(root_top, "brief", "--unit", unit, "--seat", "qa")
    except subprocess.TimeoutExpired as exc:
        return False, (f"{unit}: self-check recorded; QA brief NOT WRITTEN - `critic.py brief` "
                       f"was stopped at {exc.timeout:g}s; write it with `critic.py brief "
                       f"--unit {unit} --seat qa`")
    if brief.returncode or not brief.stdout.strip():
        return False, f"{unit}: self-check recorded; QA brief REFUSED - {_tail(brief.stderr)}"
    rel = BRIEFS / f"{unit}-qa.txt"
    resume = _reviewer_line(root_top, unit)
    (root_top / rel).parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(root_top / rel, f"{resume}\n\n{brief.stdout}" if resume else brief.stdout)
    (root_top / BRIEFS / NO_BRIEF.format(unit=unit)).unlink(missing_ok=True)
    tier = re.search(r"^review tier: (\S+)", brief.stderr, re.M)
    fp = re.search(r"^brief fingerprint: (\S+)", brief.stderr, re.M)
    return True, (f"{unit}: self-check recorded; QA brief {rel}, review tier: "
                  f"{tier.group(1) if tier else 'UNKNOWN'}, fingerprint: "
                  f"{fp.group(1) if fp else 'UNKNOWN'}" + (f"\n  {resume}" if resume else ""))


def _unbrief(root_top: Path, unit: str, why: str) -> None:
    """Leave `unit` with no QA brief, and the note of the landing that wrote none."""
    (root_top / BRIEFS / f"{unit}-qa.txt").unlink(missing_ok=True)
    (root_top / BRIEFS).mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(root_top / BRIEFS / NO_BRIEF.format(unit=unit), why + "\n")


def _price(root_top: Path, name: str, units: list[str], price) -> None:
    """Step 8: from an `agent-<id>` worktree, each unit's return priced from that agent's
    transcript by `price(root, units, agent id)`, which answers each unit with (priced, what it
    said); a unit left unpriced is named, and the landing stands either way."""
    agent = AGENT_WORKTREE.fullmatch(name)
    if price is None or agent is None:
        return
    for unit, (priced, said) in price(root_top, units, agent.group(1)).items():
        if priced:
            _say(f"{unit}'s return priced from {name}'s transcript: {said}")
        else:
            _say(f"{unit}'s return UNPRICED: {said}", err=True)


#: A landing's steps, in order. Its land record names those it completed, and `--resume` runs
#: the rest, so no step a stopped landing finished is run twice.
LAND_STEPS = ("hand-in", "commit", "rebase", "fast-forward", "remove", "self-check", "price")
#: the land record under `LANDED`, named for the first worktree landed, beside its kept hand-in
LAND_RECORD = "{name}.land.json"
#: the one message a landing of several worktrees commits with, kept with the first's hand-in
LANDING_MSG = "landing-msg.txt"
_SUBJECT = re.compile(r"^(?P<head>[\w-]+)\((?P<scope>[^)]*)\)(?P<rest>!?: .*)$")
#: the trailers a landing's commit message gathers into its one trailer block: the ids it names
#: and the attribution lines a commit ends with. A last paragraph holding any other `Key: value`
#: line is body text, as `Note: keep this` is.
_TRAILER = re.compile(r"^(?:Refs|Mentions|Co-Authored-By|Claude-Session|Signed-off-by): \S", re.I)
#: the steps that work in a worktree, so a resume of any of them needs it in place
_IN_WORKTREE = ("commit", "rebase", "fast-forward")


class _Lane:
    """One worktree of a landing: its directory name, which names the kept hand-in and, for
    `agent-<id>`, the builder's transcript; where it is and its branch, both None once it is
    gone; the root's branch it lands on; and the units whose hand-in it carries."""

    def __init__(self, name: str, keep: Path, target: str, top: Path | None = None,
                 branch: str | None = None, units: list[str] | None = None) -> None:
        self.name, self.keep, self.target = name, keep, target
        self.top, self.branch = top, branch
        self.units = list(units or [])


def _raw(cwd: Path, *args: str, data: bytes | None = None) -> subprocess.CompletedProcess:
    """git with bytes in and out, for a patch whose files need not be text."""
    return subprocess.run(["git", "-C", str(cwd), *args], input=data, capture_output=True,
                          timeout=GIT_TIMEOUT, check=False)


def _said(done: subprocess.CompletedProcess) -> str:
    return _tail((done.stdout + done.stderr).decode("utf-8", "replace"))


def _has_staged(top: Path) -> bool:
    return _git(top, "diff", "--cached", "--quiet").returncode == 1


def _staged_blobs(top: Path) -> dict[str, str]:
    """Each path `top` stages and the blob it stages there (all zeros for a deletion)."""
    fields = _git(top, "diff", "--cached", "--no-renames", "--no-abbrev", "--raw",
                  "-z").stdout.split("\0")
    return {path: meta.split()[3] for meta, path in zip(fields[0::2], fields[1::2])
            if meta.startswith(":")}


def _refuse_overlap(lanes_: list[_Lane], code: int) -> dict[str, _Lane]:
    """Which worktree first stages each path, refusing a path two of them stage with different
    content: one commit cannot hold both. The same content staged twice is landed once."""
    first: dict[str, tuple[str, _Lane]] = {}
    for lane in lanes_:
        for path, blob in _staged_blobs(lane.top).items():
            held = first.setdefault(path, (blob, lane))
            if held[0] != blob:
                raise LandError(f"{path} is staged with different content in {held[1].top} and "
                                f"{lane.top}, so the two cannot land as one commit and nothing "
                                f"was landed. Reconcile {path} in one of them, or land them one "
                                f"at a time.", code)
    return {path: lane for path, (_, lane) in first.items()}


def _refuse_commits_ahead(lanes_: list[_Lane], code: int) -> None:
    """Refuse a worktree after the first that holds commits ahead of the root's branch: only
    its staged change is added to the first's commit, so its commits would not land."""
    for lane in lanes_[1:]:
        ahead = _git(lane.top, "rev-list", "--count", f"{lane.target}..HEAD").stdout.strip()
        if ahead != "0":
            raise LandError(f"{lane.top} holds {ahead} commit(s) on {lane.branch} ahead of "
                            f"{lane.target}: a landing of several worktrees adds only a later "
                            f"worktree's staged change to the first's commit, so those commits "
                            f"would not land. Name that worktree first, or land it on its own. "
                            f"Nothing was landed.", code)


def _paragraphs(text: str) -> list[list[str]]:
    out: list[list[str]] = [[]]
    for line in text.strip().splitlines():
        if line.strip():
            out[-1].append(line.rstrip())
        elif out[-1]:
            out.append([])
    return [para for para in out if para]


def _combined_message(lanes_: list[_Lane]) -> str:
    """The one message a landing of several worktrees commits with: the first worktree's
    subject, its scope naming every landed unit it did not; each message's body in the order the
    worktrees were named, the later ones led by their own subject; then the trailers they carry,
    once each, and a `Refs:` trailer for each landed unit that none of them refs. A message's last
    paragraph is its trailers only when every line is a `Refs:`, `Mentions:`, `Co-Authored-By:`,
    `Claude-Session:` or `Signed-off-by:` line; any other last paragraph stays in its body."""
    subject, body, trailers = "", [], []
    for n, lane in enumerate(lanes_):
        paras = _paragraphs((lane.keep / COMMIT_MSG).read_text(encoding="utf-8"))
        head, *rest = paras or [[""]]
        if rest and all(_TRAILER.match(line) for line in rest[-1]):
            trailers += [line for line in rest.pop() if line not in trailers]
        if n == 0:
            subject, rest = head[0], ([head[1:], *rest] if head[1:] else rest)
        else:
            rest = [head, *rest]
        body += rest
    units = [unit for lane in lanes_ for unit in lane.units]
    shape = _SUBJECT.match(subject)
    if shape:
        scope = [part.strip() for part in shape["scope"].split(",") if part.strip()]
        named = {sdlc_md.norm_id(part) for part in scope}
        scope += [unit for unit in units if sdlc_md.norm_id(unit) not in named]
        subject = f"{shape['head']}({', '.join(scope)}){shape['rest']}"
    refd = {sdlc_md.norm_id(line.split(":", 1)[1]) for line in trailers
            if line.lower().startswith("refs:")}
    trailers += [f"Refs: {unit}" for unit in units if sdlc_md.norm_id(unit) not in refd]
    paras = [subject, *("\n".join(para) for para in body), "\n".join(trailers)]
    return "\n\n".join(paras) + "\n"


def _unwind(top: Path, applied: list[bytes]) -> str | None:
    """Take the other worktrees' changes back out of `top`, newest first, so it holds only its
    own staged change again; None, or git's reason one could not be taken out."""
    for patch in reversed(applied):
        back = _raw(top, "apply", "--index", "-R", data=patch)
        if back.returncode:
            return _said(back)
    return None


def _commit_several(lanes_: list[_Lane]) -> None:
    """Commit the staged changes of several worktrees as one, in the first, through the hooks
    once: each is replayed onto the root's branch in its own worktree, the later ones' changes
    are added to the first's staged change, and the first commits with `_combined_message`. A
    change that does not apply, or a commit the hooks refuse, takes the added changes back out
    again, so every worktree holds its own staged change and nothing was committed. The
    commit's output is kept in every worktree's kept hand-in, where each unit's repair brief
    reads a refusal."""
    carrier, target = lanes_[0], lanes_[0].target
    # a resume runs no preflight, and a commit made since the landing stopped would be left behind
    _refuse_commits_ahead(lanes_, 1)
    for lane in lanes_:
        if _has_staged(lane.top):
            _carry(lane.top, target)
    owner = _refuse_overlap(lanes_, 1)
    where = ", ".join(str(lane.top) for lane in lanes_)
    patches = []
    for lane in lanes_[1:]:
        paths = sorted(path for path, first in owner.items() if first is lane)
        if not paths:
            continue
        patch = _raw(lane.top, "diff", "--cached", "--binary", "--no-renames", "--",
                     *paths).stdout
        fits = _raw(carrier.top, "apply", "--index", "--check", data=patch)
        if fits.returncode:
            raise LandError(f"the change staged in {lane.top} does not apply beside the one "
                            f"in {carrier.top} on {target}, so nothing was committed and "
                            f"{target} is as it was. Resume in {where}, or land them one at "
                            f"a time:\n{_said(fits)}")
        patches.append(patch)
    applied: list[bytes] = []
    for patch in patches:
        done = _raw(carrier.top, "apply", "--index", data=patch)
        if done.returncode:
            stuck = _unwind(carrier.top, applied)
            raise LandError(f"adding a worktree's staged change to {carrier.top} failed, so "
                            f"nothing was committed and {target} is as it was"
                            + (f"; taking the others back out failed too: {stuck}" if stuck
                               else "") + f". Resume in {where}:\n{_said(done)}")
        applied.append(patch)
    if not _has_staged(carrier.top):
        _say(f"the staged changes are already on {target}: nothing is left to commit")
        return
    msg, log = carrier.keep / LANDING_MSG, carrier.keep / "commit.log"
    sdlc_md.atomic_write(msg, _combined_message(lanes_))
    try:
        sha = _commit(carrier.top, msg, log, target, where)
    except LandError as exc:
        stuck = _unwind(carrier.top, applied)
        if stuck:
            raise LandError(f"{exc}\nTaking the other worktrees' changes back out of "
                            f"{carrier.top} failed, so it still holds them: {stuck}") from None
        raise
    finally:
        for lane in lanes_[1:] if log.is_file() else []:
            lane.keep.mkdir(parents=True, exist_ok=True)
            shutil.copy2(log, lane.keep / "commit.log")
    _say(f"committed {sha} in {carrier.top} through the hooks, holding the staged changes of "
         f"{where}")


def _record_file(root_top: Path, name: str) -> Path:
    return root_top / LANDED / LAND_RECORD.format(name=name)


def _save(root_top: Path, record: dict) -> None:
    """Write the land record, naming the first step not completed as the one it stopped at."""
    record["stopped_at"] = next((s for s in LAND_STEPS if s not in record["completed"]), None)
    sdlc_md.atomic_write(_record_file(root_top, record["worktrees"][0]),
                         json.dumps(record, indent=2) + "\n")


def _read_record(path: Path) -> dict | None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(record, dict) and isinstance(record.get("completed"), list):
        return record
    return None


def _worktrees(root_top: Path) -> set[tuple[str, str]]:
    """Each worktree of the root's repository on a branch, as (its path, its branch)."""
    out, path = set(), None
    for line in _git(root_top, "worktree", "list", "--porcelain").stdout.splitlines():
        if line.startswith("worktree "):
            path = line.removeprefix("worktree ")
        elif line.startswith("branch refs/heads/") and path is not None:
            out.add((path, line.removeprefix("branch refs/heads/")))
    return out


def restore_for_repair(root: Path | str, unit: str) -> str:
    """Recreate, for a repair of `unit`, the worktree its landing removed: at the path it was
    built in, on the branch it was built on, at the landed commit, so the builder that built it
    can be resumed there. The record read is the newest land record naming the unit. Returns
    the line saying what was done, or why no worktree was recreated: a land record that cannot
    be read (not JSON, not UTF-8, or not a land record) is as new as any that names the unit,
    or newer, so it may be the unit's newest landing (each such record is named, and no older
    landing is recreated in its place); no land record names the unit; its landing did not
    remove the worktree or recorded no commit; the record names no branch (a landing recorded
    before branches were); the path is occupied; or git would not add the worktree there. A
    record that cannot be read and is older than the newest naming the unit is passed over,
    since it cannot be that landing. Nothing is overwritten: an occupied path is left as it
    is, and a branch that already exists is not moved. The same worktree already in place on
    its branch is said to be, so a second brief of the repair, or of another unit of the same
    lane, is not read as a failure."""
    root_top = _top(Path(root), "the root")
    uid = sdlc_md.norm_id(unit)
    none = f"no worktree was recreated for {unit}'s repair"
    found, unread = [], []
    for f in (root_top / LANDED).glob(LAND_RECORD.format(name="*")):
        rec = _read_record(f)
        if rec is None:
            unread.append((f.stat().st_mtime, f.name))
        elif uid in {sdlc_md.norm_id(u) for u in rec.get("units") or []}:
            found.append((f.stat().st_mtime, f.name, rec))
    newest = max(found)[0] if found else None
    if blind := sorted(name for at, name in unread if newest is None or at >= newest):
        return (f"{none}: the land record(s) {', '.join(blind)} under {LANDED.as_posix()} "
                f"cannot be read, so the newest landing of {unit} is not known")
    if not found:
        return f"{none}: no land record under {LANDED.as_posix()} names it"
    rec = max(found)[2]
    names = rec["worktrees"]
    owner = next((name for u, name in (rec.get("owners") or {}).items()
                  if sdlc_md.norm_id(u) == uid), None)
    at = names.index(owner) if owner in names else 0
    path, branches, commit = Path(rec["paths"][at]), rec.get("branches") or [], rec.get("commit")
    branch = branches[at] if branches else None
    if "remove" not in rec["completed"] or not commit:
        return f"{none}: its landing did not remove {path}, or recorded no landed commit"
    if not branch:
        return (f"{none}: its land record names no branch for {path} (a landing recorded "
                f"before branches were), so it is not recreated on a guessed one")
    if path.exists():
        if (str(path), branch) in _worktrees(root_top):
            return f"the worktree {path} is already in place on {branch}; it was not recreated"
        return f"{none}: {path} is occupied, and nothing there is overwritten"
    added = _git(root_top, "worktree", "add", "-q", "-b", branch, str(path), commit)
    if added.returncode:
        return f"{none}: git could not add {path} on {branch}: {_tail(added.stderr)}"
    return (f"recreated the worktree {path} on {branch} at {commit[:12]}, the landed commit, so "
            f"the builder that built {unit} can be resumed there")


def _landed_affects_in(root_top: Path, lanes_: list[_Lane], unit: str, scratch: Path) -> Path:
    """The checkout holding the copy of `unit`'s own file whose Affects the landing records
    the self-check against: the root, which step 6 reads once the landing is done, unless a
    worktree of the landing, the unit's own or another, carries a different Affects there (an
    edit to the line, or the file added or removed) than the copy it branched from. Then that
    worktree's staged copy, read from its index and never its checkout, is written under
    `scratch`, and `scratch` is that checkout; for a file the worktree removes the copy written
    is empty, which reads as no artefact (one needs its text), so `scratch` holds no artefact
    with the unit's id, as the root will not once it lands. A worktree holding no copy of the
    file is asked about the path the root's copy is at, and passed over when the root holds none
    either. A file whose Affects line two worktrees stage differently is refused as an overlap,
    and one a worktree and the root's branch both changed is a replay conflict, so nothing
    lands."""
    for lane in lanes_:
        top = lane.top
        hit = sdlc_md.find_by_id(top, unit)
        if not hit:
            top, hit = root_top, sdlc_md.find_by_id(root_top, unit)
        if not hit:
            continue
        rel = Path(hit[0]).relative_to(top).as_posix()
        base = _git(lane.top, "merge-base", lane.target, "HEAD").stdout.strip()
        staged, was = (_raw(lane.top, "show", f"{at}:{rel}") for at in ("", base))
        declared = [None if done.returncode else
                    sdlc_md.affects_files(done.stdout.decode("utf-8", "replace"))
                    for done in (staged, was)]
        if declared[0] == declared[1]:
            continue
        (scratch / rel).parent.mkdir(parents=True, exist_ok=True)
        (scratch / rel).write_bytes(staged.stdout)
        return scratch
    return root_top


def _self_check_refusal(root_top: Path, lanes_: list[_Lane], lane: _Lane,
                        unit: str) -> str | None:
    """The cause `critic.py self-check record` would refuse `unit`'s self-check for, as `lane`'s
    hand-in carries it, or None. The claims file, mutants file and runner report are read and
    judged as `_record_and_brief` hands them to the critic, by the critic's own readers and
    `check_self_check`, against the unit's Affects as the landing of `lanes_` leaves them on
    the root (`_landed_affects_in`). A hand-in missing the files a record needs (no claims file,
    or neither a mutants file nor a runner report) is not judged here: the self-check step names
    it once the lane has landed, as it always has."""
    import tempfile  # noqa: PLC0415 - only a lane carrying its own Affects edit needs one
    hand_in = lane.top / HAND_IN
    claims, mutants = (hand_in / name for name in hand_in_names(unit))
    report = hand_in / report_hand_in_name(unit)
    if not claims.is_file() or not (mutants.is_file() or report.is_file()):
        return None
    import critic  # noqa: PLC0415 - sibling; its own readers judge what it would record
    with tempfile.TemporaryDirectory(prefix="lane-land-affects-") as scratch:
        try:
            said = critic._entries(str(claims), "claims")  # noqa: SLF001
            by_hand = critic._entries(str(mutants), "mutants") if mutants.is_file() else []  # noqa: SLF001
            listed = critic.mutants_from_report(report, unit) if report.is_file() else []
            scope = _landed_affects_in(root_top, lanes_, unit, Path(scratch))
            critic.check_self_check(scope, unit, said, [*listed, *by_hand])
        except (OSError, ValueError) as exc:
            return str(exc)
    return None


def _refuse_self_checks(root_top: Path, lanes_: list[_Lane]) -> None:
    """Each unit's self-check judged before anything moves, so one the critic would refuse once
    the lane landed, a required surface missing above all, stops the landing while the builder's
    worktree still holds the change and the hand-in to repair."""
    for lane in lanes_:
        for unit in lane.units:
            if why := _self_check_refusal(root_top, lanes_, lane, unit):
                raise LandError(f"{unit}'s self-check in {lane.top / HAND_IN} would be refused "
                                f"once landed: {why}. Nothing was committed: correct the "
                                f"hand-in in the worktree and land again", 2)


def _preflight(root: Path, worktrees: list[Path], units: list[str]) -> list[_Lane]:
    """Each named worktree resolved, its units assigned, and every refusal made before anything
    moves: a worktree named twice, one with nothing to land, and for several, a unit whose
    hand-in is in none or more than one of them, a worktree after the first holding commits
    ahead of the root's branch, or a file two of them stage differently; then, for every one, a
    change left out of the index (`_refuse_leftovers`) and a unit whose handed-in self-check the
    critic would refuse (`_refuse_self_checks`)."""
    lanes_: list[_Lane] = []
    root_top = Path(root)
    for path in worktrees:
        root_top, top, branch, target = _resolve(root, path)
        for seen in lanes_:
            if seen.top == top:
                raise LandError(f"the worktree {top} is named twice; name each builder's "
                                f"worktree once. Nothing was landed.", 2)
            if seen.name == top.name:
                raise LandError(f"{seen.top} and {top} share the name {top.name}, under which "
                                f"each one's hand-in is kept. Nothing was landed.", 2)
        lanes_.append(_Lane(top.name, root_top / LANDED / top.name, target, top, branch))
    several = len(lanes_) > 1
    for lane in lanes_:
        if _has_staged(lane.top):
            msg = lane.top / HAND_IN / COMMIT_MSG
            if not msg.is_file() or not msg.read_text(encoding="utf-8").strip():
                raise LandError(f"{lane.top} holds a staged change but no commit message at "
                                f"{HAND_IN / COMMIT_MSG}; nothing was committed", 2)
        elif several:
            raise LandError(f"{lane.top} has nothing staged: a landing of several worktrees "
                            f"commits their staged changes as one, so each must hold one. Land "
                            f"a branch already committed on its own, or resume a stopped "
                            f"landing with --resume. Nothing was landed.", 2)
        elif _git(lane.top, "rev-list", "--count",
                  f"{lane.target}..HEAD").stdout.strip() == "0":
            raise LandError(f"{lane.top} has nothing staged and no commit ahead of "
                            f"{lane.target}: there is nothing to land", 2)
    _refuse_commits_ahead(lanes_, 2)
    if not several:
        lanes_[0].units = list(units)
        _refuse_leftovers(lanes_, 2)
        _refuse_self_checks(root_top, lanes_)
        return lanes_
    for unit in units:
        owners = [lane for lane in lanes_
                  if any((lane.top / HAND_IN / name).is_file()
                         for name in (*hand_in_names(unit), report_hand_in_name(unit)))]
        if len(owners) != 1:
            held = " and ".join(str(lane.top) for lane in owners) or "none of them"
            raise LandError(f"{unit}'s hand-in is in {held}, so which worktree landed it is not "
                            f"known. Nothing was landed.", 2)
        owners[0].units.append(unit)
    for lane in lanes_:
        if not lane.units:
            raise LandError(f"{lane.top} carries the hand-in of none of the units named "
                            f"({', '.join(units)}). Nothing was landed.", 2)
    _refuse_overlap(lanes_, 2)
    _refuse_leftovers(lanes_, 2)
    _refuse_self_checks(root_top, lanes_)
    return lanes_


def _keep_hand_ins(root_top: Path, lanes_: list[_Lane]) -> None:
    """Step 1: each worktree's hand-in copied to its own directory under `LANDED`, emptied
    first: a repair round reuses the worktree's name, and the self-check recorded later is read
    only from this landing's hand-in."""
    for lane in lanes_:
        # spelt out from LANDED here, where it is written, as the TRD's `.local` row reads it
        lane.keep = keep = root_top / LANDED / lane.name
        if keep.is_dir():
            shutil.rmtree(keep)
        keep.mkdir(parents=True, exist_ok=True)
        hand_in = lane.top / HAND_IN
        for path in sorted(hand_in.glob("*")) if hand_in.is_dir() else []:
            if path.is_file():
                shutil.copy2(path, keep / path.name)
        _say(f"hand-in copied to {keep.relative_to(root_top)}")


def _remove_all(root_top: Path, lanes_: list[_Lane]) -> bool:
    """Step 5: every worktree still in place removed with its branch. A later worktree's staged
    change landed in the first's commit, so it is fast-forwarded first to the root's branch,
    which holds that change; one that cannot be is left in place."""
    ok = True
    for n, lane in enumerate(lanes_):
        if lane.top is None or not lane.top.exists():
            continue
        if n:
            follow = _git(lane.top, "merge", "--ff-only", "--quiet", lane.target)
            if follow.returncode:
                _say(f"WARNING the worktree {lane.top} was left in place: it could not be "
                     f"brought to {lane.target}, which holds its landed change: "
                     f"{_tail(follow.stdout + follow.stderr)}", err=True)
                ok = False
                continue
        left = _remove(root_top, lane.top, lane.branch)
        if left:
            ok = False
            _say(f"WARNING {left}", err=True)
        else:
            _say(f"removed the worktree {lane.top} and the branch {lane.branch}")
    return ok


def _steps(root_top: Path, lanes_: list[_Lane], record: dict, author: str | None,
           price) -> int:
    """Run each step the record does not name as completed, in order, saving the record after
    each; a step that stops raises, the record naming it as the step to resume from."""
    carrier, target, failed = lanes_[0], lanes_[0].target, 0

    def commit() -> bool:
        for lane in lanes_:
            _discard_own_artefacts(lane.top, lane.units)
            _put_back_record(lane.top, lane.units, target)
        # a resume runs no preflight, and a leftover may have been made since it ran
        _refuse_leftovers(lanes_, 1)
        if len(lanes_) > 1:
            _commit_several(lanes_)
        elif _has_staged(carrier.top):
            msg = carrier.keep / COMMIT_MSG
            if not msg.is_file() or not msg.read_text(encoding="utf-8").strip():
                raise LandError(f"{carrier.top} holds a staged change but the kept hand-in "
                                f"{carrier.keep.relative_to(root_top)} has no commit message; "
                                f"nothing was committed", 2)
            if _carry(carrier.top, target):
                sha = _commit(carrier.top, msg, carrier.keep / "commit.log", target,
                              str(carrier.top))
                _say(f"committed {sha} in {carrier.top} through the hooks")
        return True

    def rebase() -> bool:
        _rebase(carrier.top, carrier.branch, target)
        _say(f"rebased {carrier.branch} onto {target}")
        return True

    def fast_forward() -> bool:
        ff = _git(root_top, "merge", "--ff-only", carrier.branch)
        if ff.returncode:
            raise LandError(f"{target} could not be fast-forwarded to {carrier.branch}, so "
                            f"{target} is as it was and the lane stays on {carrier.branch} in "
                            f"{carrier.top}. Re-run lane land once that is cleared:\n"
                            f"{_tail(ff.stdout + ff.stderr)}")
        record["commit"] = _git(root_top, "rev-parse", "HEAD").stdout.strip()
        short = _git(root_top, "rev-parse", "--short", "HEAD").stdout.strip()
        _say(f"{target} fast-forwarded to {short}")
        return True

    def self_check() -> bool:
        ok = True
        for lane in lanes_:
            for unit in lane.units:
                if unit in record["briefed"]:
                    continue
                # `--author`, else the building seat the unit's lane brief recorded, else the
                # worktree's name; kept per unit beside `owners`, the worktree that built it
                who = author or _building_seat(root_top, unit) or lane.name
                record.setdefault("authors", {})[unit] = who
                good, line = _record_and_brief(root_top, lane.keep, unit, who)
                if good:
                    record["briefed"].append(unit)
                else:
                    ok = False
                    _unbrief(root_top, unit, f"{record['landing']} wrote no brief: {line}")
                _say(line, err=not good)
        return ok

    def priced() -> bool:
        for lane in lanes_:
            _price(root_top, lane.name, lane.units, price)
        return True

    run = {"commit": commit, "rebase": rebase, "fast-forward": fast_forward,
           "remove": lambda: _remove_all(root_top, lanes_), "self-check": self_check,
           "price": priced}
    for step in LAND_STEPS:
        if step in record["completed"]:
            continue
        gone = [record["paths"][n] for n, lane in enumerate(lanes_) if lane.top is None]
        if step in _IN_WORKTREE and gone:
            raise LandError(f"the landing's {step} step works in {', '.join(gone)}, which is "
                            f"gone, so nothing was resumed", 2)
        try:
            done = run[step]()
        except LandError:
            _save(root_top, record)
            raise
        if done:
            record["completed"].append(step)
        else:
            failed += 1
        _save(root_top, record)
    return 1 if failed else 0


#: The config files markdownlint-cli reads from the folder it runs in, in its own order.
MARKDOWNLINT_CONFIGS = (".markdownlint.jsonc", ".markdownlint.json", ".markdownlint.yaml",
                        ".markdownlint.yml", ".markdownlintrc")


def _markdownlint(root_top: Path, top: Path) -> str | None:
    """The markdownlint a commit in `top` reaches: the worktree's own `node_modules`, the root
    checkout's (a worktree carries none of its own), then the PATH."""
    for base in (top, root_top):
        found = base / "node_modules" / ".bin" / "markdownlint"
        if found.is_file() and os.access(found, os.X_OK):
            return str(found)
    return shutil.which("markdownlint")


def _tracked_markdownlint_configs(top: Path) -> list[str]:
    """The markdownlint configs the worktree `top` tracks, as paths relative to it."""
    listed = _git(top, "ls-files", "-z", "--", *(f"*{n}" for n in MARKDOWNLINT_CONFIGS)).stdout
    return [r for r in listed.split("\0") if r and Path(r).name in MARKDOWNLINT_CONFIGS]


def _markdownlint_config(top: Path, rel: str, tracked: list[str] | None = None) -> Path | None:
    """The markdownlint config nearest above `rel` in the worktree `top`, or None when none
    governs it, so a project that lints no markdown has none linted here. markdownlint's glob
    never enters a dot-directory, so a hook lints one by naming its pages under a config it
    holds: a page in a dot-directory with no config of its own above it there takes the one
    config that dot-directory tracks, so `.claude/agents/` pages lint under the skill's
    `.claude/skills/sdlc-studio/.markdownlint.json` as the commit hook's payload lane does."""
    parts = Path(rel).parts
    dot = parts[0] if len(parts) > 1 and parts[0].startswith(".") else None
    inside = [t for t in tracked or [] if dot is not None and Path(t).parts[0] == dot]
    folder = (top / rel).parent
    while True:
        if folder == top and len(inside) == 1:
            return top / inside[0]
        for name in MARKDOWNLINT_CONFIGS:
            if (folder / name).is_file():
                return folder / name
        if folder == top or folder == folder.parent:
            return None
        folder = folder.parent


def _refuse_markdown(root_top: Path, lanes_: list[_Lane]) -> None:
    """Each worktree's staged markdown linted before anything moves, each file under its nearest
    config, so a hand-in the commit's markdown lane would refuse is refused here, naming the
    file and the rule, with exit 2. A linter past GIT_TIMEOUT is stopped, what it started with
    it, and refused the same way. A linter that cannot be found is said, and lands nothing
    less: the commit's own hooks still run."""
    for lane in lanes_:
        staged = _git(lane.top, "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR",
                      "--", "*.md").stdout.split("\0")
        groups: dict[Path, list[str]] = {}
        tracked = _tracked_markdownlint_configs(lane.top)
        for rel in (r for r in staged if r):
            if (config := _markdownlint_config(lane.top, rel, tracked)) is not None:
                groups.setdefault(config, []).append(rel)
        if not groups:
            continue
        lint = _markdownlint(root_top, lane.top)
        if lint is None:
            _say(f"WARNING markdownlint was not found, so the staged markdown in {lane.top} was "
                 f"not linted before the commit: "
                 f"{', '.join(r for rels in groups.values() for r in rels)}", err=True)
            continue
        failed = []
        for config, rels in groups.items():
            # bounded as every landing step is: past the bound the linter's whole process group
            # is stopped and the landing refused, before anything moved
            try:
                res = _bounded([lint, "--config", str(config), *rels], GIT_TIMEOUT,
                               cwd=str(lane.top), stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
            except subprocess.TimeoutExpired:
                raise LandError(f"markdownlint ran past {GIT_TIMEOUT}s over the staged markdown "
                                f"in {lane.top} and was stopped. Nothing was committed: re-run "
                                f"lane land, or lint the pages by hand.", 2) from None
            if res.returncode:
                failed.append(_tail(res.stdout + res.stderr))
        if failed:
            raise LandError(f"the staged markdown in {lane.top} fails markdownlint, which the "
                            f"commit's markdown lane would refuse. Nothing was committed:\n"
                            + "\n".join(failed), 2)


def _land(root: Path, worktrees: list[Path], units: list[str], author: str | None,
          price=None) -> int:
    lanes_ = _preflight(root, worktrees, units)
    root_top = _top(root, "the root")
    _refuse_markdown(root_top, lanes_)
    _keep_hand_ins(root_top, lanes_)
    names = [lane.name for lane in lanes_]
    record = {"worktrees": names, "paths": [str(lane.top) for lane in lanes_], "units": units,
              "branches": [lane.branch for lane in lanes_],
              "owners": {unit: lane.name for lane in lanes_ for unit in lane.units},
              "author": author, "commit": None, "briefed": [], "completed": ["hand-in"],
              "landing": f"the landing of {', '.join(names)} begun "
                         f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}"}
    _save(root_top, record)
    # an earlier round's brief is not this landing's: lane accept would record a verdict on it
    for unit in units:
        _unbrief(root_top, unit, f"{record['landing']} wrote no brief: it stopped before it "
                                 f"briefed {unit}")
    return _steps(root_top, lanes_, record, author, price)


def _resume(root: Path, worktrees: list[Path], units: list[str], author: str | None,
            price=None) -> int:
    """Resume the stopped landing of `worktrees` from the step its land record names: the
    hand-in it kept is read, never emptied or copied again, a unit it briefed keeps its brief,
    and a worktree a finished removal step took away is not looked for."""
    root_top = _top(root, "the root")
    target = _branch(root_top, "the root")
    names = [_top(path, "the worktree").name if path.is_dir() else path.name
             for path in worktrees]
    where = _record_file(root_top, names[0])
    record = _read_record(where)
    none = f"there is no stopped landing of {', '.join(names)} to resume"
    if record is None:
        raise LandError(f"{none}: no land record at {where.relative_to(root_top)}", 2)
    if all(step in record["completed"] for step in LAND_STEPS):
        raise LandError(f"{none}: its landing completed, at {record.get('commit')}", 2)
    # a record written before `land` spelled each unit as its artefact does keeps the spelling it
    # was given; it is read as the artefact's, so what the resume writes is named for it
    record["units"] = [sdlc_md.display_id(root_top, u) for u in record.get("units") or []]
    record["owners"] = {sdlc_md.display_id(root_top, u): owner
                        for u, owner in (record.get("owners") or {}).items()}
    record["briefed"] = [sdlc_md.display_id(root_top, u) for u in record.get("briefed") or []]
    if record.get("worktrees") != names or \
            sorted(sdlc_md.norm_id(u) for u in record["units"]) != \
            sorted(sdlc_md.norm_id(u) for u in units):
        raise LandError(f"the landing stopped at {where.relative_to(root_top)} was of "
                        f"{', '.join(record.get('worktrees') or [])} for "
                        f"{', '.join(record.get('units') or [])}: resume it as it was begun", 2)
    lanes_ = []
    for name, path in zip(names, worktrees):
        lane = _Lane(name, root_top / LANDED / name, target,
                     units=[u for u in record["units"] if record["owners"].get(u) == name])
        if path.is_dir():
            _, lane.top, lane.branch, _ = _resolve(root_top, path)
        lanes_.append(lane)
    _say(f"resuming the landing of {', '.join(names)} from its {record['stopped_at']} step; "
         f"already done: {', '.join(record['completed']) or 'nothing'}")
    return _steps(root_top, lanes_, record, author or record.get("author"), price)


def land(root: Path | str, worktrees: list[Path | str] | Path | str | None, units: list[str],
         author: str | None = None, price=None, resume: bool = False) -> int:
    """Land the lanes of one or several builders' worktrees as one commit, or with `resume`
    the landing of them that stopped; the exit status, with every step and refusal printed.
    `price` records each unit's priced return from an `agent-<id>` worktree's transcript
    (`_price`)."""
    units = [sdlc_md.display_id(root, u.strip()) for u in units or [] if u and u.strip()]
    named = [worktrees] if isinstance(worktrees, (str, Path)) else list(worktrees or [])
    named = [Path(path) for path in named if str(path).strip()]
    try:
        if not named:
            raise LandError("name the builder's worktree with --worktree", 2)
        if not units:
            raise LandError("name the lane's units with --units: each one's self-check is "
                            "recorded and its brief written, so none is assumed", 2)
        return (_resume if resume else _land)(Path(root), named, units, author, price)
    except LandError as exc:
        _say(f"sprint lane land: {exc}", err=True)
        return exc.code


def _script(root: Path, script: str, *args: str,
            timeout: int = COMMIT_TIMEOUT) -> subprocess.CompletedProcess:
    """A sibling script through its own entry point, the command an operator would run by hand.
    A run past `timeout` is a LandError: what it did by then is unknown, so nothing follows. Past
    it the script's whole process group, what it started included, is stopped first (`_bounded`)."""
    try:
        return _bounded([sys.executable, str(SCRIPTS / script), *args, "--root", str(root)],
                        timeout, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.TimeoutExpired:
        raise LandError(f"`{script} {' '.join(args[:2])}` ran past {timeout}s and was stopped, "
                        f"so nothing after it ran") from None


def _brief_of(root: Path, unit: str, verdict: Path | None = None,
              said: str = "") -> tuple[str, str]:
    """The fingerprint and tier of the brief the verdict `said` (read from `verdict`) answers:
    by default the QA brief `lane land` wrote for `unit`, whose fingerprint is hashed from the
    saved text (less the reviewer line a repair's brief opens with) as `critic.py record
    --brief-file` hashes a first-round brief, and whose tier is
    the one `critic.py brief` noted beside that fingerprint when it printed the brief. A verdict
    opening with a `BRIEF:` line names the file a `critic.py brief` issued; the note of the brief
    that issued it for `unit` gives the fingerprint and tier instead, a second seat's
    (`--seat engineering`) or a rejoinder's (`--rejoinder`), since that brief, not the saved one,
    is what the reviewer read, and a header no note of the unit's names is refused. Without the
    header, a `verdict` at the path a rejoinder brief issued is matched by its path. A brief
    noted before the landing that saved the brief, whose note is the one that issued the file
    the saved brief names, may answer an earlier round, so it is refused; a brief noted at or
    after it, a re-brief of the same scope among them, answers this round. A saved brief that
    names no file, as one saved before verdict files does, is dated by the last note of its
    fingerprint, as it was then, so a re-brief of its scope is taken for its landing. One that
    names a file no note records cannot be dated, so a verdict its header or a rejoinder's path
    ties to a noted brief is refused, naming the brief to save again. Under
    `review.author_self_check: block` a verdict on a unit with no
    current self-check (`critic.self_check_gap`) is refused, except a REJECT, which moves nothing
    and goes to the record with a warning; under `report` that is a warning; `off` asks nothing."""
    import critic  # noqa: PLC0415 - sibling; only accept needs it
    rel = BRIEFS / f"{unit}-qa.txt"
    try:
        saved = (root / rel).read_text(encoding="utf-8")
        fp = saved_brief_fingerprint(saved)
    except OSError:
        try:
            why = (root / BRIEFS / NO_BRIEF.format(unit=unit)).read_text(encoding="utf-8")
        except OSError:
            why = ""
        if why.strip():
            raise LandError(f"no QA brief at {rel}: {why.strip()}. A verdict is recorded only "
                            f"against the brief of the unit's latest landing, so nothing was "
                            f"recorded: land {unit} again with its self-check handed in, and "
                            f"that landing writes the brief", 2) from None
        raise LandError(f"no QA brief at {rel}: `sprint lane land` writes it when it lands the "
                        f"unit, and the verdict is recorded against that brief", 2) from None
    # a commit that reaches main with no `lane land` of the unit leaves the brief in place and
    # its text unchanged, so the unit is asked whether a recorded self-check still covers its
    # Affects: the check `critic.py brief` applies, refusing only under `block`
    try:
        mode = critic.author_self_check_mode(root)
    except ValueError as exc:
        raise LandError(str(exc), 2) from None
    gap = critic.self_check_gap(root, unit) if mode != "off" else None
    # A REJECT moves nothing and holds the findings the repair answers, so `block` records it
    # with the stale self-check named; only a verdict that could move the unit is refused. The
    # verdict is read for its form only, so a REJECT whose BLOCKING the record would refuse is
    # still a REJECT here and reaches that refusal, which names the fix.
    try:
        said_verdict = critic.parse_verdict_block(said, strict=False)[0]
        rejecting = str(said_verdict or "").upper() == critic.REJECT
    except ValueError:      # no readable verdict: judged as one that could move the unit
        rejecting = False
    if gap and mode == "block" and not rejecting:
        raise LandError(f"{gap}, so no self-check covers the diff {rel} would be the brief of, "
                        f"and nothing was recorded: land {unit} again with its self-check "
                        f"handed in, and that landing writes the brief "
                        f"(review.author_self_check: block)", 2)
    if gap:
        # printed before the record answers, so a REJECT is said to go to it, not to be recorded:
        # the record may still refuse its form
        _say(f"WARNING {unit}: {gap}, so no self-check covers the diff {rel} is the brief of"
             + ("; a REJECT moves nothing, so it goes to `critic.py record` "
                "(review.author_self_check: block refuses an APPROVE)" if mode == "block" else
                f" (review.author_self_check: {mode}; `block` records a REJECT too and refuses "
                f"an APPROVE)" if rejecting else
                f" (review.author_self_check: {mode}; `block` refuses the verdict)"), err=True)
    uid, tier = sdlc_md.norm_id(unit), None
    try:
        notes = (root / critic.BRIEF_NOTES_REL).read_text(encoding="utf-8", errors="replace")
    except OSError:
        notes = ""
    # the brief text repeats from round to round, and a re-brief of the scope notes the same
    # fingerprint, so the landing that saved the brief is told by the file it issued, which the
    # saved brief names last; a brief noted before that note is refused. A saved brief naming
    # no file is dated by the last note of its fingerprint instead
    stem = critic._header_lines(said.replace("\r\n", "\n")).get("BRIEF")  # noqa: SLF001
    saved_stem = (re.findall(r"^BRIEF: (\S+)[ \t]*$", saved, re.M) or [None])[-1]
    landed_at, issued = None, None
    for n, line in enumerate(notes.splitlines()):
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict) or row.get("unit") != uid:
            continue
        if row.get("fp") == fp:
            tier = row.get("tier") or tier
            if saved_stem is None:
                landed_at = n
        if verdict is None or not row.get("verdict_file"):
            continue
        if Path(str(row["verdict_file"])).stem == saved_stem:
            landed_at = n
        if stem:
            if Path(str(row["verdict_file"])).stem == stem:
                issued = (n, row)
        elif row.get("rejoinder") and Path(str(row["verdict_file"])).resolve() == verdict:
            issued = (n, row)
    if not fp or not tier:
        raise LandError(f"{rel} hashes to fingerprint {fp or 'NONE'}, and no note in "
                        f"{critic.BRIEF_NOTES_REL} records the review tier of a brief with that "
                        f"fingerprint, so the verdict would be recorded at no known depth. "
                        f"Re-run `critic.py brief --unit {unit} --seat qa` and save it there", 2)
    if stem and issued is None:
        raise LandError(f"{verdict} opens with BRIEF: {stem}, which names no brief noted for "
                        f"{uid} in {critic.BRIEF_NOTES_REL}, so the brief its reviewer answered "
                        f"is not known and nothing was recorded: record the verdict file a "
                        f"`critic.py brief --unit {unit}` issued", 2)
    if issued is None:
        return fp, tier
    n, row = issued
    kind = "rejoinder brief" if row.get("rejoinder") else "brief"
    again = (f"brief the seat again with `critic.py brief --unit {unit} --seat "
             f"{row.get('seat') or 'qa'}{' --rejoinder' if row.get('rejoinder') else ''}` and "
             f"record the file that brief names")
    if landed_at is None:
        raise LandError(f"{rel} names the brief file {saved_stem}, which no note in "
                        f"{critic.BRIEF_NOTES_REL} records, so the landing that saved it cannot "
                        f"be placed before or after the brief that issued {verdict} and nothing "
                        f"was recorded: run `critic.py brief --unit {unit} --seat qa` and save "
                        f"its output at {rel}, then {again}", 2)
    if n < landed_at:
        anchor = (f"the landing that saved {rel} (fingerprint {fp})" if saved_stem else
                  f"the last brief noted with {rel}'s fingerprint {fp}, taken as its landing "
                  f"since it names no file it issued")
        raise LandError(f"{verdict} was issued by a {kind} written before {anchor}, so it may "
                        f"answer an earlier round and nothing was recorded: {again}", 2)
    if not row.get("fp") or not row.get("tier"):
        raise LandError(f"the note in {critic.BRIEF_NOTES_REL} that issued {verdict} records "
                        f"no fingerprint or no tier, so nothing was recorded: {again}", 2)
    return row["fp"], row["tier"]


def _blocking(verdict_text: str) -> list[str]:
    """The findings the verdict's BLOCKING section names, as `critic.py record` folds them."""
    import critic  # noqa: PLC0415 - sibling; only accept needs it
    try:
        _, issues = critic.parse_verdict_block(verdict_text)
    except ValueError:
        return []
    return [item.strip() for item in critic.split_items(issues)
            if re.match(r"\s*BLOCKING\s*:", item, re.I)]


def _return_argv(unit: str, target: str, rnd: str, timeout: int,
                 passthrough: list[str]) -> list[str]:
    """The `sprint.py` argv of the `lane return` an APPROVE's `lane accept` finishes with, the
    flags it was given included; the refusal of the move names the same one."""
    return ["lane", "return", "--units", unit, "--claimed",
            f"{target} on an independent APPROVE (round {rnd})", "--timeout", str(timeout),
            *passthrough]


def _accept(root: Path, unit: str, verdict: Path, reviewer: str, author: str | None,
            terminal: dict[str, str], timeout: int, passthrough: list[str]) -> int:
    import critic  # noqa: PLC0415 - sibling; only accept needs it
    found = sdlc_md.find_by_id(root, unit)
    if not found:
        raise LandError(f"no artefact with id {unit}", 2)
    target = terminal.get(found[1])
    if not target:
        raise LandError(f"{unit} is a {found[1]}: lane accept moves only a "
                        f"{' or a '.join(sorted(terminal))}", 2)
    # the brief and its note are named for the artefact's own spelling of the id, as the landing
    # that wrote them named them
    unit = sdlc_md.display_id(root, unit)
    try:
        said = verdict.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise LandError(f"the verdict file cannot be read: {exc}", 2) from None
    fp, tier = _brief_of(root, unit, verdict, said)
    if not author:
        # the author lane land recorded the unit's self-check under, the latest one
        uid = sdlc_md.norm_id(unit)
        author = next((row["author"] for row in reversed(critic.read_self_checks(root))
                       if sdlc_md.norm_id(row["unit"]) == uid
                       and row["author"].strip() not in ("", "-")), None)
    if not author:
        raise LandError(f"name --author: {unit} has no recorded self-check to name its author, "
                        f"and a verdict is recorded against the author it reviews", 2)
    rec = _script(root, "critic.py", "record", "--unit", unit, "--from-verdict", str(verdict),
                  "--reviewer", reviewer, "--author", author, "--brief", fp, "--tier", tier, timeout=CRITIC_TIMEOUT)
    if rec.returncode:
        raise LandError(f"`critic.py record` exited {rec.returncode}, so {unit} was not moved:"
                        f"\n{_tail(rec.stderr + rec.stdout)}", rec.returncode)
    row = re.search(r"^recorded \S+ (APPROVE|REJECT) \[delivery\](?: round (\d+))?",
                    rec.stdout, re.M)
    if not row:
        raise LandError(f"`critic.py record` printed no recorded row, so {unit} was not "
                        f"moved:\n{_tail(rec.stdout)}")
    rnd = row.group(2) or "UNKNOWN"
    # A verdict can be recorded with a caveat (taken against an earlier scope, say). Nothing
    # later reads record's output, so every warning it printed is passed on here.
    for line in (rec.stderr + rec.stdout).splitlines():
        if re.search(r"(?i)\bwarn", line):
            _say(f"  critic.py record: {line.strip()}", err=True)
    if row.group(1) == critic.REJECT:
        _say(f"{unit}: REJECT recorded, round {rnd}; nothing was moved")
        for item in _blocking(said) or ["no finding is marked BLOCKING"]:
            _say(f"  {item}")
        carried = re.search(re.escape(critic.CARRIED_REASON) + r": (\S+)", rec.stdout)
        if carried:
            _say(f"  {unit} {critic.CARRIED_REASON}: {carried.group(1)} carries it")
        return 1
    _say(f"{unit}: APPROVE recorded, round {rnd}, against brief {fp} at the {tier} tier")
    owed = critic.second_seat_owed(root, unit)
    if owed:
        # A high-risk unit takes two independent seats: hold this APPROVE so the second seat's
        # verdict shares its round, and move nothing until that seat approves too.
        try:
            critic.hold_for_second_seat(root, unit)
        except (OSError, ValueError) as exc:
            _say(f"  WARNING the APPROVE could not be held for the second seat ({exc}), so "
                 f"that seat's verdict takes a round of its own", err=True)
        # held at the cap, the second seat's REJECT is that round's and the cap's rules hold it
        cap = critic.review_ceiling(root)
        rejected = (f"its REJECT shares round {rnd}, the review cap of {cap}, so it opens no "
                    f"repair: the unit is carried, or a further round takes a ruling"
                    if rnd.isdigit() and int(rnd) >= cap else
                    f"its REJECT shares round {rnd} and opens the repair")
        _say(f"{unit}: NOT moved to {target}: its risk class is high, so it takes two "
             f"independent seats and a second seat is owed ({owed}). Its APPROVE, accepted "
             f"here, moves the unit; {rejected}")
        return 1
    ran = _script(root, "verify_ac.py", "run", "--id", unit, "--timeout", str(timeout))
    if ran.returncode:
        _say(f"{unit}: NOT moved to {target}: `verify_ac.py run` exited {ran.returncode}, so a "
             f"criterion is not green:\n{_tail(ran.stdout + ran.stderr)}", err=True)
        return 1
    moved = _script(root, "transition.py", "set", "--id", unit, "--status", target)
    if moved.returncode:
        finish = _return_argv(unit, target, rnd, timeout, passthrough)
        _say(f"{unit}: NOT moved to {target}: `transition.py set` exited {moved.returncode}:"
             f"\n{_tail(moved.stderr + moved.stdout)}\nThe verdict is recorded and the criteria "
             f"are green: once the move is possible, run `transition.py set --id {unit} --status "
             f"{target}`, then `sprint.py {shlex.join(finish)}` to clear its lane, as this "
             f"command would have", err=True)
        return 1
    _say(f"{unit}: moved to {target}")
    back = _script(root, "sprint.py", *_return_argv(unit, target, rnd, timeout, passthrough))
    if back.stdout.strip():
        _say(back.stdout.rstrip())
    if back.stderr.strip():
        _say(back.stderr.rstrip(), err=True)
    return 1 if back.returncode else 0


def accept(root: Path | str, unit: str | None, verdict: Path | str | None,
           reviewer: str | None, terminal: dict[str, str], author: str | None = None,
           timeout: int = 300, passthrough: list[str] | None = None) -> int:
    """Record one unit's verdict and, on an APPROVE, verify, move and return it; the exit status.
    A high-risk unit's APPROVE that leaves it without a second seat's is held instead.
    `terminal` maps each type lane accept moves to its status; `passthrough` is the argv handed
    to `sprint.py lane return` as given."""
    try:
        for flag, value in (("--unit", unit), ("--verdict", verdict), ("--reviewer", reviewer)):
            if not value or not str(value).strip():
                raise LandError(f"name {flag}: the verdict is recorded against the unit, from "
                                f"the reviewer's returned block, under the reviewer's name", 2)
        return _accept(Path(root).resolve(), str(unit).strip(), Path(verdict).resolve(),
                       str(reviewer).strip(), author, terminal, timeout, passthrough or [])
    except LandError as exc:
        _say(f"sprint lane accept: {exc}", err=True)
        return exc.code


# -- sprint lane run ------------------------------------------------------------------------

#: Where `lane run` keeps a lane's records: one `<unit>/<session>.json` and the CLI's own stdout
#: `<unit>/<session>.out` per run, under the root because the worktree goes when the lane lands.
#: Never one file per unit: a repair run in a fresh session would overwrite its builder's record,
#: and the builder's priced cost with it.
RUN_RECORDS = Path("sdlc-studio") / ".local" / "lane-runs"
#: Where `lane run` creates a lane's worktree when none is named.
RUN_WORKTREES = Path("sdlc-studio") / ".local" / "worktrees"
#: A lane run's timeout in seconds when none is given.
RUN_TIMEOUT = 3600
#: The unmetered kind of a CLI stopped at its timeout; `harness_usage` names the other three.
TIMED_OUT = "timeout"
#: The provenance of a delegated record priced from the usage a lane's own CLI printed.
HARNESS_OUTPUT = "harness-output"
#: The tools a Claude Code lane starts with. Named with `--tools` only beside
#: `--strict-mcp-config` and `--disable-slash-commands`: a bare `--tools` allowlist loads every
#: configured MCP tool in full, and a first call measured at 113k tokens that way started at
#: 7.0k with all three (2026-11-06; 28.2k with none of them).
CLAUDE_LANE_TOOLS = ("Bash", "Read", "Edit", "Write", "Glob", "Grep")
#: Each harness's binary.
BINARIES = {"claude": "claude", "cursor": "cursor-agent", "codex": "codex",
            "copilot": "copilot", "opencode": "opencode"}
#: The longest brief passed as one argument: Linux refuses a single argument over 128 KiB.
BRIEF_MAX_BYTES = 120_000
#: The normalised counts a lane record holds, each None where the run reported none.
USAGE_COUNTS = ("input", "cache_read", "cache_write", "cache_write_1h", "output", "reasoning")
#: Git's per-checkout variables, scrubbed from the lane's CLI and from the git `lane run` uses to
#: create the worktree and read what it staged, so a run made from inside a hook cannot point the
#: lane's git at the hook's checkout.
_GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
            "GIT_COMMON_DIR", "GIT_PREFIX", "GIT_ALTERNATE_OBJECT_DIRECTORIES")


def _child_env() -> dict:
    """This process's environment less git's per-checkout variables and `CLAUDECODE`, which
    marks a session nested inside Claude Code."""
    drop = set(_GIT_ENV) | {"CLAUDECODE"}
    return {k: v for k, v in os.environ.items() if k not in drop}


def _run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                          timeout=GIT_TIMEOUT, check=False, env=_child_env())


#: Each harness whose headless command takes a reasoning-effort flag, and the flag. None does in
#: the headless form `headless_command` builds, so a headless lane runs at its harness's own
#: default whatever effort `sprint plan` stamped, and its record says a stamp other than
#: `inherit`, which asks for nothing, was not applied.
HEADLESS_EFFORT_FLAGS: dict[str, str] = {}
#: The plan `sprint plan --write` stamps each unit's `effort: {builder, reviewer}` on.
PLAN = Path("sdlc-studio") / ".local" / "sprint-plan.json"
#: The stamp that asks for the session's own effort, so there is nothing for a command to carry.
EFFORT_INHERIT = "inherit"


def stamped_effort(root: Path, unit: str) -> str | None:
    """The builder effort the plan stamped on `unit`'s row, or None where there is no plan, no
    row for the unit, no stamp on it, or a plan that cannot be read as UTF-8 JSON."""
    try:
        plan = json.loads((Path(root) / PLAN).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return None
    rows = plan.get("batch") if isinstance(plan, dict) else None
    key = sdlc_md.norm_id(unit)
    for row in rows if isinstance(rows, list) else []:
        if isinstance(row, dict) and sdlc_md.norm_id(str(row.get("id") or "")) == key:
            effort = row.get("effort")
            value = effort.get("builder") if isinstance(effort, dict) else None
            return value if isinstance(value, str) and value.strip() else None
    return None


def effort_carried(harness: str, effort: str | None) -> tuple[list[str], str | None, str | None]:
    """What a headless command carries of the stamped `effort`, from the one table
    `HEADLESS_EFFORT_FLAGS`, as (its flag arguments, the effort carried, why it was not): the
    command and the lane record are built from the same answer, so the record holds an effort
    exactly when the command carries its flag. No stamp, or `inherit`, asks for nothing."""
    if not effort or effort == EFFORT_INHERIT:
        return [], None, None
    flag = HEADLESS_EFFORT_FLAGS.get(harness)
    if flag:
        return [flag, effort], effort, None
    return [], None, (f"the {harness} lane command carries no effort flag, so the agent ran at "
                      f"the harness's own default and the stamped {effort} was not applied")


def headless_command(harness: str, brief: str, model: str | None, worktree: Path,
                     effort: str | None = None) -> list[str]:
    """The argv that runs `brief` headless in `harness` with its usage printed as JSON, in each
    CLI's own form (its `--help`, 2026-11-06). Codex's sandbox is widened to the repository's
    git directory, which a worktree keeps outside itself, so its builder can stage. `effort`, the
    plan's stamp, is carried only where `effort_carried` gives the harness a flag for it."""
    tools = ",".join(CLAUDE_LANE_TOOLS)
    if harness == "claude":
        cmd = ["claude", "-p", brief, "--output-format", "json", "--tools", tools,
               "--allowedTools", tools, "--strict-mcp-config", "--disable-slash-commands"]
    elif harness == "cursor":
        cmd = ["cursor-agent", "-p", "--output-format", "json", "--trust", "--force"]
    elif harness == "codex":
        cmd = ["codex", "exec", "--json", "--skip-git-repo-check", "--sandbox", "workspace-write"]
        common = _run_git(worktree, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if common.returncode == 0 and common.stdout.strip():
            cmd += ["--add-dir", common.stdout.strip()]
    elif harness == "copilot":
        cmd = ["copilot", "-p", brief, "--output-format", "json", "-s", "--allow-all-tools"]
    elif harness == "opencode":
        cmd = ["opencode", "run", "--format", "json"]
    else:
        raise ValueError(f"unknown harness {harness!r}; expected one of {', '.join(BINARIES)}")
    if model:
        cmd += ["-m" if harness in ("codex", "opencode") else "--model", model]
    cmd += effort_carried(harness, effort)[0]
    if harness in ("cursor", "codex", "opencode"):
        cmd.append(brief)
    return cmd


def _first_call_context(harness: str, stdout: str) -> tuple[int | None, str | None]:
    """The prompt of the session's first model call, and why it is None where it is: Claude
    Code's `usage.iterations[0]` (input, cache creation and cache read). That the first entry is
    the session's first call is observed on a one-call capture and assumed for longer ones. No
    other CLI's headless output is read for it."""
    if harness != "claude":
        return None, f"{harness}'s headless output is not read for a first-call context"
    try:
        first = (json.loads(stdout).get("usage") or {}).get("iterations")[0]
        return sum(int(first.get(k) or 0) for k in (
            "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")), None
    except (ValueError, TypeError, AttributeError, IndexError):
        return None, "the output carries no usage.iterations entry"


#: The lock, in the git common dir, that one `git worktree add` at a time holds: two adds run
#: together against one repository can refuse one of them with a commondir error.
WORKTREE_LOCK = "sdlc-lane-worktree.lock"
#: Seconds a lane waits for that lock before it is refused.
WORKTREE_LOCK_WAIT = 120.0


@contextlib.contextmanager
def _worktree_lock(common: Path, timeout: float | None = None):
    """Hold the exclusive lock `WORKTREE_LOCK` in `common` for the block, waiting up to `timeout`
    seconds (`WORKTREE_LOCK_WAIT` when None) for another holder, in this process or another, and
    releasing it however the block ends. A holder that dies releases it with the process. Past
    the wait it is a LandError and the block does not run. A no-op where `flock` is unavailable
    (Windows)."""
    timeout = WORKTREE_LOCK_WAIT if timeout is None else timeout
    try:
        import fcntl  # noqa: PLC0415 - POSIX only
    except ImportError:
        yield
        return
    lock = common / WORKTREE_LOCK
    try:
        fh = open(lock, "a")  # noqa: SIM115 - closed in finally
    except OSError as exc:
        raise LandError(f"the lane worktree lock {lock} cannot be opened: {exc}", 2) from None
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > deadline:
                    raise LandError(f"the lane worktree lock {lock} was still held after "
                                    f"{timeout:g}s: another lane is adding a worktree",
                                    2) from None
                time.sleep(0.02)
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
    finally:
        fh.close()


def _lane_worktree(root_top: Path, unit: str) -> Path:
    """The lane's worktree under `RUN_WORKTREES`, `lane-<unit>` with the id lowercased: reused
    when present, else checked out on the branch of that name where a lane whose worktree was
    removed without landing left one, else created on a new branch from the root's HEAD. The add
    is made holding `_worktree_lock`, so lanes started together add one at a time; a worktree
    already there is reused with no lock taken."""
    name = f"lane-{unit.lower()}"
    path = root_top / RUN_WORKTREES / name
    if path.is_dir():
        return path.resolve()
    found = _run_git(root_top, "rev-parse", "--git-common-dir")
    # with no common dir to lock in (not a repository), the add below says why it cannot be made
    held = (_worktree_lock((root_top / found.stdout.strip()).resolve())
            if not found.returncode else contextlib.nullcontext())
    with held:
        if path.is_dir():  # another lane for this unit added it while this one waited
            return path.resolve()
        if _run_git(root_top, "rev-parse", "--verify", "--quiet",
                    f"refs/heads/{name}").returncode:
            made = _run_git(root_top, "worktree", "add", "-q", "-b", name, str(path), "HEAD")
        else:
            made = _run_git(root_top, "worktree", "add", "-q", str(path), name)
    if made.returncode:
        raise LandError(f"the lane worktree {path} could not be created: "
                        f"{_tail(made.stderr)}", 2)
    return path.resolve()


#: Seconds a lane's process group is given to exit after SIGTERM before what is left of it is
#: sent SIGKILL.
KILL_GRACE = 2.0


def _kill_group(proc: subprocess.Popen, grace: float | None = None) -> bool:
    """End `proc`'s whole process group and reap `proc`: SIGTERM first, so a `git add` in it
    removes the `index.lock` it holds, then up to `grace` seconds (KILL_GRACE when None) for
    the group to empty, then SIGKILL to whatever is left; whether that SIGKILL was sent. The
    SIGKILL is sent from a `finally`, so an interruption of the wait (a Ctrl-C in the grace)
    still kills a member that ignores SIGTERM before it propagates. The group is the lane's own,
    led by `proc` (`start_new_session`). At a timeout `proc` is still unreaped when the SIGTERM
    is sent, so the group id is still the lane's; after `proc` has exited and been reaped the
    group lives on only in what it left running, and POSIX does not reuse a group's id while
    the group has a member. Where `os.killpg` does not exist, only `proc` is killed."""
    grace = KILL_GRACE if grace is None else grace
    if not hasattr(os, "killpg"):
        with contextlib.suppress(OSError):
            proc.kill()
        proc.wait()
        return False
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except OSError:
        proc.wait()
        return False
    emptied, killed = False, False
    try:
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            proc.poll()  # a leader left unreaped would hold its group open for the whole grace
            try:
                os.killpg(proc.pid, 0)
            except OSError:
                emptied = True
                break
            time.sleep(0.01)
    finally:
        if not emptied:
            with contextlib.suppress(OSError):
                os.killpg(proc.pid, signal.SIGKILL)
                killed = True
        proc.wait()
    return killed


def _lock_seen(lock: Path | None) -> tuple[int, int] | None:
    """The identity of the `index.lock` at `lock` (its inode and modification time), or None
    when there is none."""
    try:
        stat = lock.stat() if lock is not None else None
    except OSError:
        return None
    return (stat.st_ino, stat.st_mtime_ns) if stat is not None else None


def _clear_killed_lock(lock: Path | None, before: tuple[int, int] | None) -> None:
    """After the lane's group was sent SIGKILL, remove an `index.lock` that appeared in the
    lane's worktree while it ran: a `git add` killed holding it never removes it, and the commit
    `lane land` makes would refuse it. Every process of the group was sent SIGKILL, so none of
    them can finish the write the lock is held for; a lock that was there before the lane
    started (`before`) is someone else's and is left."""
    now = _lock_seen(lock)
    if now is None or now == before:
        return
    with contextlib.suppress(OSError):
        lock.unlink()
        _say(f"WARNING removed {lock}: a git command the lane ran was killed holding it",
             err=True)


#: The watchdog's program. It reads the lane's group id, then one byte more from a pipe whose
#: only writer is the process running the lane: a byte stands it down, and end-of-file, which
#: comes once that writer has died however it died, ends the group as `_kill_group` does.
_WATCHDOG = """\
import os, signal, sys, time
grace, got = float(sys.argv[1]), b""
while b"\\n" not in got:
    more = os.read(0, 64)
    if not more:
        sys.exit(0)
    got += more
pgid, rest = got.split(b"\\n", 1)
if not pgid or rest or os.read(0, 1):
    sys.exit(0)
pgid = int(pgid)
try:
    os.killpg(pgid, signal.SIGTERM)
except OSError:
    sys.exit(0)
deadline = time.monotonic() + grace
while time.monotonic() < deadline:
    try:
        os.killpg(pgid, 0)
    except OSError:
        sys.exit(0)
    time.sleep(0.01)
try:
    os.killpg(pgid, signal.SIGKILL)
except OSError:
    pass
"""


@contextlib.contextmanager
def _watchdog(grace: float | None = None):
    """A watchdog process, in a session of its own, that ends the lane's process group if this
    process dies while the lane runs, giving it `grace` seconds (KILL_GRACE when None) between
    the SIGTERM and the SIGKILL: the CLI's own session puts it out of reach of a kill sent
    to this process's group, and no handler runs for SIGKILL. Yields `arm(pgid)`, which names
    the group to the watchdog; leaving the block stands the watchdog down and reaps it. Where
    `os.killpg` does not exist, no watchdog is started. A watchdog that cannot be started is a
    `LandError` (exit 2), raised before the CLI starts."""
    if not hasattr(os, "killpg"):
        yield lambda pgid: None
        return
    read, write = os.pipe()
    try:
        dog = subprocess.Popen([sys.executable, "-I", "-c", _WATCHDOG,
                                str(KILL_GRACE if grace is None else grace)],
                               stdin=read, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError as exc:
        os.close(write)
        raise LandError(f"the lane's watchdog could not be started "
                        f"({exc.strerror or exc}), so no lane ran", 2) from exc
    finally:
        os.close(read)
    try:
        yield lambda pgid: os.write(write, f"{pgid}\n".encode())
    finally:
        with contextlib.suppress(OSError):
            os.write(write, b"\n")
        os.close(write)
        try:
            dog.wait(timeout=10)
        except subprocess.TimeoutExpired:
            dog.kill()
            dog.wait()


@contextlib.contextmanager
def _reaping(proc: subprocess.Popen):
    """While the lane's CLI runs, SIGTERM, SIGINT and SIGHUP first SIGKILL its group, which its
    own session puts out of reach of a signal sent to this process's group (a hangup, a cancel
    by process group), then do what they did before: the handler they replaced is called, or
    under the default disposition this process dies by the signal. The group is killed only
    while `proc` is unreaped, so it is the lane's. Only the main thread may set a handler; off
    it, and for a signal that is ignored or whose handler was not set from Python, nothing
    changes."""
    prior: dict = {}

    def reap(signum, frame):
        if proc.returncode is None:
            with contextlib.suppress(OSError):
                os.killpg(proc.pid, signal.SIGKILL)
        was = prior.get(signum, signal.SIG_DFL)
        if callable(was):
            return was(signum, frame)
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
        return None

    if hasattr(os, "killpg") and threading.current_thread() is threading.main_thread():
        for name in ("SIGTERM", "SIGINT", "SIGHUP"):
            sig = getattr(signal, name, None)
            was = signal.getsignal(sig) if sig is not None else None
            if was is None or was == signal.SIG_IGN:
                continue
            signal.signal(sig, reap)
            prior[sig] = was
    try:
        yield
    finally:
        for sig, was in prior.items():
            signal.signal(sig, was)


def _run_in_group(cmd: list[str], timeout: int, cwd: Path, env: dict,
                  on_start=None) -> subprocess.CompletedProcess:
    """Run the lane's CLI in a session of its own and return what `subprocess.run(...,
    capture_output=True, text=True)` would; `on_start`, where given, is called once the CLI has
    started. Whatever the CLI left running in its process group when it exited is killed
    (`_kill_group`) before this returns, and on a timeout, or any exit that interrupts the wait,
    the whole group is killed and reaped before the exception propagates: `subprocess.run`
    kills only the CLI, so a child it started ran on and staged work in the worktree after the
    lane's record said what was staged. A group that had to be sent SIGKILL leaves no
    `index.lock` that appeared in the worktree while the CLI ran (`_clear_killed_lock`). A
    watchdog (`_watchdog`) ends the group the same way if this process dies while the CLI runs.
    A CLI that cannot be executed is a `LandError` (exit 2) naming its path, raised before
    `on_start` is called."""
    where = _run_git(cwd, "rev-parse", "--git-path", "index.lock")
    lock = (cwd / where.stdout.strip()) if not where.returncode and where.stdout.strip() else None
    before = _lock_seen(lock)
    with _watchdog() as arm:
        try:
            proc = subprocess.Popen(cmd, cwd=str(cwd), stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    env=env, start_new_session=True)
        except OSError as exc:
            why = exc.strerror or str(exc)
            if isinstance(exc, FileNotFoundError) and Path(cmd[0]).exists():
                why += "; the file exists, so the interpreter it names is missing"
            raise LandError(f"the CLI {cmd[0]} could not be executed ({why}), so no lane ran",
                            2) from exc
        with proc, _reaping(proc):
            try:
                arm(proc.pid)
                if on_start is not None:
                    on_start()
                stdout, stderr = proc.communicate(timeout=timeout)
            except BaseException:
                if _kill_group(proc):
                    _clear_killed_lock(lock, before)
                raise
            if _kill_group(proc):
                _clear_killed_lock(lock, before)
    return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)


def _text(raw) -> str:
    return raw.decode("utf-8", "replace") if isinstance(raw, bytes) else (raw or "")


def run(root: Path | str, unit: str, harness: str, brief: str, model: str | None = None,
        worktree: Path | str | None = None, timeout: int = RUN_TIMEOUT,
        run_id: str | None = None, on_start=None) -> int:
    """Run one lane's `brief` headless in `harness` in the lane's worktree; the exit status.

    Writes this session's lane record `RUN_RECORDS/<unit>/<session>.json` (the session id, model
    and usage normalised by `harness_usage.parse`, the first-call context, the files staged) and
    the CLI's stdout beside it, keeping every earlier session's record of the unit. A CLI that
    exits non-zero, runs past `timeout` or prints no usage is recorded unmetered with the reason,
    its worktree and staged work left as they are. The CLI runs in a session of its own, and
    once it exits, or at its timeout, what is left of its process group is sent SIGTERM and,
    after a grace, SIGKILL before the staged files are read, so nothing it started stages work
    after the record; a watchdog in a session of its own does the same if this process dies
    while the CLI runs, SIGKILL included. `on_start`, where given, is called once every refusal has passed and the
    CLI has started, so a CLI that cannot be executed is a refusal that calls no `on_start`.
    Exit 2 is a refusal before the CLI ran, 1 a CLI that exited non-zero or timed out, 0
    otherwise."""
    try:
        return _run(Path(root), unit, harness, brief, model, worktree, timeout, run_id,
                    on_start)
    except LandError as exc:
        _say(f"sprint lane run: {exc}", err=True)
        return exc.code


def _run(root: Path, unit: str, harness: str, brief: str, model: str | None,
         worktree: Path | str | None, timeout: int, run_id: str | None, on_start) -> int:
    from lib import harness_usage  # noqa: PLC0415 - only a lane run reads usage
    if harness not in BINARIES:
        raise LandError(f"unknown harness {harness!r}; expected one of {', '.join(BINARIES)}", 2)
    binary = shutil.which(BINARIES[harness])
    if binary is None:
        raise LandError(f"{BINARIES[harness]} is not on PATH, so no {harness} lane can run", 2)
    if len(brief.encode("utf-8")) > BRIEF_MAX_BYTES:
        raise LandError(f"{unit}'s brief is over {BRIEF_MAX_BYTES:,} bytes, too long to pass "
                        f"as one argument", 2)
    root_top = _top(root, "the root")
    wt = Path(worktree).resolve() if worktree else _lane_worktree(root_top, unit)
    _resolve(root_top, wt)
    stamp = stamped_effort(root_top, unit)
    _flag, carried, not_applied = effort_carried(harness, stamp)
    cmd = headless_command(harness, brief, model, wt, effort=stamp)
    cmd[0] = binary
    started = sdlc_md.now_iso8601()
    try:
        proc = _run_in_group(cmd, timeout=timeout, cwd=wt, env=_child_env(), on_start=on_start)
        stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
        usage = harness_usage.parse(harness, stdout, exit_code=code, model=model)
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, code = _text(exc.stdout), _text(exc.stderr), None
        usage = harness_usage.Usage(harness, False, unmetered=TIMED_OUT,
                                    reason=f"the CLI ran past its {timeout}s timeout and was "
                                           f"stopped")
    first, first_why = _first_call_context(harness, stdout) if usage.metered else (None, None)
    staged = [p for p in _run_git(wt, "diff", "--cached", "--name-only", "-z").stdout.split("\0")
              if p]
    session = _session_key()
    out_path = root_top / RUN_RECORDS / unit / f"{session}.out"
    sdlc_md.atomic_write(out_path, stdout)
    record = {
        "unit": unit, "run_id": run_id, "harness": harness, "model": model,
        "effort": carried, "effort_stamped": stamp, "effort_reason": not_applied,
        "command": ["<brief>" if a == brief else a for a in cmd], "worktree": str(wt),
        "started_at": started, "ended_at": sdlc_md.now_iso8601(), "timeout": timeout,
        "exit_code": code, "metered": usage.metered, "unmetered": usage.unmetered,
        "reason": usage.reason, "session_id": usage.session_id, "usage_model": usage.model,
        "model_source": usage.model_source,
        "usage": {k: getattr(usage, k) for k in USAGE_COUNTS},
        "by_model": ({m: {k: c[k] for k in USAGE_COUNTS} for m, c in usage.by_model.items()}
                     if usage.by_model else None),
        "unreported": list(usage.unreported), "disagreements": list(usage.disagreements),
        "first_call_context": first, "first_call_reason": first_why, "staged": staged,
        "output": str(out_path)}
    rec_path = root_top / RUN_RECORDS / unit / f"{session}.json"
    sdlc_md.atomic_write(rec_path, json.dumps(record, indent=2) + "\n")
    _say(f"{unit}: {harness} lane ran in {wt} (exit {'none' if code is None else code})")
    if usage.metered:
        u = record["usage"]
        _say(f"  session {usage.session_id or 'not reported'}, model "
             f"{usage.model or 'not reported'}: {u['input']:,} input, {u['cache_read']:,} cache "
             f"read, {u['cache_write']:,} cache write, {u['output']:,} output")
        _say(f"  first-call context: {first:,} tokens" if first is not None
             else f"  first-call context: not available ({first_why})")
        for gap in usage.disagreements:
            _say(f"  WARNING the usage disagrees with the CLI's own total - {gap}", err=True)
    else:
        _say(f"WARNING {unit}'s lane is unmetered ({usage.unmetered}): {usage.reason}; its "
             f"return records no priced cost", err=True)
        if stderr.strip():
            _say(_tail(stderr), err=True)
    if not_applied:
        _say(f"  effort: not applied - {not_applied}")
    _say(f"  staged: {', '.join(staged) if staged else 'nothing'}")
    _say(f"  record: {rec_path}")
    _say(f"  next: sprint.py lane land --worktree {wt} --units {unit}")
    return 1 if code != 0 else 0


def _session_key() -> str:
    """The name of one session's lane record: its start in UTC to the microsecond, so a unit's
    records sort in the order they ran, and a random suffix, so no two runs share one."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def run_readings(root: Path | str, unit: str,
                 run_id: str | None) -> list[tuple[dict | None, str | None]]:
    """The readings `lane return` prices `unit` from: one `(reading, why)` per session a lane of
    the unit ran (`run_reading`), in the order they ran, and [] where it has no lane record. Each
    reading's `source` is its own session's record, so returning the unit again replaces each
    session's delegated record rather than adding it twice, and a second session adds to the
    first rather than replacing it."""
    return [run_reading(path, unit, run_id)
            for path in sorted((Path(root) / RUN_RECORDS / unit).glob("*.json"))]


def effort_not_applied(root: Path | str, run_id: str | None) -> dict[str, list[str]]:
    """Each unit a headless lane ran in `run_id` whose command carried no effort flag, with the
    harnesses that ran it so: a lane record of the run whose `effort` is empty. A record written
    before the field was kept carried none either, since no headless command took the flag
    then. A record that cannot be read as UTF-8 JSON, or is another run's, is passed over, and a
    run with no id counts none: a record naming no run is no run's."""
    out: dict[str, list[str]] = {}
    if not run_id:
        return out
    for path in sorted((Path(root) / RUN_RECORDS).glob("*/*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, ValueError):
            continue
        if not isinstance(rec, dict) or rec.get("run_id") != run_id or rec.get("effort"):
            continue
        harness = str(rec.get("harness") or "an unnamed harness")
        unit = sdlc_md.norm_id(str(rec.get("unit") or path.parent.name))
        if harness not in out.setdefault(unit, []):
            out[unit].append(harness)
    return out


def run_reading(path: Path, unit: str, run_id: str | None) -> tuple[dict | None, str | None]:
    """One session's reading from its lane record at `path`: its usage, as
    {"tokens", "components", "source", "harness", "model"}, with the session's per-model
    components under `run_state.BY_MODEL` where the record keeps a `by_model` split, or
    (None, why) where the record is unreadable, another run's or unmetered. A record with no
    split, one written before the split was kept among them, carries none, and
    `record_delegated_tokens` books it under the one model it names. A split that does not sum
    to the session's own usage is refused with the record, so the unit's dollars and its priced
    tokens are never read from two different counts."""
    from lib import run_state  # noqa: PLC0415 - only a lane return prices a reading
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
        if rec.get("run_id") != run_id:
            return None, (f"{unit}'s lane run record {path.name} was written under another run "
                          f"({rec.get('run_id') or 'none'}), so it is not priced into this one")
        if not rec.get("metered"):
            return None, (f"{unit}'s lane run recorded at {path} is unmetered "
                          f"({rec.get('unmetered')}): "
                          f"{rec.get('reason')}, so its return records no priced cost")
        parts = _components(rec["usage"])
        split = rec.get("by_model")
        by_model = {str(m): _components(c) for m, c in split.items()} if split else None
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return None, (f"{unit}'s lane run record {path} cannot be read ({exc}), so its return "
                      f"records no priced cost")
    tokens = parts["input"] + parts["output"] + parts["cache_write_5m"] + parts["cache_write_1h"]
    if tokens <= 0:
        return None, (f"{unit}'s lane run reports no input, output or cache write, so its "
                      f"return records no priced cost")
    if by_model and any(sum(c[k] for c in by_model.values()) != v for k, v in parts.items()):
        return None, (f"{unit}'s lane run record {path} cannot be read (its per-model split "
                      f"does not sum to the session's usage), so its return records no priced "
                      f"cost")
    return {"tokens": tokens, "components": parts, "source": str(path),
            "harness": rec.get("harness"), "model": rec.get("usage_model"),
            **({run_state.BY_MODEL: by_model} if by_model else {})}, None


def _components(u) -> dict:
    """One usage's counts as the priced components: its cache write split into the five-minute
    and one-hour parts."""
    hour = u.get("cache_write_1h") or 0
    return {"input": int(u["input"]), "output": int(u["output"]),
            "cache_write_5m": int(u["cache_write"]) - hour, "cache_write_1h": hour,
            "cache_read": int(u["cache_read"])}
