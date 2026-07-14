#!/usr/bin/env python3
"""SDLC Studio reconcile: census-based drift detection and mechanical repair.

Builds the file census doctrine rule 3 prescribes - artifact files are the
truth, `_index.md` tables are derived - and reports where the indexes have
drifted. Three drift classes per type: status mismatch (file vs index row),
missing row (a file with no index row), and orphan row (an index row with no
file), plus summary-count drift.

Subcommands:
  detect   Census + drift report as JSON/text (READ-ONLY).
  apply    Rewrite drifted status cells, append missing rows, recompute counts (WRITES the index).
  fields   Project file-owned index cells (title/points); `--apply` writes.

Only `detect` is read-only; the judgement calls (orphan-row removal, checkbox/
dependency/PRD-feature drift, CR cascades, changelog) stay with the agent.

Index archival lives in `archive.py` - the single archive writer. This module owns only
the shared read helper it calls (`master_terminal_rows`).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import conventions, sdlc_md  # noqa: E402

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
    "meta": [],  # retros/ + reviews/ are checked by meta_index_drift, not the pipeline detectors
}
DEFAULT_TYPES = ["story", "epic", "cr", "rfc", "plan", "test-spec", "bug", "workflow"]

# Every drift kind this module can emit into a report's `by_kind`, which feeds
# sdlc_md.remediation_lines("reconcile", ...). This is reconcile's finding-kind
# vocabulary and the single source of truth for it: the remediation registry
# (sdlc_md.REMEDIATION["reconcile"]) must carry a hint for each, a guard derives its
# expected key set from this tuple (so a new kind without a hint reddens the guard),
# and a sibling test asserts this tuple matches the kinds actually emitted in source
# (so the tuple itself cannot silently drift from the detectors). Keep it in step with
# the `"kind":` literals in the detectors below.
DRIFT_KINDS = (
    "missing-index",
    "index-status-column",
    "missing-row",
    "status-mismatch",
    "orphan-row",
    "count-mismatch",
    "breakdown-unticked",
    "breakdown-ticked-early",
)

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


# Legacy vocabulary header (no separator line under it): >2 cells, one of them
# a bare `Status`. Passed to sdlc_md.iter_tables as the header_predicate.
def _vocab_header(aliases: tuple = ()) -> callable:
    """Header predicate: a 3+-cell row naming the status column - exactly
    'Status', or a project-declared alias (conventions.status_column)."""
    def pred(cells: list) -> bool:
        low = [c.lower() for c in cells]
        return len(cells) > 2 and ("status" in low or any(a in low for a in aliases))
    return pred


_VOCAB_HEADER = _vocab_header()  # the unconfigured default


# Alias: the canonical separator regex now lives in sdlc_md (shared by every parser).
_SEP_ROW_RE = sdlc_md.SEP_ROW_RE


def _index_rows_and_summary(text: str, vocab: list,
                            aliases: tuple = ()) -> tuple[dict, dict]:
    """Parse one index file's table rows into ({norm_id: (disp, status)}, {status: count}).

    The Status (and ID) columns are located by each table's **header row**
    (structural: a `|`-row followed by its `| --- |` separator; a vocabulary
    header without a separator still re-pins) and read positionally. A table
    whose header declares NO Status column - the shipped cr.md Dependencies
    table - asserts nothing about status: its rows never overwrite a status
    parsed from a real status table (the `Dependency Status` cell of
    `| CR-0001 | CR-0003 | Complete |` is about CR-0003, not CR-0001). The
    first-matching-cell fallback fires only for header-less blocks and for
    off-schema rows inside a status-column table.
    """
    rows: dict = {}
    summary: dict = {}
    for tbl in sdlc_md.iter_tables(text, header_predicate=_vocab_header(aliases)):
        has_header = tbl["header"] is not None
        lowered = [c.lower() for c in tbl["header"]] if has_header else []
        status_col = next((i for i, c in enumerate(lowered)
                           if c == "status" or c in aliases), None)
        id_col = lowered.index("id") if "id" in lowered else None
        for _ln, cells in tbl["rows"]:
            if len(cells) == 2 and cells[1].replace(",", "").isdigit():  # `| <Status> | <int> |`
                label = _canonical_status(cells[0], vocab)
                if label:
                    summary[label] = int(cells[1].replace(",", ""))
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
            if row_status is None and (not has_header or status_col is not None):
                # header-less block, or a status-column table whose pinned cell is
                # off-schema: find the status by canonical-vocab token. A table
                # that declares no Status column is never scavenged.
                row_status = next((cs for c in cells if (cs := _canonical_status(c, vocab))), None)
            if row_id:
                key = _norm_id(row_id)
                if row_status is not None or key not in rows:
                    rows[key] = (row_id, row_status or "Unknown")
    return rows, summary


def _status_header_diagnosis(text: str, aliases: tuple = ()) -> tuple[bool, str | None]:
    """(does any data table pin an exact Status column?, first status-like
    mis-named header cell otherwise). A project-declared alias counts as exact.

    Only tables with 3+ header cells count - the 2-cell `| Status | Count |`
    summary table says nothing about the data table's schema."""
    has_exact = False
    candidate = None
    for tbl in sdlc_md.iter_tables(text, header_predicate=_vocab_header(aliases)):
        header = tbl["header"]
        if header is None or len(header) < 3 or not tbl["rows"]:
            continue
        low = [c.lower() for c in header]
        if "status" in low or any(a in low for a in aliases):
            has_exact = True
        elif candidate is None:
            candidate = next((c for c in header if "status" in c.lower()), None)
    return has_exact, candidate


def _degenerate_status_parse(index: dict) -> str | None:
    """When every parsed row is Unknown and no data table pins an exact Status
    column, the index has ONE structural defect (a mis-named or absent Status
    header) - not N status drifts. Returns the diagnostic text, else None."""
    rows = index.get("rows") or {}
    if not rows or any(st != "Unknown" for _d, st in rows.values()):
        return None
    has_exact, cand = index.get("status_header") or (True, None)
    if has_exact:
        return None
    n = len(rows)
    if cand:
        return (f"no index table declares an exact 'Status' column, so all {n} "
                f"row(s) parse as Unknown. Header '{cand}' looks like the status "
                f"column - rename it to 'Status', or declare it in "
                f"sdlc-studio/.config.yaml under conventions.status_column")
    return (f"no index table declares an exact 'Status' column, so all {n} "
            f"row(s) parse as Unknown - rename your status header to 'Status', "
            f"declare it in sdlc-studio/.config.yaml under "
            f"conventions.status_column, or add a Status column")


