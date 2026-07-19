#!/usr/bin/env python3
"""SDLC Studio reconcile: census-based drift detection and mechanical repair.

Builds the file census doctrine rule 3 prescribes - artifact files are the
truth, `_index.md` tables are derived - and reports where the indexes have
drifted. Reconciliation runs in BOTH directions: files -> rows (status mismatch,
missing row) and rows -> files (orphan row: an index row with no file; dead row
link: a row whose linked artefact file does not exist), plus summary-count drift.

Subcommands:
  detect   Census + drift report as JSON/text (READ-ONLY).
  apply    Rewrite drifted status cells, append missing rows, recompute counts (WRITES the index).
  fields   Project file-owned index cells (title/points); `--apply` writes.

Only `detect` is read-only; the judgement calls (orphan-row removal, checkbox/
dependency/PRD-feature drift, CR cascades, changelog) stay with the agent.
`apply --prune-orphans` is the one opt-in exception, and it removes only rows
whose link is provably dead - never an unlinked row, which holds its only copy.

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
    "dead-row-link",
    "count-mismatch",
    "breakdown-unticked",
    "breakdown-ticked-early",
    "epic-points-stale",
    "link-asymmetry",
    "undecomposed",
    "request-derivable",
    "linked-epics",
)

# Statuses that do NOT imply a backing file yet. An UNLINKED index row in one of
# these states (or a non-vocabulary state such as a custom "Retired"/"Reserved")
# with no file on disk is an intentional reservation or a documented retirement —
# not an orphan to remove. Only an active/terminal status (Done, In Progress,
# Complete, …) with no file is a real orphan.
#
# The exemption is for UNLINKED rows only. A row that LINKS an artefact file is
# asserting that file exists, whatever its status: when the link is dead the row
# is a phantom, and `_dead_row_links` reports it (the status gate is bypassed).
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
        # Safe read: a non-UTF-8 / unreadable artefact censuses as "Unknown" (named by validate),
        # never crashes the census - which is on the filer's post-write count recompute AND the
        # pre-commit `reconcile detect` drift gate. One bad file must not abort either.
        status = sdlc_md.extract_field(sdlc_md.read_text_safe(path), "Status") or "Unknown"
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
    _merge_archive_rows(type_, repo_root, result["rows"], vocab, aliases)
    return result


def _merge_archive_rows(type_: str, repo_root: Path, rows: dict, vocab: list,
                        aliases: tuple) -> dict:
    """Union a type's `archive/**` sub-index rows into `rows`, in place - archived
    terminal rows still count toward the census. A LIVE row always wins: an archive row
    only fills in an id absent from the live index. Otherwise a reopened
    (archived-then-live-again) artefact is permanently shadowed by its stale archive
    status - un-clearable drift."""
    archive_dir = repo_root / sdlc_md.ARTIFACT_TYPES[type_][0] / "archive"
    if archive_dir.is_dir():
        for af in sorted(archive_dir.rglob("*.md")):
            arows, _ = _index_rows_and_summary(sdlc_md.read_text_safe(af), vocab, aliases)
            for k, v in arows.items():
                if k not in rows:
                    rows[k] = v
    return rows


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


# --- The other direction: rows -> files --------------------------------------
# The census walks the FILES and fixes their rows. Nothing walked the ROWS, so a row
# pointing at a file that no longer exists was never noticed and the index kept
# advertising an artefact that is not there - the derived-index promise broken in the
# direction reconcile is supposed to make true. A row's markdown link is the row's own
# assertion that the file exists; when the link is dead, the row is a phantom.
_ROW_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+\.md)\)")


def index_row_links(text: str) -> list[tuple[int, str, str]]:
    """(1-based line, display id, link target) for every data row that links its OWN
    artefact file - the link whose filename carries the row's id.

    Only the row's own artefact is checked: a row may also link an epic, a CR or a
    parent story in another column, and those are other rows' business (and other
    directories' relative paths). A row with no self-link asserts nothing about a file -
    it stays a reservation, judged by status alone in `_orphan_row_drift`.
    """
    out: list[tuple[int, str, str]] = []
    for tbl in sdlc_md.iter_tables(text, header_predicate=_VOCAB_HEADER):
        for lineno, cells in tbl["rows"]:
            if len(cells) == 2 and cells[1].replace(",", "").isdigit():  # summary row
                continue
            m = next((sdlc_md.ID_SEARCH_RE.search(c) for c in cells
                      if sdlc_md.ID_SEARCH_RE.search(c)), None)
            if not m:
                continue
            rid = m.group(0)
            for cell in cells:
                for tgt in _ROW_LINK_RE.findall(cell):
                    rec = sdlc_md.extract_record_id(Path(tgt).stem)
                    if rec and _norm_id(rec) == _norm_id(rid):
                        out.append((lineno, rid, tgt))
                        break
    return out


def _index_files(type_: str, repo_root: Path) -> list[Path]:
    """The index files that carry this type's rows: the live `_index.md` plus any
    release sub-indexes under `<type>/archive/` (parse_index unions those rows into the
    census, so a phantom row hiding in one is just as blind)."""
    rel = repo_root / sdlc_md.ARTIFACT_TYPES[type_][0]
    files = [rel / "_index.md"] if (rel / "_index.md").exists() else []
    archive = rel / "archive"
    if archive.is_dir():
        files.extend(sorted(archive.rglob("*.md")))
    return files


def _link_exists(index_path: Path, target: str) -> bool:
    """Does a row's link target resolve to a real file, read RELATIVE to the index that carries
    it? An archived row lives in an `archive/<release>/` sub-index and carries a `../../`-relative
    link back to the file in the type dir, so the one file-relative resolution is correct for both
    the live index and an archive sub-index.

    No type-dir fallback: it was an accommodation for the old wrong-depth archive links
    (a bare filename resolved against the type dir), all fixed by BG0137. Kept standing, it was the
    second place a regressed link could HIDE - `check_links` (which shed the same fallback) would
    cry a dead link while reconcile silently tolerated it, the LL0016 class of two guards
    disagreeing about what a valid link is. The rows all resolve file-relative now, so the fallback
    only ever masked a regression."""
    return (index_path.parent / target).exists()


def _dead_row_links(type_: str, repo_root: Path) -> list[dict]:
    """An index row that LINKS an artefact file which does not exist - a phantom the
    file census can never see (it walks files, and this file is gone). Status-blind on
    purpose: a `Proposed` row that links a file is claiming that file, so deleting it
    leaves drift exactly as a `Done` row would."""
    out: list[dict] = []
    for index_path in _index_files(type_, repo_root):
        rel = index_path.relative_to(repo_root).as_posix()
        for lineno, disp, target in index_row_links(
                index_path.read_text(encoding="utf-8")):
            if _link_exists(index_path, target):
                continue
            out.append({"type": type_, "id": disp, "kind": "dead-row-link",
                        "file_status": None, "index_status": None,
                        "file": target, "index": rel, "line": lineno,
                        "fix": f"{rel}:{lineno} links {target}, which does not exist - "
                               f"restore the file, or remove the row "
                               f"(reconcile apply --prune-orphans)"})
    return out


def _orphan_row_drift(type_, census, rows, vocab, linked: set | None = None) -> list[dict]:
    """A live index row whose status implies a backing file, but none exists.

    A row already reported as a `dead-row-link` is skipped: that finding is the same
    phantom diagnosed precisely (it names the missing file and is the only safely
    prunable class), and reporting both would double-count one row.
    """
    linked = linked or set()
    out: list[dict] = []
    for norm, (disp, istatus) in sorted(rows.items()):
        if norm not in census and norm not in linked:
            icanon = _canonical_status(istatus, vocab)
            # An UNLINKED row whose status doesn't imply a file yet (Proposed/Draft/…)
            # or is a custom retirement (non-vocabulary) is an intentional reservation,
            # not an orphan — don't flag it.
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
    # Both directions: files -> rows (above), and rows -> files (here). A row whose
    # linked file is gone is a phantom the census cannot see.
    dead = _dead_row_links(type_, repo_root)
    drift += dead
    drift += _orphan_row_drift(type_, census, rows, vocab,
                               {_norm_id(d["id"]) for d in dead})
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
    text = sdlc_md.read_text_safe(path) if path.exists() else ""
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
    result: dict = {"appended": [], "missing_unapplied": [], "created": []}
    for type_ in _META_INDEX:
        rel, prefix = _META_INDEX[type_]
        index_path = root / rel / "_index.md"
        census = meta_census(type_, root)
        if not index_path.exists():
            # CR0277: create a missing meta index (reviews/, retros/) from its template, then fall
            # through to append the census rows. No-op when there are no files to seed.
            made = _create_missing_index(root, type_, rel, dry_run) if census else None
            if made == "would-create":
                result["created"].append(f"{rel}/_index.md (would create)")
                continue
            if made != "created":
                continue
            result["created"].append(f"{rel}/_index.md")
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


def declared_breakdown_ids(text: str) -> list[str]:
    """Every id-bearing checkbox line in an epic's Story Breakdown, resolvable or not.

    `_breakdown_units` yields only units it can RESOLVE - it skips a breakdown id with no
    backing file, and a unit file carrying no Status. Those skips are right for drift
    detection (there is nothing to compare) and wrong for judging completion: an
    unresolvable child is unknown, not finished.

    Lives here, beside the regexes, because two subsystems now need the same answer - the
    close derives an epic terminal from these ids, and the close-owed detector decides
    whether a retro accounted for them. When those two disagreed about what a child is, an
    epic could be forgiven off a strict subset of the children its own closure derived from.
    """
    out: list[str] = []
    in_breakdown = False
    for ln in text.splitlines():
        if ln.lstrip().startswith("#"):
            in_breakdown = bool(_BREAKDOWN_HEADING_RE.match(ln.strip()))
            continue
        if not in_breakdown or not _BREAKDOWN_BOX_RE.match(ln):
            continue
        idm = sdlc_md.ID_SEARCH_RE.search(ln)
        if idm:
            out.append(idm.group(0))
    return out


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
        raw = (sdlc_md.extract_field(sdlc_md.read_text_safe(upath), "Status") or "").strip()
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
        text = sdlc_md.read_text_safe(epath)
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
        text = sdlc_md.read_text_safe(epath)
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


# -----------------------------------------------------------------------------
# Epic derived point total (the roll-up)
#
# An epic is T-shirt sized (a `Size:` of S/M/L/XL) - its OWN coarse estimate, made before its
# stories exist. Its POINT total is a different thing entirely: the sum of the points of the
# stories beneath it, which exists only AFTER decomposition and is DERIVED, never estimated.
# Derived means checkable, and checkable means it cannot silently drift: reconcile recomputes it
# from the stories every run (LL0034 - a number that can be true in the record and false in
# reality must be computed, not stamped), exactly as the summary counts are recomputed one level
# down. Only an epic that DECLARES the field is reconciled; an epic without it asserts no roll-up
# (the same rule status-mismatch uses for a file with no Status), so this never fabricates drift
# on a legacy epic. A T-shirt `Size` is never read here - only STORY points are summed, so an
# epic's own coarse size can never leak into a points figure.
# -----------------------------------------------------------------------------
EPIC_DERIVED_FIELD = "Derived Point Total"
# Tolerate an optional leading `>` (the blockquote metadata form refine mints), not only a bare
# line - otherwise a wrong BLOCKQUOTE total is drift `apply` cannot clear.
_EPIC_DERIVED_LINE_RE = re.compile(
    r"^(\s*>?[^\S\n]*\*\*" + re.escape(EPIC_DERIVED_FIELD) + r":\*\*[^\S\n]*)(.*)$")


def _parse_leading_int(raw: str | None) -> int | None:
    """The leading integer of a field value (`10`, `10 (derived)`), or None when it carries
    none - an absent field, or an unfilled `{{derived_points}}` placeholder, both of which
    reconcile treats as drift and fills."""
    if not raw or not raw.strip():
        return None
    tok = raw.strip().split()[0].strip("*_`")
    return int(tok) if tok.isdigit() else None


def _epic_story_point_totals(repo_root: Path | str) -> dict[str, int]:
    """{normalised epic id -> sum of its stories' points}. A story counts toward an epic when it
    names that epic (`> **Epic:**`) AND carries a size on the Fibonacci scale; a story with no
    epic, or no points, contributes nothing. Reads STORY points only - never an epic's own Size -
    so a T-shirt size can never be summed into the roll-up."""
    root = Path(repo_root)
    totals: dict[str, int] = {}
    for spath in sdlc_md.artifact_files("story", root):
        text = sdlc_md.read_text_safe(spath)
        epic_ref = sdlc_md.story_epic(text)
        if not epic_ref:
            continue
        pts = sdlc_md.read_points(text)
        if pts is None:
            continue
        m = sdlc_md.ID_SEARCH_RE.search(epic_ref)
        if not m:
            continue
        key = _norm_id(m.group(0))
        totals[key] = totals.get(key, 0) + pts
    return totals


def epic_points_drift(repo_root: Path | str) -> list[dict]:
    """An epic whose declared `Derived Point Total` does not equal the sum of its stories'
    points. Only epics that CARRY the field are checked - a legacy epic without it asserts no
    roll-up to reconcile, exactly as a file with no Status field cannot status-drift."""
    root = Path(repo_root)
    totals = _epic_story_point_totals(root)
    drift: list[dict] = []
    for epath in sdlc_md.artifact_files("epic", root):
        text = sdlc_md.read_text_safe(epath)
        raw = sdlc_md.extract_field(text, EPIC_DERIVED_FIELD)
        if raw is None:
            continue
        eid = sdlc_md.extract_record_id(epath.stem) or epath.stem
        computed = totals.get(_norm_id(eid), 0)
        if _parse_leading_int(raw) != computed:
            drift.append({"type": "epic", "id": eid, "kind": "epic-points-stale",
                          "file_status": None, "index_status": None,
                          "fix": f"recompute {eid} {EPIC_DERIVED_FIELD} to {computed} "
                                 f"(the sum of its stories' points; declared {raw.strip()!r})"})
    return drift


_LINKED_EPICS_HEADER = "Linked Epics"
_CR_ROW_RE = re.compile(r"^\|\s*\[(CR-?\d+)\]")
#: A cell separator is an UNESCAPED pipe. Markdown escapes a literal pipe inside a cell as
#: `\|`, and splitting on every pipe counts that escape as a separator - which shifts every
#: cell after it, so a header-located column index then addresses the wrong one. Locating
#: the column by header does not save you once the cell count is wrong.
_UNESCAPED_PIPE_RE = re.compile(r"(?<!\\)\|")


def _split_row_cells(line: str) -> list[str]:
    """The cells of a markdown table row, respecting `\\|` escapes."""
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith(r"\|") else body
    return [c.strip() for c in _UNESCAPED_PIPE_RE.split(body)]


def _linked_epics_column(index_text: str) -> int | None:
    """The zero-based cell index of the Linked Epics column, or None when absent.

    Located by HEADER rather than by position: the CR index has carried a different column
    count across schema versions, and a hardcoded offset would silently rewrite Type or Date
    on an older index.
    """
    for line in index_text.splitlines():
        if _LINKED_EPICS_HEADER.lower() in line.lower() and line.lstrip().startswith("|"):
            cells = _split_row_cells(line)
            for i, c in enumerate(cells):
                if c.lower() == _LINKED_EPICS_HEADER.lower():
                    return i
    return None


def _cr_decomposed_into(root: Path) -> dict:
    """id -> the `Decomposed-into` value each CR file declares. Files are truth."""
    out = {}
    for p in sdlc_md.artifact_files("cr", root):
        value = sdlc_md.extract_field(sdlc_md.read_text_safe(p), "Decomposed-into")
        if value and value.strip():
            cid = sdlc_md.extract_record_id(p.stem) or p.stem
            out[_norm_id(cid)] = value.strip()
    return out


def detect_linked_epics(repo_root: Path | str) -> dict:
    """Rows whose Linked Epics cell disagrees with the CR file's `Decomposed-into`.

    The column shipped as a placeholder and stayed one - every CR in this workspace that had
    been decomposed still showed `--`. A column nothing derives is a column nobody can
    trust, so it is censused from the files like every other derived cell. A CR that was
    never decomposed has no epic to name, so a placeholder there is honest, not drift.
    """
    root = Path(repo_root)
    index_path = root / "sdlc-studio" / "change-requests" / "_index.md"
    if not index_path.is_file():
        return {"drift": []}
    text = index_path.read_text(encoding="utf-8")
    col = _linked_epics_column(text)
    if col is None:
        return {"drift": []}
    declared = _cr_decomposed_into(root)
    drift = []
    for line in text.splitlines():
        m = _CR_ROW_RE.match(line)
        if not m:
            continue
        cid = _norm_id(m.group(1))
        expected = declared.get(cid)
        if not expected:
            continue
        cells = _split_row_cells(line)
        if col < len(cells) and cells[col] != expected:
            drift.append({"id": cid, "kind": "linked-epics",
                          "found": cells[col], "expected": expected,
                          "fix": (f"set the Linked Epics cell of {cid} to '{expected}' "
                                  f"(currently '{cells[col]}') - `reconcile.py apply` does it")})
    return {"drift": drift}


def apply_linked_epics(repo_root: Path | str, dry_run: bool = False) -> dict:
    """Write each CR row's Linked Epics cell from the file's `Decomposed-into`.

    Rewrites ONLY that cell, located by header and split on UNESCAPED pipes, so the
    surrounding row survives intact. Both halves are load-bearing: locating by header
    guards against a differing column count between schema versions, and honouring `\\|`
    guards against a literal pipe inside a cell shifting every cell after it. The first
    version had only the header half and wrote the epic id over the Date column while
    leaving the real cell untouched, so the row lost data AND re-drifted on the next run.

    Idempotent. Returns {synced: [ids]}.
    """
    root = Path(repo_root)
    index_path = root / "sdlc-studio" / "change-requests" / "_index.md"
    drift = detect_linked_epics(root)["drift"]
    if not drift:
        return {"synced": []}
    if dry_run:
        return {"synced": [d["id"] for d in drift]}
    text = index_path.read_text(encoding="utf-8")
    col = _linked_epics_column(text)
    wanted = {d["id"]: d["expected"] for d in drift}
    lines = text.splitlines(True)
    synced = []
    for i, line in enumerate(lines):
        m = _CR_ROW_RE.match(line)
        if not m:
            continue
        cid = _norm_id(m.group(1))
        if cid not in wanted:
            continue
        newline = "\n" if line.endswith("\n") else ""
        cells = _split_row_cells(line)
        if col >= len(cells):
            continue
        cells[col] = wanted[cid]
        lines[i] = "| " + " | ".join(cells) + " |" + newline
        synced.append(cid)
    if synced:
        # atomic_write, not write_text: an index is read by every other lane, and a torn
        # write from an interrupted apply leaves a half-table nothing can parse.
        sdlc_md.atomic_write(index_path, "".join(lines))
    return {"synced": synced}


def apply_epic_points(repo_root: Path | str, dry_run: bool = False) -> dict:
    """Write each declaring epic's `Derived Point Total` to the sum of its stories' points - the
    same recompute discipline as the summary counts, one level up. Rewrites only the value on the
    field's own line, so the surrounding note survives; idempotent. Returns {synced: [ids]}."""
    root = Path(repo_root)
    totals = _epic_story_point_totals(root)
    synced: list[str] = []
    for epath in sdlc_md.artifact_files("epic", root):
        original = sdlc_md.read_text_safe(epath)
        if sdlc_md.extract_field(original, EPIC_DERIVED_FIELD) is None:
            continue
        eid = sdlc_md.extract_record_id(epath.stem) or epath.stem
        computed = totals.get(_norm_id(eid), 0)
        lines = original.splitlines()
        changed = False
        for i, ln in enumerate(lines):
            m = _EPIC_DERIVED_LINE_RE.match(ln)
            if not m:
                continue
            if _parse_leading_int(m.group(2)) != computed:
                lines[i] = f"{m.group(1)}{computed}"
                changed = True
            break
        if changed:
            synced.append(eid)
            if not dry_run:
                sdlc_md.atomic_write(
                    epath, "\n".join(lines) + ("\n" if original.endswith("\n") else ""))
    return {"synced": synced}


def _artefact_index(repo_root: Path) -> dict[str, tuple[str, str, str]]:
    """{normalised id -> (display id, type, text)} across every artefact type - the one census
    the link checks read, so a child and its parent are looked up the same way whatever their
    types."""
    index: dict[str, tuple[str, str, str]] = {}
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for p in sdlc_md.artifact_files(type_, repo_root):
            cid = sdlc_md.extract_record_id(p.stem)
            if cid:
                index[_norm_id(cid)] = (cid, type_, sdlc_md.read_text_safe(p))
    return index


def link_asymmetry_drift(repo_root: Path | str) -> list[dict]:
    """A declared request<->child link that does not resolve BOTH ways (G3). A decomposition
    writes the link on both sides - the child's `Parent:` and the request's `Decomposed-into:` -
    so a link asserted on one side only, or pointing at an id that resolves to no artefact, is
    drift. The story's `Epic:` link is out of scope here: an epic's Story Breakdown already
    round-trips it (`epic_breakdown_drift`), so this checks the generic `Parent:`/`Decomposed-into:`
    pairing that carries the request layer. Detect-only: which side is authoritative is a
    judgement (was the child mis-parented, or the parent's list stale?), so it is reported for a
    human, never auto-rewritten."""
    root = Path(repo_root)
    index = _artefact_index(root)
    drift: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def emit(child_id: str, child_type: str, why: str, parent_id: str) -> None:
        key = (_norm_id(child_id), _norm_id(parent_id))
        if key in seen:
            return
        seen.add(key)
        drift.append({"type": child_type, "id": child_id, "kind": "link-asymmetry",
                      "file_status": None, "index_status": None, "fix": why})

    # child -> parent: EVERY `Parent:` must resolve, and each parent must name the child back. A
    # shared batch epic (refine --into) carries one Parent line per request it delivers, so all of
    # them are checked, not only the first.
    for cnorm, (cid, ctype, ctext) in index.items():
        for par in sdlc_md.parent_refs(ctext):
            pnorm = _norm_id(par)
            if pnorm not in index:
                emit(cid, ctype, f"{cid} names Parent {par}, which resolves to no artefact", par)
                continue
            pid, ptype, ptext = index[pnorm]
            back = {_norm_id(x) for x in sdlc_md.decomposed_ids(ptext)}
            if cnorm not in back:
                emit(cid, ctype, f"{cid} names Parent {pid}, but {pid} does not list {cid} in its "
                                 f"{sdlc_md.DECOMPOSED_FIELD}", pid)

    # request -> child: every `Decomposed-into:` entry must resolve and name the request back.
    for rnorm, (rid, rtype, rtext) in index.items():
        for child in sdlc_md.decomposed_ids(rtext):
            cnorm = _norm_id(child)
            if cnorm not in index:
                emit(child, rtype, f"{rid} lists child {child} in its "
                                   f"{sdlc_md.DECOMPOSED_FIELD}, which resolves to no artefact", rid)
                continue
            cid, ctype, ctext = index[cnorm]
            # the child must name this request among its parents - a shared batch epic lists one
            # `Parent:` per request it delivers, so membership, not equality with the first.
            if rnorm not in {_norm_id(x) for x in sdlc_md.parent_refs(ctext)}:
                emit(cid, ctype, f"{rid} lists {cid} as a child, but {cid} does not name {rid} "
                                 f"as its {sdlc_md.PARENT_FIELD}", rid)
    return drift


def _requires_children(type_: str, status: str) -> bool:
    """True when a discovery item of this type+status has been ACCEPTED into the workflow and so
    must have been decomposed. A discovery item is intake until someone accepts it: the create
    state (`Proposed` cr / `Draft` rfc / `Open` issue) is pre-triage intake, and
    `inbox`/`Deferred`/`Blocked` are parked - none is expected to carry children yet. A terminal
    item is closed. Only a live, accepted, non-parked item is expected to have produced work; a
    childless one there is the graveyard G5 guards against (an accepted CR/RFC never refined, an
    Issue never triaged). Keeping the intake states exempt is what keeps `reconcile detect` clean
    on a healthy backlog (the exit-code contract CI relies on)."""
    if not sdlc_md.is_discovery(type_):
        return False
    if sdlc_md.is_terminal_status(type_, status):
        return False
    # exempt the pre-triage intake state (the type's create status), the inbox lane, and the
    # parked states - none is expected to carry children yet. (No "Planned": that is a story
    # status, unreachable here where type_ is always a discovery item.)
    if status in (sdlc_md.create_status(type_), sdlc_md.INBOX_STATUS, "Deferred", "Blocked"):
        return False
    return True


def undecomposed_drift(repo_root: Path | str) -> list[dict]:
    """A discovery item accepted into the workflow (an Approved/In-Progress CR, an In-Review RFC,
    a Triaging Issue) that has NO children (G5). A discovery item is intake, not work, until it is
    decomposed into the units that deliver it; one accepted and never broken down is the intake
    queue rotting into a graveyard. A still-Proposed/Draft/Open item is pre-triage intake and is
    deliberately NOT flagged, so a healthy backlog leaves `reconcile detect` clean. An Issue is
    triaged into bugs; a request is refined into stories/epics - the fix names the right ceremony
    per type."""
    root = Path(repo_root)
    drift: list[dict] = []
    for type_ in sdlc_md.DISCOVERY_TYPES:
        for p in sdlc_md.artifact_files(type_, root):
            text = sdlc_md.read_text_safe(p)
            vocab = sdlc_md.status_vocab(type_, root)
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)
            if not status or not _requires_children(type_, status):
                continue
            rid = sdlc_md.extract_record_id(p.stem) or p.stem
            if sdlc_md.children_of(root, rid):
                continue
            how = ("triage it into the bugs that deliver its fix (write each bug's `Parent:` and "
                   "this Issue's `Decomposed-into:`)" if type_ == "issue" else
                   "decompose it into the stories/epics that deliver it (write each child's "
                   "`Parent:` and this request's `Decomposed-into:`)")
            drift.append({"type": type_, "id": rid, "kind": "undecomposed",
                          "file_status": status, "index_status": None,
                          "fix": f"{rid} is {status} but has no children - {how}, or close it if "
                                 f"it is not going ahead"})
    return drift


