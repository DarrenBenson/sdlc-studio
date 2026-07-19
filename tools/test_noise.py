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


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--baseline", type=int, default=None,
                   help="the grandfathered leak count; absent means zero is required")
    args = p.parse_args(argv)
    text = sys.stdin.read()
    leaks = leaked_lines(text)
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
