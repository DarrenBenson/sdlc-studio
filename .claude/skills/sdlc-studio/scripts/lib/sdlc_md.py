#!/usr/bin/env python3
"""Shared parsing and utility helpers for sdlc-studio scripts.

Single source of truth for the markdown conventions the runtime scripts
parse - metadata fields (`> **Name:** value`), artifact IDs, AC blocks - plus
the small utilities (UTC timestamps, safe JSON load, slug, glob) that the
scripts would otherwise each re-implement. Pure stdlib.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")

# -----------------------------------------------------------------------------
# Canonical markdown conventions (the single source of truth for parsing)
# -----------------------------------------------------------------------------

# First `# Heading` of a document.
H1_RE = re.compile(r"^#\s+(.+)$", re.M)
# Artifact ID prefix at the start of a filename stem. CR/RFC display with a
# dash (CR-0001); the others do not (US0001). The optional dash matches both.
# Case-insensitive: some repos name files lowercase (`cr0001.md`) while indexes
# use uppercase (`CR-0001`) — both must parse to the same ID.
# Two id eras coexist (schema v3): the v2 sequential form (`US0001`, `CR-0007`)
# and the v3 form (`BG-01JQK3F8`) - a type prefix, a dash, then a Crockford-base32 short ULID
# (>= 8 chars, extended on a rare directory clash). The base32 alternative is matched
# case-SENSITIVELY (`(?-i:...)`) so it stops at the lowercase `-slug`, never swallowing it.
_V3_SUFFIX = r"(?-i:-[0-9A-HJKMNP-TV-Z]{8,})"
ID_RE = re.compile(
    r"^((?:EP|US|PL|BG|TS|WF|RFC|CR)(?:-?\d{4}|" + _V3_SUFFIX + r"))", re.IGNORECASE)
# Same, unanchored - finds an ID anywhere (e.g. inside an index table cell
# `[US0001](US0001-login.md)`). RFC before CR so `RFC-0001` is not read as `CR`.
ID_SEARCH_RE = re.compile(
    r"(?<![A-Za-z])(?:EP|US|PL|BG|TS|WF|RFC|CR)(?:-?\d{4}|" + _V3_SUFFIX + r")", re.IGNORECASE)
# Acceptance-criterion heading: `### AC1: Title`.
AC_HEADING_RE = re.compile(r"^###\s+(AC\d+)(?::\s*(.*))?$")
# Acceptance-criterion bold bullet: `- **AC1:** text` / `* **AC1** text` / a
# checkbox form `- [ ] **AC1** text` (house template) — the compact inline style
# many stories use instead of a heading per criterion.
AC_BULLET_RE = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?\*\*(AC\d+)[^*]*\*\*[:\s]*(.*)$")
# AC verifier bullets. The leading dash is optional — some repos use a standalone
# `**Verify:**` line rather than a `- **Verify:**` bullet.
VERIFY_RE = re.compile(r"^(\s*)-?\s*\*\*Verify:\*\*\s*(.+?)\s*$")
VERIFIED_RE = re.compile(
    r"^(\s*)-?\s*\*\*Verified:\*\*\s*(yes|no|stale|manual)\s*(?:\(([^)]*)\))?\s*$",
    re.IGNORECASE,
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


# -----------------------------------------------------------------------------
# Time
# -----------------------------------------------------------------------------


def now_iso8601() -> str:
    """Current UTC time as an ISO-8601 Z string (YYYY-MM-DDTHH:MM:SSZ)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_date() -> str:
    """Current UTC date as YYYY-MM-DD."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def debug_enabled() -> bool:
    """True when SDLC_DEBUG=1 - the opt-in diagnostic channel for swallowed-advisory sites."""
    return os.environ.get("SDLC_DEBUG") == "1"


def debug(where: str, detail: object = "") -> None:
    """Emit one stderr line from a swallowed-advisory site when SDLC_DEBUG=1, so a lane that
    degrades silently is still traceable; a no-op otherwise (never on the default path)."""
    if debug_enabled():
        line = f"[sdlc-debug] {where}: {detail}" if detail != "" else f"[sdlc-debug] {where}"
        print(line, file=sys.stderr)


DEFAULT_LOG_MAX_LINES = 5000


def roll_jsonl(path: Path, max_lines: int = DEFAULT_LOG_MAX_LINES) -> bool:
    """Bound an append-only `.local` JSONL log: when it exceeds `max_lines`, keep the most
    recent `max_lines` (the audit trail stays useful without growing without limit). Returns
    True when it rolled. Silent no-op when the file is absent or within bounds."""
    try:
        if not path.exists():
            return False
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) <= max_lines:
            return False
        kept = lines[-max_lines:]
        atomic_write(path, "\n".join(kept) + "\n")
        return True
    except OSError as exc:
        debug("roll_jsonl", exc)
        return False


# -----------------------------------------------------------------------------
# JSON (never raises on bad input - returns the supplied default)
# -----------------------------------------------------------------------------


def loads(text: str, default: T) -> T:
    """Parse JSON text, returning `default` on empty or malformed input."""
    if not text or not text.strip():
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


def read_json(path: Path, default: T) -> T:
    """Read and parse a JSON file, returning `default` if missing or malformed."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return default
    return loads(text, default)


# -----------------------------------------------------------------------------
# Markdown field / ID / title extraction
# -----------------------------------------------------------------------------