def derivable_request_drift(repo_root: Path | str) -> list[dict]:
    """A discovery item whose children have ALL resolved but which is not itself terminal.

    The two-backlog workflow says a request reaches its successful terminal by DERIVATION, never
    by assertion. `transition._request_terminal_gate` implemented the guard half - it refuses a
    premature close - but nothing ever performed the closure once it was earned, so a disciplined
    project accumulates delivered requests that still read as open work. Measured on this repo:
    34 of 59 open CRs, with every delivering epic already Done.

    THE GATE IS THE PREDICATE. This asks `_request_terminal_gate` and treats "no block reason" as
    "derivable", rather than deciding for itself whether the children are resolved. Two answers to
    one question is exactly how a detector and the gate it describes drift apart, and it is safe by
    construction: what apply then asserts is precisely what the gate would already have allowed.

    Import is lazy because `transition` imports this module at load time.
    """
    import transition  # noqa: PLC0415 - lazy: transition imports reconcile at module level
    root = Path(repo_root)
    drift: list[dict] = []
    for type_ in sdlc_md.DISCOVERY_TYPES:
        target = sdlc_md.default_terminal_status(type_)
        if not target:
            continue
        for p in sdlc_md.artifact_files(type_, root):
            text = sdlc_md.read_text_safe(p)
            vocab = sdlc_md.status_vocab(type_, root)
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)
            if not status or sdlc_md.is_terminal_status(type_, status):
                continue
            rid = sdlc_md.extract_record_id(p.stem) or p.stem
            if transition._request_terminal_gate(root, type_, rid, target) is not None:
                continue          # the gate would refuse: not derivable
            drift.append({"type": type_, "id": rid, "kind": "request-derivable",
                          "file_status": status, "index_status": None,
                          "fix": f"{rid} is {status} but every child it produced is resolved - "
                                 f"its terminal is DERIVED, so `reconcile apply` sets it "
                                 f"{target}"})
    return drift


