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
from typing import NamedTuple, TypeVar

T = TypeVar("T")

# -----------------------------------------------------------------------------
# Canonical markdown conventions (the single source of truth for parsing)
# -----------------------------------------------------------------------------

# First `# Heading` of a document.
H1_RE = re.compile(r"^#\s+(.+)$", re.M)
# Artifact ID prefix at the start of a filename stem. CR/RFC display with a
# dash; the others do not. The optional dash matches both.
# Case-insensitive: some repos name files lowercase (`cr0001.md`) while indexes
# use uppercase (`CR-0001`) — both must parse to the same ID.
# Two id eras coexist (schema v3): the v2 sequential form (`US0001`, `CR-0007`)
# and the v3 form (`BG-01JQK3F8`) - a type prefix, a dash, then a Crockford-base32 short ULID
# (>= 8 chars, extended on a rare directory clash). The base32 alternative is matched
# case-SENSITIVELY (`(?-i:...)`) so it stops at the lowercase `-slug`, never swallowing it.
_V3_SUFFIX = r"(?-i:-[0-9A-HJKMNP-TV-Z]{8,})"
# The digit run is `\d{4,}`, not `\d{4}`: a fixed four consumed only a prefix, so `US01010`
# read as `US0101` and any consumer matching ids this way attributed a 5-digit artefact to a
# different, real 4-digit one. The v3 alternative is tried FIRST so an all-digit ULID suffix
# (`BG-01234567`) is claimed whole by the v3 branch instead of being truncated by the v2 one.
ID_RE = re.compile(
    r"^((?:EP|US|PL|BG|TS|WF|SC|RFC|CR|IS)(?:" + _V3_SUFFIX + r"|-?\d{4,}))", re.IGNORECASE)
# Same, unanchored - finds an ID anywhere (e.g. inside an index table cell
# `[US0001](US0001-login.md)`). RFC before CR so `RFC-0001` is not read as `CR`.
ID_SEARCH_RE = re.compile(
    r"(?<![A-Za-z])(?:EP|US|PL|BG|TS|WF|SC|RFC|CR|IS)(?:" + _V3_SUFFIX + r"|-?\d{4,})", re.IGNORECASE)
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

