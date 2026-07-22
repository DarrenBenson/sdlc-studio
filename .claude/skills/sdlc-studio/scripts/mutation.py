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
        excluded: set = set()
        if path.suffix == ".py":
            excluded, tok_ok = _multiline_string_spans("\n".join(lines) + "\n")
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
            occ = 0
            for ln, line in enumerate(lines, 1):
                if ln in excluded:
                    continue
                if pattern.match(line):
                    mutations.append({"file": str(path), "class": cls,
                                      "occurrence": occ, "line": ln})
                    occ += 1
    return mutations, unchecked


def mutated_text(mutation: dict) -> str:
    """The full mutated file content for one anchored mutation."""
    path = Path(mutation["file"])
    pattern, repl = PROFILES[path.suffix][mutation["class"]]
    lines = path.read_text(encoding="utf-8").splitlines()
    occ = 0
    for i, line in enumerate(lines):
        m = pattern.match(line)
        if m:
            if occ == mutation["occurrence"]:
                lines[i] = repl(m)
                break
            occ += 1
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
    one restore source a killed run cannot corrupt."""
    return Path(root) / "sdlc-studio" / ".local" / "mutation-inflight.json"


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


def everything_reason(claim) -> str | None:
    """WHY this claim claims the whole tree, in words, or None when it does not.

    `claims_everything` is this function asked as a yes/no. It exists because a message that
    lists EVERY cause for every input cannot be asserted against: a test reading it can only
    check that a word appears, which passes for a claim the word does not describe, and a
    mutant deleting the other causes survives. Naming the ONE cause that applies makes the
    sentence vary with its input, which is what makes it checkable.
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
    # `fnmatch.fnmatch`, where a whole FAMILY of patterns matches every path - `**`, `***`,
    # `?*`, `*.` and more. The previous version listed literal spellings and got `*` right only
    # by accident, because `*` happened to be WINDOW_EVERYTHING sitting in the tuple. It never
    # reasoned about globs at all, so `--paths '**'` printed "1 path(s) ... anything else
    # proceeds" while every commit was refused. That was the FIFTH wrong version of this
    # sentence, and the four before it were all enumerations too. Probing settles it by
    # construction: a claim that matches every one of these unrelated paths claims everything.
    import fnmatch  # noqa: PLC0415 - local, as elsewhere in the matcher family
    probes = ("a", "a/b.py", "z/y/x/w.md", "README", "x.y", ".githooks/pre-commit")
    if all(s.startswith(pat + "/") or fnmatch.fnmatch(s, pat) for s in probes):
        return "it is a glob matching every path the matcher probes"
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


def _run_tests(test_cmd: str, cwd: Path) -> str:
    """One test run -> 'pass' | 'fail' | 'error' (the runner itself broke).

    The command runs in its own session and the whole process GROUP is killed on
    timeout - a compound command's grandchildren must not outlive the gate.

    `PYTHONDONTWRITEBYTECODE` is forced on: a cached `.pyc` is keyed on (source
    mtime, source size), so a same-length mutant written inside one mtime second
    would otherwise run the ORIGINAL bytecode and be recorded as survived. Writing
    no cache leaves nothing for the next mutant to inherit."""
    import os
    import signal
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    proc = subprocess.Popen(test_cmd, shell=True, cwd=cwd, start_new_session=True, env=env,  # nosec B602 - operator-authored test command, same trust boundary as verify_ac's Verify lines
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        rc = proc.wait(timeout=_RUN_TIMEOUT)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        proc.wait()
        return "error"
    if rc == 0:
        return "pass"
    if rc in (126, 127):  # not executable / command not found
        return "error"
    return "fail"


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
    to_apply, truncated = apply_budget(all_mutations, ceiling, changed)
    _install_restore_handlers()   # a kill mid-mutant must restore, never strand
    # A SIGKILLed previous run strands its mutant; reading THAT back as the original
    # would poison every restore in this run, so recover from the sidecar first.
    recovered: list[str] = []
    baseline = "error"
    refused = True
    remedy = None
    # Another declared writer in this tree makes this run the SECOND one, which is the hazard
    # itself: refuse before touching a byte, rather than interleaving two processes' rewrites.
    blocking = read_window(root)
    if blocking is not None:
        remedy = (f"a rewrite window is open, held by {blocking['owner']} over "
                  f"{', '.join(blocking.get('paths') or []) or '(unstated paths)'} - refusing to "
                  f"be the second process rewriting this tree. Wait for it, or clear it: "
                  f"{blocking['clear_with']}")
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
    if not refused:
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
                records.append({**m, "verdict": verdict})
        finally:
            # Never raise out of the restore path. A window this run cannot find - cleared by
            # hand mid-run, or replaced - would otherwise become the exception that buries the
            # run's own result, and it did: another record sorting first made this close refuse
            # and strand the very window it was clearing.
            with contextlib.suppress(ValueError):
                close_window(root, owner=WINDOW_OWNER_RUN)
    summary = {
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
        "remedy": remedy,
        "blocked_by_window": blocking,
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
    evidence = (not refused) and (killed + survived) > 0
    if refused:
        reason = f"run refused - baseline {report.get('baseline')}, no mutant was applied"
    elif not evidence:
        reason = (f"{int(s.get('applied', 0))} mutant(s) applied and none returned a killed or "
                  f"survived verdict (unviable, errored or timed out) - nothing was judged")
    else:
        reason = None
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
        "outcome": "measured" if evidence else "no-evidence",
        "no_evidence_reason": reason,
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
                    reason: str | None = None, run: str | None = None) -> dict:
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
                 story: str | None = None) -> list[Path]:
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
    raise ValueError("select a surface: --files, --since REF, or --story USxxxx")


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


