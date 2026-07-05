#!/usr/bin/env python3
"""SDLC Studio pipeline status.

Deterministic census of the four pillars (Requirements, Code, Tests, Reviews)
and the next-step hint, so Claude renders the dashboard from JSON instead of
reading every artifact in-context. Live metrics that need to run the project's
own toolchain (lint, type-check, coverage) are deliberately left out - the
script reports artifact-derived state; Claude runs the live checks.

Subcommands:
  pillars  Census of artifacts and reviews as JSON/text (default).
  hint     The single next action from the mechanical priority ladder.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def _print_update_notice(root: str) -> None:
    """Surface a one-line skill-update notice on status/hint - the skill's
    'on first use' check. Fully guarded: a disabled config / offline / any error is
    silent and never affects the status output."""
    try:
        import version_check as vc  # sibling; lazy so status never hard-depends on it
        enabled = bool(sdlc_md.project_override(root, "version_check.enabled", True))
        ttl = sdlc_md.project_override(root, "version_check.ttl_hours", vc.DEFAULT_TTL_HOURS)
        try:
            ttl = float(ttl)
        except (TypeError, ValueError):
            ttl = vc.DEFAULT_TTL_HOURS
        line = vc.notice(vc.check(ttl_hours=ttl, enabled=enabled))
        if line:
            print(line)
    except Exception:  # noqa: BLE001 - the version check must never break status/hint
        pass


def workspace_advisory(repo_root: Path | str) -> str | None:
    """One-line advisory when the sdlc-studio/ workspace carries uncommitted or
    untracked artifact changes - another session may be mid-flight. Informational
    only: names the artifact ids (or files), guesses no authorship, never blocks,
    and degrades silently when git (or a repo) is absent."""
    import subprocess
    root = Path(repo_root)
    try:
        proc = subprocess.run(["git", "status", "--porcelain", "--", "sdlc-studio/"],
                              cwd=root, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None  # not a git repo - nothing to say
    names: list[str] = []
    for line in proc.stdout.splitlines():
        # a rename line reads 'R  old -> new': name BOTH ids (the vanished old
        # one is exactly what another session would go looking for)
        for path in line[3:].split(" -> "):
            path = path.strip().strip('"')
            rec = sdlc_md.extract_record_id(Path(path).stem)
            label = sdlc_md.norm_id(rec) if rec else Path(path).name
            if label and label not in names:
                names.append(label)
    if not names:
        return None
    shown = ", ".join(names[:6]) + (f" (+{len(names) - 6} more)" if len(names) > 6 else "")
    return (f"workspace has uncommitted artifact changes: {shown} - "
            f"another session may be mid-flight; check before filing or planning")


def _config_summary(repo_root: Path) -> dict | None:
    """Representative defaults read from config-defaults.yaml.

    Reads the single source via config.py. Lazy + graceful: if PyYAML is absent
    the census still works (the stdlib core has no hard YAML dependency).
    """
    try:
        import config  # sibling script; scripts dir is on sys.path
        return {
            "schema_version": config.get(repo_root, "schema_version"),
            "coverage": config.get(repo_root, "coverage"),
        }
    except Exception:  # pragma: no cover - PyYAML missing or unreadable config
        return None


def count_by_status(type_: str, repo_root: Path) -> dict:
    """Tally a type's files by canonical Status, plus a total.

    Decorated statuses (`Done (v2.66.0)`) collapse to their vocabulary token
    (`Done`) so the tally and done-percentages are correct; consultations files
    are excluded by `artifact_files`.
    """
    vocab = sdlc_md.status_vocab(type_, repo_root)
    counts: dict[str, int] = {}
    total = 0
    for path in sdlc_md.artifact_files(type_, repo_root):
        total += 1
        raw = sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status") or "Unknown"
        status = sdlc_md.canonical_status(raw, vocab) or "Unknown"
        counts[status] = counts.get(status, 0) + 1
    return {"total": total, "by_status": counts}


def _pct_done(census: dict, done_states: tuple[str, ...]) -> int:
    """Percentage of a census in any of the done_states (0 if empty)."""
    total = census["total"]
    if not total:
        return 0
    done = sum(census["by_status"].get(s, 0) for s in done_states)
    return round(100 * done / total)


def _verify_lane(repo_root: Path) -> dict:
    """The AC-verification lane: from `verify-report.json`, surface stories with
    unverified ACs (`no`/`stale` failures) and the manual-AC count as their own line - so
    env-bound / manual ACs read as 'deferred', not as silent gaps. Empty when no report."""
    report = sdlc_md.read_json(repo_root / "sdlc-studio" / ".local" / "verify-report.json", {})
    stories = report.get("stories", {})
    entries = stories.values() if isinstance(stories, dict) else stories
    unverified = sum(1 for s in entries if s.get("failed", 0) or s.get("stale", 0))
    manual = sum(s.get("manual", 0) for s in entries)
    return {"has_report": bool(stories), "stories_with_unverified_acs": unverified,
            "manual_acs": manual}


def gather(repo_root: Path) -> dict:
    """Compute all four pillars from the artifact files and review state."""
    base = repo_root / "sdlc-studio"
    epics = count_by_status("epic", repo_root)
    stories = count_by_status("story", repo_root)
    test_specs = count_by_status("test-spec", repo_root)
    bugs = count_by_status("bug", repo_root)
    workflows = count_by_status("workflow", repo_root)

    review_state = sdlc_md.read_json(base / ".local" / "review-state.json", {})
    review_files = sdlc_md.walk_glob(base / "reviews", "RV*.md")

    return {
        "generated_at": sdlc_md.now_iso8601(),
        "config": _config_summary(repo_root),
        "requirements": {
            "prd": (base / "prd.md").exists(),
            "personas": (base / "personas.md").exists(),
            "epics": epics,
            "stories": stories,
            "epics_ready_pct": _pct_done(epics, ("Ready", "Approved", "Done")),
            "stories_done_pct": _pct_done(stories, ("Done",)),
        },
        "code": {
            "trd": (base / "trd.md").exists(),
            "note": "run project lint/type-check/coverage live; not derivable from files",
        },
        "tests": {
            "tsd": (base / "tsd.md").exists(),
            "test_specs": test_specs,
            "verification": _verify_lane(repo_root),
        },
        "bugs": bugs,
        "workflows": workflows,
        "reviews": {
            "has_review_state": bool(review_state),
            "review_files": len(review_files),
            "latest": (base / "reviews" / "LATEST.md").exists(),
        },
    }


def cmd_pillars(args: argparse.Namespace) -> int:
    """Print the four-pillar census."""
    data = gather(Path(args.root).resolve())
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 0
    req = data["requirements"]
    print(f"Requirements: PRD={'yes' if req['prd'] else 'no'} "
          f"personas={'yes' if req['personas'] else 'no'} "
          f"epics={req['epics']['total']} ({req['epics_ready_pct']}% ready+) "
          f"stories={req['stories']['total']} ({req['stories_done_pct']}% done)")
    print(f"Code:         TRD={'yes' if data['code']['trd'] else 'no'}")
    print(f"Tests:        TSD={'yes' if data['tests']['tsd'] else 'no'} "
          f"test-specs={data['tests']['test_specs']['total']}")
    print(f"Bugs:         open={data['bugs']['by_status'].get('Open', 0)} "
          f"fixed={data['bugs']['by_status'].get('Fixed', 0)} total={data['bugs']['total']}")
    print(f"Workflows:    total={data['workflows']['total']}")
    print(f"Reviews:      files={data['reviews']['review_files']} "
          f"latest={'yes' if data['reviews']['latest'] else 'no'}")
    adv = workspace_advisory(Path(args.root))
    if adv:
        print(f"advisory: {adv}")
    _print_update_notice(args.root)
    return 0


def compute_hint(data: dict, repo_root: Path) -> dict:
    """Mechanical next-step ladder. Judgment branches are left to Claude."""
    req = data["requirements"]
    base = repo_root / "sdlc-studio"
    has_code = any((repo_root / d).exists() for d in ("src", "lib", "app", "cmd"))
    if not req["prd"]:
        return {"next_command": "prd generate" if has_code else "prd create",
                "reason": "no PRD yet"}
    if not data["code"]["trd"]:
        return {"next_command": "trd generate" if has_code else "trd create",
                "reason": "no TRD yet"}
    if not data["tests"]["tsd"]:
        return {"next_command": "tsd", "reason": "no TSD yet"}
    if not req["personas"]:
        return {"next_command": "persona", "reason": "no personas yet"}
    if req["epics"]["total"] == 0:
        return {"next_command": "epic", "reason": "no epics yet"}
    if req["stories"]["total"] == 0:
        return {"next_command": "story", "reason": "no stories yet"}
    if (base / ".local" / "workflow-state.json").exists():
        return {"next_command": "resume workflow",
                "reason": "a workflow-state.json is present (judgment: confirm with the operator)"}
    return {"next_command": "story plan / story implement",
            "reason": "pipeline seeded; pick the next Ready story (judgment)"}


def cmd_hint(args: argparse.Namespace) -> int:
    """Print the single next recommended action."""
    repo_root = Path(args.root).resolve()
    data = gather(repo_root)
    hint = compute_hint(data, repo_root)
    if args.format == "json":
        print(json.dumps(hint, indent=2))
    else:
        print(f"/sdlc-studio {hint['next_command']}  ({hint['reason']})")
        _print_update_notice(args.root)
    adv = workspace_advisory(Path(args.root))
    if adv and args.format != "json":
        print(f"advisory: {adv}")
    if args.format != "json":
        for line in index_bloat_advisories(Path(args.root)):
            print(f"advisory: {line}")
    return 0


def index_bloat_advisories(repo_root: Path) -> list[str]:
    """The per-type archive recommendations (reconcile's index-bloat rule),
    surfaced at the hint so a bloating index is seen where operators look."""
    try:
        import reconcile
    except ImportError:  # pragma: no cover - sibling script always ships
        return []
    out: list[str] = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        try:
            a = reconcile.index_bloat_advisory(type_, repo_root)
        except Exception:  # noqa: BLE001 - an advisory must never break the hint
            continue
        if a:
            out.append(a)
    return out


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for pillars and hint."""
    p = argparse.ArgumentParser(
        prog="status.py",
        description="Deterministic sdlc-studio pipeline status and hint.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("pillars", help="Census of the four pillars.")
    pi.add_argument("--root", default=".", help="Repo root (default: .)")
    pi.add_argument("--format", choices=("text", "json"), default="text")
    pi.set_defaults(func=cmd_pillars)

    hi = sub.add_parser("hint", help="The next recommended action.")
    hi.add_argument("--root", default=".", help="Repo root (default: .)")
    hi.add_argument("--format", choices=("text", "json"), default="text")
    hi.set_defaults(func=cmd_hint)

    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
