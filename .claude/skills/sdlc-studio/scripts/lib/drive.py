"""`sprint drive`: walk a wave's lanes from build to paperwork, and wake the model only at a stop.

`walk` is `sprint.py drive --harness <cli>`. It drives the open run's current wave: the first wave
of the plan (`sdlc-studio/.local/sprint-plan.json`) holding a unit not at a terminal status, the
batch units no wave names making a last wave of their own. Each unit walks `STEPS` in order, with
one line printed per step; the build, land and accept steps run `sprint.py` through its own entry
point, as an operator would:

1. build: `sprint.py lane run --harness <cli>` runs the unit's brief headless in its worktree;
2. land: `sprint.py lane land` commits it through the hooks, lands it, records the self-check
   and writes the QA brief;
3. brief: the QA brief the landing saved, and the verdict file it names;
4. review: that brief run headless in the same CLI, in the root, which writes the verdict file;
5. accept: `sprint.py lane accept` records the verdict and, on an APPROVE, runs the criteria and
   moves the unit to Done or Fixed;
6. return: the priced `lane return` that an APPROVE's accept runs, printed on its own line;
7. paperwork: one commit, through the hooks, of every change under `sdlc-studio/` outside
   `.local/`, leaving out the artefact and the verdict folder of every other batch unit.

A unit stops at the first of `STOPS` it meets: a refusal (a step that exits non-zero, or leaves
nothing for the next step to read), a WARNING line on the stderr of a step that exited 0, or a
REJECT, which is recorded and answered by no repair drive briefs or spawns. A rebase conflict at a
landing stops the wave: no unit is built, landed, reviewed or accepted after it (one already
accepted still returns and commits its paperwork, so none is left moved and uncommitted), the
landing before it stands and the lane stays committed in its worktree; drive retries nothing and
forces nothing. A wave whose every unit
completed stops at its end, and no unit of the next wave is started. Each stop prints a decision
record of at most `RECORD_LINES` lines: the unit, the step, the stop, the exit status, the lines it
quotes, the last lines of the step's output, where the whole output is kept
(`sdlc-studio/.local/drive/<unit>/<step>.log`) and the command that resumes.

Units whose Affects are disjoint build at once. A unit sharing a file with an earlier unit of the
wave starts once that unit has landed, so its worktree is made from the landing. Landings, accepts
and paperwork commits take the root one at a time. A WARNING naming another unit of the same wave
as briefed and never returned is that unit's own lane in flight beside it, so it stops nothing.
Re-running `walk` resumes each unit: one whose worktree holds a hand-in commit message starts at
its landing, one whose landing completed starts at its brief, and a review whose verdict file is
already written is not run again.

`step` is `sprint.py drive step --after <agent-id>`, for an orchestrator that spawns its own agents
and hands each one's return to one command, which ends with the next prompt's path:

- a builder's or repair builder's hand-back, from the worktree `agent-<id>`: `lane land` lands it,
  records the self-check, writes the QA brief and prices the return from the agent's transcript;
  the last line is the reviewer's prompt. A repair's prompt is the round's rejoinder
  (`critic.py brief --rejoinder`, quoting the unanswered REJECT), addressed to the reviewer who
  rejected, so that reviewer is resumed rather than a fresh one spawned;
- a reviewer's hand-back, whose verdict is in the file its prompt named: `lane accept` records it.
  An APPROVE is verified, moved and returned, its paperwork committed, and the last line is the
  builder prompt of the wave's next unit no prompt was issued for, or says the wave waits or has
  ended. A REJECT under the review round cap (`review.max_rounds`) is answered by the repair brief
  (`sprint.py lane brief --repair`), whose path is the last line. A REJECT at the cap stops with a
  decision record naming the cap and the operator's ruling owed.

A stop prints the decision record and no prompt path. Exit 2 is a refusal before anything moved
(no open run, an agent the run has no lane for), 0 a step that ends with a prompt or a wave's
state, otherwise the stopped step's own status, at least 1. Drive's lane record, which prompt each
unit was given and which reviewer answers it, is `sdlc-studio/.local/drive/lanes.json`.
"""
from __future__ import annotations

import contextlib
import json
import re
import shutil
import subprocess
import sys
import threading
import traceback
from pathlib import Path

from lib import lanes, run_state, sdlc_md

SCRIPTS = Path(__file__).resolve().parent.parent
#: Where drive keeps each step's whole output, the prompts it names, and its lane record.
DRIVE = Path("sdlc-studio") / ".local" / "drive"
PROMPTS = DRIVE / "prompts"
LANES = DRIVE / "lanes.json"
STEPS = ("build", "land", "brief", "review", "accept", "return", "paperwork")
#: The only points at which drive hands control back to the model; a record carries one of them.
STOPS = ("a refusal", "a warning", "a REJECT", "a rebase conflict", "a wave end")
REFUSAL, WARNED, REJECTED, CONFLICT, WAVE_END = STOPS
#: A decision record fits one screen.
RECORD_LINES = 30
#: Lines of a stopped step's output a record quotes at most; the whole output is kept on disk.
TAIL = 10
WIDTH = 300
QUOTED = 8
#: The steps after an APPROVE moved the unit: a stopped wave still finishes them.
_FINISHING = ("return", "paperwork")
STEP_TIMEOUT = 3600

