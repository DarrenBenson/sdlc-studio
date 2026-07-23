#!/usr/bin/env python3
"""SDLC Studio deterministic finding filer.

Files a Bug / CR / RFC from an audit (or any) finding: allocate a collision-free ID,
render a STRUCTURED artifact (required sections enforced, so it cannot emit a hollow
stub - the 2nd audit run's lesson), write it, append the index row, and recompute the
index summary counts (reusing reconcile's tested count pass). Deterministic given the
inputs; the caller supplies the rich content.

Subcommands:
  file     Create one artifact (--type bug|cr|rfc) from --title + fields.
  rebuild  Recompute a type's index summary counts from its rows (delegates to reconcile).

Read-only over everything except the new artifact file and its index. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import next_id  # noqa: E402  (sibling)
import reconcile  # noqa: E402  (sibling - reuse the tested count recompute)
import triage_noise  # noqa: E402  (sibling - v3 triage noise controls; dormant on v2)

# Per-type: workspace dir, filename prefix, index display-id form, default status, and
# the fields a non-hollow artifact must carry (the richness guard). The `status` cell is
# DERIVED from the status vocabulary in `lib.sdlc_md` - the one authority - so the filer and
# the general creator can never disagree about the state a finding is born in.
TYPES = {
    "bug": {"dir": "bugs", "prefix": "BG", "disp": "BG{n:04d}",
            "status": sdlc_md.create_status("bug"),
            "required": ("severity", "summary", "steps", "fix")},
    # A CR carries an impact statement and a size. Its size is a T-shirt `Size` (S/M/L/XL), not
    # points: a CR is a REQUEST, sized coarsely before it is decomposed into stories, and story
    # points belong on the delivery unit that is measured. `Size` is demanded by the grooming
    # gate (`check_groomed`), not listed here - exactly as a bug's `Points` is - so the refusal
    # names the flag and explains the scale rather than emitting a bare "missing field".
    "cr": {"dir": "change-requests", "prefix": "CR", "disp": "CR-{n:04d}",
           "status": sdlc_md.create_status("cr"),
           "required": ("priority", "ctype", "summary", "acs", "impact")},
    "rfc": {"dir": "rfcs", "prefix": "RFC", "disp": "RFC-{n:04d}",
            "status": sdlc_md.create_status("rfc"),
            "required": ("summary", "options")},
}


# --- The pseudo-Verify refusal (one authority, both creation paths) -------------------------
#
# Only a STORY carries an executable check: its canonical `- **Verify:**` line is parsed and RUN
# by verify_ac.py, and gates the story to Done. A CR or bug carries PROSE acceptance criteria -
# a checklist a human reads. Writing a command-shaped `Verify: <cmd>` into that prose mints a
# check that LOOKS executable and is run by nothing, so a wrong command is a permanent false red
# and a vacuous one (a grep that matches unrelated prose) is a false green on an unbuilt feature.
# The creators refuse to write one; the validator warns about the ones already on disk.
#
# MATCHED (refused): a `Verify:` / `**Verify:**` lead-in whose tail, once its wrapping backticks,
# quotes and bold markers are stripped, is command-shaped - it opens with a shell/tool verb
# (`rg -q x`, `test -f x`, `python3 -m unittest`, `./install.sh`), or it carries a shell operator
# (`&&`, `||`, `$(...)`, a pipe into a command).
#
# LET THROUGH (honest prose): the word verify anywhere in a criterion ("Verify the operator sees
# the banner", "the verifier reports it"), and a `Verify:` lead-in followed by an outcome rather
# than a command ("Verify: the operator sees a red banner naming the file"). The target is the
# command shape, not the word.
_VERIFY_LEAD_RE = re.compile(r"\bverif(?:y|ies|ied)\s*:\s*(\S[^\n]*)", re.I)
# Verbs that are commands and nothing else: leading one of these IS the command shape.
_TOOL_VERBS = frozenset("""
    rg ripgrep grep egrep fgrep ag ack pytest py.test tox python python3 npm npx pnpm yarn
    node deno bash zsh fish jq yq curl wget xargs cargo cmake mvn gradle dotnet rake composer
    git gh sed awk docker kubectl terraform ruby php shell sudo printf
