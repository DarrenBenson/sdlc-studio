#!/usr/bin/env python3
"""SDLC Studio mutation-check gate - the executable half of assertion integrity.

`verify_ac` confirms an AC's tests PASS; this gate asks the complementary question:
would they FAIL if the feature broke? It applies a declared, bounded set of textual
mutations to the changed surface, re-runs the mapped tests per mutation, and reports
**killed** (test failed - it pins the behaviour) vs **survived** (test stayed green
over broken code - a finding). Honest by construction:

  - deterministic: same code + same mutation set -> same mutation list, same report;
  - bounded: a declared cost ceiling; enumeration past it is COUNTED as truncated,
    never silently dropped;
  - honest degrade: a (file, fault-class) pair the language profiles cannot mutate
    is reported un-checked, never passed; a red/broken baseline yields per-mutation
    `error` verdicts, never a fake kill.

Subcommands:
  run        apply the mutation set to a surface (--files / --since REF / --story)
             and re-run the test command per mutation; writes
             sdlc-studio/.local/mutation-report.json (the latest run), appends this
             run's per-target evidence to sdlc-studio/.local/mutation-runs.json (the
             bounded ledger the gate lane reads as coverage) and appends ONE row to
             sdlc-studio/.local/mutation-series.jsonl (the per-run cost/yield series);
             non-zero on survivors.
  register   record a mutant a builder ALREADY applied by hand, so the per-unit
             practice (apply a mutant to the code a new test pins, see RED, restore)
             leaves a trace in the same ledger. SELF-REPORTED: nothing here re-runs
             anything, so the entry is marked `registered` and the gate lane reports
             it as a claim, never as a measured run.
  yield      what one run COST (wall-clock) against what was FILED from it - the
             artefacts attributed to the run, never its raw survivor count, with any
             mutant judged `equivalent` quoted as excluded rather than decremented.
  window     declare (or clear) that a process is rewriting source files in place.
             A file, so it survives the SIGKILL that in-memory state does not; the
             gate refuses while one is open, so a concurrent commit is told rather
             than staging whatever that process has left on disk.
  prefilter  list test files with no recognisable assertion - the cheap static
             signal for which tests to mutate first (advisory).

Pure stdlib. The v1 gate lane in gate.py is advisory.
"""
from __future__ import annotations

import argparse
import contextlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

FAULT_CLASSES = ("invert-guard", "stub-return-null", "unset-delivered-field", "no-op-mapper")
DEFAULT_MAX_MUTATIONS = 25
#: Ledger bound: the most recent LEDGER_LIMIT per-target entries are kept, oldest first out.
#: Entries are one per target (a later run on the same file supersedes the earlier), so the
#: ledger grows with the number of distinct files ever mutated, not with the number of runs.
LEDGER_LIMIT = 200
#: The OTHER bound, on the other axis. `register` accumulates into one entry per (target,
#: content), so a builder registering every mutant they apply across a sprint grows that one
#: entry's `mutants` list while the entry count stays at 1 - LEDGER_LIMIT never fires on it.
#: The newest are kept, oldest first out, as everywhere else here; the entry's `summary`
#: counts are never truncated, so what was dropped is the description, never the tally.
MUTANT_LIMIT = 100
_RUN_TIMEOUT = 600  # seconds per test run - a hung mutant must not hang the gate

# WHERE a ledger entry's evidence came from. A `measured` entry is the record of a run that
# applied the mutant and observed the suite's answer. A `registered` entry is a builder's report
# that they applied one by hand: nothing in this file re-ran anything, so it is a CLAIM, and the
# ledger holding both would be silently downgraded to the weaker of the two if the entries did
# not say which they are. Every reader must be able to weight them differently.
PROVENANCE_MEASURED = "measured"
PROVENANCE_REGISTERED = "registered"
#: The verdicts a hand-applied mutant can carry. `error` and `unviable` are things the RUNNER
#: observes about a mutant it tried to execute; a builder reporting one would be reporting on a
#: run that did not happen here.
#:
#: `equivalent` is the judgement verdict: a survivor that changed no observable behaviour, so no
#: test could have killed it. It exists in the VOCABULARY rather than in a side-file because an
#: exclusion recorded away from the verdict is applied by memory and lost - and a silent
#: exclusion is indistinguishable from a mutant nobody ran. It carries a mandatory reason and is
#: excluded from yield while staying VISIBLE as excluded.
EQUIVALENT_VERDICT = "equivalent"
REGISTRABLE_VERDICTS = ("killed", "survived", EQUIVALENT_VERDICT)
#: The counters a ledger entry's summary carries. One list, so a new verdict cannot be countable
#: in one writer and absent in another. BOTH writers derive from it: `register_mutant` counts the
#: verdict it was handed, and `append_ledger` maps a RUN's verdict onto its counter below.
SUMMARY_VERDICTS = ("killed", "survived", "errors", "unviable", EQUIVALENT_VERDICT)
#: A run's verdict word -> the summary counter it increments. `error` is pluralised in the
#: summary and `equivalent` is never produced by a run, but it is listed so a counter cannot go
#: missing from one writer while the constant above claims it cannot.
RUN_VERDICT_COUNTER = {"killed": "killed", "survived": "survived", "error": "errors",
                       "unviable": "unviable", EQUIVALENT_VERDICT: EQUIVALENT_VERDICT}
#: The registered verdicts that are EVIDENCE ABOUT THE TESTS, and so count as mutation coverage
#: of a file. `equivalent` is deliberately absent: it asserts that no test could have killed the
#: mutant, which is a statement about the mutant, not about what the suite pins. A file carrying
#: only equivalent registrations has had nothing proven about its tests.
COVERING_VERDICTS = ("killed", "survived")


def entry_provenance(entry: dict) -> str:
    """A ledger entry's provenance. Absent means `measured`: before `register` existed only a
    run could write an entry, so an unmarked entry is a run's, and treating it as a claim would
    retro-actively weaken evidence that was really gathered."""
    return str(entry.get("provenance") or PROVENANCE_MEASURED)


# Language profiles: extension -> fault class -> (line regex, replacement builder).
# A class absent for an extension is UN-CHECKED for files of that language.
_PY = {
    "invert-guard": (
        re.compile(r"^(\s*)(if|elif)\s+(?!not \()(.+?):(\s*(?:#.*)?)$"),
        lambda m: f"{m.group(1)}{m.group(2)} not ({m.group(3)}):{m.group(4)}"),
    "stub-return-null": (
        re.compile(r"^(\s*)return\s+(?!None\b)(.+)$"),
        lambda m: f"{m.group(1)}return None"),
    "unset-delivered-field": (
        re.compile(r"^(\s*)([A-Za-z_][\w.]*)\s=\s(?!None\b)(.+)$"),
        lambda m: f"{m.group(1)}{m.group(2)} = None"),
    # no-op-mapper is an INSERT profile: short-circuit the function body.
    "no-op-mapper": (
        re.compile(r"^(\s*)def\s+\w+\(.*\)(\s*->.*)?:\s*$"),
        lambda m: m.group(0) + "\n" + m.group(1) + "    return None"),
}
# JS/Go profiles enumerate only forms whose mutants stay syntactically valid:
# block-form conditionals (trailing `{`), semicolon-terminated statements. A line
# no pattern matches is not enumerated - the un-checked contract is per
# (file, fault class), never per line.
_JS = {
    "invert-guard": (
        re.compile(r"^(\s*)(}?\s*)(if|while)\s*\((.+)\)\s*\{\s*$"),
        lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)} (!({m.group(4)})) {{"),
    "stub-return-null": (
        re.compile(r"^(\s*)return\s+(?!null\b)(.+?);\s*$"),
        lambda m: f"{m.group(1)}return null;"),
    "unset-delivered-field": (
        re.compile(r"^(\s*)(const |let |var )?([\w.$]+)\s*=\s*(?!null\b)(.+?);\s*$"),
        lambda m: f"{m.group(1)}{m.group(2) or ''}{m.group(3)} = null;"),
}
_GO = {
    "invert-guard": (
        re.compile(r"^(\s*)if\s+(?!!\()(?![^{]*(?::=|;))([^{]+?)\s*\{(.*)$"),
        lambda m: f"{m.group(1)}if !({m.group(2)}) {{{m.group(3)}"),
}
PROFILES: dict[str, dict] = {
    ".py": _PY,
    ".js": _JS, ".jsx": _JS, ".ts": _JS, ".tsx": _JS, ".mjs": _JS,
    ".go": _GO,
}


class MutationAnchorError(RuntimeError):
    """The line a mutation would edit is not the line it was enumerated at.

    Raised rather than warned: the run must abort, because a score published over a mutant
    applied somewhere else is evidence about nothing and reads exactly like evidence.
    """


#: The refusal that is NOT an absence of evidence. Named as its own kind so the lane can say
#: which of the two it is: a surface nobody tested is an omission, a surface carrying
#: uncommitted work is a state the runner is right to refuse and the author can still resolve.
UNCOMMITTED_SURFACE = "uncommitted-surface"


def _multiline_string_spans(text: str) -> tuple[set, bool]:
    """(line numbers inside multi-line string literals, tokenise_ok). Docstring
    interiors are code-shaped but mutate nothing - enumerating them yields false
    survivors. Single-line strings never exclude their line (real assignments
    live there). A tokenise failure returns (empty, False): exclusion skipped,
    enumeration proceeds, and the caller NOTES the skip - never silent."""
    import io
    import tokenize
    spans: set = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.STRING and tok.end[0] > tok.start[0]:
                spans.update(range(tok.start[0], tok.end[0] + 1))
    except (tokenize.TokenError, SyntaxError, IndentationError, ValueError):
        return set(), False
    return spans, True


def enumerate_mutations(paths, classes: tuple = FAULT_CLASSES) -> tuple[list[dict], list[dict]]:
    """(mutations, unchecked) over the target files, deterministically ordered by
    (file, class order, line). Each mutation is anchored by (file, class, occurrence)."""
    mutations: list[dict] = []
    unchecked: list[dict] = []
    for path in sorted(Path(p) for p in paths):
        profile = PROFILES.get(path.suffix)
        if profile is None:
            unchecked.extend({"file": str(path), "class": c,
                              "reason": f"no {path.suffix or '(no extension)'} profile"}
                             for c in classes)
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as exc:
            unchecked.extend({"file": str(path), "class": c, "reason": f"unreadable: {exc}"}
                             for c in classes)
            continue
        if path.suffix == ".py":
            # The spans themselves are NOT kept here. `_occurrences` derives them again as the
            # one place that decides what a match is, and holding a second copy in this scope
            # is what made "give the enumerator its own loop" a one-line edit - the duplication
            # this bug exists to remove, left lying beside the fix for it.
            _, tok_ok = _multiline_string_spans("\n".join(lines) + "\n")
            if not tok_ok:
                unchecked.append({"file": str(path), "class": "docstring-exclusion",
                                  "reason": "tokenise failed - string-interior "
                                            "exclusion skipped for this file"})
        for cls in classes:
            if cls not in profile:
                unchecked.append({"file": str(path), "class": cls,
                                  "reason": f"no {path.suffix} pattern for {cls}"})
                continue
            pattern, _ = profile[cls]
            # THE SAME routine `mutated_text` resolves with, so the two cannot drift.
            for occ, ln in enumerate(_occurrences(path, pattern, lines)):
                mutations.append({"file": str(path), "class": cls,
                                  "occurrence": occ, "line": ln})
    return mutations, unchecked


def _occurrences(path: Path, pattern, lines: list) -> list:
    """The 1-based line numbers this pattern matches, in occurrence order, with multiline-string
    interiors excluded for Python.

    THE ONE routine both readers use. `enumerate_mutations` used to apply the exclusion while
    `mutated_text` re-counted without it, so a pattern occurring inside a docstring above the
    real occurrence shifted the ordinal between them: the mutant was REPORTED at one line and
    APPLIED at another. A verdict attributed to a line the tool did not edit is worse than no
    verdict - a false KILL is a green mutation score for code that was never mutated, and this
    is the instrument the whole evidence story leans on. Two readers of one file disagree
    eventually, and the second is written by whoever did not know the first existed.
    """
    excluded: set = set()
    if path.suffix == ".py":
        excluded, _tok_ok = _multiline_string_spans("\n".join(lines) + "\n")
    return [ln for ln, line in enumerate(lines, 1)
            if ln not in excluded and pattern.match(line)]


def mutated_text(mutation: dict) -> str:
    """The full mutated file content for one anchored mutation.

    REFUSES when the line it would edit is not the line the mutation was enumerated at. The
    check is cheap, independent of how the anchor is computed, and it is what makes the shared
    routine above a guarantee rather than a convention the next edit can break.
    """
    path = Path(mutation["file"])
    pattern, repl = PROFILES[path.suffix][mutation["class"]]
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = _occurrences(path, pattern, lines)
    occ = mutation["occurrence"]
    if occ >= len(hits):
        # UNCHANGED text, deliberately - an existing contract this bug does not touch. The
        # caller refuses on "the patch changed nothing", which is the same refusal by a
        # different route; raising here would break `test_applied_refuses_a_mutant_identical
        # _to_the_source`. BG0533 is about applying at the WRONG line, not about an ordinal
        # that no longer resolves.
        return "\n".join(lines) + "\n"
    target = hits[occ]
    if target != mutation["line"]:
        raise MutationAnchorError(
            f"{path}: {mutation['class']} occurrence {occ} was ENUMERATED at line "
            f"{mutation['line']} and resolves to line {target}. Refusing to apply it: a verdict "
            f"attributed to a line the tool did not edit is not evidence about anything.")
    m = pattern.match(lines[target - 1])
    lines[target - 1] = repl(m)
    return "\n".join(lines) + "\n"


def changed_lines(repo_root: Path | str, since: str) -> dict:
    """Map file path -> set of line numbers touched since `since`, from `git diff -U0`.

    Zero context lines, so the hunk headers name exactly the added/modified lines. An
    untracked file is entirely new, so every line counts. Returns {} when git cannot
    answer - the caller then falls back to unbiased sampling rather than failing."""
    root = Path(repo_root)
    out: dict = {}
    try:
        diff = subprocess.run(["git", "diff", "-U0", since], cwd=root,
                              capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, OSError):
        return {}
    current = None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current = str(root / line[6:].strip())
            out.setdefault(current, set())
        elif line.startswith("@@") and current:
            # @@ -old,n +new,m @@ - the `+new,m` span is what this diff touches
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                start, count = int(m.group(1)), int(m.group(2) or 1)
                out[current].update(range(start, start + count))
    try:
        untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                                   cwd=root, capture_output=True, text=True, check=True).stdout
        for name in untracked.splitlines():
            p = root / name.strip()
            if p.suffix in PROFILES and p.exists():
                out[str(p)] = set(range(1, len(p.read_text(encoding="utf-8").splitlines()) + 2))
    except (subprocess.CalledProcessError, OSError):
        pass
    return out


def _on_diff(m: dict, changed: dict) -> bool:
    """True when this mutation sits on a line the diff touched."""
    return m["line"] in changed.get(str(m["file"]), set())


