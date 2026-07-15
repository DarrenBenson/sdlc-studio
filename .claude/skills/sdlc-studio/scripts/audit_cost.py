#!/usr/bin/env python3
"""Estimate the cost of an adversarial `audit` run BEFORE it fans out.

`/sdlc-studio audit` is a multi-agent fan-out (per-lens finders, loop-until-dry, then an N-of-M
refute panel over every candidate). A real run measured 7 lenses -> 57 candidates -> 192 agents,
~6.9M tokens, ~29 min. That is a lot to spend without a heads-up, so the audit presents this
estimate and confirms above a threshold before it starts.

The estimate is an ORDER-OF-MAGNITUDE guide, not a promise: the finder count depends on how many
loop-until-dry rounds each lens needs, and the refute count on how many candidates the finders
surface - both unknown until the run. The defaults are calibrated to the measured reference run
(~8 candidates/lens, ~36k tokens/agent), and every input is overridable. Pure stdlib; read-only.
"""
from __future__ import annotations

import argparse
import json
import math
import sys

# Calibrated to the measured reference run (7 lenses, 57 candidates, 192 agents, 6.9M tokens,
# ~29 min). These are ESTIMATE seeds, not measurements of the run you are about to make.
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


def estimate(lenses: int, *, rounds: int = 3, votes: int = 3,
             candidates_per_lens: int = CANDIDATES_PER_LENS,
             tokens_per_agent: int = TOKENS_PER_AGENT,
             concurrency: int = CONCURRENCY, agent_seconds: int = AGENT_SECONDS) -> dict:
    """Estimate {agents, tokens, wall_minutes, large, breakdown, assumptions} for an audit run.

    Model: finders = lenses x rounds (the loop-until-dry upper bound); candidates = lenses x
    candidates_per_lens; refuters = candidates x votes; +1 merge/synthesis agent. Tokens = agents x
    tokens_per_agent. Wall = ceil(agents / concurrency) waves x agent_seconds. `large` is true at or
    above the LARGE_* thresholds - the signal the audit gates its confirmation on."""
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
    }


def render(est: dict) -> str:
    b = est["breakdown"]
    scale = "LARGE - confirm before running" if est["large"] else "small - runs without ceremony"
    return (
        f"audit cost estimate ({scale}):\n"
        f"  ~{est['agents']} agents  ·  ~{est['tokens']/1e6:.1f}M tokens  ·  ~{est['wall_minutes']} min\n"
        f"  breakdown: {b['finders']} finders + ~{b['refuters']} refuters "
        f"(~{b['candidates_est']} candidates x {est['assumptions']['votes']} votes) + {b['merge']} merge\n"
        f"  estimate only - order of magnitude, calibrated to the measured reference run; "
        f"the real finder/candidate counts are known only once it runs."
    )


def cmd_run(args: argparse.Namespace) -> int:
    est = estimate(args.lenses, rounds=args.rounds, votes=args.votes,
                   candidates_per_lens=args.candidates_per_lens)
    if args.format == "json":
        print(json.dumps(est, indent=2))
    else:
        print(render(est))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="audit_cost", description=__doc__)
    p.add_argument("--lenses", type=int, required=True, help="number of audit lenses in the run")
    p.add_argument("--rounds", type=int, default=3, help="loop-until-dry round cap per lens")
    p.add_argument("--votes", type=int, default=3, help="refute-panel votes per candidate (N of M)")
    p.add_argument("--candidates-per-lens", type=int, default=CANDIDATES_PER_LENS,
                   help="expected candidates each lens surfaces (estimate seed)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