""".split())
# Verbs that are also ordinary English ("test that it fails", "make the banner red", "find the
# file"). One of these opens a command only when what FOLLOWS it is command-shaped too: a flag,
# or a path/module argument. Otherwise it is prose, and prose is allowed.
_AMBIGUOUS_VERBS = frozenset("test [ find make go ls cat head tail wc diff sh env echo".split())
_CMD_ARG_RE = re.compile(r"^-{1,2}[A-Za-z]|/|\.(?:py|sh|md|js|ts|json|ya?ml|txt|toml|cfg)\b")
_SHELL_OP_RE = re.compile(r"&&|\|\||\$\(|\|\s*(?:jq|grep|rg|wc|head|tail|sed|awk|xargs)\b")
_WRAPPERS = "`'\"*() \t"


def command_shaped(tail: str) -> bool:
    """True when `tail` reads as a command rather than an outcome.

    Command-shaped: it opens with a tool verb (`rg -q x`, `python3 -m unittest ...`), or with a
    `./path` invocation, or with an English-ambiguous verb whose next token is itself
    command-shaped (`test -f x`, `find src/ -name ...`), or it carries a shell operator
    (`&&`, `||`, `$(...)`, a pipe into a command). Everything else - including a sentence that
    merely opens with the word `test` or `make` - is prose, and prose is what a CR/bug criterion
    is supposed to be."""
    t = tail.strip().strip(_WRAPPERS).strip()
    t = re.sub(r"^!\s*", "", t)  # a negated command (`! rg -q x`) is still a command
    if not t:
        return False
    tokens = t.split()
    first = tokens[0]
    if first in _TOOL_VERBS or re.match(r"^\.{0,2}/\S", first):
        return True
    if first in _AMBIGUOUS_VERBS and len(tokens) > 1 and _CMD_ARG_RE.search(tokens[1]):
        return True
    return bool(_SHELL_OP_RE.search(t))


def pseudo_verify(text: str) -> str | None:
    """The command-shaped pseudo-`Verify:` in one acceptance criterion, or None.

    Returns the offending command so the caller can quote it back - naming the exact string is
    what makes the refusal teachable rather than cryptic."""
    for m in _VERIFY_LEAD_RE.finditer(str(text)):
        tail = m.group(1)
        if command_shaped(tail):
            return tail.strip().strip(_WRAPPERS).strip()
    return None


def check_prose_acs(type_: str, fields: dict) -> None:
    """Refuse, BEFORE any id is allocated or any byte written, a CR/bug acceptance criterion
    carrying a command-shaped `Verify:`. Called from BOTH creation paths (the finding filer and
    `artifact new` / `artifact batch`), so neither is an escape hatch for the other.

    Stories are untouched: their `--verify` lines are the real, executed thing."""
    if type_ not in ("cr", "bug"):
        return
    items = fields.get("acs")
    if not isinstance(items, (list, tuple)):
        return
    for i, ac in enumerate(items, 1):
        cmd = pseudo_verify(ac)
        if cmd is None:
            continue
        raise ValueError(
            f"{type_} acceptance criterion {i} carries a command-shaped `Verify:` check "
            f"({cmd!r}) - refused.\n"
            f"  Why: nothing runs it. verify_ac only executes the canonical `- **Verify:**` line "
            f"of a STORY. A command written into {type_.upper()} acceptance-criteria prose is "
            f"never executed, so a wrong one is a permanent false red and a loose one is a false "
            f"green - it 'passes' on unrelated prose while the feature does not exist.\n"
            f"  Instead: state the OBSERVABLE outcome - what would have to be true for this "
            f"criterion to hold. Executable proof arrives when the {type_.upper()} is actioned "
            f"into stories, which carry real `- **Verify:**` lines that verify_ac runs and that "
            f"gate them to Done.\n"
            f"  e.g. not 'Verify: rg -qi points sprint.py' but 'sprint.py reads the CR Points "
            f"field and sizes the unit by it, rather than falling back to the flat default'.")


# --- The grooming demand (the filer asks the PLANNER, it does not re-state the rule) ---------
#
# `sprint plan` REFUSES a batch holding an UNGROOMED unit - one that names neither the files it
# will touch (`Affects`) nor a size. A creator that cannot even RECORD `Affects` mints exactly
# that unit every time, and the repair then lands on an operator at plan time: the wrong person,
# at the wrong moment. The author knows which files are involved WHEN THEY FILE. Nobody knows it
# better later.
#
# So the creator asks the planner - not a second copy of the predicate, the predicate itself.
# The body about to be written is handed to `sprint.breakdown`, and whatever IT calls ungroomed
# is what the creator refuses. Two consequences a restated rule would have missed: a value the
# planner's parser cannot read as a file (`--affects everything`) is refused here too, and a
# future third grooming field lands in both ends at once.
#
# The escape is the planner's own, read from the same config key: `sprint.breakdown: judgement`
# makes the gate report instead of block, and an operator who has opted out is not then blocked
# at the creator either. Omission is not an escape - with no config, the fields are demanded.
#
# Scope: bug and CR - the finding types a sprint batch is built from. An RFC is not a unit of
# sprint work at all (the planner never selects one), and its whole purpose is to settle a design
# whose files are the OUTPUT of the decision, not an input to it: demanding `Affects` of an RFC
# would be grooming theatre, a field nothing downstream reads. A story is gated by the same
# planner, but it is created by decomposition rather than filed as a finding, and its grooming
# is out of this fix's scope - `--affects` is accepted on it and written when supplied.
GROOMED_TYPES = ("bug", "cr")

# What to hand the author for each gap the gate can name. Keyed by the gate's own token, so a
# bug/story missing its `Points` and a CR/RFC missing its `Size` each get the flag that fills it.
_GROOM_FLAG = {
    "Affects": '--affects "path/to/file.py, path/to/other.py"  (the files this will touch)',
    "Points": (f"--points {'|'.join(str(p) for p in sdlc_md.POINTS_SCALE)}  (the job SIZE of the "
               f"work, RELATIVE to units you have already delivered - a bug's Severity is its "
               f"urgency, a different axis)"),
    "Size": (f"--size {'|'.join(sdlc_md.SIZE_SCALE)}  (the T-shirt size of this REQUEST, sized "
             f"coarsely before it is decomposed into stories - story points belong on the "
             f"delivery unit, not on the request)"),
}


def grooming_gaps(repo_root: Path | str, type_: str, text: str) -> tuple[list[str], bool]:
    """What `sprint plan`'s breakdown gate would find missing on this artefact-to-be, and
    whether the gate is blocking.

    Judged by `sprint.breakdown` itself - the ONE definition of groomed - over the exact body
    that is about to be written, as a batch of one. `skip_personas`: a review seat's estimate is
    keyed by an id this artefact does not have yet, so the only size available to it is the one
    the author writes on it, which is precisely what is being asked for."""
    if type_ not in GROOMED_TYPES:
        return [], False
    import sprint  # noqa: PLC0415 - local: the creator borrows the planner's predicate, not its weight
    with tempfile.TemporaryDirectory() as td:
        preview = Path(td) / "preview.md"
        preview.write_text(text, encoding="utf-8")
        bd = sprint.breakdown(repo_root, [{"id": "PREVIEW", "type": type_,
                                           "path": str(preview)}], skip_personas=True)
    missing = list(bd["ungroomed"][0]["missing"]) if bd["ungroomed"] else []
    return missing, bool(bd["blocking"])


def check_groomed(repo_root: Path | str, type_: str, text: str) -> None:
    """Refuse - BEFORE an id is allocated or a byte written - an artefact `sprint plan` would
    then refuse to PLAN. Called from BOTH creation paths (the finding filer and `artifact new` /
    `artifact batch`), so neither can mint a unit the other end of the pipeline rejects.

    Under the recorded opt-out (`sprint.breakdown: judgement`) the creator warns instead of
    refusing, exactly as the gate reports instead of blocking - one decision, honoured at both
    ends. An opt-out that also went quiet would be the disease, not the cure."""
    missing, blocking = grooming_gaps(repo_root, type_, text)
    if not missing:
        return
    if not blocking:
        print(f"warning: this {type_} is ungroomed (no {', '.join(missing)}) - written anyway, "
              f"because this project records `sprint.breakdown: judgement`. `sprint plan` will "
              f"quote it at a flat floor, not an estimate.", file=sys.stderr)
        return
    raise ValueError(
        f"{type_} is UNGROOMED - refused. Nothing was allocated, nothing was written.\n"
        f"  Missing: {', '.join(missing)}\n"
        f"  Why: `sprint plan` REFUSES a batch holding this unit, so filing it this way mints "
        f"work nobody can plan. Without `Affects` the planner cannot size it (the complexity "
        f"seed is 0, so its forecast collapses to a flat floor nobody labelled as a fallback) "
        f"and cannot see that two units touch the SAME FILE - it would report them as safely "
        f"parallel when they will collide. Without a size, the estimate is a guess wearing a "
        f"number.\n"
        f"  Supply:\n"
        + "".join(f"    {_GROOM_FLAG.get(m, m)}\n" for m in missing) +
        f"  e.g. --affects \"scripts/sprint.py, scripts/file_finding.py\" "
        + ("--size M" if type_ == "cr" else "--points 5") + "\n"
        f"  You know which files this touches NOW. Nobody knows it better at plan time - and "
        f"an `Affects` the parser cannot read as a path (a prose phrase, a bare word) counts "
        f"as no `Affects` at all.\n"
        f"  Opt out ONLY as a recorded decision: set `sprint.breakdown: judgement` in "
        f"sdlc-studio/.config.yaml and this becomes a warning, at both ends.")


# --- The one resolvable-Affects predicate (every writer's single seam) -----------------------
#
# A declared `Affects` naming only paths with nothing behind them is a fictional footprint: the
# plan's collision analysis mis-groups the unit, the engagement floor under-reads it, and gate's
# changed-surface pass reads it too - all while the command exits 0. `file_finding.file` refused
# it already (through the grooming gate); `artifact new` and `refine apply` did not, so five of
# 23 stories minted through one decomposition run carried a wrong `Affects`.
#
# This is the ONE seam the three writers and the grooming gate all resolve `Affects` through, so
# a path one command mints is never one another refuses, and a fourth writer added later cannot
# quietly resolve paths by its own means. `sprint.breakdown` reads `unresolvable_affects` too, so
# the mint check and the plan gate cannot drift on what 'resolvable' means.
#
# It refuses ONLY when a path is declared AND none of the declared paths resolves. A path to a
# file the unit will CREATE cannot resolve yet and is the ordinary case, so SOME unresolved paths
# are legitimate; ALL of them is the error - exactly the rule the grooming gate already applies.
#: Directory names never worth walking for a basename match (VCS internals, caches, worktree
#: clones of the tree itself). Pruned so the suggestion lookup stays fast and free of noise.
_SUGGEST_SKIP_DIRS = frozenset({".git", "node_modules", "__pycache__", ".mypy_cache",
                                ".pytest_cache", ".local", ".venv", "venv", ".tox", "worktrees"})

#: The types whose declared `Affects` is a sprint footprint the planner reads - a delivery unit
#: (story/bug) or a request (cr). An RFC is excluded for the same reason the grooming gate excludes
#: it: its `Affects` names the files that are the OUTPUT of the decision it settles, so they cannot
#: resolve yet and refusing on them would be theatre. An epic or PRD carries no unit footprint here.
_AFFECTS_CHECKED_TYPES = ("bug", "cr", "story")


def declared_affects(value: str) -> list[str]:
    """The file paths a raw `Affects` value declares, read by the ONE parser the planner uses
    (`sdlc_md.affects_files`), so a value the planner cannot read as a path list (a bare word,
    a prose phrase) yields nothing here too - it is no `Affects` at all, not a fictional one."""
    return sdlc_md.affects_files(f"> **Affects:** {value or ''}")


def unresolvable_affects(repo_root: Path | str, declared: list[str]) -> list[str]:
    """The declared `Affects` paths with nothing behind them on disk - the single resolver seam.

    Every writer (`file_finding.file`, `artifact new`/`batch`, `refine apply`) and the grooming
    gate (`sprint.breakdown`) bottom out HERE, so 'resolvable' has exactly one definition. A path
    resolves against the repo root OR the installed skill dir (`sdlc_md.resolve_affects`)."""
    root = Path(repo_root)
    return [p for p in declared if sdlc_md.resolve_affects(root, p) is None]


def basename_matches(repo_root: Path | str, path: str) -> list[str]:
    """Real files in the repo carrying the basename of an unresolvable `path`, as repo-relative
    paths (sorted). The lookup behind the refusal's suggestion; empty when nothing carries the
    basename. A wrong directory prefix is the measured hazard - the same wrong prefix was typed
    six times in one session - so the basename is almost always right and the tool holds the
    answer at the moment it refuses."""
    import os  # noqa: PLC0415 - local: only the refusal path walks the tree
    root = Path(repo_root)
    base = os.path.basename(str(path).rstrip("/"))
    if not base:
        return []
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SUGGEST_SKIP_DIRS]
        if base in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, base), root))
    return sorted(out)


def affects_suggestions(repo_root: Path | str, unresolvable: list[str]) -> str:
    """The 'did you mean' lines for a refusal, one per unresolvable path. A UNIQUE basename match
    is named as the likely correction; SEVERAL are listed with a note that the tool cannot choose
    between them; NONE says so plainly, so the author is never sent to a file the tool invented.

    Built where the predicate lives so every writer's refusal carries the same suggestion. Help,
    never a correction: nothing is rewritten on the author's behalf, and a guess is never an
    answer."""
    import os  # noqa: PLC0415 - local, as `basename_matches`
    lines: list[str] = []
    for p in unresolvable:
        matches = basename_matches(repo_root, p)
        base = os.path.basename(str(p).rstrip("/"))
        if len(matches) == 1:
            lines.append(f"    {p}: did you mean {matches[0]}?")
        elif len(matches) > 1:
            lines.append(f"    {p}: {base} exists at {', '.join(matches)} - cannot choose "
                         f"between them, name the one you meant")
        else:
            lines.append(f"    {p}: no file named {base} found in the repo")
    return "\n".join(lines)


def check_affects_resolvable(repo_root: Path | str, affects_value: str,
                             type_: str | None = None, label: str = "") -> None:
    """Refuse - BEFORE an id is allocated or a byte written - a declared `Affects` that resolves
    to nothing. The check EVERY writer runs (`file_finding.file`, `artifact new`/`batch`,
    `refine apply`), from the same seam the grooming gate reads, so a path one command mints
    another never refuses and a future writer added without it fails US0323's routing check.

    Refuses only when a path is declared AND none resolves; an absent `Affects`, or one with at
    least one resolving path (the file the unit will CREATE alongside an existing one), is
    untouched - the ordinary case is unaffected. `type_`, when given, scopes the check to a unit
    whose `Affects` is a sprint footprint (`_AFFECTS_CHECKED_TYPES`): an RFC's declared files are
    the output of its decision, so it is skipped exactly as the grooming gate skips it. Honours
    the recorded grooming opt-out (`sprint.breakdown: judgement`): a warning, not a refusal, so
    this is never the one gate an opted-out project cannot escape. `label` names the unit in a
    batch refusal (a story of a decomposition), so the message says WHICH one carried the bad
    path."""
    if type_ is not None and type_ not in _AFFECTS_CHECKED_TYPES:
        return
    declared = declared_affects(affects_value)
    if not declared:
        return
    unresolvable = unresolvable_affects(repo_root, declared)
    if len(unresolvable) != len(declared):
        return  # at least one path resolves - a file the unit will CREATE is legitimate
    where = f"{label}: " if label else ""
    suggestions = affects_suggestions(repo_root, unresolvable)
    import sprint  # noqa: PLC0415 - local: the writer reads the planner's opt-out, not its weight
    if sprint.breakdown_mode(repo_root) == "judgement":
        print(f"warning: {where}the declared Affects resolves to nothing "
              f"({', '.join(unresolvable)}) - written anyway, because this project records "
              f"`sprint.breakdown: judgement`.\n{suggestions}", file=sys.stderr)
        return
    raise ValueError(
        f"{where}the declared Affects resolves to nothing - refused. Nothing was allocated, "
        f"nothing was written.\n"
        f"  No declared path exists on disk: {', '.join(unresolvable)}\n"
        f"{suggestions}\n"
        f"  Why: a fictional footprint mis-groups the unit in the plan's collision analysis, "
        f"under-reads it in the engagement floor, and misreports it in gate's changed-surface "
        f"pass - all while the command exits 0. A path to a file the unit will CREATE is fine; "
        f"the check refuses only when NO declared path resolves.\n"
        f"  Fix the directory prefix (the basename is usually right), or drop the wrong path. "
        f"Opt out ONLY as a recorded decision: `sprint.breakdown: judgement` in "
        f"sdlc-studio/.config.yaml makes this a warning.")


def scan_prose_acs(text: str) -> list[tuple[int, str, str]]:
    """Every command-shaped pseudo-`Verify:` inside an artefact's Acceptance Criteria section, as
    (1-based line number, the line, the offending command). The read-only counterpart of
    `check_prose_acs`, for the instances already on disk (the validator's warning lane)."""
    out: list[tuple[int, str, str]] = []
    in_ac = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if not in_ac:
            continue
        cmd = pseudo_verify(line)
        if cmd:
            out.append((n, line, cmd))
    return out


# --- The non-shell input path, and the hazard report on the one that survives ----------------
#
# Every field of a filed finding used to arrive as a command-line argument, so the caller's shell
# saw it first - and the fields that matter most (`--steps`, `--fix`) are precisely the ones whose
# content is COMMANDS. Inside a double-quoted argument a backtick and a `$(` are command
# substitution, so the prose was executed rather than stored. Twice in one sprint: BG0240 was
# filed with two reproduction commands silently deleted, and BG0242 - a bug about destructive git
# commands - EXECUTED `git commit -a` against the live repository while being filed.
#
# The remedy is a document no shell expands. A FILE rather than stdin, deliberately: a file can be
# re-run, committed as evidence and diffed, and reproducibility is the whole point of moving prose
# off the command line. The flags survive for compatibility - removing them breaks every caller -
# but they gain the report below, because the silent half of the defect is worse than the loud one.

#: Fields a creator may supply in a `--fields-file` document. Shared with `artifact new`, which
#: adds its own (an epic, a persona, verifiers); an unlisted key is REFUSED rather than ignored,
#: so a typo is a message and not a field that quietly went missing.
COMMON_FIELDS_FILE_KEYS: tuple[str, ...] = (
    "title", "summary", "severity", "priority", "ctype", "steps", "fix", "impact",
    "points", "size", "affects", "acs", "options", "recommendation", "parent", "author",
    "date",
)
FIELDS_FILE_KEYS: tuple[str, ...] = (*COMMON_FIELDS_FILE_KEYS,
                                     "mutation_run", "mutation_target")

#: The prose fields a shell would have expanded. Checked for damage, never rewritten.
HAZARD_FIELDS: tuple[str, ...] = ("title", "summary", "steps", "fix", "impact", "recommendation")


def shell_hazards(fields: dict, keys: tuple[str, ...] | None = None) -> list[tuple[str, str]]:
    """(field, what was found) for every value bearing the marks of a shell that already ate it.

    Three shapes, each a known outcome of passing prose through a double-quoted shell argument:
    an UNBALANCED backtick (the pair's other half, and everything between, is gone), a surviving
    `$(` (substitution the shell did not complete, or prose that would be substituted next time),
    and a TRAILING backslash (a line continuation that swallowed what followed).

    `keys` names the prose fields to inspect - the finding filer's `HAZARD_FIELDS` by default, or a
    caller's own prose keys (e.g. a sign-off `note`, a goal verdict) so a writer with a different
    field name is not silently unchecked.

    Detection only. The value is reported, never rewritten: a field quietly repaired is a
    success the tool did not achieve, and the author is the only one who knows what was lost."""
    out: list[tuple[str, str]] = []
    for key in (keys if keys is not None else HAZARD_FIELDS):
        val = fields.get(key)
        if not isinstance(val, str) or not val:
            continue
        if val.count("`") % 2:
            out.append((key, "an unbalanced backtick - a backtick pair is command "
                             "substitution, and its other half (with everything between) "
                             "is what a shell removes"))
        if "$(" in val:
            out.append((key, "a `$(` - command substitution the shell either already ran "
                             "or will run next time this value is passed as an argument"))
        stripped = val.rstrip(" \t\n")
        if stripped.endswith("\\") and not stripped.endswith("\\\\"):
            out.append((key, "a trailing backslash - a line continuation swallows whatever "
                             "followed it"))
    return out


def report_shell_hazards(fields: dict, source: str = "the command line",
                         stream=None, keys: tuple[str, ...] | None = None) -> list[tuple[str, str]]:
    """Report, on stderr, every field arriving through a shell already mangled. Returns what it
    found (empty when clean), so a caller can act on it. `keys` is passed through to
    `shell_hazards` so a writer's own prose fields are checked, not only the filer's default set.

    ONE implementation, called by every creator that takes free prose on the command line. Two
    copies of a pattern list drift, and a drifted list is the silent half of this defect all over
    again. A report, not a refusal: refusing would lose the content the author has in hand, and
    the flag path is the compatible one. What must not happen is silence."""
    found = shell_hazards(fields, keys=keys)
    if not found:
        return []
    out = stream if stream is not None else sys.stderr
    print(f"warning: {len(found)} field(s) reached the filer through {source} carrying shell "
          f"metacharacters - what is stored may already be missing what the shell removed:",
          file=out)
    for key, what in found:
        print(f"  --{key}: {what}", file=out)
    print("  Fix: pass the finding as a JSON document instead - `--fields-file finding.json` "
          "with the same field names. Nothing in it crosses a shell, so the text is stored "
          "exactly as written.", file=out)
    return found


def resolve_prose_fields(fields_file: str | None, flag_fields: dict,
                         allowed: tuple[str, ...]) -> dict:
    """The ONE path a prose-taking writer (critic, close_owed, sprint, ...) uses to obtain its
    free-text fields safely, so every writer routes through the same loader rather than a second
    idiom that could drift.

    With a `--fields-file`: read the JSON document (no value crossed a shell, so the text is stored
    exactly as written) and let it supply the fields; an explicit flag still overrides its key. With
    no fields-file: the flag values DID cross a shell, so any shell metacharacters they carry are a
    swallowed command - report them (non-blocking, the flag path stays compatible). Empty/None flag
    values are dropped before either path. Raises ValueError on a bad fields-file (unreadable, not a
    JSON object, or an unknown key), which the caller turns into a refusal."""
    flags = {k: v for k, v in flag_fields.items() if v is not None and v != ""}
    if fields_file:
        from_file = load_fields_file(fields_file, allowed=allowed)
        return {**from_file, **flags}          # an explicit flag wins over the document
    # Flag path only - a file path crossed no shell. Check the writer's OWN prose keys, not just
    # the finding filer's default HAZARD_FIELDS, or a `note`/`verdict` would go unchecked.
    report_shell_hazards(flags, keys=allowed)
    return flags


def load_fields_file(path: Path | str, allowed: tuple[str, ...] = FIELDS_FILE_KEYS) -> dict:
    """Read a `--fields-file` JSON document into a fields dict, or raise ValueError.

    The whole point is that no value here has crossed a shell, so the text is stored exactly as
    written. Refuses an unreadable file, a document that is not an object, and any key outside
    `allowed` - a mistyped key that is silently ignored is the same silent-loss class the file
    exists to end."""
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"--fields-file {p} cannot be read: {exc}") from exc
    except ValueError as exc:
        raise ValueError(f"--fields-file {p} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"--fields-file {p} holds {type(data).__name__}, not a JSON object of "
                         f"field names - e.g. {{\"title\": \"...\", \"steps\": \"...\"}}")
    unknown = sorted(k for k in data if k not in allowed)
    if unknown:
        raise ValueError(f"--fields-file {p} carries unknown field(s): {', '.join(unknown)} - "
                         f"known fields are {', '.join(allowed)}. A key nobody reads is a field "
                         f"that silently went missing, so it is refused rather than ignored")
    return {k: v for k, v in data.items() if v is not None}