def apply_budget(mutations: list[dict], max_mutations: int,
                 changed: dict | None = None) -> tuple[list[dict], int]:
    """Distribute the cost ceiling round-robin over (file, fault class) groups -
    never first-N in file order, which clusters all coverage at the top of the
    alphabetically-first file. Deterministic: groups in sorted order, one mutation
    per group per rotation, each group's own line order preserved. Returns
    (chosen in original enumeration order, truncated count).

    When `changed` is supplied (file -> touched line numbers), mutations ON those lines
    are spent first and only the remainder of the ceiling reaches untouched code. Without
    it a low ceiling on a large file samples whichever lines sort first - peripheral
    helpers - rather than the change under review, so the run reports high kill rates
    about code nobody edited (L-0086)."""
    if len(mutations) <= max_mutations:
        return list(mutations), 0
    order = {id(m): n for n, m in enumerate(mutations)}

    def _rotate(pool: list[dict], budget: int) -> list[dict]:
        """Round-robin over (file, class) groups within one priority tier."""
        groups: dict = {}
        for m in pool:
            groups.setdefault((m["file"], m["class"]), []).append(m)
        # files are the FAST axis of the rotation (sort by class, then file): with a
        # small budget every file still gets coverage before any class repeats
        queues = [groups[k] for k in sorted(groups, key=lambda k: (k[1], k[0]))]
        picked: list[dict] = []
        i = 0
        while len(picked) < budget and any(queues):
            q = queues[i % len(queues)]
            if q:
                picked.append(q.pop(0))
            i += 1
        return picked

    if changed:
        on = [m for m in mutations if _on_diff(m, changed)]
        off = [m for m in mutations if not _on_diff(m, changed)]
        chosen = _rotate(on, max_mutations)
        if len(chosen) < max_mutations:      # diff fully covered - spend the rest broadly
            chosen += _rotate(off, max_mutations - len(chosen))
    else:
        chosen = _rotate(list(mutations), max_mutations)
    chosen.sort(key=lambda m: order[id(m)])
    return chosen, len(mutations) - len(chosen)


# The mutants currently applied to disk, so a SIGTERM (TaskStop) or an interpreter exit that
# skips the `finally` below still restores the original bytes - a killed run must never strand a
# mutant on the working tree (the incident that seeded BG0180's second half).
_APPLIED: dict[str, bytes] = {}
_RESTORE_INSTALLED = False


def _restore_applied() -> None:
    """Restore every mutant still on disk to its original bytes. Idempotent."""
    for p, original in list(_APPLIED.items()):
        try:
            Path(p).write_bytes(original)
        except OSError:
            pass
        _APPLIED.pop(p, None)


def _install_restore_handlers() -> None:
    """Register the crash/signal restore ONCE. atexit covers a normal exit and an unhandled
    exception; a SIGTERM handler covers a kill (TaskStop) that would otherwise skip every
    `finally`. SIGINT keeps raising KeyboardInterrupt, which the `applied` finally already
    unwinds. Signals can only be set from the main thread, so a worker-thread call is a no-op."""
    global _RESTORE_INSTALLED
    if _RESTORE_INSTALLED:
        return
    import atexit
    import os
    import signal
    atexit.register(_restore_applied)

    def _on_sigterm(signum, _frame):
        _restore_applied()
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)   # re-raise so the process still dies

    try:
        signal.signal(signal.SIGTERM, _on_sigterm)
    except (ValueError, OSError):
        pass  # not the main thread - atexit and the `applied` finally still cover normal paths
    _RESTORE_INSTALLED = True


def _purge_bytecode(path: Path) -> None:
    """Drop cached bytecode for `path` so the next run compiles the bytes on disk.

    CPython invalidates a `.pyc` on (source mtime, source size), so a mutant of the
    same byte length written inside one mtime second is invisible to that check and
    the ORIGINAL bytecode is executed. Same-length mutants are what operator-swap
    fault classes mostly produce, so the cache must be dropped rather than trusted.
    Best-effort: a cache we cannot remove is not a reason to abort the run, because
    `_run_tests` also refuses to write bytecode in the first place.
    """
    cache = path.parent / "__pycache__"
    if not cache.is_dir():
        return
    for pyc in cache.glob(f"{path.stem}.*.pyc"):
        try:
            pyc.unlink()
        except OSError:
            pass


def _inflight_path(root: Path) -> Path:
    """The on-disk sidecar holding the original bytes of the mutant currently applied.
    In-memory state (`_APPLIED`) dies with a SIGKILL; this file does not, so it is the
    one restore source a killed run cannot corrupt. The path is `sdlc_md`'s, because the
    entry-point guard reads the same file and a second spelling here is how a writer and
    its readers stop agreeing about where the window is recorded."""
    return sdlc_md.inflight_path(root)


