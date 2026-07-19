#!/usr/bin/env python3
"""Estimate the cost of an adversarial `audit` run BEFORE it fans out, and record what it cost.

`/sdlc-studio audit` is a multi-agent fan-out (per-lens finders, loop-until-dry, then an N-of-M
refute panel over every candidate). A real run measured 7 lenses -> 57 candidates -> 192 agents,
~6.9M tokens, ~29 min. That is a lot to spend without a heads-up, so the audit presents this
estimate and confirms above a threshold before it starts.

The estimate is an ORDER-OF-MAGNITUDE guide, not a promise: the finder count depends on how many
loop-until-dry rounds each lens needs, and the refute count on how many candidates the finders
surface - both unknown until the run.

THE MEASUREMENT LOOP
--------------------
Seeds calibrated to one reference run drift, and nothing here could tell you they had. So the
estimator closes the loop the sizing doctrine asks of every other forecast: record the forecast,
record the actual, recalibrate from the evidence.

  `record`  appends a finished run - its scope, the estimate it was given, and its measured
            actuals - to a COMMITTED evidence ledger.
  `run`     estimates. When the ledger holds usable runs the seeds come from their MEDIANS;
            when it is empty or unreadable the shipped constants stand in. Either way the
            output NAMES which of the two it used, so a number is never mistaken for
            a measurement it is not.

The ledger sits beside the other committed evidence (`sdlc-studio/retros/evidence/`), not in
`.local/`: an observation of a run that already happened cannot be regenerated, and evidence the
team cannot read on a fresh clone is not evidence. It is sharded by UTC day so two people
recording on different days merge cleanly.

Pure stdlib. `run` is read-only; `record` writes only its own ledger shard.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# Calibrated to the measured reference run (7 lenses, 57 candidates, 192 agents, 6.9M tokens,
# ~29 min). These are ESTIMATE seeds, not measurements of the run you are about to make. They
# are the FALLBACK: once the ledger holds a usable run, the medians take over.
CANDIDATES_PER_LENS = 8      # 57 / 7 ~ 8
TOKENS_PER_AGENT = 36_000    # 6.9M / 192 ~ 36k
CONCURRENCY = 12             # agents in flight at once (the workflow cap is min(16, cores-2))
AGENT_SECONDS = 130          # wall seconds per agent, effective (192 / 12 waves x 130s ~ 29 min)

# A run at or above either of these is "large" - the audit confirms before starting one. Calibrated
# so a genuinely small scoped audit runs WITHOUT ceremony: a single lens at the defaults is ~28
# agents / ~1M tokens (small); two-plus lenses cross the agent bar (~55) and are confirmed. The
# token bar catches a run that stays under the agent count but is heavy per agent.
LARGE_AGENTS = 50
LARGE_TOKENS = 2_000_000

# The committed evidence dir, shared with the run telemetry it is the audit's counterpart to.
EVIDENCE = Path("sdlc-studio") / "retros" / "evidence"
LEDGER_PREFIX = "audit-cost"

#: What `record` captures. `actual_minutes` and `notes` are optional and are written as null
#: when absent rather than filled with a plausible number.
LEDGER_FIELDS = ("date", "lenses", "rounds", "votes", "estimated_agents", "estimated_tokens",
                 "actual_agents", "actual_tokens", "actual_minutes", "notes")


# ---------------------------------------------------------------------------
# The evidence ledger
# ---------------------------------------------------------------------------

def ledger_path(repo_root: Path | str, shard: str | None = None) -> Path:
    """The ledger shard a row recorded now is appended to. Public: an operator needs to be able
    to name the file their measurement landed in."""
    return Path(repo_root) / EVIDENCE / f"{LEDGER_PREFIX}-{shard or sdlc_md.now_date()}.jsonl"


def _shards(repo_root: Path | str) -> list[Path]:
    """Every shard the ledger is made of, oldest first. Name order is chronological."""
    d = Path(repo_root) / EVIDENCE
    return sorted(d.glob(f"{LEDGER_PREFIX}-*.jsonl")) if d.is_dir() else []


def read_ledger(repo_root: Path | str) -> list[dict]:
    """Every recorded run across the shards, oldest first. A malformed line is skipped rather
    than fatal - one corrupt line must not cost the whole evidence base."""
    out: list[dict] = []
    for p in _shards(repo_root):
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


def record(repo_root: Path | str, fields: dict) -> dict:
    """Append one finished run to the ledger and return the row written.

    Append-only: earlier rows are never rewritten. A measurement is taken once, so it is
    recorded once and left alone."""
    row = {k: fields.get(k) for k in LEDGER_FIELDS}
    row["date"] = row["date"] or sdlc_md.now_date()
    path = ledger_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def _measurements(row: dict) -> tuple[float, float] | None:
    """`(candidates_per_lens, tokens_per_agent)` measured by one recorded run, or None when the
    row cannot yield both.

    The candidate count is not recorded directly, so it is recovered by INVERTING the estimator's
    own model - agents = lenses x rounds + candidates x votes + 1 - which is what makes the
    recalibrated seed reproduce the agent count actually observed. A row whose numbers do not
    invert (no lenses, or fewer agents than its finders alone would need) is dropped whole rather
    than half-used: both medians then rest on the same set of runs."""
    try:
        lenses = int(row.get("lenses") or 0)
        rounds = max(1, int(row.get("rounds") or 1))
        votes = max(1, int(row.get("votes") or 1))
        agents = int(row.get("actual_agents") or 0)
        tokens = int(row.get("actual_tokens") or 0)
    except (TypeError, ValueError):
        return None
    if lenses <= 0 or agents <= 0 or tokens <= 0:
        return None
    refuters = agents - lenses * rounds - 1
    if refuters <= 0:
        return None
    return (refuters / votes) / lenses, tokens / agents


def measured_basis(repo_root: Path | str) -> dict:
    """The seeds an estimate should use, and where they came from.

    `{source, runs, candidates_per_lens, tokens_per_agent}`. `source` is `ledger` when at least
    one recorded run inverts cleanly, otherwise `constants` - and `runs` is the number of runs
    behind the medians, which is 0 exactly when the constants are standing in."""
    pairs = [m for row in read_ledger(repo_root) if (m := _measurements(row)) is not None]
    if not pairs:
        return {"source": "constants", "runs": 0,
                "candidates_per_lens": CANDIDATES_PER_LENS,
                "tokens_per_agent": TOKENS_PER_AGENT}
    return {
        "source": "ledger", "runs": len(pairs),
        "candidates_per_lens": round(statistics.median(p[0] for p in pairs)),
        "tokens_per_agent": round(statistics.median(p[1] for p in pairs)),
    }


# ---------------------------------------------------------------------------
# The estimate
# ---------------------------------------------------------------------------

def estimate(lenses: int, *, rounds: int = 3, votes: int = 3,
             candidates_per_lens: int | None = None,
             tokens_per_agent: int | None = None,
             basis: dict | None = None,
             concurrency: int = CONCURRENCY, agent_seconds: int = AGENT_SECONDS) -> dict:
    """Estimate {agents, tokens, wall_minutes, large, breakdown, assumptions, basis} for a run.

    Model: finders = lenses x rounds (the loop-until-dry upper bound); candidates = lenses x
    candidates_per_lens; refuters = candidates x votes; +1 merge/synthesis agent. Tokens = agents x
    tokens_per_agent. Wall = ceil(agents / concurrency) waves x agent_seconds. `large` is true at or
    above the LARGE_* thresholds - the signal the audit gates its confirmation on.

    The two calibrated seeds resolve in precedence order: an explicit argument, then `basis`
    (what `measured_basis` read off the ledger), then the shipped constants. No `basis` means the
    constants, so a library caller's estimate never depends on the working directory."""
    basis = basis or {"source": "constants", "runs": 0}
    if candidates_per_lens is None:
        candidates_per_lens = basis.get("candidates_per_lens", CANDIDATES_PER_LENS)
    if tokens_per_agent is None:
        tokens_per_agent = basis.get("tokens_per_agent", TOKENS_PER_AGENT)
    lenses = max(0, int(lenses))
    finders = lenses * max(1, rounds)
    candidates = lenses * max(0, candidates_per_lens)
    refuters = candidates * max(1, votes)
    merge = 1 if lenses else 0
    agents = finders + refuters + merge
    tokens = agents * tokens_per_agent
    waves = math.ceil(agents / max(1, concurrency)) if agents else 0
    wall_minutes = round(waves * agent_seconds / 60)
    return {
        "agents": agents, "tokens": tokens, "wall_minutes": wall_minutes,
        "large": agents >= LARGE_AGENTS or tokens >= LARGE_TOKENS,
        "breakdown": {"finders": finders, "candidates_est": candidates,
                      "refuters": refuters, "merge": merge},
        "assumptions": {"lenses": lenses, "rounds": rounds, "votes": votes,
                        "candidates_per_lens": candidates_per_lens,
                        "tokens_per_agent": tokens_per_agent, "concurrency": concurrency,
                        "agent_seconds": agent_seconds},
        "basis": {"source": basis.get("source", "constants"), "runs": basis.get("runs", 0)},
    }


