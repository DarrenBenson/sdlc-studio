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
import re
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
    vocab = sdlc_md.status_vocab(type_, repo_root)
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
    """Cells of a markdown table row, or None if not a table row. Thin alias for
    the shared escaped-pipe-aware splitter."""
    return sdlc_md.table_cells(line)


def _index_rows_and_summary(text: str, vocab: list) -> tuple[dict, dict]:
    """Parse one index file's table rows into ({norm_id: (disp, status)}, {status: count}).

    The Status (and ID) columns are located by the data table's **header row** and
    read positionally, so a title cell that begins with a status word (e.g.
    "review_prep..." -> Review) is never mistaken for the status. Falls back
    to a first-matching-cell scan only when no header is found.
    """
    rows: dict = {}
    summary: dict = {}
    status_col = id_col = None
    for line in text.splitlines():
        cells = _table_cells(line)
        if not cells:
            continue
        if len(cells) == 2 and cells[1].replace(",", "").isdigit():  # `| <Status> | <int> |`
            label = _canonical_status(cells[0], vocab)
            if label:
                summary[label] = int(cells[1].replace(",", ""))
            continue
        lowered = [c.lower() for c in cells]
        if len(cells) > 2 and "status" in lowered:  # re-pin per header (two-layout safe)
            status_col = lowered.index("status")
            id_col = lowered.index("id") if "id" in lowered else None
            continue
        if id_col is not None and id_col < len(cells):
            m = sdlc_md.ID_SEARCH_RE.search(cells[id_col])
            row_id = m.group(0) if m else None
        else:
            row_id = next((sdlc_md.ID_SEARCH_RE.search(c).group(0)
                           for c in cells if sdlc_md.ID_SEARCH_RE.search(c)), None)
        if status_col is not None and status_col < len(cells):
            row_status = _canonical_status(cells[status_col], vocab)
        else:
            row_status = None
        if row_status is None:
            # the pinned column held no status - a header-less block, or a stacked table whose Status
            # sits in a different column. Find the status by canonical-vocab token, not position, so an
            # off-schema row is not misread as "Unknown" -> phantom status-mismatch.
            row_status = next((cs for c in cells if (cs := _canonical_status(c, vocab))), None)
        if row_id:
            key = _norm_id(row_id)
            if row_status is not None or key not in rows:
                rows[key] = (row_id, row_status or "Unknown")
    return rows, summary


def _index_row_ids(text: str) -> list[str]:
    """Every data-row normalised id in one index file, in order, duplicates kept.

    Mirrors `_index_rows_and_summary`'s header-pinned id location, but returns the raw
    sequence (not a {id: ...} dict) so duplicate rows are visible rather than collapsed.
    """
    ids: list[str] = []
    id_col = None
    for line in text.splitlines():
        cells = _table_cells(line)
        if not cells:
            continue
        if len(cells) == 2 and cells[1].replace(",", "").isdigit():  # summary row
            continue
        lowered = [c.lower() for c in cells]
        if len(cells) > 2 and "status" in lowered:  # header row - re-pin the id column
            id_col = lowered.index("id") if "id" in lowered else None
            continue
        if id_col is not None and id_col < len(cells):
            m = sdlc_md.ID_SEARCH_RE.search(cells[id_col])
            rid = m.group(0) if m else None
        else:
            rid = next((sdlc_md.ID_SEARCH_RE.search(c).group(0)
                        for c in cells if sdlc_md.ID_SEARCH_RE.search(c)), None)
        if rid:
            ids.append(_norm_id(rid))
    return ids


