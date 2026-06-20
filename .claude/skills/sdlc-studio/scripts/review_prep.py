#!/usr/bin/env python3
"""SDLC Studio review-prep: deterministic inputs for the five-leg review.

The unified review (PRD - TRD - TSD - Persona - Code) is Claude's judgment
call. This script front-loads the *mechanical* inputs each leg needs, so the
review starts from data instead of re-deriving it in-context: artifact
staleness (changed since last review), persona usage (defined vs referenced in
the PRD), and the count/AC-verification inputs. It makes no judgements and
mutates nothing - it gathers.

Subcommand:
  prep  Emit the review inputs as JSON/text.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

PROJECT_DOCS = ["prd", "trd", "tsd", "personas"]


def _git_iso(path: Path, repo_root: Path) -> str | None:
    """Last commit time for `path` as ISO-8601, or None if untracked/unavailable."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%cI", "--", str(path)],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return r.stdout.strip() or None


def _modified_iso(path: Path, repo_root: Path) -> tuple[str, str]:
    """(timestamp, method): git commit time when tracked, else file mtime.

    The git commit time is reproducible across clones, pulls and checkouts;
    `st_mtime` is reset by every one of those, so it is only the fallback for an
    untracked file or when git is unavailable. Note the git time is the last
    *commit*, so a tracked file with uncommitted working-tree edits reads as
    unmodified - reviewing committed state is the normal case.
    """
    git = _git_iso(path, repo_root)
    if git:
        return git, "git"
    ts = path.stat().st_mtime
    return datetime.fromtimestamp(ts, timezone.utc).isoformat(), "mtime"


def _parse_dt(value: str | None) -> datetime | None:
    """Parse an ISO-8601 timestamp to an aware datetime (UTC if naive); None if bad."""
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def staleness(repo_root: Path) -> dict:
    """For each artifact and project doc, whether it changed since last review.

    'Last modified' is the git commit time (reproducible) with an st_mtime
    fallback; it is compared to review-state.json `last_reviewed` as parsed
    datetimes, not raw strings. No entry, or an unparseable `last_reviewed`,
    means needs review (the latter also surfaces a warning).
    """
    base = repo_root / "sdlc-studio"
    state = sdlc_md.read_json(base / ".local" / "review-state.json", {})
    reviewed = state.get("artifacts", {}) if isinstance(state, dict) else {}
    out: dict[str, dict] = {}

    def consider(key: str, path: Path) -> None:
        if not path.exists():
            return
        modified, method = _modified_iso(path, repo_root)
        entry = reviewed.get(key, {})
        last_reviewed = entry.get("last_reviewed")
        rec = {
            "path": str(path.relative_to(repo_root)),
            "last_modified": modified,
            "modified_method": method,
            "last_reviewed": last_reviewed,
        }
        if last_reviewed is None:
            rec["needs_review"] = True
        else:
            r_dt = _parse_dt(last_reviewed)
            if r_dt is None:
                rec["needs_review"] = True
                rec["warning"] = f"unparseable last_reviewed {last_reviewed!r}; treated as needs_review"
            else:
                m_dt = _parse_dt(modified)
                rec["needs_review"] = (m_dt is None) or (m_dt > r_dt)
        out[key] = rec

    for doc in PROJECT_DOCS:
        consider(doc, base / f"{doc}.md")
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, repo_root):
            rec = sdlc_md.extract_record_id(path.stem)
            if rec:
                consider(rec, path)
    return out


def persona_usage(repo_root: Path) -> dict:
    """Persona names defined vs referenced in the PRD (heuristic, deterministic).

    Definitions are H2 headings in personas.md; a persona is 'referenced' if its
    name appears anywhere in prd.md. 'unused' lists defined-but-unreferenced
    personas for the Persona leg to judge.
    """
    base = repo_root / "sdlc-studio"
    personas_dir = base / "personas"
    personas_md = base / "personas.md"
    prd_md = base / "prd.md"
    defined: list[str] = []
    # Prefer the personas/ directory (one file per persona) when present - this is
    # what the epic completion cascade and the review command read; fall back to
    # the single personas.md (H2 headings) otherwise. Keeps the source consistent
    # across the deterministic helpers (BG0004).
    persona_files = [p for p in sorted(personas_dir.glob("*.md"))
                     if p.name != "_index.md"] if personas_dir.is_dir() else []
    method = ""
    if persona_files:
        for p in persona_files:
            for line in p.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^#\s+(.+?)\s*$", line)
                if m:
                    defined.append(m.group(1).strip())
                    break
        method = "heuristic: H1 of each personas/*.md (preferred), substring match in prd.md"
    elif personas_md.exists():
        for line in personas_md.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^##\s+(.+?)\s*$", line)
            if m:
                defined.append(m.group(1).strip())
        method = "heuristic: H2 headings in personas.md (fallback), substring match in prd.md"
    prd_text = prd_md.read_text(encoding="utf-8") if prd_md.exists() else ""
    referenced = [name for name in defined if name and name in prd_text]
    unused = [name for name in defined if name not in referenced]
    return {
        "defined": defined,
        "referenced_in_prd": referenced,
        "unused": unused,
        "method": method or "no personas found",
    }


def inputs(repo_root: Path) -> dict:
    """Count and AC-verification inputs the review legs consume."""
    base = repo_root / "sdlc-studio"
    counts = {
        type_: len(sdlc_md.artifact_files(type_, repo_root))
        for type_ in sdlc_md.ARTIFACT_TYPES
    }
    verify_report = sdlc_md.read_json(base / ".local" / "verify-report.json", None)
    ac_summary = None
    if isinstance(verify_report, dict):
        stories = verify_report.get("stories", {})
        ac_summary = {
            "stories": len(stories),
            "verified": sum(s.get("verified", 0) for s in stories.values()),
            "failed": sum(s.get("failed", 0) for s in stories.values()),
        }
    return {"counts": counts, "ac_verification": ac_summary}


def cmd_prep(args: argparse.Namespace) -> int:
    """Emit the review inputs."""
    repo_root = Path(args.root).resolve()
    stale = staleness(repo_root)
    data = {
        "generated_at": sdlc_md.now_iso8601(),
        "staleness": stale,
        "needs_review": sorted(k for k, v in stale.items() if v["needs_review"]),
        "warnings": sorted(f"{k}: {v['warning']}" for k, v in stale.items() if "warning" in v),
        "persona_usage": persona_usage(repo_root),
        "inputs": inputs(repo_root),
    }
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        nr = data["needs_review"]
        pu = data["persona_usage"]
        print(f"needs_review ({len(nr)}): {', '.join(nr) if nr else 'none'}")
        for w in data["warnings"]:
            print(f"warning: {w}")
        print(f"personas defined={len(pu['defined'])} unused={len(pu['unused'])}"
              + (f" ({', '.join(pu['unused'])})" if pu["unused"] else ""))
        print(f"counts: {data['inputs']['counts']}")
        if data["inputs"]["ac_verification"]:
            print(f"ac: {data['inputs']['ac_verification']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for the prep subcommand."""
    p = argparse.ArgumentParser(
        prog="review_prep.py",
        description="Gather deterministic inputs for the five-leg unified review.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("prep", help="Emit review inputs (staleness, persona usage, counts).")
    pr.add_argument("--root", default=".", help="Repo root (default: .)")
    pr.add_argument("--format", choices=("text", "json"), default="text")
    pr.set_defaults(func=cmd_prep)
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