# The marker `refine` writes into an ungroomed story's Acceptance Criteria section in place of a
# bare {{placeholder}} scaffold. It is an explicit, machine-detectable statement that these ACs
# are a grooming stub rather than authored content, so a reader tells a groomed story from an
# ungroomed one at a glance and `conformance` counts the ungroomed ones by the token - the debt
# is visible on the backlog instead of being met at plan time. Kept here (not in either script)
# so the writer (`refine`) and the counter (`conformance`) read the ONE token and cannot drift.
UNGROOMED_AC_TOKEN = "Ungroomed - acceptance criteria are a grooming placeholder"
#: The marker ROUTES as well as reports. An author meeting it needs two things the token alone
#: does not give them: the SHAPE a criterion takes, and how to write a `Verify:` that runs.
#: Naming both here means the answer arrives with the problem, instead of the author guessing
#: at a shape and a reviewer correcting it afterwards - which is the grooming cost this project
#: keeps paying unpriced.
UNGROOMED_AC_MARKER = (
    f"> **{UNGROOMED_AC_TOKEN}** - author each criterion and its Verify check against this "
    "story's slice while grooming, before it is planned to Done. "
    "Shape: `templates/core/story.md`. Verifier guidance: `reference-verify.md`."
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


# -----------------------------------------------------------------------------
# Time
# -----------------------------------------------------------------------------


#: Reads this module DEGRADED rather than performed, live only inside `degradation_log()`.
#: `None` means nobody is collecting, which is the default: the swallow is correct for a
#: scanner and only a caller making a SAFETY decision needs to hear about it.
_DEGRADED: "list | None" = None


@contextlib.contextmanager
def degradation_log():
    """Collect every read this module swallowed, for the length of one sweep.

    `read_text_safe` and `walk_glob` are deliberately forgiving: one unreadable artefact must
    not abort a walk over a thousand. That is right for a census and WRONG for a guard, because
    a helper that degrades silently converts every guard above it into a fail-open guard. The
    release tag check read an unreadable delivery tree as an empty one and reported "no close is
    owed" - a positive falsehood, from the only live guard on a release.

    So the swallow stays and gains a witness. Opt-in and scoped, like `corpus_cache`: a caller
    that is about to decide something wraps the read, asks what degraded, and refuses on a
    non-empty answer. Nesting is a no-op so an inner sweep cannot steal the outer one's list."""
    global _DEGRADED  # noqa: PLW0603 - the log IS module state; the scope is the guard
    if _DEGRADED is not None:
        yield _DEGRADED
        return
    _DEGRADED = []
    try:
        yield _DEGRADED
    finally:
        _DEGRADED = None


def record_degraded(path, reason: str) -> None:
    """Note that a read of `path` was swallowed. A no-op when nobody is collecting."""
    if _DEGRADED is not None:
        _DEGRADED.append({"path": str(path), "reason": reason})


def degradations() -> list:
    """What has degraded inside the open `degradation_log`, or [] when none is open."""
    return list(_DEGRADED or [])


def read_text_safe(path, default: str = "") -> str:
    """Read a file as UTF-8, returning `default` when it is unreadable OR not valid UTF-8 (a
    half-written or binary-corrupted artefact from a crashed session). One bad file must never
    crash a scanner that walks the tree - it is NAMED by whatever consumes the default (a
    status-less census entry, an empty body), not allowed to abort the whole pass. The read/parse
    counterpart to `iter_artifact_files`, for the direct `read_text` sites that do not go through
    the enumerator.

    The default is also RECORDED in any open `degradation_log`, so a caller deciding something
    can tell "the file said nothing" from "I could not read the file"."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        record_degraded(path, f"unreadable: {exc.__class__.__name__}")
        return default


# --- The project-root resolver -------------------------------------------------------------
# THE one way a script turns `--root` into a path, and anchors a relative output on it. Every
# script in this family takes `--root`, and a script that resolved it with a bare `Path(args.root)`
# wrote its output beside the CWD instead of into the project: a run from a subdirectory produced
# a stray `sdlc-studio/.local` tree, printed the path it had used, and exited 0, so the report the
# Done gate reads was never where the gate looks. Promoted here from `verify_ac`, which now
# delegates, because a second path-joining idiom per script is exactly how a writer and its reader
# stop agreeing about where a file lives.

#: A project root is a directory holding an `sdlc-studio/` workspace. The bare presence of a
#: directory by that name is not enough: the skill's own source sits at
#: `.claude/skills/sdlc-studio/`, so a marker-free check would stop at `.claude/skills` and call it
#: a project. Each marker below exists only in a real workspace.
ROOT_MARKERS = (
    ".sdlc-studio.yaml",
    "sdlc-studio/.config.yaml",
    "sdlc-studio/stories",
    "sdlc-studio/epics",
    "sdlc-studio/bugs",
    "sdlc-studio/change-requests",
)


def under_root(repo_root: Path, rel: str) -> Path:
    """Anchor a caller-supplied output path on the resolved root when it is RELATIVE, so a run
    from any cwd writes where the gate reads. An ABSOLUTE path is returned unchanged - the
    caller's explicit destination is never rewritten."""
    p = Path(rel)
    return p if p.is_absolute() else repo_root / p


def discover_root(start: Path | str) -> Path:
    """The nearest directory at or above `start` holding an sdlc-studio workspace.

    Falls back to `start` when there is no project above it: with none in sight the cwd is the
    honest answer, and walking to `/` would anchor the output somewhere unrelated."""
    start = Path(start).resolve()
    for cand in (start, *start.parents):
        if any((cand / m).exists() for m in ROOT_MARKERS):
            return cand
    return start


def resolve_root(args) -> Path:
    """The project root every path in this run anchors on.

    A root the caller NAMED is honoured verbatim - pointing a run at another project must never
    be second-guessed. The family default `.` is not a named root; it means "work it out from
    here", so it is DISCOVERED upward rather than assumed to be the cwd. Discovery only ever
    widens `.`: a cwd that IS a project root resolves to itself, so the common case is unchanged.
    """
    named = getattr(args, "root", None) or "."
    if named != ".":
        return Path(named).resolve()
    return discover_root(Path.cwd())


# --- The applied-mutant guard --------------------------------------------------------------
# A mutation evidence run rewrites live source one file at a time, for minutes at a stretch.
# Any script invoked inside that window can execute a mutated sibling, misbehave, and hand the
# mutant's wrong behaviour to whoever is reading the output as the tool's own. The in-flight
# sidecar already marks the window exactly; this is the pair of readers that surface it. The
# functions RETURN their message rather than printing it - a library that prints leaks the
# text into every caller, including the ones capturing output for something else.

#: The environment marker a mutation run sets on itself and on the environment it runs its
#: suites under. The sidecar records only `{path: original-bytes}` and carries no owner, so
#: the run's own processes are told apart by what they inherit, not by what the file says.
MUTATION_RUN_ENV = "SDLC_STUDIO_MUTATION_RUN"

#: What the guard says a mutated tree violates, in both messages and in the doctrine: one
#: process rewrites a tree at a time.
_SINGLE_WRITER = ("the single-writer rule says one process rewrites a tree at a time")


def inflight_path(root: Path | str) -> Path:
    """The sidecar holding the original bytes of the mutant currently applied in `root`.

    The ONE spelling of that path: the writer (the mutation engine) and these readers must
    never disagree about where the window is recorded.
    """
    return Path(root) / "sdlc-studio" / ".local" / "mutation-inflight.json"


def inflight_mutation(root: Path | str) -> dict | None:
    """`{"sidecar": Path, "files": [...]}` while a mutant is applied in `root`, else None.

    None for a process carrying `MUTATION_RUN_ENV` - the mutation run applies the mutants and
    must not be blocked from cleaning up after itself. A sidecar that exists but cannot be read
    still reports the window: the file's PRESENCE is the fact, its contents only name the
    casualties.
    """
    if os.environ.get(MUTATION_RUN_ENV):
        return None
    sidecar = inflight_path(root)
    if not sidecar.exists():
        return None
    files: list[str] = []
    readable = False
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            files = sorted(str(k) for k in data)
            readable = True
    except (OSError, ValueError):
        files = []
    # `readable` separates "the sidecar says nothing is mutated" from "the sidecar cannot be
    # read". Both give an empty file list and they mean opposite things: the first is a window
    # that closed, the second is a window whose contents are unknown. Collapsing them is how a
    # guard stops refusing exactly when it cannot tell.
    return {"sidecar": sidecar, "files": files, "readable": readable}


def _inflight_named(state: dict) -> str:
    return ", ".join(state["files"]) or f"(unreadable sidecar {state['sidecar']} - files unknown)"


def inflight_age_note(state: dict) -> str:
    """How old the in-flight claim is, as a phrase for the warning and the refusal.

    A guard with no notion of age cannot distinguish a run that started ten seconds ago from an
    abandoned sidecar left by a process killed days back - and the second case blocks every write
    in the repo indefinitely while telling the operator to "wait for the run to finish". There is
    no run. Stating the age does not decide anything, which is deliberate: the guard still
    refuses, because a mutated tree is a mutated tree, but the reader can now tell which of the
    two situations they are in without stat-ing the file themselves.
    """
    try:
        mtime = Path(state["sidecar"]).stat().st_mtime
    except OSError:
        return ""
    seconds = max(0, int(datetime.now(timezone.utc).timestamp() - mtime))
    if seconds < 120:
        return f" The claim is {seconds}s old, so a run is probably alive."
    if seconds < 3600:
        return (f" The claim is {seconds // 60}m old. If no run is alive it is ABANDONED - "
                f"nothing will clear it on its own.")
    hours = seconds // 3600
    return (f" The claim is {hours}h old, which is far longer than any mutation run takes: "
            f"treat it as ABANDONED unless you can point at a live process.")


def inflight_touched_files(state: dict) -> list[str]:
    """The files the sidecar says are actually mutated.

    A sidecar recording NOTHING mutated is a window that closed without being cleaned up: there
    is no mutated code to protect anyone from, so refusing every write on its account is a
    refusal with no subject.
    """
    return [f for f in state.get("files") or [] if f]


def inflight_warning(root: Path | str) -> str | None:
    """The read-path message: a read taken over a mutated tree is degraded evidence, not
    forbidden. Returns None when no mutant is applied (or this is the run's own process)."""
    state = inflight_mutation(root)
    if state is None:
        return None
    return (f"WARNING: a mutation run has a mutant applied to {_inflight_named(state)} - "
            f"{_SINGLE_WRITER}, so this output may come from mutated code. Treat it as degraded "
            f"evidence, and re-read once {state['sidecar']} is gone."
            f"{inflight_age_note(state)}")


def inflight_refusal(root: Path | str) -> str | None:
    """The write-path message: a write made against a mutated tool is one nobody can trust
    afterwards, so it is refused. Returns None when there is nothing to refuse."""
    state = inflight_mutation(root)
    if state is None:
        return None
    if state.get("readable") and not inflight_touched_files(state):
        # A readable sidecar naming NO mutated file. There is no mutated code, so there is
        # nothing to protect a write from - refusing here blocks the repo over a window that
        # closed. An UNREADABLE sidecar is different and still refuses: its presence is the
        # fact, and not being able to read it is not evidence of innocence.
        return None
    return (f"refused: a mutation run has a mutant applied to {_inflight_named(state)} - "
            f"{_SINGLE_WRITER}, and a write made through mutated code is one nobody can trust "
            f"afterwards. Nothing was written. Wait for the run to finish, or - if no run is "
            f"alive - restore the file(s) from git and delete {state['sidecar']}."
            f"{inflight_age_note(state)}")


#: The stamp `now_iso8601` writes. The fast path, kept because it is the overwhelming case.
_ISO_Z = "%Y-%m-%dT%H:%M:%SZ"


def parse_iso8601(value) -> "datetime.datetime | None":
    """Any ISO-8601 stamp carrying an explicit UTC offset, normalised to UTC. None otherwise.

    THE ONE STAMP READER. This rule had three implementations - here (as telemetry's private
    `_parse_iso`), in `transition.py` and in `loop_guard.py` - and two of them matched a single
    hand-written `%Y-%m-%dT%H:%M:%SZ`. That is the form this project writes; it is NOT the form
    the standard library writes, and `.isoformat()` on an aware datetime yields `+00:00`, which
    is live in this tree and in any consuming project whose state these read. So a fix to the
    reader landed in one place and the other two went on refusing valid stamps.

    A NAIVE stamp is still refused: it names no instant, and calling it UTC would invent the one
    fact it is missing. Sub-second precision is kept rather than rounded away."""
    import datetime as _dt  # noqa: PLC0415 - local, as elsewhere in this module
    text = str(value).strip()
    try:
        return _dt.datetime.strptime(text, _ISO_Z).replace(tzinfo=_dt.timezone.utc)
    except (TypeError, ValueError):
        pass
    try:
        parsed = _dt.datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    except (TypeError, ValueError):
        return None
    return None if parsed.tzinfo is None else parsed.astimezone(_dt.timezone.utc)


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
    fence: tuple[str, int] | None = None
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        # A fenced code block is illustrative, not structure: a `|`-row inside ``` (a shipped
        # example table) must never be tallied. Fences are tracked by the ONE shared CommonMark
        # rule (`fence_step`), never a three-character toggle: a toggle released a ````markdown
        # block on its inner ``` and tallied the illustration below it as real rows, which is
        # the index-corruption class, because reconcile counts what this yields.
        was_open = fence is not None
        fence, is_fence_line = fence_step(stripped, fence)
        if not was_open and is_fence_line:  # an opening fence, like a heading, ends the table
            if current:
                yield current
            current = None
            continue
        if was_open:  # inside the block, closer included - never structure
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
#: THE CANONICAL EPIC-INDEX COLUMNS. One importable answer, because two consulted their own list:
#: the shipped `templates/indexes/epic.md` declared `Owner`/`Target` while every one of this
#: repository's 191 live rows carries `Deps`/`Created`/`Updated`. The live set wins - 191 rows of
#: evidence against a template nobody had reconciled - and both the derivation and the row writer
#: read this rather than restating it, so they cannot disagree about what a row is.
EPIC_INDEX_COLUMNS: tuple[str, ...] = (
    "ID", "Title", "Status", "Stories", "Deps", "Created", "Updated",
)

#: The cells this module DERIVES from the tree rather than accepting as typed.
EPIC_DERIVED_COLUMNS: tuple[str, ...] = ("Stories", "Deps")

#: A cell whose value the artefact has not stated. Distinct from `DEPS_DECLARED_NONE`: "nobody
#: said" and "the epic says there are none" are different facts, and rewriting the first as the
#: second invents a declaration.
CELL_NOT_STATED = "--"
#: The value already in use on EP0001's row for an epic that DECLARES it has no dependencies.
DEPS_DECLARED_NONE = "None"


#: {(root, signature) -> {epic id -> story count}}. The census is read once per epic row and this
#: repository has 191 of them over ~600 story files, so the naive per-epic walk read every story
#: file 191 times - 3.3s on a lane that runs on every commit. Memoised on a signature built from
#: `stat` rather than from content: a story whose Epic field changes changes its size or mtime, and
#: a stat per file is two orders of magnitude cheaper than a read per file.
_EPIC_STORY_CENSUS: dict[tuple, dict[str, int]] = {}


def _stories_signature(d: Path) -> tuple:
    """A signature over the stories directory, tolerant of a file that cannot be stat'd.

    `p.stat()` on a dangling symlink raises, and the pre-memo census read every file through
    `read_text_safe` and tolerated one. An unreadable entry must not abort the whole sweep, so it
    contributes a sentinel: the census still recomputes, it just cannot be told apart from another
    unreadable state, which is the safe direction.
    """
    out = []
    for p in sorted(d.glob("*.md")):
        try:
            s = p.stat()
            out.append((p.name, s.st_mtime_ns, s.st_size))
        except OSError:
            out.append((p.name, None, None))
    return tuple(out)


def epic_story_census(repo_root) -> dict[str, int]:
    """{epic id -> how many story files name it in their `Epic` field}, over one pass.

    An epic with no stories is ABSENT from the mapping rather than present as 0: the caller that
    needs "0" asks for a count, and a mapping that invented a key for every id it had never seen
    could not be iterated.
    """
    d = Path(repo_root) / "sdlc-studio" / "stories"
    if not d.is_dir():
        return {}
    key = (str(Path(repo_root).resolve()), _stories_signature(d))
    cached = _EPIC_STORY_CENSUS.get(key)
    if cached is not None:
        return cached
    counts: dict[str, int] = {}
    for path in sorted(d.glob("*.md")):
        if path.name == "_index.md":
            continue
        rec = extract_record_id(path.stem)
        if not rec or not rec.startswith("US"):
            continue
        # The id is EXTRACTED from the field, not compared to it whole. The shipped story template
        # writes the LINKED form `> **Epic:** [EP0001: Title](../epics/EP0001-x.md)`, and a strict
        # equality read counts none of those - which wrote a story count of 7 into a row whose true
        # count was 18. Every other reader of this field in the family already used this idiom
        # (transition, verify_ac, sprint, ac_scope, mutation); the census was the one that did not.
        field = extract_field(read_text_safe(path), "Epic") or ""
        m = ID_SEARCH_RE.search(field)
        if m:
            counts[norm_id(m.group(0))] = counts.get(norm_id(m.group(0)), 0) + 1
    # Bounded: a long-lived process reconciling many trees must not accumulate a census per edit.
    if len(_EPIC_STORY_CENSUS) > 8:
        _EPIC_STORY_CENSUS.clear()
    _EPIC_STORY_CENSUS[key] = counts
    return counts


def epic_story_count(repo_root, epic_id: str) -> int:
    """How many story files name `epic_id` in their `Epic` field. A census, never a stored total.

    Both sides normalised, so `EP-0008` and `EP0008` are one epic on the reading side as well as
    the counting side.
    """
    return epic_story_census(repo_root).get(norm_id(epic_id), 0)


def epic_declared_deps(repo_root, epic_id: str) -> list | None:
    """The epic ids its `Blocked By` table names, in FILE ORDER.

    THREE states, and the third is why this returns None rather than an empty list:
      - `["EP0001", "EP0002"]` - the section names dependencies;
      - `[]`                   - the section exists and names none, so the epic has DECLARED none;
      - `None`                 - nobody has said: there is no `## Dependencies` section, OR the
                                 section holds rows this reader cannot parse.
    Collapsing the last two would rewrite an absence as a declaration the epic never made - which
    is what the earlier version did, because it returned `[]` for a section full of rows it could
    not read. `artifact.py new --type epic --template full` emits the template's unrendered
    `| {{dependency}} | ... |` row, so a freshly minted epic declared "no dependencies" on the
    strength of a placeholder. An unparseable row is now unknown, not empty.
    """
    found = find_by_id(Path(repo_root), epic_id)
    if not found:
        return None
    # `find_by_id` returns (path, type), not a path. Unpacked rather than passed straight to
    # `Path()`, which raised on the tuple.
    text = read_text_safe(Path(found[0]))
    i = text.find("## Dependencies")
    if i == -1:
        return None
    section = text[i:]
    nxt = re.search(r"^## (?!Dependencies)", section[3:], re.M)
    if nxt:
        section = section[:nxt.start() + 3]
    # Narrow to `### Blocked By` when the epic has one, then to the FIRST contiguous table in
    # whatever remains. A Dependencies section can hold more than one table - EP0010 carries a
    # second `| Item | Type | Impact |` table of downstream effects - and reading them all judged
    # rows that are not dependency declarations at all.
    blocked = section.find("### Blocked By")
    if blocked != -1:
        section = section[blocked:]
    rows: list[list[str]] = []
    for line in section.splitlines():
        if line.lstrip().startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif rows:
            break                                     # the first table has ended
    out: list[str] = []
    for cells in rows:
        if not cells or not cells[0]:
            continue
        first = cells[0]
        if set(first) <= set("-: ") or first.lower() in ("dependency", "id", "item"):
            continue                                  # the table's own header and separator
        # An explicit `| None |` / `| -- |` row is the author SAYING there are none. It contributes
        # no dependency and it does not make the section unreadable - four founding epics and
        # EP0010 declare it exactly that way, and treating it as unparseable would have turned five
        # real declarations into "nobody has said".
        if first.lower() in ("none", "n/a", "-", "--", "–", "—"):
            continue
        # ONE id per cell. `| EP0002, EP0003 |` yielded EP0002 and dropped EP0003 silently, so a
        # declared dependency vanished - a cell naming two is not a row this reader can resolve.
        found_ids = [norm_id(x) for x in ID_SEARCH_RE.findall(first)]
        epics = [x for x in found_ids if x.startswith("EP")]
        if len(epics) == 1 and len(found_ids) == 1:
            out.append(epics[0])                      # bare or linked: `EP0001`, `[EP-0001](...)`
        else:
            # A row naming something this reader cannot resolve to an epic and that is not an
            # explicit none - an unrendered `{{dependency}}`, an external dependency, two ids in
            # one cell. The section HAS content, so "declares none" is the one answer that is
            # certainly wrong. `artifact.py new --type epic --template full` emits the template's
            # unrendered placeholder row, so a freshly minted epic used to declare "no
            # dependencies" on the strength of `{{dependency}}`.
            return None
    return out


def derive_epic_row_cells(repo_root, epic_id: str) -> dict:
    """`{column: derived value}` for the epic-index cells this module owns.

    `Deps` is ABSENT from the mapping when the epic states no `## Dependencies` section, so a
    caller writes nothing rather than writing "not stated" over whatever is there.
    """
    cells: dict = {"Stories": str(epic_story_count(repo_root, epic_id))}
    deps = epic_declared_deps(repo_root, epic_id)
    if deps is None:
        return cells
    cells["Deps"] = ", ".join(deps) if deps else DEPS_DECLARED_NONE
    return cells


#: The `Audit-lens` value meaning "nobody attributed this". A BACKFILLED finding carries it, and
#: `detector-owed` counts it as unattributable rather than as a lens of that name - 108 findings
#: sharing one placeholder across five runs would otherwise read as a detector owed on every one.
#: Declared here because two modules must agree on it: the writer that stamps it and the reader
#: that decides whether a finding is attributed.
LENS_UNKNOWN = "unknown"

SINGLE_LINE_FIELDS: tuple[str, ...] = (
    "title", "author", "epic", "persona", "tranche", "priority", "ctype", "severity",
    "points", "size", "affects", "provenance", "date", "theme", "note",
    # The audit attribution. `audit_run` is the sharp one: it is free-form, so a newline or a
    # markdown link in it lands verbatim in a tracked artefact and can red the repo's own links
    # guard. One guard at one choke point, so every creation path inherits the refusal.
    "lens", "profile", "audit_run", "detector_for_lens",
)
# List fields whose every item renders as ONE bullet. An `acs` item is the sharpest of them: a
# break in it injects a sibling `- **Verify:** <command>` line into the AC block, which the
# verifier reads back and RUNS.
SINGLE_LINE_LIST_FIELDS: tuple[str, ...] = ("acs", "options", "verify")


# -----------------------------------------------------------------------------
# The size vocabulary: modified Fibonacci story points, and nothing else
# -----------------------------------------------------------------------------
#
# ONE size vocabulary, on ONE scale, read by ONE parser. A blind re-estimation of 21 delivered
# units - each recovered as filed, its declared size stripped, sized by three independent
# estimators with no access to the outcome - scored r = +0.68 against measured cost (and +0.78
# on units of 8 or below), and stayed POSITIVE within every sprint. Every computed metric tried
# before it failed: the best of them scored +0.03, and the one that looked promising flipped
# sign between cohorts. A three-level ordinal (S/M/L) managed +0.35 - better than the machine,
# worse than points, and a second answer to the same question. It is retired.
#
# WHY FIBONACCI, AND WHY A VALUE OFF IT IS REFUSED RATHER THAN ROUNDED. The gaps widen as the
# numbers grow, so the SCALE ITSELF encodes that uncertainty grows with size. That is the whole
# property, and it is the property a linear scale destroys. It is much harder to argue a unit is
# a 7 rather than an 8 than it is to choose between a 5 and an 8 - so a 7 is not a finer
# estimate, it is false precision about something inherently uncertain. Rounding it silently to
# 8 would hand the author a number they did not choose and record it as though they had; the
# scale IS the estimate, so the refusal is the point. The estimate is RELATIVE ("is this bigger
# than that one"), never an absolute prediction of time or tokens.
POINTS_FIELD = "Points"
#: The alternate spelling the corpus writes on 20 stories. Declared beside the canonical
#: one so `read_points` is the only place that has to know there are two.
STORY_POINTS_FIELD = "Story Points"
POINTS_SCALE: tuple[int, ...] = (1, 2, 3, 5, 8, 13, 20)
# Above this, a unit MUST be split. Estimator consistency collapses beyond it - in the blind
# re-estimation the 13s were systematically OVER-estimated (1.9x cheaper per point than every
# band below), and all three estimators returned them with low confidence and the words "should
# be split". A 13 or a 20 is a legal estimate and a TRIAGE failure: it is accepted, and it warns.
POINTS_SPLIT_ABOVE = 8
_POINTS_SCALE_TEXT = ", ".join(str(p) for p in POINTS_SCALE)


def check_points(value) -> int:
    """`value` as an int on the modified Fibonacci scale, or ValueError naming the scale.

    The ONE definition of a legal size, called from `check_creator_fields` - so every creation
    path inherits it and none is the way round another. Refuse, never round: a value quietly
    rewritten is recorded as an estimate the author never made.
    """
    raw = str(value).strip().strip("*`_ ")
    try:
        num = int(raw)
        if str(num) != raw:                       # "5.0", "+5", " 5 " already stripped
            raise ValueError(raw)
    except ValueError:
        num = None
    if num in POINTS_SCALE:
        return num
    raise ValueError(
        f"Points value {str(value)!r} is not on the modified Fibonacci scale - refused. "
        f"Nothing was allocated, nothing was written.\n"
        f"  The scale is: {_POINTS_SCALE_TEXT}. Nothing else - not S/M/L, not `unknown`, not 7.\n"
        f"  Why: the gaps widen deliberately, because uncertainty grows with size. A 7 is the "
        f"false precision the Fibonacci scale exists to prevent - it is much harder to argue a "
        f"unit is a 7 rather than an 8 than to choose between a 5 and an 8. The scale IS the "
        f"estimate, so a value off it is never rounded for you: you make the call.\n"
        f"  Points are RELATIVE, not absolute - not 'how long will this take' but 'is this "
        f"bigger than that one', sized against units you have already delivered.\n"
        f"  A unit above {POINTS_SPLIT_ABOVE} points must be SPLIT, not estimated harder.")


def points_split_warning(points: int) -> str | None:
    """The warning a legal-but-too-big estimate earns, or None. Not a refusal: the estimate is
    honest, and the answer to it is decomposition - which is the author's call, not the tool's."""
    if points <= POINTS_SPLIT_ABOVE:
        return None
    return (f"warning: {points} points is above {POINTS_SPLIT_ABOVE} - this unit should be "
            f"SPLIT. Estimator consistency collapses beyond {POINTS_SPLIT_ABOVE} points (the "
            f"13s in the blind re-estimation were systematically over-estimated), so a unit "
            f"this size is a triage failure, not an estimation problem. Written anyway - "
            f"decomposition is your call, not the tool's.")


def read_points(text: str) -> int | None:
    """The size declared on an artefact, or None when it carries none.

    THE reader - the one every consumer of a size shares. Anchored on `extract_field`, so a
    bug's `> **Points:** 5` (metadata block), a CR's `**Points:** 5` (body) and an inline
    `· **Points:** 5` run are the same field, and a `**Points:**` mentioned in prose is not.
    Tolerates a decorated value (`5 (relative)`); a value the scale does not carry reads as no
    size at all, exactly as the creators refuse to write one.
    """
    raw = extract_field(text, POINTS_FIELD)
    if not raw or not raw.strip():
        # The second spelling this corpus actually writes. 20 stories carry `**Story Points:**`,
        # and `extract_field(text, "Points")` does not match it - so THE shared reader returned
        # None for them and every size consumer read them as unsized. Routing another caller
        # through a reader that cannot read the field is why the first fix for this changed
        # nothing. Tried second, so `Points` still wins where both are present.
        raw = extract_field(text, STORY_POINTS_FIELD)
    if not raw or not raw.strip():
        return None
    tok = raw.strip().split()[0].strip("*_`:,;.()")
    try:
        return check_points(tok)
    except ValueError:
        return None


# -----------------------------------------------------------------------------
# The T-shirt size: what a CONTAINER or a REQUEST carries, sized before decomposition
# -----------------------------------------------------------------------------
#
# SIZE BY WHAT A THING IS. Story points belong on the thing that is DELIVERED and MEASURED - a
# story or a bug, sized relative to units already delivered and checkable against actuals. A
# T-shirt size belongs on the CONTAINER that must be decomposed first: an epic (a container of
# stories), a CR (a REQUEST that becomes work only once it is broken down), an RFC (a design
# exploration). A request is not a unit of work until someone decomposes it, and pointing it is
# guessing at a shape that does not yet exist - so it is sized coarsely, on purpose. A coarse
# scale (S/M/L/XL) says "roughly this big" without pretending to a precision nobody has before
# the stories are known. A T-shirt size is NEVER a measurement: it is never summed into a
# velocity figure or a token forecast, both of which count delivered STORY points only.
SIZE_FIELD = "Size"
SIZE_SCALE: tuple[str, ...] = ("S", "M", "L", "XL")
_SIZE_SCALE_TEXT = ", ".join(SIZE_SCALE)


def check_size(value) -> str:
    """`value` as a canonical T-shirt size (S / M / L / XL), or ValueError naming the scale.

    The ONE definition of a legal container/request size, called from `check_creator_fields` -
    so every creation path inherits it. A lower-case `m` is accepted and canonicalised to `M`
    (a T-shirt size is a closed four-value set, not free text); anything else is refused, never
    coerced, because a container is sized coarsely and a value off the scale is a category error
    (story points on a request), not a typo to round away.
    """
    raw = str(value).strip().strip("*`_ ").upper()
    if raw in SIZE_SCALE:
        return raw
    raise ValueError(
        f"Size value {str(value)!r} is not a T-shirt size - refused. "
        f"Nothing was allocated, nothing was written.\n"
        f"  The scale is: {_SIZE_SCALE_TEXT}. A T-shirt size, NOT story points - because a CR "
        f"and an RFC are REQUESTS and an epic is a CONTAINER, each sized coarsely BEFORE it is "
        f"broken down.\n"
        f"  Story points ({_POINTS_SCALE_TEXT}) belong on the DELIVERY unit - a story or a bug - "
        f"which is measured against actuals. A container is not measured; it is decomposed.")


def heading_title(title: str) -> str:
    """A single-line H1 title composed from prose - the ONE definition, shared by every
    generator that builds a heading from a Sprint Goal or a request summary.

    A Sprint Goal is a sentence and ends in a full stop, so a heading built from one does
    too, and markdownlint MD026 (no trailing punctuation in a heading) then blocks the very
    commit that carries the generated artefact. This lives here because the same defect has
    now been fixed three times in three generators - the handoff H1, the seeded AC heading,
    and the retro scaffold - each fixing its own copy while the others stayed broken. All
    three route through here; a generator that builds a heading calls this rather than
    keeping its own idea of one. `refine._ac_heading` wraps it to add length truncation,
    and strips again afterwards because cutting at a word boundary can expose punctuation
    the first pass never saw.
    """
    return " ".join(str(title).split()).rstrip(" .,;:!?…")


def size_for_points(points: int) -> str:
    """The T-shirt Size a container/request takes from a story-point total - the ONE point->size
    band, shared by `refine` (sizing an epic from its stories) and the sizing migration (sizing a
    legacy pointed CR). Kept here so the two paths cannot drift: the band edges mirror the
    Fibonacci scale - S up to 3, M up to 8, L up to 20, XL beyond. A coarse read-off, never a
    measurement (the real size of an epic is its derived point total)."""
    return ("S" if points <= 3 else "M" if points <= 8 else "L" if points <= 20 else "XL")


def read_size(text: str) -> str | None:
    """The T-shirt size declared on a container/request artefact (`Size:` of S/M/L/XL), or None.

    THE reader every consumer of a container's size shares. Anchored on `extract_field`, so a
    CR/RFC `> **Size:** M` (metadata block) and an epic's `**Size:** M` (its Sizing section) are
    the same field, and a `**Size:**` mentioned in prose is not. A value the scale does not carry
    reads as no size at all, exactly as the creators refuse to write one. Returns the canonical
    upper-case form."""
    raw = extract_field(text, SIZE_FIELD)
    if not raw or not raw.strip():
        return None
    tok = raw.strip().split()[0].strip("*_`:,;.()")
    try:
        return check_size(tok)
    except ValueError:
        return None


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

    The SIZE is checked here for the same reason: it is the one field with a closed vocabulary,
    and this is the one place both creators already pass through. A scale restated at each
    creator is a scale the two can disagree about.
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
    if fields.get("points") is not None:
        warn = points_split_warning(check_points(fields["points"]))
        if warn:
            print(warn, file=sys.stderr)
    # A T-shirt Size is the other closed-vocabulary field: a container/request carries it in
    # place of points, and the same one-choke-point refusal keeps the scale from drifting.
    if fields.get("size") is not None:
        check_size(fields["size"])


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


def row_from_header(header: list[str], link: str, title: str, status: str, f: dict,
                    derived: dict | None = None) -> str:
    """Build an index data row matching the index's own columns - generic across every type,
    so both create paths emit identical rows. `f` supplies priority/type/severity/points/
    author/epic/date; unknown columns get `--`. Every cell is rendered as text: a numeric field
    (a size) reaches the row as the int the caller supplied, and a cell is markdown.

    `derived` supplies cells the TREE decides rather than the caller - `{"Stories": "0"}` from
    `derive_epic_row_cells`. Without it an epic's Stories cell fell to the unrecognised-column `--`
    branch, so a freshly minted epic was born drifted against the very derivation that maintains
    it. Passed in rather than computed here, because this function is type-agnostic and has no root
    to census; a column absent from `derived` still falls through to `--`, which is what keeps the
    `Deps` cell honest for an epic that declares no Dependencies section.
    """
    field_for = {"priority": ("priority", "Medium"), "type": ("ctype", "Feature"),
                 "epic": ("epic", "--"), "severity": ("severity", "--"),
                 "author": ("author", "--"), "points": ("points", "--")}
    by_derived = {k.strip().lower(): v for k, v in (derived or {}).items()}
    out: list[str] = []
    for h in header:
        hl = h.strip().lower()
        if hl in by_derived:
            out.append(str(by_derived[hl]))
        elif hl == "id":
            out.append(link)
        elif hl in ("title", "description", "feature", "name", "sprint"):
            out.append(title)
        elif hl == "status":
            out.append(status)
        elif hl in ("created", "date", "raised", "updated"):
            out.append(f.get("date", "--"))
        elif hl in field_for:
            key, default = field_for[hl]
            out.append(str(f.get(key, default)))
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


#: A leading id token for ANY artefact family, including the ones outside `ARTIFACT_TYPES`.
#: Same two key schemas as `ID_RE`, but a generic type prefix.
_STEM_ID_RE = re.compile(r"^([A-Za-z]{1,6}(?:" + _V3_SUFFIX + r"|-?\d{4,}))")


def stem_record_id(stem: str) -> str | None:
    """The id at the start of a filename stem, for any artefact family. None when there is none.

    `extract_record_id` answers this for the types in `ARTIFACT_TYPES` and ONLY those, so it
    returns None for a handoff, a retro or a review - families that live in the workspace and
    carry the same two key schemas. A caller reaching for it on those got None and read that as
    "no such document".

    That gap is why three readers hand-rolled `stem.split("-")[0]` instead, which yields the
    bare type prefix `HO` for a v3 key `HO-<ulid>-slug`, so the id never matched and the reader
    was blind to every key the product now mints by default. One idiom that covers every family
    is the fix; a fourth hand-rolled copy was not.
    """
    m = _STEM_ID_RE.match(stem or "")
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
    """Sorted files in dir_path matching glob `pattern` ([] if the dir is absent).

    A directory that EXISTS but cannot be listed also yields [] - `Path.glob` swallows the
    permission error itself - so the two are indistinguishable to a caller, and "I could not
    look" was being read as "there is nothing there". The empty result stands, because one
    unreadable directory must not abort a walk over the rest, but it is recorded in any open
    `degradation_log` so a caller making a safety decision can refuse instead."""
    if not dir_path.exists():
        return []
    if _DEGRADED is not None and not _listable(dir_path):
        record_degraded(dir_path, "directory could not be listed")
        return []
    return sorted(p for p in dir_path.glob(pattern) if p.is_file())


def _listable(dir_path: Path) -> bool:
    """Whether the directory's entries can actually be enumerated.

    Probed only when someone is collecting degradations - `os.scandir` on every glob would be a
    second syscall per directory on the hot census path for an answer nobody reads."""
    try:
        with os.scandir(dir_path) as entries:
            next(iter(entries), None)
        return True
    except OSError:
        return False


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
    "issue": ("sdlc-studio/issues", "IS"),
    "test-spec": ("sdlc-studio/test-specs", "TS"),
    "workflow": ("sdlc-studio/workflows", "WF"),
    # A planned-but-not-yet-run sprint. It is a process artefact on NEITHER backlog: it
    # carries no acceptance criteria of its own and delivers nothing - it is the shape of a
    # run that has not happened, materialised against whatever the backlog holds at the
    # moment it is run rather than against whatever it held when it was written.
    "charter": ("sdlc-studio/charters", "SC"),
}