def _within_table_dup_counts(text: str) -> dict[str, int]:
    """For each id, the most times it appears in a SINGLE data table of one index file.

    Scoped per-table: an index may legitimately show an id once in each of several
    table views - the story index ships a per-epic "Stories by Epic" view plus an "All Stories"
    table, so every id appears twice across views without being a duplicate. The bug
    `detect_duplicate_rows` guards is an id repeated WITHIN one table, which `parse_index`
    silently collapses. Resets the per-id tally at each table header (mirroring
    `_index_row_ids`' header re-pin). Returns {id: count} only for ids whose within-table count > 1.
    """
    best: dict[str, int] = {}
    table: dict[str, int] = {}
    id_col: int | None = None

    def flush() -> None:
        for rid, n in table.items():
            if n > best.get(rid, 0):
                best[rid] = n

    for line in text.splitlines():
        cells = _table_cells(line)
        if not cells:
            continue
        if len(cells) == 2 and cells[1].replace(",", "").isdigit():  # summary row
            continue
        lowered = [c.lower() for c in cells]
        if len(cells) > 2 and "status" in lowered:  # new table header - flush + reset scope
            flush()
            table = {}
            id_col = lowered.index("id") if "id" in lowered else None
            continue
        if id_col is not None and id_col < len(cells):
            m = sdlc_md.ID_SEARCH_RE.search(cells[id_col])
            rid = m.group(0) if m else None
        else:
            rid = next((sdlc_md.ID_SEARCH_RE.search(c).group(0)
                        for c in cells if sdlc_md.ID_SEARCH_RE.search(c)), None)
        if rid:
            k = _norm_id(rid)
            table[k] = table.get(k, 0) + 1
    flush()
    return {rid: n for rid, n in best.items() if n > 1}


def detect_duplicate_rows(repo_root: Path | str) -> dict:
    """Duplicate index ROWS - the same normalised id appearing more than once **within a single
    data table** of an `_index.md`. `parse_index` keys rows by id into a dict, so a within-table
    duplicate silently overwrites the first: zero drift, gate false-PASS.

        { "duplicates": [ {"type", "id", "count"} ], "count" }

    Detection is per-table: a multi-view index (the story index's per-epic view + its
    All Stories table) lists each id once per view, which is not a duplicate; only a repeat inside
    one table is.
    """
    root = Path(repo_root)
    dups: list[dict] = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        index_path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
        if not index_path.exists():
            continue
        counts = _within_table_dup_counts(index_path.read_text(encoding="utf-8"))
        dups.extend({"type": type_, "id": rid, "count": n}
                    for rid, n in sorted(counts.items()))
    return {"duplicates": dups, "count": len(dups)}


def parse_index(type_: str, repo_root: Path) -> dict:
    """Parse a type's _index.md into {rows, summary}. Rows are the live index rows
    UNIONED with any `<type>/archive/**/*.md` sub-index rows - so an
    artifact archived out of the live table is still seen as "in the index" (no false
    missing-row) and the census stays correct. The summary table is the live index's.
    """
    rel, _prefix = sdlc_md.ARTIFACT_TYPES[type_]
    index_path = repo_root / rel / "_index.md"
    result = {"exists": index_path.exists(), "rows": {}, "summary": {}}
    if not index_path.exists():
        return result
    vocab = sdlc_md.status_vocab(type_, repo_root)
    rows, summary = _index_rows_and_summary(index_path.read_text(encoding="utf-8"), vocab)
    result["summary"] = summary
    result["rows"] = rows
    archive_dir = repo_root / rel / "archive"
    if archive_dir.is_dir():  # archived terminal rows still count toward the census
        for af in sorted(archive_dir.rglob("*.md")):
            arows, _ = _index_rows_and_summary(af.read_text(encoding="utf-8"), vocab)
            for k, v in arows.items():
                if v[1] != "Unknown" or k not in result["rows"]:
                    result["rows"][k] = v
    return result


def _census_filenames(type_: str, repo_root: Path) -> dict[str, str]:
    """Map normalised artifact id -> the file's name relative to its type directory, so a
    missing-row finding can name the file to link rather than leaving the operator to guess it."""
    names: dict[str, str] = {}
    rel = repo_root / sdlc_md.ARTIFACT_TYPES[type_][0]
    for path in sdlc_md.artifact_files(type_, repo_root):
        rec = sdlc_md.extract_record_id(path.stem)
        if rec:
            names[_norm_id(rec)] = path.relative_to(rel).as_posix()
    return names


