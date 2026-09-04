#!/usr/bin/env python3
"""Detect diagnostics that escaped to the console during a PASSING test run.

A green suite must say nothing. When a test feeds a tool a deliberately-bad fixture and
lets the tool's complaint reach the console, a fully green run prints lines that read like
failures - and that trains every reader, human and agent, to skim past `error`. Skimming
past `error` is the exact reflex that lets a real one through. A signal you cannot
distinguish from noise is not a signal.

The first version of this guard matched one shape: `ERROR` or `WARN` followed by an
absolute path. Measured against this repo's own suite it caught 0 of 283 leaked lines,
because the leaks are lowercase `error:`, `warning:`, `usage:`, and tool-prefixed
messages like `gh issue create failed:`. Matching one shape of a defect is not far off
matching none.

The hard part is not catching leaks, it is NOT catching the runner. unittest's own output
- progress dots, rules, `Ran N tests`, `OK`, `FAILED`, and a failure's own traceback and
`AssertionError` text - must never fire, or the gate cries wolf on every green run and
gets switched off. So the runner's vocabulary is excluded first, and detection is anchored
to the start of a line: prose that merely contains the word "error" is not a leak.
"""
from __future__ import annotations

import re

#: unittest's own output. Checked FIRST, so every entry here is a hole: whatever this
#: swallows is invisible to the gate for ever. Two earlier entries were exactly that -
#: `\s.*` excluded ANY indented line, and `\w*(?:Error|...)` had a `\w*` matching empty,
#: so indenting or capitalising a leak disarmed the check. Two real leaks in this repo's
#: own suite were invisible for the first reason alone.
#:
#: Entries are matched on SHAPE, never on a word: the runner's failure header is `NAME
#: (dotted.path)`, which no tool's prose looks like, whereas the bare word `ERROR:` is
#: something tools print constantly.
#:
#: There are deliberately no traceback entries. This check runs ONLY over a run that
#: already exited 0, and a passing run has no traceback to exclude. Excluding for a case
#: that cannot arise is how the two holes above got in.
_RUNNER = re.compile(
    r"""^(?:
          [.sFExX]*                                  # progress dots / status chars
        | -{3,} | ={3,}                              # the rules between blocks
        | Ran\ \d+\ tests?\b.*
        | OK(?:\ \(.*\))?
        | FAILED(?:\ \(.*\))?
        | (?:FAIL|ERROR):\ \S+\ \([\w.]+\)           # the runner naming a test, by shape
        | \w+(?:Error|Exception|Warning):\ .*        # an exception repr: \w+ is NOT optional
        )$""",
    re.VERBOSE)

#: A diagnostic a tool wrote. Anchored at column 0, because an escaped diagnostic is
#: printed at the start of a line while prose mentioning the word is not.
_LEAK = re.compile(
    r"""^(?:
          (?:ERROR|WARN|WARNING)\s+/     # the original shape: level then an absolute path
        | (?:error|warning|usage|note|fatal|refused):\s
        | [a-z][a-z0-9_.-]*:\s                 # any `tool: message` prefix, alarm word or not
                                               # - a PASSING suite is silent, so a tool
                                               # announcing itself at all is the leak; the
                                               # earlier form demanded an alarm word and so
                                               # missed `capacity: this batch does not fit`
        | (?:failed|could\ not|unable\ to)\s
        | .*\b(?:failed|refused|blocked|skipped):\s
        | issue\ \#\d+\ not\ found
        )""",
    re.VERBOSE | re.IGNORECASE)


def leaked_lines(text: str) -> list[str]:
    """The diagnostic lines in `text` that a green run should not have printed.

    unittest writes its progress dots without a newline, so an escaped print lands on the
    SAME line as them - `...........gh issue create failed: denied` is the usual shape, not
    a clean line. The dots are stripped before matching so the leak is judged on its own
    text, and a line that is nothing but dots falls away rather than counting as one.

    The runner check runs on the RAW line, before stripping: `FAILED (failures=2)` begins
    with a character that is also a progress marker, and stripping first would maim it.
    """
    out = []
    for line in text.splitlines():
        if not line.strip():
            continue
        if _RUNNER.match(line):
            continue
        # Leading progress dots AND leading whitespace are both stripped before matching.
        # An escaped print often lands mid-dots, and an indented one is still a leak -
        # excluding indented lines wholesale is what hid two real ones.
        stripped = line.lstrip(".").lstrip()
        if not stripped:
            continue
        if _RUNNER.match(stripped):   # a runner line that was merely indented
            continue
        if _LEAK.match(stripped):
            out.append(stripped)
    return out