def _suite_env() -> dict:
    """The environment this gate runs its suites under.

    `PYTHONDONTWRITEBYTECODE` because a cached `.pyc` is keyed on (source mtime, source
    size), so a same-length mutant written inside one mtime second would otherwise run the
    ORIGINAL bytecode and be recorded as survived. Writing no cache leaves nothing for the
    next mutant to inherit.

    The exemption marker because the sidecar this run writes makes every skill entry point
    warn or refuse, and the suites this run launches ARE that run. Anything descending from
    here inherits it and is exempt; nothing else in the tree does.
    """
    import os  # noqa: PLC0415 - local, as elsewhere in this module
    return {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", sdlc_md.MUTATION_RUN_ENV: "1"}


# --- The rewrite window ----------------------------------------------------------------------
#
# CR0388, as CORRECTED: the incident was NOT a hand-applied mutant. A reviewer built a helper
# directory with `ln -sf <repo>/scripts/*.py .` and ran `git show <sha>:...retro.py > retro.py`
# inside it; the redirect followed the symlink and overwrote the live working tree with the
# pre-sprint version, reverting two units' work. Meanwhile the author was committing ceremony
# artefacts in the same tree, and `git add -A` staged whatever the concurrent process had left.
#
# Two things follow, and both shape this record. The guard cannot recognise MUTANTS, because no
# mutant was involved. And it cannot lean on the suite going red, because the commit was blocked
# only by luck - the reverted source happened to fail; a rewrite that left the suite green (which
# is exactly what a SURVIVING mutant is) would have been committed silently under a paperwork
# commit message.
#
# So a window is a first-class DECLARABLE object, not a side effect of running this tool: any
# process rewriting files in place says who it is, what it may touch, and for how long. It is a
# FILE, modelled on `mutation-inflight.json`, because in-memory state dies with a SIGKILL and a
# file does not. An unreadable one reads OPEN: the one direction an error may never fail in is
# "closed".
#: Owner recorded for this tool's own runs; a reviewer's window names the reviewer instead.
WINDOW_OWNER_RUN = "mutation.py run"
#: The claim that covers the whole tree. A record that does not say what it may rewrite has NOT
#: said it may rewrite nothing, and neither has one whose `paths` no reader can interpret.
WINDOW_EVERYTHING = "*"

#: Unrelated paths the matcher probes to decide "claims everything" BY CONSTRUCTION rather than
#: by a hand-picked list of spellings - the trap the first five versions of the reason fell
#: into. A claim that matches EVERY probe refuses every commit. The battery must stay wide
#: enough to separate a genuine whole-tree glob from one that only matches the character class
#: it happens to sample: `9data.txt` (digit-leading) is here so `[a-zA-Z.]*`, which matches
#: every letter-or-dot probe but no path beginning with a digit, is NOT read as everything - the
#: CLI would otherwise print WHOLE TREE while the matcher lets `9data.txt` proceed. Shrinking
#: this to fewer probes lets a prefix glob such as `a*` masquerade as the whole tree; the
#: battery's width is load-bearing and pinned by test.
#: The ONE battery both the message and the verdict are driven over (US0317 + BG0259).
#: `everything_reason` probes this via `_probe_hits`, and the message/verdict agreement test
#: runs the gate matcher over the SAME tuple. Two copies of this list is how the previous
#: oracle came to agree with the matcher only on the shapes it had chosen. The digit-leading
#: `9data.txt` is load-bearing: without it an alpha-only glob like `[a-zA-Z.]*` reads as the
#: whole tree.
WINDOW_PROBES = ("a", "a/b.py", "z/y/x/w.md", "README", "x.y", ".githooks/pre-commit", "9data.txt")


def _probe_hits(pat: str, probes=WINDOW_PROBES) -> list[str]:
    """The probes a normalised claim matches, in `probes` order. The evidence the reason
    reports: it is what the MATCHER does with the claim, not a constant sentence, so the reason
    varies with its input and an inverted clause names a different set. `probes` defaults to
    the one WINDOW_PROBES battery; the message/verdict agreement test (US0317) passes its own
    so message and verdict are driven over the SAME set."""
    import fnmatch  # noqa: PLC0415 - local, as elsewhere in the matcher family
    return [s for s in probes
            if s.startswith(pat + "/") or fnmatch.fnmatch(s, pat)]


def everything_glob_examples(candidates=("**", "***", "?*", "*", "*.", "a*")):
    """Which candidate globs match EVERY probe, derived from `WINDOW_PROBES` rather than typed.

    A comment or doc naming example whole-tree globs asks for this list instead of spelling one
    by hand: an example that does not match every probe is filtered out, so `*.` (which matches
    none of the probes and shipped in the reason's own comment for two rounds) cannot be
    written, and neither can a prefix glob like `a*`. The rule the comment advocates, applied to
    the comment."""
    return tuple(c for c in candidates if len(_probe_hits(c.rstrip("/"))) == len(WINDOW_PROBES))


def window_dir(root: Path | str) -> Path:
    """Where window records live, beside the in-flight sidecar."""
    return Path(root) / "sdlc-studio" / ".local"


def window_path(root: Path | str) -> Path:
    """Where THIS tool declares its own window. One of the spellings `window_records` reads."""
    return window_dir(root) / "mutation-window.json"


def window_records(root: Path | str) -> list[Path]:
    """Every window record on disk, in BOTH spellings of the published contract.

    The contract has always named two spellings - `.local/*window*.json` for a single record,
    and `.local/windows/*.json` for one file per window - and for a while only the pre-commit
    hook honoured both while this module read the single fixed filename. A reviewer who wrote
    `windows/reviewer.json` was then told by `window status` that no window was open, and
    `window open` let a second writer declare one over the same tree: the refusal that exists
    precisely because two declared writers in one tree is the hazard. So discovery lives HERE,
    once, and the hook's inline reader is pinned against it by test."""
    base = window_dir(root)
    found: list[Path] = []
    if base.is_dir():
        found += sorted(p for p in base.glob("*window*.json") if p.is_file())
        sub = base / "windows"
        if sub.is_dir():
            found += sorted(p for p in sub.glob("*.json") if p.is_file())
    return found


def _clear_hint(owner: str) -> str:
    return f"mutation.py window close --owner {owner!r}"


def claims_everything(claim) -> bool:
    """Does this single claim cause a MATCHER to refuse every staged path?

    The matchers' rule, in one place a caller can ask BEFORE a commit is attempted. It is
    duplicated in `gate._window_claims` and inline in the pre-commit hook (which must run where
    these scripts are absent), and the three are pinned against each other by test over a
    battery of unrelated paths - NOT over a hand-picked list of spellings, which is how the
    previous version came to agree with the matchers on exactly the shapes it had chosen.

    THIS EXISTS BECAUSE RENDERING `window_claims` IS NOT RENDERING THE VERDICT. `window_claims`
    normalises the RECORD - it turns an empty or all-blank `paths` into WINDOW_EVERYTHING. The
    matchers then treat several further spellings as everything: a bare `.`, `./`, a trailing
    slash, an absolute path (not comparable with a repo-relative staged path), and a traversal
    that no literal pattern can match. So `--paths .` produced a record claiming `.`, which
    `window_claims` passes through unchanged, and the CLI called it one narrow path while every
    commit was refused. Four successive versions of that sentence were wrong; the first three
    asked the record what it said, and the question is what the MATCHER will do with it."""
    return everything_reason(claim) is not None


def everything_reason(claim, probes=WINDOW_PROBES) -> str | None:
    """WHY this claim claims the whole tree, in words, or None when it does not.

    `claims_everything` is this function asked as a yes/no. It exists because a message that
    lists EVERY cause for every input cannot be asserted against: a test reading it can only
    check that a word appears, which passes for a claim the word does not describe, and a
    mutant deleting the other causes survives. Naming the ONE cause that applies makes the
    sentence vary with its input, which is what makes it checkable.

    `probes` is the battery the glob branch is decided over. It defaults to the module's one
    battery so the printed message and the gate lane's verdict are derived over the SAME
    inputs; a test drives both over it to assert they agree.
    """
    if not isinstance(claim, str):
        return "it is not a path (the record cannot be interpreted)"
    pat = claim.strip()
    if pat.startswith("./"):
        pat = pat[2:]
    pat = pat.rstrip("/")
    if pat == "":
        return "it names no path, which claims everything rather than nothing"
    if pat == ".":
        return "it is the repository root"
    if pat.startswith("/"):
        return "it is absolute, so it is not comparable with a repo-relative staged path"
    if pat == ".." or pat.startswith("../") or "/../" in pat or pat.endswith("/.."):
        return "it traverses out of the repository, so no literal pattern can match it"
    # ASK THE MATCHER'S QUESTION, DO NOT ENUMERATE SPELLINGS. Both matchers end in
    # `fnmatch.fnmatch`, where a whole FAMILY of patterns matches every path. Example spellings
    # are NOT typed here: `everything_glob_examples()` derives them from `WINDOW_PROBES`, so a
    # spelling that does not match every probe cannot be listed (`*.` matched none and shipped in
    # this very comment for two rounds). The previous version listed literal spellings and got
    # `*` right only by accident, because `*` happened to be WINDOW_EVERYTHING sitting in the
    # tuple. It never reasoned about globs at all, so `--paths '**'` printed "1 path(s) ...
    # anything else proceeds" while every commit was refused. That was the FIFTH wrong version of
    # this sentence, and the four before it were all enumerations too. Probing settles it by
    # construction: a claim that matches every one of these unrelated paths claims everything.
    #
    # The reason REPORTS THE EVIDENCE, not a constant. It names the probes the matcher accepted,
    # so the sentence varies with its input: an inverted clause that reports the opposite set
    # names the wrong probes and a per-claim test catches it, where an `assertIn("glob", msg)`
    # could not - the word survives its own denial. The whole-tree VERDICT is `len(hits) == len
    # (WINDOW_PROBES)`, decided here and separately by `claims_everything`, never read off a word
    # in the sentence. A claim matching every probe but not every path (`[a-zA-Z.]*` misses
    # `9data.txt`) is therefore NOT everything, so the CLI stops claiming more than it probed.
    hits = _probe_hits(pat, probes)
    if len(hits) == len(probes):
        return "it is a glob and fnmatch accepts the matcher's probes [" + ", ".join(hits) + "]"
    return None


def window_claims(raw) -> list[str]:
    """What a record's `paths` field CLAIMS, normalised to what a matcher may be handed.

    The RECORD-level half of the one contract, and its one home here. The pre-commit hook
    implements the same rule inline - it must run in a clone where these scripts are absent or
    broken, so it cannot import them - and the two are pinned against each other by test.

    They diverged once, and the divergence is why this exists: this module DISCARDED `paths`
    whenever `owner` was falsy, and passed un-stripped claims to a matcher where a blank one
    means the repo root. So `{"paths": ["tools/x.py"]}` was read here as claiming the whole
    tree while the hook read it as claiming one file - and since the hook runs the gate a few
    lines later, one commit was told both, with the blocking half winning. A malformed owner
    must not change which paths are claimed.

    `paths` absent, empty, all-blank, not a list, or holding anything that is not a string
    reads as EVERYTHING: a claim nobody can interpret comes from a record saying a writer is
    active, and the one direction this may never be wrong in is "harmless".
    """
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return [WINDOW_EVERYTHING]
    claimed: list[str] = []
    for x in raw:
        if not isinstance(x, str):
            return [WINDOW_EVERYTHING]
        if x.strip():
            claimed.append(x.strip())
    return claimed or [WINDOW_EVERYTHING]


def _read_window_record(path: Path) -> dict:
    """One record, read. Never returns None: the caller has already found the file, and a file
    that exists is a window until somebody says otherwise."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("window record is not a JSON object")
    except (ValueError, OSError) as exc:
        return {"owner": "unknown (the record is unreadable)",
                "paths": [WINDOW_EVERYTHING],
                "opened_at": None, "note": None, "pid": None, "unreadable": True,
                "record_path": str(path),
                "detail": f"{path} exists but cannot be read ({exc}) - a process declared a "
                          f"rewrite window and its record did not survive; treat the tree as "
                          f"being written to until somebody says otherwise",
                "clear_with": f"delete {path} once you have confirmed nothing is rewriting "
                              f"the tree"}
    data.setdefault("unreadable", False)
    data["paths"] = window_claims(data.get("paths"))
    owner = str(data.get("owner") or "").strip()
    if not owner:
        # A record naming no owner is still a record: it says a writer is active, and its
        # `paths` say what they may rewrite. Discarding those claims because the OWNER field is
        # malformed is what made this reader claim the whole tree over a record the hook read
        # as claiming one file. It is UNOWNED - nobody can prove whose it is, so anyone may
        # clear it - and its claims are its own.
        data["owner"] = "unknown (the record names no owner)"
        data["unreadable"] = True
        data.setdefault(
            "detail", f"{path} declares a rewrite window and names no owner, so there is "
                      f"nobody to ask and nothing to wait for; it claims "
                      f"{', '.join(data['paths'])} until somebody clears it")
        if not str(data.get("clear_with") or "").strip():
            data["clear_with"] = (f"delete {path} once you have confirmed nothing is rewriting "
                                  f"the tree")
    else:
        data["owner"] = owner
        data.setdefault("clear_with", _clear_hint(owner))
    data["record_path"] = str(path)
    return data


def read_windows(root: Path | str) -> list[dict]:
    """Every open window, in both spellings. Empty means none is open."""
    return [_read_window_record(p) for p in window_records(root)]


def read_window(root: Path | str) -> dict | None:
    """The open window, or None when there is none.

    None means ABSENT and nothing else. A record that exists but cannot be parsed - truncated by
    the kill that stranded it, or half-written - is reported OPEN with `unreadable` set, because
    the only unsafe way to be wrong here is to report a live writer as finished. With several
    records on disk the first is returned; `read_windows` gives the caller all of them."""
    held = read_windows(root)
    return held[0] if held else None


def window_claim(root: Path | str, path) -> str:
    """One claimed path, normalised to the repo-relative spelling a reader can match.

    The reader compares claims against `git diff --cached --name-only`, which is always
    repo-relative. `run` builds its claim list from `select_files`, which returns `root / f`, so
    ANY absolute `--root` produced absolute claims - a window that announced it was rewriting a
    file and then matched nothing a commit staged. Normalising at OPEN time is what keeps the
    two spellings from ever meeting: a path under the root becomes relative to it, and a path
    outside the root is left verbatim, where the reader treats it as uninterpretable and so
    claims the whole tree rather than nothing.

    TRAVERSAL is the third case, and it fails SAFE. `tools/../tools/x.py` names exactly
    `tools/x.py`, is relative - so the absolute branch never sees it - and neither matcher
    normalises, so the claim matched NOTHING and the commit rewriting that file landed.
    `--files` / `--paths` accept the spelling and `select_files` builds `root / f`, so this
    tool's own CLI reaches it. Traversal is therefore resolved here, and a claim that resolves
    OUTSIDE the root cannot be spelled repo-relative at all: it becomes the whole-tree claim,
    never a literal pattern that quietly matches nothing."""
    import posixpath
    p = Path(path)
    rel = None
    if p.is_absolute():
        for base in (Path(root).resolve(), Path(root).absolute()):
            try:
                rel = p.relative_to(base).as_posix()
                break
            except ValueError:
                continue
        if rel is None:
            return str(path)
    else:
        rel = p.as_posix()
    normalised = posixpath.normpath(rel)
    if normalised == ".." or normalised.startswith("../"):
        return WINDOW_EVERYTHING
    return normalised


def open_window(root: Path | str, owner: str, paths, note: str | None = None) -> dict:
    """Declare that `owner` may rewrite `paths` until it closes the window.

    Refuses while another window is open, naming who holds it: two declared writers in one tree
    is the hazard itself, and a silent takeover would make the record a decoration."""
    owner = str(owner or "").strip()
    if not owner:
        raise ValueError("a window must name its owner - an anonymous claim tells a blocked "
                         "author nothing about who to ask or what to wait for")
    held = read_window(root)
    if held is not None:
        raise ValueError(
            f"a rewrite window is already open, held by {held['owner']} since "
            f"{held.get('opened_at')} over {', '.join(held.get('paths') or []) or '(unstated)'}"
            f" - two writers in one tree is the hazard this record exists to announce. "
            f"Wait for it, or clear it: {held['clear_with']}")
    record = {
        "owner": owner,
        "opened_at": sdlc_md.now_iso8601(),
        "paths": [window_claim(root, p) for p in (paths or [])],
        "note": note or None,
        "pid": __import__("os").getpid(),
        "clear_with": _clear_hint(owner),
    }
    path = window_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, json.dumps(record, indent=2) + "\n")
    return record


def close_window(root: Path | str, owner: str | None = None) -> dict | None:
    """Clear the window `owner` holds and return what it held, or None when none was open.

    OWNER-SELECTED, not first-by-sort. The reader was generalised to N records while this stayed
    on `read_window`, and all three consequences were reproduced: a holder could not close their
    own window when another record sorted first, a bare close removed whichever sorted first -
    possibly a live run's - and `run`'s own `finally` raised, stranding the window it had just
    opened over a tree nobody was writing to any more.

    With `owner`, only that owner's record is cleared and another writer's is never touched:
    clearing someone else's claim would leave them rewriting the tree with nothing saying so.
    An unreadable record can be cleared by anyone, since nobody can prove whose it was. With no
    `owner`, a single open window is cleared deliberately and several are refused by name -
    "whichever sorted first" is not a choice anyone made."""
    held = read_windows(root)
    if not held:
        return None
    holders = ", ".join(sorted(w["owner"] for w in held))
    name = str(owner or "").strip()
    if name:
        mine = [w for w in held if not w.get("unreadable") and w["owner"] == name]
        mine = mine or [w for w in held if w.get("unreadable")]
        if not mine:
            raise ValueError(
                f"no rewrite window is held by {name} - the open one(s) are held by {holders}."
                f" Refusing to clear another writer's claim: ask them to close it, or clear it "
                f"deliberately with no --owner once you have confirmed nothing is rewriting "
                f"the tree")
        target = mine[0]
    elif len(held) > 1:
        raise ValueError(
            f"{len(held)} rewrite windows are open, held by {holders} - name whose to clear "
            f"with --owner rather than removing whichever record happens to sort first, which "
            f"may be a live run's")
    else:
        target = held[0]
    try:
        # the record this read, not a fixed filename: the contract has two spellings, and
        # unlinking the one this tool happens to write would leave a reviewer's own record open
        # while reporting it closed
        Path(target.get("record_path") or window_path(root)).unlink()
    except FileNotFoundError:
        pass
    return target


def _recover_stranded(root: Path) -> list[str]:
    """Restore any mutant a killed previous run stranded on disk, from its sidecar.

    Returns the recovered paths. Raises ValueError when the sidecar exists but cannot
    be parsed - a run died mid-mutant AND its recovery record is gone, so the only
    honest move is to refuse and name the manual restore source.
    """
    import base64
    sidecar = _inflight_path(root)
    if not sidecar.exists():
        return []
    try:
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            # valid JSON is not enough: a list/string/number parses and then has no .items()
            raise ValueError(f"sidecar holds {type(data).__name__}, not an object")
        entries = [(p, base64.b64decode(b64)) for p, b64 in data.items()]
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError(
            f"in-flight sidecar {sidecar} is unreadable ({exc}): a previous run died "
            "mid-mutant and its recovery record is corrupt - restore the target files "
            f"from git, delete {sidecar}, then re-run") from exc
    recovered = []
    for p, original in entries:
        Path(p).write_bytes(original)
        _purge_bytecode(Path(p))
        recovered.append(p)
    sidecar.unlink()
    return recovered


def dirty_targets(repo_root: Path | str, files) -> list[str] | None:
    """Target files git reports as carrying uncommitted work, or None when git cannot answer.

    None means UNKNOWN, never clean. Outside a work tree (every temp-directory fixture, and a
    consuming project not under git) there is no committed state to compare against, so the
    honest answer is that the question was not asked - the caller records that rather than
    reporting a clean tree it never checked.

    Why this exists at all: this engine rewrites files in place and restores them from bytes it
    read at apply time, and every published remedy for a stranded mutant says restore the target
    from git. Over a file carrying uncommitted work, neither move can tell the mutant from the
    work - so a reviewer mutation-testing in an author's live tree can revert a repair with the
    suite still green. Refusing is the only answer that does not silently destroy something.

    Staged, unstaged and untracked all count: an untracked target has no committed state to
    restore from at all, which is the same hazard with nothing to recover.
    """
    import os
    paths = [str(Path(f)) for f in files]
    if not paths:
        return []
    # Scrub repo-redirecting env for the same reason gate.py does: this may run from inside
    # ANOTHER repo's hook, and an inherited GIT_DIR would make git answer for that repo.
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    try:
        inside = subprocess.run(["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True, timeout=10, env=env)
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return None
        proc = subprocess.run(["git", "-C", str(repo_root), "status", "--porcelain",
                               "--untracked-files=all", "--", *paths],
                              capture_output=True, text=True, timeout=30, env=env)
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    found = set()
    for line in proc.stdout.splitlines():
        name = line[3:].strip()
        if not name:
            continue
        if " -> " in name:            # a rename reports `old -> new`; the new path is the target
            name = name.split(" -> ", 1)[1]
        found.add(name.strip('"'))
    return sorted(found)


@contextlib.contextmanager
def applied(mutation: dict, sidecar: Path | None = None):
    """Apply one mutation; ALWAYS restore the original bytes, even when the
    runner raises - the engine must never leave a mutant on disk.

    With `sidecar`, the original bytes are persisted BEFORE the mutant lands and the
    record is cleared only after the restore, so a SIGKILL mid-test (which skips this
    `finally` and every handler) still leaves the next run a true restore source
    rather than letting it read the stranded mutant back as the original."""
    import base64
    path = Path(mutation["file"])
    original = path.read_bytes()
    replacement = mutated_text(mutation).encode("utf-8")
    if replacement == original:
        # Surviving a patch that changed nothing is evidence about nothing. Refuse
        # rather than run it: a no-op counted as SURVIVED understates the tests, and
        # counted as KILLED overstates them.
        raise ValueError(
            f"mutation at {path}:{mutation.get('line')} does not change the file - "
            "refusing to run a no-op mutant")
    _APPLIED[str(path)] = original
    if sidecar is not None:
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        sidecar.write_text(json.dumps(
            {str(path): base64.b64encode(original).decode("ascii")}), encoding="utf-8")
    try:
        path.write_bytes(replacement)
        _purge_bytecode(path)
        yield
    finally:
        path.write_bytes(original)
        _purge_bytecode(path)
        _APPLIED.pop(str(path), None)
        if sidecar is not None:
            try:
                sidecar.unlink()
            except FileNotFoundError:
                pass


def _viability(path: Path, mutated: str) -> str | None:
    """None when the mutant is (as far as we can tell) runnable; else the reason it
    is UNVIABLE. A mutant that cannot even parse fails ANY suite - counting it
    killed would let a vacuous suite earn evidence. Python is compile-checked;
    other languages have no cheap check (their profiles are shape-restricted instead)."""
    if path.suffix == ".py":
        try:
            compile(mutated, str(path), "exec")
        except (SyntaxError, ValueError) as exc:
            return f"mutant does not compile: {exc.msg if hasattr(exc, 'msg') else exc}"
    return None


#: The last test run's captured output, so `_killing_test` can read it without changing the
#: `_run_tests` contract every caller depends on. A single slot: the run loop is sequential.
_LAST_RUN_OUTPUT = [""]

#: How much of one run's transcript is kept. Enough for any runner's failure summary, bounded
#: so a verbose suite cannot hold an unbounded string in memory for the length of a run.
_OUTPUT_CAP = 512 * 1024

#: How a failing test names itself. pytest's summary line and unittest's FAIL/ERROR header are
#: both matched - a parser knowing one runner would attribute nothing for the other, which is
#: the same silence this fix exists to end.
# pytest's summary line. The node id must LOOK like one - a path or a dotted name carrying a
# `::` or a `.` - because `^(?:FAILED|ERROR)\s+(\S+)` also matches unittest's own summary
# footer `FAILED (failures=2)`, and this repo's gate runs unittest. Every killed mutant was
# being attributed to the literal string `(failures=2)`: a fabricated attribution, in the
# function whose contract is that it must never fabricate one.
_FAILED_NODE = re.compile(r"^(?:FAILED|ERROR)\s+(?P<node>[^\s(][^\s]*(?:::|\.)[^\s]*)", re.M)
# unittest's per-failure header. Python 3.11+ prints the fully-qualified name in the
# parentheses (`FAIL: test_y (tests.test_x.C.test_y)`); older versions print the class only
# (`FAIL: test_y (tests.test_x.C)`). Joining blindly produced `...C.test_y.test_y`, a node id
# that resolves to nothing.
_UNITTEST_FAIL = re.compile(r"^(?:FAIL|ERROR):\s+(?P<meth>\w+)\s+\((?P<ctx>[^)]+)\)", re.M)


def _read_tail(path: str, cap: int | None = None) -> str:
    """The last `cap` bytes of a run's transcript, or "" when it cannot be read.

    The tail, because every runner prints its failure summary at the end, and bounded because a
    verbose suite's full output is unbounded and is held only to find one node id.

    `cap` defaults to `_OUTPUT_CAP`, read at CALL time rather than captured as a default
    argument. Captured, the two are equal-by-coincidence: the constant could be edited with no
    effect here and no test could tell, which is how `_OUTPUT_CAP` came to be a decorative
    definition with a docstring claiming a bound it did not impose."""
    import os  # noqa: PLC0415 - local, matching this module's convention
    cap = _OUTPUT_CAP if cap is None else cap
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as handle:
            if size > cap:
                handle.seek(size - cap)
            return handle.read().decode("utf-8", "replace")
    except OSError:
        return ""


def _killing_test(output: str) -> str | None:
    """The test that killed the mutant, or None when the output does not name one.

    None is honest and is NOT an error: a runner this cannot parse, a suite that prints
    nothing, or a mutant killed by a collection failure all genuinely name no test. The
    consumer treats an unattributed kill as unattributed rather than assuming one."""
    m = _FAILED_NODE.search(output or "")
    if m:
        return m.group("node")
    m = _UNITTEST_FAIL.search(output or "")
    if m:
        ctx, meth = m.group("ctx"), m.group("meth")
        # Do not double the method when the runner already qualified it.
        return ctx if ctx.split(".")[-1] == meth else f"{ctx}.{meth}"
    return None


def _run_tests(test_cmd: str, cwd: Path) -> str:
    """One test run -> 'pass' | 'fail' | 'error' (the runner itself broke).

    The command runs in its own session and the whole process GROUP is killed on EVERY exit
    path - timeout, normal return and exception alike. A compound command's grandchildren must
    not outlive the gate, and the direct child having exited says nothing about what it
    launched: `run_gate` calls this once per mutant, so one backgrounded fixture that survives
    becomes N orphans per run, and against the dev-server case it binds a port that makes every
    subsequent mutant's verdict garbage.

    The environment is `_suite_env()`: no bytecode cache (a same-length mutant would
    otherwise run the ORIGINAL bytecode and be recorded as survived) and the marker that
    exempts this run's own descendants from the applied-mutant guard."""
    import os
    import signal
    env = _suite_env()
    # Output is CAPTURED, not discarded. A killed mutant with no attribution is a killed mutant
    # nobody can act on: `US0507`'s prune-candidate consumer needs the test that did the
    # killing, and with the streams thrown away it took its refusal branch against every real
    # report - a capability unreachable because the only producer never recorded the key.
    #
    # A TEMP FILE, not a pipe. Any pipe ties the read to EOF, which needs every inheritor of
    # stdout to exit - so with `start_new_session=True` a suite that backgrounds anything (a dev
    # server, an xdist worker, an `&`-launched fixture) blocked the full timeout PER MUTANT, and
    # the verdict then flipped from `survived` - an actionable finding - to `error`, silently
    # excusing the mutant. A file has no such semantics: `wait()` returns when the direct child
    # exits, exactly as it did before output was captured at all. The tail is read afterwards,
    # bounded, because a runner's failure summary is at the end.
    #
    # Both the file and the process are created INSIDE the try. Outside it, any Popen failure
    # (a nonexistent cwd is enough) leaked the descriptor and the temp file on every call.
    import tempfile  # noqa: PLC0415 - local, only this path captures
    sink_fd = pgid = None
    sink = ""

    def reap() -> None:
        """Kill the whole session. Safe to call twice; a no-op once it is already gone.

        The group id is the CHILD'S PID, captured while it is alive, never `os.getpgid` after
        the fact: `wait()` reaps the process, so a later lookup raises `ProcessLookupError`, the
        suppression swallows it and nothing is killed. `start_new_session=True` makes the child
        its own session and group leader, so its pid IS the group id."""
        if pgid is not None:
            with contextlib.suppress(ProcessLookupError, PermissionError, OSError):
                os.killpg(pgid, signal.SIGKILL)

    try:
        sink_fd, sink = tempfile.mkstemp(prefix="mutation_run_", suffix=".log")
        proc = subprocess.Popen(test_cmd, shell=True, cwd=cwd, start_new_session=True, env=env,  # nosec B602 - operator-authored test command, same trust boundary as verify_ac's Verify lines
                                stdout=sink_fd, stderr=subprocess.STDOUT)
        pgid = proc.pid
        try:
            rc = proc.wait(timeout=_RUN_TIMEOUT)
        except subprocess.TimeoutExpired:
            # Kill BEFORE the second wait. Waiting first blocks for the command's full natural
            # runtime, which is the hang the timeout exists to bound.
            reap()
            proc.wait()
            return "error"
    finally:
        # UNCONDITIONAL, not only on timeout. Killing the group is what collects whatever the
        # command backgrounded, and with the pipe gone the timeout branch is exactly the path a
        # backgrounded child no longer reaches - so hanging the cleanup off it left the orphan
        # running on every normal exit, once per mutant.
        reap()
        if sink:
            _LAST_RUN_OUTPUT[0] = _read_tail(sink)
        # Separate suppressions: sharing one meant a raising close silently skipped the unlink,
        # so the failure that most needs the file removed is the one that kept it.
        if sink_fd is not None:
            with contextlib.suppress(OSError):
                os.close(sink_fd)
        if sink:
            with contextlib.suppress(OSError):
                os.unlink(sink)
    if rc == 0:
        return "pass"
    if rc in (126, 127):  # not executable / command not found
        return "error"
    return "fail"


def tree_isolation(repo_root: Path | str) -> dict:
    """Was this run measured in a tree of its own? `{isolated, why}`.

    `isolated` is True, False or None, and None is a real answer rather than a soft False: a
    checkout git cannot describe is one whose isolation is UNESTABLISHED, and reporting that as
    shared would be as wrong as reporting it as isolated.

    The rule this exists to make visible: a delegated reviewer mutates in an isolated checkout,
    never a shared tree. `git stash` and `git checkout --` are tree-wide, so one reviewer's
    cleanup silently reverts a concurrent reviewer's mutant, and a result reported SURVIVED may
    never have been on disk when its test ran. That is unsound in BOTH directions, and nothing
    in the counts says so - which is what this qualifier fixes. A linked worktree has its own
    `--git-dir` while sharing `--git-common-dir`; the main worktree's two are the same path.
    """
    import os  # noqa: PLC0415
    import subprocess  # noqa: PLC0415 - only this path needs it
    # `git -C <path>` does NOT override an inherited `GIT_DIR`, so the command described
    # whatever that variable named rather than the tree being measured: with GIT_DIR pointing at
    # a linked worktree, the shared main tree reported `isolated: True` and the warning was
    # suppressed exactly when it is needed. Git hooks set GIT_DIR, and this repo's own hooks run
    # the suites - so the fail-open fired in the most common case there is.
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    try:
        res = subprocess.run(["git", "-C", str(repo_root), "rev-parse",
                              "--absolute-git-dir", "--git-common-dir"],
                             capture_output=True, text=True, check=False, timeout=15, env=env)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"isolated": None, "why": f"git could not be run here ({exc}), so whether this "
                                         f"tree is the author's is UNESTABLISHED"}
    lines = [ln.strip() for ln in res.stdout.splitlines() if ln.strip()]
    if res.returncode != 0 or len(lines) < 2:
        return {"isolated": None,
                "why": "not a git checkout git can describe, so isolation is UNESTABLISHED - "
                       "read the counts knowing they may have been measured in a shared tree"}
    # `--git-common-dir` comes back RELATIVE when git is run from the repo root, so it must be
    # resolved against the repo, never against this process's cwd. Resolving it against the cwd
    # made the two paths differ in every fresh checkout, so the MAIN worktree reported itself
    # isolated - the fail-open direction, and the one the whole qualifier exists to prevent.
    own = Path(lines[0]).resolve()
    common = Path(lines[1])
    common = (common if common.is_absolute() else Path(repo_root) / common).resolve()
    if own != common:
        return {"isolated": True, "why": f"a linked worktree ({own.name}), so no concurrent "
                                         f"reviewer's cleanup could revert a mutant here"}
    # A repo's main worktree is shared only if something ELSE is using it. A private clone -
    # the canonical "isolated checkout of your own" the reviewer brief demands - is a main
    # worktree too, and reporting it SHARED fires the warning on a correctly-isolated reviewer,
    # which trains readers to skim the one line that must not be skimmed. The distinguishing
    # fact is whether this repo has any OTHER worktree attached.
    others = _linked_worktrees(repo_root, env)
    if others == 0:
        return {"isolated": True, "why": "the only worktree of this repository (a private "
                                         "clone), so no concurrent reviewer shares this tree"}
    if others is None:
        return {"isolated": None,
                "why": "the main worktree, and git could not say whether others are attached - "
                       "isolation is UNESTABLISHED, so read the counts knowing a concurrent "
                       "reviewer's tree-wide cleanup may have reverted a mutant"}
    return {"isolated": False,
            "why": f"the MAIN worktree with {others} other worktree(s) attached, so it is "
                   f"shared: a concurrent reviewer's `git stash` or `git checkout --` reverts "
                   f"mutants tree-wide, and a SURVIVED verdict here is not sound evidence "
                   f"unless nothing else was running"}


