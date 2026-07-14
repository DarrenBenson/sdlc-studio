#!/usr/bin/env python3
"""Run telemetry recorder: the project's measured evidence, and the forecasts it judges.

Two logs, both COMMITTED, both under `sdlc-studio/retros/evidence/`:

  actuals-*.jsonl    what a unit actually cost - one record per unit close.
  forecasts-*.jsonl  what the planner PREDICTED it would cost, recorded when it predicted it.

**No upload, no network.** Tokens are recorded only when the caller passes them (a script
cannot read them reliably). The loop wires `record` on each unit close.

WHY THEY ARE COMMITTED, AND NOT IN `.local/`
--------------------------------------------
Both logs are PROJECT EVIDENCE, not user-local runtime state. `.local/` is for state you can
delete and lose nothing: run-state, worklists, caches, the repo map, the allocation lock - all
of it regenerable by re-running a tool. These two are the opposite kind of thing. They are
OBSERVATIONS of runs that already happened, and no tool can regenerate them: re-run the sprint
and you get different numbers, not the same ones.

Kept in `.local/`, they were on one machine. On a fresh clone, on CI, or for anybody else,
every forecast was absent, every unit read UNFORECAST, and the entire estimate-vs-actual
history read as no-evidence - so the estimator could not be falsified by anyone but the machine
that ran the sprint. The rule is the one `retro.py` already applies to `VELOCITY.md`: evidence
the team cannot read on a fresh clone is not evidence. `VELOCITY.md` is the committed SUMMARY;
these are the committed per-unit rows underneath it, and they live beside it for that reason.

SHARDING, AND THE MERGE STORY
-----------------------------
A single append-only JSONL is a bad shape for a file two people can both append to. So each log
is sharded, one file per UTC day (`actuals-2026-07-14.jsonl`); readers concatenate the shards in
name order, which is chronological, so the ordering both readers depend on is preserved.

  Two sprints closed on different days, on different branches -> DIFFERENT FILES. Git merges
  them cleanly and no record can be lost.

  Two sprints closed on the same day, on different branches -> the same file, appended at the
  end by both sides -> a MERGE CONFLICT, with both sides' records visible between the markers,
  which a human resolves by keeping both. That is the intended outcome, and it is why the log is
  deliberately NOT given a union merge driver: union would silently interleave, and interleaving
  can flip which forecast for a unit is FIRST - quietly rewriting a prediction.

The shard key is the day, not the sprint's retro id, because the retro does not exist yet when
these records are written: the forecast is recorded at PLAN time and the actuals during the run,
while the retro id is minted at close. Keying by it would mean rewriting the log afterwards -
editing, with hindsight, the very record that exists to be un-editable.

Nothing here is rolled. A bounded roll drops the OLDEST records first, which on a committed
evidence log means deleting history out of git; the day shard bounds the file instead.

Subcommands:
  record    Append one run-outcome record.
  forecast  Append one plan-time forecast record (what the planner predicted, and with what).
  show      Print the recorded records (count + the JSON); `--forecasts` for the forecast log.
  migrate   Move a pre-existing `.local/` log into the committed evidence dir, without loss.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # resolve sibling imports (critic)
from lib import sdlc_md  # noqa: E402

# The committed evidence dir, beside the retros and the velocity history it is the rows of.
EVIDENCE = Path("sdlc-studio") / "retros" / "evidence"
ACTUALS_PREFIX = "actuals"
FORECASTS_PREFIX = "forecasts"

# Where the logs used to live: user-local, gitignored, one machine. Still READ, so a project
# that upgrades the skill does not lose the evidence it already has; `migrate` moves it. The
# legacy log is read FIRST, which is also its correct chronological place - it predates every
# shard.
LEGACY_ACTUALS = Path("sdlc-studio") / ".local" / "telemetry.jsonl"
LEGACY_FORECASTS = Path("sdlc-studio") / ".local" / "forecasts.jsonl"

# The shard a migrated legacy log lands in. Named to sort BEFORE any dated shard, because
# everything in it happened before the migration.
MIGRATED_SHARD = "0000-migrated"

# The captured fields. Optional ones are omitted when not supplied. The tier_* fields
# (routing) record which model tier was recommended vs actually delivered a unit,
# so per-tier escape/escalation rates become measurable - the routing calibration loop.
FIELDS = ("id", "type", "iterations", "wall_time_s", "stages", "critic_verdict",
          "complexity", "churn", "reopened", "tokens",
          "tier_recommended", "tier_delivered", "model", "escalated")


def shard_id() -> str:
    """The shard a record written now belongs to: the UTC date. Known at write time, always,
    with no dependency on run state; sorts chronologically; partitions the log the way sprints
    partition time."""
    return sdlc_md.now_date()


def _shard_path(repo_root: Path | str, prefix: str, shard: str | None = None) -> Path:
    return Path(repo_root) / EVIDENCE / f"{prefix}-{shard or shard_id()}.jsonl"


def _shards(repo_root: Path | str, prefix: str, legacy: Path) -> list[Path]:
    """Every file the log is made of, OLDEST FIRST: the un-migrated legacy `.local/` log (when a
    project still has one), then the tracked shards in name order.

    The order is load-bearing on both sides - the actuals reader takes the last non-null value
    per field, and the forecast reader takes the FIRST record for a unit - so it is defined by
    the filename, never by directory iteration order."""
    out: list[Path] = []
    old = Path(repo_root) / legacy
    if old.is_file():
        out.append(old)
    d = Path(repo_root) / EVIDENCE
    if d.is_dir():
        out.extend(sorted(d.glob(f"{prefix}-*.jsonl")))
    return out


def _read_jsonl(paths: list[Path]) -> list[dict]:
    """Every record across the shards. A malformed line is skipped, never fatal - one corrupt
    line must not cost the whole evidence base."""
    out: list[dict] = []
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, dict):
                out.append(rec)
    return out


def _append(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


def actuals_path(repo_root: Path | str, shard: str | None = None) -> Path:
    """The actuals shard a record written now is appended to. Public: the loop, the tests and
    an operator all need to be able to name the file the evidence lands in."""
    return _shard_path(repo_root, ACTUALS_PREFIX, shard)


def forecasts_path(repo_root: Path | str, shard: str | None = None) -> Path:
    """The forecast shard a record written now is appended to."""
    return _shard_path(repo_root, FORECASTS_PREFIX, shard)


_path = actuals_path


# ---------------------------------------------------------------------------
# The delivered model, ON THE ARTEFACT.
# ---------------------------------------------------------------------------
# The model was captured here and went nowhere a reader would ever look. You could not open a
# bug and see what built it; the committed history had no model column; and while the log lived
# in `.local/` a fresh clone lost the attribution entirely. It matters three times over: which
# model delivered a change is audit information, a cost-per-unit figure means nothing without
# knowing which model paid it, and a benchmark that compares models needs exactly this field.
#
# So the close STAMPS it on the unit. Idempotent (a re-record updates the line rather than adding
# a second), last-model-wins (the model that delivered the final state is the one that delivered
# it), and best-effort: a stamp that cannot land must never cost the measurement.
DELIVERED_BY_RE = re.compile(r"(?im)^([^\S\n]*>[^\S\n]*)\*\*Delivered-by:\*\*.*$")


def stamp_delivery(repo_root: Path | str, unit_id: str, model: str) -> Path | None:
    """Record on the ARTEFACT the model that delivered it. Returns the path, or None when there
    is no artefact to stamp.

    Writes into the header metadata blockquote (the contiguous `>` run under the H1) and nowhere
    else, so a prose blockquote or a table in the body cannot be corrupted."""
    found = sdlc_md.find_by_id(repo_root, unit_id)
    if not found:
        return None
    path = found[0]
    text = path.read_text(encoding="utf-8")
    line = f"> **Delivered-by:** {str(model).strip()}"
    if DELIVERED_BY_RE.search(text):
        new = DELIVERED_BY_RE.sub(lambda m: f"{m.group(1)}**Delivered-by:** {model}", text, count=1)
    else:
        lines = text.splitlines()
        h1 = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith("# ")), None)
        if h1 is None:
            return None
        i = h1 + 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i < len(lines) and lines[i].lstrip().startswith(">"):
            last = i
            while last + 1 < len(lines) and lines[last + 1].lstrip().startswith(">"):
                last += 1
            lines.insert(last + 1, line)
        else:  # no header metadata block - open one directly under the H1
            lines[h1 + 1:h1 + 1] = ["", line]
        new = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    if new != text:
        sdlc_md.atomic_write(path, new)
    return path


def record(repo_root: Path | str, fields: dict) -> dict:
    """Append one record (only the recognised, non-None fields), and stamp the delivering model
    on the unit itself. Best-effort: a write failure is swallowed (telemetry must never break
    the loop)."""
    rec = {k: fields[k] for k in FIELDS if fields.get(k) is not None}
    try:
        _append(_path(repo_root), [rec])
    except Exception as exc:  # noqa: BLE001 - telemetry is advisory; never raise into the loop
        sdlc_md.debug("telemetry.record", exc)
    if rec.get("id") and rec.get("model"):
        try:
            stamp_delivery(repo_root, str(rec["id"]), str(rec["model"]))
        except Exception as exc:  # noqa: BLE001 - a stamp that cannot land never costs the measurement
            sdlc_md.debug("telemetry.stamp_delivery", exc)
    return rec


def record_plan_review(repo_root: Path | str, unit: str, verdict: str,
                       reviewer: str, author: str) -> dict:
    """Append a plan-review outcome event (US0091) so the gate's value is measurable over
    time: how often plan-review runs, its verdict mix, and that it was independent. Best-effort
    (a write failure never breaks the recording path). Carries an `event: "plan-review"` marker
    AND a `phase` field; `summarise` reads it as a distinct block, never as a unit-close type.
    Independence uses the SAME notion as the gate (`critic.is_independent`), so the `-` sentinel
    and empty author read as not-independent - the metric cannot over-report independence. The
    whole thing is best-effort: neither the independence read nor the write raises into the loop."""
    try:
        import critic  # lazy: telemetry is a leaf; critic has no telemetry dep
        independent = critic.is_independent({"author": author, "reviewer": reviewer})
    except Exception:  # noqa: BLE001 - never raise into the recording path; fall back locally
        def _norm(x):
            x = (x or "").strip().casefold()
            return "" if x == "-" else x
        a, r = _norm(author), _norm(reviewer)
        independent = bool(a) and r != a
    rec = {"event": "plan-review", "phase": "plan-review", "id": str(unit),
           "verdict": (verdict or "").upper(), "reviewer": reviewer, "author": author,
           "independent": independent}
    try:
        _append(_path(repo_root), [rec])
    except Exception as exc:  # noqa: BLE001 - telemetry is advisory; never raise into the loop
        sdlc_md.debug("telemetry.record", exc)
    return rec


def read_all(repo_root: Path | str) -> list[dict]:
    """Every actuals record across the shards, oldest first. Malformed lines are skipped (a
    corrupt line never breaks a read)."""
    return _read_jsonl(_shards(repo_root, ACTUALS_PREFIX, LEGACY_ACTUALS))


#: The per-unit fields an actual is made of. `type` and `model` are context, not
#: measurements; the rest are what a run actually cost.
ACTUAL_FIELDS = ("type", "model", "tokens", "wall_time_s", "iterations", "complexity",
                 "churn", "critic_verdict")


def latest_actuals(records: list[dict]) -> dict[str, dict]:
    """Per-unit measured actuals, keyed by normalised id: the LAST non-null value seen for
    each field.

    Last-non-null, not last-record. The loop appends a second, bare record on close
    (`{"id": "BG0126", "type": "bug"}`), so taking the last record wholesale would erase a
    measurement that was genuinely taken. A field no record ever carried stays ABSENT - it is
    never defaulted to 0, because an unmeasured unit must be reportable as unmeasured rather
    than as a unit that cost nothing.

    Event records (plan-review) are not unit closes and are excluded.
    """
    out: dict[str, dict] = {}
    for rec in records:
        if rec.get("event"):
            continue
        rid = sdlc_md.norm_id(str(rec.get("id") or "").strip())
        if not rid:
            continue
        bucket = out.setdefault(rid, {})
        for field in ACTUAL_FIELDS:
            val = rec.get(field)
            if val is not None:
                bucket[field] = val
    return out


def actuals(repo_root: Path | str) -> dict[str, dict]:
    """`latest_actuals` over the project's telemetry log. The single read the retro's
    estimate-vs-actual report goes through."""
    return latest_actuals(read_all(repo_root))


# ---------------------------------------------------------------------------
# The forecast log: what the planner PREDICTED, recorded when it predicted it.
# ---------------------------------------------------------------------------
# The actuals above are one side of the estimate-vs-actual ratio. This is the other side, and
# it has to be a RECORD for exactly the same reason they do.
#
# An estimate re-derived at judgement time, from the constants it is meant to be judging, is
# not a prediction. Recalibrate and every past sprint is retroactively deemed to have forecast
# something else, so the ratio drifts toward 1.0x and the loop can never falsify its own
# estimator. It is not hypothetical: a recorded 5.2x miss was the entire evidence for a
# recalibration, and the recalibration erased it.
#
# It lives NEXT TO the actuals, in the same committed evidence directory, because it is the
# same kind of thing: a per-unit run record, keyed by unit id, written once by the tool that
# observed it. Its own log rather than a record type inside the actuals, so the two can never
# evict or overwrite one another.
#
# FIRST WINS. The reader takes the EARLIEST record for a unit. Re-planning a batch after the
# work is done must not be able to rewrite what was predicted before it started; a later record
# is kept as history and never overrides. Hindsight is not a forecast. That is why the shards
# are read in name order and never merged by a union driver: a reordering silently changes which
# prediction is the one that stands.

#: A forecast record. `tokens` is the number the plan quoted; `seed` is the complexity/effort
#: input it came from; `constants` is the estimator that produced it (so a later reader can
#: tell whether the row was forecast by the constants now in force, or by a different model);
#: `planned_at` is when the plan was made.
#:
#: The ATTRIBUTION of the size call rides here too, and it is recorded at PLAN TIME for the same
#: reason the number is: an `Effort` read off the artefact later may have been revised with
#: hindsight, and a value revised after the outcome is not a prediction.
#:   `estimator`   WHO made the size call ("unattributed" when nobody claimed it - never guessed)
#:   `effort_gate` under what compulsion: `compulsory` (the grooming gate refuses an unsized
#:                 unit) or `voluntary`. A compulsory estimate from someone who does not want to
#:                 estimate is a careless one, and that hazard is only testable if the compulsion
#:                 in force is on the record.
FORECAST_FIELDS = ("id", "tokens", "seed", "seed_source", "complexity", "effort",
                   "estimator", "effort_gate", "constants", "planned_at")


_forecast_path = forecasts_path


def read_forecasts(repo_root: Path | str) -> list[dict]:
    """Every forecast record across the shards, oldest first. A malformed line is skipped,
    never fatal."""
    return [r for r in _read_jsonl(_shards(repo_root, FORECASTS_PREFIX, LEGACY_FORECASTS))
            if r.get("id")]


def forecasts(repo_root: Path | str) -> dict[str, dict]:
    """The plan-time forecast per unit, keyed by normalised id. FIRST record wins - see the
    note above. The single read the retro's estimate-vs-actual report goes through; it never
    recomputes an estimate."""
    out: dict[str, dict] = {}
    for rec in read_forecasts(repo_root):
        rid = sdlc_md.norm_id(str(rec.get("id") or "").strip())
        if rid:
            out.setdefault(rid, rec)
    return out


def record_forecasts(repo_root: Path | str, records: list[dict]) -> dict:
    """Append the plan's per-unit forecasts. Idempotent: a record identical to one already
    held for that unit (same tokens, same constants) is not written twice, so re-planning an
    unchanged batch does not grow the log.

    NOT best-effort, unlike `record`. A telemetry write that fails costs a measurement; a
    forecast write that fails silently would leave the planner announcing a forecast that was
    never recorded, which is the whole defect. The caller is told, and says so.
    """
    have = read_forecasts(repo_root)
    seen = {(sdlc_md.norm_id(str(r.get("id"))), r.get("tokens"),
             json.dumps(r.get("constants"), sort_keys=True)) for r in have}
    fresh: list[dict] = []
    already: list[str] = []
    for rec in records:
        rid = sdlc_md.norm_id(str(rec.get("id") or "").strip())
        if not rid:
            continue
        key = (rid, rec.get("tokens"), json.dumps(rec.get("constants"), sort_keys=True))
        if key in seen:
            already.append(rid)
            continue
        seen.add(key)
        row = {k: rec[k] for k in FORECAST_FIELDS if rec.get(k) is not None}
        row["id"] = rid
        fresh.append(row)
    if fresh:
        _append(_forecast_path(repo_root), fresh)
    return {"path": str(_forecast_path(repo_root)),
            "recorded": [r["id"] for r in fresh], "already": already}


# ---------------------------------------------------------------------------
# Migration: a `.local/` log, moved into the committed evidence dir without loss.
# ---------------------------------------------------------------------------

def migrate(repo_root: Path | str) -> dict:
    """Move any pre-existing `.local/` log into `retros/evidence/`, so evidence recorded before
    the logs were committed reaches the repository instead of dying with the machine.

    Loss-proof by construction, and then CHECKED. When the destination does not exist the file
    is RENAMED - the bytes are not rewritten, so there is nothing to get wrong. When it does,
    the lines absent from the destination are appended, and the source is only unlinked once
    every one of its lines has been verified present. A dropped record here would be
    unrecoverable: these runs cannot be re-measured.
    """
    root = Path(repo_root)
    report: dict = {"moved": [], "skipped": []}
    for legacy, prefix in ((LEGACY_ACTUALS, ACTUALS_PREFIX),
                           (LEGACY_FORECASTS, FORECASTS_PREFIX)):
        src = root / legacy
        if not src.is_file():
            report["skipped"].append(str(legacy))
            continue
        dst = _shard_path(root, prefix, MIGRATED_SHARD)
        dst.parent.mkdir(parents=True, exist_ok=True)
        lines = [ln for ln in src.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not dst.exists():
            src.replace(dst)                      # a rename: the bytes are untouched
        else:
            have = {ln.strip() for ln in dst.read_text(encoding="utf-8").splitlines()}
            missing = [ln for ln in lines if ln.strip() not in have]
            with dst.open("a", encoding="utf-8") as fh:
                for ln in missing:
                    fh.write(ln.rstrip("\n") + "\n")
            landed = {ln.strip() for ln in dst.read_text(encoding="utf-8").splitlines()}
            absent = [ln for ln in lines if ln.strip() not in landed]
            if absent:
                raise RuntimeError(
                    f"refusing to remove {src}: {len(absent)} record(s) did not reach {dst}")
            src.unlink()
        report["moved"].append({"from": str(legacy), "to": str(dst.relative_to(root)),
                                "records": len(lines)})
    return report


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def cmd_record(args: argparse.Namespace) -> int:
    fields = {"id": args.id, "type": args.type, "iterations": _int(args.iterations),
              "wall_time_s": _int(args.wall_time_s), "stages": args.stages,
              "critic_verdict": args.verdict, "complexity": _int(args.complexity),
              "churn": _int(args.churn), "reopened": args.reopened, "tokens": _int(args.tokens),
              "tier_recommended": args.tier_recommended,
              "tier_delivered": args.tier_delivered,
              "model": args.model, "escalated": args.escalated}
    rec = record(args.root, fields)
    print(json.dumps(rec) if args.format == "json" else f"recorded {rec.get('id', '?')}")
    return 0


def summarise(records: list[dict]) -> dict:
    """Per-type aggregates over the raw records: count, mean iterations, mean wall
    time, reopen rate, verdict mix. A field absent from every record of a type is
    None, never a fabricated 0 - the summary reports what was measured.

    Event records (those carrying an `event` key, e.g. plan-review) are NOT unit-close
    records and are excluded from the per-type/per-tier aggregates - pooling them would inflate
    a phantom `unknown` type. Plan-review events are summarised in their own `plan_review` block
    (US0091): count, verdict mix, and the independent-review rate."""
    unit_recs = [r for r in records if not r.get("event")]
    out: dict = {}
    for rec in unit_recs:
        t = rec.get("type") or "unknown"
        b = out.setdefault(t, {"count": 0, "_iters": [], "_wall": [],
                               "_reopened": [], "verdicts": {}})
        b["count"] += 1
        if isinstance(rec.get("iterations"), (int, float)):
            b["_iters"].append(rec["iterations"])
        if isinstance(rec.get("wall_time_s"), (int, float)):
            b["_wall"].append(rec["wall_time_s"])
        if rec.get("reopened") is not None:
            b["_reopened"].append(str(rec["reopened"]).strip().lower() in ("yes", "true", "1"))
        v = rec.get("critic_verdict")
        if v:
            b["verdicts"][v] = b["verdicts"].get(v, 0) + 1
    for b in out.values():
        iters, wall, reop = b.pop("_iters"), b.pop("_wall"), b.pop("_reopened")
        b["mean_iterations"] = round(sum(iters) / len(iters), 2) if iters else None
        b["mean_wall_time_s"] = round(sum(wall) / len(wall), 2) if wall else None
        b["reopen_rate"] = round(sum(reop) / len(reop), 3) if reop else None
    # Per-delivered-tier grouping (verdict mix + reopen rate) - the routing
    # calibration signal. Emitted only when some record actually carries a tier, so a
    # non-routed project's summary is byte-identical to before.
    tiers: dict = {}
    for rec in unit_recs:
        t = rec.get("tier_delivered")
        if not t:
            continue
        b = tiers.setdefault(t, {"count": 0, "_reopened": [], "_escalated": [],
                                  "verdicts": {}})
        b["count"] += 1
        if rec.get("reopened") is not None:
            b["_reopened"].append(str(rec["reopened"]).strip().lower() in ("yes", "true", "1"))
        if rec.get("escalated") is not None:
            b["_escalated"].append(str(rec["escalated"]).strip().lower() in ("yes", "true", "1"))
        v = rec.get("critic_verdict")
        if v:
            b["verdicts"][v] = b["verdicts"].get(v, 0) + 1
    if tiers:
        for b in tiers.values():
            reop, esc = b.pop("_reopened"), b.pop("_escalated")
            b["reopen_rate"] = round(sum(reop) / len(reop), 3) if reop else None
            b["escalation_rate"] = round(sum(esc) / len(esc), 3) if esc else None
        out["by_tier"] = tiers
    # Plan-review events (their own block, US0091): how often the gate ran, its verdict mix,
    # and the independent-review rate - so the gate's value is measurable.
    pr_events = [r for r in records if r.get("event") == "plan-review"]
    if pr_events:
        verdicts: dict = {}
        for r in pr_events:
            v = r.get("verdict")
            if v:
                verdicts[v] = verdicts.get(v, 0) + 1
        indep = [bool(r.get("independent")) for r in pr_events]
        out["plan_review"] = {
            "count": len(pr_events), "verdicts": verdicts,
            "independent_rate": round(sum(indep) / len(indep), 3) if indep else None}
    return out


def cmd_forecast(args: argparse.Namespace) -> int:
    """Record ONE plan-time forecast by hand. `sprint plan` records the batch's forecasts
    itself; this exists so a forecast recoverable from the record (an old retro's own
    estimate-vs-actual table) can be restored, and so the log can be inspected."""
    rec = {"id": args.id, "tokens": _int(args.tokens), "seed": _int(args.seed),
           "seed_source": args.seed_source, "effort": args.effort,
           "estimator": args.estimator, "effort_gate": args.effort_gate,
           "planned_at": args.planned_at or sdlc_md.now_iso8601(),
           "constants": {"BASE_TOKEN_BUDGET": _int(args.base),
                         "TOKENS_PER_COGNITIVE": _int(args.per_cognitive)}}
    res = record_forecasts(args.root, [rec])
    if args.format == "json":
        print(json.dumps(res, indent=2))
    elif res["recorded"]:
        print(f"recorded forecast {args.id} ({rec['tokens']:,} tokens) -> {res['path']}")
    else:
        print(f"forecast {args.id} already recorded, unchanged - the first one stands")
    return 0


def cmd_migrate(args: argparse.Namespace) -> int:
    res = migrate(args.root)
    if args.format == "json":
        print(json.dumps(res, indent=2))
        return 0
    if not res["moved"]:
        print("nothing to migrate - no .local/ evidence log is left behind")
        return 0
    for m in res["moved"]:
        print(f"moved {m['records']} record(s): {m['from']} -> {m['to']}")
    print("the evidence is now under sdlc-studio/retros/evidence/ - git add it, and it will "
          "survive a fresh clone")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    if getattr(args, "forecasts", False):
        recs = read_forecasts(args.root)
        if args.format == "json":
            print(json.dumps(recs, indent=2))
            return 0
        for r in recs:
            c = r.get("constants") or {}
            print(f"  {r['id']:8} est={r.get('tokens', 0):>9,}  seed={r.get('seed')}  "
                  f"base={c.get('BASE_TOKEN_BUDGET')} tpc={c.get('TOKENS_PER_COGNITIVE')}  "
                  f"planned {r.get('planned_at', '-')}")
        print(f"{len(recs)} forecast record(s); the FIRST for a unit is its plan-time forecast")
        return 0
    recs = read_all(args.root)
    if getattr(args, "summary", False):
        s = summarise(recs)
        if args.format == "json":
            print(json.dumps(s, indent=2))
        else:
            by_tier = s.pop("by_tier", None)
            plan_review = s.pop("plan_review", None)
            unit_n = sum(b["count"] for b in s.values())
            print(f"{unit_n} unit record(s), {len(s)} type(s)")
            for t, b in sorted(s.items()):
                verdicts = ", ".join(f"{k}:{n}" for k, n in sorted(b["verdicts"].items())) or "-"
                print(f"  {t:8} count={b['count']} mean_iterations={b['mean_iterations']} "
                      f"mean_wall_time_s={b['mean_wall_time_s']} "
                      f"reopen_rate={b['reopen_rate']} verdicts[{verdicts}]")
            if plan_review:
                verdicts = ", ".join(f"{k}:{n}" for k, n in
                                     sorted(plan_review["verdicts"].items())) or "-"
                print(f"plan-review: count={plan_review['count']} "
                      f"independent_rate={plan_review['independent_rate']} verdicts[{verdicts}]")
            if by_tier:
                print("by tier delivered:")
                for t, b in sorted(by_tier.items()):
                    verdicts = ", ".join(f"{k}:{n}" for k, n in sorted(b["verdicts"].items())) or "-"
                    print(f"  {t:8} count={b['count']} reopen_rate={b['reopen_rate']} "
                          f"escalation_rate={b['escalation_rate']} verdicts[{verdicts}]")
        return 0
    print(json.dumps(recs, indent=2) if args.format == "json" else f"{len(recs)} record(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run telemetry recorder.")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="Append one run-outcome record.")
    r.add_argument("--id"); r.add_argument("--type"); r.add_argument("--iterations")
    r.add_argument("--wall-time-s", dest="wall_time_s"); r.add_argument("--stages")
    r.add_argument("--verdict"); r.add_argument("--complexity"); r.add_argument("--churn")
    r.add_argument("--reopened"); r.add_argument("--tokens")
    r.add_argument("--tier-recommended", dest="tier_recommended")
    r.add_argument("--tier-delivered", dest="tier_delivered")
    r.add_argument("--model"); r.add_argument("--escalated")
    r.add_argument("--root", default="."); r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_record)
    f = sub.add_parser("forecast", help="Record one plan-time token forecast (the estimate side "
                                        "of the ratio; `sprint plan` records a batch's itself).")
    f.add_argument("--id", required=True); f.add_argument("--tokens", required=True)
    f.add_argument("--seed", help="the complexity/effort input the forecast came from")
    f.add_argument("--seed-source", dest="seed_source", default="complexity",
                   choices=("complexity", "effort", "none"))
    f.add_argument("--effort", help="the declared Effort (S/M/L, or U for a declared unknown)")
    f.add_argument("--estimator", help="WHO made the size call (default: unattributed - it is "
                                       "never inferred from whoever filed the unit)")
    f.add_argument("--effort-gate", dest="effort_gate",
                   choices=("compulsory", "voluntary"),
                   help="was the Effort compulsory at filing, or freely given? The coercion "
                        "hazard is only testable if the compulsion is on the record")
    f.add_argument("--base", required=True, help="BASE_TOKEN_BUDGET in force at plan time")
    f.add_argument("--per-cognitive", dest="per_cognitive", required=True,
                   help="TOKENS_PER_COGNITIVE in force at plan time")
    f.add_argument("--planned-at", dest="planned_at", help="when the plan was made (ISO8601)")
    f.add_argument("--root", default=".")
    f.add_argument("--format", choices=("text", "json"), default="text")
    f.set_defaults(func=cmd_forecast)
    s = sub.add_parser("show", help="Print recorded records.")
    s.add_argument("--summary", action="store_true",
                   help="aggregate per type: count, mean iterations/wall-time, reopen rate, verdict mix")
    s.add_argument("--forecasts", action="store_true",
                   help="print the plan-time forecast log instead of the measured actuals")
    s.add_argument("--root", default="."); s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_show)
    m = sub.add_parser("migrate", help="move a pre-existing .local/ evidence log into the "
                                       "committed evidence dir (no loss; verified)")
    m.add_argument("--root", default=".")
    m.add_argument("--format", choices=("text", "json"), default="text")
    m.set_defaults(func=cmd_migrate)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
