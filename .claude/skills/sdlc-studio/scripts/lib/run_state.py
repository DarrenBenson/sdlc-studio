#!/usr/bin/env python3
"""The run-state object - a sprint/epic run's identity, in one place.

The loop is executed by the MODEL calling discrete scripts, so until now a run had no
identity at all: no id, no start time, no recorded outcome. What a run did was scattered
across seven files nothing joined (`loop-state.json`, `epic-state.json`,
`sprint-plan.json`, `telemetry.jsonl`, `verify-report.json`, `reconcile-report.json`,
`wsjf-inputs.json`), so nothing could say "this run started here, aimed at that, and
stopped for this reason". The handoff needs exactly that sentence, and so does anything
later that must bound a run's appetite.

This is the object: run-local (`sdlc-studio/.local/run-state.json`, gitignored like the
rest of `.local/`), opened when the batch is approved (`sprint plan --write`) and closed
when the run stops (`handoff generate`).

Three properties are load-bearing, and each exists because breaking it loses work:

* **The batch is CUMULATIVE.** Re-planning mid-run (a re-cut tranche, a blocker sweep
  pulling work in) must never DISCARD an approved unit: the handoff joins over this batch,
  so a unit dropped from a narrowed re-cut - and never attempted, so absent from the loop
  state too - would land in no bucket at all and vanish from the handover. `open_run` on an
  open run takes the UNION, in first-approval order. Only a CLOSED run resets it.
* **Every mutation is LOCKED.** `update` is a read-modify-write; unlocked, concurrent
  writers silently lose each other's keys. The lock is taken here rather than left to each
  caller, because the callers that will hurt (a spend counter incremented per unit) have a
  wider window than any caller in this module does.
* **A corrupt file FAILS LOUD.** `read` raises rather than degrading a truncated file to
  "no run was ever opened" - which would let a close overwrite a real run's identity with a
  blank record, and print in the handover that the run was never opened. A silently dropped
  field is a lie the next reader inherits.

Extensible by contract: `update()` MERGES, and nothing here drops a key it does not
recognise. A later capability adds its own fields (an appetite ceiling, a spend counter)
without touching this module, and a close preserves them.

A library, not a command: the writers are `sprint.py` and `handoff.py`.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from . import sdlc_md

REL = Path("sdlc-studio") / ".local" / "run-state.json"
SCHEMA = 1

# Where a CLOSED run's record is kept once the next one opens. The live file holds exactly
# one run and every new run overwrites it, so before this a closed cycle's forecast, goal,
# batch and verdict were gone the moment the next cycle started - which makes an N-cycle
# rolling run unauditable: N sprints happened and one record survived. The archive is a copy
# taken at close, keyed by `run_id`, and the live file's shape is deliberately UNCHANGED so
# every existing reader sees exactly what it saw before.
ARCHIVE_REL = Path("sdlc-studio") / ".local" / "run-archive"

# The outcome vocabulary. A run is RUNNING until something says otherwise; the three ways
# it stops are the three the handoff exists for (goal reached, budget spent, blocked), plus
# the honest catch-all for an operator stop. An unknown value is REFUSED, never written: a
# free-text outcome is a field no gate can read, and this one is read.
RUNNING = "running"
GOAL_REACHED = "goal-reached"
BUDGET_SPENT = "budget-spent"
BLOCKED = "blocked"
STOPPED = "stopped"
# A close that FILED its remaining blockers as artefacts and ended honestly with them
# recorded - the bounded exit between "fix everything" and "bypass the gate". States
# plainly that work is outstanding; never used while a hard correctness gate is red.
CLOSED_OUTSTANDING = "closed-outstanding"
OUTCOMES = (RUNNING, GOAL_REACHED, BUDGET_SPENT, BLOCKED, STOPPED, CLOSED_OUTSTANDING)
CLOSED = tuple(o for o in OUTCOMES if o != RUNNING)

# The fields this module owns. Anything else a caller writes is preserved verbatim - see
# the module docstring: this list documents, it does not gate.
FIELDS = ("schema", "run_id", "started_at", "ended_at", "outcome", "goal", "batch",
          "batch_changes", "reopened",
          "plan", "handoff", "review_rounds", "review_ceiling_overrides",
          "session_token_baseline", "delegated_tokens")

# The session's token meter reading at the moment this run opened. The close subtracts it from
# the meter's CURRENT reading to get the tokens THIS run spent, because the harness transcript
# records one cumulative total per SESSION and a session can hold several sprints: without a
# baseline the second sprint closed in a session books the first sprint's spend as its own, and
# the third books both. That is not a rounding error - it published 341,450 and then 472,691
# tokens per point against a measured ~25,000/pt rate, each time as if it were a measurement.
#
# Absent means NOT ATTRIBUTABLE, never zero. A run opened before this field existed, or one whose
# session could not be read, has no baseline, and the honest report is then that the sprint's
# token cost cannot be attributed - exactly as an unmeasured elapsed reads UNMEASURED rather than
# falling back to a plausible number.
TOKEN_BASELINE = "session_token_baseline"

# The delegated agents' token totals, one record per agent, SUPPLIED rather than measured.
#
# The session transcript the baseline above is read from records the MAIN THREAD only: measured
# on one live transcript, 6,624,813 tokens of usage carried ZERO sidechain records, so every
# delegated agent's spend was invisible to it. A run that fanned out to four cluster agents
# published 439,982 as "the run's own spend" while the known true figure was at least 1,227,816.
#
# A delegated total therefore cannot be measured here. It can only be SUPPLIED - each agent
# reports its own total when it finishes - so it is recorded with its own provenance and the
# published sum is a LOWER BOUND (>=), never an equality. Same discipline as the mutation
# ledger's registered-versus-re-run distinction: a claim is kept, and kept labelled.
DELEGATED = "delegated_tokens"
#: The provenance every delegated record carries. Never `measured`: nothing here read a meter.
SUPPLIED = "supplied"

# The close review's rounds, appended one per sprint-level review. Seeded in `_blank()` so a
# new run carries them and `FIELDS` stays true of the record it documents; readers still go
# through `.get(...) or []` because a run opened BEFORE these existed has no such key on disk
# and must not raise.
REVIEW_ROUNDS = "review_rounds"
CEILING_OVERRIDES = "review_ceiling_overrides"

# The sentinel for "this round's token cost was not measured", which is NOT the same fact as
# a measured zero. A falsy test cannot tell them apart, and conflating them has shipped a
# defect on this codebase before: an unmeasured round summed as 0 understates the
# spend, and the operator is then shown a total that reads cheaper than the run was.
UNMEASURED = None


#: Where the harness keeps its per-session transcripts, overridable for tests and non-standard
#: installs. The default is Claude Code's layout: one directory per project (the absolute path
#: with `/` replaced by `-`), one JSONL file per session.
TRANSCRIPTS_ENV = "SDLC_STUDIO_TRANSCRIPTS"

#: The model marker for a session whose usage records name more than one model. Kept in step
#: with `retro.MODEL_MIXED` (the same string) so a mixed harness capture and a mixed per-unit
#: batch land in the same history cell and are excluded from the per-model rate the same way.
SESSION_MODEL_MIXED = "mixed"


class RunStateError(RuntimeError):
    """The run state exists but cannot be read. Never degraded to "there is no run": that
    reading would let a close write a blank record over a real run's identity."""