def index_row_ids(text: str) -> list[str]:
    """Every data-row normalised id in one index file, in order, duplicates kept.

    Mirrors `_index_rows_and_summary`'s header-pinned id location, but returns the raw
    sequence (not a {id: ...} dict) so duplicate rows are visible rather than collapsed.
    """
    ids: list[str] = []
    for table in sdlc_md.iter_tables(text, header_predicate=_VOCAB_HEADER):
        lowered = [c.lower() for c in table["header"]] if table["header"] else []
        id_col = lowered.index("id") if "id" in lowered else None
        for _ln, cells in table["rows"]:
            if len(cells) == 2 and cells[1].replace(",", "").isdigit():  # summary row
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
    silently collapses. The table boundary is STRUCTURAL - any header row (a `|`-row
    immediately followed by its `| --- |` separator) flushes and resets the tally -
    never vocabulary-based: the shipped cr.md Dependencies header carries
    `Dependency Status`, not a bare `Status` cell, so a vocabulary match tallied its
    rows into the previous table's scope and a fully-templated project failed its own
    gate. Returns {id: count} only for ids whose within-table count > 1.
    """
    best: dict[str, int] = {}
    for tbl in sdlc_md.iter_tables(text, header_predicate=_VOCAB_HEADER):
        lowered = [c.lower() for c in tbl["header"]] if tbl["header"] else []
        id_col = lowered.index("id") if "id" in lowered else None
        counts: dict[str, int] = {}
        for _ln, cells in tbl["rows"]:
            if len(cells) == 2 and cells[1].replace(",", "").isdigit():  # summary row
                continue
            if id_col is not None and id_col < len(cells):
                m = sdlc_md.ID_SEARCH_RE.search(cells[id_col])
                rid = m.group(0) if m else None
            else:
                rid = next((sdlc_md.ID_SEARCH_RE.search(c).group(0)
                            for c in cells if sdlc_md.ID_SEARCH_RE.search(c)), None)
            if rid:
                k = _norm_id(rid)
                counts[k] = counts.get(k, 0) + 1
        for rid, n in counts.items():
            if n > best.get(rid, 0):
                best[rid] = n
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
    aliases = tuple(conventions.status_aliases(repo_root))
    text = index_path.read_text(encoding="utf-8")
    rows, summary = _index_rows_and_summary(text, vocab, aliases)
    result["summary"] = summary
    result["rows"] = rows
    result["status_header"] = _status_header_diagnosis(text, aliases)
    # Degeneracy is a property of the LIVE index, judged before the archive
    # census merge - one healthy archived row must not mask a mis-named live
    # Status column (the storm and a non-refusing apply would return).
    result["degenerate"] = _degenerate_status_parse(
        {"rows": rows, "status_header": result["status_header"]})
    # Live terminal-row count, also pre-merge: the index-bloat advisory is
    # about the table an agent actually loads, so archived rows never count.
    terminal = sdlc_md.terminal_statuses(type_)
    result["live_terminal_rows"] = sum(
        1 for _d, st in rows.values() if st in terminal)
    archive_dir = repo_root / rel / "archive"
    if archive_dir.is_dir():  # archived terminal rows still count toward the census
        for af in sorted(archive_dir.rglob("*.md")):
            arows, _ = _index_rows_and_summary(af.read_text(encoding="utf-8"), vocab, aliases)
            for k, v in arows.items():
                # a LIVE row always wins: an archive row only fills in an id absent from the
                # live index. Otherwise a reopened (archived-then-live-again) artefact is
                # permanently shadowed by its stale archive status - un-clearable drift.
                if k not in result["rows"]:
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


DEFAULT_ARCHIVE_AFTER = 30  # live terminal rows before the archive advisory fires


def index_bloat_advisory(type_: str, repo_root: Path,
                         index: dict | None = None) -> str | None:
    """Recommend the progressive-disclosure archive when the LIVE index carries
    more terminal rows than `indexes.archive_after` (config-overridable).
    Advisory only: it never blocks and never runs the archive - rows move only
    when the operator runs archive.py."""
    index = index if index is not None else parse_index(type_, repo_root)
    n = index.get("live_terminal_rows", 0)
    try:
        threshold = int(sdlc_md.project_override(
            repo_root, "indexes.archive_after", DEFAULT_ARCHIVE_AFTER))
    except (TypeError, ValueError):
        threshold = DEFAULT_ARCHIVE_AFTER
    if n <= threshold:
        return None
    rel = sdlc_md.ARTIFACT_TYPES[type_][0]
    return (f"{n} terminal row(s) in the live {type_} index (> {threshold}, "
            f"indexes.archive_after) - keep it bounded: "
            f"scripts/archive.py archive --type {type_} --release <label> "
            f"(rows move to {rel}/archive/, files stay put, census unaffected)")


def digest_drift_advisory(repo_root: Path | str) -> str | None:
    """Advisory (never blocks): when a closed-artefact digest exists but no longer matches the
    census (a closed artefact added or changed since it was written), recommend regenerating it -
    the same drift discipline as the progressive-disclosure indexes. Returns None when there is no
    digest or it is fresh."""
    import digest as _digest
    if _digest.load(repo_root) is None:
        return None
    if not _digest.is_stale(repo_root):
        return None
    return ("the closed-artefact digest is stale (a closed artefact changed since it was "
            "written) - regenerate it: scripts/digest.py build")


def _census_row_drift(type_, census, rows, filenames, vocab, degenerate) -> list[dict]:
    """Per-file drift: a census file missing its index row, or a file/index status mismatch."""
    out: list[dict] = []
    for norm, (disp, fstatus) in sorted(census.items()):
        if norm not in rows:
            fname = filenames.get(norm)
            out.append({"type": type_, "id": disp, "kind": "missing-row",
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
            if not degenerate and fcanon is not None and fcanon != target:
                out.append({"type": type_, "id": disp, "kind": "status-mismatch",
                            "file_status": fstatus, "index_status": istatus,
                            "fix": f"set index status of {disp} to {fstatus}"})
    return out


def _orphan_row_drift(type_, census, rows, vocab) -> list[dict]:
    """A live index row whose status implies a backing file, but none exists."""
    out: list[dict] = []
    for norm, (disp, istatus) in sorted(rows.items()):
        if norm not in census:
            icanon = _canonical_status(istatus, vocab)
            # A row whose status doesn't imply a file yet (Proposed/Draft/…) or
            # is a custom retirement (non-vocabulary) is an intentional
            # reservation, not an orphan — don't flag it.
            if icanon is None or icanon in _NO_FILE_EXPECTED:
                continue
            out.append({"type": type_, "id": disp, "kind": "orphan-row",
                        "file_status": None, "index_status": istatus,
                        "fix": f"remove orphan index row {disp} (no backing file)"})
    return out


def _row_counts(rows, vocab) -> dict[str, int]:
    """Canonical tally of the index ROWS (the authority the summary table summarises)."""
    counts: dict[str, int] = {}
    for _disp, istatus in rows.values():
        rc = _canonical_status(istatus, vocab)
        if rc is not None:
            counts[rc] = counts.get(rc, 0) + 1
    return counts


def _count_mismatch_drift(type_, census, index, row_counts, vocab, degenerate) -> list[dict]:
    """Summary-vs-rows count drift. The summary table summarises the INDEX ROWS, so it is checked
    against the row tally (not the file census) - the right authority for types whose files carry
    no status field (e.g. CRs); per-row file-vs-index drift is caught by status-mismatch."""
    mismatches = [
        {"status": st, "rows": row_counts.get(st, 0), "summary": index["summary"].get(st, 0)}
        for st in sorted(set(index["summary"]) | set(row_counts))
        if index["summary"].get(st, 0) != row_counts.get(st, 0)
    ]
    if not (bool(index["summary"]) and mismatches and not degenerate):
        return []
    # The finding carries its own diagnosis (the mismatched tokens with both
    # numbers) and, when out-of-vocab statuses are the cause, the offending
    # status + carriers + the config remedy - a generic "recompute" hint for a
    # vocab problem is a dead end that apply cannot clear.
    out_of_vocab: dict[str, list[str]] = {}
    for disp, fstatus in sorted(census.values()):
        if fstatus and _canonical_status(fstatus, vocab) is None:
            out_of_vocab.setdefault(fstatus, []).append(disp)
    detail = ", ".join(f"{m['status']} rows={m['rows']} summary={m['summary']}"
                       for m in mismatches)
    if out_of_vocab:
        named = "; ".join(
            f"status '{st}' on {', '.join(ids)} is not in status_vocab.{type_}"
            for st, ids in sorted(out_of_vocab.items()))
        fix = (f"{detail}. Likely cause: {named} - declare it in "
               f"sdlc-studio/.config.yaml under status_vocab.{type_} "
               f"(see reference-config.md), or diagnose with scripts/validate.py check")
    else:
        fix = (f"{detail}. All statuses are in-vocab (stale arithmetic) - "
               f"recompute the summary counts from the index rows")
    return [{"type": type_, "id": None, "kind": "count-mismatch",
             "file_status": None, "index_status": None,
             "mismatches": mismatches,
             "out_of_vocab": out_of_vocab or None,
             "fix": fix}]


def _census_counts(census, vocab) -> dict[str, int]:
    """File-census tally kept for information (status distribution on disk)."""
    counts: dict[str, int] = {}
    for _disp, fstatus in census.values():
        key = _canonical_status(fstatus, vocab) or "Unknown"
        counts[key] = counts.get(key, 0) + 1
    return counts


def detect_type(type_: str, repo_root: Path) -> dict:
    """Compute drift for one type by composing the per-concern drift detectors."""
    census = file_census(type_, repo_root)
    index = parse_index(type_, repo_root)
    filenames = _census_filenames(type_, repo_root)
    vocab = sdlc_md.status_vocab(type_, repo_root)
    rows = index["rows"]
    # A whole-index degenerate parse (mis-named/absent Status column) is one
    # structural defect: name it once and suppress the per-row mismatch storm
    # and the count-mismatch misdiagnosis it would otherwise fabricate.
    degenerate = index.get("degenerate")

    drift: list[dict] = []
    if census and not index["exists"]:
        drift.append({
            "type": type_, "id": None, "kind": "missing-index",
            "file_status": None, "index_status": None,
            "fix": f"create {sdlc_md.ARTIFACT_TYPES[type_][0]}/_index.md from the {len(census)} files",
        })
    if degenerate:
        drift.append({"type": type_, "id": None, "kind": "index-status-column",
                      "file_status": None, "index_status": None, "fix": degenerate})

    drift += _census_row_drift(type_, census, rows, filenames, vocab, degenerate)
    drift += _orphan_row_drift(type_, census, rows, vocab)
    row_counts = _row_counts(rows, vocab)
    drift += _count_mismatch_drift(type_, census, index, row_counts, vocab, degenerate)

    bloat = index_bloat_advisory(type_, repo_root, index)
    return {
        "census_total": len(census),
        "census_counts": _census_counts(census, vocab),
        "row_counts": row_counts,
        "index_exists": index["exists"],
        "index_summary": index["summary"],
        "drift": drift,
        "advisories": [bloat] if bloat else [],
    }


# -----------------------------------------------------------------------------
# Meta-index coverage (retros/, reviews/)
#
# These indexes carry house columns (Sprint/Delivered/Blocked, or Title/Date) and NO
# Status column or count-summary block, so the pipeline reconcile above - which pins the
# data table by its Status header and rewrites status cells - cannot own them. This lane
# checks row PRESENCE only: every numbered RETRO/RV file has an index row and every row a
# backing file. It keys on the meta id namespace (RETRO/RV), which the pipeline id regexes
# deliberately exclude, so it needs its own extractor rather than `index_row_ids`.
# -----------------------------------------------------------------------------
_META_INDEX = {  # mirrors next_id.META_TYPES; kept local to avoid a reconcile->next_id import
    "retro": ("sdlc-studio/retros", "RETRO"),
    "review": ("sdlc-studio/reviews", "RV"),
    "handoff": ("sdlc-studio/handoffs", "HO"),
}


def meta_census(type_: str, repo_root: Path | str) -> dict[str, str]:
    """{normalised_id: display_id} for the numbered artefact files of a meta type. Only
    `PREFIX<digits>-...md` stems count - LATEST.md, review prompts and rehearsal notes living
    alongside are not numbered artefacts and are skipped."""
    rel, prefix = _META_INDEX[type_]
    d = Path(repo_root) / rel
    pat = re.compile(rf"^{re.escape(prefix)}0*(\d+)-")
    out: dict[str, str] = {}
    for p in (sorted(d.glob(f"{prefix}*.md")) if d.is_dir() else []):
        m = pat.match(p.stem)
        if m:
            n = int(m.group(1))
            out[f"{prefix}{n:04d}"] = f"{prefix}-{n:04d}"
    return out


def _meta_index_row_ids(text: str, prefix: str) -> list[str]:
    """Normalised meta ids from the index's data table(s), located by an ID-column header
    (the meta indexes have no Status column, so `_VOCAB_HEADER` never matches them)."""
    idre = re.compile(rf"{re.escape(prefix)}-?0*(\d+)")
    ids: list[str] = []
    for tbl in sdlc_md.iter_tables(
            text, header_predicate=lambda cells: any(c.strip().lower() == "id" for c in cells)):
        lowered = [c.strip().lower() for c in tbl["header"]] if tbl["header"] else []
        if "id" not in lowered:
            # iter_tables yields EVERY separator table, not only ID tables. Confine the lane
            # to the ID-bearing table so a future summary/second table whose prose happens to
            # match RV-?0*\d+ cannot phantom a row (which would mask a real drift item).
            continue
        id_col = lowered.index("id")
        for _ln, cells in tbl["rows"]:
            if id_col >= len(cells):
                continue
            m = idre.search(cells[id_col])
            if m:
                ids.append(f"{prefix}{int(m.group(1)):04d}")
    return ids


def meta_index_drift(repo_root: Path | str) -> list[dict]:
    """Row-presence drift for the meta indexes (retros/, reviews/): a numbered file with no
    index row, an index row with no backing file, or a wholly missing index. Same drift-dict
    shape as the pipeline detectors, so items slot straight into the report's `drift` list."""
    root = Path(repo_root)
    drift: list[dict] = []
    for type_ in _META_INDEX:
        rel, prefix = _META_INDEX[type_]
        census = meta_census(type_, root)
        index_path = root / rel / "_index.md"
        if not index_path.exists():
            if census:
                drift.append({"type": type_, "id": None, "kind": "missing-index",
                              "file_status": None, "index_status": None,
                              "fix": f"create {rel}/_index.md from the {len(census)} {prefix} files"})
            continue
        rows = set(_meta_index_row_ids(index_path.read_text(encoding="utf-8"), prefix))
        for norm, disp in sorted(census.items()):
            if norm not in rows:
                drift.append({"type": type_, "id": disp, "kind": "missing-row",
                              "file_status": None, "index_status": None,
                              "fix": f"add {disp} to {rel}/_index.md (artifact new --type {type_})"})
        for norm in sorted(rows):
            if norm not in census:
                disp = f"{prefix}-{norm[len(prefix):]}"
                drift.append({"type": type_, "id": disp, "kind": "orphan-row",
                              "file_status": None, "index_status": None,
                              "fix": f"remove orphan {disp} row from {rel}/_index.md (no backing file)"})
    return drift


