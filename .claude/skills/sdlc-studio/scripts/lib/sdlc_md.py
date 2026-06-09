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
ID_RE = re.compile(r"^((?:EP|US|PL|BG|TS|WF|RFC|CR)-?\d{4})")
# Same, unanchored - finds an ID anywhere (e.g. inside an index table cell
# `[US0001](US0001-login.md)`). RFC before CR so `RFC-0001` is not read as `CR`.
ID_SEARCH_RE = re.compile(r"(?<![A-Za-z])(?:EP|US|PL|BG|TS|WF|RFC|CR)-?\d{4}")
# Acceptance-criterion heading: `### AC1: Title`.
AC_HEADING_RE = re.compile(r"^###\s+(AC\d+)(?::\s*(.*))?$")
# AC verifier bullets.
VERIFY_RE = re.compile(r"^(\s*)-\s*\*\*Verify:\*\*\s*(.+?)\s*$")
VERIFIED_RE = re.compile(
    r"^(\s*)-\s*\*\*Verified:\*\*\s*(yes|no|stale|manual)\s*(?:\(([^)]*)\))?\s*$",
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


def extract_field(text: str, name: str) -> str | None:
    """Value of a `> **Name:** value` metadata line, or None if absent."""
    m = re.search(rf"^>\s*\*\*{re.escape(name)}:\*\*\s*(.+?)\s*$", text, re.M)
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
    """(ac_id, title) from an `### AC1: Title` heading line, or None."""
    m = AC_HEADING_RE.match(line)
    if not m:
        return None
    return m.group(1), (m.group(2) or "").strip()


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
        "Draft", "Ready", "Planned", "In Progress", "Review", "Done",
        "Won't Implement", "Deferred", "Superseded",
    ],
    "plan": ["Draft", "In Progress", "Complete", "Superseded"],
    "bug": ["Open", "In Progress", "Fixed", "Verified", "Closed", "Won't Fix"],
    "cr": ["Proposed", "Approved", "In Progress", "Complete", "Rejected", "Deferred"],
    "rfc": ["Draft", "In Review", "Accepted", "Superseded", "Withdrawn"],
    "test-spec": ["Draft", "Ready", "In Progress", "Complete", "Superseded"],
    "workflow": [
        "Created", "Planning", "Testing", "Implementing", "Verifying",
        "Reviewing", "Checking", "Done", "Paused", "Superseded",
    ],
}


def artifact_files(type_: str, repo_root: Path) -> list[Path]:
    """All artifact files of `type_` under repo_root (excludes `_index.md`)."""
    if type_ not in ARTIFACT_TYPES:
        return []
    rel, prefix = ARTIFACT_TYPES[type_]
    return [
        p for p in walk_glob(repo_root / rel, f"{prefix}*.md")
        if p.name != "_index.md"
    ]


def id_number(record_id: str) -> int | None:
    """Numeric part of an artifact ID ('US0042' -> 42, 'CR-0007' -> 7)."""
    m = re.search(r"(\d{4})$", record_id)
    return int(m.group(1)) if m else None
