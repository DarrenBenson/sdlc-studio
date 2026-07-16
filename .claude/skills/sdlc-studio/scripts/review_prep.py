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
import lessons  # noqa: E402  (sibling - the ranked lesson lenses the review starts from)

PROJECT_DOCS = ["prd", "trd", "tsd", "personas"]

# Index files in personas/ are not personas. The dir uses `index.md` (some repos `_index.md`);
# excluding only one let the other be parsed as a phantom persona ("Persona Index"). One set,
# used by both the persona-usage and required-legs passes, so they cannot disagree.
PERSONA_INDEX_NAMES = {"index.md", "_index.md"}


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
    # across the deterministic helpers.
    persona_files = [p for p in sorted(personas_dir.glob("*.md"))
                     if p.name not in PERSONA_INDEX_NAMES] if personas_dir.is_dir() else []
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


def _leg_path(base: Path, leg: str) -> tuple[Path, bool]:
    """(primary artefact path, present?) for one required document leg. Personas resolve to the
    personas/ directory (any file bar the index) when it holds cards, else the single
    personas.md - the same source order the persona review and completion cascade read."""
    if leg == "personas":
        pdir = base / "personas"
        files = [p for p in pdir.glob("*.md") if p.name not in PERSONA_INDEX_NAMES] if pdir.is_dir() else []
        if files:
            return pdir, True
        pmd = base / "personas.md"
        return pmd, pmd.exists()
    p = base / f"{leg}.md"
    return p, p.exists()


def required_legs(repo_root: Path) -> dict:
    """Presence + waiver state for each of the four required document legs (PRD/TRD/TSD/Persona).
    For each leg: {present, path, waiver: <decision-id|null>}. This makes an absent leg
    machine-visible - the review can no longer silently reclassify a required-but-missing leg as
    'optional' in prose, because a downgrade without a recorded waiver is now detectable. The CODE
    leg is out of scope: it has no single artefact whose presence can be tested (decision D0022)."""
    import decisions
    base = repo_root / "sdlc-studio"
    out: dict[str, dict] = {}
    for leg in decisions.DOC_LEGS:
        path, present = _leg_path(base, leg)
        out[leg] = {
            "present": present,
            "path": str(path.relative_to(repo_root)),
            "waiver": decisions.waiver_for(repo_root, f"leg:{leg}"),
        }
    return out


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


LESSON_LENS_MAX = 12  # ranked, so the cap drops the least-biting, not an arbitrary tail