def _meta_row_fields(path: Path) -> tuple[str, str]:
    """(title, date) for a meta index append: title from the file's H1 (leading id/prefix
    stripped), date from a `> **Date:**` field or the first ISO date in the stem, else '--'."""
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    title = path.stem
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        title = re.sub(r"^(?:RV|RETRO|HO)[-\s:]*\d+\s*[-:]\s*", "", m.group(1).strip())
    dm = re.search(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    if dm:
        return title, dm.group(1)
    sm = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    return title, (sm.group(1) if sm else "--")


def apply_meta(repo_root: Path | str, dry_run: bool = False) -> dict:
    """Append a row for each numbered meta file missing from its index (retros/, reviews/),
    header-driven so the house column order is honoured. Orphan rows and a wholly missing
    index stay report-only - deleting history or fabricating a whole index is a judgement
    call, never mechanical. Returns {appended, missing_unapplied}."""
    root = Path(repo_root)
    result: dict = {"appended": [], "missing_unapplied": []}
    for type_ in _META_INDEX:
        rel, prefix = _META_INDEX[type_]
        index_path = root / rel / "_index.md"
        if not index_path.exists():
            continue
        census = meta_census(type_, root)
        lines = index_path.read_text(encoding="utf-8").splitlines()
        rows = set(_meta_index_row_ids("\n".join(lines), prefix))
        missing = [(norm, disp) for norm, disp in sorted(census.items()) if norm not in rows]
        if not missing:
            continue
        hdr = sdlc_md.find_data_header(lines)
        if hdr is None:
            result["missing_unapplied"].extend(disp for _n, disp in missing)
            continue
        changed = False
        for norm, disp in missing:
            n = int(norm[len(prefix):])
            matches = sorted((root / rel).glob(f"{prefix}{n:04d}-*.md"))
            if not matches:
                result["missing_unapplied"].append(disp)
                continue
            title, date_s = _meta_row_fields(matches[0])
            row = sdlc_md.row_from_header(hdr[1], f"[{disp}]({matches[0].name})", title,
                                          "--", {"date": date_s})
            pos = hdr[0] + 2  # past header + separator
            while pos < len(lines) and lines[pos].strip().startswith("|"):
                pos += 1
            lines.insert(pos, row)
            result["appended"].append(disp)
            changed = True
        if changed and not dry_run:
            sdlc_md.atomic_write(index_path, "\n".join(lines) + "\n")
    return result


# -----------------------------------------------------------------------------
# Epic Story Breakdown checkboxes (every unit type, not only stories)
#
# The live cascade (transition._cascade_epic) ticks a STORY's box via its `Epic` field;
# bugs and CRs listed in a breakdown have no such field, so their boxes were invisible to
# both the cascade and this census - an epic could read Done over a breakdown that
# contradicted its units. This lane compares each checkbox against its unit's
# terminal-ness (the shared sdlc_md.terminal_statuses authority). A line whose id resolves
# to no file (a founding-epic placeholder stub) is skipped, and a `Deferred` unit is
# exempt in both directions (re-activatable: neither box state is provably wrong).
# -----------------------------------------------------------------------------
_BREAKDOWN_BOX_RE = re.compile(r"^\s*- \[( |x|X)\]\s")


_BREAKDOWN_HEADING_RE = re.compile(r"^#{2,3}\s+.*breakdown", re.IGNORECASE)


def _breakdown_units(root: Path, text: str):
    """Yield (lineno, ticked, unit_id, unit_type, canonical_status) for each resolvable
    checkbox line INSIDE the epic's Story Breakdown section only. An epic body carries
    other id-bearing checkboxes (Definition of Done items, acceptance criteria, open
    questions - all template-endorsed), and syncing those to a unit's status would tick
    work that was never done; the lane is scoped to the breakdown, where a box means
    exactly 'this unit is delivered'. A unit file with no Status field asserts nothing
    and is skipped (mirrors the census rule)."""
    in_breakdown = False
    for i, ln in enumerate(text.splitlines()):
        if ln.lstrip().startswith("#"):
            in_breakdown = bool(_BREAKDOWN_HEADING_RE.match(ln.strip()))
            continue
        if not in_breakdown:
            continue
        m = _BREAKDOWN_BOX_RE.match(ln)
        if not m:
            continue
        idm = sdlc_md.ID_SEARCH_RE.search(ln)
        if not idm:
            continue
        hit = sdlc_md.find_by_id(root, idm.group(0))
        if not hit:
            continue  # placeholder stub - no backing file, nothing to compare
        upath, utype = hit
        raw = (sdlc_md.extract_field(upath.read_text(encoding="utf-8"), "Status") or "").strip()
        if not raw:
            continue  # no Status field: the unit asserts nothing to compare against
        canon = _canonical_status(raw, sdlc_md.STATUS_VOCAB.get(utype, [])) or raw
        yield i, m.group(1) in ("x", "X"), idm.group(0), utype, canon


def epic_breakdown_drift(repo_root: Path | str) -> list[dict]:
    """Checkbox drift across every epic's Story Breakdown: a terminal unit behind an
    unchecked box (`breakdown-unticked`), or a checked box over a live unit
    (`breakdown-ticked-early` - the direction that masks unfinished work)."""
    root = Path(repo_root)
    drift: list[dict] = []
    for epath in sdlc_md.artifact_files("epic", root):
        text = epath.read_text(encoding="utf-8")
        eid = sdlc_md.extract_record_id(epath.stem) or epath.stem
        for _ln, ticked, uid, utype, canon in _breakdown_units(root, text):
            if canon == "Deferred":
                continue
            terminal = sdlc_md.is_terminal_status(utype, canon)
            if terminal and not ticked:
                drift.append({"type": "epic", "id": uid, "kind": "breakdown-unticked",
                              "file_status": canon, "index_status": None,
                              "fix": f"tick {uid} ({canon}) in {eid}'s breakdown"})
            elif ticked and not terminal:
                drift.append({"type": "epic", "id": uid, "kind": "breakdown-ticked-early",
                              "file_status": canon, "index_status": None,
                              "fix": f"untick {uid} ({canon}) in {eid}'s breakdown - "
                                     f"a checked box over a live unit masks unfinished work"})
    return drift


def apply_breakdown(repo_root: Path | str, dry_run: bool = False) -> dict:
    """Mechanically sync every epic-breakdown checkbox to its unit's terminal-ness (both
    directions), the same edit the story cascade performs live. Returns {synced: [ids]}."""
    root = Path(repo_root)
    synced: list[str] = []
    for epath in sdlc_md.artifact_files("epic", root):
        text = epath.read_text(encoding="utf-8")
        lines = text.splitlines()
        changed = False
        for i, ticked, uid, utype, canon in _breakdown_units(root, text):
            if canon == "Deferred":
                continue
            want = sdlc_md.is_terminal_status(utype, canon)
            if want != ticked:
                lines[i] = re.sub(r"\[[ xX]\]", "[x]" if want else "[ ]", lines[i], count=1)
                synced.append(uid)
                changed = True
        if changed and not dry_run:
            sdlc_md.atomic_write(epath, "\n".join(lines) + ("\n" if text.endswith("\n") else ""))
    return {"synced": synced}


def era_divergence_advisory(repo_root: Path | str) -> str | None:
    """Warn when this clone's config and the workspace's ids tell different era stories: config
    says schema v2 (sequential ids) but v3 ULID-form ids exist - another user or machine is
    filing on v3, or the local .config.yaml is stale/uncommitted. On a multi-user project two
    writers in different modes WILL diverge (one minting sequential ids the other's era already
    abandoned), so surface it before it happens. The inverse (schema 3 with sequential ids
    present) is normal - a forward-only adopt keeps the old ids - so only this direction warns.
    Advisory only: never drift, never the exit code."""
    root = Path(repo_root)
    if sdlc_md.schema_version(root) >= 3:
        return None
    v3 = [rec for t in sdlc_md.ARTIFACT_TYPES for p in sdlc_md.artifact_files(t, root)
          if (rec := sdlc_md.extract_record_id(p.stem)) and sdlc_md.id_number(rec) is None]
    if not v3:
        return None
    sample = ", ".join(sorted(v3)[:3])
    return (f"era divergence: {len(v3)} v3 ULID-form id(s) exist (e.g. {sample}) but this "
            f"clone's config is schema v2 - another user/machine is filing on v3, or "
            f".config.yaml is stale. Align the era across clones (pull, or "
            f"`migrate_v3.py adopt --confirm` / `apply --confirm`) before writers diverge.")


def cmd_detect(args: argparse.Namespace) -> int:
    """Run drift detection across the selected scope and report."""
    repo_root = Path(args.root).resolve()
    types = SCOPE_TYPES.get(args.scope, DEFAULT_TYPES) if args.scope else DEFAULT_TYPES

    per_type: dict[str, dict] = {}
    all_drift: list[dict] = []
    for type_ in types:
        result = detect_type(type_, repo_root)
        per_type[type_] = result
        all_drift.extend(result["drift"])
    # The meta indexes (retros/, reviews/) run on the default 'all' sweep and on the explicit
    # 'meta' scope, never on a single pipeline scope like 'bugs'.
    if args.scope in (None, "meta"):
        all_drift.extend(meta_index_drift(repo_root))
    # Breakdown checkboxes run on the default sweep and the 'epics' scope (they belong to
    # the epic files even though the drifting unit may be a bug or CR).
    if args.scope in (None, "epics"):
        all_drift.extend(epic_breakdown_drift(repo_root))

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

    digest_note = digest_drift_advisory(repo_root)
    if digest_note:
        report["digest_advisory"] = digest_note
    era_note = era_divergence_advisory(repo_root)
    if era_note:
        report["era_advisory"] = era_note

    if getattr(args, "blocker_sweep", False):
        # advisory lane: report stale-blocked / now-unblocked units. Never affects drift or the
        # exit code - reconcile still succeeds/fails on its own census checks (US0050).
        import blocker_sweep
        try:
            sw = blocker_sweep.sweep(repo_root)
            report["blocker_sweep"] = {"now_unblocked": sw["now_unblocked"],
                                       "still_blocked": sw["still_blocked"], "errors": sw["errors"]}
        except Exception as exc:  # noqa: BLE001 - an advisory lane must never break detect
            sdlc_md.debug("reconcile.blocker_sweep", exc)
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
        for type_, result in per_type.items():
            for a in result.get("advisories", []):
                print(f"advisory ({type_}): {a}")
        if digest_note:
            print(f"advisory (digest): {digest_note}")
        if era_note:
            print(f"advisory (era): {era_note}")
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


def _header_kind(cells: list, lowered: list,
                 aliases: tuple = ()) -> tuple[str | None, int | None, int | None]:
    """Classify a table header row: ('summary'|'data'|None, status_col, id_col).
    A declared alias (conventions.status_column) pins the status column exactly
    as 'Status' does - writer parity with the read side."""
    status_i = next((i for i, c in enumerate(lowered)
                     if c == "status" or c in aliases), None)
    if status_i is None:
        return None, None, None
    if lowered == ["status", "count"]:
        return "summary", None, None
    if len(cells) >= 2:
        return "data", status_i, (lowered.index("id") if "id" in lowered else None)
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


def _rewrite_index_lines(lines: list, fixes: dict, counts: dict, vocab: list,
                         aliases: tuple = ()) -> tuple[bool, set]:
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
        kind, sc, ic = _header_kind(cells, [c.lower() for c in cells], aliases)
        if kind == "summary":
            has_total = False
            for j in range(i + 1, len(lines)):  # scan this block for a Total row
                cj = _table_cells(lines[j])
                if cj is None:
                    if not lines[j].strip().startswith("|"):
                        break  # blank/prose ends the block
                    continue   # separator row
                low_cj = [c.lower() for c in cj]
                if "status" in low_cj or any(a in low_cj for a in aliases):
                    break  # next header - block ended
                if len(cj) == 2 and cj[0].replace("*", "").strip().lower() == "total":
                    has_total = True
                    break
            in_summary, status_col, id_col = (has_total or n_summary == 1), None, None
            continue
        if kind == "data":
            in_summary, status_col, id_col = False, sc, ic
            continue
        # A header row _header_kind cannot classify (a Dependencies/Notes table, say) must
        # RESET the tracked columns - otherwise the previous data table's status_col bleeds
        # forward and clobbers an author-maintained cell that happens to be status-shaped.
        if i + 1 < len(lines) and _SEP_ROW_RE.match(lines[i + 1]):
            in_summary, status_col, id_col = False, None, None
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


def _insert_missing_summary_rows(lines: list, counts: dict, vocab: list,
                                 aliases: tuple = ()) -> tuple[list, list]:
    """Insert `| <Status> | <n> |` rows for in-vocab statuses with a non-zero
    count but no row in the reconcile-managed global summary block (the block
    carrying a Total row, or the sole summary - the same managed-block rule
    the rewriter uses; a scoped per-epic roll-up is never touched). New rows
    land before the Total row. Returns (inserted_statuses, unplaceable) -
    unplaceable is non-empty when a needed row has no managed block to live
    in, so the caller can fail loud instead of exiting 0 over drift.

    Zero summary blocks = no summary contract: nothing asserts counts, so
    nothing is missing (detect's count-mismatch fires only when a summary
    exists, and apply mirrors that authority). Missing is judged against the
    UNION of all blocks' rows - a status with a row anywhere is not missing."""
    n_summary = sum(1 for ln in lines
                    if (c := _table_cells(ln)) and [x.lower() for x in c] == ["status", "count"])
    if n_summary == 0:
        return [], []
    managed_insert_at = None
    present: set = set()
    i = 0
    while i < len(lines):
        cells = _table_cells(lines[i])
        if not (cells and [x.lower() for x in cells] == ["status", "count"]):
            i += 1
            continue
        block_present: set = set()
        total_idx = None
        last_row_idx = i
        j = i + 1
        while j < len(lines):
            cj = _table_cells(lines[j])
            if cj is None:
                if not lines[j].strip().startswith("|"):
                    break  # blank/prose ends the block
                last_row_idx = j  # separator row
                j += 1
                continue
            lo = [c.lower() for c in cj]
            if "status" in lo or any(a in lo for a in aliases):
                break  # next header - block ended
            if len(cj) == 2:
                if cj[0].replace("*", "").strip().lower() == "total":
                    total_idx = j
                else:
                    canon = _canonical_status(cj[0].replace("*", "").strip(), vocab)
                    if canon:
                        block_present.add(canon)
                last_row_idx = j
            j += 1
        present |= block_present  # union across ALL blocks, managed or not
        if managed_insert_at is None and (total_idx is not None or n_summary == 1):
            managed_insert_at = total_idx if total_idx is not None else last_row_idx + 1
        i = j
    missing = [st for st in vocab if counts.get(st, 0) > 0 and st not in present]
    if not missing:
        return [], []
    if managed_insert_at is None:
        return [], missing
    for k, st in enumerate(missing):
        lines.insert(managed_insert_at + k, f"| {st} | {counts[st]} |")
    return missing, []


_DASHED_DISPLAY = {"cr", "rfc"}  # the types whose display ids carry a dash


def _display_id(type_: str, norm: str) -> str:
    """The conventional display form for an appended row's id cell."""
    num = sdlc_md.id_number(norm)
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1].upper()
    if type_ in _DASHED_DISPLAY and num is not None:
        return f"{prefix}-{num:04d}"
    return norm


