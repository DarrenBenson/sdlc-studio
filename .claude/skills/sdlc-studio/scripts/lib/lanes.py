"""`sprint lane land`: land builders' staged lanes on the branch the root has checked out.

A builder works in its own git worktree, stages its unit's Affects and stops, leaving a commit
message and its self-check files at the hand-in path `sdlc-studio/.local/lane/`. Landing that
lane is then one command, so the minutes the commit hook takes are paid in no agent's context:

1. copy the hand-in files out of the worktree, to `sdlc-studio/.local/lane/landed/<worktree>/`
   under the root, since removing the worktree removes them, emptying that directory first so
   nothing an earlier landing of the same worktree name left there survives, and removing each
   unit's QA brief, so a brief found after the landing is one this landing wrote;
2. discard the unstaged edit `verify_ac.py run` leaves in each unit's own story or bug, which no
   commit of the Affects carries and the root's verify rewrites, and replay the staged change
   onto the root's branch, still staged, so the hooks judge it on the code it lands on; then
   commit it in the worktree through the repository's hooks, never a bypass;
3. rebase the worktree's branch onto the root's branch, aborting and naming the files on a
   conflict;
4. fast-forward the root's branch to it;
5. remove the worktree and delete its branch;
6. record each unit's self-check on the root with `critic.py self-check record`;
7. write each unit's QA brief with `critic.py brief --seat qa` to
   `sdlc-studio/.local/briefs/<unit>-qa.txt`, printing its review tier and fingerprint. A unit
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
hand-in is in none or several of them, and a worktree named twice are refused before anything
moves; a change that will not apply beside the first's, or a commit the hooks refuse, takes the
added changes back out, so every worktree holds its own staged change and nothing landed.

A failure in steps 2 to 4 stops the landing there and names the worktree to resume in. A hook
refusal leaves the staged change, the worktree and the root's branch as they were; a conflict
aborts the rebase and leaves the root's branch as it was. Re-running after a repair starts the
landing again: a branch with nothing staged but commits ahead is rebased and landed without a
second commit. After the fast-forward nothing stops: a worktree that cannot be removed unforced
is left in place, and a unit whose self-check or brief is refused is named while the others are
briefed.

Every landing keeps a land record, `landed/<worktree>.land.json` for the first worktree named:
its worktrees and units, the steps of `LAND_STEPS` it completed, the step it stopped at, the
units it briefed and, once the root's branch moved, the commit. `--resume` runs only the steps
the record does not name as completed: the hand-in it kept is read, never emptied or copied
again, a unit already briefed keeps its brief, and a worktree the removal step took away is
not looked for. A resume with no record, or with one whose landing completed, is refused.

Exit 2 is a refusal before anything was committed, 1 a landing that stopped part way or a unit
whose self-check or brief was not written, 0 a landed lane with every unit briefed, priced or
not.

`sprint lane accept` finishes the unit once its reviewer has answered that brief: it records the
verdict file with `critic.py record` against the brief's fingerprint and tier (a file a later
`critic.py brief --rejoinder` issued against that rejoinder brief's), and on an APPROVE
runs `verify_ac.py run`, moves the unit with `transition.py set` and returns its lane with
`sprint.py lane return`, each through its own entry point. Under `review.author_self_check:
block` it refuses a unit with no current self-check (`critic.self_check_gap`, the check
`critic.py brief` applies), as after a commit to its Affects that no `lane land` checked. Exit 2
is a refusal before anything was recorded, 1 a verdict recorded and the unit not moved (a REJECT,
a red criterion or a refused transition) or a return that exited non-zero, 0 a unit moved and its
lane returned.

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


def _critic(root: Path, *args: str) -> subprocess.CompletedProcess:
    """`critic.py` through its own entry point, the command an operator would run by hand."""
    return subprocess.run([sys.executable, str(CRITIC), *args, "--root", str(root)],
                          cwd=str(root), capture_output=True, text=True,
                          timeout=CRITIC_TIMEOUT, check=False)


def _commit(wt_top: Path, msg: Path, log: Path, target: str, where: str) -> str:
    """Commit the staged change in `wt_top` through the hooks with the message at `msg`; the
    short sha, or a LandError carrying the hook's own output. `where` names the worktrees a
    refusal leaves to resume in."""
    try:
        done = subprocess.run(["git", "-C", str(wt_top), "commit", "-F", str(msg)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              timeout=COMMIT_TIMEOUT, check=False)
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


def _discard_own_artefacts(wt_top: Path, units: list[str]) -> None:
    """Drop the unstaged edit `verify_ac.py run` makes to each unit's own story or bug in the
    worktree, so it cannot stop the rebase. That file is outside the Affects the builder staged,
    so no commit of the lane carries it, and the root's own verify rewrites it after the
    landing. Only the unstaged part goes: what the builder staged of it is committed as staged,
    and an unstaged edit to any other file is left for the rebase to refuse."""
    edited = set(_git(wt_top, "diff", "--name-only", "-z").stdout.split("\0"))
    for unit in units:
        hit = sdlc_md.find_by_id(wt_top, unit)
        try:
            rel = Path(hit[0]).resolve().relative_to(wt_top).as_posix() if hit else None
        except ValueError:
            rel = None
        if rel in edited and not _git(wt_top, "checkout", "--", rel).returncode:
            _say(f"discarded {rel}: the unstaged edit verify_ac leaves in {unit}'s own "
                 f"artefact, which the root's verify rewrites")


def _carry(wt_top: Path, target: str) -> bool:
    """Replay the staged change onto `target` before it is committed, leaving it staged, so the
    hooks judge it on the code it lands on, not the base the builder started from. The replay
    goes through a scratch commit no hook runs for and nothing lands: it is unwound to a staged
    change again. A replay git refuses (a conflict, an unstaged edit) is undone, leaving the
    staged change on its old base for the commit and the rebase after it to report as before.
    Whether a change is still staged: none is when `target` already holds it."""
    if not _git(wt_top, "merge-base", "--is-ancestor", target, "HEAD").returncode:
        return True
    head = _git(wt_top, "rev-parse", "HEAD").stdout.strip()
    tree = _git(wt_top, "write-tree").stdout.strip()
    scratch = _git(wt_top, "commit-tree", tree, "-p", head, "-m",
                   "lane land: the staged change, replayed").stdout.strip()
    if not scratch or _git(wt_top, "reset", "--soft", scratch).returncode:
        return True
    # kept when empty and when main holds the same patch, so HEAD~1 is always what it replayed on
    if _git(wt_top, "rebase", "--empty=keep", "--reapply-cherry-picks", target).returncode:
        _git(wt_top, "rebase", "--abort")
        _git(wt_top, "reset", "--soft", head)
        return True
    _git(wt_top, "reset", "--soft", "HEAD~1")
    if _git(wt_top, "diff", "--cached", "--quiet").returncode == 0:
        _say(f"the staged change is already on {target}: nothing is left to commit")
        return False
    _say(f"replayed the staged change onto {target} before the commit")
    return True


def _rebase(wt_top: Path, branch: str, target: str) -> None:
    rebased = _git(wt_top, "rebase", target)
    if not rebased.returncode:
        return
    conflicts = _git(wt_top, "diff", "--name-only", "--diff-filter=U").stdout.split()
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


def _record_and_brief(root_top: Path, keep: Path, unit: str, author: str) -> tuple[bool, str]:
    """Record one unit's self-check on the root and write its QA brief; (ok, the unit's line)."""
    claims, mutants = (keep / name for name in hand_in_names(unit))
    missing = [p.name for p in (claims, mutants) if not p.is_file()]
    if missing:
        return False, (f"{unit}: self-check NOT RECORDED and no brief written - the hand-in "
                       f"carries no {' or '.join(missing)}")
    rec = _critic(root_top, "self-check", "record", "--unit", unit, "--claims", str(claims),
                  "--mutants", str(mutants), "--author", author)
    if rec.returncode:
        return False, f"{unit}: self-check REFUSED and no brief written - {_tail(rec.stderr)}"
    brief = _critic(root_top, "brief", "--unit", unit, "--seat", "qa")
    if brief.returncode or not brief.stdout.strip():
        return False, f"{unit}: self-check recorded; QA brief REFUSED - {_tail(brief.stderr)}"
    rel = BRIEFS / f"{unit}-qa.txt"
    (root_top / rel).parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(root_top / rel, brief.stdout)
    (root_top / BRIEFS / NO_BRIEF.format(unit=unit)).unlink(missing_ok=True)
    tier = re.search(r"^review tier: (\S+)", brief.stderr, re.M)
    fp = re.search(r"^brief fingerprint: (\S+)", brief.stderr, re.M)
    return True, (f"{unit}: self-check recorded; QA brief {rel}, review tier: "
                  f"{tier.group(1) if tier else 'UNKNOWN'}, fingerprint: "
                  f"{fp.group(1) if fp else 'UNKNOWN'}")


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
_TRAILER = re.compile(r"^[A-Za-z][A-Za-z0-9-]*: \S")
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
    once each, and a `Refs:` trailer for each landed unit that none of them refs."""
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
    again, so every worktree holds its own staged change and nothing was committed."""
    carrier, target = lanes_[0], lanes_[0].target
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
    msg = carrier.keep / LANDING_MSG
    sdlc_md.atomic_write(msg, _combined_message(lanes_))
    try:
        sha = _commit(carrier.top, msg, carrier.keep / "commit.log", target, where)
    except LandError as exc:
        stuck = _unwind(carrier.top, applied)
        if stuck:
            raise LandError(f"{exc}\nTaking the other worktrees' changes back out of "
                            f"{carrier.top} failed, so it still holds them: {stuck}") from None
        raise
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


def _preflight(root: Path, worktrees: list[Path], units: list[str]) -> list[_Lane]:
    """Each named worktree resolved, its units assigned, and every refusal made before anything
    moves: a worktree named twice, one with nothing to land, and for several, a unit whose
    hand-in is in none or more than one of them, or a file two of them stage differently."""
    lanes_: list[_Lane] = []
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
    if not several:
        lanes_[0].units = list(units)
        return lanes_
    for unit in units:
        owners = [lane for lane in lanes_
                  if any((lane.top / HAND_IN / name).is_file() for name in hand_in_names(unit))]
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
                good, line = _record_and_brief(root_top, lane.keep, unit, author or lane.name)
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


def _land(root: Path, worktrees: list[Path], units: list[str], author: str | None,
          price=None) -> int:
    lanes_ = _preflight(root, worktrees, units)
    root_top = _top(root, "the root")
    _keep_hand_ins(root_top, lanes_)
    names = [lane.name for lane in lanes_]
    record = {"worktrees": names, "paths": [str(lane.top) for lane in lanes_], "units": units,
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
    if record.get("worktrees") != names or sorted(record.get("units") or []) != sorted(units):
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
    units = [u.strip() for u in units or [] if u and u.strip()]
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
    A run past `timeout` is a LandError: what it did by then is unknown, so nothing follows."""
    try:
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args, "--root", str(root)],
                              cwd=str(root), capture_output=True, text=True, timeout=timeout,
                              check=False)
    except subprocess.TimeoutExpired:
        raise LandError(f"`{script} {' '.join(args[:2])}` ran past {timeout}s and was stopped, "
                        f"so nothing after it ran") from None


