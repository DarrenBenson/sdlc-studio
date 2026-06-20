#!/usr/bin/env python3
"""Shared parsing and utility helpers for sdlc-studio scripts.

Single source of truth for the markdown conventions the runtime scripts
parse - metadata fields (`> **Name:** value`), artifact IDs, AC blocks - plus
the small utilities (UTC timestamps, safe JSON load, slug, glob) that the
scripts would otherwise each re-implement. Pure stdlib.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")

# -----------------------------------------------------------------------------
# Canonical markdown conventions (the single source of truth for parsing)
# -----------------------------------------------------------------------------

# A metadata line: `> **FieldName:** value`. group(1)=name, group(2)=value.
METADATA_FIELD_RE = re.compile(r"^>\s*\*\*([^*]+):\*\*\s*(.+?)\s*$", re.M)
# First `# Heading` of a document.
H1_RE = re.compile(r"^#\s+(.+)$", re.M)
# Artifact ID prefix at the start of a filename stem. CR/RFC display with a
# dash (CR-0001); the others do not (US0001). The optional dash matches both.
# Case-insensitive: some repos name files lowercase (`cr0001.md`) while indexes
# use uppercase (`CR-0001`) — both must parse to the same ID.
ID_RE = re.compile(r"^((?:EP|US|PL|BG|TS|WF|RFC|CR)-?\d{4})", re.IGNORECASE)
# Same, unanchored - finds an ID anywhere (e.g. inside an index table cell
# `[US0001](US0001-login.md)`). RFC before CR so `RFC-0001` is not read as `CR`.
ID_SEARCH_RE = re.compile(r"(?<![A-Za-z])(?:EP|US|PL|BG|TS|WF|RFC|CR)-?\d{4}", re.IGNORECASE)
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
        return default
    try:
        cur = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 - a broken override must never break parsing
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
    extra = project_override(repo_root, f"status_vocab.{type_}", [])
    extra = [str(s) for s in extra] if isinstance(extra, list) else []
    return base + [s for s in extra if s not in base]


# Remediation hints: per check, a one-line "how to fix" for each finding-kind, so a
# check tells the operator what to do, not just what is wrong (CR0025). One source
# reused by every check's text output.
REMEDIATION: dict[str, dict[str, str]] = {
    "conformance": {
        "decomposed": "add the `> **Epic:**` link to the story",
        "specified": "add an `## Acceptance Criteria` section with at least one AC",
        "verifiable": "add a `- **Verify:** <cmd>` line per AC (or, if this project does not use executable AC, scope this stage out)",
        "verified": "run `verify_ac` and back-annotate `- **Verified:** yes` (Done stories)",
        "reconciled": "index drift - run `reconcile` and fix the row/counts",
        "critiqued": "record an independent-critic verdict: `critic.py record --unit <id> --verdict approve`",
    },
    "integrity": {
        "missing-required": "add the required link field (Epic/Story); a standalone bug may leave it (advisory)",
        "dangling": "fix or remove the reference - the id resolves to no artifact on disk",
    },
    "audit": {
        "weak-AC": "replace the placeholder/empty AC with concrete, checkable acceptance criteria",
        "underspecified": "add Steps to Reproduce and a Proposed Fix to the bug",
        "unmet-deps": "deliver or re-order the dependency first (it is not yet done)",
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


def artifact_files(type_: str, repo_root: Path) -> list[Path]:
    """All artifact files of `type_` under repo_root.

    Excludes `_index.md` and `*-consultations.md` — the latter are supplementary
    notes filed under an artifact's ID (e.g. `EP0025-consultations.md`), not
    artifacts of that type, so counting them double-counts the ID and pollutes
    status tallies with a status-less namesake.
    """
    if type_ not in ARTIFACT_TYPES:
        return []
    rel, prefix = ARTIFACT_TYPES[type_]
    want = prefix.upper()
    # Glob all markdown and filter by the (case-insensitive) record ID rather
    # than a `{prefix}*.md` glob: `Path.glob` is case-sensitive on Linux, so a
    # `CR*.md` pattern silently misses repos that name files `cr0001.md`.
    out: list[Path] = []
    for p in walk_glob(repo_root / rel, "*.md"):
        if p.name == "_index.md" or p.stem.endswith("-consultations"):
            continue
        rec = extract_record_id(p.stem)
        if rec and norm_id(rec).startswith(want):
            out.append(p)
    return out


def id_number(record_id: str) -> int | None:
    """Numeric part of an artifact ID ('US0042' -> 42, 'CR-0007' -> 7)."""
    m = re.search(r"(\d{4})$", record_id)
    return int(m.group(1)) if m else None
