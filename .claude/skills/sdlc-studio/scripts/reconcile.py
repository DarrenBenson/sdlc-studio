#!/usr/bin/env python3
"""SDLC Studio reconcile: deterministic drift detection (read-only).

Builds the file census doctrine rule 3 prescribes - artifact files are the
truth, `_index.md` tables are derived - and reports where the indexes have
drifted. Three drift classes per type: status mismatch (file vs index row),
missing row (a file with no index row), and orphan row (an index row with no
file), plus summary-count drift. Read-only: emits a JSON report; Claude (or an
explicit, separately-reviewed apply step) does the editing and the judgment
(checkbox/dependency/PRD-feature drift, CR cascades, changelog).

Subcommand:
  detect  Census + drift report as JSON/text.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# scope name -> artifact types it covers.
SCOPE_TYPES = {
    "stories": ["story"],
    "epics": ["epic"],
    "crs": ["cr"],
    "rfcs": ["rfc"],
    "plans": ["plan"],
    "test-specs": ["test-spec"],
    "indexes": ["story", "epic", "cr", "rfc", "plan", "test-spec"],
}
_DEFAULT_TYPES = ["story", "epic", "cr", "rfc", "plan", "test-spec"]


def file_census(type_: str, repo_root: Path) -> dict[str, str]:
    """Map artifact ID -> Status from the files on disk (the source of truth)."""
    census: dict[str, str] = {}
    for path in sdlc_md.artifact_files(type_, repo_root):
        rec = sdlc_md.extract_record_id(path.stem)
        if not rec:
            continue
        status = sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status") or "Unknown"
        census[rec] = status
    return census


def _table_cells(line: str) -> list[str] | None:
    """Cells of a markdown table row, or None if the line is not a table row."""
    s = line.strip()
    if not s.startswith("|"):
        return None
    cells = [c.strip() for c in s.strip("|").split("|")]
    if all(set(c) <= {"-", ":"} and c for c in cells):
        return None  # separator row
    return cells


def parse_index(type_: str, repo_root: Path) -> dict:
    """Parse a type's _index.md into {rows: {id: status}, summary: {status: count}}.

    Resilient to column order: the ID is the first cell containing an artifact
    ID, the status the first cell whose text is a valid status for the type.
    The summary table is rows of `| Status | Count |`.
    """
    rel, _prefix = sdlc_md.ARTIFACT_TYPES[type_]
    index_path = repo_root / rel / "_index.md"
    result = {"exists": index_path.exists(), "rows": {}, "summary": {}}
    if not index_path.exists():
        return result
    vocab = set(sdlc_md.STATUS_VOCAB[type_])
    for line in index_path.read_text(encoding="utf-8").splitlines():
        cells = _table_cells(line)
        if not cells:
            continue
        # Summary row: `| <Status> | <int> |`
        if len(cells) == 2 and cells[1].replace(",", "").isdigit():
            label = cells[0].strip("*").strip()
            if label in vocab:
                result["summary"][label] = int(cells[1].replace(",", ""))
            continue
        # Data row: find an ID cell and a status cell.
        row_id = None
        row_status = None
        for c in cells:
            if row_id is None:
                m = sdlc_md.ID_SEARCH_RE.search(c)
                if m:
                    row_id = m.group(0)
            if row_status is None and c.strip("*").strip() in vocab:
                row_status = c.strip("*").strip()
        if row_id:
            result["rows"][row_id] = row_status or "Unknown"
    return result


def detect_type(type_: str, repo_root: Path) -> dict:
    """Compute drift for one type."""
    census = file_census(type_, repo_root)
    index = parse_index(type_, repo_root)
    drift: list[dict] = []

    if census and not index["exists"]:
        drift.append({
            "type": type_, "id": None, "kind": "missing-index",
            "file_status": None, "index_status": None,
            "fix": f"create {sdlc_md.ARTIFACT_TYPES[type_][0]}/_index.md from the {len(census)} files",
        })

    rows = index["rows"]
    for rec, fstatus in sorted(census.items()):
        if rec not in rows:
            drift.append({"type": type_, "id": rec, "kind": "missing-row",
                          "file_status": fstatus, "index_status": None,
                          "fix": f"add {rec} ({fstatus}) to the index"})
        elif rows[rec] != fstatus:
            drift.append({"type": type_, "id": rec, "kind": "status-mismatch",
                          "file_status": fstatus, "index_status": rows[rec],
                          "fix": f"set index status of {rec} to {fstatus}"})
    for rec in sorted(rows):
        if rec not in census:
            drift.append({"type": type_, "id": rec, "kind": "orphan-row",
                          "file_status": None, "index_status": rows[rec],
                          "fix": f"remove orphan index row {rec} (no backing file)"})

    # Count drift: census tally vs summary table.
    census_counts: dict[str, int] = {}
    for st in census.values():
        census_counts[st] = census_counts.get(st, 0) + 1
    count_mismatch = bool(index["summary"]) and any(
        index["summary"].get(st, 0) != census_counts.get(st, 0)
        for st in set(index["summary"]) | set(census_counts)
    )
    if count_mismatch:
        drift.append({"type": type_, "id": None, "kind": "count-mismatch",
                      "file_status": None, "index_status": None,
                      "fix": "recompute the summary counts from the file census"})

    return {
        "census_total": len(census),
        "census_counts": census_counts,
        "index_exists": index["exists"],
        "index_summary": index["summary"],
        "drift": drift,
    }


def cmd_detect(args: argparse.Namespace) -> int:
    """Run drift detection across the selected scope and report."""
    repo_root = Path(args.root).resolve()
    types = SCOPE_TYPES.get(args.scope, _DEFAULT_TYPES) if args.scope else _DEFAULT_TYPES

    per_type: dict[str, dict] = {}
    all_drift: list[dict] = []
    for type_ in types:
        result = detect_type(type_, repo_root)
        per_type[type_] = result
        all_drift.extend(result["drift"])

    by_kind: dict[str, int] = {}
    for d in all_drift:
        by_kind[d["kind"]] = by_kind.get(d["kind"], 0) + 1

    report = {
        "generated_at": sdlc_md.now_iso8601(),
        "scope": args.scope or "all",
        "types": per_type,
        "drift": all_drift,
        "summary": {"drift_items": len(all_drift), "by_kind": by_kind},
    }

    out_path = repo_root / "sdlc-studio" / ".local" / "reconcile-report.json"
    if args.write_report:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for d in all_drift:
            ident = d["id"] or d["type"]
            print(f"{d['kind']:16} {ident}: {d['fix']}")
        print(f"scope={report['scope']} drift_items={len(all_drift)} by_kind={by_kind}")
        if args.write_report:
            print(f"wrote {out_path}")
    return 1 if all_drift else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for the detect subcommand."""
    p = argparse.ArgumentParser(
        prog="reconcile.py",
        description="Detect index drift from the artifact-file census (read-only).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detect", help="Census + drift report.")
    d.add_argument("--scope", choices=sorted(SCOPE_TYPES),
                   help="Limit to one scope (default: all index-driven types)")
    d.add_argument("--root", default=".", help="Repo root (default: .)")
    d.add_argument("--format", choices=("text", "json"), default="text")
    d.add_argument("--write-report", action="store_true",
                   help="Also write sdlc-studio/.local/reconcile-report.json")
    d.set_defaults(func=cmd_detect)
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