def index_template_path(type_: str) -> Path:
    return Path(__file__).resolve().parent.parent / "templates" / "indexes" / f"{type_}.md"


def write_empty_index(idx: Path, tmpl: Path, today: str) -> bool:
    """Materialise an empty `_index.md` at `idx` from index template `tmpl` when missing.

    The single index-writer both bootstrap paths share - `ensure_index` (pipeline types) and
    `artifact._ensure_meta_index` (retro/review/handoff) - so the render is identical for
    every index. Yields a clean *empty* index: template comment stripped, `last_updated`
    stamped, summary counts zeroed, data-table headers kept (so `append_index_row` works),
    template sample rows/headings dropped (real content never carries `{{ }}`), and any double
    blank a dropped mid-body sample row would leave collapsed to one (MD012). Idempotent:
    never clobbers an existing index, and a no-op when the template is missing. Returns True
    iff it created the file."""
    if idx.exists():
        return False
    if not tmpl.exists():
        return False
    text = tmpl.read_text(encoding="utf-8")
    text = re.sub(r"^<!--.*?-->\n+", "", text, count=1, flags=re.DOTALL)  # strip template comment
    text = text.replace("{{last_updated}}", today)
    text = re.sub(r"\{\{[a-z_]*count\}\}", "0", text)  # zero the summary counts
    lines = [ln for ln in text.splitlines() if "{{" not in ln]  # drop sample rows/headings
    # Dropping a sample line that sat between two blanks leaves a double blank line (MD012);
    # collapse any run of blanks to one so the fresh index lints clean from creation.
    collapsed: list[str] = []
    for ln in lines:
        if not ln.strip() and collapsed and not collapsed[-1].strip():
            continue
        collapsed.append(ln)
    idx.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(idx, "\n".join(collapsed).rstrip() + "\n")
    return True