def _master_data_header(lines: list, census: dict) -> tuple[int, list] | None:
    """The MASTER data table's (line, header cells): among ID-carrying headers,
    the one whose contiguous rows hold the most census artifact ids. A trailing
    view or breakdown table must never capture an appended row - the id would
    parse from the view and certify the incomplete master as clean.

    Census-id ties are disambiguated structurally, never positionally alone:
    a Title column (the canonical index schema) beats a view's bespoke column,
    a richer header beats a narrower breakdown, more rows beat fewer, and only
    then does LAST win (the shipped master-last layouts). Tables identical on
    every axis are indistinguishable - return None so the caller reports the
    rows unapplied loudly instead of fabricating a choice."""
    candidates: list[tuple[tuple, int, list]] = []  # (rank-sans-line, line, cells)
    for i, ln in enumerate(lines):
        cells = _table_cells(ln)
        low = [c.lower() for c in cells] if cells else []
        if not (cells and len(cells) > 2 and "id" in low):
            continue
        score = n_rows = 0
        j = i + 1
        while j < len(lines) and lines[j].strip().startswith("|"):
            n_rows += 1
            m = sdlc_md.ID_SEARCH_RE.search(lines[j])
            if m and _norm_id(m.group(0)) in census:
                score += 1
            j += 1
        rank = (score, int("title" in low), len(cells), n_rows)
        candidates.append((rank, i, cells))
    if not candidates:
        return None
    top = max(c[0] for c in candidates)
    winners = [c for c in candidates if c[0] == top]
    # Indistinguishable mirrors (every top-ranked table has an IDENTICAL header) can never be
    # told apart - return None so the caller reports the rows unapplied loudly. Comparing the
    # whole winner set, not just winners[0] vs winners[-1], catches a 3-way tie whose distinct
    # table sits between two identical mirrors (the first/last check missed it).
    if len(winners) > 1 and len({tuple(c[2]) for c in winners}) == 1:
        return None
    best = max(winners, key=lambda c: c[1])  # distinct headers resolve by position: LAST wins
    return best[1], best[2]