def detect_type(type_: str, repo_root: Path) -> dict:
    """Compute drift for one type."""
    census = file_census(type_, repo_root)
    index = parse_index(type_, repo_root)
    filenames = _census_filenames(type_, repo_root)
    drift: list[dict] = []
    vocab = sdlc_md.status_vocab(type_, repo_root)

    if census and not index["exists"]:
        drift.append({
            "type": type_, "id": None, "kind": "missing-index",
            "file_status": None, "index_status": None,
            "fix": f"create {sdlc_md.ARTIFACT_TYPES[type_][0]}/_index.md from the {len(census)} files",
        })

    rows = index["rows"]
    for norm, (disp, fstatus) in sorted(census.items()):
        if norm not in rows:
            fname = filenames.get(norm)
            drift.append({"type": type_, "id": disp, "kind": "missing-row",
                          "file_status": fstatus, "index_status": None, "file": fname,
                          "fix": (f"add {disp} ({fstatus}) to the index, linking {fname}"
                                  if fname else f"add {disp} ({fstatus}) to the index")})
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

    # When both status drift and count drift are present, fixing the statuses moves the counts -
    # so the summary must be recomputed LAST, after every status edit settles. Signpost that order
    # rather than leave the operator to learn it by watching the count move the wrong way.
    fix_order = None
    if {"status-mismatch", "missing-row", "orphan-row"} & set(by_kind) and "count-mismatch" in by_kind:
        fix_order = ("Recommended order: resolve the file/index status mismatches first, "
                     "re-sync the index rows, then recompute counts/summaries LAST "
                     "(fixing statuses moves the counts).")

    report = {
        "generated_at": sdlc_md.now_iso8601(),
        "scope": args.scope or "all",
        "types": per_type,
        "drift": all_drift,
        "fix_order": fix_order,
        "summary": {"drift_items": len(all_drift), "by_kind": by_kind},
    }

    if getattr(args, "blocker_sweep", False):
        # advisory lane: report stale-blocked / now-unblocked units. Never affects drift or the
        # exit code - reconcile still succeeds/fails on its own census checks (US0050).
        import blocker_sweep
        try:
            sw = blocker_sweep.sweep(repo_root)
            report["blocker_sweep"] = {"now_unblocked": sw["now_unblocked"],
                                       "still_blocked": sw["still_blocked"], "errors": sw["errors"]}
        except Exception as exc:  # noqa: BLE001 - an advisory lane must never break detect
            report["blocker_sweep"] = {"error": str(exc)}

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
        if fix_order:
            print(fix_order)
        bs = report.get("blocker_sweep")
        if bs and not bs.get("error"):
            if bs["now_unblocked"]:
                print(f"blocker-sweep (advisory): {len(bs['now_unblocked'])} now-unblocked "
                      f"candidate(s): {', '.join(bs['now_unblocked'])}")
            if bs["still_blocked"]:
                print(f"blocker-sweep (advisory): {len(bs['still_blocked'])} still-blocked: "
                      f"{', '.join(bs['still_blocked'])}")
        if args.write_report:
            print(f"wrote {out_path}")
    return 1 if all_drift else 0


def _join_row(cells: list[str]) -> str:
    """Render a table row (escaped-pipe-safe). Thin alias for the shared row writer."""
    return sdlc_md.join_row(cells)


def _canonical_counts(rows: dict[str, tuple[str, str]], vocab: list[str]) -> dict[str, int]:
    """Tally canonical statuses of parse_index rows - the same authority detect uses."""
    counts: dict[str, int] = {}
    for _disp, istatus in rows.values():
        rc = _canonical_status(istatus, vocab)
        if rc is not None:
            counts[rc] = counts.get(rc, 0) + 1
    return counts


def _plan_status_fixes(rows: dict, census: dict, vocab: list) -> tuple[dict, list]:
    """Status fixes to apply (norm id -> new canonical status) and their change
    records, decided against the file census (mirrors detect_type)."""
    fixes: dict[str, str] = {}
    changes: list[dict] = []
    for norm, (disp, istatus) in rows.items():
        if norm not in census:
            continue
        fcanon = _canonical_status(census[norm][1], vocab)
        icanon = _canonical_status(istatus, vocab)
        target = icanon if icanon is not None else istatus
        if fcanon is not None and fcanon != target:
            fixes[norm] = fcanon
            changes.append({"id": disp, "from": istatus, "to": fcanon})
    return fixes, changes