def ensure_index(repo_root: Path | str, type_: str, today: str) -> bool:
    """Create `<dir>/_index.md` from `templates/indexes/<type>.md` when missing.

    The canonical pipeline-index bootstrap, shared by `artifact new` (lazy, first-use) and
    `init` (front-loaded). Delegates the render to `write_empty_index` (also used by
    `artifact._ensure_meta_index`), so every fresh index - pipeline or meta - is written the
    same way. Idempotent: never clobbers an existing index. Returns True iff it created the
    file."""
    idx = Path(repo_root) / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    return write_empty_index(idx, index_template_path(type_), today)


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return "-".join(s.split("-")[:8]) or "untitled"


def _next_number(repo_root: Path, type_: str) -> int:
    # Honour local files, lingering index rows, and origin/main - never re-issue an id
    # that exists only on the remote or as a stale index row.
    return next_id.allocate_number(type_, repo_root)


# Provenance stamp - marks this artifact as tool-created, same as
# `artifact new`, so `provenance check` no longer false-flags filer-created artifacts.
_STAMP = "> **Created-by:** sdlc-studio file\n"


def _stamp(f: dict) -> str:
    """The provenance stamp plus the typed authorship of record. `Raised-by` is resolved from
    `--author` at creation (defaulting to the invoking agent), so a filed artefact never opens
    failing the schema-v3 authorship rule."""
    return _STAMP + f"> **Raised-by:** {f.get('_raised_by') or sdlc_md.DEFAULT_AGENT_AUTHOR}\n"


