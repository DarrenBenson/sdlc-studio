#!/usr/bin/env python3
"""SDLC Studio project-constitution gate.

An optional `sdlc-studio/constitution.md` lets a project declare its inviolable
principles. A principle is either machine-checkable - carrying a `rule:` from the fixed
vocabulary below, which the gate asserts across the artifact graph - or advisory prose
(listed, loaded as a generation constraint, but not gated). Checkable rules MAP onto the
existing deterministic checks (integrity / conformance / validate / reconcile) plus a
small structural vocabulary, so this adds a single consolidated gate, not a new engine.

Enforcement is advisory by default; a project sets `constitution.enforce: true` in
`.config.yaml` to make violations errors (exit non-zero) - the same incremental-adoption
pattern as `require_ac_verification`. Read-only; pure stdlib core.

Subcommand:
  check  Assert the declared checkable principles; report violations.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import integrity  # noqa: E402  (siblings - the gate reuses the existing detectors)
import conformance  # noqa: E402
import validate  # noqa: E402
import reconcile  # noqa: E402


# --- the checkable-rule vocabulary: rule name -> detector(root) -> [violation strings]


def _r_story_requires_epic(root: Path) -> list[str]:
    return [f"{f['id']}: missing {f['field']} link"
            for f in integrity.detect_integrity(root)["findings"]
            if f["kind"] == "missing-required" and f["type"] == "story" and f["field"] == "Epic"]


def _r_links_resolve(root: Path) -> list[str]:
    return [f"{f['id']}.{f['field']} -> {f['ref']} (no such artifact)"
            for f in integrity.detect_integrity(root)["findings"] if f["kind"] == "dangling"]


def _r_ac_requires_verify(root: Path) -> list[str]:
    return [f"{u['id']}: no Verify line"
            for u in conformance.detect_conformance(root)["units"]
            if not u.get("exempt") and u["stages"].get("verifiable") is False]


def _r_story_has_ac(root: Path) -> list[str]:
    return [f"{u['id']}: no acceptance criteria"
            for u in conformance.detect_conformance(root)["units"]
            if not u.get("exempt") and u["stages"].get("specified") is False]


def _r_status_in_vocab(root: Path) -> list[str]:
    out: list[str] = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, root):
            out += [f"{path.name}: {v['message']}"
                    for v in validate.validate_file(path, type_, root) if v["rule"] == "status-vocab"]
    return out


def _r_no_index_drift(root: Path) -> list[str]:
    out: list[str] = []
    for scope in reconcile.DEFAULT_TYPES:
        for d in reconcile.detect_type(scope, root)["drift"]:
            out.append(f"{scope}: {d['kind']} {d.get('id') or ''}".strip())
    return out


RULES = {
    "story-requires-epic": _r_story_requires_epic,
    "links-resolve": _r_links_resolve,
    "ac-requires-verify": _r_ac_requires_verify,
    "story-has-ac": _r_story_has_ac,
    "status-in-vocab": _r_status_in_vocab,
    "no-index-drift": _r_no_index_drift,
}

_PRINCIPLE_RE = re.compile(r"^[-*]\s+\*\*(?P<text>.+?)\*\*")  # top-level bullets only
_RULE_RE = re.compile(r"`rule:\s*(?P<rule>[a-z0-9-]+)`", re.I)  # backticked, so prose "rule:" is not matched


def constitution_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / "sdlc-studio" / "constitution.md"


def parse_constitution(repo_root: Path | str) -> list[dict]:
    """Principles declared in constitution.md: {text, rule|None} per list item."""
    path = constitution_path(repo_root)
    if not path.exists():
        return []
    principles = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _PRINCIPLE_RE.match(line)
        if not m:
            continue
        r = _RULE_RE.search(line)
        principles.append({"text": m.group("text").strip(), "rule": r.group("rule") if r else None})
    return principles


def check_constitution(repo_root: Path | str) -> dict:
    """Assert each checkable principle. Returns the report; `ok` is False only when a
    gated principle is violated."""
    root = Path(repo_root)
    result: dict = {"exists": constitution_path(root).exists(), "enforced": False,
                    "gated": [], "advisory": [], "unknown_rules": [], "violations": [], "ok": True}
    if not result["exists"]:
        return result
    result["enforced"] = bool(sdlc_md.project_override(root, "constitution.enforce", False))
    for p in parse_constitution(root):
        if p["rule"] is None:
            result["advisory"].append(p["text"])
        elif p["rule"] not in RULES:
            result["unknown_rules"].append(p["rule"])
        else:
            result["gated"].append(p["rule"])
            items = RULES[p["rule"]](root)
            if items:
                result["violations"].append({"principle": p["text"], "rule": p["rule"], "items": items})
    result["ok"] = not result["violations"]
    return result


def cmd_check(args: argparse.Namespace) -> int:
    res = check_constitution(args.root)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    elif not res["exists"]:
        print("constitution: no sdlc-studio/constitution.md (nothing to check)")
    else:
        n = sum(len(v["items"]) for v in res["violations"])
        mode = "ENFORCED" if res["enforced"] else "advisory"
        print(f"constitution [{mode}]: {len(res['gated'])} gated, {len(res['advisory'])} advisory, "
              f"{len(res['violations'])} principle(s) violated ({n} item(s))")
        for v in res["violations"]:
            print(f"  ✗ {v['principle']} ({v['rule']})")
            for it in v["items"][:args.limit]:
                print(f"      - {it}")
        for u in res["unknown_rules"]:
            print(f"  ? unknown rule '{u}' - not one of: {', '.join(sorted(RULES))}")
    # advisory by default: only fail the run when the project opted into enforcement
    return 1 if (res["enforced"] and not res["ok"]) else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Project-constitution principle gate.")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Assert declared checkable principles.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.add_argument("--limit", type=int, default=10, help="Max violating items to print per principle")
    c.set_defaults(func=cmd_check)
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
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
