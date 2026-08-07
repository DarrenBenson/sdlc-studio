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
from pathlib import Path, PurePosixPath

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
    """Refuse, BEFORE any id is allocated or any byte written, a REQUEST's acceptance criterion
    carrying a command-shaped `Verify:`. Called from BOTH creation paths (the finding filer and
    `artifact new` / `artifact batch`), so neither is an escape hatch for the other.

    Stories and BUGS are untouched: both are delivery units whose `Verify:` lines are the real,
    executed thing. This used to refuse a bug's, which left a bug with no executable closure
    path at all - the criteria floor demanded criteria and this refused the one form that could
    prove them. WHICH types is `sdlc_md.executes_verifiers`, the same authority the runner and
    the validator read, so the three cannot drift into contradicting each other again."""
    if type_ not in sdlc_md.FINDING_TYPES or sdlc_md.executes_verifiers(type_):
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
    "Affects": ('--affects "path/to/file.py, path/to/test_file.py"  (where the FIX lands, not '
                'where the evidence was read - and a fix arrives with a test)'),
    "Points": (f"--points {'|'.join(str(p) for p in sdlc_md.POINTS_SCALE)}  (the job SIZE of the "
               f"work, RELATIVE to units you have already delivered - a bug's Severity is its "
               f"urgency, a different axis)"),
    "Size": (f"--size {'|'.join(sdlc_md.SIZE_SCALE)}  (the T-shirt size of this REQUEST, sized "
             f"coarsely before it is decomposed into stories - story points belong on the "
             f"delivery unit, not on the request)"),
}


def grooming_gaps(repo_root: Path | str, type_: str, text: str) -> tuple[list[str], bool]:
    """What `sprint plan`'s breakdown gate would find missing on this artefact-to-be that the
    CREATOR could have supplied, and whether the gate is blocking.

    Judged by `sprint.breakdown` itself - the ONE definition of groomed - then narrowed to the
    creation contract by dropping the criteria gaps, which are grooming debt rather than a
    creation defect. Over the exact body
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
    if not bd["ungroomed"]:
        return [], bool(bd["blocking"])
    row = bd["ungroomed"][0]
    # CREATION is not PLANNING, and criteria are a GROOMING concern by definition - they are
    # authored after the finding exists, which is why grooming is unpriced work in this model.
    # This module writes what the evidence supports and no more: a criterion derived from the
    # finding's own prose, or, when the evidence is too thin even for that, a stated absence.
    # The planner now (correctly) refuses both shapes. Borrowing that verdict wholesale would
    # make the filer refuse every finding it is capable of writing - including the ones filed
    # mid-review, where capture matters more than polish and where losing the finding is the
    # worse failure. So the creation gate keeps its original contract: the FOOTPRINT (Affects,
    # Points), which the author does know at filing time. The criteria debt is real, it is owed
    # at PLAN time, and `sprint breakdown` is where it is now collected.
    # WHETHER to filter is decided by the reason CODE; WHICH gaps get dropped is still a prose
    # match on a message `sprint` owns. That coupling is real and is stated rather than claimed
    # away: rewording `sprint._AC_MISS` breaks this loudly (44 tests here go red), never
    # silently, which is the property that makes it tolerable rather than a second authority.
    # A NON-criteria gap is still refused here.
    missing = list(row["missing"])
    if row.get("ac_why"):
        missing = [m for m in missing if not m.startswith("Acceptance Criteria")]
    if not missing:
        return [], bool(bd["blocking"])
    return missing, bool(bd["blocking"])


def check_groomed(repo_root: Path | str, type_: str, text: str) -> None:
    """Refuse - BEFORE an id is allocated or a byte written - an artefact `sprint plan` would
    then refuse to PLAN ON ITS FOOTPRINT. Called from BOTH creation paths (the finding filer
    and `artifact new` / `artifact batch`), so neither can mint a unit whose Affects or size
    the other end of the pipeline rejects.

    CRITERIA are deliberately outside this gate. A creator writes what the evidence
    supports and criteria are authored later, at grooming, so `sprint breakdown` is where the
    criteria debt is collected - see `grooming_gaps`.

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


# --- The understated footprint: a source file declared without its existing test ------------
#
# A declared `Affects` is where the FIX LANDS, not where the evidence was READ. A filer who names
# only the file the defect was observed in declares a footprint smaller than the change, and this
# repository's own doctrine says a fix arrives with a test - so a unit touching a source file whose
# test already exists will touch that test too. Nothing refused an understated `Affects`, so it
# caused silently exactly the three harms a FICTIONAL one is refused for: the plan's collision
# analysis mis-groups the unit, the engagement floor under-reads it, and gate's changed-surface
# pass misreports it - all while the filing exits 0. One audit filed 54 artefacts this way and not
# one named a test file.
#
# The check NAMES the path rather than inventing one: it fires only where the companion test
# EXISTS on disk, so the author is never sent to a file the tool made up. A warning, not a
# refusal - the finding in hand is worth more than a perfect footprint, and a refusal here would
# lose it. What must not happen is silence.

#: Directories a test lives in relative to its source, by the conventions the suites in this family
#: use, most conventional first. `""` is the source's own directory (`foo.py` / `test_foo.py`);
#: `../tests` is the package-sibling suite (`scripts/lib/sdlc_md.py` is tested by
#: `scripts/tests/test_sdlc_md.py`), which the source's own subtree never reaches.
_TEST_DIRS = ("tests", "", "test", "__tests__", "spec", "../tests", "../test", "../__tests__")

#: (source suffix, companion basename template) - the test-naming conventions worth deriving. A
#: language absent from this table simply yields no candidate, which is silence, not a wrong guess.
_TEST_NAMES = {
    ".py": ("test_{stem}.py",),
    ".go": ("{stem}_test.go",),
    ".js": ("{stem}.test.js", "{stem}.spec.js"),
    ".jsx": ("{stem}.test.jsx", "{stem}.spec.jsx"),
    ".ts": ("{stem}.test.ts", "{stem}.spec.ts"),
    ".tsx": ("{stem}.test.tsx", "{stem}.spec.tsx"),
    ".mjs": ("{stem}.test.mjs", "{stem}.spec.mjs"),
}


def is_test_path(path: str) -> bool:
    """Test-shaped by the conventions this family's suites use: `test_x.py`, `x_test.go`,
    `x.test.ts`, `x.spec.ts`. Matches `gate._is_test_path`, so 'is a test' means one thing."""
    stem = PurePosixPath(str(path).replace("\\", "/")).stem
    return (stem.startswith("test_") or stem.endswith("_test")
            or stem.endswith(".test") or stem.endswith(".spec"))