def _rev_author(f: dict) -> str:
    """The Revision History Author cell: the name of the authorship of record, resolved from
    `--author` (and defaulting to the invoking agent). The filer records who raised the
    artefact, never a hardcoded literal."""
    return sdlc_md.authorship_name(f.get("_raised_by") or f.get("author"))


def rev_row(today: str, f: dict, change: str) -> str:
    """The opening Revision History row an artefact is born with - the one writer both creation
    paths share. Built through `join_row`, so a `|` in an author's name is escaped rather than
    silently opening a fourth column and swallowing the Change cell."""
    return sdlc_md.join_row([today, _rev_author(f), change])


def _md_safe(text) -> str:
    """Backtick-wrap bare snake_case/dunder identifier tokens in free prose so an unbackticked
    `_` is not read as markdown emphasis (MD037/MD049/MD050) - the filer must not mint
    lint-red artefacts. Only text OUTSIDE existing code spans is touched, so an
    already-backticked token is left alone. (Reversed-link shapes like `)[1]` are a rarer
    residual, noted in the CR.)"""
    parts = str(text).split("`")
    for i in range(0, len(parts), 2):  # even indices are outside backtick spans
        parts[i] = re.sub(r"(?<![\w`])([A-Za-z_][\w.]*_[\w().\[\]]*)", r"`\1`", parts[i])
    return "`".join(parts)


# The `**Field:**` declaration shape at either place `extract_field` anchors a field: a line
# start (optional blockquote `>`) OR an inline ` · `-separated run. Both the anchor tokens AND
# the whitespace class are mirrored, so the escape covers exactly what `extract_field` can read
# - no wider (a `**bold:**` mid-sentence, anchored to neither, is left untouched), no narrower.
# `[^\S\n]` is all of `\s` (NBSP, thin space, form feed, ...) EXCEPT newline, matching
# `extract_field`'s `\s*` on a single line while never crossing a line in a multiline body (a
# `·\n**Field:**` run is caught by the line-start branch instead, since the field opens a line).
_META_DECL_RE = re.compile(r"(?m)((?:^>?|·)[^\S\n]*)\*\*([^*\n]+:)\*\*")


def _prose_safe(text) -> str:
    """`_md_safe`, plus a guard against a multi-line prose field inventing a metadata line.

    A prose field (summary/steps/fix/impact/recommendation) is multi-line by design, so it is
    not refused. But a line inside it shaped like `> **Waived:** yes` would be read by
    `extract_field` (and a human) as a provenance stamp the head never declared. The bold
    delimiters of such a line are escaped, so it renders as literal `**Field:**` text and no
    longer parses as a declaration; the author's words are kept verbatim, nothing is dropped."""
    return _META_DECL_RE.sub(r"\1\\*\\*\2\\*\\*", _md_safe(text))


def _affects_line(f: dict) -> str:
    """The `Affects` metadata line: the files this unit will touch, as the planner reads them
    (`sdlc_md.affects_files` parses this exact field). Written only when declared - an absent
    field is honestly absent, and for a bug or a CR the creator refuses to get that far."""
    val = str(f.get("affects") or "").strip().strip(",")
    return f"> **Affects:** {val}\n" if val else ""


def _mutation_link_lines(f: dict) -> str:
    """The `Mutation-run` / `Mutation-target` metadata lines: which mutation run raised this
    finding, and which file the mutant sat in.

    A survivor is a hypothesis until somebody files it, and nothing on disk connected the two
    before: RUN-01KY03GS raised three survivors, two became bugs, and the link had to be
    reconstructed from memory. It is cheap to record at filing time and impossible to
    reconstruct afterwards, so it is recorded here or not at all."""
    run = str(f.get("mutation_run") or "").strip()
    if not run:
        return ""
    target = str(f.get("mutation_target") or "").strip()
    return (f"> **Mutation-run:** {run}\n"
            + (f"> **Mutation-target:** {target}\n" if target else ""))


def check_mutation_run(repo_root: Path | str, fields: dict) -> dict:
    """Resolve a `mutation_run` attribution before anything is minted, or refuse.

    Returns the fields with `mutation_target` filled in from the run's own surface when the
    caller did not name one. A run the series does not hold is REFUSED by name: an artefact
    stamped with an unresolvable run id claims a provenance nobody can check, and yield counted
    from it would be counted against a run that never happened."""
    run = str(fields.get("mutation_run") or "").strip()
    if not run:
        return fields
    sdlc_md.require_single_line("mutation_run", run)
    import mutation  # noqa: PLC0415 - local: the filer reads the series, it does not own it
    row = mutation.series_row(repo_root, run)
    if row is None:
        raise ValueError(
            f"no mutation run {run} in {mutation.series_path(repo_root)} - refusing to stamp a "
            "finding with a run nobody recorded. Run `mutation.py run` first, or file without "
            "--mutation-run; a yield counted from an unresolvable id is counted against a run "
            "that never happened")
    target = str(fields.get("mutation_target") or "").strip()
    if not target:
        target = ", ".join(str(t) for t in (row.get("targets") or []))
    sdlc_md.require_single_line("mutation_target", target)
    return {**fields, "mutation_run": run, "mutation_target": target}