def _linked_worktrees(repo_root: Path | str, env: dict) -> int | None:
    """How many worktrees OTHER than the main one this repository has, or None when git cannot
    say. None is a real answer: an unanswerable count must not read as zero, which would report
    a shared tree as private."""
    import subprocess  # noqa: PLC0415
    try:
        res = subprocess.run(["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
                             capture_output=True, text=True, check=False, timeout=15, env=env)
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    return max(0, sum(1 for ln in res.stdout.splitlines() if ln.startswith("worktree ")) - 1)


def tree_warning_line(summary: dict) -> str | None:
    """The isolation qualifier to print beside the counts, or None for a confirmed isolated
    tree - the one state nobody needs warning about. A separate function because a field
    nothing renders is a field nobody reads, and the warning has to reach whoever reads the
    KILLED/SURVIVED numbers rather than whoever thinks to open the json."""
    tree = (summary or {}).get("tree") or {}
    if tree.get("isolated") is True:
        return None
    label = "SHARED TREE" if tree.get("isolated") is False else "TREE UNESTABLISHED"
    return f"  {label}: {tree.get('why') or 'no isolation evidence was recorded for this run'}"


def attribute_kill(row: dict, run_output: str) -> dict:
    """Name the test that killed this mutant, in both fields the consumers read.

    A SEAM on purpose. The attribution used to sit inline inside `run_gate`, so the only way to
    check it was to grep the source for the assignment - a guard that stays green with the
    assignment dead, which is exactly what happened. Extracted, the production path is callable,
    so a test asserts the VALUE rather than the presence of a line.

    `killed_by` is a LIST because `tools/test_census.py` reads it; `test` is the scalar. Shipping
    only one of them was the original defect, so both are written from the same name.

    Absent rather than guessed when the runner's output names no test: the consumer reads a
    missing key as unattributed, which is true, where a fabricated one would be evidence about
    the wrong test.
    """
    if row.get("verdict") != "killed":
        return row
    killer = _killing_test(run_output)
    if killer:
        row["killed_by"] = [killer]
        row["test"] = killer
    return row


def run_gate(repo_root: Path | str, files, test_cmd: str,
             max_mutations: int | None = None,
             classes: tuple = FAULT_CLASSES, write_report: bool = True,
             changed: dict | None = None) -> dict:
    """The gate: enumerate, apply one at a time, re-run tests, verdict each mutation.

    Baseline first: the tests must be green over UNMUTATED code. A red or broken baseline
    cannot judge anything, so the gate REFUSES immediately - no mutant is applied, the report
    is marked `refused` with the remedy, and the caller exits non-zero. Running the mutants
    anyway would only produce a worthless all-`error` report the run could mistake for done."""
    import time
    root = Path(repo_root)
    started = time.monotonic()          # the run's own wall-clock, measured, never assumed
    run_id = _new_run_id()
    ceiling = max_mutations if max_mutations is not None else DEFAULT_MAX_MUTATIONS
    all_mutations, unchecked = enumerate_mutations(files, classes)
    # An empty surface is a FIRST-CLASS outcome, not a refusal and not a pass. A surface with no
    # mutatable sites (a docs-only change is the canonical case) has nothing to mutate, so no
    # baseline is run and nothing is proven or disproven - an absence, not a negative result.
    # Recorded honestly here so the gate lane can read 'nothing to mutate' rather than mistaking a
    # zero-mutant run for a clean sweep. Distinct from `refused` (a red baseline judged nothing)
    # and from a measured pass (mutants applied and killed).
    empty_surface = not all_mutations
    to_apply, truncated = apply_budget(all_mutations, ceiling, changed)
    _install_restore_handlers()   # a kill mid-mutant must restore, never strand
    # A SIGKILLed previous run strands its mutant; reading THAT back as the original
    # would poison every restore in this run, so recover from the sidecar first.
    recovered: list[str] = []
    baseline = "error"
    refused = True
    remedy = None
    refusal_kind = None      # WHICH refusal, so the lane can tell an omission from a state
    # Another declared writer in this tree makes this run the SECOND one, which is the hazard
    # itself: refuse before touching a byte, rather than interleaving two processes' rewrites.
    blocking = read_window(root)
    # Uncommitted work on a target is the second way this run destroys something it cannot give
    # back: the mutant and the work become one file, and neither the byte-restore nor the
    # published `restore from git` remedy can separate them. None means git could not answer.
    dirty = None
    if empty_surface:
        # Nothing to mutate: skip the baseline, the window and the loop entirely. A window a
        # concurrent run holds is irrelevant to a run that touches no byte, so it does not block.
        refused = False
        baseline = "not-run"
        blocking = None
    elif blocking is not None:
        remedy = (f"a rewrite window is open, held by {blocking['owner']} over "
                  f"{', '.join(blocking.get('paths') or []) or '(unstated paths)'} - refusing to "
                  f"be the second process rewriting this tree. Wait for it, or clear it: "
                  f"{blocking['clear_with']}")
    elif (dirty := dirty_targets(root, files)):
        baseline = "not-run"
        refusal_kind = UNCOMMITTED_SURFACE
        remedy = (f"uncommitted changes on {', '.join(dirty)} - refusing to mutate a file "
                  f"carrying work that is not committed. A mutant applied over uncommitted work "
                  f"cannot be told apart from that work when the file is restored, so a run that "
                  f"proceeded here could revert it silently. Commit or stash it, or mutate an "
                  f"isolated checkout of it (git worktree add) instead of this tree.")
    else:
        try:
            recovered = _recover_stranded(root)
        except ValueError as exc:
            remedy = str(exc)
        else:
            baseline = _run_tests(test_cmd, root)
            refused = baseline != "pass"
            if refused:
                remedy = ("a red baseline proves nothing: clean the working tree (a stranded "
                          "mutant from a killed run?) or fix the failing suite, then re-run"
                          if baseline == "fail"
                          else "the test command errored on unmutated code: fix the command or "
                               "the environment, then re-run")
    records: list[dict] = []
    if not refused and not empty_surface:
        sidecar = _inflight_path(root)
        # Declare the window BEFORE the first mutant lands and clear it after the last restore.
        # A concurrent `git add -A` is then told a writer is active instead of silently staging
        # whatever this loop has left on disk.
        open_window(root, WINDOW_OWNER_RUN, [str(Path(f)) for f in files],
                    note=f"mutation gate over {len(to_apply)} mutant(s)")
        try:
            for m in to_apply:
                mutated = mutated_text(m)
                unviable_reason = _viability(Path(m["file"]), mutated)
                if unviable_reason:
                    # evidence of nothing: any suite fails on a non-parsing mutant,
                    # so it must never count as killed (nor as survived)
                    records.append({**m, "verdict": "unviable", "reason": unviable_reason})
                    continue
                with applied(m, sidecar=sidecar):
                    outcome = _run_tests(test_cmd, root)
                verdict = {"pass": "survived", "fail": "killed", "error": "error"}[outcome]
                # ATTRIBUTION on a kill. Absent rather than guessed when the runner's output
                # names no test - the consumer reads a missing key as unattributed, which is
                # true, where a fabricated one would be evidence about the wrong test.
                row = attribute_kill({**m, "verdict": verdict}, _LAST_RUN_OUTPUT[0])
                records.append(row)
        finally:
            # Never raise out of the restore path. A window this run cannot find - cleared by
            # hand mid-run, or replaced - would otherwise become the exception that buries the
            # run's own result, and it did: another record sorting first made this close refuse
            # and strand the very window it was clearing.
            with contextlib.suppress(ValueError):
                close_window(root, owner=WINDOW_OWNER_RUN)
    summary = {
        "tree": tree_isolation(root),
        "applied": len(records),
        "killed": sum(1 for r in records if r["verdict"] == "killed"),
        "survived": sum(1 for r in records if r["verdict"] == "survived"),
        "errors": sum(1 for r in records if r["verdict"] == "error"),
        "unviable": sum(1 for r in records if r["verdict"] == "unviable"),
        "truncated": truncated,
        "enumerated": len(all_mutations),
    }
    # Diff coverage: of the mutants sitting on changed lines, how many did the ceiling
    # actually reach? A truncated run that covered the whole diff is far stronger evidence
    # than one that sampled 8% of it, and the difference must be legible in the report
    # rather than inferred from `truncated` (L-0073: a bound that can bite must say so).
    if changed:
        on_diff_total = sum(1 for m in all_mutations if _on_diff(m, changed))
        on_diff_applied = sum(1 for r in records if _on_diff(r, changed))
        summary["diff_mutations"] = on_diff_total
        summary["diff_applied"] = on_diff_applied
        summary["diff_covered"] = (on_diff_total == on_diff_applied)
    # What the survivors were measured AGAINST: the files the command selects, and the
    # referencing test files it does NOT select (the manufactured-survivor condition).
    # Advisory - computed even on a refused run, so a report is never read blind.
    selected = _selected_test_files(root, test_cmd)
    selection_warnings = _selection_warnings(root, files, selected)
    # A FRESHNESS stamp over the surface this run was pointed at, and never evidence: it is
    # computed from `files`, outside every verdict and refusal path, so it names a file the
    # cost ceiling never reached and every target of a refused run. What was PROVEN is the
    # ledger below, which enters a target only on a killed-or-survived verdict. A consumer
    # that reads this field as coverage reports files no mutant ran on; that is what happened.
    import hashlib
    target_hashes = {}
    for fp in files:
        try:
            target_hashes[str(Path(fp))] = hashlib.sha256(Path(fp).read_bytes()).hexdigest()
        except OSError:
            target_hashes[str(Path(fp))] = None
    report = {
        "run_id": run_id,
        "generated_at": sdlc_md.now_iso8601(),
        "git_rev": _git_rev(root),
        "target_hashes": target_hashes,
        "test_cmd": test_cmd,
        "targets": [str(Path(f)) for f in files],
        "baseline": baseline,
        "refused": refused,
        "refusal_kind": refusal_kind,
        "empty_surface": empty_surface,
        "remedy": remedy,
        "blocked_by_window": blocking,
        "dirty_targets": dirty,
        "recovered": recovered,
        "selected_tests": ([str(p) for p in selected] if selected is not None else None),
        "selection_warnings": selection_warnings,
        "mutations": records,
        "unchecked": unchecked,
        "summary": summary,
    }
    report["elapsed_s"] = round(time.monotonic() - started, 3)
    if write_report:
        report["ledger"] = append_ledger(root, report, records)
        # The per-run series, written whatever the outcome: a refused or all-errored run costs
        # wall-clock too, and a series that recorded only the runs that worked would flatter the
        # gate exactly where CR0379 wants it judged.
        report["series"] = append_series(root, report, report["elapsed_s"])
        out = root / "sdlc-studio" / ".local" / "mutation-report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def ledger_path(root: Path | str) -> Path:
    """Where the accumulating per-target evidence lives, beside the latest-run report."""
    return Path(root) / "sdlc-studio" / ".local" / "mutation-runs.json"


# --- The per-run cost/yield series -----------------------------------------------------------
#
# The report is last-write-wins and the ledger supersedes a target's earlier numbers, so neither
# answers "what has this gate cost and what has it found". The series is the third file and the
# only per-RUN one: append-only, one JSON object per line, in the same shape `verify_ac.py` uses
# for `verify-history.jsonl` - and bounded by the same shared roller, so it cannot grow without
# limit while the trailing history stays long enough to read a trend from.


def series_path(root: Path | str) -> Path:
    """The append-only per-run series: one row per run, cost beside counts."""
    return Path(root) / "sdlc-studio" / ".local" / "mutation-series.jsonl"


def series_rows(root: Path | str) -> list[dict]:
    """Every readable row of the series, oldest first. A line that does not parse as an object
    is skipped rather than raising: a reader of the history must not die on one bad line."""
    path = series_path(root)
    if not path.exists():
        return []
    rows: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _series_malformed(path: Path) -> bool:
    """True when the file on disk is not a clean JSONL of objects. Checked before an append,
    because appending a good row to a corrupt file leaves a file that is still corrupt."""
    if not path.exists():
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return True
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            return True
        if not isinstance(row, dict):
            return True
    return False


def _new_run_id() -> str:
    """A per-run identity an artefact can point back at. Timestamped so the series sorts
    readably, with random bytes so two runs in the same second never collide."""
    import secrets
    from datetime import datetime, timezone
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    return f"MRUN-{stamp}-{secrets.token_hex(3)}"


def mutants_over_changed_lines(repo_root, files, since: str) -> tuple[list, dict]:
    """Mutants confined to the lines this unit actually CHANGED since `since`.

    `(mutations, changed)` - the second is the map the scoping was derived from, returned so a
    caller can report what it measured rather than assert it.

    The scope is the criterion, not an optimisation. A repair touching nine lines of a
    two-thousand-line module should be held to those nine: generating over the whole `Affects`
    makes the gate cost scale with the file rather than the change, and a gate nobody can afford
    to run is one that gets switched off - which is how the release verify lane reached 106 red
    criteria unobserved.
    """
    changed = changed_lines(repo_root, since)
    if not changed:
        return [], {}
    muts, _unchecked = enumerate_mutations(list(files))
    scoped = [m for m in muts
              if m["line"] in changed.get(str(Path(m["file"]).resolve()), set())
              or m["line"] in changed.get(str(m["file"]), set())]
    return scoped, changed


def series_reason(report: dict) -> str | None:
    """Why this run carries no measured evidence, or None when it does.

    A FUNCTION rather than a comprehension inside `append_series`, so a test has to call it
    instead of recomputing the same expression - a test that recomputes production passes
    whatever production does, and a mutant emptying it survives (the shape BG0516 hit).
    """
    s = report.get("summary") or {}
    killed, survived = int(s.get("killed", 0)), int(s.get("survived", 0))
    refused = bool(report.get("refused"))
    # An empty surface carries no evidence, but for a different reason than a refusal or an
    # all-errored run: there was nothing to mutate. Named as its own outcome so a summed series
    # can tell a docs-only run from one whose mutants all failed to judge anything.
    empty = bool(report.get("empty_surface"))
    evidence = (not refused) and (not empty) and (killed + survived) > 0
    if refused and report.get("refusal_kind") == UNCOMMITTED_SURFACE:
        # NOT "no evidence". A surface the runner correctly refused to mutate and one nobody
        # ever tested are different facts, and only the second is the author's omission. An
        # advisory that says the same about both teaches an author to ignore it (US0573).
        reason = (
            "the changed surface carries UNCOMMITTED work, so the runner refused to mutate it - "
            "this is not 'no evidence', it is evidence not yet obtainable here. Two routes give "
            "a measured verdict: mutate an ISOLATED CHECKOUT (`git worktree add`), or apply the "
            "mutant by hand and record it with `mutation.py register --unit <id> --criterion "
            "ACn`. A hand run is only trustworthy with the discipline that makes it so - assert "
            "the anchor occurs exactly once before patching, purge `__pycache__` and run the "
            "child under `python3 -B` so a cached module cannot report a false survival, and "
            "restore from captured bytes with the restoration asserted byte-identical.")
    elif refused:
        reason = f"run refused - baseline {report.get('baseline')}, no mutant was applied"
    elif empty:
        reason = "the selected surface has no mutatable sites - nothing to mutate"
    elif not evidence:
        reason = (f"{int(s.get('applied', 0))} mutant(s) applied and none returned a killed or "
                  f"survived verdict (unviable, errored or timed out) - nothing was judged")
    else:
        reason = None
    return reason


def append_series(root: Path | str, report: dict, elapsed_s: float) -> dict:
    """Append this run's row to the series and report what happened to the file.

    EVIDENCE is the property the row exists to carry. A run that was refused by the baseline
    guard, or that ended with no killed and no survived verdict (every mutant unviable, errored
    or timed out), judged nothing - so it is recorded as `no-evidence` with the reason named.
    Summing the series without that flag would count a 40-minute refusal as a clean run, which
    is the reading CR0379 exists to make impossible.

    A malformed file is REPLACED rather than appended to, and the replacement is reported to the
    caller (`reset`) so the run can say so on stdout - a silently rewritten history is a history
    nobody can trust.
    """
    path = series_path(root)
    s = report.get("summary") or {}
    killed, survived = int(s.get("killed", 0)), int(s.get("survived", 0))
    refused = bool(report.get("refused"))
    # Recomputed here because `series_reason` owns the WORDING and this row owns the FACT -
    # one is prose a reader sees, the other a boolean a later lane sums. Deriving the boolean
    # from the prose would make a rewording change what the series counts.
    empty = bool(report.get("empty_surface"))
    evidence = (not refused) and (not empty) and (killed + survived) > 0
    reason = series_reason(report)
    row = {
        "run_id": report.get("run_id"),
        "at": report.get("generated_at"),
        "git_rev": report.get("git_rev"),
        "test_cmd": report.get("test_cmd"),
        "targets": list(report.get("targets") or []),
        "applied": int(s.get("applied", 0)),
        "killed": killed,
        "survived": survived,
        "errors": int(s.get("errors", 0)),
        "unviable": int(s.get("unviable", 0)),
        "truncated": int(s.get("truncated", 0)),
        "unchecked": len(report.get("unchecked") or []),
        "elapsed_s": round(float(elapsed_s), 3),
        "evidence": evidence,
        "outcome": ("nothing-to-mutate" if empty else "measured" if evidence else "no-evidence"),
        "no_evidence_reason": reason,
        # The tree the counts were measured in, RECORDED as well as printed. Without it the fact
        # was recoverable only from the run's own stdout, so every later reader of the series -
        # the close report, the gate - saw KILLED/SURVIVED with no way to tell a private
        # checkout's numbers from a shared tree's.
        "tree": (s.get("tree") or {}),
    }
    reset = _series_malformed(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if reset:
        sdlc_md.atomic_write(path, json.dumps(row) + "\n")
    else:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
    rolled = sdlc_md.roll_jsonl(path)
    return {"path": str(path), "rows": len(series_rows(root)),
            "reset": reset, "rolled": rolled, "row": row}


def series_row(root: Path | str, run_id: str) -> dict | None:
    """The series row for one run, or None when the series holds no such run. None is what makes
    an attribution refusable: a link to a run nobody recorded can never be checked."""
    if not run_id:
        return None
    for row in reversed(series_rows(root)):
        if row.get("run_id") == run_id:
            return row
    return None


def _artefacts_filed_from(root: Path | str, run_id: str) -> list[str]:
    """The ids of findings whose `Mutation-run` metadata names this run, sorted.

    A survivor is a hypothesis; a filed artefact is a finding. This is the only count that may
    be called the run's YIELD, because it is the only one somebody judged worth acting on."""
    found: list[str] = []
    root = Path(root)
    for type_ in sdlc_md.FINDING_TYPES:
        for path in sdlc_md.artifact_files(type_, root):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if (sdlc_md.extract_field(text, "Mutation-run") or "").strip() == run_id:
                found.append(sdlc_md.extract_record_id(path.stem) or path.stem)
    return sorted(found)


def _equivalents_of(root: Path | str, run_id: str) -> list[dict]:
    """Every mutant registered `equivalent` against this run, newest last. Read back out of the
    ledger where the verdict lives, so the exclusion is visible wherever the verdicts are."""
    state, _ = _load_ledger(ledger_path(root))
    out: list[dict] = []
    for entry in state["entries"]:
        if not isinstance(entry, dict):
            continue
        for rec in entry.get("mutants") or []:
            if (isinstance(rec, dict) and rec.get("verdict") == EQUIVALENT_VERDICT
                    and rec.get("run") == run_id):
                out.append({"mutant": rec.get("mutant"), "reason": rec.get("reason"),
                            "verdict": EQUIVALENT_VERDICT, "target": entry.get("target"),
                            "at": rec.get("at")})
    return out


def run_yield(root: Path | str, run_id: str) -> dict:
    """What one mutation run COST and what it FOUND, with the two kept apart.

    `survivors` is what the run raised; `yield` is what somebody then filed from it, and the two
    are never conflated - RUN-01KY03GS raised three survivors of which two became bugs, so
    counting survivors would have overstated it by half. `equivalent` names the survivors judged
    unkillable, excluded from both counts and quoted with their reasons so the exclusion is
    auditable. `outstanding` is what is left: raised, not filed, not excused.

    An unknown run reports `found: False` with null counts rather than a tidy row of zeros - a
    run nobody recorded has no yield of zero, it has no yield at all.
    """
    row = series_row(root, run_id)
    if row is None:
        return {"run": run_id, "found": False, "survivors": None, "filed": [], "yield": 0,
                "equivalent": [], "outstanding": None, "elapsed_s": None, "evidence": False}
    filed = _artefacts_filed_from(root, run_id)
    equivalent = _equivalents_of(root, run_id)
    survivors = int(row.get("survived", 0))
    return {
        "run": run_id, "found": True,
        "survivors": survivors,
        "filed": filed,
        "yield": len(filed),
        "equivalent": equivalent,
        "outstanding": max(0, survivors - len(filed) - len(equivalent)),
        "elapsed_s": row.get("elapsed_s"),
        "evidence": bool(row.get("evidence")),
        "row": row,
    }


def _ledger_target(root: Path, fp) -> str:
    """Repo-relative target path where possible, so the ledger survives a moved checkout."""
    p = Path(fp)
    try:
        return str(p.resolve().relative_to(Path(root).resolve()))
    except (ValueError, OSError):
        return str(p)


def append_ledger(root: Path | str, report: dict, records: list[dict]) -> dict:
    """Append this run's per-target evidence to the bounded ledger and return its state.

    One report is last-write-wins: a per-unit run mid-sprint erases the previous unit's
    evidence, and the whole blob goes stale as soon as any file is committed. The ledger is
    the durable half - a per-target entry carrying that file's content hash AT RUN TIME, so
    a later commit touching OTHER files leaves it readable.

    ONE rule decides what is recorded, because recording more would claim evidence the run did
    not gather: a target is entered only when the test command returned a killed or survived
    verdict on it. A target whose mutants were all unviable, all errored, or fell beyond the
    cost ceiling is therefore absent, and so is every target of a refused run - a refusal
    applies no mutant at all, so no target has a verdict. A separate `refused` test here would
    read as a second rule while being pinned by nothing: deleting it as a hand-applied
    mutant survived the whole suite.

    Bounded at LEDGER_LIMIT entries, oldest dropped first, with a cumulative `dropped` count
    so the truncation is never silent. An unreadable ledger is replaced and says so (`reset`).
    """
    root = Path(root)
    path = ledger_path(root)
    state, reset = _load_ledger(path)
    new: list[dict] = []
    for fp in report.get("targets", []):
        rs = [r for r in records if str(Path(r["file"])) == str(Path(fp))]
        # Built from SUMMARY_VERDICTS, not from a hand-written list. The two writers of a
        # ledger summary (here, and `register_mutant`) hard-coded their own counters, so a
        # verdict added to the vocabulary was countable in one and absent from the other -
        # exactly what the constant's comment says cannot happen. Now it cannot.
        summary = {"applied": len(rs), **{k: 0 for k in SUMMARY_VERDICTS}}
        for r in rs:
            key = RUN_VERDICT_COUNTER.get(r["verdict"])
            if key:
                summary[key] += 1
        if not summary["killed"] and not summary["survived"]:
            continue
        digest = (report.get("target_hashes") or {}).get(str(Path(fp)))
        new.append({"target": _ledger_target(root, fp), "hash": digest,
                    "provenance": PROVENANCE_MEASURED,
                    "git_rev": report.get("git_rev"),
                    "generated_at": report.get("generated_at"),
                    "test_cmd": report.get("test_cmd"), "summary": summary})
    # A run supersedes its OWN kind only. A later run's numbers replace an earlier run's for the
    # same target, but a hand-registered claim about that file is a different statement, not a
    # stale copy of this one, and dropping it here would delete evidence this run never gathered.
    superseded = {e["target"] for e in new}
    entries = [e for e in state["entries"]
               if isinstance(e, dict)
               and not (e.get("target") in superseded
                        and entry_provenance(e) == PROVENANCE_MEASURED)] + new
    return _store_ledger(path, state, entries, reset)


def _load_ledger(path: Path) -> tuple[dict, bool]:
    """(state, reset). An unreadable ledger yields a fresh state and `reset` True, so the
    replacement is reported rather than looking like an empty history."""
    state: dict = {"version": 1, "dropped": 0, "entries": []}
    if not path.exists():
        return state, False
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or not isinstance(loaded.get("entries"), list):
            raise ValueError("ledger is not a {entries: [...]} object")
        return {"version": loaded.get("version", 1),
                "dropped": int(loaded.get("dropped", 0) or 0),
                "entries": loaded["entries"]}, False
    except (ValueError, OSError, TypeError):
        return state, True


def _store_ledger(path: Path, state: dict, entries: list[dict], reset: bool) -> dict:
    """Bound the ENTRY COUNT, write, and report. ONE truncation point for that axis, so every
    writer meets the same limit however it arrived here.

    It is not the only axis. A registration accumulates into an existing entry rather than
    adding one, so this bound never fires on a repeated `register` against unchanged content -
    `register_mutant` bounds that entry's own mutant list at MUTANT_LIMIT before calling here.

    An empty result over a ledger that does not exist yet writes nothing."""
    dropped_now = max(0, len(entries) - LEDGER_LIMIT)
    state["entries"] = entries[dropped_now:]
    state["dropped"] += dropped_now
    state["limit"] = LEDGER_LIMIT
    if reset:
        state["reset"] = True
    if not state["entries"] and not path.exists():
        # nothing was proven and there is no ledger yet: do not create an empty one
        return {"path": str(path), "entries": 0, "dropped_now": 0,
                "dropped_total": state["dropped"], "written": False}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return {"path": str(path), "entries": len(state["entries"]), "dropped_now": dropped_now,
            "dropped_total": state["dropped"], "written": True}


def register_mutant(root: Path | str, target, mutant: str, test: str, verdict: str,
                    reason: str | None = None, run: str | None = None,
                    unit: str | None = None, criterion: str | None = None) -> dict:
    """Record a mutant that was ALREADY applied by hand, against the target's content NOW.

    The practice this exists for: a builder writes a test, applies a mutant to the code it
    pins, confirms the test goes RED, and restores. That is stronger per-unit evidence than a
    blanket sampling run, and until now it left no trace at all - so a sprint that followed the
    policy for 75 mutants closed with the coverage lane reading 0/4. Forcing the practice
    through a full run instead would have changed the practice to suit the tool.

    WHAT THIS IS NOT. Nothing here applies a mutant, runs a test, or checks the claim in any
    way. The entry is a self-report, marked `registered` so no reader can mistake it for a run,
    and it is deliberately kept in the SAME ledger as the measured entries so a lane cannot
    accidentally read one file and miss the other.

    Keyed on the target's content hash, exactly as a run's entry is: an edit to the target
    starts the entry again, because the earlier claim was about bytes that no longer exist.
    Registrations on unchanged content ACCUMULATE, since a builder applies many mutants to one
    file across a sprint and overwriting per call would leave the ledger permanently reading 1.
    Accumulation is bounded at MUTANT_LIMIT descriptions per entry, oldest out - the entry
    count never grows on this path, so the ledger's own bound cannot reach it.

    A `survived` verdict is a FINDING, not a filing: the test named against it does not pin the
    behaviour that was mutated. The gate's coverage lane reads it back out of the entry's
    summary and counts it, so recording bad news is never quieter than recording nothing.

    An `equivalent` verdict is the one EXCLUSION the vocabulary allows: the mutant changed no
    observable behaviour, so no test could have killed it and counting it as an outstanding
    survivor would overstate what the gate found. It demands a `reason` - an exclusion nobody
    justified is a decrement nobody can audit - and takes no test, because there is no test to
    name. `run` attributes it to the series row it discounts, so the exclusion applies to the
    run that raised the survivor and to no other.

    Raises ValueError on a target that cannot be read, an unknown verdict, an empty description,
    an equivalent verdict with no reason, or a run id the series does not hold: an entry that
    names neither what was mutated nor what judged it is unauditable, and one with no hash could
    never go stale.
    """
    import hashlib
    root = Path(root)
    path = Path(target)
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        raise ValueError(f"no such target: {path} - a registered entry is keyed on the "
                         "target's content hash, and a file that cannot be read has none")
    if verdict not in REGISTRABLE_VERDICTS:
        raise ValueError(f"verdict must be one of {', '.join(REGISTRABLE_VERDICTS)}, "
                         f"not {verdict!r}")
    mutant, test = str(mutant or "").strip(), str(test or "").strip()
    reason = str(reason or "").strip()
    if verdict == EQUIVALENT_VERDICT:
        if not mutant or not reason:
            raise ValueError(
                "an equivalent mutant must name WHAT was mutated and give a reason it could "
                "not be killed - an exclusion nobody justified is a silent decrement, "
                "indistinguishable from a mutant nobody ran")
    elif not mutant or not test:
        raise ValueError("a registered mutant must name WHAT was mutated and WHICH test "
                         "returned the verdict - a bare count cannot be audited")
    run = str(run or "").strip() or None
    if run is not None and series_row(root, run) is None:
        raise ValueError(f"no mutation run {run} in the series - a verdict attributed to a run "
                         "nobody recorded discounts nothing and can never be checked")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rel = _ledger_target(root, path)
    lpath = ledger_path(root)
    state, reset = _load_ledger(lpath)
    entries = [e for e in state["entries"] if isinstance(e, dict)]
    record = {"mutant": mutant, "test": test or None, "verdict": verdict,
              "reason": reason or None, "run": run,
              # THE JOIN KEY for `run --from-plan` (US0632). Recorded explicitly rather than
              # matched out of the mutant's prose: a matching rule that is convenient is a gate
              # that is optional, and a substring join would silently credit one criterion's
              # execution to another's row.
              "unit": sdlc_md.norm_id(unit) if unit else None,
              "criterion": (criterion or "").strip().upper() or None,
              "at": sdlc_md.now_iso8601()}
    entry = next((e for e in entries if e.get("target") == rel
                  and entry_provenance(e) == PROVENANCE_REGISTERED
                  and e.get("hash") == digest), None)
    # any registered entry for this target on OTHER content is stale evidence: drop it rather
    # than carry counts about bytes this file no longer has
    entries = [e for e in entries
               if not (e.get("target") == rel
                       and entry_provenance(e) == PROVENANCE_REGISTERED
                       and e is not entry)]
    if entry is None:
        entry = {"target": rel, "hash": digest, "provenance": PROVENANCE_REGISTERED,
                 "git_rev": _git_rev(root), "generated_at": record["at"], "test_cmd": None,
                 "summary": {"applied": 0, **{k: 0 for k in SUMMARY_VERDICTS}},
                 "mutants": []}
    else:
        entries.remove(entry)              # re-appended below, so the newest entry sorts last
        entry["git_rev"] = _git_rev(root)
        entry["generated_at"] = record["at"]
    entry.setdefault("mutants", []).append(record)
    entry["summary"]["applied"] += 1
    # setdefault, not [verdict] += 1: an entry written before this verdict existed has no such
    # counter, and a KeyError on an older ledger would make the vocabulary's growth a crash
    entry["summary"][verdict] = entry["summary"].get(verdict, 0) + 1
    # The list is what grows here, and the ledger's entry bound cannot reach it: this entry is
    # rewritten, never added. Bounded on its own axis, newest kept, and what was dropped is
    # recorded - the summary tally below is never truncated, so the COUNT of what was
    # registered stays exact even when the oldest descriptions have gone.
    over = max(0, len(entry["mutants"]) - MUTANT_LIMIT)
    if over:
        entry["mutants"] = entry["mutants"][over:]
        entry["dropped_mutants"] = int(entry.get("dropped_mutants") or 0) + over
    entries.append(entry)
    written = _store_ledger(lpath, state, entries, reset)
    return {**written, "target": rel, "verdict": verdict,
            "registered": entry["summary"]["applied"],
            "retained": len(entry["mutants"])}


def select_files(repo_root: Path | str, files=None, since: str | None = None,
                 story: str | None = None, strategy: list[str] | None = None) -> list[Path]:
    """Resolve the target surface: explicit --files, `git diff --name-only <since>`,
    or a story's chain (story -> epic -> CR `Affects`, existing files only)."""
    root = Path(repo_root)
    if files:
        return [Path(f) if Path(f).is_absolute() else root / f for f in files]
    if since:
        diff = subprocess.run(["git", "diff", "--name-only", since], cwd=root,
                              capture_output=True, text=True, check=True)
        untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                                   cwd=root, capture_output=True, text=True, check=True)
        # brand-new (untracked) modules are the canonical new-file work - dropping
        # them would silently thin the surface below what was declared
        out = []
        for name in diff.stdout.splitlines() + untracked.stdout.splitlines():
            p = root / name.strip()
            if p.suffix in PROFILES and p.exists() and p not in out:
                out.append(p)
        return out
    if story:
        return _story_surface(root, story)
    if strategy:
        return _strategy_surface(root, strategy)
    raise ValueError("select a surface: --files, --since REF, --story USxxxx, or "
                     "--strategy (the units the plan-time test strategy named)")


def _strategy_surface(root: Path, batch: list[str]) -> list[Path]:
    """The files of the units whose plan-time risk band demanded mutation evidence.

    This replaces the blanket close-scoped sweep over a whole sprint diff. The difference is
    not size, it is provenance: a sweep spends its ceiling on whatever it reaches first, while
    this spends it on units a stated strategy said were worth mutating - a decision made at
    plan time, in the open, and checkable against what the close actually produced.
    """
    import sprint  # noqa: PLC0415 - the strategy has one definition, in the planner
    out: list[Path] = []
    for uid in sprint.strategy_mutation_targets(root, batch):
        hit = sdlc_md.find_by_id(root, uid)
        if not hit:
            continue
        affects = sdlc_md.extract_field(sdlc_md.read_text_safe(Path(hit[0])), "Affects") or ""
        for name in re.split(r"[,\s]+", affects):
            p = root / name.strip()
            if name.strip() and p.suffix in PROFILES and p.exists() and p not in out:
                out.append(p)
    return out


def _story_surface(root: Path, story_id: str) -> list[Path]:
    """Story -> its epic -> the epic's CR -> the CR's `Affects` paths that exist."""
    norm = sdlc_md.norm_id(story_id)
    story = next((p for p in sdlc_md.artifact_files("story", root)
                  if sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or "") == norm), None)
    if story is None:
        raise ValueError(f"no story found for {story_id!r}")
    chain = [story.read_text(encoding="utf-8")]
    ef = sdlc_md.extract_field(chain[0], "Epic") or ""
    m = sdlc_md.ID_SEARCH_RE.search(ef)
    if m:
        epic = next((p for p in sdlc_md.artifact_files("epic", root)
                     if sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or "")
                     == sdlc_md.norm_id(m.group(0))), None)
        if epic:
            etext = epic.read_text(encoding="utf-8")
            chain.append(etext)
            cf = sdlc_md.extract_field(etext, "CR") or ""
            cm = sdlc_md.ID_SEARCH_RE.search(cf)
            if cm:
                cr = next((p for p in sdlc_md.artifact_files("cr", root)
                           if sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or "")
                           == sdlc_md.norm_id(cm.group(0))), None)
                if cr:
                    chain.append(cr.read_text(encoding="utf-8"))
    out: list[Path] = []
    for text in chain:
        for tok in (sdlc_md.extract_field(text, "Affects") or "").split(","):
            tok = tok.strip().strip("`")
            for base in (root, root / ".claude" / "skills" / "sdlc-studio"):
                cand = base / tok
                if tok and cand.exists() and cand.suffix in PROFILES and cand not in out:
                    out.append(cand)
    return out


