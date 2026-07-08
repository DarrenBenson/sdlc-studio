#!/usr/bin/env python3
"""SDLC Studio difficulty-aware model-tier routing.

Deterministically estimate a work unit's difficulty from signals already on disk
(blast-radius cognitive complexity + churn-weighted risk via complexity.py, file scope,
unresolved-path novelty, AC count, story points) and recommend an abstract model tier
(tiny/small/medium/large/xlarge) that the project maps to its own model identifiers in
`.config.yaml` `routing.models`. **Advisory only - no gate reads a tier**, and the skill
never calls a model API: model ids are opaque strings the orchestrating agent passes to
its own worker-spawn mechanism, so routing stays tool-neutral.

Missing-signal doctrine: a subscore whose inputs did not resolve defaults to 0.5 (never
0 - unknown difficulty is never treated as minimal) and is listed in `missing`; two or
more missing signals drop confidence to low, which bumps the picked tier UP one step (a
too-small model risks quality; a too-large one only cost). Sparse model maps degrade
UPWARD: an undeclared tier resolves to the nearest declared larger tier, never a smaller
one; above the largest declared tier, the largest is used.

Subcommands:
  estimate   Difficulty score/band + signals for one unit.
  pick       Tier + resolved model after policy floors (--role author|critic).
  escalate   The next declared tier up from --tier (the failure-escalation stepper).
  tiers      The resolved tier->model map after degradation (operator debugging).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import complexity  # noqa: E402  (sibling - blast-radius code signals)
import config  # noqa: E402  (sibling - .config.yaml access)

TIERS = ("tiny", "small", "medium", "large", "xlarge")
BANDS = ("trivial", "low", "medium", "high", "extreme")
BAND_TIER = dict(zip(BANDS, TIERS))
# Subscore weights (sum to 1.0). Spec size and code complexity dominate; risk and
# novelty temper. Calibrate from per-tier telemetry once it accumulates.
WEIGHTS = {"code": 0.25, "risk": 0.15, "scope": 0.20, "spec": 0.25, "novel": 0.15}
DEFAULT_THRESHOLDS = {"tiny": 20, "small": 40, "medium": 60, "large": 80}
DEFAULT_FLOOR = {"bug": "small", "security": "medium"}
MISSING_DEFAULT = 0.5   # unknown difficulty is never minimal
SCOPE_FULL = 5          # files touched at/above this = max scope subscore
# Extensions that mark a unit as touching CODE (vs doc/config) for the critic floor.
CODE_EXTS = (".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb", ".sh",
             ".c", ".cc", ".cpp", ".cs")


def _routing_config(root: Path) -> dict:
    return config.get(root, "routing", None) or {}


def _kind_of(unit_path: Path) -> str:
    """bug / cr / story, from the artifact's id prefix (falls back to its directory)."""
    stem = unit_path.stem.upper()
    if stem.startswith("BG"):
        return "bug"
    if stem.startswith("CR"):
        return "cr"
    return "story"