def basis_line(est: dict) -> str:
    """One sentence naming what the estimate was calibrated from. An estimate that does not say
    whether its seeds were measured or assumed invites the assumption being read as a fact."""
    b = est.get("basis") or {}
    if b.get("source") == "ledger":
        runs = b.get("runs", 0)
        return (f"calibrated from the median of {runs} recorded run"
                f"{'' if runs == 1 else 's'} in the evidence ledger")
    return "calibrated from the shipped constants - the evidence ledger holds no usable run yet"


def render(est: dict) -> str:
    b = est["breakdown"]
    scale = "LARGE - confirm before running" if est["large"] else "small - runs without ceremony"
    return (
        f"audit cost estimate ({scale}):\n"
        f"  ~{est['agents']} agents  ·  ~{est['tokens']/1e6:.1f}M tokens  ·  ~{est['wall_minutes']} min\n"
        f"  breakdown: {b['finders']} finders + ~{b['refuters']} refuters "
        f"(~{b['candidates_est']} candidates x {est['assumptions']['votes']} votes) + {b['merge']} merge\n"
        f"  basis: {basis_line(est)}\n"
        f"  estimate only - order of magnitude; the real finder and candidate counts are known "
        f"only once it runs. Record the actuals afterwards with `audit_cost.py record`."
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
    est = estimate(args.lenses, rounds=args.rounds, votes=args.votes,
                   candidates_per_lens=args.candidates_per_lens,
                   tokens_per_agent=args.tokens_per_agent,
                   basis=measured_basis(args.root))
    print(json.dumps(est, indent=2) if args.format == "json" else render(est))
    return 0


def cmd_record(args: argparse.Namespace) -> int:
    row = record(args.root, {
        "lenses": args.lenses, "rounds": args.rounds, "votes": args.votes,
        "estimated_agents": args.est_agents, "estimated_tokens": args.est_tokens,
        "actual_agents": args.actual_agents, "actual_tokens": args.actual_tokens,
        "actual_minutes": args.actual_minutes, "notes": args.notes,
    })
    if args.format == "json":
        print(json.dumps(row))
    else:
        print(f"recorded {row['actual_agents']} agents / {row['actual_tokens']} tokens "
              f"against an estimate of {row['estimated_agents']} / {row['estimated_tokens']} "
              f"-> {ledger_path(args.root).name}")
    return 0


#: The subcommands. Anything else in first position is treated as a bare `run`, so the
#: documented `audit_cost.py --lenses 7` invocation keeps working unchanged.
SUBCOMMANDS = ("run", "record")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="audit_cost", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="estimate a run before it fans out")
    r.add_argument("--lenses", type=int, required=True, help="number of audit lenses in the run")
    r.add_argument("--rounds", type=int, default=3, help="loop-until-dry round cap per lens")
    r.add_argument("--votes", type=int, default=3, help="refute-panel votes per candidate (N of M)")
    r.add_argument("--candidates-per-lens", type=int, default=None,
                   help="expected candidates each lens surfaces (overrides the measured basis)")
    r.add_argument("--tokens-per-agent", type=int, default=None,
                   help="expected tokens per agent (overrides the measured basis)")
    r.add_argument("--root", default=".", help="project root holding the evidence ledger")
    r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_run)

    c = sub.add_parser("record", help="append a finished run's actuals to the evidence ledger")
    c.add_argument("--lenses", type=int, required=True, help="lenses the run covered")
    c.add_argument("--rounds", type=int, default=3, help="loop-until-dry round cap it used")
    c.add_argument("--votes", type=int, default=3, help="refute-panel votes per candidate")
    c.add_argument("--est-agents", type=int, required=True, help="agents the estimate predicted")
    c.add_argument("--est-tokens", type=int, required=True, help="tokens the estimate predicted")
    c.add_argument("--actual-agents", type=int, required=True, help="agents the run really used")
    c.add_argument("--actual-tokens", type=int, required=True, help="tokens the run really cost")
    c.add_argument("--actual-minutes", type=int, default=None, help="wall minutes the run took")
    c.add_argument("--notes", default=None,
                   help="what made this run unusual (an outage, rework, a rerun)")
    c.add_argument("--root", default=".", help="project root holding the evidence ledger")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_record)

    sdlc_md.add_global_root(p)  # --root valid before or after the verb, as family-wide
    return p


def _with_default_verb(argv: list[str]) -> list[str]:
    """`audit_cost.py --lenses 7` means `run --lenses 7`.

    The docs, the help catalogue and the audit profiles all call the estimator with bare flags
    and no verb, so the verb is inferred when argv names none. It is inferred from whether ANY
    token is a verb, not just the first, because a global option can legitimately precede it
    (`--root X run --lenses 7`)."""
    if not argv or any(tok in SUBCOMMANDS for tok in argv) or "-h" in argv or "--help" in argv:
        return argv
    return ["run", *argv]


def main(argv: list[str] | None = None) -> int:
    argv = _with_default_verb(list(sys.argv[1:] if argv is None else argv))
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