_TEST_FILE_PATTERNS = ("test_*.py", "*_test.py")
_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".local", ".venv", "venv"}


def _drop_ignored(root: Path, paths: list[Path]) -> list[Path]:
    """Remove git-IGNORED paths from a candidate set. The canonical case is a stale git worktree
    under a gitignored dir (`.claude/worktrees/agent-*/`): its duplicate copies of every test are
    not the repo's tests, and scanning them pads the covering command with dozens of worktree paths
    and re-runs their (possibly stale) copies. Filtering on `.gitignore` rather than on a path
    component named `worktrees` avoids the recorded scar where the component match skipped the whole
    tree when the tool was run from INSIDE a worktree. One batched `git check-ignore`; on any git
    failure it returns the paths unfiltered - best-effort, it must never break the scan."""
    if not paths:
        return paths
    try:
        rels = [str(p.relative_to(root)) if p.is_absolute() and str(p).startswith(str(root))
                else str(p) for p in paths]
        r = subprocess.run(["git", "-C", str(root), "check-ignore", "--stdin"],
                           input="\n".join(rels), capture_output=True, text=True)
        ignored = set(r.stdout.splitlines())
        return [p for p, rel in zip(paths, rels) if rel not in ignored]
    except Exception:  # noqa: BLE001 - no git, not a repo, anything: the scan degrades, never breaks
        return paths


