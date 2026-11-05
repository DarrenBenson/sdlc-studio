"""`sprint lane land`: land a builder's staged lane on the branch the root has checked out.

A builder works in its own git worktree, stages its unit's Affects and stops, leaving a commit
message and its self-check files at the hand-in path `sdlc-studio/.local/lane/`. Landing that
lane is then one command, so the minutes the commit hook takes are paid in no agent's context:

1. copy the hand-in files out of the worktree, to `sdlc-studio/.local/lane/landed/<worktree>/`
   under the root, since removing the worktree removes them;
2. commit the staged change in the worktree through the repository's hooks, never a bypass;
3. rebase the worktree's branch onto the root's branch, aborting and naming the files on a
   conflict;
4. fast-forward the root's branch to it;
5. remove the worktree and delete its branch;
6. record each unit's self-check on the root with `critic.py self-check record`;
7. write each unit's QA brief with `critic.py brief --seat qa` to
   `sdlc-studio/.local/briefs/<unit>-qa.txt`, printing its review tier and fingerprint.

A failure in steps 2 to 4 stops the landing there and names the worktree to resume in. A hook
refusal leaves the staged change, the worktree and the root's branch as they were; a conflict
aborts the rebase and leaves the root's branch as it was. Re-running after a repair resumes: a
branch with nothing staged but commits ahead is rebased and landed without a second commit.
After the fast-forward nothing stops: a worktree that cannot be removed unforced is left in
place, and a unit whose self-check or brief is refused is named while the others are briefed.

Exit 2 is a refusal before anything was committed, 1 a landing that stopped part way or a unit
whose self-check or brief was not written, 0 a landed lane with every unit briefed.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from lib import sdlc_md

HAND_IN = Path("sdlc-studio") / ".local" / "lane"
LANDED = HAND_IN / "landed"
BRIEFS = Path("sdlc-studio") / ".local" / "briefs"
COMMIT_MSG = "commit-msg.txt"
CRITIC = Path(__file__).resolve().parent.parent / "critic.py"
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


def _commit(wt_top: Path, keep: Path, target: str) -> str:
    """Commit the staged change through the hooks; the short sha, or a LandError carrying the
    hook's own output."""
    log = keep / "commit.log"
    try:
        done = subprocess.run(["git", "-C", str(wt_top), "commit", "-F", str(keep / COMMIT_MSG)],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              timeout=COMMIT_TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        raise LandError(f"the commit's hooks ran past {COMMIT_TIMEOUT}s and were stopped, so "
                        f"nothing was committed and {target} is as it was. Resume in "
                        f"{wt_top}.") from None
    log.write_text(done.stdout or "", encoding="utf-8")
    if done.returncode:
        raise LandError(f"the commit was refused (exit {done.returncode}). The staged change, "
                        f"the worktree and {target} are as they were. Resume in {wt_top}, then "
                        f"re-run lane land. The whole output is in {log}; its last lines:\n"
                        f"{_tail(done.stdout)}")
    return _git(wt_top, "rev-parse", "--short", "HEAD").stdout.strip()


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


def _record_and_brief(root_top: Path, keep: Path, unit: str, author: str) -> tuple[bool, str]:
    """Record one unit's self-check on the root and write its QA brief; (ok, the unit's line)."""
    claims, mutants = keep / f"{unit}-claims.json", keep / f"{unit}-mutants.json"
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
    tier = re.search(r"^review tier: (\S+)", brief.stderr, re.M)
    fp = re.search(r"^brief fingerprint: (\S+)", brief.stderr, re.M)
    return True, (f"{unit}: self-check recorded; QA brief {rel}, review tier: "
                  f"{tier.group(1) if tier else 'UNKNOWN'}, fingerprint: "
                  f"{fp.group(1) if fp else 'UNKNOWN'}")


def _land(root: Path, worktree: Path, units: list[str], author: str | None) -> int:
    root_top, wt_top, branch, target = _resolve(root, worktree)
    hand_in = wt_top / HAND_IN
    staged = _git(wt_top, "diff", "--cached", "--quiet").returncode == 1
    if staged:
        msg = hand_in / COMMIT_MSG
        if not msg.is_file() or not msg.read_text(encoding="utf-8").strip():
            raise LandError(f"{wt_top} holds a staged change but no commit message at "
                            f"{HAND_IN / COMMIT_MSG}; nothing was committed", 2)
    elif _git(wt_top, "rev-list", "--count", f"{target}..HEAD").stdout.strip() == "0":
        raise LandError(f"{wt_top} has nothing staged and no commit ahead of {target}: there "
                        f"is nothing to land", 2)
    keep = root_top / LANDED / wt_top.name
    keep.mkdir(parents=True, exist_ok=True)
    for path in sorted(hand_in.glob("*")) if hand_in.is_dir() else []:
        if path.is_file():
            shutil.copy2(path, keep / path.name)
    _say(f"hand-in copied to {keep.relative_to(root_top)}")
    if staged:
        _say(f"committed {_commit(wt_top, keep, target)} in {wt_top} through the hooks")
    _rebase(wt_top, branch, target)
    _say(f"rebased {branch} onto {target}")
    ff = _git(root_top, "merge", "--ff-only", branch)
    if ff.returncode:
        raise LandError(f"{target} could not be fast-forwarded to {branch}, so {target} is as "
                        f"it was and the lane stays on {branch} in {wt_top}. Re-run lane land "
                        f"once that is cleared:\n{_tail(ff.stdout + ff.stderr)}")
    head = _git(root_top, "rev-parse", "--short", "HEAD").stdout.strip()
    _say(f"{target} fast-forwarded to {head}")
    failed = 0
    left = _remove(root_top, wt_top, branch)
    if left:
        failed += 1
        _say(f"WARNING {left}", err=True)
    else:
        _say(f"removed the worktree {wt_top} and the branch {branch}")
    for unit in units:
        ok, line = _record_and_brief(root_top, keep, unit, author or wt_top.name)
        failed += 0 if ok else 1
        _say(line, err=not ok)
    return 1 if failed else 0


def land(root: Path | str, worktree: Path | str | None, units: list[str],
         author: str | None = None) -> int:
    """Land one builder's lane; the exit status, with every step and refusal printed."""
    units = [u.strip() for u in units or [] if u and u.strip()]
    try:
        if not worktree:
            raise LandError("name the builder's worktree with --worktree", 2)
        if not units:
            raise LandError("name the lane's units with --units: each one's self-check is "
                            "recorded and its brief written, so none is assumed", 2)
        return _land(Path(root), Path(worktree), units, author)
    except LandError as exc:
        _say(f"sprint lane land: {exc}", err=True)
        return exc.code