def _plan_missing_appends(lines: list, census: dict, rows: dict) -> tuple:
    """(data header, appendable (norm, disp, status) triples, unappendable
    display ids). Without a pinnable ID-column header nothing is appendable -
    the caller reports those rows loudly instead of guessing a layout."""
    hdr = _master_data_header(lines, census)
    missing = sorted(n for n in census if n not in rows)
    if hdr is None:
        return None, [], [census[n][0] for n in missing]
    return hdr, [(n, *census[n]) for n in missing], []


def _model_corrected_counts(rows: dict, fixes: dict, to_append: list,
                            vocab: list) -> dict:
    """Summary counts for the buffer AS IT WILL BE: existing rows with their
    planned status fixes applied, plus the rows about to be appended."""
    corrected = dict(rows)
    for norm, new in fixes.items():
        corrected[norm] = (rows[norm][0], new)
    for norm, disp, fstatus in to_append:
        corrected[norm] = (disp, _canonical_status(fstatus, vocab) or fstatus)
    return _row_counts(corrected, vocab)


def _table_display_style(lines: list, hdr: tuple, type_: str) -> bool:
    """Does the pinned table's existing id column use the dashed display form?
    Mirror the house rows; fall back to the type convention on an empty table."""
    j = hdr[0] + 1
    while j < len(lines) and lines[j].strip().startswith("|"):
        m = sdlc_md.ID_SEARCH_RE.search(lines[j])
        if m:
            return "-" in m.group(0)
        j += 1
    return type_ in _DASHED_DISPLAY