def companion_test_candidates(path: str) -> list[str]:
    """The paths a test for `path` would sit at by convention, most conventional first. Empty for
    a test file, a file with no extension this family tests, or a path that is not a file."""
    p = PurePosixPath(str(path).replace("\\", "/").rstrip("/"))
    if not p.name or is_test_path(p.name):
        return []
    names = _TEST_NAMES.get(p.suffix)
    if not names:
        return []
    import posixpath  # noqa: PLC0415 - local: only this derivation normalises a `..` segment
    out: list[str] = []
    for d in _TEST_DIRS:
        base = posixpath.normpath(str(p.parent / d)) if d else str(p.parent)
        if base.startswith(".."):
            continue  # a source at the repo root has no parent-sibling suite
        for name in names:
            cand = posixpath.normpath(posixpath.join(base, name.format(stem=p.stem)))
            if cand not in out:
                out.append(cand)
    return out


def missing_companion_tests(repo_root: Path | str, affects_value: str,
                            type_: str | None = None) -> list[tuple[str, str]]:
    """`(source, companion_test)` for each declared source file whose test EXISTS on disk and which
    the declared `Affects` does not name. Read-only; the single seam behind the filing warning.

    Empty when the footprint already names a test file for a source (the fix is declared), when no
    companion exists (nothing to name), or for a type whose `Affects` is not a sprint footprint -
    an RFC's declared files are the OUTPUT of its decision, exactly as the resolvable check
    skips it."""
    if type_ is not None and type_ not in _AFFECTS_CHECKED_TYPES:
        return []
    declared = declared_affects(affects_value)
    if not declared:
        return []
    import posixpath  # noqa: PLC0415 - local: comparing two spellings of one path
    # normpath, never lstrip("./"): lstrip takes a SET of characters, so it would eat the leading
    # dot of a dot-directory (`.claude/...` -> `claude/...`) as readily as a `./` prefix.
    have = {posixpath.normpath(str(p).replace("\\", "/")) for p in declared}
    root = Path(repo_root)
    out: list[tuple[str, str]] = []
    for src in declared:
        if is_test_path(src):
            continue
        for cand in companion_test_candidates(src):
            if cand in have:
                break  # the footprint already declares a test beside this source
            if sdlc_md.resolve_affects(root, cand) is not None:
                out.append((src, cand))
                break
    return out


def complete_affects(repo_root: Path | str, affects_value: str,
                     type_: str | None = None) -> tuple[str, list[tuple[str, str]]]:
    """The declared `Affects` with each source file's EXISTING companion test folded in, plus the
    `(source, test)` pairs that were added. Read-only over the tree; nothing is invented, because
    `missing_companion_tests` fires only where the test is already on disk.

    Warning about the gap was not enough. The message printed, the artefact was written with the
    understated footprint anyway, and the plan then read it - so the harm the warning described
    happened every time it was shown. The tool holds the exact path at the moment it complains, so
    it writes it: a fix lands in the source AND its test, and a footprint naming one is short by
    the other."""
    missing = missing_companion_tests(repo_root, affects_value, type_)
    if not missing:
        return str(affects_value or ""), []
    declared = declared_affects(affects_value)
    return ", ".join([*declared, *(t for _s, t in missing)]), missing


def report_completed_affects(added: list[tuple[str, str]], label: str = "") -> None:
    """Say what was added to the footprint and why. Not silent: an author who did not mean the
    fix to touch the test must be able to see the tool widened their declaration and edit it."""
    if not added:
        return
    where = f"{label}: " if label else ""
    lines = "\n".join(f"    {src} is tested by {cand} - added to Affects"
                      for src, cand in added)
    print(f"note: {where}the declared Affects named source files without their existing tests, so "
          f"the footprint was understated - a fix lands in both.\n{lines}\n"
          f"  Why it matters: an understated footprint mis-groups the unit in the plan's "
          f"collision analysis, under-reads it in the engagement floor and misreports it in "
          f"gate's changed-surface pass.\n"
          f"  Affects is where the FIX LANDS, not where the evidence was read. Edit the artefact "
          f"if the fix genuinely will not touch the test.", file=sys.stderr)


def warn_missing_companion_tests(repo_root: Path | str, affects_value: str,
                                 type_: str | None = None, label: str = "") -> list[tuple[str, str]]:
    """Report an understated footprint without changing it, and return the pairs reported. Kept as
    the read-only half for callers that inspect a footprint they do not own (`complete_affects` is
    what the FILER uses, because a filer can fix what it finds)."""
    missing = missing_companion_tests(repo_root, affects_value, type_)
    if not missing:
        return []
    where = f"{label}: " if label else ""
    lines = "\n".join(f"    {src} has a test at {cand}, which Affects does not name"
                      for src, cand in missing)
    print(f"warning: {where}the declared Affects names source files without their existing "
          f"tests - a fix lands in both, so the footprint is understated.\n{lines}\n"
          f"  Affects is where the FIX LANDS, not where the evidence was read. Add the test "
          f"path(s) above if the fix will touch them.", file=sys.stderr)
    return missing


# --- The derived acceptance criterion: a filed finding carries its own contract -------------
#
# A filed bug carried Steps to Reproduce and a Proposed Fix and NOTHING a lane could deliver
# against. Two costs, both measured on this repository's own backlog: whoever picked the unit up
# had to infer the contract from a summary, and the engagement floor read the unit as unplanned
# and refused the batch that held it.
#
# So a criterion is DERIVED from the finding's own evidence at filing time, when the author's
# context is at its richest. Derived, never invented: the criterion quotes the words the author
# wrote, and where the evidence cannot support one that is STATED in the artefact rather than
# scaffolded. A `{{placeholder}}` reads like content to everything downstream, and a checkbox
# nobody derived is worse still - it would satisfy the engagement floor on a finding that planned
# nothing, which is the exact failure this exists to end. The thin note is therefore a PARAGRAPH:
# `sdlc_md.count_acs` counts checkboxes and AC headings, so a stated absence stays an absence.

#: How many words of a field it takes to state what 'fixed' would look like. Below this the field
#: is a token ('r', 'f', 'see above'), which yields a criterion that only restates the token.
MIN_EVIDENCE_WORDS = 5

#: The opening of the stated-absence paragraph. Exported so the caller (and the test that pins
#: this) matches the tool's own string rather than a second copy of it.
THIN_EVIDENCE_MARK = "No acceptance criterion could be derived from this finding's evidence"

#: Required fields that CLASSIFY a finding (a severity, a priority) or that ARE criteria already.
#: Everything else in a type's `required` tuple is prose evidence, so a required field added later
#: becomes a criterion source without anybody remembering to list it here - the set is derived from
#: `TYPES`, never enumerated beside it.
_NON_EVIDENCE_FIELDS = frozenset({"severity", "priority", "ctype", "acs", "options"})