def close(repo_root: Path | str, rv_id: str, latest_body: str | None = None,
          legs: tuple[str, ...] = ("prd", "trd", "tsd", "personas")) -> dict:
    """The review close, tool-carried: stamp review-state.json for every present leg
    and (optionally) write the LATEST.md anchor - REFUSING both when the dated RV
    record does not exist, and refusing an anchor body that never references the
    record it claims to derive from. The near-loss this closes: a review that lived
    ONLY in the overwritable anchor, one rewrite from destruction, and a CRITICAL
    state stamp the workflow spelled out but nothing performed."""
    root = Path(repo_root)
    norm = sdlc_md.norm_id(rv_id)
    # match the stem directly (extract_record_id does not know the RV prefix):
    # RV0042 matches RV0042-anything.md but never RV00421-*.md (the boundary check)
    def _is_rv(stem: str) -> bool:
        s = stem.upper().replace("RV-", "RV")
        return s == norm or s.startswith(norm + "-")
    reviews_dir = root / "sdlc-studio" / "reviews"
    rv_files = ([p for p in reviews_dir.glob("*.md") if _is_rv(p.stem)]
                if reviews_dir.is_dir() else [])
    if not rv_files:
        raise ValueError(f"no dated review record for {rv_id} under sdlc-studio/reviews/ - "
                         f"the close stamps nothing and derives no anchor from a record "
                         f"that does not exist; write the RV file first (artifact.py new "
                         f"--type review)")
    rv_path = rv_files[0]
    if latest_body is not None and norm not in latest_body.replace("-", ""):
        raise ValueError(f"the anchor body never references {rv_id} - LATEST.md is a "
                         f"pointer to the dated record, not a record itself; cite the RV "
                         f"id in the body")
    now = sdlc_md.now_iso8601()
    present = required_legs(root)
    base = root / "sdlc-studio"
    state_path = base / ".local" / "review-state.json"
    state = sdlc_md.read_json(state_path, {}) or {}
    state.setdefault("version", 1)
    artifacts = state.setdefault("artifacts", {})
    stamped: list[str] = []
    for leg in legs:
        info = present.get(leg) or {}
        if not info.get("present"):
            continue
        key = "persona" if leg == "personas" else leg
        path = Path(info["path"]) if info.get("path") else base / f"{leg}.md"
        modified, _method = _modified_iso(root / path if not Path(path).is_absolute()
                                          else Path(path), root)
        entry = artifacts.setdefault(key, {})
        entry.update({"type": key, "path": str(path), "last_reviewed": now,
                      "last_modified": modified, "review_findings_ref": norm})
        stamped.append(key)
    state.setdefault("reviews", {})[norm] = {
        "artifact": "+".join(stamped), "timestamp": now,
        "findings_file": str(rv_path.relative_to(root)),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(state_path, json.dumps(state, indent=2))
    if latest_body is not None:
        sdlc_md.atomic_write(base / "reviews" / "LATEST.md", latest_body)
    return {"stamped": sorted(stamped), "rv": norm,
            "latest_written": latest_body is not None, "state": str(state_path)}


def cmd_close(args: argparse.Namespace) -> int:
    body = None
    if args.latest_body:
        body = (sys.stdin.read() if args.latest_body == "-"
                else Path(args.latest_body).read_text(encoding="utf-8"))
    try:
        r = close(args.root, args.rv, latest_body=body)
    except (ValueError, OSError) as exc:
        print(f"close refused: {exc}", file=sys.stderr)
        return 2
    print(f"review close stamped {', '.join(r['stamped'])} -> {r['state']}"
          + ("; LATEST.md derived from the record" if r["latest_written"] else ""))
    return 0


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
        "required_legs": required_legs(repo_root),
        "inputs": inputs(repo_root),
        # The lessons the last mistakes were paid for, as REVIEW LENSES. A review that does not
        # know what has already bitten this codebase re-derives it, or misses it. Ranked by what
        # is biting hardest, so the review starts with the classes most likely to be here again.
        "lessons": lessons.cross_digest(repo_root),
    }
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        nr = data["needs_review"]
        pu = data["persona_usage"]
        rl = data["required_legs"]
        print(f"needs_review ({len(nr)}): {', '.join(nr) if nr else 'none'}")
        for w in data["warnings"]:
            print(f"warning: {w}")
        absent = [k for k, v in rl.items() if not v["present"] and not v["waiver"]]
        waived = [f"{k} ({v['waiver']})" for k, v in rl.items()
                  if not v["present"] and v["waiver"]]
        print(f"required legs absent+unwaived ({len(absent)}): "
              f"{', '.join(absent) if absent else 'none'}"
              + (f"; waived: {', '.join(waived)}" if waived else ""))
        print(f"personas defined={len(pu['defined'])} unused={len(pu['unused'])}"
              + (f" ({', '.join(pu['unused'])})" if pu["unused"] else ""))
        print(f"counts: {data['inputs']['counts']}")
        if data["inputs"]["ac_verification"]:
            print(f"ac: {data['inputs']['ac_verification']}")
        _render_lens(data["lessons"])
    return 0


def _render_lens(digest: dict) -> None:
    """The lessons, printed IN the prep output the reviewer already reads.

    A prose instruction to go and open the lessons file is the kind of instruction that gets
    skipped, which is how a class can be written down, paid for, and written down again. So the
    lens arrives unasked, in the data the review starts from.
    """
    items = (digest or {}).get("lessons") or []
    if not items:
        return
    n = digest["count"]
    print(f"\nreview lenses - what has already bitten, hardest first ({n}):")
    for it in items[:LESSON_LENS_MAX]:
        cited = f" [x{it['recurrence']}]" if it.get("recurrence") else ""
        print(f"  {it['id']}{cited}: {it['title']}")
    if n > LESSON_LENS_MAX:
        print(f"  (+{n - LESSON_LENS_MAX} more, ranked lower - `lessons.py rank` for the full "
              f"order, `lessons.py recall` to read one)")


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
    cl = sub.add_parser("close", help="Stamp review-state.json for the review just written "
                                      "(and optionally derive LATEST.md) - refuses without "
                                      "the dated RV record.")
    cl.add_argument("--rv", required=True, metavar="RVxxxx",
                    help="the dated review record this close stamps")
    cl.add_argument("--latest-body", metavar="FILE|-", dest="latest_body",
                    help="anchor content to write to reviews/LATEST.md (stdin with -); "
                         "must reference the RV id - the anchor derives from the record")
    cl.add_argument("--root", default=".", help="Repo root (default: .)")
    cl.set_defaults(func=cmd_close)
    sdlc_md.add_global_root(p)
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