# The two backlogs (dual-track: discovery feeds delivery). A DISCOVERY item - an RFC design
# exploration, a CR change request, or an Issue (a raw defect report / symptom) - sits in the
# DISCOVERY backlog: the options funnel. It records something someone wants or has observed, and
# it is not committed work until it is decomposed into the units that deliver it (a request is
# `refine`d into epics/stories; an Issue is `triage`d into bugs). A PRODUCT unit (an epic
# container, a story, a bug) is the DELIVERY backlog - the work itself, sized, planned, and closed
# on executable acceptance. The distinction is load-bearing: a discovery item must never be
# planned as a sprint unit (it has no executable ACs to close on), and its terminal status is
# DERIVED from the units it produced, never asserted. One definition of "which side of the line is
# this type on", so the planner, the transition gate, status and reconcile all agree. (`plan`,
# `test-spec` and `workflow` are process artefacts on neither backlog.)
#
# Two predicates, deliberately distinct: `is_request` is the narrow RFC/CR set (`refine`'s
# domain - a request becomes an epic + stories); `is_discovery` is the whole Discovery backlog
# (RFC/CR AND Issue), the predicate every backlog-side gate consults (plan-refuse, status
# bucketing, terminal-derivation, the undecomposed check). An Issue is discovery but NOT a
# request: it is triaged, not refined, so the two must not be conflated.
REQUEST_TYPES: tuple[str, ...] = ("rfc", "cr")
DISCOVERY_TYPES: tuple[str, ...] = ("rfc", "cr", "issue")
PRODUCT_TYPES: tuple[str, ...] = ("epic", "story", "bug")