#: How each evidence field reads as a criterion. A field with no form here still yields one through
#: `_CRITERION_FALLBACK`, so a source this table forgets is covered rather than silently exempt.
_CRITERION_FORM = {
    "steps": "Following the recorded steps no longer reproduces the defect: {gist}",
    "fix": "The proposed fix lands, pinned by a test: {gist}",
    "summary": "The behaviour described is corrected: {gist}",
    "impact": "The impact described no longer follows: {gist}",
}
_CRITERION_FALLBACK = "The recorded {field} is satisfied: {gist}"
_GIST_MAX = 160


def _derived_patterns() -> tuple[re.Pattern, ...]:
    """A matcher for every criterion form this module writes, DERIVED from the forms themselves
    so a form added to `_CRITERION_FORM` is recognised from the moment it is added.

    Whole-form patterns, not prefixes. A prefix is what the first draft used, and
    `_CRITERION_FALLBACK` ("The recorded {field} is satisfied: {gist}") degenerates to the
    two-word prefix "The recorded" - which would have classified an authored criterion opening
    "The recorded impact no longer follows" as tool-derived. A form whose placeholder comes
    first degenerates to nothing at all, and would have matched everything or nothing depending
    on which way the empty string was handled."""
    pats = []
    for form in (*_CRITERION_FORM.values(), _CRITERION_FALLBACK):
        pats.append(re.compile("^" + "".join(
            ".+?" if part.startswith("{") else re.escape(part)
            for part in re.split(r"(\{[^}]*\})", form) if part)))
    return tuple(pats)


def is_derived_criterion(line: str) -> bool:
    """True when a criterion line is one THIS MODULE wrote from a finding's prose, rather than
    one an author wrote.

    A derived criterion restates the finding: "The behaviour described is corrected: <the first
    160 characters of the summary>". It is a placeholder that reads like content - it satisfies
    every "has criteria" check in the repo while being unjudgeable, because nothing in it says
    what passing looks like. Nine bugs reached a plannable batch in that state.

    Matched against the whole form, read from `_CRITERION_FORM` rather than copied, so the
    writer and the detector cannot drift apart."""
    body = line.lstrip().lstrip("-*").lstrip()
    for mark in ("[ ]", "[x]", "[X]"):
        if body.startswith(mark):
            body = body[len(mark):].lstrip()
            break
    body = body.replace("**", "").strip()
    return any(pat.match(body) for pat in _derived_patterns())


def criteria_are_all_derived(text: str) -> bool:
    """True when a unit HAS criteria and every one of them is tool-derived.

    False when it has none at all - that is a different state with a different fix, and the
    caller is expected to ask `validate._has_criteria` for it. Reporting both through one
    boolean is what let the two hide behind each other."""
    _md = sdlc_md
    lines, in_ac = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if not in_ac or not line.strip():
            continue
        if _md.UNGROOMED_AC_TOKEN in line or line.lstrip().startswith(">"):
            continue
        if line.lstrip()[:1] in ("-", "*") or _md.AC_HEADING_RE.match(line):
            lines.append(line)
    return bool(lines) and all(is_derived_criterion(ln) for ln in lines)


def evidence_fields(type_: str) -> tuple[str, ...]:
    """The prose fields of a type a criterion can be derived from, read off the type's OWN
    `required` tuple minus the fields that classify rather than evidence. Derived, so a required
    field added to `TYPES` later is a criterion source from the moment it is added."""
    return tuple(k for k in TYPES.get(type_, {}).get("required", ())
                 if k not in _NON_EVIDENCE_FIELDS)