def _insert_missing_data_rows(lines: list, hdr: tuple, to_append: list,
                              type_: str, root: Path, aliases: tuple = ()) -> list[str]:
    """Insert one header-driven row per missing census file after the pinned
    data table's last contiguous row. Title comes from the artifact file, the
    id cell links the real filename in the table's own display style, and the
    status lands in the pinned status column even when the project declares an
    alias for it (a `--` there would be drift apply itself planted and could
    never repair). Returns the appended norm ids."""
    filenames = _census_filenames(type_, root)
    low = [c.lower() for c in hdr[1]]
    status_i = next((i for i, c in enumerate(low)
                     if c == "status" or c in aliases), None)
    dashed = _table_display_style(lines, hdr, type_)
    j = hdr[0] + 1
    while j < len(lines) and lines[j].strip().startswith("|"):
        j += 1
    appended: list[str] = []
    for k, (norm, disp, fstatus) in enumerate(to_append):
        fname = filenames.get(norm)
        title = disp
        if fname:
            try:
                fv = _file_field_values(
                    (root / sdlc_md.ARTIFACT_TYPES[type_][0] / fname)
                    .read_text(encoding="utf-8"))
                title = fv["title"] or disp
            except OSError:
                pass
        shown = _display_id(type_, norm) if dashed else norm
        link = f"[{shown}]({fname})" if fname else shown
        row = sdlc_md.row_from_header(hdr[1], link, title, fstatus, {})
        if status_i is not None and "status" not in low:
            cells = _table_cells(row)  # aliased column: place the status positionally
            cells[status_i] = fstatus
            row = _join_row(cells)
        lines.insert(j + k, row)
        appended.append(norm)
    return appended