def is_request(type_: str) -> bool:
    """True when `type_` is a REQUEST (RFC/CR) - `refine`'s domain, a Discovery item decomposed
    into an epic + stories. Narrower than `is_discovery`: an Issue is a Discovery item but is
    triaged into bugs, not refined, so it is NOT a request. Used where the RFC/CR shape
    specifically matters (refine, the CR-legacy sizing tolerance)."""
    return type_ in REQUEST_TYPES


def is_discovery(type_: str) -> bool:
    """True when `type_` is a DISCOVERY-backlog item (RFC/CR/Issue) - one that must be decomposed
    before it is committed work. The one predicate the planner (G1 refuse), transition (G2
    terminal derivation), status (backlog bucketing) and reconcile (undecomposed) share, so none
    hard-codes its own list of what may not be sprinted. Broader than `is_request`: it includes
    the Issue, which is triaged rather than refined but is equally not a sprint unit."""
    return type_ in DISCOVERY_TYPES


def two_backlog_enforced(repo_root) -> bool:
    """True when this project ENFORCES the two-backlog workflow - the HARD gates that change an
    existing project's habits: `plan` refuses a request (G1), a request's terminal status is
    derived from its children (G2), `reconcile` flags an accepted childless request as
    undecomposed, and creating a CR demands a T-shirt Size. Read from `two_backlog.enforce` in the
    project's own `.config.yaml`, default False.

    Default OFF is deliberate and load-bearing for UPGRADES: an existing project pulling a newer
    skill keeps its old flow (plan a CR, complete it whole, size with points) until it opts in, so
    the release does not break it. A project turns the workflow on with one line of config; this
    repo dogfoods it on. The soft, always-on parts of the model (the sizing vocabulary itself,
    link-asymmetry which only fires on links a project chose to write) are NOT gated here - only
    the rules that would refuse an unprepared project's existing workflow. The one predicate every
    hard gate consults, so none hard-codes the enforcement decision."""
    return bool(project_override(repo_root, "two_backlog.enforce", False))


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
    # An Issue is Discovery intake: Open (raw report) -> Triaging (being worked) -> Triaged
    # (decomposed into bugs, being delivered) -> Resolved (children all resolved; the DERIVED
    # successful terminal, G2). Closed/Won't Fix/Superseded are the abandonment terminals - an
    # Issue triaged to nothing, a non-issue, a duplicate. Resolved precedes them so it is the
    # `default_terminal_status` a bare close derives.
    "issue": ["Open", "Triaging", "Triaged", "Resolved", "Closed", "Won't Fix", "Superseded"],
    "test-spec": ["Draft", "Ready", "In Progress", "Complete", "Superseded"],
    "workflow": [
        "Created", "Planning", "Testing", "Implementing", "Verifying",
        "Reviewing", "Checking", "Done", "Paused", "Superseded",
    ],
    # Queued (waiting its turn) -> Spent (a run was opened from it). Withdrawn and Superseded are
    # the abandonment terminals: a charter the operator dropped, and one another charter replaced.
    # `Spent` precedes them so a bare close derives the successful terminal, as elsewhere.
    "charter": ["Queued", "Spent", "Withdrawn", "Superseded"],
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
    "issue": {"Resolved", "Closed", "Won't Fix", "Superseded"},
    "test-spec": {"Complete", "Superseded"},
    "workflow": {"Done", "Superseded"},
    # `Spent` is the successful terminal - a run was opened from this charter, so it will
    # never be run again. `Queued` is deliberately NOT terminal: a charter waiting its turn
    # is live signal, and the whole point of the queue is that it can still be re-ordered.
    "charter": {"Spent", "Withdrawn", "Superseded"},
}


def terminal_statuses(type_: str) -> set[str]:
    """The absorbing statuses for `type_` - the set whose rows are archive candidates.
    Empty for an unknown type. Intersected with the vocab so it can never name a
    status the type does not define."""
    return set(TERMINAL_STATUS.get(type_, set())) & set(STATUS_VOCAB.get(type_, []))


# The status a freshly created artefact of each type is born in - the entry state of its
# lifecycle. Declared HERE, beside the vocab it must belong to, because a create status is
# not derivable from vocab order: a story starts at `Draft`, never at the vocab's first
# entry `Proposed` (a pre-decomposition proposal state a created story does not occupy).
# The creators (`artifact.SPEC`, `file_finding.TYPES`) derive from this rather than restate
# it, so a vocab change lands in one file. Every value must be a member of STATUS_VOCAB.
CREATE_STATUS: dict[str, str] = {
    "epic": "Draft",
    "story": "Draft",
    "plan": "Draft",
    "bug": "Open",
    "cr": "Proposed",
    "rfc": "Draft",
    "issue": "Open",
    "test-spec": "Draft",
    "workflow": "Created",
    "charter": "Queued",
}


def create_status(type_: str) -> str:
    """The status a newly created artefact of `type_` starts in. Empty for an unknown type.
    Intersected with the vocab, exactly like `terminal_statuses`, so it can never name a
    status the type does not define."""
    st = CREATE_STATUS.get(type_, "")
    return st if st in STATUS_VOCAB.get(type_, []) else ""


def default_terminal_status(type_: str) -> str:
    """The status a `close` moves `type_` to when the caller names none: the FIRST absorbing
    state in the type's vocabulary order, which is its completed-successfully outcome (Done /
    Complete / Fixed / Accepted). The later absorbing states are the abandonment outcomes
    (Won't Fix, Rejected, Superseded, Withdrawn) - never a default; a caller asks for those
    explicitly. Empty for an unknown type, or one with no absorbing state."""
    absorbing = terminal_statuses(type_)
    return next((s for s in STATUS_VOCAB.get(type_, []) if s in absorbing), "")


# Findings (bug/cr/rfc) gain an `inbox` triage lane under schema v3: an
# agent-filed finding lands in `inbox`, and a *different* seat triages it into the
# workflow proper. The triaged target is the first accepted-into-workflow state per
# type - `Proposed` (cr) / `Draft` (rfc) are pre-workflow proposal states an agent
# finding never occupies, so triage promotes straight past them. Dormant under v2.
FINDING_TYPES: tuple[str, ...] = ("bug", "cr", "rfc")

#: The types whose acceptance criteria are EXECUTED (`verify_ac`), rather than prose a human
#: reads. A story and a bug are both DELIVERY units: each is planned, sized, held to the
#: criteria floor and reaches a terminal status by being built, so a criterion on either has
#: something to gate. A CR or an RFC is a REQUEST, decomposed rather than delivered, so a
#: command-shaped `Verify:` on one is assurance with nothing behind it.
#:
#: ONE authority, read by all three sites that used to decide it independently: the runner
#: (`verify_ac`), the validator's pseudo-verify warning, and the creators' refusal. Two of
#: them disagreed - the validator called a bug's Verify line "executed by nothing" while the
#: runner was about to execute it - so an author was told opposite things about one line and
#: a fixed bug had no agreed closure path. A rule held in two places diverges, and the looser
#: copy is the one that runs.
EXECUTES_VERIFIERS: tuple[str, ...] = ("story", "bug")


def executes_verifiers(type_: str) -> bool:
    """True when this type's `- **Verify:**` lines are run rather than read."""
    return (type_ or "").strip().lower() in EXECUTES_VERIFIERS


#: A terminal status reached by DECIDING rather than by delivering. The terminal set mixes the
#: two - `Done`/`Fixed` are earned by building, `Won't Fix`/`Superseded`/`Rejected`/`Withdrawn`
#: are rulings - and callers that care about DELIVERY must not treat a ruling as one. A unit
#: nobody built owes no acceptance criteria, no verification depth and no sprint close.
#:
#: Recognised by the WORDING rather than by a per-type list, so a status added to any type's
#: vocabulary lands on the correct side without an edit here. `Superseded` is the one that has
#: to be named: it says another artefact took the work over, which is a ruling however the
#: sentence is phrased.
_DECISION_TERMINAL_MARKERS = ("won't", "wont", "reject", "withdraw", "supersede", "duplicate",
                              "cancel", "obsolete")


def is_decision_terminal(status: str) -> bool:
    """True when this terminal status was reached by a ruling rather than by delivery."""
    low = (status or "").strip().lower()
    return any(m in low for m in _DECISION_TERMINAL_MARKERS)


def is_delivered_terminal(type_: str, status: str) -> bool:
    """True when `status` is terminal for `type_` AND was reached by building the thing."""
    return is_terminal_status(type_, status) and not is_decision_terminal(status)


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


#: Parsed `.config.yaml` bodies, keyed by (path, FILE CONTENT). This function is called once
#: per artefact per lane - 4,495 times in a single `gate --only validate` run over this repo -
#: and re-parsed the YAML every time, which made PyYAML scanning ~75% of the validate and
#: constitution lanes.
#:
#: The key is the file's CONTENT (hashed), not its mtime. Content-keying makes a stale hit
#: impossible by construction rather than by argument: any edit, however fast, however
#: same-sized, is a different key and re-parses. Reading a 2KB file is not what cost anything
#: here - parsing it was - so the read still happens on every call and only the parse is saved.
#:
#: The key holds a DIGEST rather than the body, and the map is bounded. Keying on the body meant
#: every distinct config ever seen was retained in full for the life of the process: fine for a
#: short CLI, but the suite alone walks thousands of temp roots, and a long-lived agent process
#: would accumulate indefinitely.
_CONFIG_PARSE_CACHE: dict[tuple[str, str], object] = {}
_CONFIG_PARSE_CACHE_MAX = 256


def _parse_config_text(cfg_path: Path, text: str):
    """Parse a config body, memoised on its exact content. Returns the mapping, or None when
    it cannot be parsed (the caller then falls back to its default, as it always did)."""
    import hashlib
    key = (str(cfg_path), hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest())
    if key in _CONFIG_PARSE_CACHE:
        return _CONFIG_PARSE_CACHE[key]
    if len(_CONFIG_PARSE_CACHE) >= _CONFIG_PARSE_CACHE_MAX:
        _CONFIG_PARSE_CACHE.clear()   # bounded: a whole-map drop, since the win is within one run
    try:
        import yaml  # soft dependency, mirrors config.py
    except ImportError:
        _warn_unhonoured(cfg_path, "PyYAML is not installed")
        return None
    try:
        parsed = yaml.safe_load(text) or {}
    except Exception as exc:  # noqa: BLE001 - a broken override must never break parsing
        _warn_unhonoured(cfg_path, f"it could not be parsed ({exc})")
        parsed = None
    # A failed parse is cached too: without it a broken config is re-parsed (and re-fails) on
    # every one of those thousands of calls, which is the slowest possible way to reach a default.
    _CONFIG_PARSE_CACHE[key] = parsed
    return parsed