def _row_id(cells: list, status_col: int, id_col: int | None) -> str | None:
    """The artifact id in a data row - by the ID column, else the first id-bearing cell."""
    if id_col is not None and id_col < len(cells):
        m = sdlc_md.ID_SEARCH_RE.search(cells[id_col])
        return m.group(0) if m else None
    return next((sdlc_md.ID_SEARCH_RE.search(c).group(0)
                 for c in cells if sdlc_md.ID_SEARCH_RE.search(c)), None)


def _summary_cell_rewrite(cells: list, counts: dict, vocab: list) -> str | None:
    """The rewritten line for a 2-col summary count row when its count changed, else
    None (also None for a non-count row such as the `| Status | Count |` header)."""
    raw_label, raw_count = cells
    if not raw_count.replace("*", "").replace(",", "").strip().isdigit():
        return None
    label = raw_label.replace("*", "").strip()
    if label.lower() == "total":
        new = sum(counts.values())
    else:
        canon = _canonical_status(label, vocab)
        if canon is None:
            return None
        new = counts.get(canon, 0)
    bold = "**" if "*" in raw_count else ""
    newcell = f"{bold}{new}{bold}"
    return _join_row([raw_label, newcell]) if newcell != raw_count else None


def _header_kind(cells: list, lowered: list) -> tuple[str | None, int | None, int | None]:
    """Classify a table header row: ('summary'|'data'|None, status_col, id_col)."""
    if "status" not in lowered:
        return None, None, None
    if lowered == ["status", "count"]:
        return "summary", None, None
    if len(cells) >= 2:
        return "data", lowered.index("status"), (lowered.index("id") if "id" in lowered else None)
    return None, None, None


_EMPHASIS_RE = re.compile(r"^(\**|`*)(.*?)(\**|`*)$")


def _reapply_emphasis(old_cell: str, new_token: str) -> str:
    """Re-wrap `new_token` in whatever inline emphasis the old cell carried.

    The reader canonicalises a status by stripping `**`/`*`/backticks (see
    `sdlc_md.canonical_status`); the writer must mirror that on the way out, so a
    bold-wrapped cell stays bold rather than flattening to plain text.
    """
    m = _EMPHASIS_RE.match(old_cell.strip())
    lead, trail = (m.group(1), m.group(3)) if m else ("", "")
    wrap = lead if lead and lead == trail else ""
    return f"{wrap}{new_token}{wrap}"


def _data_row_rewrite(cells: list, status_col: int | None, id_col: int | None,
                      fixes: dict, vocab: list) -> tuple[str, str] | None:
    """The (rewritten line, norm_id) for a data row whose Status drifts (per `fixes`), else None.
    Rewrites ONLY when the pinned Status column actually holds a status - so per-block headers in a
    stacked index are followed correctly, while an off-schema / header-less row is left for the
    operator rather than guessing a cell and risking a clobbered title/field. Detect still reports
    it. Inline emphasis on the status cell (`**Proposed**`) is preserved on write."""
    if status_col is None or status_col >= len(cells):
        return None
    if not _canonical_status(cells[status_col], vocab):  # pinned col is not a status -> don't guess
        return None
    rid = _row_id(cells, status_col, id_col)
    if rid and _norm_id(rid) in fixes:
        cells[status_col] = _reapply_emphasis(cells[status_col], fixes[_norm_id(rid)])
        return _join_row(cells), _norm_id(rid)
    return None