def _brief_of(root: Path, unit: str, verdict: Path | None = None) -> tuple[str, str]:
    """The fingerprint and tier of the QA brief `lane land` wrote for `unit`. The fingerprint is
    hashed from the saved text as `critic.py record --brief-file` hashes a first-round brief; the
    tier is the one `critic.py brief` noted beside that fingerprint when it printed the brief.
    When `verdict` is the file a `critic.py brief --rejoinder` issued for `unit`, its note gives
    the fingerprint and tier instead: that brief, not the saved one, is what the reviewer read.
    A rejoinder noted before the latest plain note of the saved brief's fingerprint may answer
    an earlier round, so it is refused. Under `review.author_self_check: block` a unit with no
    current self-check (`critic.self_check_gap`) is refused; under `report` that is a warning;
    `off` asks nothing."""
    import critic  # noqa: PLC0415 - sibling; only accept needs it
    rel = BRIEFS / f"{unit}-qa.txt"
    try:
        fp = critic.brief_fingerprint((root / rel).read_text(encoding="utf-8"))
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
    if gap and mode == "block":
        raise LandError(f"{gap}, so no self-check covers the diff {rel} would be the brief of, "
                        f"and nothing was recorded: land {unit} again with its self-check "
                        f"handed in, and that landing writes the brief "
                        f"(review.author_self_check: block)", 2)
    if gap:
        _say(f"WARNING {unit}: {gap}, so no self-check covers the diff {rel} is the brief of "
             f"(review.author_self_check: {mode}; `block` refuses the verdict)", err=True)
    uid, tier = sdlc_md.norm_id(unit), None
    try:
        notes = (root / critic.BRIEF_NOTES_REL).read_text(encoding="utf-8", errors="replace")
    except OSError:
        notes = ""
    # the brief text repeats from round to round, so the LATEST plain note of the saved
    # fingerprint is taken as the landing that saved it (a later re-brief of that scope too),
    # and a rejoinder noted before it is refused
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
            if not row.get("rejoinder"):
                landed_at = n
        if (verdict is not None and row.get("rejoinder") and row.get("verdict_file")
                and Path(str(row["verdict_file"])).resolve() == verdict):
            issued = (n, row)
    if not fp or not tier:
        raise LandError(f"{rel} hashes to fingerprint {fp or 'NONE'}, and no note in "
                        f"{critic.BRIEF_NOTES_REL} records the review tier of a brief with that "
                        f"fingerprint, so the verdict would be recorded at no known depth. "
                        f"Re-run `critic.py brief --unit {unit} --seat qa` and save it there", 2)
    if issued is None:
        return fp, tier
    n, row = issued
    again = (f"brief the seat again with `critic.py brief --unit {unit} --seat "
             f"{row.get('seat') or 'qa'} --rejoinder` and record the file that brief names")
    if landed_at is None or n < landed_at:
        raise LandError(f"{verdict} was issued by a rejoinder brief written before the landing "
                        f"that saved {rel} (fingerprint {fp}), so it may answer an earlier round "
                        f"and nothing was recorded: {again}", 2)
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
    try:
        said = verdict.read_text(encoding="utf-8")
    except OSError as exc:
        raise LandError(f"the verdict file cannot be read: {exc}", 2) from None
    fp, tier = _brief_of(root, unit, verdict)
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
    ran = _script(root, "verify_ac.py", "run", "--id", unit, "--timeout", str(timeout))
    if ran.returncode:
        _say(f"{unit}: NOT moved to {target}: `verify_ac.py run` exited {ran.returncode}, so a "
             f"criterion is not green:\n{_tail(ran.stdout + ran.stderr)}", err=True)
        return 1
    moved = _script(root, "transition.py", "set", "--id", unit, "--status", target)
    if moved.returncode:
        _say(f"{unit}: NOT moved to {target}: `transition.py set` exited {moved.returncode}:"
             f"\n{_tail(moved.stderr + moved.stdout)}", err=True)
        return 1
    _say(f"{unit}: moved to {target}")
    back = _script(root, "sprint.py", "lane", "return", "--units", unit, "--claimed",
                   f"{target} on an independent APPROVE (round {rnd})", "--timeout",
                   str(timeout), *passthrough)
    if back.stdout.strip():
        _say(back.stdout.rstrip())
    if back.stderr.strip():
        _say(back.stderr.rstrip(), err=True)
    return 1 if back.returncode else 0