def within_baseline(count: int, baseline: int | None) -> bool:
    """True when `count` does not exceed the grandfathered `baseline`.

    A ratchet, not an amnesty. Demanding zero before the gate may run at all is why this
    guard currently runs nowhere: the debt is 283 lines and no one pays that to switch a
    check on. Recording the count freezes it - the gate fails the moment a change adds a
    leak - and the number is visible in the repo rather than implied. With no baseline
    recorded, nothing is tolerated: a project adopting this clean must not inherit an
    allowance it never asked for.
    """
    if baseline is None:
        return count == 0
    return count <= baseline


TOTAL_KEY = "_total"


def read_budget(path) -> dict[str, int]:
    """The per-module leak budget: `{"_total": N, "<test module>": n, ...}`.

    A missing or unreadable file is refused LOUDLY (exit 2 with the path named), never read as
    "no budget" - a silent fall-back to any absolute number would re-admit the check this budget
    replaces the moment the file is mistyped or moved. Keys beginning with `_` other than
    `_total` may hold a string, so the file can carry its own explanation (`_note`)."""
    import json
    from pathlib import Path as _P
    fp = _P(path)
    try:
        raw = json.loads(fp.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"test-noise: the budget file {fp} cannot be read ({exc}) - REFUSED. There is no "
              f"fall-back: name the file, or record one with every module measured alone plus "
              f"`{TOTAL_KEY}` for the full run.", file=__import__("sys").stderr)
        raise SystemExit(2)
    problems = budget_shape_problems(raw)
    if problems:
        print(f"test-noise: {fp} is not a budget - REFUSED: {'; '.join(problems)}",
              file=__import__("sys").stderr)
        raise SystemExit(2)
    return {k: v for k, v in raw.items() if not (k.startswith("_") and k != TOTAL_KEY)}


def budget_shape_problems(raw) -> list[str]:
    """Why `raw` is not a budget, or an empty list: an object of non-negative integers carrying
    `_total`, where a `_`-prefixed key other than `_total` may hold a note string."""
    if not isinstance(raw, dict):
        return [f"expected an object, found {type(raw).__name__}"]
    out = []
    if TOTAL_KEY not in raw:
        out.append(f"no `{TOTAL_KEY}` entry")
    for k, v in raw.items():
        if k.startswith("_") and k != TOTAL_KEY:
            if not isinstance(v, str):
                out.append(f"`{k}` must be a note string")
        elif isinstance(v, bool) or not isinstance(v, int) or v < 0:
            out.append(f"`{k}` must be a non-negative integer, found {v!r}")
    return out


def budget_for(budget: dict[str, int], selection: list[str] | None) -> tuple[int, str]:
    """`(ceiling, how)` for a run: the SUM of the selected modules' entries, or `_total` for a
    full run.

    Attribution is by sum over the selection: one `unittest` process does not say which module
    printed a leaked line, so a per-module promise would be one the script cannot keep. The
    bound this leaves - a module's overrun masked by another's slack within the same selection
    - is stated here rather than hidden. A module with NO entry contributes ZERO, so a new or
    renamed module cannot arrive carrying a leak nobody recorded. `_total` is the measured
    full-run figure, separate from the sum: the entries need not add up to it - a module measured
    alone prints any import-time leak once (a couple of lines here), and an entry may be held at
    a state-independent figure where the module once printed this clone's state (BG0647, fixed) - and a
    selection of EVERY module is still held to the sum, not `_total`."""
    if selection is None:
        return budget[TOTAL_KEY], f"the recorded full-run total of {budget[TOTAL_KEY]}"
    parts, missing = [], []
    for mod in selection:
        if mod in budget:
            parts.append(f"{mod}={budget[mod]}")
        else:
            missing.append(mod)
    ceiling = sum(budget.get(m, 0) for m in selection)
    how = f"the summed budget of {ceiling} over {len(selection)} selected module(s) ({', '.join(parts) or 'none recorded'})"
    if missing:
        how += f"; no entry, contributing zero: {', '.join(missing)} - record an entry at zero or capture its leaks"
    return ceiling, how