def _rewrite_index_lines(lines: list, fixes: dict, counts: dict, vocab: list) -> tuple[bool, set]:
    """Rewrite drifted data-row Status cells (per `fixes`) and summary counts in
    `lines`, in place. Returns (whether any summary count changed, the set of norm-ids whose
    Status cell was actually rewritten). A planned fix whose row the writer declines to touch
    (off-schema/header-less) is absent from that set, so the caller can report it as unapplied
    rather than as a landed change."""
    counts_updated = False
    applied: set = set()
    status_col = id_col = None
    in_summary = False
    # An index may carry many `Status | Count` tables (per-epic/per-section roll-ups) plus the one
    # global summary. Only the canonical global summary is reconcile-managed: the block carrying a
    # `Total` row (the template signature), or the sole summary in the file. A scoped per-epic table
    # is author-maintained - stamping the global total into it corrupts it.
    n_summary = sum(1 for ln in lines
                    if (c := _table_cells(ln)) and [x.lower() for x in c] == ["status", "count"])
    for i, line in enumerate(lines):
        cells = _table_cells(line)
        if not cells:
            if not line.strip().startswith("|"):
                in_summary = False  # a blank/non-table line ends a block (a `---` separator does not)
            continue
        kind, sc, ic = _header_kind(cells, [c.lower() for c in cells])
        if kind == "summary":
            has_total = False
            for j in range(i + 1, len(lines)):  # scan this block for a Total row
                cj = _table_cells(lines[j])
                if cj is None:
                    if not lines[j].strip().startswith("|"):
                        break  # blank/prose ends the block
                    continue   # separator row
                if "status" in [c.lower() for c in cj]:
                    break  # next header - block ended
                if len(cj) == 2 and cj[0].replace("*", "").strip().lower() == "total":
                    has_total = True
                    break
            in_summary, status_col, id_col = (has_total or n_summary == 1), None, None
            continue
        if kind == "data":
            in_summary, status_col, id_col = False, sc, ic
            continue
        if in_summary and len(cells) == 2:        # summary count row
            new_line = _summary_cell_rewrite(cells, counts, vocab)
            if new_line is not None:
                lines[i] = new_line
                counts_updated = True
            continue
        rewritten = _data_row_rewrite(cells, status_col, id_col, fixes, vocab)
        if rewritten is not None:
            lines[i], rid = rewritten
            applied.add(rid)
    return counts_updated, applied


def apply_type(type_: str, repo_root: Path, dry_run: bool = False) -> dict:
    """Apply the two mechanical index fixes for one type: rewrite each drifted data
    row's Status cell to the file's canonical status, then recompute the summary
    counts (from the same parse_index authority `detect` uses). Idempotent; cells
    are re-escaped on write. Structural classes (missing-row/orphan-row/
    missing-index) are left report-only.

    `changes` lists only the fixes that actually landed in the buffer. A planned fix the
    writer could not persist (an off-schema/header-less row it declines to guess) is reported in
    `unapplied`, never as a change - the tool must not announce an edit it did not make. Returns
    {changes: [{id, from, to}], unapplied: [{id, from, to}], counts_updated}.
    """
    root = Path(repo_root)
    vocab = sdlc_md.status_vocab(type_, repo_root)
    index_path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    result: dict = {"changes": [], "unapplied": [], "counts_updated": False}
    if not index_path.exists():
        return result
    rows = parse_index(type_, root)["rows"]
    fixes, planned = _plan_status_fixes(rows, file_census(type_, root), vocab)
    # Model the corrected rows so the count recompute matches detect's authority.
    corrected = dict(rows)
    for norm, new in fixes.items():
        corrected[norm] = (rows[norm][0], new)
    counts = _canonical_counts(corrected, vocab)

    original = index_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    result["counts_updated"], applied = _rewrite_index_lines(lines, fixes, counts, vocab)
    # Partition the planned status fixes by what the writer actually rewrote, so a row it
    # declined to touch is surfaced as unapplied rather than fabricated as a clean flip.
    for ch in planned:
        (result["changes"] if _norm_id(ch["id"]) in applied else result["unapplied"]).append(ch)
    if (result["changes"] or result["counts_updated"]) and not dry_run:
        text = "\n".join(lines) + ("\n" if original.endswith("\n") else "")
        index_path.write_text(text, encoding="utf-8")
    return result