def accept(root: Path | str, unit: str | None, verdict: Path | str | None,
           reviewer: str | None, terminal: dict[str, str], author: str | None = None,
           timeout: int = 300, passthrough: list[str] | None = None) -> int:
    """Record one unit's verdict and, on an APPROVE, verify, move and return it; the exit status.
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


def headless_command(harness: str, brief: str, model: str | None, worktree: Path) -> list[str]:
    """The argv that runs `brief` headless in `harness` with its usage printed as JSON, in each
    CLI's own form (its `--help`, 2026-11-06). Codex's sandbox is widened to the repository's
    git directory, which a worktree keeps outside itself, so its builder can stage."""
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


def _lane_worktree(root_top: Path, unit: str) -> Path:
    """The lane's worktree under `RUN_WORKTREES`, `lane-<unit>` with the id lowercased: reused
    when present, else checked out on the branch of that name where a lane whose worktree was
    removed without landing left one, else created on a new branch from the root's HEAD."""
    name = f"lane-{unit.lower()}"
    path = root_top / RUN_WORKTREES / name
    if path.is_dir():
        return path.resolve()
    if _run_git(root_top, "rev-parse", "--verify", "--quiet", f"refs/heads/{name}").returncode:
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


def _kill_group(proc: subprocess.Popen, grace: float = KILL_GRACE) -> None:
    """End `proc`'s whole process group and reap `proc`: SIGTERM first, so a `git add` in it
    removes the `index.lock` it holds, then up to `grace` seconds for the group to empty, then
    SIGKILL to whatever is left. The group is the lane's own, led by `proc`
    (`start_new_session`). At a timeout `proc` is still unreaped when the SIGTERM is sent, so the
    group id is still the lane's; after `proc` has exited and been reaped the group lives on
    only in what it left running, and POSIX does not reuse a group's id while the group has a
    member. Where `os.killpg` does not exist, only `proc` is killed."""
    if not hasattr(os, "killpg"):
        with contextlib.suppress(OSError):
            proc.kill()
        proc.wait()
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except OSError:
        proc.wait()
        return
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        proc.poll()  # a leader left unreaped would hold its group open for the whole grace
        try:
            os.killpg(proc.pid, 0)
        except OSError:
            proc.wait()
            return
        time.sleep(0.01)
    with contextlib.suppress(OSError):
        os.killpg(proc.pid, signal.SIGKILL)
    proc.wait()


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
def _watchdog():
    """A watchdog process, in a session of its own, that ends the lane's process group if this
    process dies while the lane runs: the CLI's own session puts it out of reach of a kill sent
    to this process's group, and no handler runs for SIGKILL. Yields `arm(pgid)`, which names
    the group to the watchdog; leaving the block stands the watchdog down and reaps it. Where
    `os.killpg` does not exist, no watchdog is started. A watchdog that cannot be started is a
    `LandError` (exit 2), raised before the CLI starts."""
    if not hasattr(os, "killpg"):
        yield lambda pgid: None
        return
    read, write = os.pipe()
    try:
        dog = subprocess.Popen([sys.executable, "-I", "-c", _WATCHDOG, str(KILL_GRACE)],
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
    lane's record said what was staged. A watchdog (`_watchdog`) ends the group the same way if
    this process dies while the CLI runs. A CLI that cannot be executed is a `LandError` (exit
    2) naming its path, raised before `on_start` is called."""
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
                _kill_group(proc)
                raise
            _kill_group(proc)
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
    cmd = headless_command(harness, brief, model, wt)
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
    staged = _run_git(wt, "diff", "--cached", "--name-only").stdout.split()
    session = _session_key()
    out_path = root_top / RUN_RECORDS / unit / f"{session}.out"
    sdlc_md.atomic_write(out_path, stdout)
    record = {
        "unit": unit, "run_id": run_id, "harness": harness, "model": model,
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