def table_cells(line: str) -> list[str] | None:
    """Cells of a markdown table row, or None for a non-table line or a `---`
    separator row. The single splitter every table parser shares: it splits on
    UNescaped pipes only and unescapes `\\|`, so a cell that legitimately contains
    a pipe (e.g. a title `string \\| string[]`) does not shift the columns after it.
    """
    s = line.strip()
    if not s.startswith("|"):
        return None
    cells = [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", s.strip("|"))]
    if all(set(c) <= {"-", ":"} and c for c in cells):
        return None  # separator row
    return cells


# A GFM delimiter row (`| --- |`, `|--|`, `| :-: |`) - the structural marker that
# the |-row above it is a table header. Any dash count (GFM accepts one).
SEP_ROW_RE = re.compile(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$")


def iter_tables(text: str, header_predicate=None):
    """Yield each markdown table as {"header", "header_line", "rows"} - the ONE
    structural boundary rule every table parser shares, so no parser hand-rolls
    its own and re-imports the tallied-into-the-wrong-table defect class.

    - header: the header row's cells, or None for a header-less block
    - header_line / rows: 1-based line numbers; rows = [(lineno, cells), ...]
    - a header row is a |-row immediately followed by a GFM separator (any dash
      count); a markdown heading (#...) ends the current table; `header_predicate`
      (cells -> bool) additionally opens a table on a legacy vocabulary header
      that lacks a separator line
    - separator rows are never yielded (table_cells returns None for them)
    """
    current = None  # {"header": ..., "header_line": ..., "rows": [...]}
    in_fence = False
    fence = ""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        # A fenced code block is illustrative, not structure: a `|`-row inside ``` (a shipped
        # example table) must never be tallied. Track fences and skip their contents entirely.
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            if current:  # a fence, like a heading, ends the table scope
                yield current
            current = None
            in_fence, fence = True, stripped[:3]
            continue
        if in_fence:
            if stripped.startswith(fence):
                in_fence = False
            continue
        if line.lstrip().startswith("#"):  # a heading ends the table scope
            if current:
                yield current
            current = None
            continue
        cells = table_cells(line)
        if cells is None:
            continue
        is_header = (i + 1 < len(lines) and SEP_ROW_RE.match(lines[i + 1])) or                     (header_predicate is not None and header_predicate(cells))
        if is_header:
            if current:
                yield current
            current = {"header": cells, "header_line": i + 1, "rows": []}
            continue
        if current is None:
            current = {"header": None, "header_line": None, "rows": []}
        current["rows"].append((i + 1, cells))
    if current:
        yield current


# -----------------------------------------------------------------------------
# Single-line values: the refusal every writer of a metadata line, a table cell,
# or a one-line bullet shares
# -----------------------------------------------------------------------------

# Every character `str.splitlines` treats as a line break, plus NUL. A value carrying one of
# these breaks OUT of the construct it is written into: the readers in this module take a file
# a line at a time, so what the caller passed as one field becomes two lines, and whatever
# follows the break is read as a metadata line, a table row, or an AC directive of its own -
# lines nobody asked for, written by the tool, over the tool's own signature. NUL is not a line
# break but has no place in a markdown document and truncates in C-backed tooling.
_LINE_BREAK_NAMES: dict[str, str] = {
    "\n": "newline (U+000A)", "\r": "carriage return (U+000D)",
    "\v": "vertical tab (U+000B)", "\f": "form feed (U+000C)",
    "\x1c": "file separator (U+001C)", "\x1d": "group separator (U+001D)",
    "\x1e": "record separator (U+001E)", "\x85": "next line (U+0085)",
    "\u2028": "line separator (U+2028)", "\u2029": "paragraph separator (U+2029)",
    "\x00": "NUL (U+0000)",
}
_LINE_BREAK_RE = re.compile("[" + "".join(re.escape(c) for c in _LINE_BREAK_NAMES) + "]")

# Fields a creator writes into a metadata line, an index cell, or a one-line bullet. Each must
# be a single line or it escapes that construct. The prose fields (summary, steps, fix, impact,
# recommendation) are deliberately absent: they are written into a section body, where more than
# one line is the point.
SINGLE_LINE_FIELDS: tuple[str, ...] = (
    "title", "author", "epic", "persona", "tranche", "priority", "ctype", "severity",
    "effort", "provenance", "date", "theme", "note",
)
# List fields whose every item renders as ONE bullet. An `acs` item is the sharpest of them: a
# break in it injects a sibling `- **Verify:** <command>` line into the AC block, which the
# verifier reads back and RUNS.
SINGLE_LINE_LIST_FIELDS: tuple[str, ...] = ("acs", "options", "verify")


def require_single_line(field: str, value: str) -> str:
    """`value` unchanged, or ValueError naming the field and the character that breaks it.

    Refuse, never strip. A value quietly rewritten is a success the tool did not achieve: the
    caller is handed exit 0 over a record that does not say what they asked it to say. Loud is
    the only honest answer. The refusal is by CHARACTER, not by position: a line break anywhere
    escapes the construct - leading, interior or trailing alike - because the callers write the
    value they were handed, not a trimmed one, and a leading break renders a blank first cell
    then a forged line. A surrounding SPACE is not a line break and is not refused, so a
    caller's untidiness ("  Sam  ") still passes; the distinction is space versus line break,
    never where it sits.
    """
    m = _LINE_BREAK_RE.search(value or "")
    if not m:
        return value
    raise ValueError(
        f"{field} must be a single line - it carries a {_LINE_BREAK_NAMES[m.group(0)]} at "
        f"position {m.start()}: {value!r}. The value would break out of its metadata line, "
        "table cell or bullet and write lines nobody asked for; nothing was written. Remove "
        "the break - detail that needs more than a line belongs in a body section.")


def check_creator_fields(fields: dict) -> None:
    """Refuse, BEFORE a creator writes anything, any supplied field that would break out of the
    metadata line, index cell, or bullet it is written into.

    One guard at one choke point, so every creation path inherits the refusal instead of each
    escaping (or forgetting to escape) separately. Raises ValueError naming the field.

    The RAW value is checked, never a stripped copy: the persona, acs, options and title
    writers emit the value verbatim (`f"> **Persona:** {value}"`, `_md_safe(item)`), so a
    payload whose only break is LEADING would pass a stripped check and then be written in full
    - the exact bypass. The value that is checked here must be the value the writer emits.
    """
    for key in SINGLE_LINE_FIELDS:
        val = fields.get(key)
        if isinstance(val, str):
            require_single_line(key, val)
    for key in SINGLE_LINE_LIST_FIELDS:
        items = fields.get(key)
        if isinstance(items, (list, tuple)):
            for i, item in enumerate(items, 1):
                require_single_line(f"{key}[{i}]", str(item))


def join_row(cells: list[str]) -> str:
    """Render a table row, re-escaping any literal pipe in a cell so a value that contains
    `|` round-trips through `table_cells` without shifting columns. The single row writer
    every index builder shares.

    A cell carrying a line break is REFUSED, not written: escaping the pipe but not the newline
    is what let an author's name split a row across two lines and open a second, forged one.
    The pipe is escapable; the line break is not, so it is a refusal."""
    return "| " + " | ".join(
        require_single_line(f"table cell {i}", c).replace("|", "\\|")
        for i, c in enumerate(cells, 1)) + " |"


def find_data_header(lines: list[str]) -> tuple[int, list[str]] | None:
    """The last index DATA-table header (the row carrying an `ID` column) as (line, cells),
    or None. Locates the data table so a new row never lands in the Summary table. Shared by
    `artifact new` and the finding filer."""
    found = None
    for i, ln in enumerate(lines):
        cells = table_cells(ln)
        if cells and len(cells) > 2 and "id" in [c.lower() for c in cells]:
            found = (i, cells)
    return found


def row_from_header(header: list[str], link: str, title: str, status: str, f: dict) -> str:
    """Build an index data row matching the index's own columns - generic across every type,
    so both create paths emit identical rows. `f` supplies priority/type/severity/
    author/epic/date; unknown columns get `--`."""
    field_for = {"priority": ("priority", "Medium"), "type": ("ctype", "Feature"),
                 "epic": ("epic", "--"), "severity": ("severity", "--"), "author": ("author", "--")}
    out: list[str] = []
    for h in header:
        hl = h.strip().lower()
        if hl == "id":
            out.append(link)
        elif hl in ("title", "description", "feature", "name", "sprint"):
            out.append(title)
        elif hl == "status":
            out.append(status)
        elif hl in ("created", "date", "raised", "updated"):
            out.append(f.get("date", "--"))
        elif hl in field_for:
            key, default = field_for[hl]
            out.append(f.get(key, default))
        else:
            out.append("--")
    return join_row(out)


def extract_field(text: str, name: str) -> str | None:
    """Value of a `**Name:** value` metadata field, or None if absent.

    Handles three shapes: a standalone `> **Name:** value` line, a plain
    `**Name:** value` line (no blockquote), and an inline run where several fields
    share one line separated by `·`, e.g.
    `> **Status:** Done · **Epic:** EP0088 · **Points:** 3`. The field is anchored
    to a line start (optional `>`) or a `·` separator, so a `**Name:**` mentioned
    in prose is not matched; the value is captured up to the next `·`, the next
    `**Field:**`, or end of line, so a field never swallows the ones after it.
    """
    m = re.search(
        rf"(?:^>?\s*|·\s*)\*\*{re.escape(name)}:\*\*\s*(.+?)\s*(?=·|\s\*\*[^*\n]+:\*\*|$)",
        text, re.M)
    return m.group(1) if m else None


def extract_h1_title(text: str) -> str | None:
    """The first `# Heading` text, or None."""
    m = H1_RE.search(text)
    return m.group(1).strip() if m else None


_TRANCHE_RE = re.compile(
    r"\*\*Tranche:\*\*[^\S\n]*([^\n·]*?)\s*(?=·|\s\*\*[^*\n]+:\*\*|$)", re.M)


def tranche_ref(text: str) -> str | None:
    """The record-only tranche reference (EP0014, US0068), or None when absent OR present but
    empty. Unlike the general `extract_field`, the value is captured with horizontal-only leading
    whitespace, so an empty `> **Tranche:**` field never swallows the following line - both the
    `tranche-shape` validation and the `status tranche` query read through here so they agree on
    what a tranche value is."""
    m = _TRANCHE_RE.search(text)
    if not m:
        return None
    return m.group(1).strip() or None


def extract_record_id(stem: str) -> str | None:
    """Artifact ID at the start of a filename stem.

    'US0001-login' -> 'US0001', 'CR-0001-add-auth' -> 'CR-0001'. Returns None
    if the stem carries no recognised artifact ID.
    """
    m = ID_RE.match(stem)
    return m.group(1) if m else None


def extract_ac_id(line: str) -> tuple[str, str] | None:
    """(ac_id, title) from an `### AC1: Title` heading or a `- **AC1:**` bullet."""
    m = AC_HEADING_RE.match(line)
    if m:
        return m.group(1), (m.group(2) or "").strip()
    m = AC_BULLET_RE.match(line)
    if m:
        return m.group(1), (m.group(2) or "").strip()
    return None


def slug(value: str) -> str:
    """Lowercase, hyphenate and trim a string for use as a slug/label component."""
    return _SLUG_RE.sub("-", value.strip().lower()).strip("-")


# -----------------------------------------------------------------------------
# Filesystem
# -----------------------------------------------------------------------------


def walk_glob(dir_path: Path, pattern: str) -> list[Path]:
    """Sorted files in dir_path matching glob `pattern` ([] if the dir is absent)."""
    if not dir_path.exists():
        return []
    return sorted(p for p in dir_path.glob(pattern) if p.is_file())


# -----------------------------------------------------------------------------
# Artifact tables (single source of truth, from reference-outputs.md)
# -----------------------------------------------------------------------------

# type -> (directory relative to repo root, ID prefix). The CR prefix matches
# both `CR0001` and `CR-0001` filenames (the skill is inconsistent; ID_RE and
# the `CR*.md` glob both tolerate the dash).
ARTIFACT_TYPES: dict[str, tuple[str, str]] = {
    "epic": ("sdlc-studio/epics", "EP"),
    "story": ("sdlc-studio/stories", "US"),
    "plan": ("sdlc-studio/plans", "PL"),
    "bug": ("sdlc-studio/bugs", "BG"),
    "cr": ("sdlc-studio/change-requests", "CR"),
    "rfc": ("sdlc-studio/rfcs", "RFC"),
    "test-spec": ("sdlc-studio/test-specs", "TS"),
    "workflow": ("sdlc-studio/workflows", "WF"),
}

# Allowed Status values per artifact type. A status outside this set is a
# validation error (it breaks dashboard/reconcile counting).
STATUS_VOCAB: dict[str, list[str]] = {
    "epic": ["Draft", "Ready", "Approved", "In Progress", "Done"],
    "story": [
        "Proposed", "Draft", "Ready", "Planned", "In Progress", "Review", "Blocked",
        "Done", "Won't Implement", "Deferred", "Superseded",
    ],
    "plan": ["Draft", "In Progress", "Complete", "Superseded"],
    "bug": ["Open", "In Progress", "Fixed", "Verified", "Closed", "Won't Fix", "Superseded"],
    "cr": ["Proposed", "Approved", "In Progress", "Complete", "Rejected", "Deferred", "Superseded", "Blocked"],
    "rfc": ["Draft", "In Review", "Accepted", "Superseded", "Withdrawn"],
    "test-spec": ["Draft", "Ready", "In Progress", "Complete", "Superseded"],
    "workflow": [
        "Created", "Planning", "Testing", "Implementing", "Verifying",
        "Reviewing", "Checking", "Done", "Paused", "Superseded",
    ],
}

# Absorbing (terminal) statuses per type: a unit at one of these is a closed
# outcome whose index row carries no live signal and is a candidate for archival
# Derived from STATUS_VOCAB, not hardcoded at call sites. States that can
# still re-activate - Blocked, Deferred, Paused, Planned - are deliberately NOT
# terminal. Every value here must be a member of the type's STATUS_VOCAB.
TERMINAL_STATUS: dict[str, set[str]] = {
    "epic": {"Done"},
    "story": {"Done", "Won't Implement", "Superseded"},
    "plan": {"Complete", "Superseded"},
    "bug": {"Fixed", "Verified", "Closed", "Won't Fix", "Superseded"},
    "cr": {"Complete", "Rejected", "Superseded"},
    "rfc": {"Accepted", "Superseded", "Withdrawn"},
    "test-spec": {"Complete", "Superseded"},
    "workflow": {"Done", "Superseded"},
}


def terminal_statuses(type_: str) -> set[str]:
    """The absorbing statuses for `type_` - the set whose rows are archive candidates.
    Empty for an unknown type. Intersected with the vocab so it can never name a
    status the type does not define."""
    return set(TERMINAL_STATUS.get(type_, set())) & set(STATUS_VOCAB.get(type_, []))


# Findings (bug/cr/rfc) gain an `inbox` triage lane under schema v3 (EP0014): an
# agent-filed finding lands in `inbox`, and a *different* seat triages it into the
# workflow proper. The triaged target is the first accepted-into-workflow state per
# type - `Proposed` (cr) / `Draft` (rfc) are pre-workflow proposal states an agent
# finding never occupies, so triage promotes straight past them. Dormant under v2.
FINDING_TYPES: tuple[str, ...] = ("bug", "cr", "rfc")
INBOX_STATUS = "inbox"
TRIAGE_TARGET: dict[str, str] = {"bug": "Open", "cr": "Approved", "rfc": "In Review"}


def triage_target(type_: str) -> str | None:
    """The status an `inbox` finding of this type triages into (None for non-findings)."""
    return TRIAGE_TARGET.get(type_)


def is_terminal_status(type_: str, status: str) -> bool:
    """True if `status` is an absorbing state for `type_`."""
    return status in terminal_statuses(type_)


_OVERRIDE_WARNED: set[str] = set()


def _warn_unhonoured(cfg_path: Path, why: str) -> None:
    """Emit a one-line stderr warning (once per file) that a present `.config.yaml` could not
    be honoured, so a project's declared conventions are never SILENTLY ignored. Silent-default
    is the failure class this defends against; the warning never raises."""
    key = str(cfg_path)
    if key in _OVERRIDE_WARNED:
        return
    _OVERRIDE_WARNED.add(key)
    try:
        import sys
        print(f"warning: {cfg_path} exists but was not applied - {why}; using built-in "
              "defaults (config-driven behaviour needs PyYAML)", file=sys.stderr)
    except Exception:  # noqa: BLE001 - a warning must never break a read
        pass


def project_override(repo_root, dotted: str, default=None):
    """Read a dotted key from the project's `sdlc-studio/.config.yaml` (the override
    file only, no defaults merge). Self-contained and fully degrading: a missing
    file, no PyYAML, or malformed YAML all return `default`. This is the reader for
    parser-critical paths that must never hard-depend on PyYAML; the richer merged
    config (defaults + override) lives in config.py."""
    cfg_path = Path(repo_root) / "sdlc-studio" / ".config.yaml"
    if not cfg_path.exists():
        return default
    try:
        import yaml  # soft dependency, mirrors config.py
    except ImportError:
        _warn_unhonoured(cfg_path, "PyYAML is not installed")
        return default
    try:
        cur = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001 - a broken override must never break parsing
        _warn_unhonoured(cfg_path, f"it could not be parsed ({exc})")
        return default
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def status_vocab(type_: str, repo_root=None) -> list[str]:
    """The status vocabulary for a type: the shared base, plus any project-declared
    extensions (`.config.yaml` `status_vocab.<type>`) when a repo_root is given.
    Pass the repo root so a consuming project's custom statuses (e.g. `Gated`) are
    recognised by reconcile/validate/conformance instead of parsing as Unknown."""
    base = list(STATUS_VOCAB.get(type_, []))
    if repo_root is None:
        return base
    # schema v3: findings gain an `inbox` triage lane prepended before the first state
    # (dormant under v2, where is_schema_v3 is False, so existing vocab is untouched).
    if type_ in FINDING_TYPES and is_schema_v3(repo_root):
        base = [INBOX_STATUS] + base
    extra = project_override(repo_root, f"status_vocab.{type_}", [])
    extra = [str(s) for s in extra] if isinstance(extra, list) else []
    return base + [s for s in extra if s not in base]


# Remediation hints: per check, a one-line "how to fix" for each finding-kind, so a
# check tells the operator what to do, not just what is wrong. One source
# reused by every check's text output.
REMEDIATION: dict[str, dict[str, str]] = {
    "conformance": {
        "decomposed": "add the `> **Epic:**` link to the story",
        "specified": "add an `## Acceptance Criteria` section with at least one AC",
        "verifiable": "add a `- **Verify:** <cmd>` line per AC (or, if this project does not use executable AC, scope this stage out)",
        "verified": "run `verify_ac` and back-annotate `- **Verified:** yes` (Done stories)",
        "reconciled": "index drift - run `reconcile` and fix the row/counts",
        "critiqued": "record an independent-critic verdict: `critic.py record --unit <id> --verdict approve` (author != reviewer; at sprint close the adversarial full-diff pass re-runs its own repros before approving - reference-sprint.md)",
        "promoted": "this story is still a planning-tier scaffold - run `artifact.py promote --id <id> --to full` to add the sections it deferred (constraint chain, edge cases, test scenarios, rollback envelope)",
    },
    "integrity": {
        "missing-required": "add the required link field (Epic/Story); a standalone bug may leave it (advisory)",
        "dangling": "fix or remove the reference - the id resolves to no artifact on disk",
    },
    "audit": {
        "weak-AC": "replace the placeholder/empty AC with concrete, checkable acceptance criteria",
        "underspecified": "add Steps to Reproduce and a Proposed Fix to the bug",
        "unmet-deps": "deliver or re-order the dependency first (it is not yet done)",
        "unresolved-deps": "check out the sibling repo the product manifest names (or fix its path) - the dependency could not be checked either way",
        "already-terminal": "already Complete/Done - drop it from the batch",
        "link-integrity": "fix the artifact's required links (see the integrity check)",
        "not-found": "the id matches no artifact on disk - check the batch list",
    },
    "reconcile": {
        "status-mismatch": "set the index row's Status to match the file (or fix the file)",
        "missing-row": "add an index row for this artifact",
        "orphan-row": "remove the index row - no file backs it (or restore the file)",
        "missing-index": "create the type's `_index.md`",
        "count-mismatch": "recompute the summary counts from the index rows",
    },
}


def remediation_lines(check: str, kinds) -> list[str]:
    """Fix-hint lines for the finding-kinds present, in registry (stable) order."""
    present = set(kinds)
    return [f"{kind} -> {hint}" for kind, hint in REMEDIATION.get(check, {}).items() if kind in present]


def norm_id(rec: str) -> str:
    """Case- and punctuation-insensitive comparison key for an artifact ID.

    Files often use one id format and an index another (e.g. `CR0001` on disk
    vs `CR-0001` in a table). Both normalise to `CR0001` so they match instead
    of being treated as two different records.
    """
    return re.sub(r"[^A-Za-z0-9]", "", rec).upper()


def canonical_status(raw: str | None, vocab: list[str]) -> str | None:
    """Reduce a decorated status line to its canonical vocabulary token.

    Projects often append release context, e.g.
    `Done (v2.83.0) · **CR:** CR-0088 · **Points:** 8`. The canonical status is
    the vocabulary term that prefixes the (bold-stripped) text. Returns None if
    no vocab term prefixes it (a genuinely unrecognised status still surfaces).
    """
    if not raw:
        return None
    s = raw.replace("*", "").strip()
    low = s.lower()
    # Longest term first so multi-word terms ('In Progress') win over a prefix.
    for term in sorted(vocab, key=len, reverse=True):
        t = term.lower()
        if low == t or (low.startswith(t) and not low[len(t):len(t) + 1].isalnum()):
            return term
    return None


def iter_artifact_files(type_: str, repo_root: Path, trust_names=frozenset()):
    """Yield `(path, text)` for each artifact file of `type_`. `text` is the file's content,
    read to apply the is-artifact filter - EXCEPT for a filename in `trust_names`, which is
    yielded as `(path, None)` WITHOUT being read. A caller that already knows a file is a
    closed artefact (e.g. from a digest keyed by filename) passes its name here to skip the
    read - the context-tiering optimisation. The filter/exclusion rules match `artifact_files`;
    only the read is elided for trusted names.
    """
    if type_ not in ARTIFACT_TYPES:
        return
    try:  # late import: conventions imports this module at load time
        from lib import conventions
    except ImportError:
        import conventions  # type: ignore
    rel, prefix = ARTIFACT_TYPES[type_]
    want = prefix.upper()
    suffixes = tuple(f"-{s}" for s in conventions.companion_suffixes(repo_root))
    # Glob all markdown and filter by the (case-insensitive) record ID rather
    # than a `{prefix}*.md` glob: `Path.glob` is case-sensitive on Linux, so a
    # `CR*.md` pattern silently misses repos that name files `cr0001.md`.
    for p in walk_glob(repo_root / rel, "*.md"):
        if p.name == "_index.md" or (suffixes and p.stem.endswith(suffixes)):
            continue
        rec = extract_record_id(p.stem)
        if not (rec and norm_id(rec).startswith(want)):
            continue
        if p.name in trust_names:
            yield p, None  # trusted closed artefact: no read (digest already vetted it)
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            yield p, None  # unreadable: keep it visible so a checker names it
            continue
        if conventions.is_artifact(text):
            yield p, text


def artifact_files(type_: str, repo_root: Path) -> list[Path]:
    """All artifact files of `type_` under repo_root.

    Excludes `_index.md`, declared companion suffixes (default
    `*-consultations.md`), and any file carrying no artifact header at all
    (no `> **Status:**` line and no `# <ID>:` title) - a companion/note filed
    under an artifact's ID (e.g. `EP0025-...-decisions.md`) would otherwise
    double-count the ID and pollute status tallies with a status-less
    namesake. A file with an `# <ID>:` title but no Status line is still an
    artifact: it stays in the set so validate can flag it.
    """
    return [p for p, _ in iter_artifact_files(type_, repo_root)]


def id_number(record_id: str) -> int | None:
    """Numeric part of a v2 sequential ID ('US0042' -> 42, 'CR-0007' -> 7). A v3 ULID id
    ('BG-01JQK3F8') has no sequential number - even one whose suffix ends in digits - so this
    returns None for it, keeping ULID ids out of the max+1 numeric allocation path."""
    # letters, optional dash, then EXACTLY four trailing digits and nothing else. This admits
    # any sequential prefix (US, CR, and the meta ids LL/RV/RETRO) but never a v3 ULID, whose
    # 8+-char base32 suffix cannot fullmatch a bare 4-digit tail.
    m = re.fullmatch(r"[A-Za-z]+-?(\d{4})", record_id)
    return int(m.group(1)) if m else None


_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"  # Crockford base32 (no I, L, O, U)


def b32(value: int, length: int) -> str:
    """Encode the low bits of `value` as `length` Crockford-base32 chars, most-significant first."""
    out = []
    for _ in range(length):
        out.append(_CROCKFORD[value & 0x1F])
        value >>= 5
    return "".join(reversed(out))


_V3_ID_RE = re.compile(r"^[A-Za-z]{1,6}-[" + _CROCKFORD + r"]{8,}$", re.IGNORECASE)


def is_v3_id(record_id: str) -> bool:
    """True when `record_id` is a well-formed v3 short-ULID id (`BG-01JQK3F8`): a type prefix,
    a dash, then 8+ Crockford-base32 chars. Distinguishes a real ULID id from a v2 sequential
    (`CR-0007`, whose 4-char numeric tail is too short) and from an arbitrary dashed string."""
    return bool(_V3_ID_RE.match(record_id or ""))


def atomic_write(path, text: str, encoding: str = "utf-8") -> None:
    """Write `text` to `path` atomically: a same-directory temp file then `os.replace`, so a
    crash mid-write leaves the previous file intact rather than a truncated one, and a reader
    never sees a half-written index. The temp is cleaned up on any failure."""
    import os
    import tempfile
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".tmp-", suffix=p.suffix or ".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as fh:
            fh.write(text)
        # mkstemp makes the temp 0600; os.replace keeps the temp's mode, so without this every
        # atomic_write would silently flip an index/artefact to owner-only (breaking shared
        # checkouts / web-served docs). Preserve the existing file's mode, else apply umask.
        try:
            os.chmod(tmp, os.stat(p).st_mode & 0o777)
        except FileNotFoundError:
            cur = os.umask(0o022)
            os.umask(cur)
            os.chmod(tmp, 0o666 & ~cur)
        os.replace(tmp, str(p))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


@contextlib.contextmanager
def allocation_lock(repo_root, timeout: float = 10.0):
    """Advisory cross-process lock around id allocation + write, so two concurrent writers do
    not mint the same sequential id or clobber a shared index. Best-effort: a no-op where
    `flock` is unavailable (Windows), and it proceeds rather than hang if the lock cannot be
    taken within `timeout` (a stale lock must never wedge an agent wave). v3 ULID allocation
    is already collision-free, so this most matters for the v2 sequential path."""
    import time
    lockdir = Path(repo_root) / "sdlc-studio" / ".local"
    try:
        lockdir.mkdir(parents=True, exist_ok=True)
        import fcntl
    except (OSError, ImportError):
        yield  # non-POSIX or unwritable: degrade to no lock
        return
    fh = open(lockdir / "allocation.lock", "w")  # noqa: SIM115 - released in finally
    try:
        deadline = time.time() + timeout
        while True:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.time() > deadline:
                    break  # contended past the timeout: proceed rather than wedge the wave
                time.sleep(0.02)
        yield
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fh.close()


def schema_version(repo_root) -> int:
    """The project's artefact schema version (`schema_version` in `.config.yaml`), defaulting
    to 2. v3 turns on ULID identity and the structured-authorship / evidence enforcement."""
    v = project_override(repo_root, "schema_version", None)
    try:
        return int(v) if v is not None else 2
    except (TypeError, ValueError):
        return 2


def is_schema_v3(repo_root) -> bool:
    """True when the project opted into schema v3 (the team-schema rules apply)."""
    return schema_version(repo_root) >= 3


def profile(repo_root) -> str:
    """The project's pipeline profile (`profile` in `.config.yaml`): `lite` or `full`,
    defaulting to `full`. Lite collapses the pipeline to PRD -> story -> implement (no
    TRD/TSD/persona/epic layer), so the ceremony never outweighs a small codebase. Any
    unrecognised value degrades to `full` - the profile only ever relaxes discipline
    when explicitly asked."""
    return "lite" if str(project_override(repo_root, "profile", "full")).strip().lower() \
        == "lite" else "full"


def parse_authorship_value(raw: str | None) -> dict | None:
    """Parse an already-extracted `Name; type; version` value into `{name, type, version}`
    (type lower-cased). None when the value is absent/empty. Lets a caller parse a raw
    authorship value (e.g. a `--triaged-by` argument) without reconstructing a metadata line."""
    if not raw:
        return None
    parts = [p.strip() for p in raw.split(";")]
    return {"name": parts[0] if parts else "",
            "type": (parts[1].lower() if len(parts) > 1 else ""),
            "version": parts[2] if len(parts) > 2 else ""}


def parse_authorship(text: str, field: str = "Raised-by") -> dict | None:
    """Parse a typed authorship reference `Name; type; version` from a `> **Field:**` metadata
    line into `{name, type, version}` (type lower-cased). None when the field is absent. The
    resolver treats `type` as one of human | persona | agent - persona today, agent later,
    with no schema change."""
    return parse_authorship_value(extract_field(text, field))


AUTHOR_TYPES = ("human", "persona", "agent")
# The identity a creator stamps when the caller named nobody: the tool acted on an agent's
# behalf, and says so rather than attributing the artefact to a person who did not raise it.
DEFAULT_AGENT_AUTHOR = "sdlc-studio; agent; v1"


def authorship_value(author: str | None, repo_root) -> str:
    """The `Name; type; version` authorship a creator stamps as `Raised-by`.

    One resolver for every creation path, so a minted artefact always satisfies the
    schema-v3 authorship rule. `author` may be a typed triple (`Dani Okafor; agent; v2` -
    carried verbatim) or a bare name, whose type is inferred: `persona` when it resolves to
    a persona document, else `human` (a named author is a person until a persona says
    otherwise). With no author at all, the invoking agent's identity is used - `SDLC_AUTHOR`
    from the environment when set, else the tool's own. An unknown type raises rather than
    minting an artefact the validator will reject.

    A multi-line author is REFUSED here, at the one resolver every creation path calls, rather
    than escaped separately by each. The value is written into a `> **Raised-by:**` metadata
    line AND an index cell AND a revision row: a line break in it escapes all three, letting
    whoever supplies the name write arbitrary metadata lines under the tool's signature - the
    provenance tooling forging provenance.
    """
    raw = require_single_line("author", (author or "").strip())
    if not raw:
        raw = require_single_line("SDLC_AUTHOR", os.environ.get("SDLC_AUTHOR", "").strip()) \
            or DEFAULT_AGENT_AUTHOR
    parsed = parse_authorship_value(raw) or {}
    name = (parsed.get("name") or "").strip()
    if not name:
        parsed = parse_authorship_value(DEFAULT_AGENT_AUTHOR)
        name = parsed["name"]
    atype = (parsed.get("type") or "").strip().lower()
    if not atype:
        atype = "persona" if resolve_author(name, "persona", repo_root) else "human"
    if atype not in AUTHOR_TYPES:
        raise ValueError(f"author type {atype!r} must be one of {' | '.join(AUTHOR_TYPES)} "
                         f"(pass --author 'Name; type; version')")
    return f"{name}; {atype}; {(parsed.get('version') or '').strip() or 'v1'}"


def authorship_name(value: str | None) -> str:
    """The display NAME of an authorship value, for a Revision History Author cell.

    The history table names who acted; the typed triple lives in the `Raised-by` field, so a
    cell takes `Dani Okafor`, not `Dani Okafor; agent; v2`. Accepts either form (a bare name
    passes through). With nothing resolvable, the tool's own identity is named rather than a
    hardcoded literal - a creator must never mint a false provenance record.

    A formatter, NOT a resolver: it reads the value it is handed and does not consult
    `SDLC_AUTHOR`. Feed it the output of `authorship_value()` (which does), never a raw
    `--author` that may be empty - on `None` it names the tool, silently passing over an
    invoking agent that `authorship_value` would have found.
    """
    parsed = parse_authorship_value(value) or {}
    return (parsed.get("name") or "").strip() \
        or parse_authorship_value(DEFAULT_AGENT_AUTHOR)["name"]


def resolve_author(name: str, atype: str, repo_root) -> bool:
    """Whether a typed authorship reference resolves. `human`/`agent` always validate (git
    identity / reserved for later); `persona` must match a document under `sdlc-studio/personas/`
    (including `amigos/`) by display name or filename. Unknown type -> False."""
    if atype in ("human", "agent"):
        return True
    if atype != "persona":
        return False
    pdir = Path(repo_root) / "sdlc-studio" / "personas"
    if not pdir.exists():
        return False
    key = re.sub(r"[^a-z0-9]", "", (name or "").lower())
    if not key:
        return False
    for p in pdir.rglob("*.md"):
        if p.name == "index.md" or p.name.startswith("_"):
            continue
        title = extract_h1_title(p.read_text(encoding="utf-8")) or p.stem
        blob = re.sub(r"[^a-z0-9]", "", f"{title} {p.stem}".lower())
        if key in blob:
            return True
    return False


def alias_map(repo_root) -> dict[str, str]:
    """Map every artefact alias (normalised) -> its current canonical id, read from the
    `> **Aliases:** OLD1, OLD2` metadata line. Lets a reader resolve a pre-migration id to the
    current ULID after a v2 -> v3 migration. Empty when nothing has been migrated."""
    out: dict[str, str] = {}
    root = Path(repo_root)
    for type_ in ARTIFACT_TYPES:
        for p in artifact_files(type_, root):
            canonical = extract_record_id(p.stem)
            if not canonical:
                continue
            text = p.read_text(encoding="utf-8")
            raw = extract_field(text, "Aliases")
            for a in re.split(r"[,\s]+", (raw or "").strip()):
                if a:
                    out[norm_id(a)] = canonical
            # A synced artefact's GitHub issue number is a friendly alias too, so an operator
            # can look an artefact up by `GH42`; the ULID stays the canonical identity.
            issue = extract_field(text, "GitHub Issue")
            if issue:
                m = re.search(r"\d+", issue)
                if m:
                    out[norm_id(f"GH{m.group(0)}")] = canonical
    return out


def find_by_id(repo_root, rec_id: str):
    """(path, type) of the artefact with this id across all types, or None. Resolves a
    pre-migration id through the `alias_map` (a `--id US0001` still works after a v2 -> v3
    migration). The single lookup that `transition` and `audit` delegate to, so a fix to
    id-resolution lands in one place."""
    root = Path(repo_root)
    norm = norm_id(rec_id)
    for type_ in ARTIFACT_TYPES:
        for p in artifact_files(type_, root):
            rec = extract_record_id(p.stem)
            if rec and norm_id(rec) == norm:
                return p, type_
    aliased = alias_map(root).get(norm)
    if aliased and norm_id(aliased) != norm:
        return find_by_id(root, aliased)
    return None


_EPIC_FIELD = re.compile(r"(?m)^>?[^\S\n]*\*\*Epic:\*\*[^\S\n]*(.*)$")


def story_epic(source) -> str | None:
    """The epic a story names (`> **Epic:** ...`), or None when it has none (`-`/`--`/absent).
    Accepts the story text or a `Path`. Same-line capture so a blank field is not a phantom
    match of the next line. The canonical reader the story/epic helpers delegate to."""
    text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
    m = _EPIC_FIELD.search(text)
    if not m:
        return None
    val = m.group(1).strip()
    return None if val in ("", "-", "--") else val


def new_ulid() -> str:
    """A 26-char Crockford-base32 ULID: a 48-bit millisecond timestamp (lexicographically
    sortable = creation order) followed by 80 bits of randomness. Collision-free across
    concurrent writers without coordination."""
    import os
    import time
    ms = int(time.time() * 1000) & ((1 << 48) - 1)
    return b32(ms, 10) + b32(int.from_bytes(os.urandom(10), "big"), 16)


def short_ulid() -> str:
    """The 8-char id suffix: 6 timestamp chars (so short ids coarsely sort in creation order -
    the truncated prefix resolves to roughly a 17-minute bucket) + 2 random chars. The old
    pure-timestamp prefix carried NO entropy, so two uncoordinated writers in the same ~1ms
    window minted the SAME id; the random tail makes an in-window collision improbable
    (~1/1024) rather than certain. Extended by the allocator on a rare directory clash - that
    glob-retry is the true single-writer backstop, the tail only narrows the concurrent window."""
    u = new_ulid()  # 10 timestamp chars + 16 random chars
    return u[:6] + u[10:12]


def mint_v3_id(root: Path, type_: str) -> str:
    """A collision-checked v3 id (`BG-01JQK3F8`) for a new artefact of `type_` - the ONE
    era-v3 allocator, shared by `artifact new` and the finding filer so both paths mint the
    same form. Retries against the type directory, then extends the suffix on a persistent
    clash."""
    prefix = ARTIFACT_TYPES[type_][1]
    d = Path(root) / ARTIFACT_TYPES[type_][0]
    for _ in range(16):
        ident = f"{prefix}-{short_ulid()}"
        if not (d.exists() and any(d.glob(f"{ident}-*.md"))):
            return ident
    return f"{prefix}-{new_ulid()[:12]}"  # extend the suffix on a persistent clash


def parse_cutoff(value) -> int | None:
    """The one adoption-cutoff parser shared by every gate (conformance, provenance).

    Accepts both spellings the operator might write in `.config.yaml` `*.adopt_after`:
    a bare integer (`57`, `103`, or the string `"57"`) AND a prefixed id (`US0103`,
    `CR0103`, `US-0103`). Returns the numeric id. `None` means no cutoff is set (a
    legitimate "judge everything"). An unparseable value raises ValueError rather than
    returning None - a config typo must fail loud, never silently disable the gate
    (lesson LL0008). The cutoff is the highest id treated as legacy: ids <= it are exempt.
    """
    if value is None:
        return None
    if isinstance(value, bool):  # bool is an int subclass; a YAML true/false is not a cutoff
        raise ValueError(f"adopt_after cutoff is not a number or id: {value!r}")
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if re.fullmatch(r"\d+", s):  # bare integer, possibly as a string
        return int(s)
    n = id_number(s)  # prefixed id (US0103, CR-0103)
    if n is not None:
        return n
    raise ValueError(
        f"adopt_after cutoff is not a number or id: {value!r} - "
        "use a bare integer (103) or a prefixed id (US0103)")


def affects_files(text: str) -> list[str]:
    """File paths a unit declares it will touch (its `Affects` field).

    Shared by the sprint planner (WSJF complexity seed) and the routing estimator
    One parser, one behaviour. Tolerates trailing parentheticals and
    backtick-wrapped paths; a token counts as a path when it contains a `/` or a
    known source/doc extension."""
    val = extract_field(text, "Affects") or ""
    files = []
    for tok in val.split(","):
        tok = re.sub(r"\s*\(.*\)\s*$", "", tok.strip()).strip().strip("`").strip()
        if tok and ("/" in tok or tok.endswith((".py", ".md", ".yaml", ".yml", ".sh"))):
            files.append(tok)
    return files


def resolve_affects(root, p: str):
    """Resolve an Affects path against the repo root or the installed skill dir.
    Returns the resolved Path, or None for a not-yet-existing (greenfield) path."""
    root = Path(root)
    for base in (root, root / ".claude" / "skills" / "sdlc-studio"):
        cand = base / p
        if cand.exists():
            return cand
    return None


_AC_CHECKBOX_RE = re.compile(r"^\s*- \[[ xX]\] ")


def count_acs(text: str) -> int:
    """Checkable AC items inside the Acceptance Criteria section (checkbox lines,
    `### ACn` headings, or `**ACn**` bullets). The same recognition set audit.py's
    weak-AC check uses - shared so the routing estimator and the tranche
    audit count the same things."""
    count = 0
    in_ac = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if not in_ac:
            continue
        if (_AC_CHECKBOX_RE.match(line) or AC_HEADING_RE.match(line)
                or AC_BULLET_RE.match(line)):
            count += 1
    return count


# -----------------------------------------------------------------------------
# CLI argument grammar (shared so every script's id list reads the same way)
#
# One convention across the script family: a batch verb takes ids as a repeatable
# `--id` OR a single comma-separated `--ids` (the legacy spelling, kept as an alias).
# `add_ids_argument` declares both on a subparser; `resolve_ids` merges whichever the
# caller supplied into one de-duplicated, order-preserving list. A single-target verb
# keeps a scalar `--id` and needs neither helper.
# -----------------------------------------------------------------------------
def add_ids_argument(parser, *, dest: str = "id", help_: str | None = None) -> None:
    """Declare the canonical id-list pair on a batch subparser: a repeatable `--id`
    plus a legacy comma-separated `--ids`. Read them back with `resolve_ids(args)`."""
    parser.add_argument("--id", action="append", dest=dest, metavar="ID",
                        help=help_ or ("artifact id; repeat --id for several, or pass "
                                       "--ids as one comma-separated list"))
    parser.add_argument("--ids", dest="ids",
                        help="legacy: comma-separated ids (equivalent to repeating --id)")


def add_format_arg(parser, *, default: str = "text") -> None:
    """Declare the standard `--format {text,json}` on a report/check subparser, so every
    machine-readable verb spells its output switch the same way."""
    parser.add_argument("--format", choices=("text", "json"), default=default,
                        help="output format (default: %s)" % default)


def add_global_root(parser) -> None:
    """Make `--root` uniform across the script family: valid BEFORE or AFTER the
    subcommand. Call once at the end of `build_parser`, on the top-level parser.

    It declares `--root` (default '.', dest 'root') on the top-level parser so
    `prog --root X sub` parses, and re-points every per-subcommand `--root` that binds
    the standard `root` dest to `argparse.SUPPRESS` so `prog sub --root Y` still
    overrides without the subparser default clobbering a value given before the
    subcommand. Every `--root` in the family binds the standard `root` dest (the
    conformance sweep forbids a `--root` bound to any other dest, since the global
    could not populate it and the two positions would silently diverge). A legacy
    spelling like `run`'s `--repo-root` is kept as an alias onto that same `root` dest,
    never a separate one. Idempotent: safe on a parser that already
    carries a top-level `--root`, and a no-op on subcommands that never declared one
    (they inherit the global value)."""
    def _std_root(action) -> bool:
        return "--root" in action.option_strings and action.dest == "root"

    top_root = next((a for a in parser._actions if _std_root(a)), None)
    if top_root is None:
        top_root = parser.add_argument("--root", default=".", help="Repo root (default: .)")
    # SUPPRESS every standard-dest per-subcommand `--root` so it does not overwrite a
    # value given before the verb. Skip an action aliased with the top-level one (a
    # `parents=` idiom shares the object) - mutating it would corrupt the global.
    for a in parser._actions:
        if isinstance(a, argparse._SubParsersAction):
            for sp in a.choices.values():
                for x in sp._actions:
                    if _std_root(x) and x is not top_root:
                        x.default = argparse.SUPPRESS
    top_root.default = "."


def resolve_ids(args, *, dest: str = "id") -> list[str]:
    """The id list from a parser built with `add_ids_argument` - `--id` (scalar or
    repeated) and `--ids` (comma list) merged, whitespace-trimmed, de-duplicated in
    first-seen order. Empty list when neither was given (the command decides if that
    is an error)."""
    out: list[str] = []
    v = getattr(args, dest, None)
    if isinstance(v, str):
        out.append(v)
    elif isinstance(v, list):
        out.extend(v)
    raw = getattr(args, "ids", None)
    if raw:
        out.extend(s.strip() for s in raw.split(",") if s.strip())
    seen: set[str] = set()
    return [x for x in (s.strip() for s in out) if x and not (x in seen or seen.add(x))]
