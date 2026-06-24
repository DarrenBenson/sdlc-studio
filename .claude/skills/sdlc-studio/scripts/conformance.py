#!/usr/bin/env python3
"""SDLC Studio lifecycle-conformance check.

Asserts each unit (story) passed through the required lifecycle stages -
decomposed (an Epic link), specified (at least one AC), verifiable (a `Verify:`
line), and for Done stories: verified (AC marked `Verified: yes/manual`),
reconciled (no index drift, via reconcile), and critiqued (a committed
independent-critic APPROVE, via critic.py). Exits non-zero on any non-conformant
unit, so the sprint loop cannot mark a unit Done with a stage silently
skipped - including skipping the critic. Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import reconcile  # noqa: E402  (sibling scripts; scripts dir is on sys.path)
import critic  # noqa: E402
import doc_coverage  # noqa: E402  (the `documented` stage)

_PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
# A bullet's fillable value: strip the leading marker (checkbox, **Label:**) -> group(1).
_BULLET_VAL = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?(?:\*\*[^*]+\*\*:?\s*)?(.*)$")


def _real(value: str | None) -> bool:
    """True when a line's fillable value has substance beyond a {{placeholder}}:
    a scaffold whose AC/Verify slots are still `{{...}}` is not yet specified. Punctuation
    or markdown left after stripping the placeholder is not substance (so `{{x}}.` is not
    real - this keeps conformance consistent with validate, which flags that line)."""
    residue = _PLACEHOLDER.sub("", value or "")
    return re.sub(r"[\s.,;:!?*_`>~\-]+", "", residue) != ""


def detect_conformance(repo_root: Path | str) -> dict:
    """Per-story lifecycle conformance.

    Returns {"units": [{id, type, status, stages, conformant, missing}],
    "summary": {total, conformant, nonconformant}}. A story is conformant when
    every required stage for its status is present.
    """
    root = Path(repo_root)
    vocab = sdlc_md.status_vocab("story", root)
    # Adoption cutoff: a project that turns the gate on partway can set
    # `conformance.adopt_after: US0360` in .config.yaml so units before that id are
    # exempt (reported, not judged) - the discipline applies forward, not retroactively.
    cutoff = sdlc_md.project_override(root, "conformance.adopt_after")
    cutoff_num = sdlc_md.id_number(str(cutoff)) if cutoff is not None else None
    # A story is "reconciled" only if its index row matches and exists: a drifted
    # status (status-mismatch) or a story absent from the index (missing-row) both
    # fail it, and a missing index file fails every story.
    _drift = reconcile.detect_type("story", root)["drift"]
    _no_index = any(d["kind"] == "missing-index" for d in _drift)
    drift_ids = {sdlc_md.norm_id(d["id"]) for d in _drift
                 if d.get("id") and d["kind"] in ("status-mismatch", "missing-row")}
    # Repo-global doc-coverage - the `documented` stage, like `reconciled`.
    _doc_ok = doc_coverage.check(root)["ok"]
    units: list[dict] = []
    ok = 0
    for path in sdlc_md.artifact_files("story", root):
        text = path.read_text(encoding="utf-8")
        rid = sdlc_md.extract_record_id(path.stem) or path.stem
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab) or "Unknown"
        decomposed = sdlc_md.extract_field(text, "Epic") is not None
        has_ac = has_verify = False
        in_ac = False
        verified_states: list[str] = []
        for line in text.splitlines():
            if line.startswith("## "):
                in_ac = "acceptance criteria" in line.lower()
                continue
            hm = sdlc_md.AC_HEADING_RE.match(line)
            bm_ac = sdlc_md.AC_BULLET_RE.match(line)
            if hm and _real(hm.group(2)):
                has_ac = True
            elif bm_ac and _real(bm_ac.group(2)):
                has_ac = True
            # A populated Acceptance Criteria section counts as "specified" even when the
            # ACs are prose bullets without an ACn id (house templates) - but a line whose
            # fillable value is only a {{placeholder}} does not count.
            elif in_ac and line.strip() and not line.startswith("#"):
                bm = _BULLET_VAL.match(line)
                if _real(bm.group(1) if bm else line):
                    has_ac = True
            vm = sdlc_md.VERIFY_RE.match(line)
            if vm and _real(vm.group(2)):
                has_verify = True
            m = sdlc_md.VERIFIED_RE.match(line)
            if m:
                verified_states.append(m.group(2).lower())
        verified = reconciled = critiqued = documented = None
        if status == "Done":
            verified = bool(verified_states) and all(v in ("yes", "manual") for v in verified_states)
            reconciled = (not _no_index) and sdlc_md.norm_id(rid) not in drift_ids
            verdict = critic.verdict_for(root, rid)
            critiqued = bool(verdict) and verdict["verdict"] == critic.APPROVE
            documented = _doc_ok
        stages = {
            "decomposed": decomposed,
            "specified": has_ac,
            "verifiable": has_verify,
            "verified": verified,
            "reconciled": reconciled,
            "critiqued": critiqued,
            "documented": documented,
        }
        required = ["decomposed", "specified", "verifiable"]
        if status == "Done":
            required += ["verified", "reconciled", "critiqued", "documented"]
        rid_num = sdlc_md.id_number(rid)
        exempt = cutoff_num is not None and rid_num is not None and rid_num < cutoff_num
        missing = [] if exempt else [s for s in required if not stages[s]]
        conformant = not missing
        ok += int(conformant and not exempt)
        units.append({
            "id": rid,
            "type": "story",
            "status": status,
            "stages": stages,
            "exempt": exempt,
            "conformant": conformant,
            "missing": missing,
        })
    units.sort(key=lambda u: u["id"])
    total = len(units)
    exempt_n = sum(1 for u in units if u["exempt"])
    nonconformant = sum(1 for u in units if not u["conformant"])
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "units": units,
        "summary": {"total": total, "conformant": ok,
                    "nonconformant": nonconformant, "exempt": exempt_n},
    }


def cmd_check(args: argparse.Namespace) -> int:
    """Run the conformance check; exit non-zero if any unit is non-conformant."""
    result = detect_conformance(args.root)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        s = result["summary"]
        extra = f", {s['exempt']} exempt (pre-adoption)" if s.get("exempt") else ""
        print(f"conformance: {s['conformant']}/{s['total']} conformant, {s['nonconformant']} not{extra}")
        tally: dict[str, int] = {}
        for u in result["units"]:
            if not u["conformant"]:
                print(f"  {u['id']} ({u['status']}): missing {', '.join(u['missing'])}")
                for m in u["missing"]:
                    tally[m] = tally.get(m, 0) + 1
        hints = sdlc_md.remediation_lines("conformance", tally)
        if hints:
            print("Guidance:")
            for h in hints:
                print(f"  - {h}")
            judged = s["total"] - s.get("exempt", 0)
            bulk = sorted(k for k, c in tally.items() if judged >= 3 and c >= 0.8 * judged)
            if bulk:
                print(f"  note: most units miss {', '.join(bulk)} - likely an unadopted "
                      "discipline or template shape, not per-unit drift; adopt it or scope conformance.")
    return 1 if result["summary"]["nonconformant"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio lifecycle-conformance check.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Check each story passed the required lifecycle stages.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