def _candidate_test_files(root: Path) -> list[Path]:
    """Every test-shaped file under root (skipping vendored/derived trees)."""
    out: set[Path] = set()
    for pat in _TEST_FILE_PATTERNS:
        for p in Path(root).rglob(pat):
            if not any(part in _SKIP_DIRS for part in p.parts):
                out.add(p)
    return sorted(out)


def _selected_test_files(root: Path, test_cmd: str) -> list[Path] | None:
    """Best-effort STATIC resolution of which test files `test_cmd` selects.

    Recognises path tokens (`tests/test_x.py`, `pytest path::TestC::test_n`),
    directory tokens (each contributes its test-shaped files), and bare/dotted
    module tokens (`test_good`, `tests.test_x`). Returns None when nothing in the
    command resolves - an honest UNRESOLVED, never an empty selection that would
    warn on every test file in the repo."""
    import shlex
    root = Path(root)
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


def _selection_warnings(root: Path, targets, selected: list[Path] | None) -> list[dict]:
    """The manufactured-survivor condition: a test file that references a target
    module but sits OUTSIDE the command's selection. Advisory only - a narrow run
    stays legal; it just cannot stay silent about what it did not run."""
    if selected is None:
        return []
    sel = {p.resolve() for p in selected}
    stems = [Path(f).stem for f in targets]
    warnings: list[dict] = []
    for tf in _candidate_test_files(Path(root)):
        if tf.resolve() in sel:
            continue
        try:
            text = tf.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for stem in stems:
            if re.search(rf"\b{re.escape(stem)}\b", text):
                warnings.append({"test_file": str(tf), "references": stem})
                break
    return warnings


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
    root = Path(args.root)
    try:
        files = select_files(root, files=args.files, since=args.since, story=args.story)
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not files:
        print("no mutatable files in the selected surface", file=sys.stderr)
        return 2
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
    if report.get("refused"):
        # a red/broken baseline proves nothing: refuse loudly, name the remedy, exit non-zero -
        # NEVER a clean-looking zero over a report that judged nothing
        if args.format == "json":
            print(json.dumps(report, indent=2))
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


def cmd_register(args: argparse.Namespace) -> int:
    try:
        res = register_mutant(args.root, args.target, args.mutant, args.test, args.verdict,
                              reason=getattr(args, "reason", None),
                              run=getattr(args, "run", None))
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
    r.add_argument("--test", required=True, help="test command run per mutation (shell)")
    r.add_argument("--max-mutations", type=int, default=None,
                   help=f"cost ceiling (default quality.mutation_max, else {DEFAULT_MAX_MUTATIONS})")
    r.add_argument("--root", default=".")
    r.add_argument("--dry-run", action="store_true", dest="dry_run",
                   help="run the mutants and print the verdicts, but write no report, no "
                        "ledger entry and no series row - a rehearsal leaves no evidence")
    r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_run)
    g = sub.add_parser("register",
                       help="Record a mutant applied BY HAND - self-reported, never measured.")
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