def estimate(repo_root: Path | str, unit_path: Path | str) -> dict:
    """Deterministic difficulty estimate for one unit. Pure read; raises only on an
    unreadable unit file (callers in the planner catch and degrade)."""
    root = Path(repo_root)
    unit_path = Path(unit_path)
    text = unit_path.read_text(encoding="utf-8")
    cfg = config.load_config(root)

    cognitive_high = (cfg.get("complexity") or {}).get("cognitive_high", 15)
    sizing = ((cfg.get("story_quality") or {}).get("sizing") or {})
    max_ac = sizing.get("max_ac", 10)
    max_points = sizing.get("max_points", 13)

    declared = sdlc_md.affects_files(text)
    resolved = [str(r) for p in declared if (r := sdlc_md.resolve_affects(root, p))]
    new_files = len(declared) - len(resolved)
    ac_count = sdlc_md.count_acs(text)
    points_raw = sdlc_md.extract_field(text, "Story Points")
    try:
        story_points = int(str(points_raw).strip().split()[0]) if points_raw else None
    except (ValueError, IndexError):
        story_points = None

    max_cognitive = risk_score = None
    if resolved:
        try:
            a = complexity.assess(root, resolved)
            max_cognitive, risk_score = a["max_cognitive"], a["risk_score"]
        except Exception:  # noqa: BLE001 - degrade to missing, never break the estimate
            pass

    subscores: dict[str, float] = {}
    missing: list[str] = []

    def sub(name: str, value: float | None) -> None:
        if value is None:
            subscores[name] = MISSING_DEFAULT
            missing.append(name)
        else:
            subscores[name] = round(min(max(value, 0.0), 1.0), 3)

    sub("code", min(max_cognitive / cognitive_high, 2.0) / 2.0
        if max_cognitive is not None else None)
    sub("risk", min(risk_score, 2.0) / 2.0 if risk_score is not None else None)
    sub("scope", min(len(declared) / SCOPE_FULL, 1.0) if declared else None)
    if story_points is not None:
        sub("spec", min(story_points / max_points, 1.0))
    elif ac_count:
        sub("spec", min(ac_count / max_ac, 1.0))
    else:
        sub("spec", None)
    sub("novel", new_files / max(len(declared), 1) if declared else None)

    score = round(100 * sum(WEIGHTS[k] * subscores[k] for k in WEIGHTS))
    band, _tier = band_for(score, _routing_config(root))
    confidence = "high" if not missing else ("medium" if len(missing) == 1 else "low")
    return {
        "id": sdlc_md.extract_record_id(unit_path.stem) or unit_path.stem,
        "difficulty_score": score,
        "difficulty_band": band,
        "confidence": confidence,
        "missing": missing,
        "signals": {"max_cognitive": max_cognitive, "risk_score": risk_score,
                     "files_affected": len(declared), "new_files": new_files,
                     "ac_count": ac_count, "story_points": story_points},
        "subscores": subscores,
    }


def band_for(score: int, routing: dict) -> tuple[str, str]:
    """(band, default tier) for a 0-100 difficulty score, using the project's
    configured cutpoints (each threshold is the score at which the NEXT band starts)."""
    th = {**DEFAULT_THRESHOLDS, **(routing.get("thresholds") or {})}
    if score < th["tiny"]:
        return "trivial", "tiny"
    if score < th["small"]:
        return "low", "small"
    if score < th["medium"]:
        return "medium", "medium"
    if score < th["large"]:
        return "high", "large"
    return "extreme", "xlarge"


def resolve_tier(name: str, models: dict) -> tuple[str, str | None]:
    """Resolve an abstract tier against a (possibly sparse) model map, degrading
    UPWARD only. Empty map: the abstract name with model None - the recommendation
    stays useful as prose."""
    if not models:
        return name, None
    idx = TIERS.index(name)
    for t in TIERS[idx:]:
        if t in models:
            return t, models[t]
    declared = [t for t in TIERS if t in models]
    top = declared[-1]
    return top, models[top]


def _lift(tier: str, floor: str) -> str:
    return TIERS[max(TIERS.index(tier), TIERS.index(floor))]


def _touches_code(root: Path, text: str) -> bool:
    return any(p.endswith(CODE_EXTS) for p in sdlc_md.affects_files(text))


def pick(repo_root: Path | str, unit_path: Path | str, role: str = "author",
         routing: dict | None = None) -> dict:
    """Tier + model recommendation for one unit and role, after policy adjustments:
    kind floors, the high-risk-band security floor, the low-confidence upward bump,
    and the critic rule (never smaller than the author; medium floor for code units;
    +1 under `critic_tier: above`). Advisory - the orchestrator may override, and an
    override is recorded in the decisions ledger (reference-sprint.md)."""
    root = Path(repo_root)
    unit_path = Path(unit_path)
    routing = routing if routing is not None else _routing_config(root)
    est = estimate(root, unit_path)
    text = unit_path.read_text(encoding="utf-8")
    floors = {**DEFAULT_FLOOR, **(routing.get("floor") or {})}
    adjustments: list[str] = []

    _band, tier = band_for(est["difficulty_score"], routing)

    kind = _kind_of(unit_path)
    if kind in floors and TIERS.index(floors[kind]) > TIERS.index(tier):
        tier = _lift(tier, floors[kind])
        adjustments.append(f"floor:{kind}")

    # deterministic security proxy: a high churn-weighted risk band floors at the
    # security floor (the orchestrator may additionally flag security by judgement)
    risk = est["signals"].get("risk_score")
    if risk is not None and risk >= 1.0 and "security" in floors:
        if TIERS.index(floors["security"]) > TIERS.index(tier):
            tier = _lift(tier, floors["security"])
            adjustments.append("floor:risk-band-high")

    if est["confidence"] == "low":
        idx = min(TIERS.index(tier) + 1, len(TIERS) - 1)
        if TIERS[idx] != tier:
            tier = TIERS[idx]
            adjustments.append("confidence:low")

    if role == "critic":
        # the critic is never a smaller tier than the author's picked tier; code
        # units floor the critic at medium; `above` lifts one further step
        if _touches_code(root, text):
            new = _lift(tier, "medium")
            if new != tier:
                tier = new
                adjustments.append("critic:code-medium-floor")
        if (routing.get("critic_tier") or "match") == "above":
            idx = min(TIERS.index(tier) + 1, len(TIERS) - 1)
            if TIERS[idx] != tier:
                tier = TIERS[idx]
                adjustments.append("critic:above")

    resolved, model = resolve_tier(tier, routing.get("models") or {})
    return {"id": est["id"], "role": role,
            "difficulty_score": est["difficulty_score"],
            "difficulty_band": est["difficulty_band"],
            "confidence": est["confidence"],
            "tier": resolved, "model": model, "adjustments": adjustments}


