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
    "bugs": ["bug"],
    "workflows": ["workflow"],
    "indexes": ["story", "epic", "cr", "rfc", "plan", "test-spec", "bug", "workflow"],
}
_DEFAULT_TYPES = ["story", "epic", "cr", "rfc", "plan", "test-spec", "bug", "workflow"]

# Statuses that do NOT imply a backing file yet. An index row in one of these
# states (or a non-vocabulary state such as a custom "Retired"/"Reserved") with
# no file on disk is an intentional reservation or a documented retirement —
# not an orphan to remove. Only an active/terminal status (Done, In Progress,
# Complete, …) with no file is a real orphan.
_NO_FILE_EXPECTED = {
    "Proposed", "Draft", "Deferred", "Superseded", "Withdrawn", "Rejected",
    "Won't Implement", "Won't Fix",
}


# Shared, project-agnostic helpers (id normalisation + status canonicalisation)
# live in sdlc_md so every script handles the same conventions identically.
_norm_id = sdlc_md.norm_id
_canonical_status = sdlc_md.canonical_status


def file_census(type_: str, repo_root: Path) -> dict[str, tuple[str, str]]:
    """Map normalised artifact ID -> (display id, raw Status) from disk (truth)."""
    vocab = sdlc_md.STATUS_VOCAB.get(type_, [])
    census: dict[str, tuple[str, str]] = {}
    for path in sdlc_md.artifact_files(type_, repo_root):
        rec = sdlc_md.extract_record_id(path.stem)
        if not rec:
            continue
        status = sdlc_md.extract_field(path.read_text(encoding="utf-8"), "Status") or "Unknown"
        key = _norm_id(rec)
        prev = census.get(key)
        # A file with a recognised status wins over a status-less namesake
        # sharing the ID (e.g. `EP0025-consultations.md` must not clobber the
        # real `EP0025` epic's status).
        if _canonical_status(status, vocab) is not None or prev is None:
            census[key] = (rec, status)
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

    The Status (and ID) columns are located by the data table's **header row** and
    read positionally, so a title cell that begins with a status word (e.g.
    "review_prep..." -> Review, "Complete the gate..." -> Complete) is never mistaken
    for the status (BG0018). Falls back to a first-matching-cell scan only when no
    header is found. The summary table is rows of `| Status | Count |`.
    """
    rel, _prefix = sdlc_md.ARTIFACT_TYPES[type_]
    index_path = repo_root / rel / "_index.md"
    result = {"exists": index_path.exists(), "rows": {}, "summary": {}}
    if not index_path.exists():
        return result
    vocab = list(sdlc_md.STATUS_VOCAB[type_])
    status_col = id_col = None  # resolved from the data table's header row
    for line in index_path.read_text(encoding="utf-8").splitlines():
        cells = _table_cells(line)
        if not cells:
            continue
        # Summary row: `| <Status> | <int> |`
        if len(cells) == 2 and cells[1].replace(",", "").isdigit():
            label = _canonical_status(cells[0], vocab)
            if label:
                result["summary"][label] = int(cells[1].replace(",", ""))
            continue
        lowered = [c.lower() for c in cells]
        # Header row of ANY table block: a data row never has a cell that is
        # literally "status", so this fires only on headers. Re-pin every time
        # (no first-header latch) so a second table with a different layout - e.g.
        # per-CR breakdown tables with Status in a different column than the master
        # table - is read against its own header, not the first one (agent-crew
        # two-layout indexes).
        if len(cells) > 2 and "status" in lowered:
            status_col = lowered.index("status")
            id_col = lowered.index("id") if "id" in lowered else None
            continue
        # Data row - read positionally when the header was found.
        if id_col is not None and id_col < len(cells):
            m = sdlc_md.ID_SEARCH_RE.search(cells[id_col])
            row_id = m.group(0) if m else None
        else:
            row_id = next((sdlc_md.ID_SEARCH_RE.search(c).group(0)
                           for c in cells if sdlc_md.ID_SEARCH_RE.search(c)), None)
        if status_col is not None and status_col < len(cells):
            row_status = _canonical_status(cells[status_col], vocab)
        else:  # header-less fallback (legacy): first cell that canonicalises
            row_status = next((cs for c in cells if (cs := _canonical_status(c, vocab))), None)
        if row_id:
            key = _norm_id(row_id)
            prev = result["rows"].get(key)
            # A real status never gets clobbered by a later status-less row
            # mentioning the same ID (e.g. a dependency or breakdown table).
            if row_status is not None or prev is None:
                result["rows"][key] = (row_id, row_status or "Unknown")
    return result


def detect_type(type_: str, repo_root: Path) -> dict:
    """Compute drift for one type."""
    census = file_census(type_, repo_root)
    index = parse_index(type_, repo_root)
    drift: list[dict] = []
    vocab = sdlc_md.STATUS_VOCAB.get(type_, [])

    if census and not index["exists"]:
        drift.append({
            "type": type_, "id": None, "kind": "missing-index",
            "file_status": None, "index_status": None,
            "fix": f"create {sdlc_md.ARTIFACT_TYPES[type_][0]}/_index.md from the {len(census)} files",
        })

    rows = index["rows"]
    for norm, (disp, fstatus) in sorted(census.items()):
        if norm not in rows:
            drift.append({"type": type_, "id": disp, "kind": "missing-row",
                          "file_status": fstatus, "index_status": None,
                          "fix": f"add {disp} ({fstatus}) to the index"})
        else:
            istatus = rows[norm][1]
            fcanon = _canonical_status(fstatus, vocab)
            icanon = _canonical_status(istatus, vocab)
            # Only a file that DECLARES a recognised status can drift from its
            # index row. A file with no status field (legacy docs) or a
            # non-vocabulary status asserts nothing to compare — skip it rather
            # than emit noise every run.
            target = icanon if icanon is not None else istatus
            if fcanon is not None and fcanon != target:
                drift.append({"type": type_, "id": disp, "kind": "status-mismatch",
                              "file_status": fstatus, "index_status": istatus,
                              "fix": f"set index status of {disp} to {fstatus}"})
    for norm, (disp, istatus) in sorted(rows.items()):
        if norm not in census:
            icanon = _canonical_status(istatus, vocab)
            # A row whose status doesn't imply a file yet (Proposed/Draft/…) or
            # is a custom retirement (non-vocabulary) is an intentional
            # reservation, not an orphan — don't flag it.
            if icanon is None or icanon in _NO_FILE_EXPECTED:
                continue
            drift.append({"type": type_, "id": disp, "kind": "orphan-row",
                          "file_status": None, "index_status": istatus,
                          "fix": f"remove orphan index row {disp} (no backing file)"})

    # Count drift: the summary table summarises the INDEX ROWS, so check it
    # against the row tally (canonical), not the file census. This is the right
    # authority for types whose files routinely carry no status field (e.g. CRs)
    # — per-row file-vs-index drift is already caught by status-mismatch above.
    row_counts: dict[str, int] = {}
    for _disp, istatus in rows.values():
        rc = _canonical_status(istatus, vocab)
        if rc is not None:
            row_counts[rc] = row_counts.get(rc, 0) + 1
    count_mismatch = bool(index["summary"]) and any(
        index["summary"].get(st, 0) != row_counts.get(st, 0)
        for st in set(index["summary"]) | set(row_counts)
    )
    if count_mismatch:
        drift.append({"type": type_, "id": None, "kind": "count-mismatch",
                      "file_status": None, "index_status": None,
                      "fix": "recompute the summary counts from the index rows"})

    # File-census tally kept for information (status distribution on disk).
    census_counts: dict[str, int] = {}
    for _disp, fstatus in census.values():
        key = _canonical_status(fstatus, vocab) or "Unknown"
        census_counts[key] = census_counts.get(key, 0) + 1

    return {
        "census_total": len(census),
        "census_counts": census_counts,
        "row_counts": row_counts,
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
        hints = sdlc_md.remediation_lines("reconcile", by_kind)
        if hints:
            print("Guidance:")
            for h in hints:
                print(f"  - {h}")
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