def evidence_gist(value) -> str:
    """One field's evidence as a single clause: fenced/indented code stripped (an illustration is
    not a statement of the contract), `{{placeholder}}` scaffolding removed, whitespace collapsed,
    cut at the first sentence and bounded. Empty when nothing substantive is left."""
    text = _strip_code_blocks(str(value or ""))
    text = re.sub(r"\{\{.*?\}\}", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    flat = " ".join(text.split())
    if not flat:
        return ""
    m = re.search(r"[.!?](?:\s|$)", flat)
    first = flat[:m.start() + 1] if m else flat
    if len(first) > _GIST_MAX:
        first = first[:_GIST_MAX].rsplit(" ", 1)[0].rstrip(" ,;:") + "..."
    return first.strip()


def _is_thin(gist: str) -> bool:
    """A gist too thin to state a contract from: fewer than `MIN_EVIDENCE_WORDS` words."""
    return len(gist.split()) < MIN_EVIDENCE_WORDS


def derived_criteria(type_: str, fields: dict) -> list[str]:
    """The acceptance criteria derived from a finding's own evidence, one per evidence field that
    carries enough to state a contract from. Empty when the author supplied their own `acs` (an
    authored criterion is never displaced by a derived one) and when every field is thin."""
    if fields.get("acs"):
        return []
    out: list[str] = []
    for key in evidence_fields(type_):
        gist = evidence_gist(fields.get(key))
        if not gist or _is_thin(gist):
            continue
        form = _CRITERION_FORM.get(key, _CRITERION_FALLBACK)
        out.append(form.format(field=key, gist=gist))
    return out


def thin_evidence_note(type_: str, fields: dict) -> str:
    """The stated absence written in place of a criterion, naming the fields whose evidence was
    too thin. A paragraph, deliberately: it must read as an absence to a human AND count as one
    to `sdlc_md.count_acs`, or a finding that planned nothing would pass the engagement floor."""
    thin = [k for k in evidence_fields(type_) if _is_thin(evidence_gist(fields.get(k)))]
    named = ", ".join(f"`{k}`" for k in thin) or "none of its prose fields"
    return (f"{THIN_EVIDENCE_MARK}: {named} carries fewer than {MIN_EVIDENCE_WORDS} words of "
            f"substance, so nothing here states what fixed would look like. Whoever picks this "
            f"up agrees the contract with the author before starting - this is a stated gap, "
            f"not a criterion to tick.")


def criteria_block(type_: str, fields: dict) -> str:
    """The body of a filed finding's `## Acceptance Criteria` section: the AUTHORED criteria,
    else derived checkboxes, else the stated absence. The one renderer both halves share.

    Authored first, and that order is the whole point. `derived_criteria` returns nothing when
    the author supplied their own - "an authored criterion is never displaced by a derived one" -
    but nothing then rendered them, so the block fell through to the stated absence and wrote
    `nothing here states what fixed would look like` OVER criteria the author had written. That
    is worse than dropping them: the document asserts the opposite of the truth, and the
    engagement floor reads the assertion and agrees."""
    supplied = fields.get("acs") or []
    if isinstance(supplied, str):        # a bare string is ONE criterion, not one per character
        supplied = [supplied] if supplied.strip() else []
    authored = [re.sub(r"^\s*-\s*\[[ xX]\]\s*", "", str(a)).strip()
                for a in supplied]
    authored = [a for a in authored if a]
    # THE `ACn` MARKER, because `sdlc_md.AC_BULLET_RE` requires it and a bare `- [ ] <prose>`
    # bullet is invisible to `verify_ac`. The writer and the parser disagreed for 400 bugs and
    # nothing detected it, because the failure mode was exit 0 - 311 of 534 bug files printed a
    # line byte-comparable to a clean pass. A criteria block this module writes must be
    # readable by the module that executes it.
    if authored:
        return "\n".join(f"- [ ] **AC{n}** {a}" for n, a in enumerate(authored, 1))
    derived = derived_criteria(type_, fields)
    if derived:
        return "\n".join(f"- [ ] **AC{n}** {c}" for n, c in enumerate(derived, 1))
    return thin_evidence_note(type_, fields)


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
#: The filer's own extra keys. `evidence` is deliberately NOT in the common set: it is the finding
#: filer's record of WHERE a defect was observed, and a key the general creator would accept and
#: then ignore is the silent-loss class the fields-file refusal exists to end.
#: `lens`/`profile`/`audit_run` are here because `load_fields_file` RAISES on any key outside this
#: tuple, and `--fields-file` is the path that does not cross a shell - so it is the one a
#: prose-heavy audit finding has to use.
FIELDS_FILE_KEYS: tuple[str, ...] = (*COMMON_FIELDS_FILE_KEYS,
                                     "mutation_run", "mutation_target", "evidence",
                                     "lens", "profile", "audit_run", "detector_for_lens")

#: The `--fields-file` spelling that means "read the document from stdin" - the family
#: convention, so no writer grows its own.
STDIN_FIELDS_FILE = "-"

#: The prose fields a shell would have expanded. Checked for damage, never rewritten.
HAZARD_FIELDS: tuple[str, ...] = ("title", "summary", "steps", "fix", "impact", "recommendation")

# --- post-damage fingerprints -------------------------------------------------------------
# The three shapes above all detect a metacharacter that SURVIVED. The corruptions actually
# suffered are the opposite case: the substitution COMPLETED, so the backticks and everything
# between them are gone and the text carries no metacharacter at all. What it does carry is the
# HOLE - the spacing and punctuation that used to sit around the token. Three marks, each
# measured against four recorded corruptions and against every prose field in this repository's
# own artefacts (tests/test_shell_hazard_rate.py).

#: An inline code span SURVIVED the shell, so it is intact text rather than a hole. It is
#: replaced by one word character before the fingerprints run, or a quoted command line
#: ("find . -name x") reads as a sentence with a hole in it.
_CODE_SPAN = re.compile(r"`[^`]*`")
#: A hole between two words: the shell substituted empty and the spaces that flanked the token
#: closed up into one run.
_COLLAPSED_SPACE = re.compile(r"(?<=\w)  +(?=\w)")
#: A full stop or question mark only ends a clause when what follows is nothing, or a new
#: sentence. Without this, a path (`diff .local/`) or an argument reads as sentence punctuation.
_CLAUSE_END = r"(?:\s*$|\s+[A-Z\"'(\[])"
#: The space that separated a word from the token the shell removed, now sitting against the
#: punctuation that followed it.
_SPACE_BEFORE_PUNCT = re.compile(rf"(?<=\w) +(?:[.?]{_CLAUSE_END}|[,;:]\s)")
#: A preposition takes an object. One left against punctuation names WHAT went missing, so it
#: is reported in place of the generic mark above. Prepositions only - a verb or a noun before
#: punctuation is ordinary English.
_PREPOSITIONS = ("of", "in", "to", "for", "with", "from", "under", "by", "at", "on", "into",
                 "via", "against", "between", "about", "over", "after", "before", "during",
                 "through", "per", "than")
_DANGLING_PREPOSITION = re.compile(
    rf"\b(?:{'|'.join(_PREPOSITIONS)}) +(?:[.?]{_CLAUSE_END}|[,;:]\s)", re.IGNORECASE)


def _follows_a_flag(text: str, idx: int) -> bool:
    """True when the token before `idx` is a command-line flag, so what follows it is that
    flag's ARGUMENT rather than a sentence. `--root .` is a spelling, not a hole."""
    start = max(text.rfind(" ", 0, idx), text.rfind("\n", 0, idx)) + 1
    return text[start:idx].startswith("-")


def _strip_code_blocks(value: str) -> str:
    """Remove fenced (``` / ~~~) and indented (four-space / tab) code blocks from a field value.

    A code block is an ILLUSTRATION quoted in prose, not a command being stored as an argument: its
    column-aligned two-space gaps and its fence markers (an odd run of backticks) are not the marks
    of a shell that ate a field. Scanning them for those marks was the false-positive source that
    reddened the tree-wide catch-rate gate on legitimately-authored artefacts, so they are dropped
    before any fingerprint runs. Detection is unaffected for real command-shaped values, which do
    not arrive fenced or indented."""
    out: list[str] = []
    fence: tuple[str, int] | None = None
    for line in value.splitlines():
        # the ONE shared CommonMark tracker, never a three-character toggle: a toggle released a
        # ````markdown block on its inner ``` and scanned the illustration below it as a value
        fence, is_fence_line = sdlc_md.fence_step(line.lstrip(), fence)
        if is_fence_line or fence is not None:
            continue
        if line.startswith("    ") or line.startswith("\t"):
            continue  # an indented code block - not a stored command
        out.append(line)
    return "\n".join(out)


def substitution_fingerprints(value: str) -> list[str]:
    """What was found in `value` bearing the marks of a command substitution that COMPLETED.

    Empty when clean. Detection only, and one finding per mark: the point is to name the field
    a reader should distrust, not to guess at the words that were removed.

    The limit is measured rather than implied: over the four recorded corruptions these three
    marks catch three. The fourth lost a backticked token from the START of a sentence, which
    leaves grammatical text behind and is undetectable in principle - which is why the
    fields-file path, not this, is the fix."""
    text = _CODE_SPAN.sub("C", _strip_code_blocks(value))
    found: list[str] = []
    if _COLLAPSED_SPACE.search(text):
        found.append("a collapsed double space - a completed command substitution leaves the "
                     "spaces that flanked the token closed up against each other")
    prep = [m for m in _DANGLING_PREPOSITION.finditer(text) if not _follows_a_flag(text, m.start())]
    if prep:
        found.append(f"a preposition left against punctuation ({prep[0].group(0).strip()!r}) - "
                     "the words it governed are what a completed substitution removed")
    # A dangling preposition ALSO matches the generic mark below; reporting both would say the
    # same hole twice, so the specific finding wins over the span it already covers.
    if any(not _follows_a_flag(text, m.start())
           and not any(p.start() <= m.start() < p.end() for p in prep)
           for m in _SPACE_BEFORE_PUNCT.finditer(text)):
        found.append("a space before punctuation - what stood between the two is what a "
                     "completed command substitution removed")
    return found


#: How a field declares that it QUOTES a shell hazard rather than having suffered one. The
#: shape this repo already uses for a recorded exception: an explicit marker the author writes,
#: not a pattern the tool guesses at.
_QUOTING_MARKER = re.compile(r"<!--\s*quotes-shell-hazard:\s*\S.*?-->", re.IGNORECASE | re.DOTALL)


def shell_hazards(fields: dict, keys: tuple[str, ...] | None = None) -> list[tuple[str, str]]:
    """(field, what was found) for every value bearing the marks of a shell that already ate it.

    Two halves. The SURVIVING metacharacter: an UNBALANCED backtick (the pair's other half, and
    everything between, is gone), a surviving `$(` (substitution the shell did not complete, or
    prose that would be substituted next time), and a TRAILING backslash (a line continuation
    that swallowed what followed). Then the substitution that COMPLETED, leaving no
    metacharacter at all and only the hole where the token was - see
    `substitution_fingerprints`, whose measured limit is recorded with it.

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
        # A fenced or indented code block is an illustration, not a stored command: its fence
        # markers and aligned spacing are not the marks of a shell that ate a field. Strip them
        # before every check, so a quoted excerpt no longer reddens the tree-wide catch-rate gate.
        scanned = _strip_code_blocks(val)
        # A field DECLARING that it quotes the hazard is exempt. An artefact documenting the
        # shell-mangling defect necessarily contains the mangled text, so the detector flagged
        # the very report written to explain it - the filing had to be reworded to describe the
        # evidence rather than show it, which is the opposite of what a defect report is for.
        #
        # DECLARED, never inferred: a heuristic guessing which prose is illustrative would
        # exempt the real cases too. The author states it, and the statement is in the field, so
        # a reader meets the exemption at the same place as the hazard.
        if _QUOTING_MARKER.search(scanned):
            continue
        if scanned.count("`") % 2:
            out.append((key, "an unbalanced backtick - a backtick pair is command "
                             "substitution, and its other half (with everything between) "
                             "is what a shell removes"))
        if "$(" in scanned:
            out.append((key, "a `$(` - command substitution the shell either already ran "
                             "or will run next time this value is passed as an argument"))
        stripped = scanned.rstrip(" \t\n")
        if stripped.endswith("\\") and not stripped.endswith("\\\\"):
            out.append((key, "a trailing backslash - a line continuation swallows whatever "
                             "followed it"))
        out.extend((key, what) for what in substitution_fingerprints(scanned))
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
          f"metacharacters, or the marks of a substitution that already completed - what is "
          f"stored may already be missing what the shell removed:", file=out)
    for key, what in found:
        print(f"  --{key}: {what}", file=out)
    print("  Fix: pass the finding as a JSON document instead - `--fields-file finding.json` "
          "with the same field names. Nothing in it crosses a shell, so the text is stored "
          "exactly as written.", file=out)
    return found


def resolve_prose_fields(fields_file: str | None, flag_fields: dict,
                         allowed: tuple[str, ...],
                         metadata_keys: tuple[str, ...] | None = None) -> dict:
    """The ONE path a prose-taking writer (critic, close_owed, sprint, ...) uses to obtain its
    free-text fields safely, so every writer routes through the same loader rather than a second
    idiom that could drift.

    With a `--fields-file`: read the JSON document (no value crossed a shell, so the text is stored
    exactly as written) and let it supply the fields; an explicit flag still overrides its key. With
    no fields-file: the flag values DID cross a shell, so any shell metacharacters they carry are a
    swallowed command - report them (non-blocking, the flag path stays compatible). Empty/None flag
    values are dropped before either path. Raises ValueError on a bad fields-file (unreadable, not a
    JSON object, or an unknown key), which the caller turns into a refusal.

    `allowed` is every field the writer accepts - prose AND metadata - so one document can be the
    whole invocation. `metadata_keys` names the fields that are NOT free text (`tags`, `epic`,
    `points`) and so need no shell-hazard check; EVERYTHING ELSE in `allowed` is treated as prose
    and IS checked. The direction is deliberately fail-safe: a key nobody classified stays checked,
    so a prose field a caller forgets to declare is never silently skipped (that unsafe default was
    the `prose_keys` form this replaced). `metadata_keys=None` means the whole allowed set is prose
    - the back-compatible default, so a writer that passed only prose keys as `allowed` is
    unchanged."""
    md = set(metadata_keys or ())
    prose = tuple(k for k in allowed if k not in md)
    flags = {k: v for k, v in flag_fields.items() if v is not None and v != ""}
    # A FLAG value crossed a shell whether or not a --fields-file was also given, so it is hazard-
    # checked either way. The file's OWN values never crossed a shell and are not checked. Check
    # the writer's PROSE keys, not the whole allowed set, or a metadata field a shell cannot mangle
    # would be reported and a `note`/`verdict` prose field could go unchecked.
    report_shell_hazards(flags, keys=prose)
    if fields_file:
        from_file = load_fields_file(fields_file, allowed=allowed)
        return {**from_file, **flags}          # an explicit flag wins over the document
    return flags


def load_fields_file(path: Path | str, allowed: tuple[str, ...] = FIELDS_FILE_KEYS) -> dict:
    """Read a `--fields-file` JSON document into a fields dict, or raise ValueError.

    The whole point is that no value here has crossed a shell, so the text is stored exactly as
    written. Refuses an unreadable file, a document that is not an object, and any key outside
    `allowed` - a mistyped key that is silently ignored is the same silent-loss class the file
    exists to end.

    A path of `-` reads the document from STDIN, so a document another process produced reaches
    the writer without being spilled to a temporary file first. The file stays the documented
    default - it can be re-run, committed as evidence and diffed - but a caller holding the text
    in a pipe must not be pushed back onto the flag path, which is the path that loses it."""
    p = "stdin" if str(path) == STDIN_FIELDS_FILE else Path(path)
    try:
        raw = sys.stdin.read() if p == "stdin" else p.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"--fields-file {p} cannot be read: {exc}") from exc
    try:
        data = json.loads(raw)
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
    stamp = _STAMP + f"> **Raised-by:** {f.get('_raised_by') or sdlc_md.DEFAULT_AGENT_AUTHOR}\n"
    if f.get("_batch"):
        # WHERE this finding was raised, so its cost is priced against the batch that caused it
        # rather than read as close overhead. An absence is stated, not omitted.
        stamp += f"> **Raised-in-batch:** {f['_batch']}\n"
    return stamp


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


def _evidence_line(f: dict) -> str:
    """The `Evidence` metadata line: WHERE the finding was observed - a review, a transcript, a
    log, a file and line.

    A separate field from `Affects` on purpose. `Affects` is the sprint FOOTPRINT the planner
    reads, so a filer who wrote the evidence location into it declared a footprint that is not
    where any code will change: the collision analysis then groups the unit by the wrong surface.
    Losing the trace instead would be no better, so it is recorded here, where nothing reads it as
    a file the fix will touch."""
    val = str(f.get("evidence") or "").strip()
    return f"> **Evidence:** {val}\n" if val else ""


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


def _audit_attribution_lines(f: dict) -> str:
    """The `Audit-lens` / `Audit-profile` / `Audit-run` metadata lines.

    Beside `Raised-by` rather than inside it: 108 findings already hide a run id in that line's
    prose, which means counting a class across runs needs a regex over free text instead of a
    field read. Recorded at filing time because the filer is the only thing that knows.
    """
    lens = str(f.get("lens") or "").strip()
    if not lens:
        return ""
    profile = str(f.get("profile") or "").strip()
    run = str(f.get("audit_run") or "").strip()
    return (f"> **Audit-lens:** {lens}\n"
            + (f"> **Audit-profile:** {profile}\n" if profile else "")
            + (f"> **Audit-run:** {run}\n" if run else ""))


def _detector_for_lens_line(f: dict) -> str:
    """The `Detector-for-lens` metadata line: this unit exists to BUILD a detector for that lens.

    Deliberately OUTSIDE the lens/profile/run triple. The unit is about one lens across TWO runs,
    so it has no single `--audit-run`; under all-or-none it would have to file with none of the
    three, and `detector-owed`'s own output would then be unattributable and invisible to the next
    run. A distinct field also makes the idempotence check EXACT - matching on a title substring
    would re-file the same unit the moment anyone reworded it.
    """
    lens = str(f.get("detector_for_lens") or "").strip()
    return f"> **Detector-for-lens:** {lens}\n" if lens else ""


def check_audit_attribution(repo_root: Path | str, fields: dict) -> dict:
    """Resolve a lens / profile / audit-run attribution before anything is minted, or refuse.

    Runs PRE-MINT, beside `check_mutation_run`: a `raise` here happens before the advisory lock is
    taken and before an id is allocated, so a refusal costs no id and holds no cross-process lock
    while it parses packs.

    ALL THREE OR NONE, never some - except that `profile` is DERIVED. A lens name resolves to
    exactly one pack, so demanding the profile is asking for input the operator can get wrong;
    supplied, it is cross-checked, and a lens/profile MISMATCH is refused, which all-three-or-none
    cannot catch. A filing carrying none of the three stays legal, because 923 existing findings
    carry none.
    """
    lens = str(fields.get("lens") or "").strip()
    profile = str(fields.get("profile") or "").strip()
    run = str(fields.get("audit_run") or "").strip()
    if not (lens or profile or run):
        return fields
    import readiness  # noqa: PLC0415 - local: the filer reads the packs, it does not own them
    packs = sorted(set(readiness.profile_names()) - set(readiness.REFERENCE_PROFILES))
    # A profile no pack declares is refused FIRST and by name, listing what the resolver does
    # declare. It used to fall through to the "lens required" branch, which named `--audit-run` -
    # a flag the operator had not supplied - and named neither the profile nor the packs.
    if profile and profile not in packs:
        raise ValueError(
            f"no pack declares the profile {profile!r} - refusing to stamp a finding against a "
            f"pack that resolves to nothing. Packs that exist: {', '.join(packs)}")
    if not lens:
        raise ValueError(
            "--lens is required alongside --audit-run or --profile: a class is counted PER LENS "
            "per run, so a finding stamped without one can never take part in the comparison the "
            "stamp exists for. Supply lens and run together, or neither")
    if not run:
        raise ValueError(
            "--audit-run is required alongside --lens: a lens seen once is the lens working and a "
            "lens seen across two runs is a detector owed, so the run is what makes the count "
            "mean anything. Supply both, or neither")
    owners = []
    unreadable = []
    for p in packs:
        # Guarded PER PACK. `resolve_profile` raises for a pack that parses to no lens, and
        # `reference-audit.md#audit-extend` invites a project to add packs - so a half-written one
        # is an expected state. Unguarded, an unrelated stub refused every attributed filing in the
        # project and named a file the operator had never mentioned. Same shape as
        # `readiness.cmd_validate_profiles`, forty lines away.
        try:
            lenses = readiness.resolve_profile(p)["lenses"]
        except readiness.UnknownProfile:
            unreadable.append(p)
            continue
        if any(l["name"] == lens for l in lenses):
            owners.append(p)
    if not owners:
        detail = f". Packs that could not be read: {', '.join(unreadable)}" if unreadable else ""
        raise ValueError(
            f"no pack declares the lens {lens!r} - refusing to stamp a finding with a lens that "
            f"resolves to nothing. Packs that exist: {', '.join(packs)}{detail}")
    if len(owners) > 1:
        # AMBIGUOUS, so refused rather than resolved alphabetically. Picking `owners[0]` made
        # supplying `--profile` and omitting it produce DIFFERENT records for the same finding,
        # from the very check that claims to be stronger than requiring all three.
        raise ValueError(
            f"the lens {lens!r} is declared by more than one pack ({', '.join(owners)}), so the "
            f"profile cannot be derived and the two would disagree with a supplied one. Rename the "
            f"lens in one pack so it identifies a single one")
    if profile and profile not in owners:
        raise ValueError(
            f"the lens {lens!r} belongs to {', '.join(owners)}, not to {profile!r} - a consistent-"
            f"looking pair naming the wrong pack is exactly what a per-field existence check "
            f"cannot see. Omit --profile and it is derived")
    import audit_cost  # noqa: PLC0415 - local: the filer reads the register, it does not own it
    reg = audit_cost.register(repo_root)
    if run not in reg["runs"]:
        # The hint depends on WHICH of the three states the register is in. Telling an operator to
        # record the run again when the register is merely CORRUPT appends a duplicate row to an
        # already-broken file, and the run they are being told to record is very likely in there.
        if reg["state"] == "corrupt":
            hint = (f"The register is UNREADABLE, so this run may well be recorded: {reg['detail']}"
                    f". Repair the shard by hand - do NOT re-record, which would append a "
                    f"duplicate to a file that is already broken")
        elif reg["state"] == "empty":
            hint = ("The register is empty - record the run with `audit_cost.py record --run-id` "
                    "first")
        else:
            hint = "Registered: " + ", ".join(sorted(reg["runs"]))
        raise ValueError(
            f"no audit run {run!r} in the register ({audit_cost.EVIDENCE}/"
            f"{audit_cost.LEDGER_PREFIX}-*.jsonl) - refusing to stamp a finding with a run nobody "
            f"recorded, because a one-character typo would otherwise manufacture a second "
            f"distinct run id and with it a false detector-owed verdict. {hint}")
    return {**fields, "lens": lens, "profile": profile or owners[0], "audit_run": run}


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


#: Prose fields a caller can supply, and the section each is rendered under. Every filer must
#: LAND every one of these somewhere, or refuse: a field accepted at the CLI and dropped by the
#: renderer is content the author believes they filed. `artifact.py` was fixed for this class;
#: this renderer still had no home for a CR's `steps` or `fix`, so both were discarded in
#: silence - which is how the remedy of a change request about wasted time was itself lost.
_LANDABLE = (
    ("steps", "Steps to Reproduce"),
    ("fix", "Proposed Fix"),
    ("impact", "Impact"),
    ("recommendation", "Recommendation"),
)


def _open_batch_key(root) -> str | None:
    """The open delivery batch's key, READ-ONLY - safe to call while the allocation lock is
    held, because it takes no lock of its own.

    Best-effort: a project with no run state, or a corrupt one, still files findings. A filer
    that refused because a ledger could not be read would make the attribution more important
    than the finding."""
    try:
        from lib import run_state  # noqa: PLC0415 - deferred sibling, as elsewhere here
        span = run_state.open_batch(root)
        return span.get("opened_at") if span else None
    except Exception as exc:  # noqa: BLE001 - attribution must never block a filing
        sdlc_md.debug("file_finding._open_batch_key", exc)
        return None


def _attribute_to_open_batch(root, finding_id: str) -> str | None:
    """Record this finding against the open delivery batch, OUTSIDE the allocation lock.

    Kept separate from the read above because it WRITES, and writing takes the same advisory
    lock the filer holds while allocating the id. Calling it from inside that lock made the
    process contend with itself for the full 10-second timeout on every filing, and
    `allocation_lock` proceeds unserialised once the timeout expires - so the fast path was
    ten seconds slower and the slow path lost the serialisation the lock exists for."""
    try:
        from lib import run_state  # noqa: PLC0415 - deferred sibling, as elsewhere here
        return run_state.note_finding(root, finding_id)
    except Exception as exc:  # noqa: BLE001 - attribution must never block a filing
        sdlc_md.debug("file_finding._attribute_to_open_batch", exc)
        return None


def _land_unhomed(body: str, f: dict) -> str:
    """Append a section for every supplied prose field this type's renderer has no home for.

    Appended rather than refused, because the content is the point and an author who supplied
    it is right to expect it. Inserted BEFORE the revision history so the document keeps its
    shape."""
    # A HEADING, at the start of a line - not the substring anywhere in the document. Reading
    # it loosely meant a finding whose prose merely MENTIONED `## Impact` was refused as
    # already-homed, with a message that was false and no remedy; this project files bugs
    # about its own renderers constantly, so that case is the normal one.
    headings = {ln.strip() for ln in body.splitlines() if ln.startswith("## ")}
    missing = [(key, heading) for key, heading in _LANDABLE
               if str(f.get(key) or "").strip() and f"## {heading}" not in headings]
    if not missing:
        return body
    # ESCAPED, exactly as `_render_sections` escapes the fields it homes. This landed the raw
    # value while the renderers next to it apply `_prose_safe`, so a CR whose `steps` contained
    # a metadata-shaped line (`> **Points:** 99`) had it read back by `extract_field` as a real
    # declaration - the injection `_prose_safe` exists to stop, through the one path that
    # skipped it.
    extra = "".join(f"## {heading}\n\n{_prose_safe(str(f[key]))}\n\n"
                    for key, heading in missing)
    marker = "## Revision History"
    return body.replace(marker, extra + marker, 1) if marker in body else body + "\n" + extra


def _refuse_dropped(body: str, f: dict) -> None:
    """Backstop: raise if any supplied prose field still reaches nothing.

    The lander above should make this unreachable. It exists because "the renderer covers every
    field" is exactly the belief that was false, and a filer that silently drops content is
    worse than one that stops."""
    lost = [key for key, _h in _LANDABLE
            if str(f.get(key) or "").strip() and _probe(f[key]) not in _probe(body)]
    if lost:
        raise ValueError(
            f"refusing to file: the supplied field(s) {', '.join(lost)} reach no section of "
            f"this document, so filing would discard content the author supplied")


def _probe(value) -> str:
    """Alphanumerics only - compares CONTENT across any escaping the renderer applied."""
    return "".join(c for c in str(value).lower() if c.isalnum())


def _render(type_: str, disp_id: str, title: str, today: str, f: dict,
            status: str | None = None) -> str:
    """A structured artifact body (required sections populated). `status` overrides the
    per-type create status (schema v3 files findings into `inbox`); None keeps the default."""
    body = _render_sections(type_, disp_id, title, today, f, status)
    body = _land_unhomed(body, f)
    _refuse_dropped(body, f)
    # Last, over the WHOLE body: a fenced block can only be recognised across the lines that
    # open and close it, which no per-field normaliser sees. Without it the filer mints
    # artefacts markdownlint MD040 refuses.
    return sdlc_md.normalise_fence_languages(body)


def _render_sections(type_: str, disp_id: str, title: str, today: str, f: dict,
                     status: str | None = None) -> str:
    """The per-type layout. `_render` is the only caller; it lands anything this misses."""
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
                f"{points}{_affects_line(f)}{_evidence_line(f)}{_mutation_link_lines(f)}{_audit_attribution_lines(f)}{_detector_for_lens_line(f)}"
                f"> **Created:** {today}\n{_stamp(f)}\n"
                f"## Summary\n\n{f['summary']}\n\n"
                f"## Steps to Reproduce\n\n{f['steps']}\n\n"
                f"## Proposed Fix\n\n{f['fix']}\n\n"
                # Derived from the evidence above, so the lane that picks this up has a contract
                # and the engagement floor has something to read. Thin evidence is STATED here,
                # never scaffolded - see `criteria_block`.
                f"## Acceptance Criteria\n\n{_md_safe(criteria_block(type_, f))}\n\n"
                f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"{rev_row(today, f, 'Filed')}\n")
    if type_ == "cr":
        # normalise: an AC supplied with its own leading checkbox ('- [ ] x',
        # '-[x] y') is not doubled into '- [ ] - [ ] x'
        stripped = (re.sub(r"^\s*-\s*\[[ xX]\]\s*", "", a) for a in f["acs"])
        acs = "\n".join(f"- [ ] {a}" for a in stripped)
        return (f"# {disp_id}: {title}\n\n"
                f"> **Status:** {status or 'Proposed'}\n> **Priority:** {f['priority']}\n"
                f"> **Type:** {f['ctype']}\n{_size_line(f)}{_affects_line(f)}{_evidence_line(f)}"
                f"{_mutation_link_lines(f)}{_audit_attribution_lines(f)}{_detector_for_lens_line(f)}"
                f"> **Date:** {today}\n{_stamp(f)}\n"
                f"## Summary\n\n{f['summary']}\n\n"
                f"## Impact\n\n{f['impact']}\n\n"
                f"## Acceptance Criteria\n\n{acs}\n\n"
                f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
                f"{rev_row(today, f, 'Raised')}\n")
    options = "\n".join(f"- **{o}**" for o in f["options"])
    decision = _decision_question(title, f["options"])
    return (f"# {disp_id}: {title}\n\n"
            f"> **Status:** {status or 'Draft'}\n{_size_line(f)}{_affects_line(f)}{_evidence_line(f)}"
            f"{_mutation_link_lines(f)}{_audit_attribution_lines(f)}{_detector_for_lens_line(f)}"
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


def duplicate_candidates(repo_root: Path | str, title: str, fields: dict,
                         type_: str | None = None) -> list[dict]:
    """Existing artefacts a NEW finding would probably duplicate. The cheapest triage lens - a
    duplicate is cheapest to catch at filing, where the author has the most context. It WARNS with
    the candidate named; it never refuses, because a genuine near-miss is common and only the author
    can tell them apart.

    ONE detector, shared with `artifact.py new`: both entry points call
    `artifact.duplicate_candidates`, so "is this a duplicate?" cannot be answered two ways. This
    used to carry a SECOND implementation - a Jaccard scorer over the open backlog - that disagreed
    with the mint-time one on real data (the pair that motivated the check scored 0.21 by Jaccard,
    under the bar, and 0.44 by the containment scorer that survives). Keeping two in sync is exactly
    what failed here, so the second is deleted rather than re-synced.

    `type_` scopes the comparison to ONE artefact type, matching `artifact new <type>` exactly, so
    the two entry points agree on SCOPE as well as algorithm - a bug is compared to bugs, not to
    CRs (comparing across types is the structural-pairing noise the within-type check avoids). When
    `type_` is None every dup-type is scanned (the type-agnostic caller). Terminal artefacts are in
    scope either way - re-filing a fixed bug is the costliest miss."""
    try:
        import artifact  # noqa: PLC0415 - deferred: artifact imports file_finding, so this is lazy
        root = Path(repo_root)
        types = (type_,) if type_ else artifact.DUP_TYPES
        out: list[dict] = []
        for t in types:
            out.extend(artifact.duplicate_candidates(root, t, title, fields))
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
    # `Evidence` is written into a metadata line of its own, so it is held to the same
    # one-line rule as every other metadata field rather than being the one that can break out.
    if isinstance(fields.get("evidence"), str):
        sdlc_md.require_single_line("evidence", fields["evidence"])
    # ... and refuse a CR/bug criterion carrying a command-shaped `Verify:` - a check nobody runs.
    check_prose_acs(type_, fields)
    root = Path(repo_root)
    today = fields.get("date") or date.today().isoformat()
    fields = {**fields, "date": today}
    # ... and refuse a declared `Affects` that resolves to nothing, before an id is allocated,
    # from the ONE seam every writer shares - naming the closest basename match where there is one.
    check_affects_resolvable(root, fields.get("affects"), type_)
    # ... and COMPLETE an understated one: a source file declared without its existing test is a
    # footprint smaller than the change, and the tool holds the exact path at the moment it would
    # otherwise only complain about it. Written, then reported - never silently.
    completed, added = complete_affects(root, fields.get("affects"), type_)
    if added:
        fields = {**fields, "affects": completed}
        report_completed_affects(added)
    # ... and refuse an attribution to a mutation run the series does not hold, before an id is
    # allocated: a finding stamped with an unresolvable run claims a provenance nobody can check.
    fields = check_mutation_run(root, fields)
    # PRE-MINT, beside the mutation guard: before the advisory lock and before an id is
    # allocated, so a refused attribution costs no id.
    fields = check_audit_attribution(root, fields)
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
    warnings = duplicate_candidates(root, title, fields, type_=type_)
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
        # OUTSIDE the lock, deliberately - the batch record is not part of the id allocation,
        # and writing it takes the same advisory lock. See `_attribute_to_open_batch`.
        _attribute_to_open_batch(root, result.get("id") or "")
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
    # US0561: a finding raised while a delivery batch is open is that batch's work, so its
    # cost is priced where the work was rather than as close overhead. The absence is STATED,
    # never guessed: with no batch open the field says so, because silently attributing to the
    # last-closed span is exactly the misattribution this exists to remove.
    batch_key = _open_batch_key(root)
    fields = {**fields, "_batch": batch_key or "none open - raised outside a delivery batch"}
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
             "affects": args.affects, "evidence": getattr(args, "evidence", None),
             "author": args.author, "recommendation": args.recommendation,
             "parent": getattr(args, "parent", None),
             "mutation_run": getattr(args, "mutation_run", None),
             "mutation_target": getattr(args, "mutation_target", None),
             # This dict is hand-enumerated, so a new argparse flag absent from it is parsed and
             # silently DROPPED - the filing then succeeds unattributed while every test that
             # calls `file_finding()` directly still passes.
             "lens": getattr(args, "lens", None),
             "profile": getattr(args, "profile", None),
             "audit_run": getattr(args, "audit_run", None),
             "detector_for_lens": getattr(args, "detector_for_lens", None)}
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
                   help="comma-separated files the FIX will touch - where the change lands, not "
                        "where the evidence was read - written as the `Affects` metadata line. "
                        "Include the test file: a fix arrives with a test, so that test is part "
                        "of the footprint. Required for a bug and a cr: `sprint plan` refuses a "
                        "unit that names no files - it cannot size one, nor see two units "
                        "colliding on the same file. Optional on an rfc (not a sprint unit)")
    f.add_argument("--evidence",
                   help="WHERE this finding was observed - a review, a transcript, a log, a "
                        "file:line. Recorded as the `Evidence` metadata line and deliberately "
                        "kept OUT of `Affects`: the evidence site is not where the fix lands, and "
                        "a footprint naming it groups the unit by a surface no code will change")
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
    f.add_argument("--lens",
                   help="the audit lens that found this, as a pack declares it. Stamped as "
                        "`Audit-lens` so a class recurring across runs can be counted from a "
                        "field rather than a regex over prose. Requires --audit-run; a lens no "
                        "pack declares is refused before an id is minted")
    f.add_argument("--profile",
                   help="the lens pack --lens belongs to (default: DERIVED, since a lens name "
                        "resolves to exactly one pack). Supplied, a lens/profile mismatch is "
                        "refused - which is what an existence check per field cannot catch")
    f.add_argument("--detector-for-lens", dest="detector_for_lens",
                   help="this unit exists to BUILD the mechanical detector for that lens. Stamped "
                        "as `Detector-for-lens` and OUTSIDE the lens/run pair, because the unit "
                        "spans two runs and so has no single one; it is what makes "
                        "`detector-owed --file` idempotent on an exact field rather than a title")
    f.add_argument("--audit-run", dest="audit_run",
                   help="the audit run that raised this finding, as recorded in the audit-cost "
                        "ledger by `audit_cost.py record --run-id`. Requires --lens. A run the "
                        "register does not hold is refused, so a typo cannot manufacture a second "
                        "distinct run and with it a false detector-owed verdict")
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
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