def apply_derivable_requests(repo_root: Path | str, dry_run: bool = False) -> list[str]:
    """Derive every request whose children have all resolved. Returns the ids transitioned.

    Goes through `transition.transition`, never a direct write, so the index row, any parent
    cascade and the telemetry event all happen exactly as a hand transition would.
    """
    import transition  # noqa: PLC0415 - lazy, as above
    root = Path(repo_root)
    done: list[str] = []
    for d in derivable_request_drift(root):
        target = sdlc_md.default_terminal_status(d["type"])
        if dry_run:
            done.append(d["id"])
            continue
        try:
            transition.transition(root, d["id"], target)
            done.append(d["id"])
        except (ValueError, FileNotFoundError) as exc:
            # A refusal here is information, not a crash: report and carry on, so one stuck
            # request cannot block the rest of the sweep.
            print(f"  request-derivable: {d['id']} -> {target} refused: {exc}", file=sys.stderr)
    return done


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
        all_drift.extend(epic_points_drift(repo_root))
    # The request<->child link check and the undecomposed check are cross-type (a CR under an RFC,
    # an epic under a CR), so they run on the default full sweep like the meta indexes, not under a
    # single pipeline scope. link-asymmetry is always on (it only fires on links a project chose to
    # write); undecomposed is a HARD workflow rule, so it fires only when the project enforces the
    # two-backlog workflow - an unenforced project is not told its childless CRs are drift.
    if args.scope is None:
        all_drift.extend(link_asymmetry_drift(repo_root))
        all_drift.extend(detect_linked_epics(repo_root)["drift"])
        if sdlc_md.two_backlog_enforced(repo_root):
            all_drift.extend(undecomposed_drift(repo_root))
            all_drift.extend(derivable_request_drift(repo_root))

    by_kind: dict[str, int] = {}
    for d in all_drift:
        by_kind[d["kind"]] = by_kind.get(d["kind"], 0) + 1

    # When both status drift and count drift are present, fixing the statuses moves the counts -
    # so the summary must be recomputed LAST, after every status edit settles. Signpost that order
    # rather than leave the operator to learn it by watching the count move the wrong way.
    fix_order = None
    if ({"status-mismatch", "missing-row", "orphan-row", "dead-row-link"} & set(by_kind)
            and "count-mismatch" in by_kind):
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
        # exit code - reconcile still succeeds/fails on its own census checks.
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
                fv = _file_field_values(sdlc_md.read_text_safe(
                    root / sdlc_md.ARTIFACT_TYPES[type_][0] / fname))
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