# --- File-owned index-cell projection ----------------------------------------
# The index displays per-row fields the FILE owns - Title and Points. `detect`/`apply`
# above sync only Status + counts, so these drift and must be hand-copied (the audited
# story-points read-back). Project them from the file too, so the index is fully derived
# (LL0001). Persona is deferred: it has no single canonical field in a story (it lives in
# prose), so projecting it would risk the value-clobber class.
_POINTS_RE = re.compile(r"\*\*(?:Story )?Points:\*\*\s*([0-9]+)", re.IGNORECASE)
_TITLE_RE = re.compile(r"^#\s+[A-Za-z]+-?\d+:\s*(.+?)\s*$", re.MULTILINE)
_PERSONA_RE = re.compile(r"^>?\s*\*\*Persona:\*\*\s*(.+?)\s*$", re.MULTILINE)  # canonical field


def _file_field_values(text: str) -> dict:
    t = _TITLE_RE.search(text)
    p = _POINTS_RE.search(text)
    pe = _PERSONA_RE.search(text)
    return {"title": t.group(1).strip() if t else None,
            "points": p.group(1) if p else None,
            "persona": pe.group(1).strip() if pe else None}


def project_fields(repo_root: Path | str, type_: str = "story", dry_run: bool = True) -> dict:
    """Sync the index's file-owned cells (Title, Points, Persona) from the backing files.

    Detect-or-apply by the same discipline as status. A field absent in the file leaves the
    cell untouched (never blank a value an operator set). Columns are located by the
    data-table header, so an off-schema layout is skipped, not clobbered. Returns
    {drift: [{id, field, index, file}], applied: n}."""
    root = Path(repo_root)
    index_path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    if not index_path.exists():
        return {"drift": [], "applied": 0}
    fvals: dict = {}
    for path in sdlc_md.artifact_files(type_, root):
        rec = sdlc_md.extract_record_id(path.stem)
        if rec:
            fvals[_norm_id(rec)] = _file_field_values(path.read_text(encoding="utf-8"))
    original = index_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    cols: dict = {}
    drift: list = []
    changed = False
    for i, line in enumerate(lines):
        cells = _table_cells(line)
        if not cells:
            continue
        lowered = [c.strip().lower() for c in cells]
        if "id" in lowered and ("title" in lowered or "points" in lowered):  # re-pin per header
            cols = {n: lowered.index(n) for n in ("id", "title", "points", "persona") if n in lowered}
            continue
        if "id" not in cols or cols["id"] >= len(cells):
            continue
        m = sdlc_md.ID_SEARCH_RE.search(cells[cols["id"]])
        if not m:
            continue
        fv = fvals.get(_norm_id(m.group(0)))
        if not fv:
            continue
        row_changed = False
        for field in ("title", "points", "persona"):
            if field in cols and cols[field] < len(cells) and fv[field] is not None:
                cur = cells[cols[field]].strip()
                if cur != fv[field]:
                    drift.append({"id": m.group(0), "field": field, "index": cur, "file": fv[field]})
                    cells[cols[field]] = fv[field]
                    row_changed = True
        if row_changed:
            lines[i] = _join_row(cells)
            changed = True
    if changed and not dry_run:
        index_path.write_text("\n".join(lines) + ("\n" if original.endswith("\n") else ""),
                              encoding="utf-8")
    return {"drift": drift, "applied": len(drift) if (changed and not dry_run) else 0}


