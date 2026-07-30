#!/usr/bin/env python3
"""SDLC Studio tranche audit - sprint pre-flight readiness.

Runs between `sprint plan` and the triage STOP, so the operator approves a
clean, verifiable batch. Per unit it flags, deterministically:

- **weak-AC**       - no checkable AC, or the tautology placeholder (the
                      vacuous-pass class the downstream verify/conformance miss),
- **unmet-deps**    - a `Depends on` referent that is not yet delivered. Referents resolve
                      in-repo first, then across the sibling repos a PVD product manifest
                      names, so a cross-repo dependency delivered elsewhere counts as met,
- **unresolved-deps** - a referent the audit could not check at all because the manifest's
                      sibling checkout is not on disk (named, never silently passed),
- **already-terminal** - already Complete/Superseded/Done (close, do not re-work),
- **missing-regression-test** - a Fixed/Done bug whose recorded tests carry no
                      integration/regression-level case (name-signal only; the seam
                      judgement stays with review - see best-practices/testing.md),
- **link-integrity** - reuses `integrity.py`'s error findings for the unit.

Emits a JSON readiness report; exits non-zero when any unit is not ready, and equally
when a check could not be computed at all (reported under `uncomputed`, never as a pass). The
adversarial "is the problem still real" lens stays model-instructed (delegates to
the adversarial audit when built). Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import conventions, sdlc_md, xrepo  # noqa: E402  (xrepo: cross-repo id resolution)
import integrity  # noqa: E402  (sibling script; scripts dir is on sys.path)
import sprint  # noqa: E402
import verify_ac  # noqa: E402  (reuse the Verify-line lint)
import ac_scope  # noqa: E402  (reuse the cross-epic AC check)

TAUTOLOGY = "lint and tests green"
# An unexpanded `{{...}}` span from the scaffolding template. A unit carrying one
# has AC-shaped markup but no authored criterion, so an item count alone reads it
# as groomed - and `verify_ac` would then run `{{executable check}}` as its oracle.
_PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
# A dependency counts as met once it has been delivered (or replaced).
MET = {"Done", "Complete", "Verified", "Fixed", "Accepted", "Superseded", "Closed"}
# Terminal-but-not-delivered: the dependency is dead, surfaced distinctly.
DEAD = {"Rejected", "Withdrawn", "Won't Implement", "Won't Fix", "Deferred"}
_AC_CHECKBOX = re.compile(r"^\s*- \[[ xX]\] ")

# Every readiness issue kind audit_unit can put in a unit's `issues`, whose prefix
# (before any `: detail` suffix) is fed to sdlc_md.remediation_lines("audit", ...) by
# cmd_check. This is audit's finding-kind vocabulary and the single source of truth for
# it: the remediation registry (sdlc_md.REMEDIATION["audit"]) must carry a hint for each,
# a guard derives its expected key set from this tuple (so a new issue kind without a hint
# reddens the guard), and a sibling test asserts this tuple matches the kinds actually
# appended in source (so the tuple itself cannot silently drift). Informational `info`
# notes (e.g. sequenced-in-batch) never block readiness and are not remediation kinds.
# Keep this in step with the issue literals in audit_unit below.
FINDING_KINDS = (
    "not-found",
    "weak-AC",
    "weak-verify",
    "underspecified",
    "missing-regression-test",
    "cross-epic-ac",
    "unmet-deps",
    "unresolved-deps",
    "already-terminal",
    "link-integrity",
    "already-satisfied",
)


# --------------------------------------------------------------------------
# Lens profiles
# --------------------------------------------------------------------------
# A profile is a declarative lens pack: a name, an adversarial question and what the
# lens hunts, one row per lens. Packs ship under templates/audit-profiles/; the default
# project profile is declared in the reference instead, so both are resolved here and a
# name no profile declares is refused rather than silently running zero lenses.
SKILL_DIR = Path(__file__).resolve().parent.parent
PROFILE_DIR = SKILL_DIR / "templates" / "audit-profiles"
#: Profiles declared in a reference section rather than as a pack file, mapped to the
#: file and the heading anchor whose section holds the lens table.
REFERENCE_PROFILES = {"project": ("reference-audit.md", "audit-project-profile")}
_REFUTE_RE = re.compile(r"\*\*Refute panel:\*\*(.*)", re.I)
_THRESHOLD_RE = re.compile(r">=\s*(\d+)\s*of\s*(\d+)")
_TABLE_DIVIDER_RE = re.compile(r"^\|[\s:|-]+\|$")

#: Leading tokens a mechanical lens `signature` may open with - a detector a finder can
#: actually run. A signature that opens with anything else is not mechanical, and the
#: absent form opens with `manual` (below), which is deliberately not in this set.
#:
#: THE SINGLE AUTHORITY for what counts as a runner. `process.md`'s Signatures section states
#: the documented set in prose, and that sentence is DERIVED from this tuple rather than typed
#: beside it - a hand-kept second copy is the `count-by-hand` lens in that very pack pointed
#: at this constant.
SIGNATURE_DETECTORS = ("bash", "npm", "python3", "rg")
#: `npm` alone runs nothing; only `npm run <script>` does. Kept as a rule rather than folded
#: into the tuple so a bare `npm` cannot pass as mechanical.
NPM_RUN = ("npm", "run")
#: The fixed leading token of a signature that declares no mechanical detector exists.
#: A `signature` field parses as `mechanical=False` unless its first token is a detector,
#: so a blank cell, a dash or a hedged sentence is not-mechanical too - but only this token
#: is the *documented* way to say so, which the pack's own test holds it to.
SIGNATURE_ABSENT = "manual"


class UnknownProfile(ValueError):
    """A profile name no pack and no reference section declares."""


def profile_names(skill_dir: Path | None = None) -> list[str]:
    """Every profile that can be resolved, sorted. Packs on disk plus the
    reference-declared defaults."""
    # PROFILE_DIR is the one answer to "where do the packs live". This used to recompute
    # the same path inline, leaving the constant defined and unused - dead, and therefore
    # unpinnable by any test.
    d = (skill_dir / "templates" / "audit-profiles") if skill_dir else PROFILE_DIR
    packs = {p.stem for p in d.glob("*.md")} if d.is_dir() else set()
    return sorted(packs | set(REFERENCE_PROFILES))


#: A cell delimiter is a pipe that is NOT escaped. `\|` is markdown's literal pipe.
_CELL_SPLIT_RE = re.compile(r"(?<!\\)\|")


def _split_row(line: str) -> list[str]:
    """A table row's cells, honouring markdown's `\\|` escape for a literal pipe.

    Splitting on every `|` tore a cell in half whenever its content needed one - an `rg`
    signature with an alternation (`(secret|password)`) became the fragment `rg -ni "(secret`,
    which then failed validation for "naming no target". The pattern was fine; the parser was
    eating it. Escaped pipes are unescaped after the split, as a markdown reader does.
    """
    cells = _CELL_SPLIT_RE.split(line.strip().strip("|"))
    return [c.strip().replace("\\|", "|") for c in cells]


def _signature_tokens(signature: str) -> list[str]:
    """`signature` split as a shell would split it, so a QUOTED pattern stays one token.

    `str.split()` was wrong for `rg 'two words' path`: it yields `two` and `words'` as
    separate tokens, and the path is then not the last one. Falls back to a plain split
    on an unbalanced quote rather than raising - a malformed cell is a finding for the
    validator to report, not a crash in the parser.
    """
    try:
        return shlex.split(signature)
    except ValueError:
        return signature.split()


def _signature_is_mechanical(signature: str) -> bool:
    """True when `signature`'s leading token is a documented detector a finder can run.

    This is the single rule the parser uses to mark a lens `mechanical`. The absent form
    (`manual - ...`) opens with `manual`, which is not a detector, so it parses as
    not-mechanical; so does a blank cell, a bare dash or a hedged sentence. A pack that
    wants the absence *declared* rather than merely detected holds itself to the `manual`
    form in its own test - the parser only distinguishes a runnable detector from
    everything else.

    MUTANTS THIS MUST DIE TO. (1) `tokens[0] in SIGNATURE_DETECTORS` widened to
    `any(t in SIGNATURE_DETECTORS for t in tokens)` - caught only by a `manual - ...` reason
    that MENTIONS a detector token mid-sentence, so the negative fixture must contain one.
    (2) Dropping the `npm run` rule so a bare `npm` passes. (3) Deleting any single runner
    from the tuple - caught only by one assertion per runner, never by `all(mechanical)`
    over the packs.
    """
    tokens = _signature_tokens(signature)
    if not tokens or tokens[0] not in SIGNATURE_DETECTORS:
        return False
    if tokens[0] == NPM_RUN[0]:
        return tokens[1:2] == [NPM_RUN[1]]
    return True


def _header_index(columns: list[str]) -> dict[str, int]:
    """`{header_lower: index}` for a lens table's header row.

    Built from the HEADER row, never from the divider row: a divider is all dashes and colons,
    so a map built from it is empty and every by-name read silently returns the empty string -
    a mutant that leaves the packs parsing exactly as the positional read did.
    """
    return {c.strip().lower(): i for i, c in enumerate(columns) if c.strip()}


def _cell(cells: list[str], index: int | None) -> str:
    """`cells[index]`, or "" when the column is absent or the row is short."""
    if index is None or index >= len(cells):
        return ""
    return cells[index]


#: The shortest reason that counts as stating why no search singles a class out. A bare
#: `manual`, a dash, or `manual -` is a cell that looks decided and says nothing.
MIN_ABSENT_REASON = 20

#: The shortest reason that counts once padding is discounted. A length floor alone accepted
#: `manual - xxxxxxxxxxxxxxxxxxxx`: twenty characters that state nothing. A reason has to carry
#: DISTINCT words, so the floor is applied to the wording as well as the length.
MIN_ABSENT_REASON_WORDS = 5

#: Placeholders that are not a reason however long the cell is.
_REASON_PLACEHOLDER = re.compile(r"\b(tbd|todo|fixme|xxx+|fill this in|later)\b", re.I)

#: The installed skill's own prefix. A shipped pack names its detectors relative to the SKILL,
#: because the skill is what travels: a consuming project may have it at `.claude/skills/...`
#: inside the project or at `~/.claude/skills/...` outside it, and a repo-root-relative resolve
#: finds it in neither case reliably.
SKILL_PATH_PREFIX = ".claude/skills/sdlc-studio/"

#: Shell metacharacters that make a "path" not a path. `python3 x.py | head` resolves its first
#: token and silently ignores a pipeline the finder would actually run.
_SHELL_META = set("|&;><$`")

#: Runners that need a FILE. A search takes a directory tree quite legitimately, so the
#: directory refusal is scoped to the interpreters rather than applied to every mechanical
#: signature - `rg tools` is correct and `python3 tools` runs nothing.
_FILE_RUNNERS = ("bash", "python3")


def _resolve_signature_path(value: str, repo_root: Path | str) -> Path | None:
    """Where `value` actually lives, or None when it is not a resolvable relative path.

    A skill-prefixed path resolves against the INSTALLED SKILL rather than the audited root, so
    a shipped pack's detector is found wherever the skill is installed. Everything else is
    relative to the root being audited, which is what a project's own appended row names.
    """
    if value.startswith(SKILL_PATH_PREFIX):
        return SKILL_DIR / value[len(SKILL_PATH_PREFIX):]
    return Path(repo_root) / value


def _path_shape_error(value: str) -> str | None:
    """Why `value` cannot be a runnable path at all, or None when its shape is fine.

    An existence check alone accepted an absolute path (`Path(root) / "/etc/passwd"` discards the
    root, so a machine-local path validated here and nowhere else - precisely the written-from-
    memory class), a `..` escape, a directory where a script is implied, and a shell pipeline
    whose later stages nothing checked.
    """
    if Path(value).is_absolute():
        return (f"{value!r} is an absolute path - it resolves on the machine that wrote it and "
                f"nowhere else, which is the detector-from-memory case this check exists for")
    if ".." in Path(value).parts:
        return f"{value!r} escapes the root with `..`"
    if set(value) & _SHELL_META:
        return (f"{value!r} carries a shell metacharacter, so the command a finder runs is not "
                f"the single path this check resolved")
    return None


def signature_target(signature: str) -> tuple[str, str] | None:
    """What a mechanical signature's runner actually invokes, as `(kind, value)`.

    `kind` is `"path"` for `python3`/`bash`/`rg` and `"npm-script"` for `npm run <script>`.
    None when the signature is not mechanical.

    The shapes differ and one rule cannot serve them. `python3 <path>` and `bash <path>` name
    the path FIRST. `rg <pattern> [path...]` names it LAST, after a pattern that may be quoted -
    and the path is optional and repeatable, so "the path" cannot be recovered from an arbitrary
    `rg` line at all. The contract this enforces instead is that a shipped `rg` signature must
    END with the path it searches; one that names none yields `""` and the validator refuses it,
    so "mechanical but unresolvable" cannot be authored rather than being reported later.

    MUTANTS THIS MUST DIE TO. (1) Returning the first token after the runner unconditionally, so
    `npm run lint:links` yields `run` and `rg pat path` yields `pat` - caught only by asserting
    the extracted VALUE, never by asserting that a resolution check merely passed.
    (2) Dropping the `rest[-1]` rule for `rg` back to `rest[0]`.
    """
    if not _signature_is_mechanical(signature):
        return None
    tokens = _signature_tokens(signature)
    runner = tokens[0]
    if runner == NPM_RUN[0]:
        return "npm-script", tokens[2] if len(tokens) > 2 else ""
    rest = [t for t in tokens[1:] if not t.startswith("-")]
    if runner == "rg":
        # Pattern first, path last. With only one token there is a pattern and no path.
        return "path", rest[-1] if len(rest) > 1 else ""
    return "path", rest[0] if rest else ""


def _npm_scripts(repo_root: Path | str) -> dict:
    """`package.json`'s `scripts` object, or empty when absent or unreadable.

    Read from `scripts` SPECIFICALLY, never from the top level: a mutant that looks the key up
    across the whole document passes on any colliding top-level key (`name`, `version`), which
    proves nothing about whether `npm run <key>` works.
    """
    p = Path(repo_root) / "package.json"
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}
    scripts = data.get("scripts") if isinstance(data, dict) else None
    return scripts if isinstance(scripts, dict) else {}


def _absent_reason(signature: str) -> str:
    """The stated reason after a leading `manual`, with the separator stripped."""
    rest = signature.strip()[len(SIGNATURE_ABSENT):].strip()
    return rest.lstrip("-:– ").strip()


def signature_errors(lens: dict, repo_root: Path | str) -> list[str]:
    """Every way one lens's signature breaks the pack contract, as human-readable errors.

    SHIPPED CODE ON PURPOSE, not a repo unit test. `process.md`'s own Notes and
    `reference-audit.md#audit-extend` invite a consuming project to append pack rows "stating
    its own signature in the same way", and a consuming project never runs this repository's
    tests. A contract enforced only in `test_audit_profiles.py` is enforced nowhere for the
    people it is documented for.
    """
    name = lens.get("name") or "?"
    sig = (lens.get("signature") or "").strip()
    if not sig:
        return [f"{name}: carries no signature - a blank cell cannot read as a considered "
                f"declaration that no detector exists"]
    # `mechanical` is RE-DERIVED, never trusted. It is a parsed field, and a caller that hands in
    # a stale or hand-built lens dict used to reach `kind, value = signature_target(...)` with
    # None and raise TypeError out of the public helper a consuming project is told to use.
    mechanical = _signature_is_mechanical(sig)
    if not mechanical:
        tokens = _signature_tokens(sig)
        if not tokens or tokens[0] != SIGNATURE_ABSENT:
            return [f"{name}: signature {sig!r} opens with neither a documented runner "
                    f"({', '.join(SIGNATURE_DETECTORS)}) nor {SIGNATURE_ABSENT!r}"]
        reason = _absent_reason(sig)
        if len(reason) < MIN_ABSENT_REASON:
            return [f"{name}: declares {SIGNATURE_ABSENT!r} without stating why no search "
                    f"singles the class out"]
        # A LENGTH floor alone accepted `manual - xxxxxxxxxxxxxxxxxxxx`: twenty characters that
        # say nothing. A reason states something, so it needs distinct words, not just bytes.
        words = {w for w in re.findall(r"[a-z]{2,}", reason.lower())}
        if len(words) < MIN_ABSENT_REASON_WORDS:
            return [f"{name}: declares {SIGNATURE_ABSENT!r} with {len(words)} distinct word(s) - "
                    f"long enough to clear the length floor while stating nothing"]
        if _REASON_PLACEHOLDER.search(reason):
            return [f"{name}: the stated reason is a placeholder, not a reason"]
        return []
    # Checked on the TOKENS, not the raw string: `|` inside a quoted `rg` pattern is part of the
    # pattern, while a bare `|` token is a pipeline whose later stages nothing here resolves.
    # Scanning the raw string would have banned every alternation an `rg` detector needs.
    shell_tokens = [t for t in _signature_tokens(sig) if t and set(t) <= _SHELL_META]
    if shell_tokens:
        return [f"{name}: signature {sig!r} chains on {shell_tokens[0]!r}, so what a finder runs "
                f"is a shell construct and not the single target this check can resolve"]
    kind, value = signature_target(sig)
    if not value:
        return [f"{name}: signature {sig!r} names a runner but no target - an `rg` signature "
                f"must end with the path it searches, so an unresolvable detector cannot ship"]
    if kind == "npm-script":
        if value not in _npm_scripts(repo_root):
            return [f"{name}: `npm run {value}` names no key in package.json's `scripts`, so "
                    f"the command a finder would type does not run"]
        return []
    shape = _path_shape_error(value)
    if shape:
        return [f"{name}: {shape}"]
    resolved = _resolve_signature_path(value, repo_root)
    if resolved is None or not resolved.exists():
        return [f"{name}: signature names {value!r}, which is not on disk - a detector written "
                f"from memory, caught here rather than by the finder who runs it and gets "
                f"nothing"]
    # A DIRECTORY is the right target for a search and the wrong one for an interpreter. `rg tools`
    # searches a tree; `python3 tools` runs nothing, yet a bare existence check accepts both.
    runner = _signature_tokens(sig)[0]
    if resolved.is_dir() and runner in _FILE_RUNNERS:
        return [f"{name}: signature names {value!r}, which is a DIRECTORY - `{runner}` needs a "
                f"file to run, and a directory silently satisfies an existence check"]
    return []


def profile_signature_errors(profile: dict, repo_root: Path | str) -> list[str]:
    """Every signature error across one resolved profile's lenses, prefixed with its name."""
    return [f"{profile['name']}: {err}"
            for lens in profile.get("lenses", [])
            for err in signature_errors(lens, repo_root)]