def _plan_prune(lines: list, rel_index: str, dead: list[dict]) -> tuple[list[int], list[dict], list[dict]]:
    """(0-based line indices to delete, rows pruned here, dead rows this cannot prune).

    Only a row whose LINK is dead is prunable, and only where that row physically lives
    in the file being rewritten. Two deliberate refusals:

    - an unlinked orphan row is never pruned: an inline-only record holds its ONLY copy
      in that row, so deleting it destroys the record rather than a duplicate of it;
    - a dead row in an `archive/` sub-index is reported, not pruned: `archive.py` is the
      one archive writer, and a second writer editing its files is how two incompatible
      layouts get born.
    """
    here = [d for d in dead if d["index"] == rel_index and 0 < d["line"] <= len(lines)]
    elsewhere = [d for d in dead if d not in here]
    return sorted(d["line"] - 1 for d in here), here, elsewhere


def _prune_dead_rows(type_: str, root: Path, index_path: Path, lines: list, vocab: list,
                     aliases: tuple, rows: dict, dead: list[dict]) -> tuple[list, list, dict]:
    """Delete this index's dead-linked rows from `lines` (in place) and return
    (pruned, prune_unapplied, the rows AS THEY WILL BE) - so the caller's summary
    recompute follows the pruned buffer rather than the rows it no longer holds. Rows are
    cut last-line-first, so an earlier row's index is never shifted by a later deletion."""
    _cut, here, elsewhere = _plan_prune(
        lines, index_path.relative_to(root).as_posix(), dead)
    pruned: list[dict] = []
    for d in sorted(here, key=lambda x: x["line"], reverse=True):
        pruned.append({"id": d["id"], "file": d["file"], "row": lines[d["line"] - 1]})
        del lines[d["line"] - 1]
    if here:
        rows, _summary = _index_rows_and_summary("\n".join(lines), vocab, aliases)
        _merge_archive_rows(type_, root, rows, vocab, aliases)
    return pruned, elsewhere, rows