def project_override(repo_root, dotted: str, default=None):
    """Read a dotted key from the project's `sdlc-studio/.config.yaml` (the override
    file only, no defaults merge). Self-contained and fully degrading: a missing
    file, no PyYAML, or malformed YAML all return `default`. This is the reader for
    parser-critical paths that must never hard-depend on PyYAML; the richer merged
    config (defaults + override) lives in config.py."""
    cfg_path = Path(repo_root) / "sdlc-studio" / ".config.yaml"
    if not cfg_path.exists():
        return default          # absent: silently the default, as it always was
    try:
        text = cfg_path.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        # BOTH arms matter, and narrowing this to OSError was a real regression. The read used to
        # sit inside the same broad `except` as the parse, so a non-UTF-8 byte in a config -
        # UnicodeDecodeError, which is a ValueError, NOT an OSError - warned and degraded. Moved
        # out and narrowed, it escaped instead: one legacy-encoded byte in a consuming project's
        # config turned 7 blocking gate lanes red with a message that never named the file.
        # A present-but-unreadable config (a directory, a permissions error) must also WARN and
        # not just return the default: silent-default is the exact failure `_warn_unhonoured`
        # exists to prevent, so returning the right value without the warning is only half right.
        _warn_unhonoured(cfg_path, f"it could not be read ({exc})")
        return default
    cur = _parse_config_text(cfg_path, text)
    if cur is None:
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
        "documented": "skill docs are incomplete - run `doc_coverage.py` and add the missing help/help.md command entry or reference-scripts.md script entry it names (a no-op in a consuming project, which has no SKILL.md to cover)",
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
        "weak-verify": "the story's `- **Verify:**` line is not executable - replace the prose with a runnable command (pytest/jest/curl ...), or scope out executable AC for this project",
        "missing-regression-test": "add an integration/regression-level test that reproduces the bug before the fix, so a recurrence is caught (see best-practices/testing.md)",
        "cross-epic-ac": "an AC references another epic's scope - move it to a story under the owning epic, or rescope the AC to this epic",
        "already-satisfied": "the unit's verifiers already pass - confirm with `verify_ac` and close it (do not re-build) rather than carrying it in the batch",
    },
    "reconcile": {
        "status-mismatch": "set the index row's Status to match the file (or fix the file)",
        "missing-row": "add an index row for this artifact",
        "orphan-row": "remove the index row - no file backs it (or restore the file)",
        "dead-row-link": "the index row links an artefact file that does not exist - restore the file (a bad checkout or an unstaged rename looks the same from here), or remove the row with `reconcile apply --prune-orphans`",
        "missing-index": "create the type's `_index.md`",
        "count-mismatch": "recompute the summary counts from the index rows",
        "index-status-column": "the index table's Status column is mis-named or absent, so rows cannot be compared - fix the `_index.md` header row (name the column `Status`) and re-run reconcile",
        "breakdown-unticked": "an epic breakdown checkbox is unticked over a terminal unit - run `reconcile apply` to sync every breakdown box to its unit's status (both directions)",
        "breakdown-ticked-early": "an epic breakdown checkbox is ticked over a still-live unit (masks unfinished work) - run `reconcile apply` to untick it, or finish the unit",
        "epic-status-stale": "an epic is still live over a breakdown whose every declared unit is terminal (masks FINISHED work - the delivery backlog reads as larger than it is) - close it with `transition.py set --id EPxxxx --status Done`, which runs the epic's own gates; `reconcile apply` deliberately does not write this one, so a completion is never recorded round them",
        "epic-points-stale": "an epic's derived point total no longer equals the sum of its stories' points - run `reconcile apply` to recompute it (the total is DERIVED, never hand-set; the epic's own coarse estimate is its T-shirt `Size`, not points)",
        "link-asymmetry": "a request/child link is declared on one side only - add the missing half (the child's `Parent:` or the request's `Decomposed-into:`) so it resolves both ways, or fix the id that resolves to nothing; a decomposition writes BOTH sides",
        "supersession-asymmetry": "a supersession is recorded on one side of the pair only - add the missing half (the superseder's `Supersedes:` or the superseded artefact's `Superseded by:`) so a reader arriving from either direction sees it, or record the pair in sdlc-studio/.supersession-waivers.json with the reason it is legitimate asymmetry (a partial supersession is); the tolerated set may only shrink",
        "epic-index-derivable": "an epic index cell the tree can derive does not carry it - `reconcile apply` fills a PLACEHOLDER cell from the census; a cell holding a real value the census contradicts is reported and left alone, because rewriting it would drop the only record of it (correct it by hand, or leave it as history)",
        "undecomposed": "a discovery item accepted into the workflow has no children - decompose it into the units that deliver it (refine a request into epics/stories; triage an Issue into bugs), or close it if it is not going ahead; a still-Proposed/Draft/Open item is pre-triage intake and is not flagged",
        "linked-epics": "the request index's Linked Epics cell disagrees with the file's `Decomposed-into` - run `reconcile apply` to census it from the files; a request that was never decomposed keeps its placeholder and is not flagged",
        "stale-index-stamp": "the index's `**Last Updated:**` header is older than the newest date on its own rows, so it claims a freshness it does not have - run `reconcile apply` to restamp it from the rows (the stamp is derived, never hand-set; a header AHEAD of the rows is just an index nothing has been added to and is not flagged)",
        "index-field": "an index CELL disagrees with the artefact it is derived from - a bug's Severity, an RFC's Status, a CR's Priority. The index is derived output, and `status.py` reads it, so a stale cell makes every backlog figure taken from it wrong. Run `reconcile apply` to project the cells from the artefacts (an off-schema row is skipped rather than written into, and reported here so it can be fixed by hand)",        "spawned-column": "a request's index cell claiming the work it spawned disagrees with the census of what actually names it as parent. A one-off backfill corrected 33 such cells here and nothing kept them true, so the next decomposition left a stale one exactly as before - correct the cell from the census, which `children_of` computes; the column can be wrong by over-claiming as readily as by under-claiming",
        "request-derivable": "every child a request produced is resolved, so its successful terminal is EARNED but was never recorded - run `reconcile apply` to derive it (Complete / Accepted / Resolved), which goes through `transition` so the index row and cascades still run; a childless request is the separate `undecomposed` case and is never derived. Where the item names a gate that still refuses (an RFC with an open decision, say), `reconcile apply` CANNOT clear it and says so - resolve that gate first",
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


#: The corpus memo, live only inside `corpus_cache()`. `None` means OFF, and off is the default
#: everywhere: a cache that outlives the read it was taken for serves a writer its own stale
#: view, and every one of this module's callers may write.
_CORPUS_CACHE: "dict | None" = None


@contextlib.contextmanager
def corpus_cache():
    """Read the artefact corpus ONCE for the duration of a read-only sweep.

    `find_by_id`, `children_of` and every `artifact_files` caller walk the whole tree and read
    every file. Called once that is cheap; called once per unit it is quadratic, and one
    `reconcile detect` over this workspace opened 777,732 files and took 22 seconds - paid on
    every commit, because reconcile is a gate lane.

    OPT-IN and SCOPED, never a module-level memo. The cache cannot see a write, so anything
    holding it open across one would read its own stale corpus - and the caller most likely to
    write is `reconcile apply`, sitting next to the sweep this exists for. A `with` block makes
    the window explicit and closes it on the way out, including on an exception.

    Nesting is a no-op rather than an error: a sweep that calls a helper which also takes the
    cache must not get a second, emptier one."""
    global _CORPUS_CACHE  # noqa: PLW0603 - the memo IS module state; the scope is the guard
    if _CORPUS_CACHE is not None:
        yield _CORPUS_CACHE
        return
    _CORPUS_CACHE = {}
    try:
        yield _CORPUS_CACHE
    finally:
        _CORPUS_CACHE = None


def corpus_cache_active() -> bool:
    """Whether a corpus cache is currently open. For tests and diagnostics, never for control."""
    return _CORPUS_CACHE is not None


def iter_artifact_files(type_: str, repo_root: Path, trust_names=frozenset()):
    """Yield `(path, text)` for each artifact file of `type_`, memoised inside `corpus_cache`.

    `text` is the file's content, read to apply the is-artifact filter - EXCEPT for a filename
    in `trust_names`, which is yielded as `(path, None)` WITHOUT being read. A caller that
    already knows a file is a closed artefact (e.g. from a digest keyed by filename) passes its
    name here to skip the read - the context-tiering optimisation. The filter/exclusion rules
    match `artifact_files`; only the read is elided for trusted names.

    A `trust_names` call BYPASSES the cache in both directions. Its results differ from an
    ordinary walk's by construction (a trusted file yields `None` for its text), so serving one
    from the other's memo would hand a caller the opposite of what it asked for."""
    if _CORPUS_CACHE is None or trust_names:
        yield from _walk_artifact_files(type_, repo_root, trust_names)
        return
    key = ("files", type_, os.path.abspath(repo_root))
    rows = _CORPUS_CACHE.get(key)
    if rows is None:
        rows = _CORPUS_CACHE[key] = list(_walk_artifact_files(type_, repo_root, frozenset()))
    yield from rows


def _walk_artifact_files(type_: str, repo_root: Path, trust_names=frozenset()):
    """The unmemoised walk. `iter_artifact_files` is the only caller."""
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
        except (OSError, UnicodeDecodeError):
            # Unreadable OR not valid UTF-8 (a half-written or binary-corrupted artefact from a
            # crashed session): keep it visible so a checker NAMES it, never let one bad file crash
            # every scanner that walks the tree.
            yield p, None
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


def fence_step(stripped: str, fence: tuple[str, int] | None) -> tuple[tuple[str, int] | None, bool]:
    """Advance a CommonMark fenced-block state machine by one already-stripped line.

    Returns `(new_fence_state, is_fence_line)`. `fence` is None outside a block, else
    `(marker_char, opening_run_length)`.

    Two rules a naive toggle gets wrong, both of which have shipped as live defects here:

    * A block closes only on the SAME marker character at the opening run length or LONGER, so
      the inner ```text of a ````markdown block is content, not a closer.
    * A closing fence "may be followed only by spaces" (CommonMark 4.5). A line carrying an info
      string - ```markdown, ```python, ~~~text - therefore never closes; it is content inside an
      open block. Treating it as a closer released the block early and turned the illustration
      beneath it into live document content, which for the acceptance-criteria parser meant an
      illustrative Verify line became an EXECUTED shell verifier.

    An opener may carry an info string; only the closer may not. Callers that merely need to skip
    fenced content should treat `is_fence_line` as "skip this line too".
    """
    marker = "`" if stripped.startswith("```") else ("~" if stripped.startswith("~~~") else None)
    if marker is None:
        return fence, False
    run = len(stripped) - len(stripped.lstrip(marker))
    if fence is None:
        return (marker, run), True
    if marker == fence[0] and run >= fence[1] and not stripped[run:].strip():
        return None, True
    # a shorter fence, a different character, or a run carrying an info string: all content
    return fence, True


RETRACTED_DEPTH = "RETRACTED"


def depth_retracted(text: str) -> bool:
    """True when a unit's `Verification depth` was withdrawn by a reopen.

    Lives here because THREE copies of this predicate existed - one public and callerless in
    `transition`, one inlined inside `_retract_depth`, one in `sprint` justified by a
    no-sibling-import rule. Both modules already import this library, so the rule costs nothing
    and there is one place for it to be wrong."""
    return (extract_field(text, "Verification depth") or "").strip().upper().startswith(RETRACTED_DEPTH)


#: The heading an artefact records its open questions under, and the heading a RULING moves
#: them to. Matched at any depth, because the templates differ by type.
#: A SUFFIX after the heading text does not make it a different heading. `## Open Questions
#: (deferred)` anchored to `$` was invisible to the detector, so one token of author edit
#: turned the gate off for the whole section - and read as a clean artefact, not a refusal.
_OPEN_Q_RE = re.compile(r"^#+\s*Open Questions\b[^\n]*$(.*?)(?=^#+\s|\Z)", re.M | re.S)
# A `## Resolved Questions` band needs no pattern of its own: the open-questions pattern is
# anchored to `## Open Questions`, so moving a question under Resolved takes it out of scope
# by not matching. The route works by OMISSION, and a pattern defined beside it and never
# referenced read as though something enforced it.
_Q_ITEM_RE = re.compile(r"^\s*[-*]\s*\[( |x|X)\]\s*(.+)$", re.M)


def _own_id_of(text: str) -> str:
    """The id an artefact's own title line declares, or "" when it declares none.

    Read from the text rather than taken as an argument, so every existing caller gets the
    self-citation refusal without a signature change. "" is the honest answer for a fragment
    with no title - the caller then applies no self-citation rule at all, rather than guessing
    an id and refusing a legitimate follow-up on it.
    """
    for line in (text or "").splitlines():
        if line.startswith("#"):
            m = ID_SEARCH_RE.search(line)
            return norm_id(m.group(0)) if m else ""
        if line.strip():
            break
    return ""


def unresolved_questions(text: str, repo_root=None) -> list:
    """The Open Questions a TERMINAL artefact must not still be carrying.

    THE one implementation, so `validate` and the transition gate cannot disagree about what a
    resolved question is - two readings of one rule is two rules, and the looser one wins.

    A question is RESOLVED by either route the templates offer, and by nothing else:

    * a **ruling**, recorded by moving the item under a `Resolved Questions` heading, or
    * a **follow-up artefact**, cited by id on the item and RESOLVING in the workspace.

    An item ticked with no destination is refused. That is the whole point: the escape hatch
    cannot be a tick pointing at nothing, which is how sixteen artefacts reached a terminal
    status carrying questions nobody had answered.

    `repo_root` is needed to resolve a cited id. Without it a cited id is accepted on its shape
    alone - a caller that cannot look up ids is not a reason to invent a stricter answer, but it
    IS reported by the caller that can.
    """
    # EVERY such section, not the first. `search` read one, so a second `## Open Questions`
    # anywhere below it was never scanned - and an artefact carrying its unanswered question
    # there reached a terminal status with the detector reporting clean.
    sections = [m.group(1) for m in _OPEN_Q_RE.finditer(text or "")]
    if not sections:
        return []
    own = extract_record_id(_own_id_of(text or "") or "") or ""
    offending = []
    for state, body in _Q_ITEM_RE.findall("\n".join(sections)):
        item = body.strip()
        if not item or _DECLARES_NONE_RE.match(item) or "{{" in item:
            # A `{{question}}` placeholder is an UNFILLED TEMPLATE, not an unanswered question.
            # It is a real defect and validate's placeholder rule owns it; reporting it here as
            # well would double-report it and - worse - refuse a transition for the wrong
            # reason, naming two routes out that neither apply.
            #
            # `- [ ] None - behaviour fully extracted from scripts/x.py` is the template
            # saying there ARE no questions. Reading it as an unanswered one would force ten
            # already-correct artefacts to be "fixed", which is a guard manufacturing work.
            continue
        defect = _citation_defect(item, own, repo_root)
        if _RULING_RE.search(item) or _decision_cited(item, repo_root):
            # A ruling recorded ON THE ITEM is the same fact as one moved under a heading, and
            # a decision row is the project's own form for a ruling. Demanding the heading
            # would be demanding a layout, not an answer.
            #
            # But a ruling that NAMES a destination is held to that destination, exactly as the
            # follow-up route is. The verb used to skip the check outright, so `resolved by
            # BG9999` - a ruling citing an artefact nothing in the workspace holds - was
            # accepted while the identical citation without the verb was refused. Four words of
            # prose bought an exemption from the one thing being checked, which is the
            # tick-pointing-at-nothing this whole helper exists to refuse.
            if defect:
                offending.append(defect)
            continue
        if state == " ":
            offending.append(item)
            continue
        if not ID_SEARCH_RE.findall(item):
            offending.append(f"{item} (ticked with no ruling and no follow-up id)")
            continue
        if defect:
            offending.append(defect)
    return offending


def _citation_defect(item: str, own: str, repo_root) -> str:
    """Why an item's cited destination answers nothing, or "" when it answers.

    ONE destination check, consulted by BOTH routes out of an open question, so a ruling and a
    follow-up cannot be held to different standards - two readings of one rule is two rules,
    and the looser one wins.
    """
    # The decision route SETTLES the item when it holds, before any follow-up analysis. A
    # ruling that names a real decision row has named its destination, and an artefact citing
    # its own id ALONGSIDE that row - "RULED MOOT: CR0019 is Superseded, see D0011" - is
    # describing what was ruled, not offering itself as its own follow-up. Running the
    # self-citation check first reported three such items across the live corpus.
    decision_ids = _DECISION_ID_RE.findall(item)
    if decision_ids:
        if _decision_cited(item, repo_root):
            return ""
        if _decisions_table(repo_root) is not None:
            return (f"{item} (cites decision row {', '.join(decision_ids)}, "
                    "which the decisions table does not hold)")
        return ""
    cited = ID_SEARCH_RE.findall(item)
    if not cited:
        return ""
    # An artefact citing ITSELF answers nothing. `find_by_id` only proves an id resolves, and an
    # artefact always resolves to itself, so self-citation satisfied the follow-up route in
    # full. A follow-up is somewhere ELSE by definition.
    elsewhere = [c for c in cited if not own or norm_id(c) != own]
    if not elsewhere:
        return f"{item} (ticked citing only itself, which is not a follow-up)"
    if repo_root is not None and not any(find_by_id(repo_root, c) for c in elsewhere):
        return f"{item} (cites {', '.join(elsewhere)}, which resolves to no artefact)"
    return ""


#: `None`, `None - <why>`, `n/a`: the template's way of saying there are no questions.
_DECLARES_NONE_RE = re.compile(r"^(none|n/?a)\b", re.IGNORECASE)

#: A ruling recorded on the item itself, in the forms this corpus actually uses.
_RULING_RE = re.compile(r"\b(ruled by|ruled:|settled in|resolved by|decided:)\b", re.IGNORECASE)

#: A decision row id - the project's own form for a recorded ruling.
_DECISION_ID_RE = re.compile(r"\bD\d{4}\b")


def _decisions_table(repo_root) -> str | None:
    """The decisions table's text, or None when this project keeps none.

    An absent table is not a failed lookup, and the two must not be conflated. A project that
    records no decision rows must not have every `ruled by D0001` refused on the strength of a
    file it never had - that is a guard manufacturing work. A table that EXISTS and does not
    hold the cited id is a dangling citation, which is a real defect, and separating the two is
    the only way to report the second without inventing the first.
    """
    if repo_root is None:
        return None
    try:
        return (Path(repo_root) / "sdlc-studio" / "decisions.md").read_text(encoding="utf-8")
    except OSError:
        return None


def _decision_cited(item: str, repo_root) -> bool:
    """True when the item cites a decision row that EXISTS.

    A decision id is a ruling; an id pointing at no row is not, which is the same standard the
    follow-up-artefact route is held to."""
    ids = _DECISION_ID_RE.findall(item)
    if not ids:
        return False
    rows = _decisions_table(repo_root)
    if rows is None:
        return True
    return any(re.search(rf"^\|\s*{d}\s*\|", rows, re.M) for d in ids)


def questions_are_resolved(text: str, repo_root=None) -> bool:
    """Convenience inverse of `unresolved_questions`, for a caller that wants a verdict."""
    return not unresolved_questions(text, repo_root)


def normalise_fence_languages(text: str, default: str = "text") -> str:
    """Supply `default` as the info string of every unlabelled fenced block that CLOSES.

    A generator rendering an author's prose cannot control whether they fenced their evidence,
    and markdownlint MD040 refuses a bare ``` opener. Without this the deterministic filer mints
    artefacts the deterministic gate rejects, and the only way past is to hand-edit the file the
    filer exists to stop anyone hand-writing.

    Four things it deliberately does NOT do, each a live defect if got wrong:

    * A CLOSER is never labelled. "The closing code fence may be followed only by spaces"
      (CommonMark 4.5), so a language on it stops it closing, releasing the block early and
      turning the illustration below into live document content.
    * A block already carrying an info string is untouched - the author's language wins.
    * An UNCLOSED opener is left bare. It is malformed either way, and labelling it makes a
      broken block look deliberate instead of leaving it visibly broken.
    * A fence marker inside a FOUR-SPACE INDENTED code block is content, not a fence. Missing
      this desynchronised the state machine: the literal ``` in an indented illustration was
      taken for a real opener, so author content was rewritten AND the genuine bare fence
      further down was consumed as that block's closer and left unlabelled - failing the very
      lint this exists to satisfy, while corrupting the document on the way past.

    Known limit, stated rather than silently wrong: a fence inside a BLOCKQUOTE (`> ```) is not
    labelled. MD040 still flags it, which is visible and fixable; guessing at quoted content is
    not. Line endings are preserved, so a CRLF document does not come back mixed.
    """
    lines = text.split("\n")
    fence: "tuple[str, int] | None" = None
    opener: int | None = None
    label: list = []
    for i, raw in enumerate(lines):
        line = raw[:-1] if raw.endswith("\r") else raw
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        # Outside a fenced block, four spaces (or a tab) means an INDENTED CODE BLOCK, whose
        # contents are literal. A ``` in there is text an author wrote, not a fence.
        if fence is None and (indent >= 4 or line.startswith("\t")):
            continue
        new_fence, is_fence_line = fence_step(stripped, fence)
        if is_fence_line:
            if fence is None and new_fence is not None:          # an opener
                opener = i if not stripped[new_fence[1]:].strip() else None
            elif fence is not None and new_fence is None:        # a closer
                if opener is not None:
                    label.append((opener, fence[0], fence[1]))
                opener = None
            # else: a fence line INSIDE an open block, which is content
        fence = new_fence
    for i, marker, run in label:
        raw = lines[i]
        eol = "\r" if raw.endswith("\r") else ""
        line = raw[:-1] if eol else raw
        pad = line[:len(line) - len(line.lstrip())]
        lines[i] = f"{pad}{marker * run}{default}{eol}"
    return "\n".join(lines)


# A CommonMark code span: an opening backtick run closed by a run of EQUAL length. Deliberately
# single-line - a cross-line greedy match would swallow ordinary prose between two stray
# backticks, and masking prose a guard is meant to read is worse than leaving one span visible.
_CODE_SPAN_RUN = re.compile(r"(?<!`)(`+)(?!`)([^\n]+?)(?<!`)\1(?!`)")


def mask_code_spans(text: str, replacement: str = "C") -> str:
    """Replace every inline code span in `text` with `replacement`, delimiters included.

    Backticks are how an author says "the characters between these are QUOTED, not meant". A
    reader of stored prose that cannot tell quoting from content has to treat an artefact whose
    evidence quotes shell syntax - because the defect it reports IS shell syntax - as if a shell
    had eaten the field, and the only way past that is to reword the evidence, which trades
    fidelity for a green gate.

    The default replacement is a word-like token rather than the empty string, and that is the
    whole care in this function: deleting a span closes the spaces that flanked it and butts the
    surrounding words against punctuation, which is exactly the damage signature a completed
    command substitution leaves. Masking must not manufacture the hole it is helping to look for.

    An unpaired backtick, or runs of unequal length, form no span and are left where they are -
    that shape is not quoting and stays visible to whatever is reading."""
    return _CODE_SPAN_RUN.sub(replacement, text)


def id_number(record_id: str) -> int | None:
    """Numeric part of a v2 sequential ID ('US0042' -> 42, 'CR-0007' -> 7). A v3 ULID id
    ('BG-01JQK3F8') has no sequential number - even one whose suffix ends in digits - so this
    returns None for it, keeping ULID ids out of the max+1 numeric allocation path."""
    # letters, optional dash, then four to seven trailing digits and nothing else. This admits
    # any sequential prefix (US, CR, and the meta ids LL/RV/RETRO) but never a v3 ULID, whose
    # base32 suffix is 8+ chars and so cannot fullmatch even when it happens to be all digits.
    # Four is the minted width; the upper bound is what separates a long sequential id from a
    # ULID, and without accepting 5+ a `US01010` would return None and be invisible to the
    # max+1 allocator, which would then re-mint an id already in use.
    m = re.fullmatch(r"[A-Za-z]+-?(\d{4,7})", record_id)
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


# The current schema version has ONE source of truth: templates/config.yaml, the file `init`
# copies into every new project. Everything that needs "what version is current" (the upgrade
# target, the skill-vs-project drift check) derives it from here, so the seed and the upgrade
# target cannot disagree. This is DISTINCT from `schema_version`'s default of 2, which is the
# fallback an UN-STAMPED legacy workspace resolves to (config-defaults.yaml) - a different fact.
_CURRENT_SCHEMA_FALLBACK = 3  # matches templates/config.yaml; used only if the template is unreadable


def current_schema() -> int:
    """The current artefact schema version - read from templates/config.yaml, the new-project seed.

    The single source of truth for "current". Falls back to `_CURRENT_SCHEMA_FALLBACK` (kept in
    step with the template) only if the template cannot be read, so a moved/renamed template
    degrades to a known-current constant rather than silently reporting the legacy fallback."""
    tmpl = Path(__file__).resolve().parents[2] / "templates" / "config.yaml"
    try:
        text = tmpl.read_text(encoding="utf-8")
    except OSError:
        return _CURRENT_SCHEMA_FALLBACK
    m = re.search(r"^schema_version:\s*(\d+)", text, re.M)
    return int(m.group(1)) if m else _CURRENT_SCHEMA_FALLBACK


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


# -----------------------------------------------------------------------------
# The design-persona registry (sdlc-studio/personas/index.md)
# -----------------------------------------------------------------------------
# Who the product is FOR - the goal-directed design personas, not the review seats that
# critique artefacts (those live in personas/seats/ and resolve through persona_resolve).
# One reader, so every command that needs a design target derives it from the registry
# instead of restating a list that drifts.

#: The roles the registry declares, in the order the index states them.
PERSONA_ROLES = ("primary", "secondary", "negative")
#: A role heading: `## Primary (the design target)`, `### Negative`, ...
_PERSONA_ROLE_RE = re.compile(r"^#{2,}\s*(primary|secondary|negative)\b", re.I)


class PersonaEntry(NamedTuple):
    """One declared design persona: its name, its declared role, and its card path resolved
    against the workspace (None when the bullet carries no local link)."""
    name: str
    role: str
    card: str | None


class PersonaRegistry(NamedTuple):
    """The parsed registry. `available` is the honest-absence flag: False means the reader
    could not read a registry (no `index.md`, unreadable, or no role heading in it) and
    `reason` says which. A registry that parses but lists nobody is `available=True` with no
    entries - genuinely empty, which is a different fact and must stay distinguishable."""
    path: str
    available: bool
    reason: str | None
    entries: tuple[PersonaEntry, ...]

    @property
    def primary(self) -> PersonaEntry | None:
        """The declared Primary - the design target - or None."""
        return next((e for e in self.entries if e.role == "primary"), None)

    def by_role(self, role: str) -> tuple[PersonaEntry, ...]:
        return tuple(e for e in self.entries if e.role == role.lower())

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(e.name for e in self.entries)

    def find(self, name: str) -> PersonaEntry | None:
        """The entry a supplied name refers to, matched on a normalised key so
        `maya okafor`, `Maya Okafor` and `maya-okafor` are one person. None when unregistered."""
        key = _persona_key(name)
        if not key:
            return None
        return next((e for e in self.entries if _persona_key(e.name) == key), None)


def _persona_key(name: str) -> str:
    """The normalised match key for a persona name (letters and digits only, lower-cased)."""
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


def _persona_bullet(line: str) -> tuple[str, str | None] | None:
    """`(name, href)` from a registry bullet, or None when the line is not a bullet.

    Accepts the three shapes a registry uses: a linked card
    (`- [Maya Okafor](maya-okafor.md) - ...`), a bold name, or bare prose whose name runs up
    to the first ` - ` separator."""
    m = re.match(r"^\s*[-*]\s+(.*)$", line)
    if not m:
        return None
    body = m.group(1).strip()
    if not body:
        return None
    link = re.match(r"^\[([^\]]+)\]\(([^)]+)\)", body)
    if link:
        return link.group(1).strip(), link.group(2).strip()
    bold = re.match(r"^\*\*([^*]+)\*\*", body)
    if bold:
        return bold.group(1).strip(), None
    name = re.split(r"\s+[-–:]\s+", body, maxsplit=1)[0].strip()
    return (name, None) if name else None


def persona_registry(repo_root) -> PersonaRegistry:
    """Parse `sdlc-studio/personas/index.md` into its declared Primary / Secondary / Negative
    personas with their card paths.

    NEVER returns a bare empty result for a registry it could not read: an absent, unreadable or
    heading-less index comes back `available=False` with a `reason` the caller reports, so
    'there is no registry' can never be mistaken for 'the registry declares nobody'. Read-only.
    """
    path = Path(repo_root) / "sdlc-studio" / "personas" / "index.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        why = ("no persona registry at" if not path.exists() else f"cannot read ({exc.strerror})")
        return PersonaRegistry(str(path), False, f"{why} {path}", ())
    entries: list[PersonaEntry] = []
    role: str | None = None
    seen_heading = False
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        # the shared CommonMark tracker, never a toggle: a bullet quoted inside a ````markdown
        # block is an example, and a toggle registered it as a declared persona
        fence, is_fence_line = fence_step(line.lstrip(), fence)
        if is_fence_line or fence is not None:
            continue
        if line.startswith("#"):
            m = _PERSONA_ROLE_RE.match(line)
            role = m.group(1).lower() if m else None
            seen_heading = seen_heading or role is not None
            continue
        if role is None:
            continue
        bullet = _persona_bullet(line)
        if bullet is None:
            continue
        name, href = bullet
        card = None
        if href and not re.match(r"^[a-z][a-z0-9+.-]*:", href):
            card = str((path.parent / href.split("#", 1)[0]).resolve())
        entries.append(PersonaEntry(name, role, card))
    if not seen_heading:
        return PersonaRegistry(str(path), False,
                               f"{path} declares no Primary/Secondary/Negative heading, so no "
                               f"design target could be read from it", ())
    return PersonaRegistry(str(path), True, None, tuple(entries))


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
    id-resolution lands in one place.

    Inside `corpus_cache` this reads a by-id index built once instead of walking every type for
    every lookup - 650 lookups over this workspace walked the corpus 650 times. The index keeps
    the FIRST match in `ARTIFACT_TYPES` order, which is the answer the linear walk gave, so the
    memo cannot change which of two same-id artefacts wins."""
    root = Path(repo_root)
    norm = norm_id(rec_id)
    if _CORPUS_CACHE is not None:
        key = ("byid", os.path.abspath(root))
        index = _CORPUS_CACHE.get(key)
        if index is None:
            index = _CORPUS_CACHE[key] = {}
            for type_ in ARTIFACT_TYPES:
                for p in artifact_files(type_, root):
                    rec = extract_record_id(p.stem)
                    if rec:
                        index.setdefault(norm_id(rec), (p, type_))
        hit = index.get(norm)
        if hit is not None:
            return hit
    else:
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


# -----------------------------------------------------------------------------
# The request -> product link: the primitive the two-backlog gates share
# -----------------------------------------------------------------------------
#
# A child names its parent UP; a request names its children DOWN. Both directions are recorded so
# reconcile can verify each link resolves both ways (a link asserted on one side only is drift).
# A story's parent is its `Epic:` (the pre-existing specialisation, kept); every other child - an
# epic under a CR, a CR under an RFC - names its parent with the generic `Parent:` field. A
# request lists the units it was decomposed into with `Decomposed-into:`.
PARENT_FIELD = "Parent"
DECOMPOSED_FIELD = "Decomposed-into"

#: The metadata fields that may legitimately repeat. Everything else is single-valued, and a
#: repeated single-valued field is a defect: `extract_field` searches, so it reads FIRST-WINS,
#: and `transition._set_field` substitutes with `count=1`, so a correction rewrites the first
#: line and leaves the rest standing - looking like live metadata to a reader while the gate
#: reads the other one.
#:
#: DECLARED, not observed. A guard inferring plurality from the corpus would learn whatever the
#: corpus happens to contain, so the day a field is wrongly repeated twice it becomes exempt.
#: `Parent` is plural by design - a shared batch epic delivers more than one request, and
#: `parent_refs` reads every line - and 23 live epics rely on it.
PLURAL_FIELDS = frozenset({PARENT_FIELD, DECOMPOSED_FIELD})
_PARENT_FIELD_RE = re.compile(r"(?m)^>?[^\S\n]*\*\*Parent:\*\*[^\S\n]*(.*)$")
# The LEGACY upward link an epic carries before the two-backlog `Parent:` convention: the
# `cr action` workflow stamps `> **Change Request:** [CR-0001](...)` on each epic it creates.
_CHANGE_REQUEST_FIELD_RE = re.compile(r"(?m)^>?[^\S\n]*\*\*Change Request:\*\*[^\S\n]*(.*)$")


def change_request_ref(source) -> str | None:
    """The originating CR an epic declares the LEGACY way - `> **Change Request:** CR-0001` (the
    `cr action` convention that predates the two-backlog `Parent:` link) - or None. `child_parent`
    falls back to it so a CR decomposed the OLD way is correctly seen as having children: without
    it, `children_of` reads only `Parent:`/`Epic:`, so `discovery_awaiting`, `migrate` and
    `undecomposed_drift` false-flag an already-decomposed old-flow CR as un-refined."""
    text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
    m = _CHANGE_REQUEST_FIELD_RE.search(text)
    if not m:
        return None
    mid = ID_SEARCH_RE.search(m.group(1))
    return mid.group(0) if mid else None


def parent_ref(source) -> str | None:
    """The parent id a child names with `> **Parent:** CR0271`, or None when it has none
    (`-`/`--`/absent). Accepts the child text or a `Path`. The generic upward link; a story ALSO
    carries `Epic:` (read by `story_epic`), so use `child_parent` to get either uniformly.

    Returns the FIRST NON-sentinel parent, so the singular reader agrees with `parent_refs` even
    when an earlier `Parent:` line is a `-`/`--`/empty sentinel (it delegates to that plural read)."""
    refs = parent_refs(source)
    return refs[0] if refs else None


def parent_refs(source) -> list[str]:
    """EVERY parent id a child declares via `> **Parent:** <id>`, in order, de-duplicated. A shared
    batch epic (`refine --into`) delivers more than one request and carries one `Parent:` line per
    request, so the upward link resolves for each of them - `parent_ref` (singular) returns only the
    first and is kept for the common single-parent read. A `-`/`--`/empty value contributes nothing."""
    text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
    out: list[str] = []
    for m in _PARENT_FIELD_RE.finditer(text):
        val = m.group(1).strip()
        if val in ("", "-", "--"):
            continue
        mm = ID_SEARCH_RE.search(val)
        if mm and mm.group(0) not in out:
            out.append(mm.group(0))
    return out


def child_parent(source) -> str | None:
    """The parent id a child declares, most-specific-first: the two-backlog `Parent:` (generic),
    else a story's `Epic:`, else the LEGACY `Change Request:` an old-flow epic carries, or
    None. The one reader every consumer of the upward link shares, so a story-under-epic, an
    epic-under-CR (new link), and an epic-under-CR (old `cr action` link) all resolve the same way -
    which is what keeps `children_of` correct on a project that has NOT adopted the two-backlog
    workflow (its CRs are decomposed via `Change Request:`, not `Parent:`)."""
    text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
    par = parent_ref(text)
    if par:
        return par
    epic = story_epic(text)
    if epic:
        m = ID_SEARCH_RE.search(epic)
        return m.group(0) if m else None
    return change_request_ref(text)


# -----------------------------------------------------------------------------
# Supersession: one grammar for every spelling the corpus carries
# -----------------------------------------------------------------------------
#
# A supersession is a fact about a PAIR, and each side records it in its own field. Nine distinct
# spellings are in the corpus, measured rather than assumed - the specification for this named six,
# and the three it missed are the free prose ones a field-name allowlist would have read as an
# absence. An unrecognised spelling is the dangerous failure here: it makes a recorded supersession
# look unrecorded, which is a report of drift that does not exist.
#
# So the label is matched on the VERB, not on an enumerated set of field names, and the direction
# is read from that verb: `Supersedes` names what this artefact replaces, `Superseded by` names
# what replaces it. The template ships a COMBINED `Supersedes / Superseded by:` field carrying
# both verbs, so its direction comes from the value instead; recording both directions for it
# manufactured a reversed phantom pair for every one of the fifteen in the corpus.

#: `[text](url)` - reduced to its TEXT before ids are scanned, so a link's target contributes no
#: id and its label still does. Applied before the parenthetical strip, since a link's URL is
#: itself a parenthetical run.
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")

#: `> **Superseded by:** X`, `> **Supersedes (in part):** X`, and the dated prose forms
#: `> **Superseded 2026-07-04 by [CR-0142](...).**` - the label is whatever sits inside the bold
#: run, and it qualifies on containing the verb.
SUPERSESSION_FIELD_RE = re.compile(
    r"(?m)^>?[^\S\n]*\*\*([^*]*[Ss]upersed[^*]*?)\*\*[^\S\n]*(.*)$")

# A partial-supersession sentence names decision and workstream rows (`decisions **D5** and
# workstreams **WS3**`), which are not artefacts - a pair built from one points at nothing. No
# filter for them here: `ID_SEARCH_RE`'s prefix set does not include `D` or `WS`, so they never
# reach this code. A filter was written anyway and a mutant proved it unfireable - a guard that
# cannot fire reads as protection and provides none. `test_the_id_grammar_excludes_decision_rows`
# pins the premise instead, so a `D` prefix added to the id grammar reddens rather than silently
# turning `D5` into a supersession counterpart.

#: Values meaning "nothing declared". The template's placeholder, and the en dash a hand edit left.
SUPERSESSION_EMPTY = ("", "-", "--", "–", "—", "none", "n/a")

#: Directions a declaration can carry. `AMBIGUOUS` is a real answer and not a failure: a combined
#: field whose value names an id but no verb states a pairing without saying which way round, and
#: guessing would invent half a supersession.
SUPERSEDES, SUPERSEDED_BY, SUPERSESSION_AMBIGUOUS = "supersedes", "superseded-by", "ambiguous"


def supersession_direction(label: str, value: str = "") -> str:
    """Which way round a declaration points, read from its verb.

    The combined template field carries both verbs, so it defers to the value's verb; a value
    with neither is AMBIGUOUS rather than assumed.
    """
    low = label.lower()
    forward, backward = "supersedes" in low or "supersede " in low, "superseded" in low
    if forward and backward:
        vlow = value.lower()
        if "superseded" in vlow:
            return SUPERSEDED_BY
        if "supersede" in vlow:
            return SUPERSEDES
        return SUPERSESSION_AMBIGUOUS
    if backward:
        return SUPERSEDED_BY
    if forward:
        return SUPERSEDES
    return SUPERSESSION_AMBIGUOUS


def supersession_declarations(source, own: str | None = None) -> list[dict]:
    """Every supersession this artefact declares: `[{label, direction, ids, partial, value}]`.

    `ids` are normalised (`CR-0132` and `CR0132` are one id) and never include the artefact's own
    id or a decision row. A declaration naming no id is still RETURNED, with an empty `ids` - a
    dated `> **Superseded 2026-06-22:** accepted by operator override` is a record of the event,
    and dropping it would report the artefact as declaring nothing at all.
    """
    text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
    mine = norm_id(own) if own else None
    out: list[dict] = []
    for label, value in SUPERSESSION_FIELD_RE.findall(text):
        label, value = label.strip(), value.strip()
        # A PARENTHETICAL is an annotation, not a counterpart. `decomposed_ids` strips them for
        # exactly this reason, twenty lines below, and this reader did not - so
        # a field like `> **Superseded-by:** X (shipped via Y; residual folded into X)` read Y as a
        # second superseder and manufactured a pair that never existed. It reached the waiver set
        # with a reason asserting something untrue about an artefact that superseded nothing, and
        # the entry could only ever have been cleared by writing a false declaration.
        #
        # Markdown links are kept: a linked id is how a corpus writes a followable reference, so
        # the URL is dropped and the link TEXT retained rather than the whole run.
        scannable = _MD_LINK_RE.sub(r"\1", f"{label} {value}")
        scannable = _PAREN_RUN_RE.sub(" ", scannable)
        ids: list[str] = []
        for m in ID_SEARCH_RE.finditer(scannable):
            rec = norm_id(m.group(0))
            if rec != mine and rec not in ids:
                ids.append(rec)
        # An UNFILLED field declares nothing; a filled one whose prose sits inside the bold run
        # declares plenty. Both have an empty value, so the label decides: a bare field name ends
        # in `:`, whereas `> **Superseded by the sdlc-studio.com website.**` is the whole sentence.
        if not ids and label.endswith(":") and value.lower() in SUPERSESSION_EMPTY:
            continue
        out.append({"label": label, "value": value, "ids": ids,
                    "direction": supersession_direction(label, value),
                    "partial": "part" in label.lower()})
    return out


_PAREN_RUN_RE = re.compile(r"\([^)]*\)")


def decomposed_ids(text: str) -> list[str]:
    """The DIRECT child ids a request lists in `Decomposed-into:`, in order, de-duplicated. []
    when the field is absent or names none.

    A parenthetical is an ANNOTATION, not a child: `Decomposed-into: EP0033 (US0120, US0121)`
    means the request produced the epic EP0033, and the parenthetical merely shows what that epic
    in turn holds - those stories are the EPIC's children (they carry `Epic:`, not `Parent:` this
    request), never the request's. So parenthetical runs are stripped before ids are read; without
    that, the down-link back-check would demand a grandchild name the request as its Parent and
    falsely report `link-asymmetry` on a correctly-linked chain. The downward link reconcile
    verifies against each direct child's upward `Parent:`."""
    raw = extract_field(text, DECOMPOSED_FIELD)
    if not raw:
        return []
    raw = _PAREN_RUN_RE.sub(" ", raw)
    out: list[str] = []
    seen: set[str] = set()
    for m in ID_SEARCH_RE.finditer(raw):
        key = norm_id(m.group(0))
        if key not in seen:
            seen.add(key)
            out.append(m.group(0))
    return out


