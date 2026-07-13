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
             sdlc-studio/.local/mutation-report.json; exits non-zero on survivors.
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
_RUN_TIMEOUT = 600  # seconds per test run - a hung mutant must not hang the gate

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


def apply_budget(mutations: list[dict], max_mutations: int) -> tuple[list[dict], int]:
    """Distribute the cost ceiling round-robin over (file, fault class) groups -
    never first-N in file order, which clusters all coverage at the top of the
    alphabetically-first file. Deterministic: groups in sorted order, one mutation
    per group per rotation, each group's own line order preserved. Returns
    (chosen in original enumeration order, truncated count)."""
    if len(mutations) <= max_mutations:
        return list(mutations), 0
    groups: dict = {}
    for m in mutations:
        groups.setdefault((m["file"], m["class"]), []).append(m)
    # files are the FAST axis of the rotation (sort by class, then file): with a
    # small budget every file still gets coverage before any class repeats
    queues = [groups[k] for k in sorted(groups, key=lambda k: (k[1], k[0]))]
    chosen: list[dict] = []
    i = 0
    while len(chosen) < max_mutations and any(queues):
        q = queues[i % len(queues)]
        if q:
            chosen.append(q.pop(0))
        i += 1
    order = {id(m): n for n, m in enumerate(mutations)}
    chosen.sort(key=lambda m: order[id(m)])
    return chosen, len(mutations) - len(chosen)


@contextlib.contextmanager
def applied(mutation: dict):
    """Apply one mutation; ALWAYS restore the original bytes, even when the
    runner raises - the engine must never leave a mutant on disk."""
    path = Path(mutation["file"])
    original = path.read_bytes()
    try:
        path.write_text(mutated_text(mutation), encoding="utf-8")
        yield
    finally:
        path.write_bytes(original)


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
    timeout - a compound command's grandchildren must not outlive the gate."""
    import os
    import signal
    proc = subprocess.Popen(test_cmd, shell=True, cwd=cwd, start_new_session=True,  # nosec B602 - operator-authored test command, same trust boundary as verify_ac's Verify lines
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
             classes: tuple = FAULT_CLASSES, write_report: bool = True) -> dict:
    """The gate: enumerate, apply one at a time, re-run tests, verdict each mutation.

    Baseline first: the tests must be green over UNMUTATED code - a red or broken
    baseline cannot judge anything, so every enumerated mutation records verdict
    `error` (reason in the report) rather than a fake kill."""
    root = Path(repo_root)
    ceiling = max_mutations if max_mutations is not None else DEFAULT_MAX_MUTATIONS
    all_mutations, unchecked = enumerate_mutations(files, classes)
    to_apply, truncated = apply_budget(all_mutations, ceiling)
    baseline = _run_tests(test_cmd, root)
    records: list[dict] = []
    if baseline != "pass":
        reason = ("baseline red - tests fail on unmutated code" if baseline == "fail"
                  else "test command errored on unmutated code")
        records = [{**m, "verdict": "error", "reason": reason} for m in to_apply]
    else:
        for m in to_apply:
            mutated = mutated_text(m)
            unviable_reason = _viability(Path(m["file"]), mutated)
            if unviable_reason:
                # evidence of nothing: any suite fails on a non-parsing mutant,
                # so it must never count as killed (nor as survived)
                records.append({**m, "verdict": "unviable", "reason": unviable_reason})
                continue
            with applied(m):
                outcome = _run_tests(test_cmd, root)
            verdict = {"pass": "survived", "fail": "killed", "error": "error"}[outcome]
            records.append({**m, "verdict": verdict})
    summary = {
        "applied": len(records),
        "killed": sum(1 for r in records if r["verdict"] == "killed"),
        "survived": sum(1 for r in records if r["verdict"] == "survived"),
        "errors": sum(1 for r in records if r["verdict"] == "error"),
        "unviable": sum(1 for r in records if r["verdict"] == "unviable"),
        "truncated": truncated,
        "enumerated": len(all_mutations),
    }
    import hashlib
    target_hashes = {}
    for fp in files:
        try:
            target_hashes[str(Path(fp))] = hashlib.sha256(Path(fp).read_bytes()).hexdigest()
        except OSError:
            target_hashes[str(Path(fp))] = None
    report = {
        "generated_at": sdlc_md.now_iso8601(),
        "git_rev": _git_rev(root),
        "target_hashes": target_hashes,
        "test_cmd": test_cmd,
        "targets": [str(Path(f)) for f in files],
        "baseline": baseline,
        "mutations": records,
        "unchecked": unchecked,
        "summary": summary,
    }
    if write_report:
        out = root / "sdlc-studio" / ".local" / "mutation-report.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


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
    report = run_gate(root, files, args.test, max_mutations=ceiling)
    s = report["summary"]
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"mutation: {s['applied']} applied, {s['killed']} killed, "
              f"{s['survived']} survived, {s['errors']} error(s), "
              f"{s['unviable']} unviable, "
              f"{s['truncated']} truncated, {len(report['unchecked'])} un-checked")
        for r in report["mutations"]:
            if r["verdict"] != "killed":
                print(f"  {r['verdict'].upper():9} {r['file']}:{r['line']} "
                      f"{r['class']} (occurrence {r['occurrence']})")
        if s["truncated"]:
            print(f"  note: sampled {s['applied']}/{s['enumerated']} enumerated "
                  f"({_pct(s['applied'], s['enumerated'])}) - the "
                  f"{s['truncated']} beyond the ceiling are un-checked, not clean")
    return 1 if s["survived"] or s["errors"] else 0


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
    r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_run)
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