_WARNING = re.compile(r"^\s*WARNING\b")
_IN_FLIGHT = re.compile(r"^\s*WARNING (\S+) was briefed at \S+ and never returned")
_CONFLICT = re.compile(r"Conflicting files: (.*?)\. The lane stays")
_VERDICT = re.compile(r"^(/.*/sdlc-studio/reviews/verdicts/.+\.txt)\nUNIT: \S+\nBRIEF: \S+\s*$",
                      re.M)
_AGENT = re.compile(r"[A-Za-z0-9_-]+")
_WHOLE = re.compile(r"The whole output is in (\S+?);")


class _Stop(Exception):
    """A step that stopped: its decision record and the exit status drive ends with."""

    def __init__(self, record: str, code: int, halt: bool = False) -> None:
        super().__init__(record)
        self.record, self.code, self.halt = record, max(int(code or 1), 1), halt


class _Refused(Exception):
    """A refusal before anything moved: exit 2."""


# -- shared ---------------------------------------------------------------------------------

def run_script(root: Path, script: str, *args: str,
               timeout: int = STEP_TIMEOUT) -> subprocess.CompletedProcess:
    """A sibling script through its own entry point, as an operator runs it by hand. Every step
    drive takes runs through here. A run past `timeout` answers exit 124 with what it said."""
    cmd = [sys.executable, str(SCRIPTS / script), *args, "--root", str(root)]
    try:
        return subprocess.run(cmd, cwd=str(root), capture_output=True, text=True,
                              timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(cmd, 124, lanes._text(exc.stdout),  # noqa: SLF001
                                           lanes._text(exc.stderr)  # noqa: SLF001
                                           + f"\nstopped at its {timeout}s timeout\n")


def keep(root: Path, unit: str, step: str, done: subprocess.CompletedProcess,
         shown: list[str] | None = None) -> str:
    """Write a step's whole output to `DRIVE/<unit>/<step>.log`; its path from the root."""
    rel = DRIVE / sdlc_md.norm_id(unit) / f"{step}.log"
    args = shown if shown is not None else done.args
    cmd = " ".join(map(str, args)) if isinstance(args, (list, tuple)) else str(args)
    sdlc_md.atomic_write(root / rel, f"$ {cmd}\nexit {done.returncode}\n--- stdout\n"
                                     f"{done.stdout or ''}\n--- stderr\n{done.stderr or ''}")
    return rel.as_posix()


def _clip(line: str) -> str:
    return line if len(line) <= WIDTH else line[:WIDTH - 3] + "..."


def decision_record(unit: str, step: str, stop: str, status=None, output: str = "",
                    kept: str | None = None, resume: str | None = None,
                    quote=()) -> str:
    """The one-screen record of a stop: at most `RECORD_LINES` lines naming the unit, the step,
    the stop (one of `STOPS`, else ValueError), the exit status, what it quotes, the last lines of
    the step's output, where the whole output is kept and the command that resumes."""
    if stop not in STOPS:
        raise ValueError(f"{stop!r} is not one of drive's stops: {', '.join(STOPS)}")
    head = [f"DRIVE STOPPED: {unit} at {step}, {stop}"]
    if status is not None:
        head.append(f"  exit status: {status}")
    head += [_clip(f"  {line}") for line in list(quote)[:QUOTED]]
    foot = ([f"  whole output: {kept}"] if kept else []) + ([f"  resume: {resume}"]
                                                           if resume else [])
    room = min(TAIL, RECORD_LINES - len(head) - len(foot) - 1)
    lines = [ln for ln in (output or "").strip().splitlines() if ln.strip()]
    tail = lines[-room:] if room > 0 and lines else []
    body = ["  last lines of its output:"] + [_clip(f"    | {ln}") for ln in tail] if tail else []
    return "\n".join((head + body + foot)[:RECORD_LINES])


def warnings(text: str, own=frozenset()) -> list[str]:
    """The WARNING lines of `text`, less those naming a unit of `own` (normalised ids) as briefed
    and never returned: that is a lane drive itself has in flight."""
    out = []
    for line in (text or "").splitlines():
        if not _WARNING.match(line):
            continue
        flight = _IN_FLIGHT.match(line)
        if flight and sdlc_md.norm_id(flight.group(1)) in own:
            continue
        out.append(line.strip())
    return out


def _status(root: Path, unit: str) -> tuple[str, bool]:
    """`unit`'s status and whether it is terminal for its type."""
    hit = sdlc_md.find_by_id(root, unit)
    if hit is None:
        return "not found", False
    raw = sdlc_md.extract_field(sdlc_md.read_text_safe(hit[0]), "Status") or ""
    status = sdlc_md.canonical_status(raw, sdlc_md.status_vocab(hit[1], root)) or raw.strip()
    return status, sdlc_md.is_terminal_status(hit[1], status)


def _affects(root: Path, unit: str) -> set[str]:
    hit = sdlc_md.find_by_id(root, unit)
    return set(sdlc_md.affects_files(sdlc_md.read_text_safe(hit[0]))) if hit else set()


def waves(root: Path, state: dict) -> list[list[str]]:
    """The open run's waves, in the batch's own spelling: the plan's, then one wave of the batch
    units no wave names."""
    from lib import resume_brief  # noqa: PLC0415
    batch = [str(u) for u in state.get("batch") or []]
    by_key = {sdlc_md.norm_id(u): u for u in batch}
    planned = [[by_key[k] for k in wave if k in by_key]
               for wave in resume_brief._waves(root, state)]  # noqa: SLF001
    planned = [wave for wave in planned if wave]
    named = {u for wave in planned for u in wave}
    rest = [u for u in batch if u not in named]
    return planned + ([rest] if rest else [])


def _open_run(root: Path) -> dict:
    state = run_state.read(root)
    if state.get("outcome") != run_state.RUNNING or not state.get("run_id"):
        raise _Refused(f"no run is open at {run_state.path(root)}: open one with "
                       f"`sprint.py plan --write`")
    return state


def _verdict_file(text: str) -> Path | None:
    """The verdict file a brief names, the last one when several are."""
    found = _VERDICT.findall(text or "")
    return Path(found[-1]) if found else None


def _written(path) -> bool:
    try:
        return bool(path) and Path(path).read_text(encoding="utf-8").strip() != ""
    except OSError:
        return False


def paperwork(root: Path, unit: str) -> tuple[subprocess.CompletedProcess | None, list[str]]:
    """Commit, through the hooks, every change under `sdlc-studio/` outside `.local/`, leaving
    out the artefact and the verdict folder of every other unit of the open run's batch, so a
    unit stopped beside this one keeps its move uncommitted: (the commit, or None with nothing
    to commit, and the paths). A refused commit is unstaged again, so the root is as it was."""
    status = lanes._git(root, "status", "--porcelain", "-z", "--untracked-files=all",  # noqa: SLF001
                        "--", "sdlc-studio").stdout.split("\0")
    paths, skip = [], False
    for entry in status:
        if skip or len(entry) < 4:
            skip = False
            continue
        skip = entry[0] in "RC"
        paths.append(entry[3:])
    verdicts, key = "sdlc-studio/reviews/verdicts/", sdlc_md.norm_id(unit)
    others = set()
    for other in run_state.read(root).get("batch") or []:
        hit = sdlc_md.find_by_id(root, str(other))
        if hit and sdlc_md.norm_id(str(other)) != key:
            with contextlib.suppress(ValueError):
                others.add(Path(hit[0]).resolve().relative_to(root).as_posix())
    paths = [p for p in paths if not p.startswith("sdlc-studio/.local/") and p not in others
             and not (p.startswith(verdicts)
                      and sdlc_md.norm_id(p[len(verdicts):].split("/", 1)[0]) != key)]
    if not paths:
        return None, []
    added = lanes._git(root, "add", "--", *paths)  # noqa: SLF001
    if added.returncode:
        return added, paths
    status_word = _status(root, unit)[0]
    done = lanes._git(root, "commit", "-q", "-m",  # noqa: SLF001
                      f"docs({unit}): record {unit}'s review and its move to {status_word}",
                      timeout=lanes.COMMIT_TIMEOUT)
    if done.returncode:
        lanes._git(root, "reset", "-q", "--", *paths)  # noqa: SLF001
    return done, paths


def _paperwork_step(root: Path, unit: str) -> str:
    done, paths = paperwork(root, unit)
    if done is None:
        return "nothing under sdlc-studio/ to commit"
    if done.returncode:
        kept = keep(root, unit, "paperwork", done)
        raise _Stop(decision_record(
            unit, "paperwork", REFUSAL, done.returncode, done.stdout + done.stderr, kept,
            resume=f"repair what the hook names, then git add -- {' '.join(paths)} && "
                   f"git commit -m \"docs({unit}): record {unit}'s review\""), done.returncode)
    sha = lanes._git(root, "rev-parse", "--short", "HEAD").stdout.strip()  # noqa: SLF001
    return f"committed {sha} ({len(paths)} file(s))"


def _stop_for(root: Path, unit: str, step: str, done: subprocess.CompletedProcess, resume: str,
              own=frozenset(), shown: list[str] | None = None) -> str:
    """Keep the step's output and raise the stop it makes, if any; the kept path otherwise."""
    kept = keep(root, unit, step, done, shown)
    said = (done.stdout or "") + (done.stderr or "")
    if done.returncode:
        conflict = _CONFLICT.search(done.stderr or "") if step == "land" else None
        if conflict:
            raise _Stop(decision_record(
                unit, step, CONFLICT, done.returncode, said, kept, resume=resume,
                quote=[f"conflicting files: {conflict.group(1)}",
                       "the landing before it stands; this lane stays committed in its "
                       "worktree; drive retried nothing and forced nothing"]),
                done.returncode, halt=True)
        # a refused commit keeps the hook's whole output beside the landing's hand-in
        whole = _WHOLE.search(said)
        raise _Stop(decision_record(unit, step, REFUSAL, done.returncode, said, kept,
                                    resume=resume,
                                    quote=[f"the commit's whole output: {whole.group(1)}"]
                                    if whole else ()), done.returncode)
    if warned := warnings(done.stderr, own):
        raise _Stop(decision_record(unit, step, WARNED, 0, said, kept, resume=resume,
                                    quote=warned[:3]), 1)
    return kept


def _blocking(text: str) -> list[str]:
    return [ln.strip() for ln in (text or "").splitlines() if re.match(r"\s*BLOCKING\s*:", ln)]


# -- walk -----------------------------------------------------------------------------------

class _Wave:
    """One wave's walk: the shared root lock, the landed set, each unit's outcome."""

    def __init__(self, root: Path, harness: str, model: str | None, timeout: int | None,
                 order: list[str]) -> None:
        self.root, self.harness, self.model, self.timeout = root, harness, model, timeout
        self.order = order
        self.own = {sdlc_md.norm_id(u) for u in order}
        self.root_lock, self.say_lock = threading.Lock(), threading.Lock()
        self.cond = threading.Condition()
        self.halt = threading.Event()
        self.landed: set[str] = set()
        self.records: dict[str, tuple[str, int]] = {}
        self.held: dict[str, str] = {}
        self.again = f"sprint.py drive --harness {harness}"

    def say(self, text: str) -> None:
        with self.say_lock:
            print(text, flush=True)

    def mark_landed(self, unit: str) -> None:
        with self.cond:
            self.landed.add(unit)
            self.cond.notify_all()


def _resume_at(root: Path, unit: str, wt: Path) -> str:
    """The step a unit's walk starts at: its brief once its landing completed, its landing when
    its worktree holds a hand-in commit message, else its build."""
    record = lanes._read_record(lanes._record_file(root, wt.name))  # noqa: SLF001
    if (record and unit in (record.get("units") or [])
            and all(s in (record.get("completed") or []) for s in lanes.LAND_STEPS)
            and (root / lanes.BRIEFS / f"{unit}-qa.txt").is_file() and not wt.is_dir()):
        return "brief"
    if (wt / lanes.HAND_IN / lanes.COMMIT_MSG).is_file():
        return "land"
    return "build"


def _walk_steps(w: _Wave, unit: str) -> None:
    root = w.root
    wt = root / lanes.RUN_WORKTREES / f"lane-{unit.lower()}"
    ctx: dict = {}
    first = _resume_at(root, unit, wt)
    if first != "build":
        w.say(f"{unit}: resuming at {first}")
    if STEPS.index(first) > STEPS.index("land"):
        w.mark_landed(unit)
    for step in STEPS[STEPS.index(first):]:
        if w.halt.is_set() and step not in _FINISHING:
            w.held[unit] = step
            return
        if step == "build":
            args = ["lane", "run", "--units", unit, "--harness", w.harness]
            args += ["--model", w.model] if w.model else []
            args += ["--timeout", str(w.timeout)] if w.timeout else []
            done = run_script(root, "sprint.py", *args,
                              timeout=(w.timeout or lanes.RUN_TIMEOUT) + 600)
            _stop_for(root, unit, step, done, f"sprint.py lane run --units {unit} --harness "
                                              f"{w.harness}, or {w.again}", w.own)
            staged = next((ln.split(":", 1)[1].strip() for ln in done.stdout.splitlines()
                           if ln.strip().startswith("staged:")), "nothing")
            line = f"{w.harness} session ran in {wt.name}; staged {staged}"
        elif step == "land":
            with w.root_lock:
                if w.halt.is_set():
                    w.held[unit] = step
                    return
                done = run_script(root, "sprint.py", "lane", "land", "--worktree", str(wt),
                                  "--units", unit, timeout=lanes.COMMIT_TIMEOUT + 600)
            if done.returncode == 0:
                w.mark_landed(unit)
            _stop_for(root, unit, step, done, f"repair the lane in {wt}, then {w.again}", w.own)
            line = next((ln.strip() for ln in done.stdout.splitlines()
                         if "fast-forwarded to" in ln), "landed")
        elif step == "brief":
            rel = lanes.BRIEFS / f"{unit}-qa.txt"
            try:
                ctx["brief"] = (root / rel).read_text(encoding="utf-8")
            except OSError:
                ctx["brief"] = ""
            ctx["verdict"] = _verdict_file(ctx["brief"])
            if ctx["verdict"] is None:
                raise _Stop(decision_record(
                    unit, step, REFUSAL, quote=[f"{rel.as_posix()} holds no brief naming a "
                                                f"verdict file, so no review can run"],
                    resume=f"sprint.py lane land --worktree {wt} --units {unit}, then "
                           f"{w.again}"), 1)
            line = f"{rel.as_posix()}, verdict file {ctx['verdict'].name}"
        elif step == "review":
            line = _review(w, unit, ctx)
        elif step == "accept":
            line = _walk_accept(w, unit, ctx)
            if line is None:
                return
        elif step == "return":
            lines = ctx["accepted"].stdout.splitlines()
            at = next((n for n, ln in enumerate(lines) if ln.startswith(f"{unit}: moved to")),
                      None)
            said = [ln.strip() for ln in lines[at + 1:] if ln.strip()] if at is not None else []
            if not said:
                raise _Stop(decision_record(unit, step, REFUSAL, quote=[
                    "lane accept printed no lane return after the move"],
                    kept=keep(root, unit, "accept", ctx["accepted"]),
                    resume=f"sprint.py lane return --units {unit}"), 1)
            line = _clip(" ".join(said))
        else:
            with w.root_lock:
                line = _paperwork_step(root, unit)
        w.say(f"{unit} {step}: {line}")


def _review(w: _Wave, unit: str, ctx: dict) -> str:
    verdict, brief = ctx["verdict"], ctx["brief"]
    if _written(verdict):
        return f"the verdict file {verdict.name} is already written; no reviewer is run again"
    binary = shutil.which(lanes.BINARIES[w.harness])
    if binary is None or len(brief.encode("utf-8")) > lanes.BRIEF_MAX_BYTES:
        why = (f"{lanes.BINARIES[w.harness]} is not on PATH" if binary is None
               else f"the brief is over {lanes.BRIEF_MAX_BYTES:,} bytes")
        raise _Stop(decision_record(unit, "review", REFUSAL, quote=[why], resume=w.again), 2)
    cmd = lanes.headless_command(w.harness, brief, w.model, w.root)
    cmd[0] = binary
    shown = ["<brief>" if a == brief else a for a in cmd]
    try:
        done = lanes._run_in_group(cmd, timeout=w.timeout or lanes.RUN_TIMEOUT,  # noqa: SLF001
                                   cwd=w.root, env=lanes._child_env())  # noqa: SLF001
    except subprocess.TimeoutExpired as exc:
        done = subprocess.CompletedProcess(cmd, 124, lanes._text(exc.stdout),  # noqa: SLF001
                                           lanes._text(exc.stderr)  # noqa: SLF001
                                           + "\nthe reviewer ran past its timeout\n")
    kept = _stop_for(w.root, unit, "review", done, w.again, w.own, shown)
    if not _written(verdict):
        raise _Stop(decision_record(unit, "review", REFUSAL, done.returncode,
                                    done.stdout + done.stderr, kept, resume=w.again,
                                    quote=[f"the reviewer wrote no verdict to {verdict}"]), 1)
    return f"{w.harness} reviewer wrote {verdict.name}"


def _walk_accept(w: _Wave, unit: str, ctx: dict) -> str | None:
    """The accept step's line, or None when the wave stopped while it waited for the root."""
    with w.root_lock:
        if w.halt.is_set():
            w.held[unit] = "accept"
            return None
        done = run_script(w.root, "sprint.py", "lane", "accept", "--unit", unit, "--verdict",
                          str(ctx["verdict"]), "--reviewer", f"qa-seat-{unit}-{w.harness}")
    ctx["accepted"] = done
    rejected = re.search(rf"^{re.escape(unit)}: REJECT recorded, round \S+", done.stdout, re.M)
    if rejected:
        raise _Stop(decision_record(
            unit, "accept", REJECTED, done.returncode, "", keep(w.root, unit, "accept", done),
            resume=f"sprint.py lane brief --repair --units {unit}",
            quote=[rejected.group(0).rstrip(";"), *_blocking(done.stdout),
                   "drive briefs and spawns no repair: the repair-scope brief is the "
                   "command under resume"]), done.returncode)
    _stop_for(w.root, unit, "accept", done, f"sprint.py lane accept --unit {unit} --verdict "
                                            f"{ctx['verdict']} --reviewer <name>", w.own)
    moved = next((ln.split(": ", 1)[1] for ln in done.stdout.splitlines()
                  if ln.startswith(f"{unit}: moved to")), "moved")
    return f"APPROVE recorded; {moved}"


def _walk(w: _Wave, unit: str) -> None:
    try:
        _walk_steps(w, unit)
    except _Stop as stop:
        w.records[unit] = (stop.record, stop.code)
        if stop.halt:
            w.halt.set()
    except Exception:  # noqa: BLE001
        w.records[unit] = (decision_record(unit, "walk", REFUSAL, "crashed",
                                           traceback.format_exc(), resume=w.again), 1)
    finally:
        with w.cond:
            w.cond.notify_all()


def _run_wave(w: _Wave) -> list[str]:
    """Walk each unit of the wave, starting a unit once every earlier unit sharing a file with it
    has landed; the units never started."""
    files = {u: _affects(w.root, u) for u in w.order}
    pending, threads = list(w.order), []
    with w.cond:
        while True:
            if not w.halt.is_set():
                for unit in list(pending):
                    ahead = w.order[:w.order.index(unit)]
                    if any(files[p] & files[unit] and p not in w.landed for p in ahead):
                        continue
                    pending.remove(unit)
                    thread = threading.Thread(target=_walk, args=(w, unit), daemon=True,
                                              name=f"drive-{unit}")
                    threads.append(thread)
                    thread.start()
            if not any(t.is_alive() for t in threads):
                break
            w.cond.wait(timeout=0.5)
    for thread in threads:
        thread.join()
    return pending


def wave_end_record(index: int, total: int, states: dict[str, str], harness: str) -> str:
    """The record of a wave whose every unit completed: each unit's state, and what is next."""
    lines = [f"DRIVE STOPPED: wave {index} of {total} ended, {WAVE_END}"]
    lines += [f"  {unit}: {state}" for unit, state in states.items()][:RECORD_LINES - 2]
    lines.append(f"  next: write the resume brief with `sprint.py handoff`; in a fresh session "
                 f"`sprint.py drive --harness {harness}` drives wave {index + 1}"
                 if index < total else
                 "  next: every wave has ended; the close runs next, in a fresh session")
    return "\n".join(lines)


def walk(root: Path | str, harness: str, model: str | None = None,
         timeout: int | None = None) -> int:
    """Drive the open run's current wave from build to paperwork; the exit status."""
    root = Path(root).resolve()
    try:
        state = _open_run(root)
        if harness not in lanes.BINARIES:
            raise _Refused(f"unknown harness {harness!r}; expected one of "
                           f"{', '.join(lanes.BINARIES)}")
        if shutil.which(lanes.BINARIES[harness]) is None:
            raise _Refused(f"{lanes.BINARIES[harness]} is not on PATH, so no {harness} lane "
                           f"can run")
        every = waves(root, state)
        if not every:
            raise _Refused("the open run's batch is empty, so there is no wave to drive")
    except _Refused as exc:
        print(f"sprint drive: {exc}", file=sys.stderr)
        return 2
    index = next((n for n, wave in enumerate(every)
                  if any(not _status(root, u)[1] for u in wave)), None)
    if index is None:
        print(f"drive: every unit of the open run's {len(every)} wave(s) is at a terminal "
              f"status; nothing is left to drive")
        return 0
    wave = every[index]
    w = _Wave(root, harness, model, timeout, [u for u in wave if not _status(root, u)[1]])
    w.say(f"drive: wave {index + 1} of {len(every)}: {', '.join(w.order)} ({harness})")
    never = _run_wave(w)
    for unit in w.order:
        if unit in w.records:
            print(w.records[unit][0])
    for unit, step in w.held.items():
        print(f"{unit}: held before its {step} step, as the wave stopped at a rebase conflict")
    for unit in never:
        print(f"{unit}: not started; an earlier unit of the wave sharing a file with it did "
              f"not land")
    if w.records or w.held or never:
        return max([code for _, code in w.records.values()] or [1])
    print(wave_end_record(index + 1, len(every), {u: _status(root, u)[0] for u in wave},
                          harness))
    return 0


# -- step -----------------------------------------------------------------------------------

def _load(root: Path) -> dict:
    try:
        data = json.loads((root / LANES).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _save(root: Path, record: dict) -> None:
    sdlc_md.atomic_write(root / LANES, json.dumps(record, indent=2, sort_keys=True) + "\n")


def _prompt(root: Path, name: str, text: str) -> Path:
    path = root / PROMPTS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, text if text.endswith("\n") else text + "\n")
    return path


def _agent_worktree(root: Path, agent: str) -> Path | None:
    listed = lanes._git(root, "worktree", "list", "--porcelain").stdout  # noqa: SLF001
    for line in listed.splitlines():
        if line.startswith("worktree ") and Path(line[9:]).name == f"agent-{agent}":
            return Path(line[9:])
    return None


def _after_builder(root: Path, agent: str, wt: Path, state: dict, record: dict) -> list[str]:
    hand_in = wt / lanes.HAND_IN
    keys = sorted({p.name[:-len(suffix)] for suffix in ("-claims.json", "-mutants.json")
                   for p in (hand_in.glob(f"*{suffix}") if hand_in.is_dir() else [])})
    batch = {sdlc_md.norm_id(u): u for u in state.get("batch") or []}
    if not keys or any(k not in batch for k in keys):
        raise _Refused(f"agent {agent}'s worktree {wt} hands in "
                       f"{', '.join(keys) if keys else 'no self-check'}, not units of the open "
                       f"run {state.get('run_id')}, so nothing was landed")
    units = [batch[k] for k in keys]
    done = run_script(root, "sprint.py", "lane", "land", "--worktree", str(wt), "--units",
                      *units, timeout=lanes.COMMIT_TIMEOUT + 600)
    _stop_for(root, units[0], "land", done, f"repair the lane in {wt}, then sprint.py drive "
                                            f"step --after {agent}", set(batch))
    out = [ln.strip() for ln in done.stdout.splitlines()
           if "fast-forwarded to" in ln or "self-check recorded" in ln or "return priced" in ln]
    out += [ln.strip() for ln in done.stderr.splitlines() if "UNPRICED" in ln]
    paths = []
    for unit in units:
        key = sdlc_md.norm_id(unit)
        entry = record.get(key) or {}
        if entry.get("stage") == "repair":
            rnd, reviewer = int(entry.get("round") or 1) + 1, entry.get("reviewer")
            brief = run_script(root, "critic.py", "brief", "--unit", unit, "--seat", "qa",
                               "--rejoinder")
            kept = keep(root, unit, "rejoinder", brief)
            if brief.returncode or not brief.stdout.strip():
                raise _Stop(decision_record(
                    unit, "rejoinder", REFUSAL, brief.returncode, brief.stdout + brief.stderr,
                    kept, resume=f"critic.py brief --unit {unit} --seat qa --rejoinder"),
                    brief.returncode)
            text = brief.stdout
            path = _prompt(root, f"{key}-review-r{rnd}.txt",
                           f"For reviewer agent {reviewer}, resumed for round {rnd} of {unit}: "
                           f"this re-review answers that reviewer's own REJECT, so resume "
                           f"agent {reviewer} with it rather than spawning a fresh "
                           f"reviewer.\n\n{text}")
            said = f"{unit}: repair landed; resume reviewer agent {reviewer} with its round " \
                   f"{rnd} prompt:"
        else:
            rnd, reviewer = 1, None
            text = (root / lanes.BRIEFS / f"{unit}-qa.txt").read_text(encoding="utf-8")
            path = _prompt(root, f"{key}-review-r1.txt", text)
            said = f"{unit}: landed; the reviewer's prompt (round 1):"
        verdict = _verdict_file(text)
        record[key] = {"unit": unit, "stage": "review", "round": rnd, "builder": agent,
                       "reviewer": reviewer, "verdict": str(verdict) if verdict else None,
                       "prompt": str(path.relative_to(root))}
        paths += [said, str(path)]
    _save(root, record)
    return out + paths


def _resolve_reviewer(agent: str, unit: str | None, record: dict) -> str:
    waiting = {k: e for k, e in record.items() if e.get("stage") == "review"}
    if unit:
        key = sdlc_md.norm_id(unit)
        if key not in waiting:
            raise _Refused(f"{unit} awaits no verdict in drive's lane record, so nothing was "
                           f"recorded")
        return key
    mine = [k for k, e in waiting.items() if e.get("reviewer") == agent]
    if mine:
        return mine[0]
    ready = [k for k, e in waiting.items() if not e.get("reviewer") and _written(e.get("verdict"))]
    if not ready:
        raise _Refused(f"the open run has no lane for agent {agent}: no worktree is named "
                       f"agent-{agent}, and no unit awaits a verdict from it, so nothing was "
                       f"changed")
    if len(ready) > 1:
        raise _Refused(f"{', '.join(waiting[k]['unit'] for k in ready)} each await a written "
                       f"verdict: name the unit agent {agent} reviewed with --unit")
    return ready[0]


def _after_reviewer(root: Path, agent: str, unit: str | None, state: dict,
                    record: dict) -> list[str]:
    import critic  # noqa: PLC0415
    key = _resolve_reviewer(agent, unit, record)
    entry = record[key]
    unit, verdict = entry["unit"], Path(entry.get("verdict") or "")
    if not _written(verdict):
        raise _Refused(f"agent {agent} has written no verdict to {verdict}, so nothing was "
                       f"recorded")
    done = run_script(root, "sprint.py", "lane", "accept", "--unit", unit, "--verdict",
                      str(verdict), "--reviewer", f"qa-seat-{unit}-{agent}")
    rejected = re.search(rf"^{re.escape(unit)}: REJECT recorded, round \S+", done.stdout, re.M)
    own = {sdlc_md.norm_id(u) for u in state.get("batch") or []}
    if not rejected:
        _stop_for(root, unit, "accept", done, f"sprint.py lane accept --unit {unit} --verdict "
                                              f"{verdict} --reviewer qa-seat-{unit}-{agent}",
                  own)
        entry["stage"] = "done"
        _save(root, record)
        lines = [ln.strip() for ln in done.stdout.splitlines() if ln.strip()]
        out = [f"{unit} accept: {'; '.join(lines)}"[:WIDTH]]
        out.append(f"{unit} paperwork: {_paperwork_step(root, unit)}")
        return out + _next_prompt(root, unit, state, record)
    kept = keep(root, unit, "accept", done)
    entry["reviewer"] = agent
    rounds, cap = len(critic.delivery_rounds(root, unit)), critic.review_ceiling(root)
    found = [rejected.group(0).rstrip(";"), *_blocking(done.stdout)]
    if rounds >= cap:
        entry["stage"] = "capped"
        _save(root, record)
        raise _Stop(decision_record(
            unit, "accept", REJECTED, done.returncode, "", kept,
            resume=f"the operator's ruling: carry {unit} as a known issue, or authorise one "
                   f"more round with a recorded decision (critic.py record --ruling DNNNN)",
            quote=[*found, f"round {rounds} is at the review round cap of {cap} "
                           f"(review.max_rounds), so no repair is briefed: the operator's "
                           f"ruling is owed"]), done.returncode)
    brief = run_script(root, "sprint.py", "lane", "brief", "--repair", "--units", unit)
    if brief.returncode or not brief.stdout.strip():
        _save(root, record)
        raise _Stop(decision_record(
            unit, "repair brief", REFUSAL, brief.returncode, brief.stdout + brief.stderr,
            keep(root, unit, "repair-brief", brief),
            resume=f"sprint.py lane brief --repair --units {unit}"), brief.returncode)
    path = _prompt(root, f"{key}-repair-r{rounds}.txt", brief.stdout)
    entry.update(stage="repair", round=rounds, prompt=str(path.relative_to(root)))
    _save(root, record)
    return [*found, f"{unit}: the repair builder's prompt (round {rounds} of a cap of {cap}):",
            str(path)]


def _next_prompt(root: Path, unit: str, state: dict, record: dict) -> list[str]:
    """After `unit` is accepted: the builder prompt of its wave's next unit given none yet, or
    what the wave waits on, or that it has ended."""
    every = waves(root, state)
    key = sdlc_md.norm_id(unit)
    k = next((n for n, wave in enumerate(every)
              if key in {sdlc_md.norm_id(u) for u in wave}), None)
    if k is None:
        return [f"{unit} is in no wave of the open run, so no next unit is named"]
    wave = every[k]
    left = [u for u in wave if not _status(root, u)[1]]
    if not left:
        nxt = ("the next wave starts after `sprint.py handoff`, in a fresh session"
               if k + 1 < len(every) else "every wave has ended: the close runs next")
        return [f"wave {k + 1} of {len(every)} has ended: "
                + "; ".join(f"{u} {_status(root, u)[0]}" for u in wave) + f". {nxt}"]
    building = set().union(*[_affects(root, u) for u in left
                             if (record.get(sdlc_md.norm_id(u)) or {}).get("stage")
                             in ("build", "repair")])
    fresh = [u for u in left if sdlc_md.norm_id(u) not in record
             and not (_affects(root, u) & building)]
    if not fresh:
        return [f"wave {k + 1} of {len(every)} waits on "
                + ", ".join(f"{u} ({(record.get(sdlc_md.norm_id(u)) or {}).get('stage', 'not started')})"
                            for u in left) + "; no unit is left to brief now"]
    nxt = fresh[0]
    brief = run_script(root, "sprint.py", "lane", "brief", "--units", nxt)
    if brief.returncode or not brief.stdout.strip():
        raise _Stop(decision_record(nxt, "builder brief", REFUSAL, brief.returncode,
                                    brief.stdout + brief.stderr,
                                    keep(root, nxt, "builder-brief", brief),
                                    resume=f"sprint.py lane brief --units {nxt}"),
                    brief.returncode)
    path = _prompt(root, f"{sdlc_md.norm_id(nxt)}-build.txt", brief.stdout)
    record[sdlc_md.norm_id(nxt)] = {"unit": nxt, "stage": "build",
                                    "prompt": str(path.relative_to(root))}
    _save(root, record)
    return [f"{nxt}: the next unit's builder prompt:", str(path)]


def step(root: Path | str, after: str, unit: str | None = None) -> int:
    """Handle one agent's hand-back as one command; the exit status, the last line printed the
    next prompt's path unless the step stopped."""
    root = Path(root).resolve()
    after = (after or "").strip()
    try:
        if not _AGENT.fullmatch(after):
            raise _Refused(f"{after!r} is not an agent id (letters, digits, `_` and `-`)")
        state = _open_run(root)
        record = _load(root)
        wt = _agent_worktree(root, after)
        lines = (_after_builder(root, after, wt, state, record) if wt is not None
                 else _after_reviewer(root, after, unit, state, record))
    except _Refused as exc:
        print(f"sprint drive step: {exc}", file=sys.stderr)
        return 2
    except _Stop as stop:
        print(stop.record)
        return stop.code
    for line in lines:
        print(line)
    return 0