def budget_check(path) -> list[str]:
    """Shrink-only, against the committed version: an entry may only fall or vanish, `_total`
    may only fall, and a NEW entry may only be zero. Returns the refusals (empty means ok).

    Compared with `git -C <dir> show HEAD:./<name>`, where the previous state lives; a file
    with no committed version passes (its introduction), a directory that is not inside a work
    tree is REFUSED rather than read as "no committed version", because a run from an export
    would otherwise pass shrink-only unconditionally, and a committed version that is not a
    budget is refused by name. Read from the WORKING file, as every other working-tree lane is:
    a raise staged beside a lowered working copy passes this check and is caught at the next
    commit, the bound the repo-writes lane already states for the tree."""
    import os
    import subprocess
    from pathlib import Path as _P
    fp = _P(path).resolve()
    working = read_budget(fp)
    env = {**os.environ, "LC_ALL": "C"}   # the probe below is by exit code, never by localised text
    probe = subprocess.run(["git", "-C", str(fp.parent), "rev-parse", "--is-inside-work-tree"],
                           capture_output=True, text=True, check=False, env=env)
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return [f"{fp.parent} is not inside a git work tree, so shrink-only cannot be judged - REFUSED"]
    cp = subprocess.run(["git", "-C", str(fp.parent), "show", f"HEAD:./{fp.name}"],
                        capture_output=True, text=True, check=False, env=env)
    if cp.returncode != 0:
        return []   # no committed version: the file is being introduced
    import json
    try:
        committed = json.loads(cp.stdout)
    except ValueError as exc:
        return [f"the committed {fp.name} is not JSON ({exc}) - REFUSED rather than read as no committed version"]
    shape = budget_shape_problems(committed)
    if shape:
        return [f"the committed {fp.name} is not a budget ({'; '.join(shape)}) - REFUSED"]
    committed = {k: v for k, v in committed.items() if not (k.startswith("_") and k != TOTAL_KEY)}
    problems = []
    for key, value in working.items():
        was = committed.get(key)
        if was is None:
            if key != TOTAL_KEY and value > 0:
                problems.append(f"new entry {key}={value}: a new module is held to ZERO - capture its leaks or record 0")
        elif value > was:
            problems.append(f"{key} raised {was} -> {value}: the budget may only fall - capture the leak instead")
    return problems


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--baseline", type=int, default=None,
                   help="the grandfathered leak count; absent means zero is required")
    p.add_argument("--budget", default=None,
                   help="the per-module budget file; with it the ceiling is the sum over --select, "
                        "or `_total` for a full run, and --baseline is ignored")
    p.add_argument("--select", nargs="*", default=None,
                   help="the test modules this run was selected to (basenames without .py); "
                        "absent with --budget means a full run held to `_total`")
    p.add_argument("--budget-check", default=None, metavar="FILE",
                   help="compare FILE with its committed version and exit non-zero if any entry "
                        "rose or a new entry is above zero; reads no run")
    args = p.parse_args(argv)
    if args.budget_check:
        problems = budget_check(args.budget_check)
        for line in problems:
            print(f"test-noise budget-check: {line}", file=sys.stderr)
        return 1 if problems else 0
    text = sys.stdin.read()
    leaks = leaked_lines(text)
    if args.budget:
        ceiling, how = budget_for(read_budget(args.budget), args.select)
        if len(leaks) <= ceiling:
            if leaks:
                print(f"test-noise: {len(leaks)} leaked line(s), at or under {how} - declared "
                      f"debt, not a new leak", file=sys.stderr)
            return 0
        print(f"\ntest-noise: a PASSING run printed {len(leaks)} diagnostic line(s), above {how} "
              f"(recorded in {args.budget} - lower an entry as leaks are captured, never raise one):",
              file=sys.stderr)
        for line in leaks[:5]:
            print(f"  {line}", file=sys.stderr)
        print("\nfix: wrap the call in contextlib.redirect_stdout/redirect_stderr and assert on\n"
              "     the captured text. A green suite must say nothing, or a real error hides in\n"
              "     the noise.", file=sys.stderr)
        return 1
    if within_baseline(len(leaks), args.baseline):
        if leaks:
            print(f"test-noise: {len(leaks)} leaked line(s), at or under the recorded "
                  f"baseline of {args.baseline} - declared debt, not a new leak",
                  file=sys.stderr)
        return 0
    print(f"\ntest-noise: a PASSING run printed {len(leaks)} diagnostic line(s), above the "
          f"baseline of {args.baseline if args.baseline is not None else 0}:", file=sys.stderr)
    for line in leaks[:5]:
        print(f"  {line}", file=sys.stderr)
    print("\nfix: wrap the call in contextlib.redirect_stdout/redirect_stderr and assert on\n"
          "     the captured text. A green suite must say nothing, or a real error hides in\n"
          "     the noise.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