def _create_missing_index(repo_root: Path, type_: str, rel: str, dry_run: bool) -> str | None:
    """Create a missing `_index.md` at `rel` from its template - the same
    `write_empty_index` path `artifact.py` uses, so the created index matches the house style
    (headers, zeroed counts). Returns 'created' / 'would-create' / None (no template to seed from).
    Shared by the pipeline (`apply_type`) and meta (`apply_meta`) apply paths. Lazy import of
    `file_finding` avoids a module-load cycle (file_finding imports reconcile)."""
    import file_finding
    from datetime import date as _date
    idx = Path(repo_root) / rel / "_index.md"
    if idx.exists():
        return None
    tmpl = file_finding.index_template_path(type_)
    if not tmpl.exists():
        return None
    if dry_run:
        return "would-create"
    file_finding.write_empty_index(idx, tmpl, _date.today().isoformat())
    return "created"


def _seed_missing_index(root: Path, type_: str, result: dict, dry_run: bool) -> bool:
    """Handle a missing pipeline index for `apply_type`: create it from the template when
    there are census files to seed, recording the outcome on `result`. Returns True to PROCEED (the
    index now exists - fall through to append rows + recompute counts), False to BAIL (nothing to
    seed, no template, or a dry-run that only reports it would create). Kept out of `apply_type` so
    that function stays under the cognitive-complexity guard."""
    if not file_census(type_, root):
        return False
    made = _create_missing_index(root, type_, sdlc_md.ARTIFACT_TYPES[type_][0], dry_run)
    if made == "would-create":
        result["would_create_index"] = True
        return False
    if made != "created":
        return False
    result["created_index"] = True
    return True


