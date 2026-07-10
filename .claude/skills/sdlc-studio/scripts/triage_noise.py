#!/usr/bin/env python3
"""SDLC Studio triage noise controls (schema v3 only - dormant under schema_version: 2).

Two creation-time controls keep a flood of agent-filed findings from burying the few that
matter (EP0014):

- **Session cap.** One session may file at most `triage.session_cap` findings; the N+1th is
  refused loudly (never a silent drop). A session is keyed by the `SDLC_TRIAGE_SESSION`
  environment variable (default `"default"`), so an orchestrator starts a fresh budget per run
  by setting a new value; the count persists in the gitignored
  `sdlc-studio/.local/triage-session.json`.
- **Low-severity consolidation.** With `triage.low_consolidation`, a Low-severity finding folds
  into a themed consolidation CR (one per theme) rather than minting its own artefact; Medium and
  above always get individual artefacts.

Both `file_finding.py` and `artifact.py` route finding creation through here, so neither path is
a bypass. Pure stdlib bar the soft PyYAML dependency behind `config.get` (the v3 path already
needs it to have read `schema_version: 3`).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import config  # noqa: E402  (sibling - merged defaults + project override)
import next_id  # noqa: E402
# file_finding is imported lazily inside _new_consolidation_cr: file_finding imports this
# module at load time, so a top-level import here would be a cycle.

_LOW_TOKENS = {"low", "p4", "trivial", "minor"}


def _cfg(root, key: str, default):
    try:
        return config.get(root, f"triage.{key}", default)
    except Exception:  # noqa: BLE001 - config must never break a creation path
        return default


def session_cap(root) -> int:
    try:
        return int(_cfg(root, "session_cap", 20))
    except (TypeError, ValueError):
        return 20


def low_consolidation(root) -> bool:
    return bool(_cfg(root, "low_consolidation", True))


def is_low(severity: str | None) -> bool:
    """True when a severity/priority token means Low (case- and scheme-tolerant)."""
    return (severity or "").strip().lower() in _LOW_TOKENS


def _session_key() -> str:
    return os.environ.get("SDLC_TRIAGE_SESSION", "default")


def _state_path(root) -> Path:
    return Path(root) / "sdlc-studio" / ".local" / "triage-session.json"


def session_count(root) -> int:
    """Findings filed in the current session (0 when the stored session key differs, i.e. a
    new session, or the state is absent/unreadable)."""
    p = _state_path(root)
    if not p.exists():
        return 0
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return int(d.get("count", 0)) if d.get("session") == _session_key() else 0
    except Exception:  # noqa: BLE001 - a corrupt counter must not break filing
        return 0


def enforce_session_cap(root) -> None:
    """Raise loudly when the session has already filed `session_cap` findings. Call BEFORE
    minting a new finding artefact; a no-op unless the project is schema v3."""
    if not sdlc_md.is_schema_v3(root):
        return
    cap = session_cap(root)
    if session_count(root) >= cap:
        raise ValueError(
            f"triage session cap reached ({cap} findings filed this session) - refusing to file "
            "more. Fail loud, not silent drop: triage the backlog, raise triage.session_cap, or "
            "start a new session (set the SDLC_TRIAGE_SESSION environment variable).")


def record_creation(root) -> int:
    """Count one minted finding against the session budget; returns the new count. No-op
    (returns 0) unless schema v3. Call AFTER a new finding artefact is written."""
    if not sdlc_md.is_schema_v3(root):
        return 0
    cur = session_count(root)
    p = _state_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"session": _session_key(), "count": cur + 1}), encoding="utf-8")
    return cur + 1


def should_consolidate(root, severity: str | None) -> bool:
    """True when a finding of this severity folds into a consolidation CR instead of its own
    artefact (Low severity, low_consolidation on, schema v3)."""
    return sdlc_md.is_schema_v3(root) and low_consolidation(root) and is_low(severity)


def _theme(type_: str, fields: dict) -> str:
    return (fields.get("theme") or f"low-severity {type_}s").strip()


def _theme_key(theme: str) -> str:
    """A separator-safe, case-insensitive slug of a theme - used as BOTH the stored
    `Consolidation` marker and the match key. `sdlc_md.extract_field` truncates a raw value at
    the inline `·` field separator (and at a `**Field:**` run), so the marker must contain none;
    a slug also folds case/whitespace/punctuation so `Auth · Session` and `auth session` match."""
    return re.sub(r"[^a-z0-9]+", "-", (theme or "").lower()).strip("-") or "findings"


def _find_consolidation_cr(root, theme: str) -> Path | None:
    """A non-terminal consolidation CR whose `> **Consolidation:**` marker matches this theme's
    key, or None."""
    key = _theme_key(theme)
    for p in sdlc_md.artifact_files("cr", Path(root)):
        text = p.read_text(encoding="utf-8")
        if (sdlc_md.extract_field(text, "Consolidation") or "").strip() != key:
            continue
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"),
                                          sdlc_md.status_vocab("cr", root))
        if status not in sdlc_md.terminal_statuses("cr"):
            return p
    return None


def _bullet(title: str, detail: str) -> str:
    detail = (detail or "").strip()
    return f"- **{title}**" + (f": {detail}" if detail else "")


def _append_finding(path: Path, title: str, detail: str) -> None:
    """Append a finding bullet under the CR's `## Consolidated Findings` section."""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip().lower() == "## consolidated findings")
    except StopIteration:  # defensive: section missing - recreate it before the revision log
        lines += ["", "## Consolidated Findings", ""]
        start = len(lines) - 2
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    insert = end
    while insert > start and not lines[insert - 1].strip():
        insert -= 1  # keep the bullet adjacent to the list, before trailing blanks
    lines.insert(insert, _bullet(title, detail))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _alloc_cr_id(root: Path) -> tuple[str, str]:
    """(file_id, disp) for the consolidation CR, era-aware: a ULID under schema v3 (matching
    artifact.py's v3 identity), a sequential CRnnnn under v2."""
    prefix = sdlc_md.ARTIFACT_TYPES["cr"][1]
    if sdlc_md.is_schema_v3(root):
        d = root / sdlc_md.ARTIFACT_TYPES["cr"][0]
        for _ in range(16):
            ident = f"{prefix}-{sdlc_md.short_ulid()}"
            if not (d.exists() and any(d.glob(f"{ident}-*.md"))):
                return ident, ident
        ident = f"{prefix}-{sdlc_md.new_ulid()[:12]}"
        return ident, ident
    n = next_id.allocate_number("cr", root)
    return f"{prefix}{n:04d}", f"{prefix}-{n:04d}"


