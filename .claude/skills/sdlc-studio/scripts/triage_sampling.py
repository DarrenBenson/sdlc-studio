#!/usr/bin/env python3
"""SDLC Studio triage sampling policy + triage-quality metrics (schema v3, EP0014).

Once triage becomes a sampled human audit rather than a gate (US0065/US0066), two questions
follow: *which* triaged findings should a human look at, and *how good* is the triage over time.

- **Sampling policy** (`sample`): deterministic given a seed. Every Critical is sampled, every
  raiser/triager severity disagreement is sampled, and a configured fraction
  (`triage.sample_rate`) of the rest - selected by a stable hash of `(seed, id)` so the same
  batch and seed always pick the same subset (reproducible over a fixture).
- **Triage-quality metrics** (`metrics`): computed from the records, never hand-counted. The
  false-positive rate (a finding triaged into the workflow but later closed invalid) and severity
  inflation (raiser severity vs the triager's) come straight from the artefacts' `Severity` /
  `Triage-severity` / status fields. Sampled-but-unreviewed findings surface as standing pending
  audit, not a one-time prompt.

Pure stdlib. Dormant unless the project is schema v3 (the metrics simply find no triaged findings
on a v2 project, since `Triage-severity` is a v3 field).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import config  # noqa: E402

_CRITICAL = {"critical", "p1"}
# Severity/priority rank for inflation deltas (higher = more severe); unknown tokens are skipped.
_RANK = {"critical": 3, "high": 2, "medium": 1, "low": 0, "p1": 3, "p2": 2, "p3": 1, "p4": 0}
# The invalid-close state per finding type: a finding triaged as real, then closed as not-real.
_INVALID_CLOSE = {"bug": {"Won't Fix"}, "cr": {"Rejected"}, "rfc": {"Withdrawn"}}
_SAMPLED = Path("sdlc-studio") / ".local" / "triage-sampled.json"


def _cfg(root, key: str, default):
    try:
        return config.get(root, f"triage.{key}", default)
    except Exception:  # noqa: BLE001 - config must never break the policy
        return default


def sample_rate(root) -> float:
    try:
        return float(_cfg(root, "sample_rate", 0.20))
    except (TypeError, ValueError):
        return 0.20


def always_sample(root) -> set[str]:
    raw = _cfg(root, "always_sample", ["Critical", "disagreement"])
    if not isinstance(raw, list):
        return {"critical", "disagreement"}
    return {str(t).strip().lower() for t in raw}


def _is_critical(severity: str) -> bool:
    return (severity or "").strip().lower() in _CRITICAL


def _is_disagreement(severity: str, triage_severity: str) -> bool:
    t = (triage_severity or "").strip().lower()
    return bool(t) and t != (severity or "").strip().lower()


def _hash(seed: int, ident: str) -> str:
    return hashlib.sha256(f"{seed}:{ident}".encode("utf-8")).hexdigest()


def sample(items: list[dict], root: Path | str = ".", seed: int = 0) -> list[dict]:
    """The subset a human should audit. `items` are triaged findings carrying `id`, `severity`
    (raiser) and `triage_severity` (triager). Always-sampled tokens (`triage.always_sample`) take
    every Critical and every raiser/triager disagreement; a stable hash of `(seed, id)` then
    picks `round(sample_rate * n)` of the remaining pool, so the choice is reproducible."""
    always = always_sample(root)
    rate = sample_rate(root)
    picked: list[dict] = []
    pool: list[dict] = []
    for it in items:
        sev, tsev = it.get("severity", ""), it.get("triage_severity", "")
        if ("critical" in always and _is_critical(sev)) or \
                ("disagreement" in always and _is_disagreement(sev, tsev)):
            picked.append(it)
        else:
            pool.append(it)
    k = round(len(pool) * rate)
    if k > 0 and pool:
        # Rank pool positions by the stable hash and keep the lowest k; selecting by INDEX (not
        # object identity) is immune to a duplicated item and preserves input order in the output.
        ranked = sorted(range(len(pool)), key=lambda i: _hash(seed, str(pool[i].get("id", ""))))
        keep = set(ranked[:k])
        picked.extend(pool[i] for i in range(len(pool)) if i in keep)
    return picked


def _sampled_path(root) -> Path:
    return Path(root) / _SAMPLED


def record_sample(root, ids: list[str]) -> None:
    """Persist the ids selected for audit (gitignored `.local/triage-sampled.json`), so
    sampled-but-unreviewed findings can surface as standing pending audit in `metrics`."""
    p = _sampled_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sorted({sdlc_md.norm_id(i) for i in ids})), encoding="utf-8")


def _sampled_ids(root) -> set[str]:
    p = _sampled_path(root)
    if not p.exists():
        return set()
    try:
        return {sdlc_md.norm_id(i) for i in json.loads(p.read_text(encoding="utf-8"))}
    except Exception:  # noqa: BLE001 - a corrupt sample record must not break metrics
        return set()


def collect_triaged(root) -> list[dict]:
    """Every finding carrying a `Triage-severity` (i.e. triaged under v3), with its raiser
    severity (Severity, or Priority for a CR), triager severity, canonical status and id."""
    root = Path(root)
    out: list[dict] = []
    for type_ in sdlc_md.FINDING_TYPES:
        vocab = sdlc_md.status_vocab(type_, root)
        for p in sdlc_md.artifact_files(type_, root):
            text = p.read_text(encoding="utf-8")
            tsev = sdlc_md.extract_field(text, "Triage-severity")
            if not tsev:
                continue
            raiser = sdlc_md.extract_field(text, "Severity") or \
                sdlc_md.extract_field(text, "Priority") or ""
            out.append({
                "id": sdlc_md.extract_record_id(p.stem) or p.stem, "type": type_,
                "severity": raiser, "triage_severity": tsev,
                "status": sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)})
    return out


def metrics(root) -> dict:
    """Triage-quality metrics from the records (no hand-counting): the false-positive rate
    (triaged then closed invalid), severity inflation (triager vs raiser), and how many sampled
    findings still await audit."""
    items = collect_triaged(root)
    terminal = [i for i in items if i["status"] in sdlc_md.terminal_statuses(i["type"])]
    invalid = [i for i in terminal if i["status"] in _INVALID_CLOSE.get(i["type"], set())]
    fpr = round(len(invalid) / len(terminal), 4) if terminal else 0.0
    inflated = deflated = 0
    for i in items:
        r = _RANK.get((i["severity"] or "").strip().lower())
        t = _RANK.get((i["triage_severity"] or "").strip().lower())
        if r is None or t is None:
            continue
        if t > r:
            inflated += 1
        elif t < r:
            deflated += 1
    sampled = _sampled_ids(root)
    open_ids = {sdlc_md.norm_id(i["id"]) for i in items
                if i["status"] not in sdlc_md.terminal_statuses(i["type"])}
    pending = sorted(sampled & open_ids)
    return {
        "triaged": len(items), "terminal": len(terminal),
        "false_positive_rate": fpr, "invalid_closed": len(invalid),
        "severity_inflation": {"inflated": inflated, "deflated": deflated},
        "sampled_pending_audit": pending,
    }