def _size_line(f: dict) -> str:
    """The `Size` metadata line: the T-shirt size (S/M/L/XL) a CR/RFC carries in place of points.
    Canonicalised through `sdlc_md.check_size` (a `--size m` becomes `M`) and written only when
    declared - a preview render for the grooming gate leaves it absent so the gate can see it is
    missing, exactly as `_affects_line` does."""
    val = str(f.get("size") or "").strip()
    return f"> **Size:** {sdlc_md.check_size(val)}\n" if val else ""


def _decision_question(title: str, options) -> str:
    """The D1 decision row, written from the finding's own options.

    The generator used to emit one fixed sentence - `Act on this finding or keep status quo`
    - into every RFC it filed, while the real options sat two lines above it in Design
    Options. A row that says nothing gets closed by nobody, so accepted RFCs accumulated an
    unanswered decision each; the accept gate now refuses that, which makes the generator
    that manufactures it the thing to fix.

    With two or more options the row states the choice between them. With one, or none, it
    poses the finding's own subject rather than a generic question - a finding always has a
    subject, so there is never a reason to fall back to boilerplate.
    """
    named = [str(o).strip() for o in (options or []) if str(o).strip()]
    subject = (title or "").strip().rstrip(".?") or "this finding"
    if len(named) >= 2:
        return f"Choose between: {', '.join(named[:-1])} or {named[-1]}"
    if len(named) == 1:
        return f"Whether to {named[0]}"
    return f"Whether to {subject[0].lower() + subject[1:] if subject else subject}"


def _render(type_: str, disp_id: str, title: str, today: str, f: dict,
            status: str | None = None) -> str:
    """A structured artifact body (required sections populated). `status` overrides the
    per-type create status (schema v3 files findings into `inbox`); None keeps the default."""
    f = {**f, **{k: _prose_safe(f[k]) for k in ("summary", "steps", "fix", "recommendation", "impact")
                 if isinstance(f.get(k), str)}}
    if isinstance(f.get("acs"), list):
        f = {**f, "acs": [_md_safe(a) for a in f["acs"]]}
    if isinstance(f.get("options"), list):
        f = {**f, "options": [_md_safe(o) for o in f["options"]]}
    if type_ == "bug":
        # Points are the job SIZE of the fix (Severity is its urgency - a different axis, and the
        # one a bug has always carried). Demanded, not optional: the sprint plan refuses a unit
        # nobody sized, so a bug filed without one is work that cannot be planned. It sizes the
        # unit in the plan instead of the planner falling back to a flat floor.
        points = f"> **Points:** {f['points']}\n" if f.get("points") is not None else ""
        return (f"# {disp_id}: {title}\n\n"
                f"> **Status:** {status or 'Open'}\n> **Severity:** {f['severity']}\n"
                f"{points}{_affects_line(f)}{_mutation_link_lines(f)}"
                f"> **Created:** {today}\n{_stamp(f)}\n"
                f"## Summary\n\n{f['summary']}\n\n"
                f"## Steps to Reproduce\n\n{f['steps']}\n\n"
                f"## Proposed Fix\n\n{f['fix']}\n\n"
                f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"{rev_row(today, f, 'Filed')}\n")
    if type_ == "cr":
        # normalise: an AC supplied with its own leading checkbox ('- [ ] x',
        # '-[x] y') is not doubled into '- [ ] - [ ] x'
        stripped = (re.sub(r"^\s*-\s*\[[ xX]\]\s*", "", a) for a in f["acs"])
        acs = "\n".join(f"- [ ] {a}" for a in stripped)
        return (f"# {disp_id}: {title}\n\n"
                f"> **Status:** {status or 'Proposed'}\n> **Priority:** {f['priority']}\n"
                f"> **Type:** {f['ctype']}\n{_size_line(f)}{_affects_line(f)}"
                f"{_mutation_link_lines(f)}"
                f"> **Date:** {today}\n{_stamp(f)}\n"
                f"## Summary\n\n{f['summary']}\n\n"
                f"## Impact\n\n{f['impact']}\n\n"
                f"## Acceptance Criteria\n\n{acs}\n\n"
                f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"{rev_row(today, f, 'Raised')}\n")
    options = "\n".join(f"- **{o}**" for o in f["options"])
    decision = _decision_question(title, f["options"])
    return (f"# {disp_id}: {title}\n\n"
            f"> **Status:** {status or 'Draft'}\n{_size_line(f)}{_affects_line(f)}"
            f"{_mutation_link_lines(f)}"
            f"> **Date:** {today}\n{_stamp(f)}\n"
            f"## Summary\n\n{f['summary']}\n\n"
            f"## Design Options\n\n{options}\n\n"
            f"## Recommendation\n\n{f.get('recommendation', 'TBD - pending decision.')}\n\n"
            f"## Open Decisions\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
            f"| D1 | {decision} | Open |\n\n"
            f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
            f"{rev_row(today, f, 'Filed')}\n")


def append_index_row(repo_root: Path | str, type_: str, row_line: str) -> bool:
    """Insert a pre-built data-table row into a type's `_index.md` and recompute its summary
    counts (reusing reconcile). Locates the DATA table by its ID-column header so the row
    never lands in the Summary table. Returns False if the index is absent. Shared by the
    finding filer and the general `artifact new`."""
    root = Path(repo_root)
    index_path = root / sdlc_md.ARTIFACT_TYPES[type_][0] / "_index.md"
    if not index_path.exists():
        return False
    lines = index_path.read_text(encoding="utf-8").splitlines()
    hdr = sdlc_md.find_data_header(lines)
    if hdr is None:
        return False
    data_header = hdr[0]
    # Bound the scan to THIS table's contiguous rows (header, separator, then rows until the
    # first non-table line). Scanning to EOF let a later link-first view/breakdown table
    # capture the appended row, so it escaped the master table.
    end = data_header + 2  # past header + separator
    while end < len(lines) and lines[end].lstrip().startswith("|"):
        end += 1
    rows_after = [j for j in range(data_header + 2, end)
                  if lines[j].strip().startswith("| [")]
    pos = (max(rows_after) + 1) if rows_after else data_header + 2
    lines.insert(pos, row_line)
    sdlc_md.atomic_write(index_path, "\n".join(lines) + "\n")
    reconcile.apply_type(type_, root)  # recompute summary counts (tested)
    return True


def duplicate_candidates(repo_root: Path | str, title: str, fields: dict, *, sim: float = 0.5) -> list[dict]:
    """Open artefacts a NEW finding substantially overlaps: a shared Affects file AND similar
    wording (title + summary). The cheapest triage lens - a duplicate is cheapest to catch at
    filing, where the author has the most context. It WARNS with the candidate named; it never
    refuses, because a genuine near-miss is common and only the author can tell them apart. Empty
    when the finding declares no Affects (nothing structural to compare) - it states what it reads.

    Reuses the backlog-triage overlap primitives, so the filing-time lens and the plan-time lens
    agree by construction."""
    # Advisory-only: it must NEVER break the filer. Any failure (a missing sibling, an unreadable
    # or non-UTF-8 artefact anywhere in the backlog) degrades to "no warning", exactly as the two
    # other consumers of the full-backlog scan (sprint._batch_triage, status advisory) do.
    try:
        import backlog_triage as bt
        root = Path(repo_root)
        affects_line = f"> **Affects:** {fields.get('affects') or ''}"
        new_affects = {a for a in (bt._affect_key(root, a)
                                   for a in sdlc_md.affects_files(affects_line)) if a}
        if not new_affects:
            return []
        new_tokens = bt._tokens(title, str(fields.get("summary") or ""))
        out: list[dict] = []
        for u in bt.load_backlog(root):
            shared = u["affects"] & new_affects
            if not shared:
                continue
            j = bt._jaccard(u["tokens"], new_tokens)
            if j >= sim:
                out.append({"id": u["id"], "type": u["type"], "shared": sorted(shared),
                            "similarity": round(j, 2)})
        return sorted(out, key=lambda c: (-c["similarity"], c["id"]))
    except Exception as exc:  # noqa: BLE001 - a duplicate warning must never fail a filing
        sdlc_md.debug("file_finding.duplicate_candidates", exc)
        return []