def apply_type(type_: str, repo_root: Path, dry_run: bool = False,
               prune_orphans: bool = False) -> dict:
    """Apply the mechanical index fixes for one type: rewrite each drifted data
    row's Status cell to the file's canonical status, APPEND a row for each
    census file the index is missing (header-driven, matching the table's own
    column order), then recompute the summary counts (from the same parse_index
    authority `detect` uses). Idempotent; cells are re-escaped on write.
    Orphan-row and missing-index stay report-only - removing history is a
    judgement call, never mechanical.

    `prune_orphans` (opt-in, never the default) additionally DELETES rows whose linked
    artefact file is gone (`dead-row-link`). It is off by default because a missing file
    is not proof of a deletion: a bad checkout, an in-flight rename, or a file not yet
    staged all look identical from here, and a silent prune would destroy the row that is
    the artefact's last trace. `detect` always reports the phantom; removing it is the
    operator's call, and each removed row is echoed verbatim as it goes.

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
    # CR0277: a missing index is now a MECHANICAL fix - `_seed_missing_index` creates it from the
    # template (recording the outcome on `result`); we bail only when it cannot/should not seed,
    # else fall through so the census rows are appended and counts recomputed.
    if not index_path.exists() and not _seed_missing_index(root, type_, result, dry_run):
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

    # Phantom rows (opt-in only): delete the rows whose linked file is gone, then re-read
    # the surviving rows so the recomputed summary counts follow the buffer as it will be.
    # `dead_rows` is reported whether or not the operator asked to prune: an index still
    # advertising an artefact that is not there must never leave apply silent ("changed 0
    # row(s)" over a phantom is how BG0135 survived every guard in the gate).
    result["dead_rows"] = _dead_row_links(type_, root)
    result["pruned"], result["prune_unapplied"] = [], []
    if prune_orphans:
        result["pruned"], result["prune_unapplied"], rows = _prune_dead_rows(
            type_, root, index_path, lines, vocab, aliases, rows, result["dead_rows"])

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
    if (result["changes"] or result["counts_updated"] or result["pruned"]) and not dry_run:
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
#. Persona is deferred: it has no single canonical field in a story (it lives in
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
            fvals[_norm_id(rec)] = _file_field_values(sdlc_md.read_text_safe(path))
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
        sdlc_md.atomic_write(index_path,
                             "\n".join(lines) + ("\n" if original.endswith("\n") else ""))
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
    prune = getattr(args, "prune_orphans", False)
    do_meta = args.scope in (None, "meta")
    do_breakdown = args.scope in (None, "epics")
    if getattr(args, "format", "text") == "json":
        by_type = {t: apply_type(t, repo_root, dry_run=args.dry_run, prune_orphans=prune)
                   for t in types}
        if do_meta:
            by_type["meta"] = apply_meta(repo_root, dry_run=args.dry_run)
        if do_breakdown:
            by_type["breakdown"] = apply_breakdown(repo_root, dry_run=args.dry_run)
            by_type["epic_points"] = apply_epic_points(repo_root, dry_run=args.dry_run)
            by_type["linked_epics"] = apply_linked_epics(repo_root, dry_run=args.dry_run)
        if args.scope is None and sdlc_md.two_backlog_enforced(repo_root):
            by_type["derivable_requests"] = {
                "synced": apply_derivable_requests(repo_root, dry_run=args.dry_run)}
        applied = sum(len(r.get("changes", [])) + len(r.get("appended", []))
                      + len(r.get("pruned", [])) + len(r.get("synced", []))
                      for r in by_type.values())
        blocked = sum(len(r.get("unapplied", [])) + len(r.get("missing_unapplied", []))
                      + len(r.get("prune_unapplied", []))
                      + (1 if r.get("refused") else 0) for r in by_type.values())
        print(json.dumps({"dry_run": args.dry_run, "applied": applied, "unapplied": blocked,
                          "by_type": by_type}, indent=2))
        return 1 if blocked else 0  # JSON mode must signal failure like the text path
    for type_ in types:
        res = apply_type(type_, repo_root, dry_run=args.dry_run, prune_orphans=prune)
        if res.get("refused"):
            print(f"REFUSED {type_}: {res['refused']}")
            unapplied += 1
            continue
        for p in res.get("pruned", []):
            # echo the row verbatim as it goes: the file is already gone, so this row was
            # the artefact's last trace in the tree. It must survive in the run log.
            print(f"{'WOULD prune' if args.dry_run else 'pruned'} {type_} row {p['id']} "
                  f"(links {p['file']}, which does not exist): {p['row']}")
            n += 1
        pruned_ids = {p["id"] for p in res.get("pruned", [])}
        for dr in res.get("dead_rows", []):
            if dr["id"] in pruned_ids:
                continue
            # Never silent: a phantom row apply did not remove is still a phantom.
            remedy = ("restore the file, or edit the archive sub-index (archive.py is the "
                      "one archive writer - reconcile will not rewrite its files)"
                      if "/archive/" in dr["index"] else
                      "restore the file, or remove the row with "
                      "`reconcile apply --prune-orphans`")
            print(f"WARNING: {type_} row {dr['id']} ({dr['index']}:{dr['line']}) links "
                  f"{dr['file']}, which does not exist - {remedy}", file=sys.stderr)
        # Only when the operator ASKED to prune is an unprunable row an unapplied action.
        unapplied += len(res.get("prune_unapplied", []))
        if res.get("created_index"):
            print(f"created {type_} index (from template)")
            n += 1
        elif res.get("would_create_index"):
            print(f"WOULD create {type_} index (from template)")
            n += 1
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
        ep = apply_epic_points(repo_root, dry_run=args.dry_run)
        for eid in ep["synced"]:
            print(f"{'WOULD recompute' if args.dry_run else 'recomputed'} "
                  f"derived point total for {eid}")
            n += 1
        le = apply_linked_epics(repo_root, dry_run=args.dry_run)
        for cid in le["synced"]:
            print(f"{'WOULD sync' if args.dry_run else 'synced'} Linked Epics for {cid}")
            n += 1
    # Full-sweep only, and gated exactly as the detector is: an unenforced project closes its
    # requests by assertion, so nothing here may move them.
    if args.scope is None and sdlc_md.two_backlog_enforced(repo_root):
        for rid in apply_derivable_requests(repo_root, dry_run=args.dry_run):
            print(f"{'WOULD derive' if args.dry_run else 'derived'} {rid} "
                  f"(every child resolved)")
            n += 1
    if do_meta:
        m = apply_meta(repo_root, dry_run=args.dry_run)
        for c in m.get("created", []):
            print(f"{'WOULD create' if args.dry_run else 'created'} meta index {c}")
            n += 1
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
    a.add_argument("--prune-orphans", action="store_true",
                   help="Also DELETE index rows whose linked artefact file does not exist "
                        "(dead-row-link). Off by default: a missing file can be a bad "
                        "checkout, an in-flight rename or an unstaged file, so the removal "
                        "is never automatic. Each pruned row is echoed verbatim. An "
                        "UNLINKED orphan row is never pruned - it holds its only copy.")
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