def insert_after_status(path, line: str) -> None:
    """Insert a `> **Field:** value` metadata line immediately after the `> **Status:**` line -
    the one field every artefact carries, so the insertion point is universal. Raises if the file
    has no Status line: writing nothing there would leave a ONE-SIDED link (a link the two-backlog
    gates would then flag as asymmetry), so a missing Status is a loud failure, never a silent
    no-op. The shared link-writer both decomposition ceremonies use - `refine` (request -> epic)
    and `triage` (issue -> bugs) - so the Parent/Decomposed-into wiring is written identically by
    each, beside the link READERS (`parent_ref`, `decomposed_ids`) that verify it."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    out: list[str] = []
    done = False
    for ln in text.splitlines():
        out.append(ln)
        if not done and ln.lstrip().startswith("> **Status:**"):
            out.append(line)
            done = True
    if not done:
        raise ValueError(f"{p.name} has no `> **Status:**` line to anchor the link after")
    atomic_write(p, "\n".join(out) + ("\n" if text.endswith("\n") else ""))


_DECOMPOSED_LINE_RE = re.compile(r"(?m)^(>?\s*\*\*Decomposed-into:\*\*)\s*.*$")


def write_decomposed(path, ids: list[str]) -> None:
    """Set a discovery item's `Decomposed-into:` to `ids` - de-duplicated (by normalised id) and
    order-preserving, so an incremental `add` APPENDS a new child without ever losing or
    duplicating an earlier one. Updates the existing line in place when there is one (the `add`
    path), else inserts one after `Status:` (the first decomposition). The append-only guarantee
    the incremental slices depend on; shared by `refine` and `triage`."""
    seen: set[str] = set()
    ordered: list[str] = []
    for i in ids:
        k = norm_id(i)
        if k and k not in seen:
            seen.add(k)
            ordered.append(i)
    line = f"> **{DECOMPOSED_FIELD}:** {', '.join(ordered)}"
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    if _DECOMPOSED_LINE_RE.search(text):
        new = _DECOMPOSED_LINE_RE.sub(lambda m: line, text, count=1)
        atomic_write(p, new)
    else:
        insert_after_status(p, line)


def children_of(repo_root, parent_id: str) -> list[tuple[str, str]]:
    """Every artefact that names `parent_id` as its parent (via `Parent:` or a story's `Epic:`),
    as `[(child_id, child_type)]` in type/id order. The census-based primitive the derived-status
    gate (a request is terminal only when its children are), the two-backlog status view, and the
    UNDECOMPOSED drift check all share - so "what did this request produce" has ONE answer."""
    root = Path(repo_root)
    target = norm_id(parent_id)
    if _CORPUS_CACHE is not None:
        # Inside a sweep this is asked once per request - 72 times over this workspace, each
        # re-deriving every child's parent links from scratch. The index is the same derivation
        # done once; membership in it is the same test the linear scan makes.
        return list(_child_index(root).get(target, ()))
    out: list[tuple[str, str]] = []
    for type_ in ARTIFACT_TYPES:
        for p in artifact_files(type_, root):
            cid = extract_record_id(p.stem)
            if not cid:
                continue
            if target in _parents_of(read_text_safe(p)):
                out.append((cid, type_))
    return out


def _parents_of(text: str) -> set:
    """Every parent id a child declares, normalised.

    ALL of them: each `Parent:` line (a shared batch epic carries one per request it delivers),
    plus the most-specific single link (a story's `Epic:`, or the legacy `Change Request:`) via
    `child_parent` - so a multi-parent epic and a story both resolve here. One definition,
    shared by the linear scan and the index, so the memo cannot answer a different question
    from the walk it replaces."""
    parents = {norm_id(x) for x in parent_refs(text)}
    cp = child_parent(text)
    if cp:
        parents.add(norm_id(cp))
    return parents


def _child_index(root: Path) -> dict:
    """parent id -> [(child_id, child_type)] in type/id order, built once per corpus cache."""
    key = ("children", os.path.abspath(root))
    index = _CORPUS_CACHE.get(key)
    if index is None:
        index = _CORPUS_CACHE[key] = {}
        for type_ in ARTIFACT_TYPES:
            for p in artifact_files(type_, root):
                cid = extract_record_id(p.stem)
                if not cid:
                    continue
                for parent in _parents_of(read_text_safe(p)):
                    index.setdefault(parent, []).append((cid, type_))
    return index


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


# --- DoR/DoD check-id registry -------------------------------------------------------
# The ONE authority for the machine-checkable vocabulary a project's
# definition-of-ready.md / definition-of-done.md may tag a criterion with
# (`[check: <id>]`). Each id names an EXISTING gate, so a tagged criterion is a
# criterion something actually enforces; an unknown id is a loud validation error,
# never silently unenforced. Untagged criteria are explicitly human-judged.
DOR_DOD_CHECK_IDS = {
    "grooming.affects": "Affects declared and resolvable (the sprint plan breakdown gate)",
    "grooming.points": "Points declared on the modified Fibonacci scale (breakdown gate)",
    "grooming.split": "at or under the split ceiling - above it, decompose (breakdown gate)",
    "grooming.acs": "at least one checkable acceptance criterion (tranche audit weak-AC lens)",
    "grooming.deps": "dependencies delivered or sequenced in-batch (tranche audit unmet-deps)",
    "story.verify-ac": "the story's executable ACs pass (verify_ac; the transition -> Done gate)",
    "review.critic-approve": "an independent critic APPROVE is recorded (conformance critiqued)",
    "review.two-role": "adversarial evidence + reviewer-of-record sign-off (review.two_role_after)",
    "close.review-coverage": "every unit in the batch is covered by an independent review "
                             "(sprint close's first chain step - asserted, never performed there)",
    "close.retro": "the batch retro exists and validates (gate --require-retro)",
    "close.lessons": "open lessons revalidated and the summary current (the gate's lessons lanes)",
    "close.review": "reviews/LATEST.md at least as new as every artefact (gate --require-review)",
    "close.reconcile": "no index drift (the gate's reconcile lane)",
    "release.gate": "the full release gate is green (gate --release)",
    "release.changelog": "changelog fragments composed, no strays (the release gate's lane)",
    "release.version": "version strings consistent across the authoritative files",
}
CHECK_TAG_RE = re.compile(r"\[check:\s*([a-z0-9.-]+)\s*\]")
# A bracketed token shaped like a check tag (the word `check` on a word boundary, any case)
# that the strict parser above does NOT accept - a mis-cased or mis-spaced near-miss.
_CHECK_NEAR_MISS_RE = re.compile(r"\[\s*check\b[^\]]*\]", re.IGNORECASE)
# A near-miss must ALSO carry a tag SHAPE - a colon, or an id-shaped dotted/hyphenated token
# (e.g. `grooming.affects`). Bracketed prose that merely starts with "check" (`[check the logs]`)
# is not a mis-written tag and must not flag.
_CHECK_TAG_SHAPE_RE = re.compile(r":|[a-z0-9]+[.-][a-z0-9]+", re.IGNORECASE)


def check_tags(text: str) -> list[str]:
    """Every `[check: <id>]` tag in a document, in order."""
    return CHECK_TAG_RE.findall(text or "")


def check_tag_near_misses(text: str) -> list[str]:
    """Bracketed tokens shaped like a check tag (the word `check`, any case) that the strict
    `CHECK_TAG_RE` does NOT accept - a mis-cased or mis-spaced tag that would otherwise parse as
    no-tag and silently leave its criterion unenforced. Returned verbatim, in order, for a loud
    error. A token the strict parser already accepts is not a near-miss."""
    out: list[str] = []
    for m in _CHECK_NEAR_MISS_RE.finditer(text or ""):
        token = m.group(0)
        if CHECK_TAG_RE.fullmatch(token):
            continue
        if not _CHECK_TAG_SHAPE_RE.search(token):
            continue  # bracketed prose, not a mis-written tag
        out.append(token)
    return out


def unknown_check_ids(text: str) -> list[str]:
    """The tags that resolve to NO registered check - each is human intent that
    nothing would enforce, so validation must fail loud on any."""
    return [t for t in check_tags(text) if t not in DOR_DOD_CHECK_IDS]


def dor_dod_level_checks(repo_root, kind: str, level: str) -> set[str] | None:
    """The tagged check ids at one level of the project's DoR/DoD document, or None
    for shipped-default behaviour (no document, no such level section, or a level
    heading with no body - only an explicit level WITH criteria redefines its bar).
    `kind` is "ready" or "done"; `level` is "story", "sprint" or "release". A level
    whose criteria carry no tags resolves to an empty set: the project downgraded
    every criterion there to human judgement - the gates report that downgrade
    visibly, never act on it silently. The heading match is word-exact ("## Story"
    or "## Story ..." as separate words), so an unrelated heading sharing the
    prefix cannot redefine a level."""
    path = Path(repo_root) / "sdlc-studio" / f"definition-of-{kind}.md"
    if not path.is_file():
        return None
    text = read_text_safe(path)
    if text is None:
        return None
    head_re = re.compile(rf"^{re.escape(level)}(?:\s|$)", re.IGNORECASE)
    section: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = bool(head_re.match(line[3:].strip()))
            continue
        if inside:
            section.append(line)
    return set(check_tags("\n".join(section))) if section else None


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
        "use a bare integer (103) or a prefixed id")


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


def loaded_skill_dir() -> Path:
    """The skill directory THIS process is running from.

    `sdlc_md.py` lives at `<skill>/scripts/lib/`, so the skill root is two parents up. Derived
    rather than assumed, because the skill is loaded from an INSTALLED copy in every consuming
    project and from the repo tree only here - and a path that resolves only under the second
    is a path that resolves nowhere for the projects the skill ships to.
    """
    return Path(__file__).resolve().parent.parent.parent


def resolve_affects(root, p: str):
    """Resolve an Affects path against the repo root, a vendored skill dir, or the LOADED one.

    The third base is the one the docstring already promised and the code did not have. A
    shipped-payload path such as `.claude/skills/sdlc-studio/templates/audit-profiles/x.md`
    resolved only in a project that VENDORS the skill into its own tree; everywhere else - which
    is every consuming project - it silently resolved to nothing, and an Affects that resolves
    to nothing is read as an ungroomed unit.

    Returns the resolved Path, or None for a not-yet-existing (greenfield) path.
    """
    root = Path(root)
    skill = loaded_skill_dir()
    bases = [root, root / ".claude" / "skills" / "sdlc-studio", skill]
    # A path already written relative to the skill root resolves against it directly; one
    # written repo-relative needs its `.claude/skills/sdlc-studio/` prefix stripped first, which
    # is the spelling the corpus overwhelmingly uses.
    #
    # The stripped candidate is SKILL-RELATIVE and is offered to the skill bases only. Offering
    # it to the project root as well let a consuming project holding its own
    # `templates/core/story.md` win the resolution of
    # `.claude/skills/sdlc-studio/templates/core/story.md` - the loop nested base outside
    # candidate, so the stripped form was tried at the root before either skill base was tried
    # at all. This repo cannot see it, because the vendored copy wins either way, which is what
    # made it a defect that reaches consumers first.
    prefix = ".claude/skills/sdlc-studio/"
    stripped = p[len(prefix):] if p.startswith(prefix) else None
    for base in bases:
        candidates = [p] if base == root else [p, *([stripped] if stripped else [])]
        for cand_rel in candidates:
            cand = base / cand_rel
            if cand.exists():
                return cand
    return None


_AC_CHECKBOX_RE = re.compile(r"^\s*- \[[ xX]\] ")


def criteria_section(text: str) -> str:
    """Just the `## Acceptance Criteria` section, or "" when there is none.

    Shared, because a gate that asks a question ABOUT the criteria must not be answerable by
    anything outside them. Scanning the whole artefact let a `- [x]` in Steps to Reproduce, and
    a `Verify:` line in Proposed Fix, satisfy an oracle gate whose own refusal says "every
    acceptance criterion is unticked".
    """
    out, in_ac = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if in_ac:
            out.append(line)
    return "\n".join(out)


def count_acs(text: str) -> int:
    """Checkable AC items inside the Acceptance Criteria section (checkbox lines,
    `### ACn` headings, or `**ACn**` bullets). The same recognition set readiness.py's
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


def split_id_list(value) -> list[str]:
    """One id list from a repeatable flag, a comma list, or both - the HOUSE grammar.

    Extracted so a verb taking two id lists (`--out` / `--in`) reads them the same way
    `resolve_ids` reads one. A second splitter would be a second grammar, and the conformance
    sweep exists because those drift.
    """
    values = value if isinstance(value, list) else ([value] if value else [])
    out: list[str] = []
    for item in values:
        for token in str(item).replace(",", " ").split():
            token = token.strip()
            if token and token not in out:
                out.append(token)
    return out


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
