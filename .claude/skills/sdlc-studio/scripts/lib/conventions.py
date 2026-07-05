"""Tolerant convention layer: the ONE place a consuming project's house
conventions are interpreted.

Several checks used to hard-code an exact string (the index status-column
name, the companion-doc suffix, the bug-readiness headings) and every project
whose equally-valid convention differed collected false findings across
several tools at once. This module retires that class: checks ask these
functions instead of embedding a literal.

Policy: a `conventions:` block in `sdlc-studio/.config.yaml` is the primary
mechanism, every key defaulting to the historical literal so an unconfigured
project behaves exactly as before. Normalised matching applies only where a
synonym is unambiguous (word-set equality on headings - `Fix (proposed)` ==
`Proposed Fix`; containment never counts). A wrong-shaped conventions value
raises ConventionsError - the layer fails loud, it never guesses. Exact
guards whose relaxation would scavenge (a `Dependency Status` cell is about
the dependency, not the row) stay at their call sites.
"""
from __future__ import annotations

import re
from pathlib import Path

try:
    from lib import sdlc_md
except ImportError:  # loaded with lib/ itself on sys.path
    import sdlc_md  # type: ignore


class ConventionsError(ValueError):
    """A conventions value has the wrong shape - name it, never guess."""


DEFAULT_COMPANION_SUFFIXES = ["consultations"]

# Bug-readiness heading vocabularies. A plain string is one accepted heading;
# a list is a combo - every heading in it must be present. Symptom + Root
# cause is repro evidence (stronger than bare steps, not weaker).
DEFAULT_BUG_READY_SECTIONS = {
    "repro": ["Steps to Reproduce", "Reproduction Steps",
              ["Symptom", "Root cause"]],
    "fix": ["Proposed Fix", "Fix Description", "Fix (proposed)"],
}


def _get(repo_root, key: str, default):
    if repo_root is None:
        return default
    got = sdlc_md.project_override(repo_root, f"conventions.{key}", None)
    return default if got is None else got


def _require_str_list(value, key: str) -> list[str]:
    if not (isinstance(value, list) and all(isinstance(v, str) for v in value)):
        raise ConventionsError(
            f"conventions.{key} must be a list of strings, got {value!r}")
    return value


def companion_suffixes(repo_root) -> list[str]:
    """Stem suffixes (no leading dash) marking a file as a companion doc
    filed under an artifact's id, e.g. EP0244-...-decisions.md."""
    got = _get(repo_root, "companion_suffixes", DEFAULT_COMPANION_SUFFIXES)
    return _require_str_list(got, "companion_suffixes")


def status_aliases(repo_root) -> list[str]:
    """Extra header names (lowered) a project declares for its index status
    column. Exact cell match only - an alias is a declaration, not a fuzz."""
    got = _get(repo_root, "status_column", [])
    return [s.lower() for s in _require_str_list(got, "status_column")]


_TITLE_ID_RE = re.compile(r"^#\s+[A-Za-z]{2,4}-?\d{3,4}\s*:", re.MULTILINE)


def is_artifact(text: str) -> bool:
    """Is this file a tracked artifact (vs a companion/note under a shared id)?

    An artifact carries a `> **Status:**` metadata line or an `# <ID>: <title>`
    block. The title alone still counts so a real artifact that LOST its Status
    line keeps being flagged by validate rather than silently skipped."""
    if sdlc_md.extract_field(text, "Status"):
        return True
    return bool(_TITLE_ID_RE.search(text))


def bug_ready_sections(repo_root=None) -> dict:
    got = _get(repo_root, "bug_ready_sections", DEFAULT_BUG_READY_SECTIONS)
    if not isinstance(got, dict):
        raise ConventionsError(
            f"conventions.bug_ready_sections must be a mapping, got {got!r}")
    out: dict = {}
    for kind, entries in got.items():
        if not isinstance(entries, list):
            raise ConventionsError(
                f"conventions.bug_ready_sections.{kind} must be a list, got {entries!r}")
        for e in entries:
            ok = isinstance(e, str) or (
                isinstance(e, list) and all(isinstance(i, str) for i in e))
            if not ok:
                raise ConventionsError(
                    f"conventions.bug_ready_sections.{kind} entries must be "
                    f"strings or lists of strings, got {e!r}")
        out[str(kind)] = entries
    return out


_HEADING_RE = re.compile(r"^#{2,6}\s+(.+?)\s*$", re.MULTILINE)


def _word_set(s: str) -> frozenset:
    """Normalised heading identity: case-folded word set, punctuation and
    parentheticals stripped. Equality only - containment would let
    'Won't Fix rationale' read as a fix section."""
    return frozenset(re.sub(r"[^a-z0-9 ]", " ", s.lower()).split())


def section_present(text: str, kind: str, repo_root=None) -> bool:
    """Does `text` carry a section satisfying the `kind` vocabulary
    (default or project-declared)? A string entry matches any heading with
    the same word set; a list entry requires all its headings present."""
    entries = bug_ready_sections(repo_root).get(kind, [])
    headings = [_word_set(h) for h in _HEADING_RE.findall(text)]
    for entry in entries:
        needles = entry if isinstance(entry, list) else [entry]
        if needles and all(_word_set(n) in headings for n in needles):
            return True
    return False


def template_for(type_: str, repo_root) -> Path | None:
    """The project-declared scaffold template for an artifact type
    (`conventions.templates.<type>`, repo-root-relative), or None to use the
    skill default. Existence is the caller's check so it can fail loud with
    the action it was attempting."""
    got = _get(repo_root, "templates", {})
    if not isinstance(got, dict):
        raise ConventionsError(
            f"conventions.templates must be a mapping, got {got!r}")
    rel = got.get(type_)
    if rel is None:
        return None
    if not isinstance(rel, str):
        raise ConventionsError(
            f"conventions.templates.{type_} must be a path string, got {rel!r}")
    return Path(repo_root) / rel