def _parse_lens_table(lines: list[str]) -> tuple[list[str], list[dict]]:
    """(column headers, lens rows) for the first markdown table in `lines`.

    A lens row is `{name, question, hunts, drawn_from, signature, mechanical}`. Every cell
    after the first is filled when the row has it and left empty otherwise, never dropped: a
    two-column table (the project profile's artifact/lens shape) yields an empty `hunts`, and
    a pack with no provenance column an empty `drawn_from`. `drawn_from` carries the recorded
    failure modes a lens was drawn from, as lesson ids, for the packs that cite them.
    `signature` carries the mechanical detector that finds the lens or a declared absence; it
    is surfaced as its own field so a lens shipped with the column blank is a parse a test can
    see rather than a cell dropped on the floor, and `mechanical` records whether that
    signature names a detector a finder can run. Nothing here judges a row's content; a pack
    that must declare more is held to it by its own test.

    `drawn_from` and `signature` are resolved BY HEADER NAME, never by position. The packs ship
    at three, four and five columns, and the old `cells[4]` read put a four-column pack's
    Signature into `drawn_from` and left `signature` empty - which parses as not-mechanical, so
    a real detector read as an absent one. Position works only while every pack happens to agree
    on a column order, and `reference-audit.md#audit-extend` invites consuming projects to
    append rows of their own.
    """
    columns: list[str] = []
    lenses: list[dict] = []
    header: list[str] | None = None
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if header is not None and columns:
                break  # the table ended; ignore any later table in the file
            continue
        cells = _split_row(stripped)
        if header is None:
            header = cells
            continue
        if _TABLE_DIVIDER_RE.match(stripped):
            columns = header
            continue
        if not columns:  # a table without a divider row is not a lens table
            continue
        by_name = _header_index(columns)
        signature = _cell(cells, by_name.get("signature"))
        lenses.append({"name": cells[0],
                       "question": cells[1] if len(cells) > 1 else "",
                       "hunts": cells[2] if len(cells) > 2 else "",
                       "drawn_from": _cell(cells, by_name.get("drawn from")),
                       "signature": signature,
                       "mechanical": _signature_is_mechanical(signature)})
    return columns, lenses