def apply_type(type_: str, repo_root: Path, dry_run: bool = False) -> dict:
    """Apply the mechanical index fixes for one type: rewrite each drifted data
    row's Status cell to the file's canonical status, APPEND a row for each
    census file the index is missing (header-driven, matching the table's own
    column order), then recompute the summary counts (from the same parse_index
    authority `detect` uses). Idempotent; cells are re-escaped on write.
    Orphan-row and missing-index stay report-only - removing history is a
    judgement call, never mechanical.

    `changes`/`appended` list only the edits that actually landed in the buffer. A
    planned fix the writer could not persist (an off-schema/header-less row or a
    data table with no pinnable ID header) is reported in `unapplied`/
    `missing_unapplied`, never as a change - the tool must not announce an edit it
    did not make. Returns {changes, unapplied, appended, missing_unapplied,
    summary_missing, counts_updated}.
    """
    root = Path(repo_root)
    vocab = sdlc_md.status_vocab(type_, repo_root)
    index_path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    result: dict = {"changes": [], "unapplied": [], "counts_updated": False,
                    "appended": [], "missing_unapplied": []}
    if not index_path.exists():
        return result
    index = parse_index(type_, root)
    diagnosis = index.get("degenerate")
    if diagnosis:
        # apply cannot rewrite status cells it cannot pin, and recomputing the
        # summary against all-Unknown rows would report a sync it did not
        # achieve - refuse loudly and hand back the structural remedy instead
        result["refused"] = diagnosis
        return result
    rows = index["rows"]
    census = file_census(type_, root)
    fixes, planned = _plan_status_fixes(rows, census, vocab)

    original = index_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    aliases = tuple(conventions.status_aliases(root))

    # Missing rows: append mechanically when (and only when) the data table can
    # be pinned by its own ID-column header - the row is built in the table's
    # column order, so a house layout is honoured, never guessed at.
    hdr, to_append, result["missing_unapplied"] = _plan_missing_appends(lines, census, rows)

    # Model the corrected rows (status fixes + appends) so the count recompute
    # matches what the buffer will actually hold.
    counts = _model_corrected_counts(rows, fixes, to_append, vocab)

    result["counts_updated"], applied = _rewrite_index_lines(
        lines, fixes, counts, vocab, aliases)
    if to_append:
        result["appended"] = _insert_missing_data_rows(
            lines, hdr, to_append, type_, root, aliases)
        result["counts_updated"] = True
    inserted, unplaceable = _insert_missing_summary_rows(lines, counts, vocab, aliases)
    if inserted:
        result["counts_updated"] = True
    result["summary_missing"] = unplaceable
    # Partition the planned status fixes by what the writer actually rewrote, so a row it
    # declined to touch is surfaced as unapplied rather than fabricated as a clean flip.
    for ch in planned:
        (result["changes"] if _norm_id(ch["id"]) in applied else result["unapplied"]).append(ch)
    if (result["changes"] or result["counts_updated"]) and not dry_run:
        text = "\n".join(lines) + ("\n" if original.endswith("\n") else "")
        sdlc_md.atomic_write(index_path, text)
    return result


def index_derived_issues(repo_root: Path | str, types=None) -> list[str]:
    """Types whose `_index.md` is NOT a fixed point of `apply` - a hand edit or drift the
    derived-index contract forbids (the index is output of the census, never an input).
    Empty list = every index is reproduced by the tool. Uses a dry-run apply, so it reads
    only; a caller (the `index-derived` gate check) turns a non-empty result into a failure."""
    root = Path(repo_root)
    out: list[str] = []
    for t in (types or DEFAULT_TYPES):
        res = apply_type(t, root, dry_run=True)
        if res.get("refused"):
            out.append(f"{t}: index structurally broken - {res['refused']}")
        elif res.get("changes") or res.get("appended") or res.get("counts_updated"):
            n = len(res.get("changes", [])) + len(res.get("appended", []))
            out.append(f"{t}: index not derived-consistent (apply would change "
                       f"{n} row(s)/counts) - regenerate with `reconcile apply`, do not hand-edit")
    return out


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
    # BG0088: unapplied drift signals a non-zero exit in EVERY format (detect-consistent);
    # once --apply has written the fixes there is no residual drift, so it exits 0.
    rc = 1 if (r["drift"] and not args.apply) else 0
    if args.format == "json":
        print(json.dumps(r, indent=2))
        return rc
    for d in r["drift"]:
        verb = "set" if args.apply else "WOULD set"
        print(f"{verb} {d['id']} {d['field']}: {d['index']!r} -> {d['file']!r}")
    print(f"fields: {len(r['drift'])} drift{' (applied)' if args.apply else ''}")
    return rc