def file_finding(repo_root: Path | str, type_: str, title: str, fields: dict,
                 dry_run: bool = False) -> dict:
    """Allocate an ID, write a structured artifact, append its index row, recompute
    counts. Returns {id, path}, plus `duplicate_warnings` naming any open artefact the finding
    overlaps (a warning, never a refusal). Raises ValueError on a missing required field."""
    if type_ not in TYPES:
        raise ValueError(f"unknown type {type_!r} (expected bug|cr|rfc)")
    spec = TYPES[type_]
    missing = [k for k in spec["required"] if not fields.get(k)]
    if missing:
        raise ValueError(f"{type_} finding missing required field(s): {', '.join(missing)} "
                         "- the filer refuses to write a hollow artifact")
    # Refuse a field that would break out of its metadata line, index cell or bullet before
    # anything is allocated or written - the same guard the general creator runs, from the
    # same authority, so neither path is an escape hatch for the other.
    sdlc_md.check_creator_fields({**fields, "title": title})
    # ... and refuse a CR/bug criterion carrying a command-shaped `Verify:` - a check nobody runs.
    check_prose_acs(type_, fields)
    root = Path(repo_root)
    today = fields.get("date") or date.today().isoformat()
    fields = {**fields, "date": today}
    # ... and refuse a declared `Affects` that resolves to nothing, before an id is allocated,
    # from the ONE seam every writer shares - naming the closest basename match where there is one.
    check_affects_resolvable(root, fields.get("affects"), type_)
    # ... and refuse an attribution to a mutation run the series does not hold, before an id is
    # allocated: a finding stamped with an unresolvable run claims a provenance nobody can check.
    fields = check_mutation_run(root, fields)
    # ... and refuse an artefact the PLANNER would then refuse to plan: the body about to be
    # written is judged by `sprint.breakdown` itself. A preview id is enough - the grooming
    # fields the gate reads are in the metadata block, which does not depend on the id.
    check_groomed(root, type_, _render(type_, "PREVIEW", title, today, fields))
    # Parent link (spawning a child under an RFC/CR): the parent must RESOLVE before
    # anything is minted - a child born pointing at nothing is the asymmetry class the
    # bidirectional wiring exists to abolish.
    parent = (fields.get("parent") or "").strip()
    parent_path = None
    if parent:
        found = sdlc_md.find_by_id(root, parent)
        if not found:
            raise ValueError(f"--parent {parent} does not resolve to any artefact - "
                             f"a child is never minted against a missing parent")
        parent_path = found[0]
        parent = sdlc_md.norm_id(parent)
    # The cheapest triage lens, run BEFORE the id is minted: does this finding overlap an artefact
    # already open? A warning attached to the result, never a refusal.
    warnings = duplicate_candidates(root, title, fields)
    if dry_run:
        result = _file_finding_locked(root, type_, spec, title, fields, today, dry_run=True)
    else:
        # CR0183/BG0076: allocate id + write file + append row under the advisory cross-process
        # lock, so concurrent filers (multi-agent waves) cannot mint the same v2 id or clobber a
        # shared index row. Best-effort - a no-op on non-POSIX, exactly like `artifact new`.
        with sdlc_md.allocation_lock(root):
            result = _file_finding_locked(root, type_, spec, title, fields, today, dry_run=False)
            if parent_path is not None and result.get("path"):
                # wire BOTH directions inside the same lock as the mint, so two
                # concurrent same-parent spawns cannot lose an update on the
                # parent's Decomposed-into read-modify-write
                sdlc_md.insert_after_status(Path(result["path"]), f"> **Parent:** {parent}")
                existing = sdlc_md.decomposed_ids(parent_path.read_text(encoding="utf-8"))
                child_id = sdlc_md.norm_id(result["id"])
                if child_id not in existing:
                    sdlc_md.write_decomposed(parent_path, [*existing, child_id])
    if warnings:
        result["duplicate_warnings"] = warnings
    return result


def _file_finding_locked(root: Path, type_: str, spec: dict, title: str, fields: dict,
                         today: str, dry_run: bool) -> dict:
    if sdlc_md.is_schema_v3(root):
        # era-aware: a v3 project's findings mint the same collision-checked ULID form as
        # `artifact new` - sequential numbers here would race and shadow live ULID aliases.
        file_id = disp_id = sdlc_md.mint_v3_id(root, type_)
    else:
        n = _next_number(root, type_)
        file_id = f"{spec['prefix']}{n:04d}"
        disp_id = spec["disp"].format(n=n)
    slug = _slug(title)
    rel_dir = sdlc_md.ARTIFACT_TYPES[type_][0]
    path = root / rel_dir / f"{file_id}-{slug}.md"
    if path.exists():
        raise FileExistsError(path)
    # schema v3: findings file into `inbox` (a different seat then triages them into the
    # workflow); dormant under v2, where the per-type create status is kept.
    create_status = (sdlc_md.INBOX_STATUS
                     if type_ in sdlc_md.FINDING_TYPES and sdlc_md.is_schema_v3(root)
                     else spec["status"])
    # Triage noise controls (v3 only, dormant on v2): a Low-severity finding folds into a
    # themed consolidation CR instead of minting its own artefact; the session cap refuses a
    # flood loudly. `severity` (bug) or `priority` (cr) carries the Low signal.
    sev = fields.get("severity") or fields.get("priority")
    if triage_noise.should_consolidate(root, sev):
        if dry_run:
            return {"id": None, "file_id": None, "path": None,
                    "consolidated": True, "dry_run": True}
        res = triage_noise.consolidate_low_finding(root, type_, title, fields, today)
        res.setdefault("indexed", True)
        return res
    if dry_run:  # preview: write nothing
        indexed = (root / rel_dir / "_index.md").exists()
        return {"id": disp_id, "file_id": file_id, "path": str(path),
                "indexed": indexed, "dry_run": True}
    triage_noise.enforce_session_cap(root)  # refuse the N+1th individual finding loudly (v3)
    raised_by = sdlc_md.authorship_value(fields.get("author"), root)
    # The index's Author column and the Revision History row both take the resolved author's
    # NAME (the typed triple is the `Raised-by` field's job), so an unattributed filing still
    # names whoever raised it - the invoking agent - rather than a literal or a blank cell.
    fields = {**fields, "_raised_by": raised_by, "author": sdlc_md.authorship_name(raised_by)}
    sdlc_md.atomic_write(path, _render(type_, disp_id, title, today, fields, create_status))
    triage_noise.record_creation(root)  # count this minted finding against the session budget
    # One shared header-driven row builder for both create paths: read the index's
    # own columns and fill by name, identical to `artifact new`.
    indexed = False
    idx = root / rel_dir / "_index.md"
    if idx.exists():
        hdr = sdlc_md.find_data_header(idx.read_text(encoding="utf-8").splitlines())
        if hdr:
            link = f"[{disp_id}]({file_id}-{slug}.md)"
            row = sdlc_md.row_from_header(hdr[1], link, title, create_status, fields)
            indexed = append_index_row(root, type_, row)
    return {"id": disp_id, "file_id": file_id, "path": str(path), "indexed": indexed}