def _candidate_test_files(root: Path) -> list[Path]:
    """Every test-shaped file under root (skipping vendored/derived trees and gitignored paths -
    the latter is what keeps a stale worktree's duplicate tests out of the scan)."""
    out: set[Path] = set()
    for pat in _TEST_FILE_PATTERNS:
        for p in Path(root).rglob(pat):
            if not any(part in _SKIP_DIRS for part in p.parts):
                out.add(p)
    return sorted(_drop_ignored(Path(root), sorted(out)))


def _selected_test_files(root: Path, test_cmd: str) -> list[Path] | None:
    """Best-effort STATIC resolution of which test files `test_cmd` selects.

    Recognises path tokens (`tests/test_x.py`, `pytest path::TestC::test_n`),
    directory tokens (each contributes its test-shaped files), and bare/dotted
    module tokens (`test_good`, `tests.test_x`). Returns None when nothing in the
    command resolves - an honest UNRESOLVED, never an empty selection that would
    warn on every test file in the repo."""
    import shlex
    root = Path(root)
    if not test_cmd:                       # an empty surface can be recorded with no command
        return None
    try:
        tokens = shlex.split(test_cmd)
    except ValueError:
        return None
    selected: set[Path] = set()
    resolved = False
    # `--ignore`/`--deselect` values are paths the runner will NEVER run: counting one as
    # selected silences the manufactured-survivor warning for exactly the file the command
    # excluded. Both the space form and the `=` form are honoured.
    exclude_opts = ("--ignore", "--deselect")
    ignored_raw: list[str] = []
    args_only: list[str] = []
    it = iter(tokens[1:])   # tokens[0] is the runner/interpreter, never a selection
    for tok in it:
        if tok in exclude_opts:
            ignored_raw.append(next(it, ""))
            continue
        if tok.startswith(tuple(o + "=" for o in exclude_opts)):
            ignored_raw.append(tok.split("=", 1)[1])
            continue
        args_only.append(tok)

    def _paths_of(t: str) -> set[Path]:
        t = t.strip().split("::", 1)[0]
        if not t or t.startswith("-"):
            return set()
        direct = Path(t) if Path(t).is_absolute() else root / t
        module_form = root / (t.replace(".", "/") + ".py")
        for cand in (direct, module_form):
            if cand.is_file() and cand.suffix == ".py":
                return {cand}
            if cand.is_dir():
                return set(_candidate_test_files(cand))
        return set()

    for tok in args_only:
        found = _paths_of(tok)
        if found:
            selected.update(found)
            resolved = True
    for raw in ignored_raw:
        selected -= _paths_of(raw)
    return sorted(selected) if resolved else None