class DisjointBatchError(RuntimeError):
    """A plan would fold a batch sharing NO unit into the run already open.

    One project holds one run slot. An open run carries one Sprint Goal and one closing
    verdict, so absorbing a second, unrelated batch produces a run whose goal describes a
    fraction of it and whose verdict carries no information. An OVERLAPPING re-plan still
    accumulates - a re-cut or a blocker sweep pulling work in shares units with the run it
    extends - so only a batch disjoint from the open one is refused here.

    Raised BEFORE anything is written, so `run-state.json` is byte-identical after the refusal:
    the guard sits inside `open_run.apply`, ahead of every mutation, and `_mutate` writes only
    the value `apply` returns. The message names the open run's id, outcome and batch size, both
    ways forward as commands (close it, or deliberately re-plan it), and - when the run is
    mid-close - that a close attempt already ran against it and what it left outstanding, so the
    operator is pointed at finishing the close rather than working around the one run most likely
    to be worked around."""

    def __init__(self, run_id, outcome, batch_size, close_attempts=None,
                 repo_root: Path | str = "."):
        self.run_id = run_id
        self.outcome = outcome
        self.batch_size = batch_size
        # The latest close attempt's outstanding count, or None when no close was attempted.
        attempts = [a for a in (close_attempts or []) if isinstance(a, dict)]
        self.close_attempts = attempts
        self.outstanding = attempts[-1].get("outstanding") if attempts else None
        root = str(repo_root)
        lines = [
            f"plan refused: run {run_id} is already open (outcome={outcome}, batch of "
            f"{batch_size} unit(s)), and the batch just planned shares no unit with it. A "
            f"project holds one run slot: a batch disjoint from the open run is NOT folded in, "
            f"because the run carries one Sprint Goal and one closing verdict and a fused run "
            f"can be judged against neither.",
        ]
        if self.outstanding is not None:
            lines.append(
                f"{run_id} is mid-close, not finished: a close attempt has already run against "
                f"it and left {self.outstanding} item(s) outstanding. Finish that close rather "
                f"than working around the run.")
        lines.append("Two ways forward:")
        lines.append("  close the open run, then plan this batch as its own run:")
        lines.append(f"    sprint.py close --root {root}")
        lines.append("  or re-plan the open run deliberately, folding this batch into it by "
                     "planning a worklist that also names one of its units:")
        lines.append(f"    sprint.py plan --worklist WORKLIST.txt --write --root {root}")
        super().__init__("\n".join(lines))


class ReviewLedgerError(ValueError):
    """A write would contradict the review ledger at the moment it is recorded: a goal-verdict
    note naming a round count the ledger does not carry, a round recorded against a run that has
    already ended, or a reviewer label naming a round number other than the index it lands at.
    Each is refused here rather than written, because the ledger is the thing later readers trust
    to say how many rounds ran and when they stopped, and a note beside the data restating it
    wrong is the exact drift BG0261 was filed for."""


# Number words the ledger checks understand, so a note or reviewer label that spells a count out
# ("three rounds") is read the same as one that writes the digit ("3 rounds").
_WORD_NUMBERS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                 "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
_NUM = r"(?:\d+|" + "|".join(_WORD_NUMBERS) + r")"

# A COUNT of rounds ("three independent adversarial rounds", "5 rounds"): the number comes first
# and only a bounded set of review adjectives may sit between it and the word. Kept tight on
# purpose so an ordinal phrase ("one of the rounds", "round 3") is not misread as a count.
_ROUND_COUNT_RE = re.compile(
    r"\b(" + _NUM + r")\s+(?:(?:independent|adversarial|review|close|closing|full|more)\s+){0,3}"
    r"rounds?\b", re.I)

# An ORDINAL a reviewer label carries ("round 7"): the word comes first, then the number. This is
# what a reviewer-supplied string uses to name which round it is, and it must agree with the index
# the entry is stored at.
_ROUND_ORDINAL_RE = re.compile(r"\bround\s+(" + _NUM + r")\b", re.I)


def _as_int(token: str) -> int | None:
    t = token.lower()
    if t in _WORD_NUMBERS:
        return _WORD_NUMBERS[t]
    try:
        return int(t)
    except ValueError:
        return None


def stated_round_count(text: str | None) -> int | None:
    """The round COUNT a note narrates, or None when it names none. `len(review_rounds)` is the
    only honest source; this only exists to catch a note that restates a different one."""
    m = _ROUND_COUNT_RE.search(text or "")
    return _as_int(m.group(1)) if m else None


def stated_round_ordinal(text: str | None) -> int | None:
    """The round NUMBER a reviewer label names ("round 7" -> 7), or None. A label that names none
    is fine - the index stands. A label naming a different one is the disagreement BG0261 found."""
    m = _ROUND_ORDINAL_RE.search(text or "")
    return _as_int(m.group(1)) if m else None


def path(repo_root: Path | str) -> Path:
    return Path(repo_root) / REL


def read(repo_root: Path | str) -> dict:
    """The current run state, or `{}` when there is none.

    Never fabricated: a run that was not opened has no start time, and this returns nothing
    rather than inventing one. A file that EXISTS but does not parse RAISES - "unreadable"
    is not the same fact as "absent", and reporting it as absent destroys the run it failed
    to read."""
    p = path(repo_root)
    try:
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise RunStateError(f"cannot read the run state at {p}: {exc}") from exc
    if not text.strip():
        return {}
    try:
        state = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RunStateError(
            f"the run state at {p} is not valid JSON ({exc}) - it holds the run's id, start "
            f"time, approved batch and outcome, and nothing may overwrite it blind. Repair "
            f"it, or delete it to start a fresh run (the run it described is then "
            f"unrecoverable, which is the point of saying so out loud)") from exc
    if not isinstance(state, dict):
        raise RunStateError(
            f"the run state at {p} is not an object (got {type(state).__name__})")
    return state