def cmd_file(args: argparse.Namespace) -> int:
    flags = {"severity": args.severity, "priority": args.priority, "ctype": args.ctype,
             "summary": args.summary, "steps": args.steps, "fix": args.fix,
             "impact": args.impact, "points": args.points, "size": args.size,
             "affects": args.affects,
             "author": args.author, "recommendation": args.recommendation,
             "parent": getattr(args, "parent", None),
             "mutation_run": getattr(args, "mutation_run", None),
             "mutation_target": getattr(args, "mutation_target", None)}
    flags = {k: v for k, v in flags.items() if v is not None}
    if args.ac:
        flags["acs"] = args.ac
    if args.option:
        flags["options"] = args.option
    if args.title:
        flags["title"] = args.title
    # The values that DID cross a shell, and only those: a `$(` that arrived intact through the
    # file is data, and warning about it would train the reader to ignore the warning.
    report_shell_hazards(flags)
    try:
        from_file = load_fields_file(args.fields_file) if args.fields_file else {}
    except ValueError as exc:
        print(f"file refused: {exc}", file=sys.stderr)
        return 1
    fields = {**from_file, **flags}          # an explicit flag wins over the document
    title = fields.pop("title", None)
    if not title:
        print("file refused: no title - pass --title, or a \"title\" key in the "
              "--fields-file document", file=sys.stderr)
        return 1
    try:
        result = file_finding(args.root, args.type, title, fields, dry_run=args.dry_run)
    except (ValueError, FileExistsError) as exc:
        # a refusal is a message, not a traceback - the reason and the fix, on stderr
        # (exit 1: the same code the top-level guard has always given refusals)
        print(f"file refused: {exc}", file=sys.stderr)
        return 1
    verb = "would file" if result.get("dry_run") else "filed"
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"{verb} {result['id']} -> {result['path']}")
        for c in result.get("duplicate_warnings", []):
            print(f"  warning: possible duplicate of {c['id']} ({c['type']}): shares "
                  f"{', '.join(c['shared'])}, {int(c['similarity'] * 100)}% similar wording - "
                  f"merge or confirm they are distinct")
    return 0


def cmd_rebuild(args: argparse.Namespace) -> int:
    res = reconcile.apply_type(args.type, Path(args.root))
    print(f"rebuilt {args.type} index counts (counts_updated={res['counts_updated']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic Bug/CR/RFC finding filer.")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("file", help="File one structured artifact from a finding.")
    f.add_argument("--type", required=True, choices=("bug", "cr", "rfc"))
    f.add_argument("--fields-file", dest="fields_file", metavar="FINDING.json",
                   help="THE RECOMMENDED PATH. A JSON object of the same field names, read "
                        "straight off disk so no value ever crosses a shell. Use it for any "
                        "finding whose prose contains commands - backticks and `$(` are command "
                        "substitution inside a shell argument, so on the flag path the steps are "
                        "EXECUTED rather than stored (a filing once ran `git commit -a` against "
                        "the live repository). A file is also re-runnable, committable as "
                        "evidence and diffable. An explicit flag overrides the document")
    f.add_argument("--title", help="required unless the --fields-file document carries a title")
    f.add_argument("--summary")
    f.add_argument("--severity", help="bug severity")
    f.add_argument("--priority", help="cr/rfc priority")
    f.add_argument("--ctype", help="cr type (Improvement/Feature/Bug)")
    f.add_argument("--steps", help="bug steps to reproduce")
    f.add_argument("--fix", help="bug proposed fix")
    f.add_argument("--impact", help="cr: who this affects and what breaks (required for a cr)")
    # Deliberately NOT an argparse `choices` list: argparse would exit 2 with a bare "invalid
    # choice", and the whole point of refusing a 7 is to explain WHY the scale has no 7. The
    # value is checked by `sdlc_md.check_points` - the one definition both creators share.
    f.add_argument("--points",
                   help="job SIZE of a DELIVERY unit (a bug), on the modified Fibonacci scale "
                        f"({', '.join(str(p) for p in sdlc_md.POINTS_SCALE)}) - RELATIVE to "
                        "units already delivered, not a prediction of time. A bug's Severity is "
                        "its urgency, a different axis. Required for a bug: `sprint plan` refuses "
                        "a unit nobody sized. A value off the scale is refused, never rounded; "
                        "above 8, split the unit. A CR is a REQUEST - it takes --size, not --points.")
    # A CR/RFC is a container/request, sized coarsely BEFORE decomposition: a T-shirt Size, not
    # story points (which belong on the measured delivery unit). Not an argparse `choices` list,
    # for the same reason --points is not: a bare "invalid choice" teaches nothing, and the value
    # is checked by `sdlc_md.check_size` so the refusal can explain why a request is not pointed.
    f.add_argument("--size",
                   help="T-shirt size of a REQUEST/container (a cr, or optionally an rfc): "
                        f"{' | '.join(sdlc_md.SIZE_SCALE)}. Sized coarsely before the request is "
                        "decomposed into stories - a CR is not a unit of work until it is broken "
                        "down. Required for a cr: `sprint plan` refuses a request nobody sized. "
                        "Story points belong on the delivery unit (a story/bug), not on the request.")
    f.add_argument("--affects",
                   help="comma-separated files this unit will touch, written as the `Affects` "
                        "metadata line. Required for a bug and a cr: `sprint plan` refuses a "
                        "unit that names no files - it cannot size one, nor see two units "
                        "colliding on the same file. Optional on an rfc (not a sprint unit)")
    f.add_argument("--ac", action="append", help="cr acceptance criterion (repeatable)")
    f.add_argument("--option", action="append", help="rfc design option (repeatable)")
    f.add_argument("--recommendation", help="rfc recommendation")
    f.add_argument("--parent", help="spawn this finding as a child of an existing RFC/CR: the parent must resolve, and BOTH link directions are wired at mint")
    f.add_argument("--mutation-run", dest="mutation_run", metavar="MRUNxxx",
                   help="the mutation run that raised this finding, as recorded in "
                        "sdlc-studio/.local/mutation-series.jsonl. The run's yield is counted "
                        "in artefacts filed against it, so a survivor only becomes yield here. "
                        "A run the series does not hold is refused, never stamped")
    f.add_argument("--mutation-target", dest="mutation_target",
                   help="the file the surviving mutant sat in (default: the run's own targets)")
    f.add_argument("--author",
                   help="authorship of record, stamped as `Raised-by`: 'Name; type; version' "
                        "(type is human|persona|agent) or a bare name; defaults to the "
                        "invoking agent (SDLC_AUTHOR when set)")
    f.add_argument("--root", default=".")
    f.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview; write nothing")
    f.add_argument("--format", choices=("text", "json"), default="text")
    f.set_defaults(func=cmd_file)
    r = sub.add_parser("rebuild", help="Recompute a type's index summary counts.")
    r.add_argument("--type", required=True, choices=("bug", "cr", "rfc", "story", "epic"))
    r.add_argument("--root", default=".")
    r.set_defaults(func=cmd_rebuild)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