def escalate_tier(tier: str, models: dict) -> dict:
    """The next tier up: the nearest DECLARED tier above the current one (or the next
    abstract tier when no map is declared). `at_max: true` when there is nothing
    above - the loop's signal to stop escalating and block the unit (D2)."""
    idx = TIERS.index(tier)
    candidates = TIERS[idx + 1:]
    if models:
        for t in candidates:
            if t in models:
                return {"tier": t, "model": models[t], "at_max": False}
        return {"tier": tier, "model": models.get(tier), "at_max": True}
    if candidates:
        return {"tier": candidates[0], "model": None, "at_max": False}
    return {"tier": tier, "model": None, "at_max": True}


def cmd_estimate(args: argparse.Namespace) -> int:
    est = estimate(args.root, args.unit)
    if args.format == "json":
        print(json.dumps(est, indent=2))
    else:
        print(f"{est['id']}: difficulty {est['difficulty_score']} ({est['difficulty_band']}) "
              f"confidence={est['confidence']}"
              + (f" missing={','.join(est['missing'])}" if est["missing"] else ""))
    return 0


def cmd_pick(args: argparse.Namespace) -> int:
    p = pick(args.root, args.unit, role=args.role)
    if args.format == "json":
        print(json.dumps(p, indent=2))
    else:
        model = p["model"] or "(no model map)"
        adj = f" [{', '.join(p['adjustments'])}]" if p["adjustments"] else ""
        print(f"{p['id']} ({p['role']}): {p['tier']} -> {model}{adj}")
    return 0


def cmd_escalate(args: argparse.Namespace) -> int:
    models = _routing_config(Path(args.root)).get("models") or {}
    r = escalate_tier(args.tier, models)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        print("already at the largest declared tier" if r["at_max"]
              else f"escalate to {r['tier']}" + (f" -> {r['model']}" if r["model"] else ""))
    return 0


def cmd_tiers(args: argparse.Namespace) -> int:
    models = _routing_config(Path(args.root)).get("models") or {}
    out = {}
    for t in TIERS:
        resolved, model = resolve_tier(t, models)
        out[t] = {"tier": resolved, "model": model}
    if args.format == "json":
        print(json.dumps(out, indent=2))
    else:
        for t, r in out.items():
            print(f"{t:8} -> {r['tier']:8} {r['model'] or '(unmapped)'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Difficulty-aware model-tier routing (advisory).")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--root", default=".")
        sp.add_argument("--format", choices=("text", "json"), default="text")

    e = sub.add_parser("estimate", help="Difficulty score/band + signals for one unit.")
    e.add_argument("--unit", required=True)
    common(e)
    e.set_defaults(func=cmd_estimate)

    pk = sub.add_parser("pick", help="Tier + resolved model after policy floors.")
    pk.add_argument("--unit", required=True)
    pk.add_argument("--role", choices=("author", "critic"), default="author")
    common(pk)
    pk.set_defaults(func=cmd_pick)

    es = sub.add_parser("escalate", help="The next declared tier up from --tier.")
    es.add_argument("--tier", required=True, choices=TIERS)
    common(es)
    es.set_defaults(func=cmd_escalate)

    t = sub.add_parser("tiers", help="The resolved tier->model map after degradation.")
    common(t)
    t.set_defaults(func=cmd_tiers)
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