def write(repo_root: Path | str, state: dict) -> dict:
    """Persist the state atomically (a crash mid-write must not truncate a run's identity).
    Anything mutating an EXISTING state goes through `_mutate`, which holds the lock."""
    p = path(repo_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(p, json.dumps(state, indent=2))
    return state


def archive_dir(repo_root: Path | str) -> Path:
    return Path(repo_root) / ARCHIVE_REL


def archive_path(repo_root: Path | str, run_id: str) -> Path:
    return archive_dir(repo_root) / f"{run_id}.json"


def archive(repo_root: Path | str, state: dict | None = None) -> Path | None:
    """Copy a run's record to its own file, so a closed run stays readable after the next
    one opens. Returns the path written, or None when there is no run to archive.

    Keyed by `run_id` and rewritten in place, so archiving the same run twice leaves one
    record, not two - the boundary archives at close and the next open archives again as a
    safety net, and neither may double-count. A run with no `run_id` (nobody opened it) is
    NOT archived: a record with no identity cannot be joined to anything later."""
    state = read(repo_root) if state is None else state
    run_id = state.get("run_id")
    if not run_id:
        return None
    p = archive_path(repo_root, run_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(p, json.dumps(state, indent=2))
    return p


def archived(repo_root: Path | str) -> list[dict]:
    """Every archived run, oldest first. An unreadable record is SKIPPED rather than raising:
    unlike the live file, a damaged archive entry cannot cause a close to overwrite a real
    run's identity, so failing the whole read would lose the intact records for nothing."""
    d = archive_dir(repo_root)
    if not d.is_dir():
        return []
    out = []
    for p in sorted(d.glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(rec, dict) and rec.get("run_id"):
            out.append(rec)
    # Chronological, and the CYCLE INDEX breaks a tie before the run id does. Two cycles of a
    # fast run start inside the same second, and `short_ulid` is not monotonic within one - so
    # ordering on the id alone reads a rolling run's cycles back out of order, which is exactly
    # the sequence the archive exists to preserve.
    def _index(rec: dict) -> int:
        """The cycle index, or 0 when it is absent, not a dict, or not a number.

        Coerced defensively rather than with a bare `int()`: this runs inside the SORT KEY,
        which sits outside the try/except above, so one malformed record raised and lost
        every intact one - precisely what this function's contract says it will not do.
        AttributeError is caught too: `cycle` is JSON, so it can be a string or a list, and
        the first repair caught only the one variant its test happened to exercise.
        """
        try:
            return int((rec.get("cycle") or {}).get("index") or 0)
        except (ArithmeticError, AttributeError, TypeError, ValueError):
            # ArithmeticError covers OverflowError: json round-trips Infinity by default, so
            # this module can WRITE a value int() then refuses. Each repair here has caught
            # only the shapes its own test exercised; the exception set is now the whole
            # family rather than a list of the ones seen so far.
            return 0

    def _started(rec: dict) -> str:
        """The start time as a STRING. A non-string `started_at` would otherwise raise from
        the tuple comparison itself, outside `_index` entirely - the same contract breach
        one level out."""
        value = rec.get("started_at")
        return value if isinstance(value, str) else ""

    def _rid(rec: dict) -> str:
        """The run id as a STRING. It is the final tie-break, so a non-string reaches the
        tuple comparison only when started_at and the index both tie - rare, and it raised."""
        value = rec.get("run_id")
        return value if isinstance(value, str) else ""

    out.sort(key=lambda r: (_started(r), _index(r), _rid(r)))
    return out


def read_archived(repo_root: Path | str, run_id: str) -> dict:
    """One archived run by id, or `{}` when it was never archived."""
    p = archive_path(repo_root, run_id)
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return rec if isinstance(rec, dict) else {}


def is_open(repo_root: Path | str) -> bool:
    """True when a run is open (recorded and not yet closed)."""
    return read(repo_root).get("outcome") == RUNNING


def _blank() -> dict:
    """The record for a run nobody opened. `run_id`, `started_at` and the token baseline are
    None, and stay None: a close that invented a start time - or a baseline - would put a
    false fact in the one file the next reader trusts. An unopened run says so."""
    return {"schema": SCHEMA, "run_id": None, "started_at": None, "ended_at": None,
            "outcome": RUNNING, "goal": None, "batch": [], "plan": None, "handoff": None,
            REVIEW_ROUNDS: [], CEILING_OVERRIDES: [], TOKEN_BASELINE: None, DELEGATED: [],
            # Seeded empty like its siblings: `reopened` is part of the documented shape, and a
            # field that only appears after a reopen would make every reader test for it.
            "reopened": [],
            # Likewise `batch_changes`: the drop/add ledger is part of the shape from the start, so
            # a reader never has to test for its presence - it is [] until the batch is first mutated.
            "batch_changes": []}


def _mutate(repo_root: Path | str, fn) -> dict:
    """Read-modify-write the run state under the shared advisory lock.

    The single mutation path. Every writer goes through it, so a writer cannot read the
    state, be overtaken, and then write its stale copy back over the other's keys. It is
    the same advisory lock the id allocator and the finding filer take, for the same
    reason."""
    with sdlc_md.allocation_lock(repo_root):
        state = read(repo_root)          # inside the lock; a corrupt file still raises
        return write(repo_root, fn(state))


def _union(existing, incoming) -> list[str]:
    """The approved batch, accumulated: first-approval order, no duplicates. An approved
    unit is never removed by a later, narrower plan."""
    out = [sdlc_md.norm_id(b) for b in (existing or [])]
    seen = set(out)
    for b in incoming:
        n = sdlc_md.norm_id(b)
        if n not in seen:
            out.append(n)
            seen.add(n)
    return out


# The close artefacts a finalised run carries. A run holding ANY of them has been judged or
# closed - it is history - even if its `outcome` string was never moved off `running`: a close
# chain that records the goal-verdict but stops before the handoff leaves exactly that
# inconsistent state. `open_run` treats such a run as CLOSED so the next plan mints a fresh run
# rather than accumulating the new batch onto - and clobbering the verdict of - the judged one.
_CLOSE_ARTEFACTS = ("sprint_goal_verdict", "ended_at", "handoff")


def _mint_run_id(repo_root: Path | str, outgoing: dict | None = None) -> str:
    """A run id no run in this project has already used.

    `short_ulid` is 6 timestamp characters - roughly a 17-minute bucket - plus 2 random ones, so
    two mints inside one bucket collide with probability about 1 in 1,024, and its own docstring
    names the allocator's glob-retry as the true backstop. The RUN id never went through one: it
    was minted and used. That surfaced as a commit gate failing at random on an unchanged tree,
    but the real exposure is that two runs could share an identity, and the telemetry, archive
    and velocity records all join on it.

    So the ALLOCATOR provides what the generator cannot. Checked against every archived run (the
    register of what this project has opened) and the run being replaced, retried on a clash and
    extended on a persistent one - the same shape `sdlc_md.mint_v3_id` uses for artefact ids.

    EVERY candidate is checked, including the extended one. An unchecked final fallback would be
    exactly the luck this allocator exists to replace: drive both generators constant and the old
    one returned a duplicate while the docstring above claimed uniqueness by construction. When
    even the extended suffix cannot produce a free id, that is a broken generator rather than an
    unlucky one, so this RAISES: returning a known-duplicate id would silently merge two runs'
    telemetry, archive and velocity records, which is the data problem the whole allocator exists
    to prevent.
    """
    taken = {r.get("run_id") for r in archived(repo_root)}
    # Not dead, and deliberately kept: `open_run` archives the outgoing run before minting, so
    # this is usually redundant - but only while the archive write SUCCEEDS. An archive that
    # could not be written (a read-only or full `.local`) leaves the register without the run
    # being replaced, and this is then the only thing standing between the new run and its
    # predecessor's identity. Pinned directly by test rather than through `open_run`.
    taken.add((outgoing or {}).get("run_id"))
    for _ in range(16):
        rid = f"RUN-{sdlc_md.short_ulid()}"
        if rid not in taken:
            return rid
    for _ in range(16):
        rid = f"RUN-{sdlc_md.new_ulid()[:12]}"   # extend the suffix on a persistent clash
        if rid not in taken:
            return rid
    raise RuntimeError(
        "could not mint a run id no run in this project already holds: 32 candidates, from both "
        "the short and the extended generator, were all already taken. That is a broken id "
        "generator, not bad luck - refusing to hand back a duplicate, because the telemetry, "
        "archive and velocity records all join on the run id")


def _is_spent(state: dict) -> bool:
    """True when the run is finalised: a terminal outcome, or a close artefact recorded while
    the outcome string still says `running`. A judged run is history regardless of the string.

    `close_attempts` is deliberately NOT a close artefact (see `_CLOSE_ARTEFACTS`): a run whose
    only close artefact is a FAILED close attempt is still `running`, so it stays open and
    protected - the disjoint guard covers it rather than exempting it, which is the run most
    likely to be worked around."""
    if state.get("outcome") != RUNNING or not state.get("run_id"):
        return True
    return any(state.get(k) for k in _CLOSE_ARTEFACTS)


def _disjoint(state: dict, batch) -> bool:
    """True when `batch` shares no unit with an OPEN run that already holds one. False for a
    spent run (the next plan mints fresh), an empty incoming batch, and an open run with nothing
    approved yet (there is nothing to be disjoint from). Ids are normalised on both sides so a
    spelling difference is never read as disjointness."""
    if batch is None or _is_spent(state):
        return False
    existing = {sdlc_md.norm_id(b) for b in (state.get("batch") or [])}
    incoming = {sdlc_md.norm_id(b) for b in batch}
    return bool(existing) and not (existing & incoming)


def disjoint_refusal(repo_root: Path | str, batch) -> "DisjointBatchError | None":
    """The refusal `open_run` would raise for planning `batch` against the open run, or None
    when it would accept. PURE - reads the state, writes nothing - so a caller can refuse before
    writing any sibling artefact (the sprint plan, the forecast log) that the refusal should not
    leave behind. `open_run` enforces the same rule inside its lock; this only pre-empts it."""
    state = read(repo_root)
    if not _disjoint(state, batch):
        return None
    return DisjointBatchError(state.get("run_id"), state.get("outcome"),
                              len({sdlc_md.norm_id(b) for b in (state.get("batch") or [])}),
                              close_attempts=state.get("close_attempts"), repo_root=repo_root)


def session_tokens(repo_root: Path | str, transcripts_dir: Path | str | None = None) -> dict:
    """The CURRENT session's harness-tracked token total, read from the transcript.

    The harness records usage per message; the most recently modified session file is the one
    running this call. Summed: input, output and cache-creation tokens of every record carrying
    usage. Cache READS are excluded - they re-bill the same context every turn, so counting them
    would price the conversation quadratically rather than the work.

    Returns {"tokens", "source", "basis"} on success, {"tokens": None, "reason"} when the total
    cannot be read - and the caller must SAY which it got.

    It lives in this module rather than in `retro` because `open_run` has to stamp the baseline
    itself: `open_run` is the only place that knows a fresh run is being minted, and `retro`
    imports this module, so the reader has to sit at the lower layer. `retro.harness_tokens`
    wraps it, so both the baseline and the close read one definition.
    """
    d = transcripts_dir or os.environ.get(TRANSCRIPTS_ENV)
    if not d:
        d = Path.home() / ".claude" / "projects" / str(Path(repo_root).resolve()).replace("/", "-")
    d = Path(d)
    if not d.is_dir():
        return {"tokens": None, "reason": f"no harness transcript directory at {d}"}
    files = sorted(d.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    if not files:
        return {"tokens": None, "reason": f"no session transcript (*.jsonl) in {d}"}
    src = files[-1]
    total, seen = 0, False
    #: The distinct models that spent the counted tokens. Collected only from the records that
    #: carry usage - a record with no usage bought nothing, so its model must not colour the
    #: attribution. One model reports as itself; more than one reports as SESSION_MODEL_MIXED,
    #: never one picked from the set, so a sprint run across two models is booked to neither's
    #: rate rather than the wrong one's.
    models_seen: set[str] = set()
    try:
        with src.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                msg = rec.get("message")
                usage = (msg.get("usage") if isinstance(msg, dict) else None) or rec.get("usage")
                if not isinstance(usage, dict):
                    continue
                seen = True
                model = (msg.get("model") if isinstance(msg, dict) else None) or rec.get("model")
                if isinstance(model, str) and model.strip():
                    models_seen.add(model.strip())
                try:
                    total += sum(int(usage.get(k) or 0) for k in
                                 ("input_tokens", "output_tokens", "cache_creation_input_tokens"))
                except (ArithmeticError, AttributeError, TypeError, ValueError) as exc:
                    # A malformed usage value REFUSES the whole read rather than skipping the
                    # record. Skipping would return a total that is quietly short, and a short
                    # baseline inflates the delta measured against it - a wrong number, which is
                    # the expensive failure here. Not-attributable is the cheap one.
                    return {"tokens": None,
                            "reason": f"transcript {src.name} carries a malformed usage record "
                                      f"({type(exc).__name__}: {exc}) - the total cannot be "
                                      f"trusted, so no figure is reported"}
    except (ArithmeticError, AttributeError, OSError, TypeError, ValueError) as exc:
        # The whole family, not the shapes seen so far. This transcript format is the harness's,
        # not this project's, and it has already moved once (hence the two-shape probe above).
        # `archived()._index` in this same file records the same lesson from its own repairs.
        return {"tokens": None, "reason": f"transcript {src} unreadable ({type(exc).__name__}: {exc})"}
    if not seen or total <= 0:
        return {"tokens": None, "reason": f"transcript {src.name} carries no usage records"}
    if len(models_seen) == 1:
        model = next(iter(models_seen))
    elif len(models_seen) > 1:
        model = SESSION_MODEL_MIXED
    else:
        model = None   # a transcript that named no model - the caller reports it unrecorded
    return {"tokens": total, "source": str(src), "model": model,
            # MAIN THREAD ONLY, said here because here is where it is true: the transcript
            # carries no subagent (sidechain) usage record at all - measured, 6,624,813 tokens
            # of usage with ZERO from sidechains - so a session that delegated work spent more
            # than this. Every caller inherits the sentence, and none of them may drop it.
            "basis": "current-session transcript usage sum, MAIN THREAD only "
                     "(input + output + cache creation; cache reads excluded). The transcript "
                     "records no subagent usage, so this is a LOWER BOUND on what the session "
                     "cost"}


def _session_baseline(repo_root: Path | str) -> dict | None:
    """The token meter reading to stamp on a run being minted, or None.

    `{"tokens": N, "source": <transcript path>, "at": <iso>}`. The SOURCE is half the record:
    the delta is only meaningful against the same session file, so a close that happens in a
    later session can tell that this baseline is not its own rather than subtracting a number
    from an unrelated meter.

    None whenever the meter cannot be read - including a session whose transcript carries no
    usage yet, whose true baseline is zero. That is a deliberate false negative: the run then
    reports NOT ATTRIBUTABLE, and losing a measurement is the cheap failure here while
    publishing a wrong one is the expensive one. Never raises: a plan must not fail because a
    transcript was unreadable.
    """
    try:
        cap = session_tokens(repo_root)
    except (ArithmeticError, AttributeError, OSError, TypeError, ValueError):
        # Backstop, deliberately the whole family: `session_tokens` is meant to return rather
        # than raise, but "a plan must not fail because a transcript was unreadable" has to hold
        # even when that contract is broken. A narrower clause here let a TypeError from one
        # malformed record abort `sprint plan --write` entirely, so no run was minted at all.
        return None
    if not cap.get("tokens"):
        return None
    return {"tokens": int(cap["tokens"]), "source": cap.get("source"),
            "at": sdlc_md.now_iso8601()}


def open_run(repo_root: Path | str, batch: list[str] | None = None, goal: str | None = None,
             plan: str | None = None) -> dict:
    """Open a run, or re-plan the OPEN one.

    Re-running `sprint plan --write` must not restart the clock: an already-open run keeps
    its `run_id` and `started_at`, and its batch ACCUMULATES (see the module docstring - a
    narrowing re-cut must not silently discard work the run was approved to do). A run that
    has been CLOSED - or judged but left `running`, an inconsistent state - is history: the
    next open mints a fresh run with a fresh batch, so a handoff can never be re-attributed
    to the run after it.

    A FRESH run is stamped with the session's token baseline (see TOKEN_BASELINE). A re-plan
    is not: the baseline belongs to the moment the run started, and moving it forward mid-run
    would silently discount everything spent before the re-cut.

    A DISJOINT batch against an OPEN run is REFUSED (`DisjointBatchError`), not fused: one
    project holds one run slot, and a batch sharing no unit with the open run cannot join it
    without stranding the run's goal verdict. The refusal is raised before any mutation, so the
    state file is byte-identical afterwards. An overlapping re-plan is unaffected.
    """
    def apply(state: dict) -> dict:
        if _is_spent(state):
            # ARCHIVE BEFORE BLANKING. This is the last moment the finished run exists: the
            # next statement replaces it. `close_run` normally archived it already and this
            # rewrites the same key, but a run judged and left `running` never reached a
            # close, and without this its record would be destroyed here unrecorded.
            archive(repo_root, state)
            # Minted AFTER the archive above, so the run being replaced is already in the
            # register the new id is checked against.
            state = {**_blank(), "run_id": _mint_run_id(repo_root, state),
                     "started_at": sdlc_md.now_iso8601(),
                     TOKEN_BASELINE: _session_baseline(repo_root)}
        elif _disjoint(state, batch):
            # The run is OPEN (not spent) and this batch shares no unit with it: a second sprint
            # the one run slot cannot hold. Refused here, ahead of every write - inside the lock,
            # on the state just read - so nothing is minted, nothing is archived, and the state
            # file is untouched. An overlapping re-plan falls through and accumulates below.
            raise DisjointBatchError(
                state.get("run_id"), state.get("outcome"),
                len({sdlc_md.norm_id(b) for b in (state.get("batch") or [])}),
                close_attempts=state.get("close_attempts"), repo_root=repo_root)
        if batch is not None:
            state["batch"] = _union(state.get("batch"), batch)
        if goal is not None:
            state["goal"] = goal
        if plan is not None:
            state["plan"] = plan
        return state

    return _mutate(repo_root, apply)


def update(repo_root: Path | str, **fields) -> dict:
    """Merge fields into the run state. Unknown keys are kept: this is the extension point,
    and a silently-dropped field is a lie the next reader inherits. With no run open the
    fields land on a blank record (no fabricated start time). Locked: see `_mutate`."""
    if "outcome" in fields:
        _check_outcome(fields["outcome"])

    def apply(state: dict) -> dict:
        state = state or _blank()
        state.update(fields)
        return state

    return _mutate(repo_root, apply)


def drop_from_batch(repo_root: Path | str, unit_id: str, reason: str) -> dict:
    """Remove a unit from the OPEN run's approved batch and record the change.

    Drop judges THIS BATCH: the unit leaves `batch`, so the done-gate and sign-off lanes - which
    read `batch` - stop demanding it, while its own status is left untouched. That is the whole
    distinction from `Deferred`, which judges the WORK: a Deferred unit keeps its place in the
    batch and still blocks the close. Every drop is recorded in `batch_changes` (action, id,
    reason, timestamp) so the batch a sprint DELIVERED can always be reconstructed against the
    batch it was PLANNED with. A drop needs a reason - it is recorded, not silent - and an open
    run to drop from; it never fabricates one."""
    if not (reason or "").strip():
        raise RunStateError("a batch drop needs a reason - it is recorded, not silent")
    norm = sdlc_md.norm_id(unit_id)

    def apply(state: dict) -> dict:
        if (state or {}).get("outcome") != RUNNING:
            raise RunStateError(
                "no open run to drop from - `sprint batch drop` needs a running sprint")
        batch = state.get("batch") or []
        kept = [b for b in batch if sdlc_md.norm_id(b) != norm]
        if len(kept) == len(batch):
            raise RunStateError(f"{norm} is not in the open batch - nothing to drop")
        state["batch"] = kept
        state["batch_changes"] = list(state.get("batch_changes") or []) + [
            {"action": "drop", "id": norm, "reason": reason.strip(), "at": sdlc_md.now_iso8601()}]
        return state

    return _mutate(repo_root, apply)


def add_to_batch(repo_root: Path | str, unit_id: str) -> dict:
    """Add a unit to the OPEN run's approved batch and record the change.

    The added unit is then held to the same gates as the rest - the done-gate reads `batch`, so
    appending to it IS subjecting the unit to the gate. Idempotent on the batch (an id already
    present is not duplicated), but every call is recorded in `batch_changes` so the history stays
    honest. Needs an open run to add to."""
    norm = sdlc_md.norm_id(unit_id)

    def apply(state: dict) -> dict:
        if (state or {}).get("outcome") != RUNNING:
            raise RunStateError(
                "no open run to add to - `sprint batch add` needs a running sprint")
        batch = [sdlc_md.norm_id(b) for b in (state.get("batch") or [])]
        already = norm in batch
        if not already:
            batch.append(norm)
        state["batch"] = batch
        entry = {"action": "add", "id": norm, "at": sdlc_md.now_iso8601()}
        if already:
            entry["note"] = "already in batch"
        state["batch_changes"] = list(state.get("batch_changes") or []) + [entry]
        return state

    return _mutate(repo_root, apply)


def appetite_record(*, accepted_units: int, accepted_minutes: float,
                    standing_units: int, standing_minutes: float) -> dict:
    """The run's appetite record: the ACCEPTED pair the breaker stops on, AND the STANDING one it
    was measured against (the sprint capacity), with the overage flagged when the accepted exceeds
    the standing on either axis. Pure - the plan folds this into its single atomic run-state write,
    and `record_appetite` writes it directly. Keeps `units`/`minutes` as the accepted pair the
    existing appetite readers (loop_guard, handoff) already use, so this is additive."""
    acc_u, acc_m = int(accepted_units or 0), float(accepted_minutes or 0)
    std_u, std_m = int(standing_units or 0), float(standing_minutes or 0)
    return {
        "units": acc_u, "minutes": acc_m,
        "standing_units": std_u, "standing_minutes": std_m,
        # over on EITHER axis is an overage: a batch that fits the clock but not the unit
        # count was still accepted past its standing appetite, and the trace must say so.
        "over_appetite": acc_u > std_u or acc_m > std_m,
    }


def record_appetite(repo_root: Path | str, *, accepted_units: int, accepted_minutes: float,
                    standing_units: int, standing_minutes: float) -> dict:
    """Write the run's appetite record (see `appetite_record`): the accepted appetite and the
    standing one it was measured against, so the DECISION to accept an over-appetite batch survives
    the decision itself - the record must never read as though the batch fitted when it was made to
    fit by raising the ceiling."""
    return update(repo_root, appetite=appetite_record(
        accepted_units=accepted_units, accepted_minutes=accepted_minutes,
        standing_units=standing_units, standing_minutes=standing_minutes))


def appetite_overage(repo_root: Path | str) -> dict | None:
    """The recorded over-appetite as `{units, minutes}` of `{accepted, standing}`, or None for an
    ordinary run. None is the signal that DISTINGUISHES an accepted overage from a run that simply
    fitted - without it the field would mean nothing (US0359 AC3). Only the axes actually over are
    flagged `over`, so a reader sees WHICH ceiling was raised."""
    ap = read(repo_root).get("appetite") or {}
    if not ap.get("over_appetite"):
        return None
    acc_u, std_u = int(ap.get("units") or 0), int(ap.get("standing_units") or 0)
    acc_m, std_m = float(ap.get("minutes") or 0), float(ap.get("standing_minutes") or 0)
    return {
        "units": {"accepted": acc_u, "standing": std_u, "over": acc_u > std_u},
        "minutes": {"accepted": acc_m, "standing": std_m, "over": acc_m > std_m},
    }


def review_rounds(repo_root: Path | str) -> list[dict]:
    """Every recorded close-review round, in order. A malformed entry is skipped rather than
    raising: the rounds are a cost and convergence signal, and one bad record must not make
    the run unreadable to the close that needs the rest."""
    rounds = read(repo_root).get(REVIEW_ROUNDS) or []
    if not isinstance(rounds, list):
        return []
    return [r for r in rounds if isinstance(r, dict)]


def review_round_count(repo_root: Path | str) -> int:
    """How many close-review rounds this run has recorded. Zero when no run is open - a round
    counted against a run with no identity could not be joined to anything later, so it is
    not counted at all (the review itself is still recorded by the caller)."""
    if not read(repo_root).get("run_id"):
        return 0
    return len(review_rounds(repo_root))


def round_duration(entry: dict) -> int | None:
    """A recorded round's duration in seconds, or None for UNMEASURED.

    None is the honest reading of a round nobody timed, and it must never be folded to 0: the
    overhead ratio computes delivery by subtraction, so a silent zero reports review as having
    cost nothing and inflates the delivered share by exactly the time the review took. The two
    largest sprints in this record spent more wall-clock in review-and-repair than in delivery,
    and the ratio said review was unmeasured while treating it as free."""
    value = entry.get("seconds", UNMEASURED)
    if value is UNMEASURED or value is None:
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    return n if n >= 0 else None


def _elapsed_seconds(started_at: str | None, ended_at: str | None) -> int | None:
    """Seconds between two ISO-8601 stamps, or None when either is absent or unparseable.

    Unparseable is UNMEASURED, never 0 - a stamp the parser cannot read says nothing about how
    long the round took, and answering 0 would be an invented measurement."""
    if not started_at or not ended_at:
        return None
    from datetime import datetime
    try:
        a = datetime.fromisoformat(str(started_at).replace("Z", "+00:00"))
        b = datetime.fromisoformat(str(ended_at).replace("Z", "+00:00"))
    except ValueError:
        return None
    delta = int((b - a).total_seconds())
    return delta if delta >= 0 else None


def record_review_round(repo_root: Path | str, verdict: str, units: list[str] | None = None,
                        reviewer: str = "", tokens: int | None = UNMEASURED,
                        repaired: list[dict] | None = None,
                        started_at: str | None = None, ended_at: str | None = None,
                        seconds: int | None = UNMEASURED) -> dict | None:
    """Append one close-review round to the run. Returns the round recorded, or None when no
    run is open.

    `tokens` distinguishes an unmeasured round (None) from a measured zero, and both are
    preserved as given - see UNMEASURED. `repaired` is the file-and-line surface the round's
    repair touched, which the NEXT round compares its findings against.

    REFUSED, never written silently, when the write would contradict the ledger it is joining:
    a round recorded against a run that already carries `ended_at` (a review accepted against a
    run already closed - BG0261 found one recorded 33 minutes after the run ended), or a reviewer
    label naming a round number other than the index this entry lands at (the tool's numbering and
    the reviewer's must not disagree by one and nothing object)."""
    current = read(repo_root)
    if not current.get("run_id"):
        return None
    index = len(review_rounds(repo_root)) + 1
    if current.get("ended_at"):
        raise ReviewLedgerError(
            f"cannot record a review round against a run that already ended at "
            f"{current['ended_at']!r} - the review would be accepted against a closed run and "
            f"counted after the fact. Record the round before the run is closed, or reopen it")
    label = stated_round_ordinal(reviewer)
    if label is not None and label != index:
        raise ReviewLedgerError(
            f"reviewer label {reviewer!r} names round {label}, but this entry is stored at round "
            f"{index} - the ledger's numbering and the reviewer's must not disagree. Drop the "
            f"number from the label (the index is authoritative) or record it at the right round")
    # A round's DURATION, on the same UNMEASURED discipline as its tokens: an explicit figure
    # wins, else it is derived from a start and an end, else it stays UNMEASURED. Never 0 by
    # default - a zero is a measurement, and inventing one here is what let the overhead ratio
    # report review as free while it was the largest cost in the sprint.
    if seconds is UNMEASURED or seconds is None:
        derived = _elapsed_seconds(started_at, ended_at)
        seconds = UNMEASURED if derived is None else derived
    entry = {
        "round": index,
        "verdict": (verdict or "").upper(),
        "reviewer": reviewer,
        "units": [sdlc_md.norm_id(u) for u in (units or [])],
        "recorded_at": sdlc_md.now_iso8601(),
        "tokens": tokens,
        "repaired": repaired or [],
        "started_at": started_at or None,
        "ended_at": ended_at or None,
        "seconds": seconds,
    }

    def apply(state: dict) -> dict:
        state = state or _blank()
        existing = state.get(REVIEW_ROUNDS)
        state[REVIEW_ROUNDS] = ([r for r in existing if isinstance(r, dict)]
                                if isinstance(existing, list) else []) + [entry]
        return state

    _mutate(repo_root, apply)
    return entry


#: How a multi-clause Sprint Goal is split. A goal is one sentence by convention, and its
#: clauses are what the operator actually wrote as separable commitments. Semicolons and
#: dashes always separate. Commas separate ONLY when the sentence also carries `, and ` - the
#: Oxford-list shape an operator uses to enumerate commitments. Without that marker a comma is
#: ordinary punctuation inside one clause, and splitting on it would shred a single commitment
#: into three nobody made.
# A semicolon needs no space before it (`thing; another` is the usual spelling); a dash
# does, or a hyphenated word would separate two clauses out of one.
_CLAUSE_HARD = re.compile(r"\s*;\s+|\s-\s+")
_CLAUSE_LIST = re.compile(r"\s*,\s+(?:and\s+)?")
_OXFORD = re.compile(r",\s+and\s+")


def goal_clauses(goal: str | None) -> list[str]:
    """A Sprint Goal as its clauses, in order. One clause for a single-clause goal.

    A goal reached in two parts of three is a real and common outcome, and collapsing it to one
    word forces the closer to overstate or understate. Splitting is deliberately conservative:
    a goal nobody wrote as separable commitments comes back as ONE clause rather than being
    shredded into commitments its author never made."""
    text = " ".join(str(goal or "").split())
    if not text:
        return []
    head, sep, tail = text.partition(": ")
    body = tail if sep and len(head) < 80 else text
    splitter = _CLAUSE_LIST if _OXFORD.search(body) else _CLAUSE_HARD
    parts = [p.strip(" .;-") for p in splitter.split(body) if p and p.strip(" .;-")]
    return parts if len(parts) > 1 else [text]


#: How many words of a goal reach a filename. Long enough to tell two sprints apart at a
#: glance, short enough that the name stays a name - a 200-character filename is one nothing
#: displays in full and every tool truncates differently.
_NAME_SLUG_WORDS = 8


def sprint_name(run_id: str, goal: str | None = None) -> str:
    """A sprint's display name: `sprint-<run id>-<goal slug>`, or the bare id when no goal.

    The RUN ID stays first and canonical. A goal can be reworded - it routinely is, between the
    plan and the close - and a name that resolved only through its slug would orphan every
    reference to that sprint the moment it changed. The slug is decoration on a stable id, and
    `run_id_from_name` reads the id back out of any spelling.

    A run with NO recorded goal is named by its id alone. Inventing a slug for a goal nobody
    wrote is the same class of error as reporting an unmeasured figure as zero."""
    rid = str(run_id or "").strip()
    if not rid:
        raise ValueError("a sprint name needs a run id - the id is the canonical half")
    words = " ".join(str(goal or "").split()).split(" ")[:_NAME_SLUG_WORDS]
    tail = sdlc_md.slug(" ".join(words))
    return f"sprint-{rid}-{tail}" if tail else f"sprint-{rid}"


_RUN_ID_IN_NAME = re.compile(r"(RUN-[0-9A-Za-z]+)", re.I)


def run_id_from_name(name: str) -> str | None:
    """The run id inside a sprint name, whatever the slug says - or None.

    This is what makes a reworded goal harmless: the slug in an old filename may describe a
    goal nobody uses any more, and the sprint still resolves."""
    m = _RUN_ID_IN_NAME.search(str(name or ""))
    return m.group(1).upper() if m else None


def record_goal_verdict(repo_root: Path | str, verdict: str, note: str = "",
                        clauses: list[dict] | None = None) -> dict:
    """Record the closing review's Sprint Goal verdict beside the goal it judges.

    The round count is DERIVED from the ledger and stamped on the record (`rounds`), never taken
    from the prose. A note that narrates a DIFFERENT count is REFUSED, not silently written: the
    verdict note is the sentence a fresh context reads to learn how many adversarial rounds ran,
    and BG0261 found one saying 'three independent adversarial rounds' while six sat in the
    `review_rounds` key beside it. Derive it from the ledger or do not restate it - the two must
    not disagree. Returns the record written."""
    ledger = review_round_count(repo_root)
    stated = stated_round_count(note)
    if stated is not None and stated != ledger:
        raise ReviewLedgerError(
            f"the goal-verdict note narrates {stated} round(s), but the ledger carries {ledger} "
            f"(len(review_rounds)) - a note may not restate a round count the ledger contradicts. "
            f"Drop the number (the derived `rounds` field carries it) or record the missing rounds")
    record = {"verdict": verdict, "note": note, "rounds": ledger}
    if clauses:
        # Per-clause verdicts, recorded BESIDE the single word rather than instead of it: the
        # one-word verdict is what every existing reader consumes, and a clause list is what
        # makes `partial` mean something specific rather than "not entirely".
        record["clauses"] = clauses
    update(repo_root, sprint_goal_verdict=record)
    return record


def delegated_records(state: dict) -> list[dict]:
    """Every SUPPLIED delegated total on a run record, in the order they landed.

    Pure over a state dict, because the close already holds one and re-reading the file would
    let the two answers drift. A malformed entry is skipped rather than raising: these are cost
    records, and one bad entry must not make the run unreadable to the close that needs the
    rest. A record whose `tokens` is not a positive number carries no total and is not one.
    """
    recs = (state or {}).get(DELEGATED)
    if not isinstance(recs, list):
        return []
    out = []
    for r in recs:
        if not isinstance(r, dict):
            continue
        t = r.get("tokens")
        if isinstance(t, bool) or not isinstance(t, int) or t <= 0:
            continue
        out.append(r)
    return out


def delegated_total(state: dict) -> int:
    """The supplied delegated spend on a run, or 0 when none was supplied.

    0 here means NOTHING WAS SUPPLIED, which is not the same fact as no delegation happening -
    which is exactly why the figure it is added to is published as a lower bound rather than as
    the run's cost."""
    return sum(r["tokens"] for r in delegated_records(state))


def record_delegated_tokens(repo_root: Path | str, tokens, agent: str = "",
                            note: str = "") -> dict | None:
    """Record one delegated agent's SUPPLIED token total against the open run.

    Returns the record, or None when no run is open - a spend counted against a run with no
    identity could not be joined to anything later, so it is not counted at all.

    A non-positive or non-integer total RAISES rather than being recorded: the whole point of
    this record is that it is a real figure an agent reported, and a 0 recorded here would be
    added into a published total as though a delegated agent had cost nothing.
    """
    if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens <= 0:
        raise ValueError(f"a delegated token total must be a positive integer, got {tokens!r} - "
                         f"an absent or zero total is not a measurement of a delegated agent")
    if not read(repo_root).get("run_id"):
        return None
    entry = {"tokens": tokens, "agent": agent, "note": note,
             "provenance": SUPPLIED, "recorded_at": sdlc_md.now_iso8601()}

    def apply(state: dict) -> dict:
        state = state or _blank()
        existing = state.get(DELEGATED)
        state[DELEGATED] = ([r for r in existing if isinstance(r, dict)]
                            if isinstance(existing, list) else []) + [entry]
        return state

    _mutate(repo_root, apply)
    return entry


def record_ceiling_override(repo_root: Path | str, at_round: int, ceiling: int) -> dict | None:
    """Record that the operator explicitly bought a round past the ceiling. Returns the
    override, or None with no run open. The record is what makes the override auditable: a
    ceiling silently exceeded is the same as no ceiling."""
    if not read(repo_root).get("run_id"):
        return None
    entry = {"at_round": at_round, "ceiling": ceiling}

    def apply(state: dict) -> dict:
        state = state or _blank()
        existing = state.get(CEILING_OVERRIDES)
        state[CEILING_OVERRIDES] = ([o for o in existing if isinstance(o, dict)]
                                    if isinstance(existing, list) else []) + [entry]
        return state

    _mutate(repo_root, apply)
    return entry


def _check_outcome(outcome: str) -> None:
    if outcome not in OUTCOMES:
        raise ValueError(f"unknown run outcome {outcome!r} - expected one of "
                         f"{', '.join(OUTCOMES)}")


def reopen_run(repo_root: Path | str, reason: str) -> dict:
    """Reopen the closed run so evidence that belongs to it can still be recorded.

    This exists because the close's own refusal named it and it did not exist. The documented
    two-invocation flow is: close once to produce the sign-off brief, then close again with
    `--apply-signoff`. But the first invocation SEALS the run, and the sprint-level review the
    sign-off needs cannot be recorded against a sealed run - the refusal says so and offers
    "or reopen it", a remedy with no implementation. The sequence the close documents therefore
    could not be completed.

    Deliberately NOT a general undo:

    * The reason is mandatory and recorded on the state, so a reopen is always attributable.
      A run that can be silently reopened is a run whose closure means nothing.
    * The archived record written at close is left ALONE. It is the evidence of what was
      claimed at that moment, and rewriting history to match a later correction is the
      failure this whole project is built to refuse.
    * The outcome and end time are cleared, so nothing reads a reopened run as still closed,
      and `reopened` records that it happened.
    """
    if not (reason or "").strip():
        raise ValueError("reopen needs a reason - an unattributable reopen makes every close "
                         "provisional")

    def apply(state: dict) -> dict:
        state = state or _blank()
        if not state.get("run_id"):
            raise ValueError("no run to reopen")
        if state.get("outcome") == RUNNING:
            raise ValueError(f"{state['run_id']} is already open - nothing to reopen")
        history = list(state.get("reopened") or [])
        history.append({"at": sdlc_md.now_iso8601(),
                        "from_outcome": state.get("outcome"),
                        "was_ended_at": state.get("ended_at"),
                        "reason": reason.strip()})
        state["reopened"] = history
        state["outcome"] = RUNNING
        state["ended_at"] = None
        return state

    return _mutate(repo_root, apply)


def close_run(repo_root: Path | str, outcome: str, handoff: str | None = None) -> dict:
    """Close the run with its outcome (and the handoff that documents it). Idempotent - a
    second close re-stamps the outcome rather than raising. Every field an earlier caller
    added survives, and a run nobody opened closes onto a blank record rather than a
    fabricated one."""
    _check_outcome(outcome)
    if outcome == RUNNING:
        raise ValueError(f"{RUNNING!r} is not a close outcome - expected one of "
                         f"{', '.join(CLOSED)}")

    def apply(state: dict) -> dict:
        state = state or _blank()
        state["outcome"] = outcome
        state["ended_at"] = sdlc_md.now_iso8601()
        if handoff is not None:
            state["handoff"] = handoff
        return state

    state = _mutate(repo_root, apply)
    # The record is final here, so keep it: the next `open_run` overwrites the live file, and
    # a closed run that only ever existed there is a sprint whose evidence expires.
    archive(repo_root, state)
    return state