def cmd_apply(args: argparse.Namespace) -> int:
    """Apply mechanical index fixes (status cells + summary counts); --dry-run reports only.
    `--format json` emits the per-type result structures for a programmatic caller."""
    repo_root = Path(args.root).resolve()
    types = SCOPE_TYPES.get(args.scope, DEFAULT_TYPES) if args.scope else DEFAULT_TYPES
    n = 0
    unapplied = 0
    do_meta = args.scope in (None, "meta")
    do_breakdown = args.scope in (None, "epics")
    if getattr(args, "format", "text") == "json":
        by_type = {t: apply_type(t, repo_root, dry_run=args.dry_run) for t in types}
        if do_meta:
            by_type["meta"] = apply_meta(repo_root, dry_run=args.dry_run)
        if do_breakdown:
            by_type["breakdown"] = apply_breakdown(repo_root, dry_run=args.dry_run)
        applied = sum(len(r.get("changes", [])) + len(r.get("appended", [])) for r in by_type.values())
        blocked = sum(len(r.get("unapplied", [])) + len(r.get("missing_unapplied", []))
                      + (1 if r.get("refused") else 0) for r in by_type.values())
        print(json.dumps({"dry_run": args.dry_run, "applied": applied, "unapplied": blocked,
                          "by_type": by_type}, indent=2))
        return 1 if blocked else 0  # JSON mode must signal failure like the text path
    for type_ in types:
        res = apply_type(type_, repo_root, dry_run=args.dry_run)
        if res.get("refused"):
            print(f"REFUSED {type_}: {res['refused']}")
            unapplied += 1
            continue
        for a in res.get("appended", []):
            print(f"{'WOULD add' if args.dry_run else 'added'} missing {type_} row {a}")
            n += 1
        for a in res.get("missing_unapplied", []):
            print(f"WARNING: could not add missing {type_} row {a} - no UNIQUELY "
                  f"pinnable data table (either no header carries an ID column, or "
                  f"two candidate tables are indistinguishable); fix the layout, "
                  f"then re-run apply", file=sys.stderr)
            unapplied += 1
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
        for st in res.get("summary_missing", []):
            print(f"WARNING: could not insert a summary row for status '{st}' in the "
                  f"{type_} index - no reconcile-managed summary block (add a Total "
                  f"row to the global summary); counts remain drifted", file=sys.stderr)
            unapplied += 1
    if do_breakdown:
        b = apply_breakdown(repo_root, dry_run=args.dry_run)
        for uid in b["synced"]:
            print(f"{'WOULD sync' if args.dry_run else 'synced'} breakdown checkbox for {uid}")
            n += 1
    if do_meta:
        m = apply_meta(repo_root, dry_run=args.dry_run)
        for a in m["appended"]:
            print(f"{'WOULD add' if args.dry_run else 'added'} missing meta row {a}")
            n += 1
        for a in m["missing_unapplied"]:
            print(f"WARNING: could not add missing meta row {a} - its index has no "
                  f"pinnable ID-column data table; fix the layout, then re-run apply",
                  file=sys.stderr)
            unapplied += 1
    print(f"apply: {'would change' if args.dry_run else 'changed'} {n} row(s)"
          + (f", {unapplied} could not be applied" if unapplied else "")
          + (" [dry-run]" if args.dry_run else ""))
    return 1 if unapplied else 0


def _type_id_in(cell: str, prefix: str) -> str | None:
    """An artifact id of this type in a cell (e.g. US0042, allowing a CR-0042 dash)."""
    m = re.search(rf"\b{re.escape(prefix)}-?\d+\b", cell)
    return m.group(0) if m else None


def master_terminal_rows(text: str, type_: str, repo_root: Path | str) -> dict | None:
    """The archive READ side, shared with `archive.py` (the one archive writer): via
    `sdlc_md.iter_tables` (the one structural boundary,
    no hand-rolled table parsing), find the MASTER data table for `type_` - the status-bearing
    table with the most rows carrying this type's id in its ID column, so a secondary/per-epic
    view can never win selection and cause a double-archive - and classify its id-bearing rows.

    Returns {header_line0, header_cells, rows} where rows = [(line0, id, canonical_status_or_None,
    is_terminal)] (0-based line indices), or None when no master table / no id rows. Status is
    canonicalised against the type vocab; `None` means an unrecognised status (the caller decides
    whether to fail loud). `is_terminal` uses the shared `sdlc_md.terminal_statuses`."""
    root = Path(repo_root)
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
    vocab = sdlc_md.status_vocab(type_, root)
    terminal = sdlc_md.terminal_statuses(type_)
    best = None
    best_n = 0
    best_cols = (0, None)
    for tbl in sdlc_md.iter_tables(text, header_predicate=_VOCAB_HEADER):
        hdr = tbl["header"]
        if not hdr:
            continue
        low = [c.strip().lower() for c in hdr]
        if "status" not in low:
            continue
        status_col = low.index("status")
        id_col = low.index("id") if "id" in low else 0
        n = sum(1 for _ln, cells in tbl["rows"]
                if id_col < len(cells) and _type_id_in(cells[id_col], prefix))
        if n > best_n:
            best, best_n, best_cols = tbl, n, (id_col, status_col)
    if best is None:
        return None
    id_col, status_col = best_cols
    rows: list[tuple] = []
    for lineno, cells in best["rows"]:
        if id_col >= len(cells):
            continue
        rid = _type_id_in(cells[id_col], prefix)
        if not rid:
            continue
        raw = cells[status_col].strip() if status_col is not None and status_col < len(cells) else ""
        st = _canonical_status(raw, vocab)
        rows.append((lineno - 1, rid, st, st in terminal))
    return {"header_line0": best["header_line"] - 1, "header_cells": best["header"], "rows": rows}


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
    a.add_argument("--format", choices=("text", "json"), default="text",
                   help="Output format (json for programmatic callers)")
    a.set_defaults(func=cmd_apply)
    fi = sub.add_parser("fields", help="Project file-owned index cells (title/points).")
    fi.add_argument("--type", default="story", help="Artifact type (default: story)")
    fi.add_argument("--apply", action="store_true", help="Write the cells (default: report only)")
    fi.add_argument("--root", default=".", help="Repo root (default: .)")
    fi.add_argument("--format", choices=("text", "json"), default="text")
    fi.set_defaults(func=cmd_fields)
    # No `archive` subcommand here on purpose: `archive.py` is the ONE archive writer
    # (release-grouped sub-index + live-index pointer). A second writer here relocated the
    # same rows into a different, pointerless layout, and an operator using both silently
    # split a type's terminal rows across two incompatible schemes. reconcile keeps only the
    # shared READ helper (`master_terminal_rows`), which `archive.py` calls.
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