def cmd_fields(args: argparse.Namespace) -> int:
    """Project file-owned index cells (title/points); --apply writes, default reports."""
    r = project_fields(args.root, args.type, dry_run=not args.apply)
    if args.format == "json":
        print(json.dumps(r, indent=2))
        return 0
    for d in r["drift"]:
        verb = "set" if args.apply else "WOULD set"
        print(f"{verb} {d['id']} {d['field']}: {d['index']!r} -> {d['file']!r}")
    print(f"fields: {len(r['drift'])} drift{' (applied)' if args.apply else ''}")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    """Apply mechanical index fixes (status cells + summary counts); --dry-run reports only."""
    repo_root = Path(args.root).resolve()
    types = SCOPE_TYPES.get(args.scope, _DEFAULT_TYPES) if args.scope else _DEFAULT_TYPES
    n = 0
    unapplied = 0
    for type_ in types:
        res = apply_type(type_, repo_root, dry_run=args.dry_run)
        for c in res["changes"]:
            print(f"{'WOULD set' if args.dry_run else 'set'} {type_} {c['id']}: {c['from']} -> {c['to']}")
            n += 1
        if res["counts_updated"]:
            print(f"{'WOULD recompute' if args.dry_run else 'recomputed'} {type_} summary counts")
        for u in res["unapplied"]:
            # fail loud: a status the writer could not place in the row (off-schema/header-less)
            # is reported as needing a hand-edit, never as a landed change.
            print(f"WARNING: could not apply {type_} {u['id']}: {u['from']} -> {u['to']} "
                  "- row not in a rewritable layout; edit it by hand", file=sys.stderr)
            unapplied += 1
    print(f"apply: {'would change' if args.dry_run else 'changed'} {n} row(s)"
          + (f", {unapplied} could not be applied" if unapplied else "")
          + (" [dry-run]" if args.dry_run else ""))
    return 1 if unapplied else 0


_SEP_LINE_RE = re.compile(r"\|[\s:|-]*-[\s:|-]*\|")  # a `| --- | --- |` table separator


def _is_sep_line(line: str) -> bool:
    """A markdown table separator row. `table_cells` returns None for these, so the
    archive parser must recognise them from the raw line to stay 'in table'."""
    return bool(_SEP_LINE_RE.fullmatch(line.strip()))


def _line_id(line: str) -> str | None:
    m = sdlc_md.ID_SEARCH_RE.search(line)
    return m.group(0) if m else None


def archive_plan(type_: str, repo_root: Path | str) -> dict | None:
    """Compute which terminal rows to relocate from `<type>/_index.md` to the archive
    sub-index. Returns {move, keep_text, archive_text, archive_path, index_path} or None
    when there is no index or nothing terminal to move (idempotent no-op). Raises
    ValueError on a data row whose status is not in the vocab - fail loud, never
    silently drop or misfile a row (LL0008)."""
    root = Path(repo_root)
    rel = sdlc_md.ARTIFACT_TYPES[type_][0]
    index_path = root / rel / "_index.md"
    if not index_path.exists():
        return None
    vocab = sdlc_md.status_vocab(type_, root)
    terminal = sdlc_md.terminal_statuses(type_)
    if not terminal:
        return None
    original = index_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    status_col = id_col = None
    header = sep = None
    in_table = False
    keep: list[str] = []
    move: list[str] = []
    for line in lines:
        cells = _table_cells(line)
        if cells is None:  # separators (table_cells returns None) and prose/blanks
            if in_table and _is_sep_line(line):
                if sep is None:
                    sep = line
                keep.append(line)
                continue
            in_table = False
            keep.append(line)
            continue
        lowered = [c.strip().lower() for c in cells]
        if len(cells) > 2 and "status" in lowered and "id" in lowered:  # data-table header
            status_col, id_col = lowered.index("status"), lowered.index("id")
            header, in_table = line, True
            keep.append(line)
            continue
        if in_table and id_col is not None and id_col < len(cells) and _line_id(cells[id_col]):
            raw = cells[status_col].strip() if status_col is not None and status_col < len(cells) else ""
            status = _canonical_status(raw, vocab)
            if status is None:
                raise ValueError(
                    f"{type_} index row {_line_id(cells[id_col])}: status {raw!r} is not a "
                    f"{type_} status - refusing to archive (fix the row first)")
            (move if status in terminal else keep).append(line)
            continue
        keep.append(line)  # summary rows, prose, blanks
    if not move or header is None or sep is None:
        return None
    moved_ids = {_line_id(m) for m in move}
    archive_path = root / rel / "archive" / "_index.md"
    prior_rows: list[str] = []
    if archive_path.exists():
        for line in archive_path.read_text(encoding="utf-8").splitlines():
            cells = _table_cells(line)
            if (cells and len(cells) > 2
                    and "status" not in [c.strip().lower() for c in cells]
                    and _line_id(line) and _line_id(line) not in moved_ids):
                prior_rows.append(line)
    title = type_.replace("-", " ").title()
    archive_rows = prior_rows + move
    archive_text = f"# {title} Archive Index\n\n{header}\n{sep}\n" + "\n".join(archive_rows) + "\n"
    keep_text = "\n".join(keep) + ("\n" if original.endswith("\n") else "")
    return {"move": move, "keep_text": keep_text, "archive_text": archive_text,
            "archive_path": archive_path, "index_path": index_path}