def referencing_test_files(root: Path | str, targets) -> dict[str, list[Path]]:
    """Per target stem, the test files whose text NAMES it - the reference scan.

    The single scan `_selection_warnings` reads BACKWARD (which referencing tests a command
    failed to select) and `suggest_test_command` reads FORWARD (which tests would cover a
    target). One definition, so the covering command a run is told to use is built from exactly
    the files whose absence would otherwise warn - which is what makes the zero-warning
    guarantee hold BY CONSTRUCTION rather than by two scans agreeing.

    Reference-scan coverage is a HEURISTIC: a test that names the target is not proof it
    exercises it, and a test that exercises it via a re-export may not name it. Every consumer
    states that caveat rather than reading this as a coverage oracle."""
    root = Path(root)
    stems = [Path(f).stem for f in targets]
    hits: dict[str, list[Path]] = {s: [] for s in stems}
    for tf in _candidate_test_files(root):
        try:
            text = tf.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for stem in stems:
            if re.search(rf"\b{re.escape(stem)}\b", text):
                hits[stem].append(tf)
    return hits


def _selection_warnings(root: Path, targets, selected: list[Path] | None) -> list[dict]:
    """The manufactured-survivor condition: a test file that references a target
    module but sits OUTSIDE the command's selection. Advisory only - a narrow run
    stays legal; it just cannot stay silent about what it did not run."""
    if selected is None:
        return []
    sel = {p.resolve() for p in selected}
    warnings: list[dict] = []
    refs = referencing_test_files(root, targets)
    for stem, files in refs.items():
        for tf in files:
            if tf.resolve() in sel:
                continue
            warnings.append({"test_file": str(tf), "references": stem})
    return warnings


REFERENCE_SCAN_CAVEAT = ("reference-scan coverage is a heuristic: a test that names the target "
                         "is not proof it exercises it, only that it references it")


def _rel(root: Path, p: Path) -> str:
    try:
        return str(p.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(p)


def suggest_test_command(root: Path | str, targets, runner: str = "pytest") -> dict:
    """A per-target covering command derived from the reference scan.

    For each target, the referencing test files its scan found, and a command that selects
    exactly them (`<runner> <files>`). A run executed with the covering command produces zero
    out-of-selection warnings for those targets BY CONSTRUCTION, because the command lists the
    very files the warning scan looks for. A target no test references yields a null command and
    is named as uncovered - an honest gap, never a fabricated pass. The heuristic caveat rides on
    the result so no reader mistakes 'names it' for 'exercises it'."""
    root = Path(root)
    refs = referencing_test_files(root, targets)
    per_target: dict[str, dict] = {}
    combined: list[str] = []
    for f in targets:
        stem = Path(f).stem
        rels = sorted({_rel(root, p) for p in refs.get(stem, [])})
        per_target[str(Path(f))] = {
            "referencing_tests": rels,
            "command": (f"{runner} " + " ".join(rels)) if rels else None,
            "uncovered": not rels,
        }
        combined.extend(rels)
    combined = sorted(set(combined))
    return {
        "per_target": per_target,
        "covering_command": (f"{runner} " + " ".join(combined)) if combined else None,
        "runner": runner,
        "caveat": REFERENCE_SCAN_CAVEAT,
    }


def _git_rev(root: Path) -> str | None:
    """Best-effort HEAD rev, recorded in the report so the gate lane can tell a
    current report from a stale one. None outside a git repo."""
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                              capture_output=True, text=True, timeout=10)
        return proc.stdout.strip() or None if proc.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


_ASSERT_RE = re.compile(r"\bassert\b|\.assert|expect\s*\(|\.should\b|require\.")


def prefilter(test_paths) -> list[Path]:
    """Test files with no recognisable assertion - candidates for vacuous suites.
    Advisory: an ordering signal for which tests to mutate first, never a verdict."""
    flagged: list[Path] = []
    for p in sorted(Path(t) for t in test_paths):
        try:
            if not _ASSERT_RE.search(p.read_text(encoding="utf-8")):
                flagged.append(p)
        except (OSError, UnicodeDecodeError):
            flagged.append(p)  # unreadable test = unverifiable test: surface it
    return flagged


def _pct(part: int, whole: int) -> str:
    """Sampled-coverage percentage, one decimal - '0.5%' never rounds to '0%'."""
    if whole <= 0:
        return "0.0%"
    return f"{100.0 * part / whole:.1f}%"