def _new_consolidation_cr(root, theme: str, title: str, detail: str, today: str) -> Path:
    """Mint a fresh consolidation CR for `theme`, seeded with the first finding, and index it."""
    root = Path(root)
    file_id, disp = _alloc_cr_id(root)
    key = _theme_key(theme)
    # The default theme is already "low-severity <type>s", and title/slug both prepend
    # "Low-severity" - strip a leading low-severity from the theme so we don't emit
    # "Low-severity low-severity crs" / "low-severity-low-severity-crs-consolidated".
    stem = re.sub(r"^low-severity-?", "", key) or key
    display_theme = re.sub(r"(?i)^low[- ]severity\s*", "", theme).strip() or theme
    slug = f"low-severity-{stem[:24]}-consolidated"
    create_status = sdlc_md.INBOX_STATUS if sdlc_md.is_schema_v3(root) else "Proposed"
    cr_title = f"Low-severity {display_theme} (consolidated)"
    body = (
        f"# {disp}: {cr_title}\n\n"
        f"> **Status:** {create_status}\n> **Priority:** Low\n> **Type:** Improvement\n"
        f"> **Date:** {today}\n> **Consolidation:** {key}\n"
        f"> **Created-by:** sdlc-studio file\n\n"
        "## Summary\n\nA themed consolidation of Low-severity findings that individually do not "
        "warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then "
        "action or reject as one.\n\n"
        f"## Consolidated Findings\n\n{_bullet(title, detail)}\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
        f"| {today} | audit | Consolidation opened |\n")
    path = root / sdlc_md.ARTIFACT_TYPES["cr"][0] / f"{file_id}-{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    # Index the CR through the same header-driven builder the create paths use (recomputes
    # counts); lazy import breaks the file_finding <-> triage_noise load-time cycle.
    import file_finding  # noqa: E402
    idx = path.parent / "_index.md"
    if idx.exists():
        hdr = sdlc_md.find_data_header(idx.read_text(encoding="utf-8").splitlines())
        if hdr:
            link = f"[{disp}]({file_id}-{slug}.md)"
            rowf = {"date": today, "priority": "Low", "ctype": "Improvement"}
            row = sdlc_md.row_from_header(hdr[1], link, cr_title, create_status, rowf)
            file_finding.append_index_row(root, "cr", row)
    record_creation(root)             # a minted artefact counts against the session budget
    return path


def consolidate_low_finding(root, type_: str, title: str, fields: dict, today: str) -> dict:
    """Fold a Low-severity finding into its themed consolidation CR (creating the CR on the
    first finding of a theme, appending on the rest). Returns
    {id, path, consolidated_into, created}."""
    root = Path(root)
    theme = _theme(type_, fields)
    detail = fields.get("summary", "")
    existing = _find_consolidation_cr(root, theme)
    if existing is not None:
        _append_finding(existing, title, detail)
        cr_id = sdlc_md.extract_record_id(existing.stem)
        result = {"id": cr_id, "path": str(existing), "consolidated_into": cr_id, "created": False}
    else:
        enforce_session_cap(root)  # opening a consolidation CR mints an artefact - honour the cap
        path = _new_consolidation_cr(root, theme, title, detail, today)
        cr_id = sdlc_md.extract_record_id(path.stem)
        result = {"id": cr_id, "path": str(path), "consolidated_into": cr_id, "created": True}
    # Fail loud, not silent drop (the EP0014 principle): a consolidation CR aggregates many
    # findings and cannot own one finding's record-only tranche, so a tranche supplied on a
    # consolidated Low finding is not recorded - say so rather than discard it silently.
    dropped = str(fields.get("tranche") or "").strip()
    if dropped:
        print(f"warning: tranche {dropped!r} not recorded - this Low-severity finding "
              f"consolidates into {cr_id} (a shared CR carries no per-finding tranche); file it "
              "as Medium or above to keep an individual, tranche-tagged artefact", file=sys.stderr)
        result["tranche_dropped"] = dropped
    return result


def main(argv=None) -> int:
    """Module-only library: a --help stub so disclosure and humans learn its role."""
    import argparse
    ap = argparse.ArgumentParser(
        prog="triage_noise.py",
        description="Internal module (no CLI): imported by file_finding/artifact for the "
                    "v3 triage noise controls. Drive it through those tools.")
    ap.parse_args(argv)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