def archive_type(type_: str, repo_root: Path | str, dry_run: bool = False) -> dict:
    """Relocate `type_`'s terminal index rows to the archive sub-index. Validates the
    whole index (fail loud) before any write, so a bad row aborts with no partial state."""
    plan = archive_plan(type_, repo_root)
    if plan is None:
        return {"type": type_, "moved": 0, "archive": None}
    if not dry_run:
        plan["archive_path"].parent.mkdir(parents=True, exist_ok=True)
        plan["archive_path"].write_text(plan["archive_text"], encoding="utf-8")
        plan["index_path"].write_text(plan["keep_text"], encoding="utf-8")
    return {"type": type_, "moved": len(plan["move"]),
            "archive": str(plan["archive_path"].relative_to(Path(repo_root))),
            "ids": [_line_id(m) for m in plan["move"]]}


def cmd_archive(args: argparse.Namespace) -> int:
    """Relocate terminal index rows to per-type archive sub-indexes; --dry-run reports only."""
    repo_root = Path(args.root).resolve()
    types = [args.type] if args.type else (
        SCOPE_TYPES.get(args.scope, _DEFAULT_TYPES) if args.scope else _DEFAULT_TYPES)
    results = []
    try:
        for type_ in types:
            results.append(archive_type(type_, repo_root, dry_run=args.dry_run))
    except ValueError as e:  # fail loud: no partial write across the sweep
        print(f"error: {e}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(results, indent=2))
        return 0
    total = 0
    for r in results:
        if r["moved"]:
            verb = "WOULD archive" if args.dry_run else "archived"
            print(f"{verb} {r['moved']} {r['type']} row(s) -> {r['archive']}: {', '.join(r['ids'])}")
            total += r["moved"]
    print(f"archive: {'would move' if args.dry_run else 'moved'} {total} row(s)"
          + (" [dry-run]" if args.dry_run else ""))
    return 0


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
    d.add_argument("--blocker-sweep", action="store_true",
                   help="Advisory lane: also report now-unblocked / stale-blocked units")
    d.set_defaults(func=cmd_detect)
    a = sub.add_parser("apply", help="Apply mechanical index fixes (status cells + counts).")
    a.add_argument("--scope", choices=sorted(SCOPE_TYPES), help="Limit to one scope")
    a.add_argument("--root", default=".", help="Repo root (default: .)")
    a.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    a.set_defaults(func=cmd_apply)
    fi = sub.add_parser("fields", help="Project file-owned index cells (title/points).")
    fi.add_argument("--type", default="story", help="Artifact type (default: story)")
    fi.add_argument("--apply", action="store_true", help="Write the cells (default: report only)")
    fi.add_argument("--root", default=".", help="Repo root (default: .)")
    fi.add_argument("--format", choices=("text", "json"), default="text")
    fi.set_defaults(func=cmd_fields)
    ar = sub.add_parser("archive", help="Relocate terminal index rows to archive sub-indexes.")
    ar.add_argument("--type", help="Single artifact type (default: all index-driven types)")
    ar.add_argument("--scope", choices=sorted(SCOPE_TYPES), help="Limit to one scope")
    ar.add_argument("--root", default=".", help="Repo root (default: .)")
    ar.add_argument("--dry-run", action="store_true", help="Report the relocation without writing")
    ar.add_argument("--format", choices=("text", "json"), default="text")
    ar.set_defaults(func=cmd_archive)
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