def cmd_run(args: argparse.Namespace) -> int:
    if getattr(args, "from_plan", False):
        if not getattr(args, "story", None):
            print("run --from-plan needs --story: the plan belongs to a unit", file=sys.stderr)
            return 2
        return cmd_from_plan(args)
    root = Path(args.root)
    try:
        files = select_files(root, files=args.files, since=args.since, story=args.story)
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not files:
        # A chosen surface (--since / --story / --strategy) that resolves to no mutatable file is
        # an empty surface, not an error: there is nothing to mutate. Record it as a first-class
        # outcome (exit 0) so a docs-only close reads 'nothing to mutate' on the gate, never a
        # silent non-pass with no record. run_gate short-circuits an empty surface - no baseline,
        # no mutant, no test run - and writes the honest report.
        report = run_gate(root, [], args.test, changed=None,
                          write_report=not getattr(args, "dry_run", False))
        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            print("mutation: nothing to mutate - the selected surface has no mutatable files "
                  "(recorded as an empty surface, not a pass and not a refusal)")
        return 0
    # Suggestion mode: print the per-target covering command from the reference scan and exit,
    # mutating nothing. Triggered by --suggest-test, or by omitting --test (there is nothing to
    # run, so the honest response is to propose one). --test alone is unchanged - the default.
    if getattr(args, "suggest_test", False) or args.test is None:
        if args.test is None and not getattr(args, "suggest_test", False):
            print("error: --test is required unless --suggest-test is given (with --suggest-test, "
                  "--test may be omitted to just print the covering command)", file=sys.stderr)
            return 2
        sugg = suggest_test_command(root, files, runner=getattr(args, "runner", "pytest"))
        if args.format == "json":
            print(json.dumps(sugg, indent=2))
        else:
            print(f"mutation: suggested covering command per target - {sugg['caveat']}")
            for tgt, info in sugg["per_target"].items():
                if info["command"]:
                    print(f"  {tgt}: {info['command']}")
                else:
                    print(f"  {tgt}: (no referencing test found - UNCOVERED)")
            if sugg["covering_command"]:
                print(f"  all targets: {sugg['covering_command']}")
        return 0
    ceiling = args.max_mutations
    if ceiling is None:
        import config  # sibling; soft default when no project override
        ceiling = int(config.get(root, "quality.mutation_max", DEFAULT_MAX_MUTATIONS))
    # With a diff to aim at, spend the ceiling on the changed lines first - otherwise a
    # low ceiling on a large file samples peripheral helpers and reports a kill rate about
    # code nobody touched (L-0086).
    changed = changed_lines(root, args.since) if args.since else None
    report = run_gate(root, files, args.test, max_mutations=ceiling, changed=changed,
                      write_report=not getattr(args, "dry_run", False))
    s = report["summary"]
    ser = report.get("series") or {}
    if ser.get("reset") and args.format != "json":
        # a silently rewritten history is a history nobody can trust
        print(f"  note: the mutation series at {ser['path']} was malformed and has been "
              f"replaced - this run's row is the only one it now holds")
    if report.get("empty_surface"):
        # A surface with no mutatable site (an explicit --files over a docstring/import-only
        # module, say) is the honest empty outcome, not a pass: exit 0 with the reason named.
        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            print("mutation: nothing to mutate - the selected surface has no mutatable sites "
                  "(recorded as an empty surface, not a pass and not a refusal)")
        return 0
    if report.get("refused"):
        # a red/broken baseline proves nothing: refuse loudly, name the remedy, exit non-zero -
        # NEVER a clean-looking zero over a report that judged nothing
        if args.format == "json":
            print(json.dumps(report, indent=2))
        elif report.get("dirty_targets"):
            # A dirty target refuses BEFORE the baseline, so quoting a baseline verdict here
            # would name a run that never happened. Name the files instead - they are the
            # thing the operator has to act on.
            print(f"mutation: REFUSED - uncommitted changes on "
                  f"{', '.join(report['dirty_targets'])} (no mutants applied). "
                  f"{report['remedy']}", file=sys.stderr)
        else:
            print(f"mutation: REFUSED - baseline {report['baseline']} (no mutants applied). "
                  f"{report['remedy']}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for p in report.get("recovered", []):
            print(f"  note: recovered a stranded mutant on {p} from the in-flight "
                  f"sidecar (a previous run was killed mid-mutant) before the baseline")
        print(f"mutation: {s['applied']} applied, {s['killed']} killed, "
              f"{s['survived']} survived, {s['errors']} error(s), "
              f"{s['unviable']} unviable, "
              f"{s['truncated']} truncated, {len(report['unchecked'])} un-checked "
              f"in {report.get('elapsed_s')}s")
        # Printed with the counts, never below them: a survivor measured in a shared tree is
        # not the same evidence as one measured in a checkout of its own, and the difference
        # has to be legible to whoever reads the number rather than inferred by whoever
        # remembers to ask. Silent only for a confirmed isolated tree, which is the state
        # nobody needs warning about.
        warn = tree_warning_line(s)
        if warn:
            print(warn)
        sel = report.get("selected_tests")
        if sel is None:
            print("  test selection: UNRESOLVED - the command could not be statically "
                  "mapped to test files; read survivors knowing only the recorded command")
        else:
            print(f"  test selection: {len(sel)} file(s) - "
                  + ", ".join(Path(p).name for p in sel))
        led = report.get("ledger") or {}
        if led.get("dropped_now"):
            print(f"  note: the mutation ledger dropped its {led['dropped_now']} oldest "
                  f"entr(ies) at the {LEDGER_LIMIT}-entry bound "
                  f"({led['dropped_total']} dropped in all)")
        for w in report.get("selection_warnings", []):
            print(f"  WARNING: {w['test_file']} references target `{w['references']}` but "
                  f"is OUTSIDE the test command's selection - a survivor may be "
                  f"manufactured by the narrow command, not proof of a missing test")
        for r in report["mutations"]:
            if r["verdict"] != "killed":
                print(f"  {r['verdict'].upper():9} {r['file']}:{r['line']} "
                      f"{r['class']} (occurrence {r['occurrence']})")
        if s["truncated"]:
            print(f"  note: sampled {s['applied']}/{s['enumerated']} enumerated "
                  f"({_pct(s['applied'], s['enumerated'])}) - the "
                  f"{s['truncated']} beyond the ceiling are un-checked, not clean")
        if "diff_mutations" in s:
            if s["diff_covered"]:
                print(f"  diff coverage: {s['diff_applied']}/{s['diff_mutations']} "
                      f"mutants on changed lines - the diff is fully covered")
            else:
                print(f"  WARNING: diff coverage {s['diff_applied']}/{s['diff_mutations']} "
                      f"({_pct(s['diff_applied'], s['diff_mutations'])}) - the ceiling could "
                      f"not reach every mutant on the changed lines; raise "
                      f"--max-mutations to judge the whole diff")
    return 1 if s["survived"] or s["errors"] else 0


NOT_RUN = "not-run"


def plan_execution(root: Path | str, unit: str) -> dict:
    """Join a unit's test-plan rows to the mutation ledger: what was executed, and what was not.

    A plan is paperwork until its rows are EXECUTED. The join is on an explicit `criterion` field
    recorded at registration, never on the mutant's prose: a substring match would credit one
    criterion's execution to another's row, and a matching rule that is convenient is a gate that
    is optional.

    A row with no execution is `not-run` - reported as its own state, never folded into "killed"
    and never silently omitted. An unexecuted plan and a passed one must not read alike, because
    the whole point of the plan is that somebody checks.
    """
    root = Path(root)
    import verify_ac as _va  # noqa: PLC0415 - deferred; the module that owns the plan format
    found = sdlc_md.find_by_id(root, unit)
    if not found:
        return {"ok": False, "unit": unit, "rows": [],
                "errors": [f"{unit}: no artefact with that id"]}
    text = sdlc_md.read_text_safe(found[0])
    planned = _va._testplan_rows(text)
    # Only a WELL-FORMED `unnameable` - one carrying its reason - exempts a row. A bare one is
    # malformed, and US0633 refuses it at grooming precisely so it costs something; exempting it
    # here too would refund that cost one lane later and make the marker a free pass at the gate
    # it matters most at. Found by an independent seat.
    unnameable = {r["ac"] for r in _va.testplan_unnameable(text) if not r["malformed"]}
    uid = sdlc_md.norm_id(unit)

    executed: dict = {}
    state, _reset = _load_ledger(ledger_path(root))
    for entry in state.get("entries", []):
        if not isinstance(entry, dict):
            continue
        for m in entry.get("mutants", []) or []:
            if not isinstance(m, dict) or m.get("unit") != uid or not m.get("criterion"):
                continue
            # The WORST verdict wins per criterion: a survivor is not cancelled by a later kill
            # of some other mutant on the same row. Silence about a survivor is the failure this
            # gate exists to catch.
            prev = executed.get(m["criterion"])
            if prev is None or prev["verdict"] != "survived":
                executed[m["criterion"]] = {"verdict": m.get("verdict"),
                                            "target": entry.get("target"),
                                            "mutant": m.get("mutant"), "test": m.get("test")}
    rows = []
    for ac, mutant in sorted(planned.items()):
        if ac in unnameable:
            rows.append({"ac": ac, "verdict": "unnameable", "mutant": mutant})
            continue
        hit = executed.get(ac.upper())
        rows.append({"ac": ac, "mutant": mutant,
                     "verdict": (hit or {}).get("verdict") or NOT_RUN,
                     "target": (hit or {}).get("target"),
                     "test": (hit or {}).get("test")})
    outstanding = [r for r in rows
                   if r["verdict"] in (NOT_RUN, "survived")]
    return {"ok": not outstanding and bool(rows), "unit": uid, "rows": rows,
            "outstanding": outstanding, "planned": len(rows),
            "errors": ([] if rows else
                       [f"{uid}: no `## Test Plan` rows - derive one first: "
                        f"`verify_ac.py testplan derive --unit {uid}`"])}


def cmd_from_plan(args: argparse.Namespace) -> int:
    """`mutation.py run --story <id> --from-plan` - was every planned mutant executed?"""
    res = plan_execution(args.root, args.story)
    for e in res.get("errors", []):
        print(f"from-plan refused: {e}", file=sys.stderr)
    if res.get("errors"):
        return 2
    for r in res["rows"]:
        print(f"  {r['ac']}: {r['verdict']}"
              + (f" [{r.get('target')}]" if r.get("target") else "")
              + f" - {r['mutant'][:90]}")
    if res["ok"]:
        print(f"from-plan: {res['planned']} planned mutant(s), every one executed and killed")
        return 0
    for r in res["outstanding"]:
        if r["verdict"] == NOT_RUN:
            print(f"from-plan: {res['unit']} {r['ac']} was PLANNED and never executed - a plan "
                  f"whose rows are optional measures nothing. Apply it, then record it with "
                  f"`mutation.py register --unit {res['unit']} --criterion {r['ac']} ...`",
                  file=sys.stderr)
        else:
            print(f"from-plan: {res['unit']} {r['ac']} mutant SURVIVED on {r.get('target')} - "
                  f"the test named by that criterion did not notice `{r['mutant'][:80]}`. The "
                  f"finding is about the TEST, not the mutant.", file=sys.stderr)
    return 2


def cmd_register(args: argparse.Namespace) -> int:
    try:
        res = register_mutant(args.root, args.target, args.mutant, args.test, args.verdict,
                              reason=getattr(args, "reason", None),
                              run=getattr(args, "run", None),
                              unit=getattr(args, "unit", None),
                              criterion=getattr(args, "criterion", None))
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if res["verdict"] == EQUIVALENT_VERDICT:
        # excluded from yield, and said out loud: a silent exclusion is indistinguishable
        # from a mutant nobody ran
        print(f"mutation: recorded an EQUIVALENT mutant on {res['target']} - EXCLUDED from "
              f"this run's yield and from its outstanding survivors, because "
              f"{args.reason}. Self-reported: nothing here re-ran anything")
        return 0
    print(f"mutation: registered a SELF-REPORTED mutant on {res['target']} "
          f"({res['verdict']}) - {res['registered']} registered mutant(s) on this content. "
          f"Nothing was re-run here, so the ledger holds this as a claim, not a measurement")
    if res["verdict"] == "survived":
        print(f"  FINDING: the mutant SURVIVED, so {args.test} does not pin the behaviour it "
              f"was applied to. The gate's coverage lane counts this - fix the test or file it")
    if res["registered"] > res["retained"]:
        print(f"  note: this entry keeps the {MUTANT_LIMIT} most recent mutant descriptions; "
              f"{res['registered'] - res['retained']} older one(s) have been dropped (the "
              f"counts are not truncated)")
    if res.get("dropped_now"):
        print(f"  note: the mutation ledger dropped its {res['dropped_now']} oldest "
              f"entr(ies) at the {LEDGER_LIMIT}-entry bound "
              f"({res['dropped_total']} dropped in all)")
    return 0


def cmd_yield(args: argparse.Namespace) -> int:
    y = run_yield(args.root, args.run)
    if args.format == "json":
        print(json.dumps(y, indent=2))
        return 0 if y["found"] else 2
    if not y["found"]:
        print(f"mutation: no run {args.run} in the series - it has no yield of zero, it has "
              f"no yield at all", file=sys.stderr)
        return 2
    print(f"mutation run {args.run}: {y['elapsed_s']}s, {y['survivors']} survivor(s), "
          f"yield {y['yield']} filed artefact(s)"
          + (f" ({', '.join(y['filed'])})" if y["filed"] else "")
          + f", {y['outstanding']} outstanding")
    for eq in y["equivalent"]:
        print(f"  EXCLUDED (equivalent): {eq['mutant']} - {eq['reason']}")
    if not y["evidence"]:
        print(f"  note: this run recorded NO EVIDENCE "
              f"({y['row'].get('no_evidence_reason')}) - read its yield knowing that")
    return 0


def cmd_window(args: argparse.Namespace) -> int:
    """open / close / status over the rewrite window. A REVIEWER hand-editing files needs a
    command of their own: the incident CR0388 records involved no mutation run at all, so a
    window only this tool could arm would not have covered it."""
    if args.window_cmd == "open":
        if not (args.owner or "").strip():
            print("error: `window open` needs --owner - an anonymous claim tells a blocked "
                  "author nothing about who to ask or what to wait for", file=sys.stderr)
            return 2
        try:
            rec = open_window(args.root, args.owner, args.paths or [], note=args.note)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        # What the guard DOES, not what it once did. This said "Commits in this tree will be
        # refused until it is closed", which was true while the gate lane blocked on the
        # record's existence and false the moment it became path-scoped: a commit staging
        # nothing this window claims proceeds. A CLI that overstates its own guard teaches an
        # author to route around it.
        # PRINT THE NORMALISED CLAIMS, NOT THE RAW FIELD. `--paths` defaults to empty, and
        # both readers normalise an empty or all-blank `paths` to WINDOW_EVERYTHING - "a record
        # that does not say what it may rewrite has NOT said it may rewrite nothing". So the
        # DEFAULT invocation opens a whole-tree window, and printing the raw list said "0
        # path(s)" and then promised that anything else proceeds. That understated the guard,
        # which is the worse direction: an author told the window is narrow when it claims
        # everything believes the guard is inert. Two roundings of the same sentence were wrong
        # before this one; the fix is to render what the MATCHER will be handed.
        claims = window_claims(rec["paths"])
        everything = any(claims_everything(c) for c in claims)
        # Name the ONE cause that applies to THIS window, not a list of every cause there is.
        # A static list cannot be asserted against - see `everything_reason`.
        why = next((f"`{c}`: {everything_reason(c)}" for c in claims
                    if everything_reason(c) is not None), "")
        scope = (f"the WHOLE TREE - every commit is refused, because {why}"
                 if everything else f"{len(claims)} path(s): {', '.join(claims)}")
        consequence = ("Every commit will be refused until it is closed."
                       if everything else
                       "A commit staging a path it claims will be refused until it is closed; "
                       "a commit staging anything else proceeds.")
        print(f"mutation: rewrite window OPEN, held by {rec['owner']} over {scope}. "
              f"{consequence} Close it with: {rec['clear_with']}")
        return 0
    if args.window_cmd == "close":
        try:
            held = close_window(args.root, owner=args.owner)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print("mutation: no rewrite window was open" if held is None
              else f"mutation: rewrite window CLOSED (was held by {held['owner']})")
        return 0
    held = read_window(args.root)
    if held is None:
        print("mutation: no rewrite window is open")
        return 0
    print(f"mutation: rewrite window OPEN - {held['owner']} since {held.get('opened_at')} "
          f"over {', '.join(held.get('paths') or []) or '(unstated paths)'}"
          + (f" ({held['note']})" if held.get("note") else ""))
    if held.get("unreadable"):
        print(f"  {held['detail']}")
    print(f"  clear it with: {held['clear_with']}")
    return 1


def cmd_prefilter(args: argparse.Namespace) -> int:
    flagged = prefilter(args.tests)
    for p in flagged:
        print(f"  no load-bearing assertion found: {p}")
    print(f"prefilter: {len(flagged)}/{len(args.tests)} test file(s) flagged (advisory)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Executable mutation-check gate.")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="Mutate a surface and re-run its tests per mutation.")
    r.add_argument("--files", nargs="+", help="explicit target files")
    r.add_argument("--since", metavar="REF", help="target = files changed since this git ref")
    r.add_argument("--story", metavar="USxxxx", help="target = the story's CR/epic Affects")
    r.add_argument("--test", required=False, default=None,
                   help="test command run per mutation (shell). Omit it with --suggest-test to "
                        "print the reference-scan covering command instead of running")
    r.add_argument("--suggest-test", action="store_true", dest="suggest_test",
                   help="print the per-target covering command derived from the reference scan "
                        "(the referencing test files found), then exit without mutating")
    r.add_argument("--runner", default="pytest",
                   help="runner prefix for the suggested covering command (default: pytest)")
    r.add_argument("--max-mutations", type=int, default=None,
                   help=f"cost ceiling (default quality.mutation_max, else {DEFAULT_MAX_MUTATIONS})")
    r.add_argument("--root", default=".")
    r.add_argument("--dry-run", action="store_true", dest="dry_run",
                   help="run the mutants and print the verdicts, but write no report, no "
                        "ledger entry and no series row - a rehearsal leaves no evidence")
    r.add_argument("--format", choices=("text", "json"), default="text")
    r.add_argument("--from-plan", action="store_true", dest="from_plan",
                   help="do not mutate: join --story's TEST PLAN rows to the ledger and report "
                        "which planned mutants were executed. A row never applied is `not-run`, "
                        "which is not a pass")
    r.set_defaults(func=cmd_run)
    g = sub.add_parser("register",
                       help="Record a mutant applied BY HAND - self-reported, never measured.")
    g.add_argument("--unit", help="the unit whose test plan this mutant belongs to")
    g.add_argument("--criterion", metavar="ACn",
                   help="the criterion whose planned mutant this is - the JOIN KEY "
                        "`run --from-plan` reads, recorded rather than matched out of prose")
    g.add_argument("--target", required=True, help="the file the mutant was applied to")
    g.add_argument("--mutant", required=True,
                   help="what was mutated, in words a reviewer can check against the diff")
    g.add_argument("--test", help="the test that returned the verdict (required for "
                                  "killed/survived; an equivalent mutant has none)")
    g.add_argument("--verdict", required=True, choices=REGISTRABLE_VERDICTS,
                   help="killed (the test went red), survived (it stayed green - a finding), "
                        "or equivalent (no behaviour changed, so no test could kill it - "
                        "excluded from yield, and it needs --reason)")
    g.add_argument("--reason", help="why an equivalent mutant could not be killed - mandatory "
                                    "for --verdict equivalent, since an unjustified exclusion "
                                    "is a silent decrement")
    g.add_argument("--run", metavar="MRUNxxx",
                   help="the mutation run this verdict belongs to (must be in the series)")
    g.add_argument("--root", default=".")
    g.set_defaults(func=cmd_register)
    y = sub.add_parser("yield", help="What one run COST and what was FILED from it.")
    y.add_argument("--run", required=True, metavar="MRUNxxx")
    y.add_argument("--root", default=".")
    y.add_argument("--format", choices=("text", "json"), default="text")
    y.set_defaults(func=cmd_yield)
    w = sub.add_parser("window",
                       help="Declare (or clear) that a process is rewriting source files "
                            "in place, so a concurrent commit is refused rather than staging "
                            "whatever that process has left on disk.")
    # One subcommand level, as every script in this family has: the action is a positional,
    # not a nested subparser, so `--root` keeps working on either side of the verb.
    w.add_argument("window_cmd", choices=("open", "close", "status"),
                   help="open a window, close it, or report the one that is open")
    w.add_argument("--owner", help="who is rewriting the tree - a reviewer, an agent, a tool "
                                   "(required to open; on close, refuse unless it matches)")
    w.add_argument("--paths", nargs="+", default=[], help="the files this window may rewrite")
    w.add_argument("--note", help="what is being done, for whoever the guard blocks")
    w.add_argument("--root", default=".")
    w.set_defaults(func=cmd_window)
    f = sub.add_parser("prefilter", help="List test files with no recognisable assertion.")
    f.add_argument("--tests", nargs="+", required=True)
    f.set_defaults(func=cmd_prefilter)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    import os  # noqa: PLC0415 - local, as elsewhere in this module
    # This process IS the mutation run, so it carries the exemption marker its suites carry:
    # a gate that refused to run because it had itself applied a mutant would be absurd, and
    # every child it spawns needs the same exemption.
    os.environ[sdlc_md.MUTATION_RUN_ENV] = "1"
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
