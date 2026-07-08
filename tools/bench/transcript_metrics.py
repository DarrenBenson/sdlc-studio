#!/usr/bin/env python3
"""Automatic token/wall-time capture for benchmark runs (repo-only).

Parses an orchestrator's per-run usage output into the small JSON shape
`runner.py record --metrics-json` consumes: {"tokens": int|null, "wall_time_s": float|null}.
Closes the CR0178 disclosure gap where tokens/wall-time were operator-typed: the figures
now come from a machine-written file, and `record` stamps `metrics_source: parsed`.

Accepted inputs (auto-detected):
  - a JSON object with usage fields - e.g. Claude Code headless `claude -p --output-format
    json` output (`{"usage": {...}, "duration_ms": ...}`), or an Agent-tool result blob
    (`{"subagent_tokens": ..., "duration_ms": ...}`)
  - a JSONL transcript whose lines carry cumulative `usage` objects (last one wins)

Usage:
    python3 tools/bench/transcript_metrics.py --input <run-output.json> [--output <metrics.json>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _tokens_from_usage(usage: dict) -> int | None:
    """Total tokens from a usage object, whichever spelling it uses."""
    if not isinstance(usage, dict):
        return None
    if isinstance(usage.get("total_tokens"), (int, float)):
        return int(usage["total_tokens"])
    parts = [usage.get(k) for k in ("input_tokens", "output_tokens",
                                     "cache_creation_input_tokens", "cache_read_input_tokens")]
    nums = [int(p) for p in parts if isinstance(p, (int, float))]
    return sum(nums) if nums else None


def extract(obj: dict) -> dict:
    """{tokens, wall_time_s} from one run-output object; missing fields are None."""
    tokens = None
    for key in ("subagent_tokens", "total_tokens", "tokens"):
        if isinstance(obj.get(key), (int, float)):
            tokens = int(obj[key])
            break
    if tokens is None:
        tokens = _tokens_from_usage(obj.get("usage") or {})
    wall = None
    for key, scale in (("duration_ms", 1000.0), ("wall_time_s", 1.0), ("duration_s", 1.0)):
        if isinstance(obj.get(key), (int, float)):
            wall = round(obj[key] / scale, 1)
            break
    return {"tokens": tokens, "wall_time_s": wall}


def parse_file(path: Path) -> dict:
    """Parse a run-output file (JSON object, or JSONL where the last usage-carrying
    line wins). Raises ValueError when nothing usable is found - a silent
    {null, null} would let an empty file masquerade as a measured run."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"{path}: empty input")
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            m = extract(obj)
            if m["tokens"] is None and m["wall_time_s"] is None:
                raise ValueError(f"{path}: no usage/duration fields recognised")
            return m
    except json.JSONDecodeError:
        pass
    # JSONL: walk the lines, last extractable record wins
    best = {"tokens": None, "wall_time_s": None}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if isinstance(rec, dict):
            m = extract(rec)
            if m["tokens"] is not None:
                best["tokens"] = m["tokens"]
            if m["wall_time_s"] is not None:
                best["wall_time_s"] = m["wall_time_s"]
    if best["tokens"] is None and best["wall_time_s"] is None:
        raise ValueError(f"{path}: no usage/duration fields recognised in any line")
    return best


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Parse run output into record --metrics-json input.")
    p.add_argument("--input", required=True, help="run-output JSON / JSONL file")
    p.add_argument("--output", help="write the metrics JSON here (default: stdout)")
    args = p.parse_args(argv)
    metrics = parse_file(Path(args.input))
    payload = json.dumps(metrics, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