def _refute_declaration(text: str) -> str:
    """The whole `**Refute panel:**` blockquote, joined. Taken as a block rather than a
    single line so a declaration wrapped across lines is read in full."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if _REFUTE_RE.search(line):
            block = [line]
            for nxt in lines[i + 1:]:
                if not nxt.lstrip().startswith(">"):
                    break
                block.append(nxt)
            joined = " ".join(part.lstrip().lstrip(">").strip() for part in block)
            return _REFUTE_RE.search(joined).group(1).strip()
    return ""


def _parse_threshold(text: str) -> dict | None:
    """The refute threshold a `**Refute panel:**` declaration states, as
    `{survive, votes}`. None when the declaration is absent or states no threshold."""
    m = _THRESHOLD_RE.search(_refute_declaration(text))
    if not m:
        return None
    return {"survive": int(m.group(1)), "votes": int(m.group(2))}


def parse_pack(path: Path | str) -> dict:
    """Parse a lens pack file into `{columns, lenses, refute, threshold}`."""
    text = Path(path).read_text(encoding="utf-8")
    columns, lenses = _parse_lens_table(text.splitlines())
    return {"columns": columns, "lenses": lenses,
            "refute": _refute_declaration(text),
            "threshold": _parse_threshold(text)}


def _reference_section(skill_dir: Path, filename: str, anchor: str) -> str:
    """The body of the heading whose anchor is `{#anchor}`, up to the next heading of
    the same or a higher level."""
    text = (skill_dir / filename).read_text(encoding="utf-8")
    lines = text.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        if line.startswith("#") and f"{{#{anchor}}}" in line:
            start = i + 1
            level = len(line) - len(line.lstrip("#"))
            break
    if start is None:
        return ""
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("#"):
            if len(line) - len(line.lstrip("#")) <= level:
                break
        out.append(line)
    return "\n".join(out)


def resolve_profile(name: str, skill_dir: Path | None = None) -> dict:
    """Resolve a profile name to its lens pack.

    Returns `{name, source, lenses, refute, threshold, columns}`. Raises
    `UnknownProfile` for a name nothing declares, and for a declaration that
    carries no lens at all - an empty lens set is a broken profile, never a run.
    """
    d = skill_dir or SKILL_DIR
    known = profile_names(d)
    pack = d / "templates" / "audit-profiles" / f"{name}.md"
    if pack.is_file():
        parsed = parse_pack(pack)
        source = f"templates/audit-profiles/{name}.md"
    elif name in REFERENCE_PROFILES:
        filename, anchor = REFERENCE_PROFILES[name]
        body = _reference_section(d, filename, anchor)
        columns, lenses = _parse_lens_table(body.splitlines())
        parsed = {"columns": columns, "lenses": lenses,
                  "refute": _refute_declaration(body),
                  "threshold": _parse_threshold(body)}
        source = f"{filename}#{anchor}"
    else:
        raise UnknownProfile(
            f"unknown audit profile {name!r}; profiles that exist: {', '.join(known)}")
    if not parsed["lenses"]:
        raise UnknownProfile(f"audit profile {name!r} declares no lens ({source})")
    return {"name": name, "source": source, **parsed}


# ---------------------------------------------------------------------------
# detector-owed: a lens the model has now paid for twice wants a script
# ---------------------------------------------------------------------------

#: Exit codes. `3` for cannot-judge and NOT 2: `cmd_profile` already returns 2 for an unknown
#: profile and argparse uses 2 for a usage error, so a caller could not tell "I could not judge
#: this workspace" from "you typed the flag wrong".
OWED_CLEAN, OWED_FOUND, OWED_CANNOT_JUDGE = 0, 1, 3

#: Where findings live. Both, because a class parked in a bug is where nobody looks.
FINDING_DIRS = (("bugs", ("BG",)), ("change-requests", ("CR",)))


def _finding_attributions(repo_root: Path | str) -> tuple[list[dict], list[str]]:
    """`(attributed, unattributed_ids)` read from the findings' metadata FIELDS.

    Fields rather than `Raised-by` prose: 108 findings hide a run id in that line, and counting a
    class from free text is a regex where a field read will do.
    """
    root = Path(repo_root)
    attributed: list[dict] = []
    unattributed: list[str] = []
    for rel, prefixes in FINDING_DIRS:
        d = root / "sdlc-studio" / rel
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            if path.name == "_index.md":
                continue
            rec = sdlc_md.extract_record_id(path.stem)
            if not rec or not rec[:2] in prefixes:
                continue
            text = sdlc_md.read_text_safe(path)
            lens = (sdlc_md.extract_field(text, "Audit-lens") or "").strip()
            run = (sdlc_md.extract_field(text, "Audit-run") or "").strip()
            if lens and run:
                attributed.append({"id": rec, "lens": lens, "run": run})
            else:
                unattributed.append(rec)
    return attributed, unattributed


def _lens_signature(lens_name: str, skill_dir: Path | None = None) -> dict | None:
    """The pack row for `lens_name`, or None when no pack declares it."""
    d = skill_dir or SKILL_DIR
    for name in sorted(set(profile_names(d)) - set(REFERENCE_PROFILES)):
        try:
            profile = resolve_profile(name, d)
        except UnknownProfile:
            continue
        for lens in profile["lenses"]:
            if lens["name"] == lens_name:
                return {**lens, "profile": name}
    return None


def detector_owed(repo_root: Path | str, skill_dir: Path | None = None) -> dict:
    """Which lenses have now been paid for twice and want a deterministic detector.

    `{owed, exists, unattributed, unregistered, cannot_judge}`.

    A lens is **owed** when it appears under two or more DISTINCT REGISTERED run ids and its pack
    signature is not mechanical. Registered matters: without it a one-character typo in a run id
    manufactures a second distinct run and with it a false verdict, which is the whole reason the
    register is validated at filing time.

    A recurring lens whose signature IS mechanical is **detector-exists** - the script already
    ships and a finder should run it, so re-commissioning it would be waste.

    Volume inside ONE run is not evidence: a run finding a class five times is the lens working.
    """
    attributed, unattributed = _finding_attributions(repo_root)
    import audit_cost  # noqa: PLC0415 - local: this reads the register, it does not own it
    reg = audit_cost.register(repo_root)
    registered = reg["runs"]

    by_lens: dict[str, dict] = {}
    unregistered: list[dict] = []
    for rec in attributed:
        if rec["run"] not in registered:
            # NOT counted towards a verdict: an id the register does not hold proves nothing, and
            # counting it would be the typo-manufactured second run the register exists to stop.
            unregistered.append(rec)
            continue
        entry = by_lens.setdefault(rec["lens"], {"runs": {}, "findings": []})
        entry["runs"].setdefault(rec["run"], registered[rec["run"]])
        entry["findings"].append(rec["id"])

    owed, exists = [], []
    for lens_name, entry in sorted(by_lens.items()):
        if len(entry["runs"]) < 2:
            continue
        sig = _lens_signature(lens_name, skill_dir)
        row = {"lens": lens_name,
               "profile": (sig or {}).get("profile"),
               "runs": sorted(entry["runs"]),
               "provenance": sorted(set(entry["runs"].values())),
               "findings": sorted(entry["findings"]),
               "signature": (sig or {}).get("signature", ""),
               "rationale": (sig or {}).get("signature", "") if not (sig or {}).get("mechanical")
               else ""}
        (exists if (sig or {}).get("mechanical") else owed).append(row)

    # CANNOT-JUDGE DOMINATES. A workspace with 3 owed lenses and 40 findings it could not read is
    # not "3 owed" - the 40 would vanish behind a verdict that looks like an answer.
    # A CORRUPT register is its own cannot-judge cause, and a loud one. Every run then reads as
    # unregistered, so without this the verdict would be driven by a file nobody could parse -
    # the exact "reported clean over something that never ran" class this verb exists to refuse.
    register_unreadable = reg["state"] == "corrupt"
    cannot_judge = bool(unattributed or unregistered or register_unreadable)
    return {"owed": owed, "exists": exists,
            "unattributed": sorted(unattributed), "unregistered": unregistered,
            "register_state": reg["state"], "register_detail": reg["detail"],
            "cannot_judge": cannot_judge}


def owed_exit_code(result: dict) -> int:
    """0 clean, 1 owed, 3 cannot-judge - with cannot-judge taking precedence over owed."""
    if result["cannot_judge"]:
        return OWED_CANNOT_JUDGE
    return OWED_FOUND if result["owed"] else OWED_CLEAN


def _pack_rel_path(profile: str | None) -> str:
    """The lens pack's path as a consuming project sees it, for a filed unit's `Affects`."""
    base = ".claude/skills/sdlc-studio/templates/audit-profiles"
    return f"{base}/{profile}.md" if profile else base


def existing_detector_units(repo_root: Path | str) -> dict:
    """`{lens: id}` for every unit already filed to build a lens's detector.

    Matched on the `Detector-for-lens` FIELD, never on a title substring: a reworded title would
    otherwise re-file the same unit on the next close-out, and the wording of a title is exactly
    the thing a human edits.
    """
    root = Path(repo_root)
    out: dict = {}
    for rel, prefixes in FINDING_DIRS:
        d = root / "sdlc-studio" / rel
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            if path.name == "_index.md":
                continue
            rec = sdlc_md.extract_record_id(path.stem)
            if not rec or rec[:2] not in prefixes:
                continue
            lens = (sdlc_md.extract_field(sdlc_md.read_text_safe(path),
                                          "Detector-for-lens") or "").strip()
            if lens:
                out.setdefault(lens, rec)
    return out


def file_owed_detectors(repo_root: Path | str, result: dict, dry_run: bool = False) -> list:
    """File one sized CR per owed lens that has none, and report what already existed.

    Returns a row per owed lens: `{lens, id, created}`. NOTHING is filed for a detector-exists
    lens - that script already ships, and re-commissioning it is the waste this verb prevents.
    """
    import file_finding  # noqa: PLC0415 - local: this files through the filer, it is not one
    root = Path(repo_root)
    existing = existing_detector_units(root)
    rows = []
    for owed in result["owed"]:
        lens = owed["lens"]
        if lens in existing:
            rows.append({"lens": lens, "id": existing[lens], "created": False})
            continue
        if dry_run:
            rows.append({"lens": lens, "id": None, "created": False})
            continue
        runs = ", ".join(owed["runs"])
        findings = ", ".join(owed["findings"])
        title = f"Build the mechanical detector for the {lens} lens"
        res = file_finding.file_finding(root, "cr", title, {
            "priority": "Medium", "ctype": "Improvement", "size": "M",
            # The pack file that must gain the signature, as a path relative to the audited root.
            # `SKILL_DIR.name` alone produced `sdlc-studio/templates/...`, which resolves nowhere:
            # the skill lives under `.claude/skills/`, and a fictional footprint mis-groups the
            # unit in the planner's collision analysis while the command still exits 0.
            "affects": _pack_rel_path(owed.get("profile")),
            "detector_for_lens": lens,
            "summary": (
                f"The `{lens}` lens has now been filed under {len(owed['runs'])} separate audit "
                f"runs ({runs}) and its pack still declares no mechanical detector, so the same "
                f"judgement has been paid for twice.\n\n"
                f"The pack's own stated reason for having none: {owed['rationale'] or 'not stated'}"
                f"\n\nThe findings that prove the recurrence: {findings}. Those are the cases the "
                f"detector must catch - a detector that cannot fire on them is decoration."),
            "impact": (
                f"Every future run re-derives this judgement from scratch. Recurrence is the "
                f"evidence that it is derivable, and a script that finds the class costs nothing "
                f"per run once written."),
            "acs": [
                f"A detector for `{lens}` exists and its command is recorded as that lens's "
                f"signature, so `profile --validate` holds it to a target that resolves.",
                f"The detector fires on each finding that raised this unit ({findings}); one that "
                f"cannot is not evidence.",
                f"`detector-owed` reports `{lens}` as detector-exists rather than owed once the "
                f"signature lands, so this unit cannot be filed a second time."],
        })
        # The id is re-derived FROM THE WRITTEN PATH rather than taken from the filer's return
        # value. The filer reports a display form (`CR-0001`) while a later scan of the tree reads
        # the record id from the filename (`CR0001`), so the two paths disagreed on identity - and
        # identity is the whole basis of an idempotence check. Deriving both the same way makes
        # them agree by construction instead of by coincidence.
        rec = sdlc_md.extract_record_id(Path(res["path"]).stem) or res["id"]
        rows.append({"lens": lens, "id": rec, "created": True})
    return rows


def cmd_detector_owed(args: argparse.Namespace) -> int:
    """Report the lenses a recurring class has now paid for twice."""
    root = Path(getattr(args, "root", None) or ".")
    res = detector_owed(root)
    code = owed_exit_code(res)
    filed = None
    if getattr(args, "file", False):
        # Only when a verdict is trustworthy. Filing off a cannot-judge verdict would mint units
        # from a workspace the verb has just said it cannot read.
        if code == OWED_CANNOT_JUDGE:
            print("refusing to file: the verdict is CANNOT JUDGE, so an owed list minted from it "
                  "would rest on a workspace this verb has just said it cannot read",
                  file=sys.stderr)
            return code
        filed = file_owed_detectors(root, res, dry_run=getattr(args, "dry_run", False))
        res = {**res, "filed": filed}
    if args.format == "json":
        print(json.dumps({**res, "exit_code": code}, indent=2))
        return code
    for row in res["owed"]:
        print(f"detector-owed: {row['lens']} ({row['profile']}) - filed under "
              f"{len(row['runs'])} runs: {', '.join(row['runs'])}")
        print(f"  findings: {', '.join(row['findings'])}")
        if row["rationale"]:
            print(f"  the pack's own rationale for no detector: {row['rationale']}")
    for row in res["exists"]:
        print(f"detector-exists: {row['lens']} recurs, and its detector already ships - run and "
              f"skip on: {row['signature']}")
    if res["unattributed"]:
        print(f"CANNOT JUDGE: {len(res['unattributed'])} finding(s) carry no lens attribution, so "
              f"a class recurring among them is invisible here: "
              f"{', '.join(res['unattributed'][:8])}"
              + (" ..." if len(res["unattributed"]) > 8 else ""))
    if res.get("register_state") == "corrupt":
        print(f"CANNOT JUDGE: the audit-run register is UNREADABLE, so every citation reads as "
              f"unregistered and no verdict here rests on evidence: {res['register_detail']}")
    for rec in res["unregistered"]:
        print(f"CANNOT JUDGE: {rec['id']} cites run {rec['run']!r}, which the register does not "
              f"hold - it is not counted, because an unregistered id proves nothing")
    for row in (filed or []):
        if row["created"]:
            print(f"filed {row['id']} to build the detector for {row['lens']}")
        elif row["id"]:
            print(f"already filed: {row['id']} covers {row['lens']} - nothing minted")
        else:
            print(f"would file a unit for {row['lens']} (dry run)")
    if code == OWED_CANNOT_JUDGE:
        print("verdict: CANNOT JUDGE - this is NOT 'nothing owed'. Attribute the findings above "
              "(file_finding --lens/--audit-run) or record their runs, then re-run.")
    elif code == OWED_CLEAN:
        print("verdict: clean - no lens has survived two separate audit runs unconverted.")
    return code


def cmd_validate_profiles(args: argparse.Namespace) -> int:
    """Hold every lens of every pack to the signature contract.

    Scope is `profile_names()` minus `REFERENCE_PROFILES`, DERIVED rather than listed, so a pack
    added later is held to the rule without anyone remembering to name it here. The two-column
    `project` reference section declares lenses against artifacts and carries no signature
    column, so it is out of scope by construction and not by omission.
    """
    root = Path(getattr(args, "root", None) or ".")
    names = ([args.name] if args.name
             else sorted(set(profile_names()) - set(REFERENCE_PROFILES)))
    errors: list[str] = []
    for name in names:
        try:
            errors.extend(profile_signature_errors(resolve_profile(name), root))
        except UnknownProfile as exc:
            errors.append(f"{name}: {exc}")
    if args.format == "json":
        print(json.dumps({"profiles": names, "errors": errors}, indent=2))
    else:
        for err in errors:
            print(f"SIGNATURE: {err}", file=sys.stderr)
        if not errors:
            print(f"every lens of {len(names)} pack(s) names a detector that resolves or "
                  f"declares `manual` with a reason: {', '.join(names)}")
    return 1 if errors else 0


def cmd_profile(args: argparse.Namespace) -> int:
    """Resolve a profile and report its lenses plus the refute threshold."""
    if getattr(args, "validate", False):
        return cmd_validate_profiles(args)
    if args.list or not args.name:
        names = profile_names()
        if args.format == "json":
            print(json.dumps({"profiles": names}, indent=2))
        else:
            print("audit profiles: " + ", ".join(names))
        return 0
    try:
        p = resolve_profile(args.name)
    except UnknownProfile as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(p, indent=2))
        return 0
    print(f"profile {p['name']} -> {p['source']}")
    print(f"lenses: {len(p['lenses'])}")
    for lens in p["lenses"]:
        print(f"  {lens['name']}: {lens['question']}")
    t = p["threshold"]
    print(f"refute panel: {t['survive']} of {t['votes']} votes" if t
          else "refute panel: NOT DECLARED (the pack must state its threshold)")
    return 0


def find_artifact(root: Path, rec_id: str):
    """Locate an artifact file by id across all types; return (path, type) or None.
    Delegates to the shared `sdlc_md.find_by_id` (one source of truth, alias-aware)."""
    return sdlc_md.find_by_id(root, rec_id)


def _weak_ac(text: str) -> bool:
    """True when the unit has no checkable AC, or the AC are not authored.

    Three ways an AC section fails to be a criterion anyone can check: it holds no
    AC-shaped item at all; an item is the tautology phrase; or the section still
    carries an unexpanded `{{...}}` span from the scaffolding template. The last is
    judged over the whole section rather than the collected items, because a
    criterion's `Verify:` line is part of it whether or not that line is itself
    counted as an item - and the Verify line is precisely what a downstream oracle
    would go on to execute.
    """
    items: list[str] = []
    section: list[str] = []
    in_ac = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if not in_ac:  # only AC inside the Acceptance Criteria section count
            continue
        section.append(line)
        if (_AC_CHECKBOX.match(line) or sdlc_md.AC_HEADING_RE.match(line)
                or sdlc_md.AC_BULLET_RE.match(line)):
            items.append(line)
    if not items:
        return True
    if any(_PLACEHOLDER.search(line) for line in section):
        return True
    return any(TAUTOLOGY in i.lower() for i in items)


def _bug_underspecified(text: str, root: Path | None = None) -> bool:
    """A bug is ready when it documents how to reproduce AND a proposed fix.

    Bugs have no Acceptance Criteria section - judging them by `_weak_ac` would
    always flag them. Readiness for a bug is repro + fix presence instead.
    The accepted heading vocabularies live in the convention layer
    (`conventions.bug_ready_sections` declares a house set): the skill and
    template-revision names plus semantic equivalents - Symptom + Root cause
    counts as repro evidence, and 'Fix (proposed)' equals 'Proposed Fix'.
    """
    has_repro = conventions.section_present(text, "repro", root)
    has_fix = conventions.section_present(text, "fix", root)
    return not (has_repro and has_fix)


def _unmet_deps(root: Path, text: str) -> tuple[list[str], list[str]]:
    """(unmet, unresolved) referents of `Depends on`.

    Resolution runs through the shared `xrepo` helper, so a multi-repo product's real edge is
    seen: a referent delivered in another repo of the PVD manifest MEETS the dependency
    instead of being reported unmet. The two lists are distinct claims, never collapsed -
    `unmet` says the referent exists and is not delivered (or is dead), `unresolved` says the
    audit could not check it because the sibling checkout named in the manifest is not on
    disk. The second is reported with the repo and path named, so it can be neither a silent
    pass nor mistaken for a delivery failure.
    """
    val = sdlc_md.extract_field(text, "Depends on") or sdlc_md.extract_field(text, "Depends On")
    if not val or integrity._is_blank(val):
        return [], []
    repos = xrepo.manifest_repos(root)
    unmet: list[str] = []
    unresolved: list[str] = []
    for ref in sorted({sdlc_md.norm_id(r) for r in sdlc_md.ID_SEARCH_RE.findall(val)}):
        r = xrepo.resolve(ref, Path(root), repos)
        st = r["status"]
        if st is None:  # resolved nowhere: absent sibling checkout, or no such id at all
            if r["error"] == xrepo.MISSING:
                unmet.append(f"{ref}:missing")
            else:
                unresolved.append(f"{ref}: {r['error']}")
        elif st in DEAD:
            unmet.append(f"{ref}:{st}(dead)")
        elif st not in MET:
            unmet.append(f"{ref}:{st}")
    return unmet, unresolved


def _already_satisfied(root: Path, rid: str) -> bool:
    """True if the unit's executable ACs all pass in the verify-report: verified > 0,
    no failures, no stale. Such a Ready unit is already delivered (the audit cannot see a feature
    shipped under a different artifact, but a green verifier set is the deterministic signal) -
    surface it as a close-candidate, not work to build. Manual-only / AC-less units never match."""
    report = sdlc_md.read_json(root / "sdlc-studio" / ".local" / "verify-report.json", {})
    stories = report.get("stories", {})
    items = stories.items() if isinstance(stories, dict) else []
    for stem, e in items:
        if sdlc_md.norm_id(stem.split("-")[0]) == sdlc_md.norm_id(rid):
            return e.get("verified", 0) > 0 and not e.get("failed", 0) and not e.get("stale", 0)
    return False


def _weak_verify(text: str) -> bool:
    """True if a story has a non-executable / mis-written Verify line: reuses
    verify_ac.lint_verifier, so the breakdown flags prose-curl verifiers at design time instead
    of discovering them 0/7 at verify time."""
    for line in text.splitlines():
        m = verify_ac.VERIFY_RE.match(line)
        if m and verify_ac.lint_verifier(m.group(2).strip()):
            return True
    return False


_REGRESSION_RE = re.compile(r"regression|integration|\be2e\b|end[- ]to[- ]end", re.I)


def _missing_regression_test(text: str) -> bool:
    """CR0128 heuristic 2: a Fixed/Done bug should carry an integration- or regression-level test
    (the bug lived in the seams), not only a unit test on the root-cause file. This mechanises the
    NAME signal - a `Verify` line or a 'regression/integration/e2e' marker - and returns True for a
    bug that records tests but none at that level. It deliberately does NOT try to prove a test
    truly exercises the seams: that stays a review judgement (the advisory boundary recorded in
    CR0128). A bug with no test info at all is left to `underspecified`, not double-flagged here."""
    lines = text.splitlines()
    mentions_test = any("**verify:**" in low or "test" in low
                        for low in (line.lower() for line in lines))
    if not mentions_test:
        return False
    return not any(_REGRESSION_RE.search(line) for line in lines)


def audit_unit(root: Path | str, rec_id: str, integrity_errors: set[str] | None = None,
               cross_epic_ids: dict[str, dict] | None = None,
               batch_ids: set[str] | None = None) -> dict:
    """Readiness verdict for a single unit. A dependency that sits in the SAME batch
    (`batch_ids`) is the planner's dependency waves doing their job - reported as
    informational `sequenced-in-batch`, never `unmet-deps`."""
    root = Path(root)
    found = find_artifact(root, rec_id)
    if found is None:
        return {"id": sdlc_md.norm_id(rec_id), "status": "missing", "issues": ["not-found"], "ready": False}
    path, type_ = found
    text = path.read_text(encoding="utf-8")
    rid = sdlc_md.extract_record_id(path.stem) or path.stem
    status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"),
                                      sdlc_md.status_vocab(type_, root)) or "Unknown"
    issues: list[str] = []
    if type_ == "bug":
        if _bug_underspecified(text, root):
            issues.append("underspecified")
        if status in integrity.TERMINAL and _missing_regression_test(text):
            issues.append("missing-regression-test")
    elif _weak_ac(text):
        issues.append("weak-AC")
    if type_ == "story" and _weak_verify(text):  # non-executable Verify line
        issues.append("weak-verify")
    info: list[str] = []
    # Cross-epic AC leakage. `cross_epic_ids` maps a story id to its strongest hit; only a
    # MULTI-keyword hit blocks readiness. `ac_scope` is a single-word keyword heuristic that
    # documents itself as advisory, and every finding it produced against this repo was an
    # ordinary English word ("fixes", "residual", "cleanup", "around") shared with an
    # unrelated epic title. Blocking a tranche on that forced the author either to reword
    # innocent prose or to rescope an AC that was already correctly scoped.
    hit = (cross_epic_ids or {}).get(sdlc_md.norm_id(rid)) if cross_epic_ids else None
    if hit:
        if hit["advisory"]:
            info.append(f"cross-epic-ac (advisory, 1 shared keyword {hit['keyword']!r} with "
                        f"{hit['owner_epic']}) - a single common word is not evidence of scope leakage")
        else:
            issues.append("cross-epic-ac")
    unmet, unresolved = _unmet_deps(root, text)
    if unmet and batch_ids:
        # only a PENDING in-batch dep is the planner's sequencing at work; a dead
        # (Rejected/Superseded) or missing dep cannot be delivered by wave order.
        def _sequenceable(u: str) -> bool:
            return (sdlc_md.norm_id(u.split(":")[0]) in batch_ids
                    and not u.endswith(":missing") and "(dead)" not in u)
        sequenced = [u for u in unmet if _sequenceable(u)]
        unmet = [u for u in unmet if not _sequenceable(u)]
        info.extend(f"sequenced-in-batch: {u.split(':')[0]}" for u in sequenced)
    if unmet:
        issues.append("unmet-deps: " + ", ".join(unmet))
    if unresolved:  # the checkout is absent, so the dependency could not be checked either way
        issues.append("unresolved-deps: " + ", ".join(unresolved))
    if status in integrity.TERMINAL:
        issues.append("already-terminal")
    if integrity_errors and rid in integrity_errors:
        issues.append("link-integrity")
    if status not in integrity.TERMINAL and _already_satisfied(root, rid):
        issues.append("already-satisfied")  # verifiers pass -> close-candidate, don't build
    return {"id": rid, "type": type_, "status": status, "issues": issues,
            "info": info, "ready": not issues}


def audit_batch(repo_root: Path | str, ids: list[str]) -> dict:
    """Readiness report over a batch of unit ids.

    `uncomputed` names any check that did not run. It is never empty and quietly ignored:
    a batch whose cross-epic sweep crashed has no cross-epic verdict for ANY unit, so the
    report says so, the caller exits non-zero, and a partial answer is never dressed up as
    a clean one."""
    root = Path(repo_root)
    ierr = {f["id"] for f in integrity.detect_integrity(root)["findings"] if f["severity"] == "error"}
    uncomputed: list[str] = []
    # cross-epic AC leakage, computed once for the batch (ac_scope is repo-wide)
    cross: dict[str, dict] = {}
    try:
        for f in ac_scope.check(root):
            if not f.get("story"):
                continue
            sid = sdlc_md.norm_id(f["story"])
            # Keep the STRONGEST hit per story: a blocking one must not be hidden behind an
            # advisory one that happened to sort first.
            if sid not in cross or f.get("strength", 1) > cross[sid].get("strength", 1):
                cross[sid] = f
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        # The sweep is repo-wide, so a partial `cross` cannot be trusted for any unit: drop
        # it AND declare it. Erasing a blocking strength>1 hit silently is how a not-ready
        # unit walks into a sprint carrying a green verdict nobody computed.
        cross = {}
        uncomputed.append(f"cross-epic-ac: {type(exc).__name__}: {exc}")
        print(f"warning: cross-epic AC check did not run ({type(exc).__name__}: {exc}); "
              "no unit in this batch has a cross-epic verdict", file=sys.stderr)
    batch_ids = {sdlc_md.norm_id(i) for i in ids}
    units = [audit_unit(root, i, ierr, cross, batch_ids=batch_ids) for i in ids]
    ready = sum(1 for u in units if u["ready"])
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "units": units,
        "uncomputed": uncomputed,
        "summary": {"total": len(units), "ready": ready, "not_ready": len(units) - ready,
                    "uncomputed": len(uncomputed)},
    }


def cmd_check(args: argparse.Namespace) -> int:
    """Audit a batch (by ids or a status query); exit non-zero if any unit is not ready."""
    ids = sdlc_md.resolve_ids(args)
    query = args.crs if args.crs is not None else args.bugs if args.bugs is not None else args.stories
    if bool(ids) == (query is not None):
        print("specify exactly one selection mode: id(s) (--id/--ids) OR a status query "
              "(--crs/--bugs/--stories)", file=sys.stderr)
        return 2
    if not ids:
        kind, status = (("cr", args.crs) if args.crs is not None
                        else ("bug", args.bugs) if args.bugs is not None
                        else ("story", args.stories))
        ids = [b["id"] for b in sprint.select_batch(args.root, kind, status)]
    res = audit_batch(args.root, ids)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        s = res["summary"]
        # The header carries the partial marker, derived from the same list the exit code
        # keys off: a total that reads as complete over a check that never ran is the
        # defect, not the wording.
        partial = f" - PARTIAL, {s['uncomputed']} check(s) did not run" if res["uncomputed"] else ""
        print(f"tranche audit: {s['ready']}/{s['total']} ready, {s['not_ready']} not{partial}")
        for miss in res["uncomputed"]:
            print(f"  UNCOMPUTED {miss}")
        kinds = set()
        for u in res["units"]:
            if not u["ready"]:
                print(f"  NOT READY {u['id']} ({u['status']}): {'; '.join(u['issues'])}")
                kinds.update(i.split(":")[0].strip() for i in u["issues"])  # issue may carry a suffix
            for note in u.get("info", []):  # informational, never blocks readiness
                print(f"  note      {u['id']}: {note}")
        hints = sdlc_md.remediation_lines("audit", kinds)
        if hints:
            print("Guidance:")
            for h in hints:
                print(f"  - {h}")
    # A check that did not run fails the gate exactly like a not-ready unit: the batch was
    # not cleared, and only an exit code says so to the caller.
    return 1 if (res["summary"]["not_ready"] or res["uncomputed"]) else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio tranche audit (sprint pre-flight).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Audit a batch for readiness before the triage STOP.")
    sdlc_md.add_ids_argument(c, help_="unit ids to audit; repeat --id or pass --ids as one "
                                      "comma list (e.g. --id CR0003 --id CR0004)")
    g = c.add_mutually_exclusive_group()
    g.add_argument("--crs", metavar="STATUS", help="CRs with this Status")
    g.add_argument("--bugs", metavar="STATUS", help="Bugs with this Status")
    g.add_argument("--stories", metavar="STATUS", help="Stories with this Status")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    p = sub.add_parser("profile", help="Resolve an audit lens profile (--name repo) or "
                                       "list the profiles that exist.")
    p.add_argument("--name", help="profile to resolve (e.g. repo, code, skill, project)")
    p.add_argument("--list", action="store_true", help="list the profiles that exist")
    p.add_argument("--validate", action="store_true",
                   help="hold every lens to the signature contract: a signature present, a "
                        "mechanical one naming a target that resolves, an absent one declared "
                        "as `manual - <reason>`. Every pack when --name is omitted. Exits 1 on "
                        "any breach, so a consuming project that appends a pack row can enforce "
                        "the same rule without running this repository's tests")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_profile)
    o = sub.add_parser("detector-owed",
                       help="name the lenses filed under two or more separate audit runs whose "
                            "signature declares no mechanical detector - a judgement the model "
                            "has now paid for twice, and that a script should take over. "
                            "Exits 0 clean, 1 owed, 3 cannot-judge")
    o.add_argument("--file", action="store_true",
                   help="mint one sized CR per owed lens through file_finding.py, stamped "
                        "`Detector-for-lens`. Idempotent on that field, so a second close-out "
                        "reports the existing unit and mints nothing. Refuses on a cannot-judge "
                        "verdict rather than filing off a workspace it could not read")
    o.add_argument("--dry-run", action="store_true",
                   help="with --file, name what would be filed and mint nothing")
    o.add_argument("--format", choices=("text", "json"), default="text")
    o.set_defaults(func=cmd_detector_owed)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
