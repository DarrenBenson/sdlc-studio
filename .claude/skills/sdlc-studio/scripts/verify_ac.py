#!/usr/bin/env python3
"""SDLC Studio acceptance-criteria verifier.

Parses story files for AC sections, runs each AC's Verify expression
against the live codebase, and updates the Verified state in place.
Writes a report to sdlc-studio/.local/verify-report.json.

Verifier DSL (one expression per AC):

    pytest <node>            Run pytest, pass on exit 0
    jest <pattern>           Run jest -t <pattern>
    vitest <pattern>         Run vitest run -t <pattern>
    go <path> -run <node>    Run go test -run <node> <path>
    file <path>              File must exist
    grep <regex> <path_glob> Ripgrep must find at least one match
    http <METHOD> <URL> -- <jq_expr>
                             curl + jq assertion
    shell <cmd>              Arbitrary shell, pass on exit 0

An unrecognised expression is an invalid verifier (exit 2), not a silent shell run;
prefix `shell` to run one, or pass --allow-shell-fallback for the legacy behaviour.
Shell-backed verbs are gated by story provenance and --no-shell (the trust boundary).

Trust boundary (verifiers run against possibly-untrusted content):
  - Shell-backed verbs (shell/eval/http/fallback) run only when `allow_shell` is set;
    story provenance `external` disables them unless `--allow-external` is passed.
  - The `http` verb has a scheme floor enforced in every mode - only http/https, so a
    `file://`/`ftp://`/`gopher://` SSRF target is refused. Setting SDLC_VERIFY_HTTP_HOSTS
    (comma-separated) turns on restricted mode: a target host outside the allow-list is
    refused (and a relative URL, having no host, is refused).
  - The complementary mutation gate's `--test` command runs under the SAME boundary: it is
    an operator-authored shell command, trusted exactly as a `shell` Verify line is (see
    scripts/mutation.py).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402

# -----------------------------------------------------------------------------
# AC parsing (regexes live in the shared lib; aliased here for local use)
# -----------------------------------------------------------------------------

AC_HEADING_RE = sdlc_md.AC_HEADING_RE
AC_BULLET_RE = sdlc_md.AC_BULLET_RE
VERIFY_RE = sdlc_md.VERIFY_RE
VERIFIED_RE = sdlc_md.VERIFIED_RE


@dataclass
class ACBlock:
    """An acceptance-criterion block parsed out of a story file."""

    heading_line: int  # 0-indexed
    ac_id: str
    title: str
    verify_line: int | None = None
    verifier: str | None = None
    verified_line: int | None = None
    verified_state: str | None = None
    verified_when: str | None = None
    # The line index where a new Verified line should be inserted if absent.
    # Defaults to just after the Verify line, or just after the last bullet
    # of the AC block.
    insert_after: int | None = None
    #: Verify expressions after the first in this block. The runner executes ONLY the
    #: first, so these are read as ordinary bullets and never run. Captured rather than
    #: discarded, so the fact can be reported instead of being invisible: six such
    #: verifiers were found sitting unexecuted in one workspace, four of them on stories
    #: already marked Done and two counted inside a published claim of verified criteria.
    extra_verifiers: list[str] = field(default_factory=list)


def ac_fingerprint(text: str) -> str:
    """Hash what a verification result actually depends on: the ACs and their verifiers.

    File mtime is the wrong staleness signal for a green verify entry - a Status
    transition, a Revision History row, or this script's own `**Verified:**` stamp all
    bump mtime without changing a single thing the run judged, so a correct green was
    reported as "edited after it was last verified". The fingerprint covers each AC's id,
    title and Verify command and nothing else, so a metadata-only edit leaves it identical
    while any change to an AC or its verifier (added, removed, retitled, re-pointed)
    changes it. Prose inside an AC body is deliberately excluded: it cannot change what
    the verifier executes.
    """
    import hashlib
    parts = [
        f"{b.ac_id}\x1f{b.title.strip()}\x1f{(b.verifier or '').strip()}"
        for b in parse_story(text)
    ]
    return hashlib.sha256("\x1e".join(parts).encode("utf-8")).hexdigest()


def parse_story(text: str) -> list[ACBlock]:
    """Extract AC blocks from story markdown."""
    lines = text.splitlines()
    blocks: list[ACBlock] = []
    current: ACBlock | None = None

    def flush() -> None:
        """Append the in-progress AC block, if any, to the result list."""
        if current is not None:
            blocks.append(current)

    fence = None          # (char, length) of the OPEN fence, or None
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        # A fenced code block inside an AC is an ILLUSTRATION, not a directive: a
        # `- **Verify:**` line shown as an example inside ``` must never be picked up and
        # executed. Skip fenced contents (the fence does not end the current AC block).
        # One shared CommonMark tracker (sdlc_md.fence_step), never a local rule: two parsers
        # with their own copy disagreed about where a block ended, and the disagreement put an
        # illustrative Verify line outside the fence, where it became a LIVE shell verifier.
        fence, is_fence_line = sdlc_md.fence_step(stripped, fence)
        if is_fence_line or fence is not None:
            continue

        m = AC_HEADING_RE.match(line)
        if m:
            flush()
            current = ACBlock(
                heading_line=i,
                ac_id=m.group(1),
                title=(m.group(2) or "").strip(),
            )
            continue

        # Bullet-style AC: `- **AC1:** ...` (the compact form the shared parser
        # also recognises). Without this, bullet-AC stories parse to zero ACs
        # and the verifier passes vacuously.
        bm = AC_BULLET_RE.match(line)
        if bm:
            flush()
            current = ACBlock(
                heading_line=i,
                ac_id=bm.group(1),
                title=(bm.group(2) or "").strip(),
            )
            continue

        if current is None:
            continue

        vm = VERIFY_RE.match(line)
        if vm:
            if current.verify_line is None:
                current.verify_line = i
                current.verifier = vm.group(2).strip()
                current.insert_after = i
            else:
                # Silently dropped before BG0265. Recorded now so a caller can say so.
                current.extra_verifiers.append(vm.group(2).strip())
            continue

        rm = VERIFIED_RE.match(line)
        if rm and current.verified_line is None:
            current.verified_line = i
            current.verified_state = rm.group(2).lower()
            current.verified_when = (rm.group(3) or "").strip()
            continue

        # Track the last bullet line inside the AC so we know where to
        # insert a new Verified line if we need to create one later. A
        # Verify line, once seen, is the preferred anchor (canonical order
        # is Given / When / Then / Verify / Verified) and must not be
        # displaced by later bullets.
        if line.strip().startswith("-") and current.verify_line is None:
            current.insert_after = i

    flush()
    return blocks


# -----------------------------------------------------------------------------
# Verifier execution
# -----------------------------------------------------------------------------


@dataclass
class VerifierResult:
    ok: bool
    kind: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    score: float | None = None  # graded `eval` verifier score, if any
    vacuous: bool = False  # exited clean having run no tests at all


# A filtered runner that matches nothing can exit 0: `unittest` only began returning 5 for
# "no tests ran" in Python 3.12 (the skill supports 3.10+), and `go test -run NoMatch` exits 0
# on every version. An AC whose test class is renamed or deleted then turns into a green no-op -
# exit 0 proving nothing ran rather than that anything held.
#
# Vacuity is decided PER RUNNER FAMILY, from that family's own output and nothing else. A
# blob-wide "did anything pass?" veto was tried and removed: `shell` verifiers routinely run
# `make test` / `npm run check`, and any co-running linter or coverage tool printing "12 passed"
# then silenced the whole gate. Disarming this check is a worse failure than the false alarm it
# was added to fix, so nothing outside a family's own summary may speak for it.
#
# A run can also be empty WITHOUT being zero-count: every selected test skipped. That exits 0
# and prints a summary with real counts in it, so it is judged by reading those counts rather
# than by matching an empty-run phrase - see `_all_skipped` and the per-family signatures below.
#
# For the zero-count case, only `go` and `jest` need a counter-signature, because only they
# report PER UNIT and can say "nothing here" beside a real result. `unittest` and `pytest` each
# print exactly one summary, and their empty and non-empty forms are mutually exclusive ("Ran 0
# tests" vs "Ran 9 tests"; "no tests ran" vs "3 passed, 90 deselected"), so they are judged on
# their own line with no veto.

# unittest: one summary line, exclusive.
_UNITTEST_ZERO = re.compile(r"^Ran 0 tests? in ", re.M)
# pytest: one summary line, exclusive. `--collect-only` reports "collected".
_PYTEST_ZERO = re.compile(r"^(?:=+ )?no tests (?:ran|collected)\b", re.M | re.I)
# pytest again: an ALL-SKIPPED run is not "no tests ran". Collection worked, the node exists,
# the process exits 0 and prints "1 skipped in 0.01s" - and nothing executed. The batch path
# has always refused a skip (`_parse_junit_xml`: a <skipped> case is not a pass), so without
# this the two paths returned opposite verdicts for one run. Matched only when the summary
# counts nothing that ran: "1 passed, 1 skipped" does not match, because a test did run.
# Counts pytest prints after `skipped` and that still mean nothing ran are allowed through.
_PYTEST_ONLY_SKIPPED = re.compile(
    r"^(?:=+ )?\d+ skipped(?:, \d+ (?:deselected|warnings?))* in \d", re.M | re.I)
# The same hole is open in every other family, and each needs its OWN signature because each
# reports skips differently. `unittest` is the one that matters most: it is this repository's
# own default runner, so the silent pass was live on the path the project itself uses.
#
# unittest prints BOTH a run count and a skip count, so the two are compared rather than
# pattern-matched: "Ran 4 tests" beside "OK (skipped=1)" means three tests really ran. Counts
# are summed across the blob so a `shell` line that runs two suites is judged on the whole:
# one empty run beside a real one is not vacuous, both empty is.
_UNITTEST_RAN = re.compile(r"^Ran (\d+) tests? in ", re.M)
_UNITTEST_OK_SKIPPED = re.compile(r"^OK \([^)]*\bskipped=(\d+)", re.M)
# jest: "Tests:  1 skipped, 2 passed, 3 total". A `todo` test never runs either, so it counts
# with the skips - calling it "ran" would stamp a run of nothing but todos green.
_JEST_TESTS_LINE = re.compile(r"^Tests:[ \t]+(.+)$", re.M)
# vitest: "Tests  2 passed | 1 skipped (3)", the total in brackets. The `Test Files` line above
# it does not match: `Tests` must be followed by whitespace, and there it is followed by " Files".
_VITEST_TESTS_LINE = re.compile(r"^[ \t]*Tests[ \t]+(.+?)[ \t]*\((\d+)\)[ \t]*$", re.M)
# go: `go test` WITHOUT -v prints `ok pkg 0.002s` whether every test passed or every test
# called t.Skip, so a non-verbose all-skipped run is genuinely indistinguishable from a green
# one and is not detectable here. With -v each test prints its own outcome line, and that is
# judged: every outcome a SKIP means nothing ran. A parent test whose subtests all skip is
# itself reported PASS, so such a run reads as not-vacuous - a miss, never a false alarm.
_GO_OUTCOME = re.compile(r"^[ \t]*--- (PASS|FAIL|SKIP|BENCH)\b", re.M)
_COUNT_WORD = "(?:^|[ \t|,])(\\d+) {}\\b"
# go: one line per PACKAGE. `?  pkg [no test files]` and `ok pkg 0.0s [no tests to run]` are
# normal output of a green `./...` run, so the whole run is empty only when EVERY package line
# says so.
_GO_PKG_LINE = re.compile(r"^(?:ok|\?|FAIL)\s+\S+.*$", re.M)
_GO_PKG_EMPTY = re.compile(r"\[no tests? (?:to run|files)\]")
# The testing package's own warning, printed inside the test binary when -run matched nothing.
# It is the fallback when no package summary line is present to judge.
_GO_WARN = re.compile(r"^testing: warning: no tests to run$", re.M)
# jest/vitest: one project may report none beside another that passed.
_JEST_ZERO = re.compile(r"^No tests? (?:found|files found)", re.M)
_JEST_RAN = re.compile(r"^PASS\b", re.M)

# Only the verbs that RUN a test suite are judged for vacuity. `file`/`grep`/`http` have no
# concept of a test count, and `grep` in particular could match a signature inside the very
# file it is searching.
_TEST_KINDS = {"pytest", "jest", "vitest", "go", "shell", "fallback"}


def _go_ran_nothing(blob: str) -> bool:
    """True when go reported package results and every one of them ran no tests."""
    pkgs = _GO_PKG_LINE.findall(blob)
    if pkgs:
        return all(_GO_PKG_EMPTY.search(line) for line in pkgs)
    # No package summary to weigh: the testing package's warning is on its own unambiguous
    # evidence that the filter matched nothing.
    return bool(_GO_WARN.search(blob))


def _jest_ran_nothing(blob: str) -> bool:
    """True when jest/vitest found no tests and no project reported a pass."""
    return bool(_JEST_ZERO.search(blob)) and not _JEST_RAN.search(blob)


def _ran_no_tests(kind: str, stdout: str, stderr: str) -> bool:
    """True when a clean exit came from a runner that executed nothing at all."""
    if kind not in _TEST_KINDS:
        return False
    blob = f"{stdout}\n{stderr}"
    return bool(_UNITTEST_ZERO.search(blob)
                or _PYTEST_ZERO.search(blob)
                or _go_ran_nothing(blob)
                or _jest_ran_nothing(blob)
                or _all_skipped(kind, stdout, stderr))


def _pytest_all_skipped(blob: str) -> bool:
    """True when pytest's summary reports skips and nothing that actually ran."""
    return bool(_PYTEST_ONLY_SKIPPED.search(blob))


def _summary_count(segment: str, word: str) -> int:
    """Total of `<n> <word>` counts in one runner summary segment."""
    return sum(int(n) for n in re.findall(_COUNT_WORD.format(word), segment))


def _unittest_all_skipped(blob: str) -> bool:
    """True when every test unittest ran was skipped: `Ran N` matched by `skipped=N`."""
    ran = sum(int(n) for n in _UNITTEST_RAN.findall(blob))
    if not ran:
        return False  # "Ran 0 tests" is the zero signature, judged separately
    return sum(int(n) for n in _UNITTEST_OK_SKIPPED.findall(blob)) == ran


def _summaries_all_skipped(rows: list[tuple[str, int]]) -> bool:
    """True when every (segment, total) summary counts a total > 0 of nothing but skips/todos."""
    if not rows:
        return False
    return all(total and _summary_count(seg, "skipped") + _summary_count(seg, "todo") == total
               for seg, total in rows)


def _jest_all_skipped(blob: str) -> bool:
    """True when jest's `Tests:` summary counts nothing but skips and todos."""
    return _summaries_all_skipped([(seg, _summary_count(seg, "total"))
                                   for seg in _JEST_TESTS_LINE.findall(blob)])


def _vitest_all_skipped(blob: str) -> bool:
    """True when vitest's `Tests` summary counts nothing but skips and todos."""
    return _summaries_all_skipped([(seg, int(total))
                                   for seg, total in _VITEST_TESTS_LINE.findall(blob)])


def _go_all_skipped(blob: str) -> bool:
    """True when go printed per-test outcomes (-v) and every one of them was a SKIP."""
    outcomes = _GO_OUTCOME.findall(blob)
    return bool(outcomes) and all(o == "SKIP" for o in outcomes)


def _all_skipped(kind: str, stdout: str, stderr: str) -> bool:
    """True when a runner selected tests, ran none of them, and exited clean anyway.

    Vacuous for a DIFFERENT reason from a filter that matched nothing, and it takes a different
    remedy - the Verify line names a test that exists, it is switched off - so the caller says
    so rather than telling the reader to re-point a selector that is fine.
    """
    if kind not in _TEST_KINDS:
        return False
    blob = f"{stdout}\n{stderr}"
    return bool(_pytest_all_skipped(blob)
                or _unittest_all_skipped(blob)
                or _jest_all_skipped(blob)
                or _vitest_all_skipped(blob)
                or _go_all_skipped(blob))


_VACUOUS_MSG = ("verifier exited 0 but ran NO tests - a filter that matches nothing "
                "(renamed or deleted test, stale -k/-run pattern) proves nothing. "
                "Re-point the Verify line at a test that exists.")

_SKIPPED_MSG = ("verifier exited 0 but every selected test was SKIPPED - a skipped test "
                "proves exactly as much as one that never ran. Un-skip it, or re-point the "
                "Verify line at a test that runs in this environment.")


def _run_eval(expr: str, timeout: int, cwd: Path, start: float) -> VerifierResult:
    """Graded verifier: `eval <command> --threshold <float>`.

    Shells to a configurable eval tool (promptfoo/deepeval/...), parses a numeric
    `score` from its JSON stdout, and passes only when score >= threshold. The
    tool is a soft dependency; tests stub it. For AI-output and qualitative ACs.
    """
    body = expr[len("eval"):].strip()
    m = re.search(r"--threshold\s+(\S+)\s*$", body)
    if not m:
        return VerifierResult(False, "eval", 2, "", "eval: expected `eval <command> --threshold <float>`", 0)
    try:
        threshold = float(m.group(1))
    except ValueError:
        return VerifierResult(False, "eval", 2, "", f"eval: non-numeric threshold {m.group(1)!r}", 0)
    command = body[:m.start()].strip()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout, cwd=str(cwd))  # nosec B602 - project-authored AC verifier, trusted input (reference-verify.md trust boundary)
    except subprocess.TimeoutExpired:
        return VerifierResult(False, "eval", 124, "", "timeout", int((time.time() - start) * 1000))
    except FileNotFoundError as e:
        return VerifierResult(False, "eval", 127, "", str(e), int((time.time() - start) * 1000))
    duration = int((time.time() - start) * 1000)
    try:
        score = float(json.loads(result.stdout).get("score"))
    except (ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return VerifierResult(False, "eval", result.returncode or 1, result.stdout[-4000:],
                              "eval: no numeric 'score' in the tool's JSON output", duration)
    ok = score >= threshold
    return VerifierResult(ok, "eval", 0 if ok else 1, result.stdout[-4000:],
                          f"score={score} threshold={threshold}", duration, score=score)


_SHELL_DISABLED_MSG = ("shell execution disabled (--no-shell, or the story is stamped "
                       "Provenance: external) - use a structured DSL verb, or pass "
                       "--allow-external to run this story's shell verifiers")


def run_verifier(expression: str, timeout: int, cwd: Path,
                 allow_shell: bool = True, allow_fallback: bool = False) -> VerifierResult:
    """Parse a verifier expression and execute it. `allow_shell=False` blocks the
    shell-backed verbs (shell/eval/http and the fallback) instead of running them - the
    technical control behind the documented trust boundary. `allow_fallback`
    re-enables the legacy unrecognised-head-as-shell behaviour."""
    expr = expression.strip()
    start = time.time()
    if expr.lower() == "eval" or expr.lower().startswith("eval "):
        if not allow_shell:
            return VerifierResult(False, "blocked", 2, "", _SHELL_DISABLED_MSG, 0)
        return _run_eval(expr, timeout, cwd, start)
    try:
        kind, cmd = _build_command(expr, allow_fallback=allow_fallback, cwd=cwd)
    except ValueError as e:
        return VerifierResult(False, "invalid", 2, "", str(e), 0)

    # A string command runs under shell=True (shell/http/fallback verbs); block those
    # when shell execution is disabled rather than executing untrusted content.
    if isinstance(cmd, str) and not allow_shell:
        return VerifierResult(False, "blocked", 2, "", _SHELL_DISABLED_MSG, 0)

    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),  # nosec B602 - gated by allow_shell + provenance
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd),
        )
        duration = int((time.time() - start) * 1000)
        stdout, stderr = result.stdout[-4000:], result.stderr[-4000:]
        # A clean exit that ran nothing is vacuous. So is a pytest run whose named
        # target no longer resolves: a deleted node exits 4, a -k pattern matching nothing
        # exits 5, and both mean the runner ran no tests, so the green they were meant to
        # renew proves nothing. Attributed as vacuous rather than a plain failure
        # because the remedy differs - re-point the Verify line at a test that exists, not
        # debug code that did not break. Scoped to pytest's documented no-collection codes so
        # a shell verb's own nonzero exit stays a plain failure it owns.
        unresolved = kind == "pytest" and result.returncode in (4, 5)
        vacuous = unresolved or (result.returncode == 0 and _ran_no_tests(kind, stdout, stderr))
        # An all-skipped run is vacuous for a different reason and takes a different remedy,
        # so it says so rather than telling the reader to re-point a Verify line that is fine.
        msg = (_SKIPPED_MSG if (vacuous and not unresolved
                                and _all_skipped(kind, stdout, stderr))
               else _VACUOUS_MSG)
        return VerifierResult(
            ok=(result.returncode == 0 and not vacuous),
            kind=kind,
            exit_code=result.returncode,
            stdout=stdout,
            stderr=(f"{stderr}\n{msg}".strip() if vacuous else stderr),
            duration_ms=duration,
            vacuous=vacuous,
        )
    except subprocess.TimeoutExpired:
        duration = int((time.time() - start) * 1000)
        return VerifierResult(False, kind, 124, "", "timeout", duration)
    except FileNotFoundError as e:
        duration = int((time.time() - start) * 1000)
        return VerifierResult(False, kind, 127, "", str(e), duration)


# DSL verbs the verifier recognises; anything else falls through to `shell` (and may be a
# mis-written runner invocation - the 0/7 class). `manual`/`manually` are handled upstream.
_DSL_VERBS = {"pytest", "jest", "vitest", "go", "file", "grep", "http", "shell",
              "manual", "manually"}


def lint_verifier(expr: str) -> str | None:
    """Flag a Verify expression that would fall through to `shell` but looks like a
    mis-written runner invocation - the drift that silently fails at verify time
    (US0001 was 0/7). Advisory: returns a nudge to the DSL, or None when the expression is
    a legitimate DSL verb or a deliberate shell command."""
    head = (expr.split(None, 1)[0].lower() if expr.split() else "")
    if head in _DSL_VERBS:
        return None
    low = expr.lower()
    if head in {"npm", "npx", "yarn", "pnpm"}:
        return "use the `jest <pattern>` / `pytest <node>` verb, not a raw package-manager call"
    if head == "curl" or " returns " in low:
        return "use `http METHOD URL -- <jq>` for a service AC (or `manual` if no runner can run it)"
    if head in {"psql", "docker", "docker-compose"}:
        return "needs a live service - author as `http`, or mark `manual` if it cannot run here"
    return None


# A verifier that only reads prose. Kept beside the DSL verbs it names, so a new
# text-reading verb cannot be added without meeting this list.
_PROSE_VERBS = {"grep", "file"}
#: Statuses at which a criterion is still being AUTHORED. Past these the story has
#: shipped and a retrospective refusal helps nobody - it is the writing moment this
#: guard exists to interrupt.
_AUTHORING_STATUSES = {"draft", "ready"}


def _verifier_targets(expr: str) -> list[str]:
    """The paths a `grep`/`file` expression names, using the DSL's OWN operand split.

    `_build_command` does `pattern, *paths = args`, so operand 0 is the pattern whatever it
    looks like and a leading flag becomes the pattern. Splitting flags out here would be a
    second parse that disagrees with the runner, which is how one earlier version of this
    guard was defeated. Used as the fallback when `_build_command` cannot parse.
    """
    parts = expr.split(None, 1)
    head = parts[0].lower() if parts else ""
    tail = parts[1] if len(parts) > 1 else ""
    if not tail:
        return []
    if head == "file":
        return [tail.strip('"\'')]
    if head == "grep":
        try:
            args = shlex.split(tail)
        except ValueError:
            return []
        return args[1:]
    return []


def _is_markdown(path) -> bool:
    """The ONE place this project decides whether a path is markdown.

    It was decided in two places - once while walking a directory and once while judging the
    result - and the two disagreed on case, so a mutant dropping the walk's `.lower()` flipped
    a real verdict while every test stayed green. Two implementations of one rule is the exact
    defect this whole guard exists to catch, and it had taken up residence inside it.
    """
    return str(path).lower().endswith(".md")


def _reads_a_non_markdown_file(targets: list[str], cwd) -> bool:
    """Can we DEMONSTRATE that the grep runner reads at least one non-markdown file?

    The burden is deliberately inverted, and this is the fifth version of this logic. Every
    previous one tried to enumerate what the runner reads and was beaten by a case it had not
    thought of: a directory glob, a flag as the pattern, a bare directory, hidden and
    symlinked files, `rg --files` listing a file `rg` cannot open, and `rg --files` exiting 2
    on one unreadable subdirectory. Enumeration has now failed five times, so it is no longer
    the thing being trusted.

    A verifier is treated as prose-only unless a non-markdown file it reads can be POINTED AT.
    Every uncertainty therefore refuses rather than allows: rg missing, rg erroring, a file
    listed but unreadable, a symlink `grep -r` will not follow. The cost of a false refusal is
    one author writing `manual`; the cost of a false allowance is a criterion verified by a
    sentence, which this project has already published four times.
    """
    for t in targets:
        p = Path(t) if Path(t).is_absolute() or cwd is None else Path(cwd) / t
        if not p.exists():
            # EQUIVALENT to omitting this: a missing path is neither a file nor a directory,
            # so the two checks below skip it anyway. Kept because it states the reason - the
            # runner warns and carries on, so an unread operand proves nothing - and recorded
            # as equivalent rather than claimed as covered.
            continue
        if p.is_file():
            # A file named on the command line IS read, symlink or not, by both runners.
            if not _is_markdown(p) and os.access(p, os.R_OK):
                return True
            continue
        if not p.is_dir():
            continue
        for f in _runner_candidates(p):
            if _is_markdown(f):
                continue
            if not os.access(f, os.R_OK):
                continue  # listed, but the runner cannot open it - it reads nothing here
            if f.is_symlink():
                # NEITHER runner follows a symlink discovered during a walk: rg does not
                # follow by default, and `grep -r` follows only paths named on the command
                # line. An earlier draft excluded it only when rg was absent, which had the
                # condition backwards and left the escape open with rg present.
                continue
            return True
    return False


def _runner_candidates(directory: Path):
    """Files under `directory` that the runner MIGHT read. Deliberately over-inclusive in the
    safe direction: every caller must still prove a candidate is readable and non-markdown.

    `rg --files` when rg is present and succeeds. Note what that set is NOT: it is what rg
    LISTS, not what rg can OPEN, and it exits 2 if any part of the tree errors. Both were
    escapes. Here a failure yields the plain walk, and because the caller has to prove
    readability anyway, an over-broad candidate set cannot create a false allowance.
    """
    if shutil.which("rg"):
        # rg IS the runner here, and it skips hidden and ignored files. If `rg --files`
        # cannot tell us what it would list - it exits 2 when any part of the tree errors,
        # e.g. one unreadable subdirectory - then we know NOTHING, and falling back to a
        # plain walk would silently reinstate exactly the hidden files rg refuses to read.
        # That fallback was the escape. No candidates means no demonstration, which refuses.
        try:
            cp = subprocess.run(["rg", "--files", str(directory)],
                                capture_output=True, text=True, timeout=30)
            if cp.returncode == 0:
                return sorted(Path(line) for line in cp.stdout.splitlines() if line.strip())
        except (OSError, subprocess.SubprocessError):
            pass
        return []
    # Without rg the runner is `grep -rqE`, which does read hidden and ignored files.
    try:
        return sorted(f for f in directory.rglob("*") if f.is_file())
    except OSError:
        return []


def lint_markdown_evidence(expr: str, cwd=None) -> str | None:
    """REFUSAL: a `grep`/`file` verifier whose every target is markdown proves that
    somebody wrote a sentence, not that the behaviour exists.

    This is the only lint here that refuses rather than advises, because the class has
    already shipped past a human review. US0310 declared four criteria about a guard's
    behaviour and verified them with four `grep`s over the two reference documents the
    same author was editing (`grep "window" reference-sprint.md` was one). All four
    passed, none touched the guard, and the sprint published a verified count four
    higher than its evidence supported. The verifier is self-confirming by construction:
    the author writes the line and the search for it in one sitting, so it is true of
    the line just written and silent about the code.

    Note what is NOT refused. A criterion genuinely ABOUT documentation is legitimate
    and says `manual`, which puts it in the manual count where a reader can weigh it,
    rather than in the passing count where it is indistinguishable from a test. A mixed
    expression that also searches a non-markdown path is left alone: it can discriminate,
    and narrowing it further is a judgement this check has no basis to make.

    The verdict takes the FILES ACTUALLY READ where they resolve, and the tokens as written
    where they do not. Judging only what was written let three expressions through - a
    directory glob, a flag mistaken for the pattern, and a bare recursive directory - and the
    first version of this guard called that difference equivalent in a docstring, which was
    false. Neither reading is sufficient alone: the resolved one depends on the filesystem
    the lint runs on, the written one cannot see where a glob points.

    Still NOT closed, deliberately: a `shell`-prefixed grep bypasses this entirely, because
    `shell` is the documented escape hatch, and an expression whose resolved files are a mix
    of markdown and code is allowed by the same all-or-nothing rule stated above. Both are
    disclosed on BG0264 as well, because a residual named only in a docstring is a residual
    the next author will not read.
    """
    head = (expr.split(None, 1)[0].lower() if expr.split() else "")
    if head not in _PROSE_VERBS:
        return None
    targets = _verifier_targets(expr) if head == "grep" else [expr.split(None, 1)[1].strip('"\'')]
    if head == "grep":
        try:
            kind, argv = _build_command(expr, cwd=cwd)
            if kind == "grep" and isinstance(argv, list) and "--" in argv:
                targets = argv[argv.index("--") + 1:]
        except ValueError:
            pass
    if _reads_a_non_markdown_file(targets, cwd):
        return None
    return ("this verifier reads nothing but prose, so it proves someone wrote a sentence, "
            "not that the behaviour exists - the shape that passed four US0310 criteria "
            "against prose asserting their opposite. Verify the behaviour (`pytest`/`shell`), "
            "or say `manual` if the criterion really is about the document")


def lint_stacked_verifiers(block: "ACBlock") -> str | None:
    """REFUSAL: an AC block carrying more than one `Verify:` line.

    `parse_story` executes the FIRST and reads the rest as ordinary bullets, so a second
    verifier is not a second check - it is a sentence that looks like one. Seven sat in this
    workspace having never run, four on stories at Done, and two of those were counted inside
    a sprint's published claim of 84 criteria verified.

    Refused rather than warned, for the same reason the pseudo-verify refusal is: the author
    sees their verifier on disk and the report counts the criterion as verified, so nothing
    downstream will ever contradict them. A criterion that genuinely needs two checks is two
    criteria, and saying so at author time costs one heading.
    """
    if not block.extra_verifiers:
        return None
    n = len(block.extra_verifiers)
    return (f"{n} further `Verify:` line(s) in this block will NEVER RUN - only the first is "
            f"executed, and the rest parse as ordinary bullets. Dropped: "
            f"{'; '.join(repr(v) for v in block.extra_verifiers)}. A criterion needing two "
            f"checks is two criteria - split the block")


#: Verbs whose selector can be resolved by COLLECTION - asking the runner what a selector
#: would select, without executing a single test body.
_COLLECTABLE = {"pytest"}


#: Per-file collection cache, keyed by (resolved test file, cwd). Collecting a file imports
#: it once; every selector into that file is then answered in-process. This is what keeps the
#: check cheap enough to run on the whole workspace: without it, conformance spawned one
#: `pytest --collect-only` per stamped AC - 306 of them - and turned an 8s gate into 81s.
_COLLECT_CACHE: dict = {}


def _collect_nodes(test_file: str, cwd=None) -> list[str] | None:
    """Every node id `pytest` collects from `test_file`, or None if the file itself will not
    collect (a syntax error, a missing import). Cached per (file, cwd)."""
    key = (test_file, str(cwd) if cwd else None)
    if key in _COLLECT_CACHE:
        return _COLLECT_CACHE[key]
    result: list[str] | None = None
    try:
        cp = subprocess.run(["pytest", "--collect-only", "-q", test_file],
                            capture_output=True, text=True, timeout=120,
                            cwd=str(cwd) if cwd else None)
        if cp.returncode in (0, 5):
            # -q collect lists one node id per line, then a blank line and a summary.
            result = [ln.strip() for ln in cp.stdout.splitlines()
                      if "::" in ln and not ln.startswith(" ")]
    except (OSError, subprocess.SubprocessError):
        result = None
    _COLLECT_CACHE[key] = result
    return result


def _selector_target(expr: str, cwd=None) -> tuple[str | None, str | None]:
    """`(node address, test file)` for a selector, or `(None, None)`.

    THE ONE TARGET PARSER. `selector_resolves`, `selector_near_miss` and the write-time guard all
    need to know what a selector points at, and they answered it separately with predicates that
    had already drifted - one arm tested `.endswith(".py")` and another did not, so the two
    disagreed about a bare-file target. A fourth copy would make the divergence AC4 exists to
    prevent more likely, not less.
    """
    try:
        _kind, argv = _build_command(expr, cwd=cwd)
    except Exception:  # noqa: BLE001 - never raise out of a classifier
        return (None, None)
    if not isinstance(argv, list):
        return (None, None)   # a shell-backed verb: a string, not an argv list
    target = next((a for a in argv[1:] if "::" in a or a.endswith(".py")), None)
    if target is None:
        return (None, None)
    return (target, target.split("::", 1)[0])


def selector_target_file(expr: str, cwd=None) -> str | None:
    """The test FILE a selector points at, or None when it names none this way."""
    return _selector_target(expr, cwd)[1]


def selector_collected(expr: str, cwd=None) -> bool:
    """Did the selector's target file yield a NODE LIST?

    The discriminator the write-time guard needs, and the one `selector_resolves` collapses. That
    predicate answers False for three different facts: a node absent from a file that listed its
    nodes (a typo), a file that does not exist, and a file that exists but will not collect - a
    missing import, a syntax error, a project whose dependencies are not installed. Only the first
    is a mistake the author can fix by reading the file, and only the first may be refused at
    write time; treating the third as a typo would refuse every selector in a fresh clone and tell
    the author their test does not exist while it sits on disk.
    """
    _node, test_file = _selector_target(expr, cwd)
    return test_file is not None and _collect_nodes(test_file, cwd) is not None


def selector_resolves(expr: str, cwd=None) -> bool | None:
    """Does this verifier's selector still select anything? None when unanswerable.

    Resolution is decided by COLLECTION, not execution, and the collected node list is CACHED
    per test file, so the whole workspace costs one collection per distinct file rather than
    one per stamped AC. A sweep is what let a stamp read green for two days against a test that
    did not exist; a per-AC subprocess is what made checking for that unaffordable.

    Returns None - not False - for a verifier whose selector cannot be resolved this way
    (`manual`, `grep`, `shell`, a runner that is absent, a file that will not collect).
    Unanswerable is not the same fact as unresolvable, and reporting it as stale would mark
    every non-pytest stamp dead.
    """
    head = (expr.split(None, 1)[0].lower() if expr.split() else "")
    if head not in _COLLECTABLE or _is_manual(expr):
        return None
    if not shutil.which(head):
        return None  # the runner is absent here; that says nothing about the selector
    try:
        kind, argv = _build_command(expr, cwd=cwd)
    except ValueError:
        return None
    if not isinstance(argv, list) or len(argv) < 2:
        return None
    # argv is `pytest -q <target> [-k pat]`. The file target is read by the ONE target parser.
    target, test_file = _selector_target(expr, cwd)
    if target is None:
        return None
    nodes = _collect_nodes(test_file, cwd)
    if nodes is None:
        return False  # the file itself does not collect - the node/pattern cannot resolve
    # Node address: the exact id (or a prefix of it, for a class selecting its methods).
    if "::" in target:
        return any(n == target or n.startswith(target + "::") for n in nodes)
    # -k pattern: pytest's -k is a boolean expression over substring matches of the node id.
    kflag = argv.index("-k") if "-k" in argv else -1
    if kflag != -1 and kflag + 1 < len(argv):
        pat = argv[kflag + 1]
        return _k_selects(pat, nodes)
    # A bare file target with no filter selects whatever it collects.
    return bool(nodes)


def _k_selects(pattern: str, nodes: list[str]) -> bool:
    """Does pytest's `-k <pattern>` match any node id? Supports the `and/or/not` and
    parenthesised forms pytest accepts, over case-insensitive substring matches - enough to
    answer "does this select anything" without importing pytest's own expression engine."""
    import re as _re
    tokens = _re.findall(r"\(|\)|\band\b|\bor\b|\bnot\b|[^\s()]+", pattern)
    for node in nodes:
        low = node.lower()
        reduced = [
            tok if tok in ("and", "or", "not", "(", ")")
            else ("True" if tok.lower() in low else "False") for tok in tokens]
        try:
            if _eval_bool(reduced):
                return True
        except SyntaxError:
            return True  # an expression we cannot evaluate: assume it selects, never false-dead
    return False


def _eval_bool(tokens: list[str]) -> bool:
    """Evaluate a token stream of `True`/`False`/`and`/`or`/`not`/parens, with Python's
    precedence: `not` binds tightest, then `and`, then `or`.

    This replaced `eval()`, which bandit flags as B307 and which carried a `# noqa: S307` that
    silences ruff and NOT bandit - so the lane failed while the code looked annotated. The
    operands were only ever ours, so the risk was theoretical; the reason to remove it anyway is
    that a suppression has to be re-argued by every reader, and a parser that cannot execute
    anything does not. Checked against Python's own evaluation over 5,000 generated expressions.

    Raises `SyntaxError` on a malformed stream. The caller reads that as "assume it selects",
    because a `-k` expression this cannot parse must never be reported as selecting nothing.
    """
    pos = 0

    def peek() -> str | None:
        return tokens[pos] if pos < len(tokens) else None

    def take() -> str:
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def atom() -> bool:
        tok = peek()
        if tok == "(":
            take()
            value = or_expr()
            if peek() != ")":
                raise SyntaxError("unbalanced parenthesis")
            take()
            return value
        if tok == "not":
            take()
            return not atom()
        if tok in ("True", "False"):
            return take() == "True"
        raise SyntaxError(f"unexpected token {tok!r}")

    def and_expr() -> bool:
        value = atom()
        while peek() == "and":
            take()
            value = atom() and value
        return value

    def or_expr() -> bool:
        value = and_expr()
        while peek() == "or":
            take()
            value = and_expr() or value
        return value

    result = or_expr()
    if pos != len(tokens):
        raise SyntaxError("trailing tokens")
    return result


def selector_near_miss(expr: str, cwd=None) -> str | None:
    """For a selector that does NOT resolve, the closest node that DOES - or None.

    A refusal saying only "this does not resolve" sends the author back to grep, which is the
    step they skipped to get here. The overwhelmingly common cause is a real test named slightly
    wrong - this repository's own scar is a class name typed as it OUGHT to have been rather than
    read off the file, twice in one session - so naming the near miss closes the loop where it
    actually broke.

    Reuses `_build_command` and the `_collect_nodes` cache rather than parsing selectors a second
    time: the divergent-reader defect is the one CR0508 exists to avoid, and a hint that disagreed
    with the refusal about what a selector means would be worse than no hint.

    Best-effort by construction. None whenever there is nothing confident to say, so a caller can
    always render it as an optional clause.
    """
    target, test_file = _selector_target(expr, cwd)
    if target is None or "::" not in target:
        return None
    node = target.partition("::")[2]
    nodes = _collect_nodes(test_file, cwd)
    if not nodes:
        return None
    parts = [p for p in node.split("::") if p]
    if not parts:
        return None
    # The recurring shape: right file, right METHOD, wrong class. Answer it exactly - a node
    # whose final segment matches names the class the author meant.
    leaf = parts[-1]
    same_leaf = [n for n in nodes if n.rsplit("::", 1)[-1] == leaf and n != target]
    if same_leaf:
        return f"did you mean {same_leaf[0]}"
    # Otherwise the closest name among the segments actually collected at that depth.
    import difflib  # noqa: PLC0415 - local: only reached on a refusal path
    depth = len(parts) - 1
    candidates = {seg[depth] for seg in (n.split("::")[1:] for n in nodes) if len(seg) > depth}
    close = difflib.get_close_matches(parts[-1], sorted(candidates), n=1, cutoff=0.6)
    if close:
        return f"no `{parts[-1]}` in {test_file}; did you mean `{close[0]}`"
    return None


def unresolvable_stamps(path: Path, cwd=None) -> list[dict]:
    """Stamped-green ACs in `path` whose verifier no longer selects anything.

    Only ACs recorded as verified are examined: an unstamped AC makes no claim, so a dead
    selector there is the author's business at the next run, not a false green on disk.
    """
    out: list[dict] = []
    text = sdlc_md.read_text_safe(path)
    for block in parse_story(text):
        if (block.verified_state or "").strip().lower() != "yes" or not block.verifier:
            continue
        if selector_resolves(block.verifier, cwd) is False:
            out.append({"ac": block.ac_id, "verifier": block.verifier,
                        "record": sdlc_md.extract_record_id(path.stem) or path.stem})
    return out


#: A script is CLI-BEARING when it exposes an entry point a user runs. Both markers, because
#: a module with `main()` and no parser is a library with a convenience runner, and one with a
#: parser and no `main()` is not reachable as a command either.
_CLI_MARKERS = ("def main(", "argparse")

#: What entering the front door LOOKS LIKE in a test's source. Deliberately about execution -
#: calling the entry point, or running the script as a process - never about naming. A
#: convention is satisfied by a rename; this must not be.
_LANE_MARKERS = ("main(", "subprocess.run", "subprocess.check", "runpy", "check_output")

# Helpers a scoped node calls, for the one-level resolution in `_enters_the_lane`. `self.x(` and
# a bare `x(` both, because these suites use module-level helpers as often as methods.
_HELPER_CALL_RE = re.compile(r"(?:self\.)?\b(_[A-Za-z0-9_]+)\s*\(")


def _lane_test_paths(expr: str) -> list[str]:
    """The test FILES a runner expression names.

    Separate from `_verifier_targets`, which reads the `grep`/`file` DSL operands and returns
    nothing for a runner selector. A pytest node id carries the path before `::`; jest, vitest
    and go all name the file plainly. Extensions rather than a runner table, so a runner added
    tomorrow is covered instead of silently exempt (LL0013).
    """
    out = []
    for token in expr.replace("'", " ").replace('"', " ").split():
        path = token.split("::", 1)[0]
        if path.endswith((".py", ".js", ".ts", ".tsx", ".go")) and "/" in path:
            out.append(path)
    return out


def _is_cli_bearing(path: Path) -> bool:
    text = sdlc_md.read_text_safe(path)
    return bool(text) and all(m in text for m in _CLI_MARKERS)


def _node_source(text: str, node: str) -> str | None:
    """The source of ONE test function, by name, or None when it cannot be isolated.

    Whole-file matching is what made the first version of this detector useless: these test
    modules are thousands of lines, so a single `main([...])` call anywhere marked every
    criterion in the file clean. Measured over 615 units it reported ZERO findings - a
    detector that never fires. The verifier names a node; judge that node.
    """
    if not node:
        return None
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("def ", "async def ")) and f" {node}(" in f" {stripped[4:]}":
            start = i
            break
        if stripped.startswith(f"def {node}(") or stripped.startswith(f"async def {node}("):
            start = i
            break
    if start is None:
        return None
    indent = len(lines[start]) - len(lines[start].lstrip())
    body = [lines[start]]
    for line in lines[start + 1:]:
        if line.strip() and (len(line) - len(line.lstrip())) <= indent:
            break
        body.append(line)
    return "\n".join(body)


def _enters_the_lane(test_path: Path, node: str = "") -> bool:
    """Whether the verifier's own test SOURCE shows it entering the shipped entry point.

    Scoped to the named node where the selector gives one. Falls back to the whole file only
    when the node cannot be isolated - and that fallback is deliberately permissive, because
    reporting a criterion whose test could not even be located would be noise about the
    detector rather than about the code.
    """
    text = sdlc_md.read_text_safe(test_path)
    if not text:
        return False
    scoped = _node_source(text, node) if node else None
    if scoped is None:
        return any(m in text for m in _LANE_MARKERS)
    if any(m in scoped for m in _LANE_MARKERS):
        return True
    # ONE level of same-file helper. A class that shells the CLI once in a `_run` helper and
    # calls `self._run(...)` from every method is a correct and common shape, and scoping to the
    # node alone reports it as never entering the lane - which is a detector telling tested work
    # it is untested. One level only: resolving a call graph would restore the whole-file
    # permissiveness that made the first version report 0/615.
    for name in set(_HELPER_CALL_RE.findall(scoped)):
        helper = _node_source(text, name)
        if helper and any(m in helper for m in _LANE_MARKERS):
            return True
    return False


def lane_check(root, unit_paths) -> list[dict]:
    """Criteria whose verifiers never enter the shipped entry point.

    US0577 shipped `brief_fingerprint` with a passing acceptance test and a feature that did
    not work: the test computed it IN-PROCESS while the CLI never called it. A library test
    cannot see a missing lane, because the wiring between entry point and function is exactly
    the part it does not exercise - and that is where this defect class lives.

    Reported, never failed. The yield is measured before the check is allowed to block, on the
    same terms the claim-drift lane shipped under.
    """
    root = Path(root)
    out: list[dict] = []
    for path in unit_paths:
        path = Path(path)
        text = sdlc_md.read_text_safe(path)
        if not text:
            continue
        declared = [f.strip().strip("`") for f in sdlc_md.affects_files(text)]
        cli = [d for d in declared
               if d.endswith(".py") and _is_cli_bearing(root / d)]
        if not cli:
            continue  # nothing here is reachable as a command; the question does not arise
        # PER UNIT, not per criterion. Judged per AC this flagged 563 of 615 units, because
        # most individual tests legitimately exercise a library function and not every
        # criterion is about the command. The defect being caught is narrower and precise:
        # a unit that ships a CLI change where NOTHING in its own verifiers ever enters the
        # entry point. That is exactly US0577 - `brief_fingerprint` had a passing acceptance
        # test computing it in-process while no command called it at all.
        checked, entered, first = [], False, None
        for block in parse_story(text):
            expr = (block.verifier or "").strip()
            if not expr or expr.lower().startswith("manual"):
                continue
            node = ""
            for token in expr.split():
                if "::" in token:
                    node = token.rsplit("::", 1)[-1]
                    break
            targets = [root / tgt for tgt in _lane_test_paths(expr)]
            targets = [t for t in targets if t.exists()]
            if not targets:
                continue
            checked.append(expr)
            first = first or (block.title or expr[:60])
            if any(_enters_the_lane(t, node) for t in targets):
                entered = True
                break
        if checked and not entered:
            out.append({
                "unit": sdlc_md.extract_record_id(path.stem) or path.stem,
                "ac": first or "",
                "cli": cli,
                "verifier": checked[0],
                "why": f"this unit changes a command ({', '.join(cli)}) and NONE of its "
                       f"{len(checked)} verifier(s) enters the shipped entry point - the "
                       f"wiring is the part a library test does not exercise",
            })
    return out


def duplicate_verifiers(paths) -> list[dict]:
    """Verify commands that appear byte-identically under more than one AC.

    Two ACs sharing a selector cannot both be discriminating: a regression in either
    behaviour fails both, and neither AC tells you which one broke. It is also how a
    whole-file selector spreads - `discover -p test_x.py` copied onto every AC of a story
    reads as green evidence for criteria it never separately exercised.

    Reported per duplicated command with every AC that claims it, so the author can see
    which criteria are leaning on the same run. Advisory: identical commands are legitimate
    in a few cases (two ACs asserting one indivisible behaviour), and this names them rather
    than refusing them.
    """
    seen: dict[str, list[str]] = {}
    written: dict[str, set[str]] = {}
    for p in paths:
        if not p.exists():
            continue
        text = sdlc_md.read_text_safe(p)  # a corrupt story must not abort the duplicate scan
        rec = sdlc_md.extract_record_id(p.stem) or p.stem
        for block in parse_story(text):
            if not block.verifier:
                continue
            expr = dup_group_key(block.verifier)
            if _is_manual(expr):
                continue
            # Grouped on the RESOLVED command, so two criteria that name one run in different
            # words join the group they actually share instead of forming a group of one under
            # each spelling and being reported as no duplicate at all.
            seen.setdefault(expr, []).append(f"{rec} {block.ac_id}")
            written.setdefault(expr, set()).add(" ".join(block.verifier.split()))
    out = []
    for expr, acs in sorted(seen.items()):
        if len(acs) < 2:
            continue
        # REPORTED as the author wrote it, never as the internal key. The key is a resolved argv
        # - `-q` the runner supplies, flags in sorted order - and quoting that back at an author
        # names a line that appears nowhere in their file. The lowest spelling is taken so the
        # identity is deterministic, and every other spelling in the group is listed beside it,
        # since "these two lines are the same run" is the whole finding when they differ.
        spellings = sorted(written.get(expr) or [expr])
        row = {"verifier": spellings[0], "acs": acs}
        if len(spellings) > 1:
            row["also_written"] = spellings[1:]
        out.append(row)
    return out


# The runners a Verify verb shells out to, for the advisory availability check.
# `shell` and `manual` are exempt (sh is always present / nothing runs).
_RUNNER_BINARIES = {"pytest": ("pytest",), "jest": ("jest",), "vitest": ("vitest",),
                    "go": ("go",), "rg": ("rg",), "http": ("curl", "jq")}


def lint_runner_available(expr: str, _which=None) -> str | None:
    """Advisory: the Verify expression's runner is absent from THIS machine's PATH.

    Strictly informational - the author machine's PATH may legitimately differ
    from the machine that verifies (CI, a teammate), so the wording owns that
    ambiguity and the check never blocks or fails anything on its own."""
    import shutil as _shutil
    which = _which or _shutil.which
    head = (expr.split(None, 1)[0].lower() if expr.split() else "")
    missing = [b for b in _RUNNER_BINARIES.get(head, ()) if which(b) is None]
    if not missing:
        return None
    names = ", ".join(missing)
    return (f"runner '{names}' is not on this machine's PATH - install it here, "
            f"rewrite the line, or ignore if verification runs elsewhere (advisory)")


def _expand_globs(paths: list[str], cwd) -> list[str]:
    """Expand any glob path against cwd - the grep verb runs argv, with no shell to expand it.

    An unmatched glob passes through literally so the tool reports an honest not-found (a real
    failing AC) rather than silently matching nothing. A plain path is returned untouched.
    """
    out: list[str] = []
    for p in paths:
        if any(ch in p for ch in "*?["):
            base = os.path.join(str(cwd), p) if cwd else p
            hits = sorted(glob.glob(base, recursive=True))
            out.extend(hits if hits else [p])
        else:
            out.append(p)
    return out


def _build_command(expr: str, allow_fallback: bool = False, cwd=None) -> tuple[str, list[str] | str]:
    """Translate a verifier expression into a subprocess command.

    Returns (kind, command) where command is a list for argv-style runs or
    a string for shell=True runs. An unrecognised head raises ValueError unless
    `allow_fallback` is set - so a typo or stray prose line is an invalid verifier,
    not a silent shell execution. The legacy whole-expression-as-shell
    behaviour stays available behind the opt-in.
    """
    # Split first token
    parts = expr.split(None, 1)
    head = parts[0].lower() if parts else ""
    tail = parts[1] if len(parts) > 1 else ""

    if head == "pytest" and tail:
        return "pytest", ["pytest", "-q"] + shlex.split(tail)
    if head == "jest" and tail:
        return "jest", ["jest", "-t", tail.strip('"\'')]
    if head == "vitest" and tail:
        return "vitest", ["vitest", "run", "-t", tail.strip('"\'')]
    if head == "go" and tail:
        # Format: go <path> -run <node>
        return "go", ["go", "test"] + shlex.split(tail)
    if head == "file" and tail:
        path = tail.strip('"\'')
        return "file", ["test", "-e", path]
    if head == "grep" and tail:
        # grep <regex> <path>  - the path may be a glob (e.g. src/**/*.ts).
        try:
            args = shlex.split(tail)
        except ValueError as e:
            raise ValueError(f"grep: {e}")
        if len(args) < 2:
            raise ValueError("grep: expected <regex> <path>")
        pattern, *paths = args
        # The verb runs as an argv list (no shell), so a glob would otherwise reach rg/grep
        # literally and always miss - the documented `src/**/*.ts` example matched present code
        # only after this expansion, against cwd, before the tool sees the paths.
        paths = _expand_globs(paths, cwd)
        # rg (Rust regex) when present, else grep -rqE (POSIX ERE). Different dialects: keep grep
        # patterns POSIX-ERE-portable, or install rg for consistent behaviour - see
        # reference-verify.md.
        #
        # `-e <pattern>` and a `--` terminator, never a bare positional: a pattern that starts
        # with a dash (`-Ran`, `--foo`) was otherwise read by the tool as its own flags, so the
        # AC silently stopped searching for what it said it searched for - it errored out, or
        # worse, ran a different search and reported on that.
        if shutil.which("rg"):
            return "grep", ["rg", "-q", "-e", pattern, "--"] + paths
        return "grep", ["grep", "-rqE", "-e", pattern, "--"] + paths
    if head == "http" and tail:
        return "http", _build_http(tail)
    if head == "shell" and tail:
        return "shell", tail  # shell=True

    if allow_fallback:
        # Legacy opt-in: treat the whole expression as a shell command.
        return "shell", expr
    raise ValueError(
        f"unrecognised verifier {head!r} - use a DSL verb (pytest/jest/vitest/go/file/"
        f"grep/http/eval) or prefix an explicit `shell` to run it as a shell command")


_HTTP_SCHEMES = ("http", "https")


def _restricted_http_hosts() -> tuple[str, ...]:
    """Host allow-list for the `http` verb. Non-empty turns on restricted mode: a target
    host outside the list is refused. Sourced from SDLC_VERIFY_HTTP_HOSTS (comma-separated);
    empty by default (unrestricted, subject only to the scheme floor)."""
    raw = os.environ.get("SDLC_VERIFY_HTTP_HOSTS", "")
    return tuple(h.strip().lower() for h in raw.split(",") if h.strip())


def _check_http_target(url: str) -> None:
    """Safety floor for the `http` verb, enforced before a curl command is built:
    only http/https schemes (blocks file://, ftp://, gopher:// SSRF vectors), and - when a
    host allow-list is configured (restricted mode) - only allow-listed hosts. Raises
    ValueError (an invalid verifier, exit 2) when the target is refused."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in _HTTP_SCHEMES:
        # refuse an empty scheme in every mode: a scheme-less URL lets curl guess the protocol
        # from the host (an `ftp.`-prefixed host goes FTP), defeating the http/https-only floor.
        raise ValueError(f"http: scheme {scheme or '(none)'!r} is not permitted (only http/https)")
    allowed = _restricted_http_hosts()
    if allowed:
        # (an empty scheme is already refused above, in every mode)
        host = (parsed.hostname or "").lower()
        if host not in allowed:
            raise ValueError(
                f"http: host {host!r} is not in the allow-list {list(allowed)} (restricted mode)")


def _build_http(tail: str) -> str:
    """Translate `http GET /url -- .field == "x"` into a curl+jq shell pipe."""
    # Split on " -- " to separate URL from jq assertion
    if " -- " not in tail:
        raise ValueError("http: expected `METHOD URL -- <jq assertion>`")
    url_part, jq_expr = tail.split(" -- ", 1)
    url_parts = url_part.split(None, 1)
    if len(url_parts) != 2:
        raise ValueError("http: expected `METHOD URL`")
    method, url = url_parts
    method = method.upper()
    _check_http_target(url)
    # Escape single quotes in the jq expression
    jq_expr_escaped = jq_expr.replace("'", "'\\''")
    curl = f"curl -sf -X {shlex.quote(method)} {shlex.quote(url)}"
    return f"{curl} | jq -e '{jq_expr_escaped}' > /dev/null"


# -----------------------------------------------------------------------------
# Story update
# -----------------------------------------------------------------------------


def update_verified(lines: list[str], block: ACBlock, new_state: str) -> list[str]:
    """Return a modified list of lines with the AC's Verified state set.

    Adds a new Verified line if one does not exist. Preserves original
    indentation.
    """
    today = sdlc_md.now_date()
    new_line = None

    if not lines:
        return lines

    if block.verified_line is not None and block.verified_line < len(lines):
        orig = lines[block.verified_line]
        indent_match = re.match(r"^(\s*)", orig)
        indent = indent_match.group(1) if indent_match else ""
        new_line = f"{indent}- **Verified:** {new_state} ({today})"
        lines = lines.copy()
        lines[block.verified_line] = new_line
        return lines

    # Insert after the Verify line or last bullet. Clamp to the file bounds so
    # malformed markdown (a stale line index past EOF) can never IndexError.
    insert_at = block.insert_after if block.insert_after is not None else block.heading_line
    insert_at = max(0, min(insert_at, len(lines) - 1))
    # Inherit indent from the line we're inserting after
    base = lines[insert_at]
    indent_match = re.match(r"^(\s*)", base)
    indent = indent_match.group(1) if indent_match else ""
    new_line = f"{indent}- **Verified:** {new_state} ({today})"
    lines = lines[: insert_at + 1] + [new_line] + lines[insert_at + 1 :]
    return lines


# -----------------------------------------------------------------------------
# Orchestration
# -----------------------------------------------------------------------------


@dataclass
class StoryReport:
    path: str
    ac_count: int = 0
    verified: int = 0
    failed: int = 0
    stale: int = 0
    manual: int = 0        # AC authored `Verify: manual ...` - a declared human-checked judgement
    vacuous: int = 0       # AC whose verifier exited 0 having run no tests - counted as failed
    unspecified: int = 0   # AC with NO Verify: line at all - an omission, not a declaration
    passed: list[str] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)
    changed: int = 0
    flips: list[dict] = field(default_factory=list)  # pending/applied (ac, old_state, new_state)
    # sha256 over the ACs and their verifiers as they stood at verification time; the
    # Done gate compares it to the story's current fingerprint (see `ac_fingerprint`)
    ac_fingerprint: str = ""


def _is_manual(expression: str) -> bool:
    """True for a human-checked AC authored as `Verify: manual ...` (or `manually ...`) - counted
    manual, never executed. Keyed on the leading token so a real command like `pnpm test`
    is unaffected."""
    toks = expression.strip().lstrip("`*_ ").split()
    return bool(toks) and toks[0].strip("`*:.,").lower() in {"manual", "manually"}


def _parse_jest_json(stdout: str) -> list[dict]:
    """Flatten `jest --json` output to [{name, ok}] over every assertion. Tolerates
    leading non-JSON noise; returns [] when no JSON object is present or it does not parse."""
    out = stdout.strip()
    start = out.find("{")
    if start < 0:
        return []
    try:
        data = json.loads(out[start:])
    except ValueError:
        return []
    asserts: list[dict] = []
    for tr in data.get("testResults", []):
        for a in tr.get("assertionResults", []):
            name = a.get("fullName") or a.get("title") or ""
            asserts.append({"name": name, "ok": a.get("status") == "passed"})
    return asserts


def jest_batch_cache(repo_root: Path, timeout: int) -> list[dict]:
    """Run jest ONCE with --json and return its flattened assertions, so per-AC jest
    verifiers resolve against the result set instead of a cold `jest -t` start each. Empty on any
    failure -> callers fall back to the per-AC path."""
    try:
        result = subprocess.run(["npx", "--no-install", "jest", "--json", "--silent"], cwd=str(repo_root),
                                capture_output=True, text=True, timeout=timeout)  # nosec B603 B607
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
        sdlc_md.debug("jest_batch_cache", exc)  # advisory: fall back to the per-AC path
        return []
    return _parse_jest_json(result.stdout)


def _parse_junit_xml(text: str, scope: list[str]) -> dict[str, bool]:
    """Flatten a pytest JUnit XML report into {node_id: passed}, keyed the way a Verify line
    addresses a test: `path/to/test_x.py::Class::test_name`.

    pytest's JUnit output carries NO `file` attribute - only a dotted `classname` such as
    `.claude.skills.sdlc-studio.scripts.tests.test_status.CensusTests`, in which the directory
    separators and the module boundary are indistinguishable. Reconstructing a path from that
    alone is ambiguous, so it is not attempted: `scope` is the list of files the run was given,
    each is converted to its dotted form once, and a testcase is attributed to the file whose
    dotted form its classname matches. Anything unmatched is dropped rather than guessed, and a
    dropped node simply falls through to its own subprocess.
    """
    import xml.etree.ElementTree as ET  # noqa: PLC0415 - stdlib, only needed in batch mode
    try:
        root = ET.fromstring(text)  # nosec B314 - our own pytest output, not external input
    except ET.ParseError as exc:
        sdlc_md.debug("_parse_junit_xml", exc)
        return {}
    dotted = {f[:-3].replace("/", "."): f for f in scope if f.endswith(".py")}
    out: dict[str, bool] = {}
    for case in root.iter("testcase"):
        cname, name = case.get("classname") or "", case.get("name") or ""
        if not cname or not name:
            continue
        # A skip is NOT a pass. A skipped verifier proves nothing, and reporting it green is
        # the vacuous pass this whole layer exists to refuse.
        ok = not any(case.find(t) is not None for t in ("failure", "error", "skipped"))
        for dot, path in dotted.items():
            if cname == dot:                       # module-level test function
                out[f"{path}::{name}"] = ok
            elif cname.startswith(dot + "."):      # class-based test
                out[f"{path}::{cname[len(dot) + 1:]}::{name}"] = ok
    return out


def pytest_verifier_files(paths: list[Path]) -> list[str]:
    """The distinct test FILES the `pytest` verifiers in `paths` name.

    The batch run is scoped to exactly these, never to the repo root. A bare `pytest .` here
    collects benchmark fixtures that fail at import, so an unscoped batch returns nothing and
    every verifier falls back to its own subprocess - the slowness stays and the batch silently
    does nothing. Scoping to the named files also keeps this project-agnostic: no test directory
    is hardcoded, and a project whose tests live elsewhere batches just as well.
    """
    files: dict[str, None] = {}
    for path in paths:
        for block in parse_story(_read_body(path)):
            head, _, tail = (block.verifier or "").strip().partition(" ")
            if head.lower() != "pytest" or not tail:
                continue
            target = tail.strip()
            if target.startswith("-") or " " in target:
                continue
            files.setdefault(target.split("::", 1)[0], None)
    return list(files)


def pytest_batch_collected(nodes: dict[str, bool]) -> set[str]:
    """The test FILES the batch run actually collected, derived from the node ids it produced.

    This is what lets an ABSENT node be judged without a subprocess. If a file collected and a
    node in it is not in the cache, that node does not exist - which is exactly the verdict the
    per-AC path reaches via pytest's exit code 4 (no collection), reported as VACUOUS rather
    than as a plain failure because the remedy differs: re-point the Verify line, do not debug
    code that did not break. If the file did NOT collect, nothing is known and the verifier must
    still run for itself.
    """
    return {n.split("::", 1)[0] for n in nodes}


def pytest_batch_cache(repo_root: Path, timeout: int,
                       targets: list[str] | None = None) -> dict[str, bool]:
    """Run pytest ONCE and return {node_id: passed}, so per-AC pytest verifiers resolve against
    one result set instead of a cold process start each.

    This is the release gate's cost. `--release` runs every acceptance criterion in the
    workspace: 694 of the 1,223 Verify lines are pytest, and a bare pytest start costs ~1.26s
    here before a single relevant assertion runs, so the spawns alone were ~15 minutes and the
    gate could not be completed inside any usable timeout. Jest has had this treatment
    since batch mode was added; pytest had not.

    Empty on any failure, so every caller falls back to the authoritative per-AC subprocess -
    a batch that silently resolved nothing would turn the release gate green by running nothing,
    which is worse than the slowness it fixes.
    """
    import tempfile  # noqa: PLC0415 - only needed in batch mode
    scope = [t for t in (targets or []) if (repo_root / t).is_file()]
    if not scope:
        return {}   # nothing to batch, or nothing that exists: fall back per-AC
    with tempfile.TemporaryDirectory() as d:
        report = Path(d) / "junit.xml"
        try:
            # `--continue-on-collection-errors` is load-bearing, not defensive. This repo's
            # two suites (scripts/tests and tools/tests) are discovered SEPARATELY and cannot
            # be collected in one pytest run: collecting them together raised 12 errors and
            # pytest aborted with `Interrupted`, so the batch returned nothing and every
            # verifier fell back to its own spawn - the fix silently doing nothing. With the
            # flag, whatever collects is cached and the rest falls through per-AC, which is
            # the honest degrade: uncached never means green, only unbatched.
            subprocess.run(["pytest", "-q", "--tb=no", "--continue-on-collection-errors",
                            f"--junit-xml={report}", *scope],
                           cwd=str(repo_root), capture_output=True, text=True,
                           timeout=timeout)  # nosec B603 B607
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
            sdlc_md.debug("pytest_batch_cache", exc)
            return {}
        if not report.is_file():
            return {}
        return _parse_junit_xml(sdlc_md.read_text_safe(report), scope)


def resolve_pytest_from_cache(verifier: str, nodes: dict[str, bool],
                              collected: set[str] | None = None) -> VerifierResult | None:
    """Resolve a `pytest <node>` verifier against one cached run.

    None when the verb is not pytest, when the line carries flags rather than a bare node id, or
    when the node is ABSENT from the cache - and that last case matters most. An unknown node is
    exactly the deleted-target case the per-AC path reports as VACUOUS, so it must fall through
    to the authoritative subprocess rather than be reported as a pass or a plain failure here.
    """
    head, _, tail = verifier.strip().partition(" ")
    if head.lower() != "pytest" or not tail:
        return None
    target = tail.strip()
    if target.startswith("-") or " " in target:
        return None  # flags or multiple targets: let the subprocess own it
    ok = nodes.get(target)
    if ok is None:
        # Absent from the cache. If its file COLLECTED, the node genuinely does not exist and
        # the answer is known: vacuous, the same verdict the subprocess reaches on exit 4.
        # If the file did not collect, nothing is known - fall through and let it run.
        if collected and target.split("::", 1)[0] in collected:
            return VerifierResult(
                False, "pytest", 4, "",
                f"no such test node: {target} - the batch collected its file and the node is "
                f"not in it, so the verifier names a test that does not exist", 0,
                vacuous=True)
        return None
    # The cache records pass / not-pass, and a skip is not a pass, so a red test and a
    # skipped one are indistinguishable here. Calling both a "failure" sent the reader to
    # debug code that may never have run, so the verdict says only what is known.
    return VerifierResult(ok, "pytest", 0 if ok else 1, "",
                          "" if ok else f"cached pytest run for {target} did not pass "
                                        "(failed, errored, or skipped)", 0)


def resolve_jest_from_cache(verifier: str, asserts: list[dict]) -> VerifierResult | None:
    """Resolve a `jest <pattern>` verifier against cached assertions, mirroring `jest -t`:
    pass iff >=1 assertion name MATCHES the pattern as a regex and all matching pass. None when
    the verb is not jest, when the pattern will not compile, or when nothing matches -> the
    caller runs the authoritative per-AC subprocess.

    The pattern is a regex, not a substring. `jest -t` is `testNamePattern`, so `total$` selects
    "renders the total" and not "renders the totals" - selecting by containment computes the
    verdict over a DIFFERENT set of tests from the one jest would run, and under `--release`
    this cache stands in for the authoritative run in a blocking lane. A pattern Python cannot
    compile is not a verdict either: fall through and let the subprocess answer, rather than
    guess with the wrong matcher.
    """
    head, _, tail = verifier.strip().partition(" ")
    if head.lower() != "jest" or not tail:
        return None
    pat = tail.strip().strip('"\'')
    try:
        rx = re.compile(pat)
    except re.error as exc:
        sdlc_md.debug("jest_cache_pattern", exc)
        return None
    matches = [a for a in asserts if rx.search(a["name"])]
    if not matches:
        return None
    ok = all(a["ok"] for a in matches)
    return VerifierResult(ok, "jest", 0 if ok else 1, "",
                          "" if ok else f"cached jest failure for {pat!r}", 0)


def _read_body(path: Path | str) -> str:
    """An artefact body, defaulted to empty when the file is unreadable or not valid UTF-8, so
    one wreck cannot abort a whole pass - and NAMED on stderr when that happens. A body that
    silently reads empty is indistinguishable from an artefact with no ACs in it, which is the
    difference between "nothing to prove" and "nothing was proved"."""
    p = Path(path)
    text = sdlc_md.read_text_safe(p)
    if not text and p.is_file() and p.stat().st_size:
        print(f"warning: {p} is unreadable or not valid UTF-8 - read as an empty body",
              file=sys.stderr)
    return text



def shell_allowed_for(text: str, *, allow_shell: bool = True,
                      allow_external: bool = False) -> bool:
    """May a `shell` verifier in THIS artefact's text be executed?

    The technical control behind the documented trust boundary: externally ingested content
    must not reach a shell just because a workflow copied it into an artefact. This is the ONE
    definition - a second caller re-deriving it is how a lane runner came to execute a
    `shell` verifier on an external-provenance story that the authoritative runner refused,
    passing a criterion the project's own verifier failed.
    """
    provenance = (sdlc_md.extract_field(text, "Provenance") or "").strip().lower()
    return allow_shell and (allow_external or provenance != "external")

def verify_story(
    story_path: Path,
    dry_run: bool,
    timeout: int,
    repo_root: Path,
    jest_cache: list[dict] | None = None,
    pytest_cache: dict[str, bool] | None = None,
    pytest_collected: set[str] | None = None,
    allow_shell: bool = True,
    allow_external: bool = False,
    allow_fallback: bool = False,
) -> StoryReport:
    """Run every AC verifier in one story and update its Verified state. With `jest_cache`
    (batch mode) a jest verifier resolves against the cached single run; anything not
    found there falls through to the authoritative per-AC subprocess.

    Shell-backed verifiers are executed only when `allow_shell` is set AND the story is not
    stamped `Provenance: external` (unless `allow_external` overrides) - the technical control
    matching the documented trust boundary, so externally ingested content cannot reach a
    shell just because a workflow copied it into a story."""
    text = _read_body(story_path)
    lines = text.splitlines()
    blocks = parse_story(text)
    report = StoryReport(path=str(story_path), ac_count=len(blocks),
                         ac_fingerprint=ac_fingerprint(text))
    story_allow_shell = shell_allowed_for(text, allow_shell=allow_shell,
                                          allow_external=allow_external)
    pending: list = []  # (block, new_state) - applied bottom-up after the loop

    for block in blocks:
        # Two distinct non-executable cases, counted SEPARATELY - conflating them is how a
        # deleted (rather than declared) verifier reaches a green release gate:
        #   * NO `Verify:` line at all -> UNSPECIFIED. An omission, not a claim. Nothing was
        #     asserted about this AC, so nothing was proved.
        #   * `Verify: manual ...` (or `manually ...`) -> MANUAL. A declared human-checked
        #     judgement call. Never shell it out (shelling prose timed out and reported
        #     "failed" instead - "manual" is honest, "failed" is not).
        if block.verifier is None:
            report.unspecified += 1
            continue
        if _is_manual(block.verifier):
            report.manual += 1
            continue

        result = None
        if jest_cache is not None:
            result = resolve_jest_from_cache(block.verifier, jest_cache)
        if result is None and pytest_cache is not None:
            result = resolve_pytest_from_cache(block.verifier, pytest_cache, pytest_collected)
        if result is None:
            result = run_verifier(block.verifier, timeout, repo_root,
                                  allow_shell=story_allow_shell, allow_fallback=allow_fallback)

        if result.ok:
            report.verified += 1
            report.passed.append(block.ac_id)
            if block.verified_state != "yes":
                report.flips.append({"ac": block.ac_id, "old_state": block.verified_state or "none", "new_state": "yes"})
                report.changed += 1
                if not dry_run:
                    pending.append((block, "yes"))
        else:
            report.failed += 1
            report.failures.append(
                {
                    "ac": block.ac_id,
                    "verifier": block.verifier,
                    "kind": result.kind,
                    "exit_code": result.exit_code,
                    "stderr": result.stderr.strip()[:500],
                    "duration_ms": result.duration_ms,
                    "score": result.score,
                    "vacuous": result.vacuous,
                }
            )
            if result.vacuous:
                report.vacuous += 1
            if block.verified_state == "yes":
                report.stale += 1
                report.flips.append({"ac": block.ac_id, "old_state": "yes", "new_state": "no"})
                report.changed += 1
                if not dry_run:
                    pending.append((block, "no"))

    # Apply write-backs BOTTOM-UP: an insertion shifts every line below it, so
    # applying top-down from one parse compounds a one-line drift per prior
    # insert (the Given/Verified/When misordering in the field). Reverse order
    # leaves every earlier block's cached indices valid.
    for block, state in sorted(pending, key=lambda bs: bs[0].heading_line, reverse=True):
        lines = update_verified(lines, block, state)

    if report.changed and not dry_run:
        new_text = "\n".join(lines)
        if text.endswith("\n"):
            new_text += "\n"
        story_path.write_text(new_text, encoding="utf-8")

    return report


#: The unit types whose acceptance criteria this module EXECUTES. A story and a bug are both
#: DELIVERY units: each is planned, sized, gated by the criteria floor and reaches a terminal
#: status by being built, so a criterion on either has something to gate. A CR or an RFC is a
#: REQUEST - it is decomposed rather than delivered, so an executable check on one would gate
#: nothing, and `file_finding.check_prose_acs` still refuses to write it. The split is the
#: repo's own delivery/discovery vocabulary rather than a list invented here.
VERIFIABLE_PREFIXES = ("US", "BG")

#: Where each verifiable prefix's files live, relative to the workspace.
_UNIT_DIRS = {"US": "stories", "BG": "bugs"}


def unit_dirs(repo_root: Path, stories_dir: Path) -> list[Path]:
    """Every directory holding a verifiable unit, given the `--dir` the caller named.

    `--dir` names the stories directory (its historical meaning, kept so no caller breaks).
    The bugs directory is its sibling, derived rather than configured: a bug that cannot be
    found is a bug whose criteria cannot run, which is the defect this resolves."""
    out = [stories_dir]
    if stories_dir.name == "stories":
        bugs = stories_dir.parent / "bugs"
        if bugs.exists():
            out.append(bugs)
    return out


def walk_units(dirs: Iterable[Path], prefixes: tuple[str, ...] = VERIFIABLE_PREFIXES) -> list[Path]:
    """Every verifiable unit file across `dirs`, sorted within each directory."""
    out: list[Path] = []
    for d in dirs:
        out.extend(walk_stories(d, prefixes))
    return out


def walk_stories(stories_dir: Path,
                 prefixes: tuple[str, ...] = ("US",)) -> Iterable[Path]:
    """Yield every unit file in a directory, sorted, EXCLUDING companion docs. Matches the
    shared `sdlc_md.iter_artifact_files` discipline: a file counts only when its stem resolves
    to a record id with one of `prefixes` and it does not carry a declared companion suffix (a
    `US0001-login-consultations.md` note must not be verified - executing its quoted example
    `Verify:` lines runs arbitrary shell from a non-story document). Case-insensitive.

    `prefixes` defaults to stories alone so every existing caller is unchanged; the callers
    that verify a whole batch pass `VERIFIABLE_PREFIXES` and reach bugs too."""
    if not stories_dir.exists():
        return []
    from lib import conventions
    # stories_dir is normally <root>/sdlc-studio/stories; the config read falls back to the
    # default suffix set if the shape differs, so this is safe either way.
    repo_root = stories_dir.parent.parent if stories_dir.name == "stories" else stories_dir
    suffixes = tuple(f"-{s}" for s in conventions.companion_suffixes(repo_root))
    out = []
    for p in sorted(stories_dir.glob("*.md")):
        if not p.is_file() or p.name == "_index.md":
            continue
        if suffixes and p.stem.endswith(suffixes):
            continue  # a companion/note under a shared id, not the story itself
        rec = sdlc_md.extract_record_id(p.stem) or ""
        if sdlc_md.norm_id(rec).startswith(tuple(prefixes)):
            out.append(p)
    return out


def write_report(path: Path, stories: list[StoryReport], dry_run: bool = False,
                 merge: bool = True) -> None:
    """Write the per-story verification summary to JSON.

    by default this MERGES the run's stories into any existing report (this run's
    entries win, others are preserved), so verifying a sprint one story at a time accumulates
    and the Done-gate finds every verified story. `merge=False` rebuilds the report from this
    run only (the `--fresh` path). In dry-run the snapshot enumerates the pending `flips`
    (ac, old_state, new_state) so the preview's most actionable output is recoverable.
    """
    stamp = sdlc_md.now_iso8601()
    new_stories = {
        os.path.basename(s.path).replace(".md", ""): {
            "ac_count": s.ac_count,
            "verified": s.verified,
            "failed": s.failed,
            "stale": s.stale,
            "manual": s.manual,
            "unspecified": s.unspecified,
            "passed": s.passed,
            "failures": s.failures,
            "flips": s.flips,
            # when THIS story was verified, so the Done gate can tell a fresh green from a
            # stale one carried forward by the merge.
            "verified_at": stamp,
            # what was verified: a hash of the ACs and their verifiers. The Done gate
            # prefers this over mtime, so metadata-only edits do not invalidate a green.
            "ac_fingerprint": s.ac_fingerprint,
        }
        for s in stories
    }
    merged = new_stories
    if merge and path.exists():
        try:
            prior = json.loads(path.read_text(  # bare-read-ok: not an artefact body; the
                    # enclosing except already catches UnicodeDecodeError via ValueError
                    encoding="utf-8")).get("stories", {})
            if isinstance(prior, dict):
                merged = {**prior, **new_stories}  # this run's entries take precedence
        except (ValueError, OSError):
            pass
    data = {
        "generated_at": sdlc_md.now_iso8601(),
        "dry_run": dry_run,
        "stories": merged,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def append_history(path: Path, stories: list[StoryReport], dry_run: bool) -> None:
    """Append one JSONL line per story per run, so the gate has an audit trail.

    Answers "when did AC-3 last pass / regress" that a single overwriting
    snapshot cannot. Append-only.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    at = sdlc_md.now_iso8601()
    with path.open("a", encoding="utf-8") as fh:
        for s in stories:
            fh.write(json.dumps({
                "at": at,
                "dry_run": dry_run,
                "story": os.path.basename(s.path).replace(".md", ""),
                "verified": s.verified,
                "failed": s.failed,
                "stale": s.stale,
                "passed": s.passed,
                "failed_acs": [f["ac"] for f in s.failures],
                "exit": 1 if s.failed else 0,
            }) + "\n")
    sdlc_md.roll_jsonl(path)  # bound the append-only history so it cannot grow without limit


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


# The project-root resolver lives in `lib.sdlc_md` - ONE implementation the whole family shares.
# These names stay here because `repo_map.py`, `lessons.py` and `loop_guard.py` already import
# them from this module; they are aliases to the shared functions, never a second copy. A copy
# would drift, and a drifted resolver is how a writer and its reader stop agreeing where a file
# lives - the defect this resolver exists to prevent.
under_root = sdlc_md.under_root
discover_root = sdlc_md.discover_root
resolve_root = sdlc_md.resolve_root
_ROOT_MARKERS = sdlc_md.ROOT_MARKERS


def worklist_ids(path: Path | str) -> list[str]:
    """The artifact ids a worklist/tranche file names, in file order, de-duplicated.

    Deliberately the SAME tolerances as the sprint planner's tranche reader - markdown
    bullets are stripped, a `#` comment or heading line is skipped, a repeated id is one
    member - so one file can drive both and neither reads a batch the other cannot.
    """
    out: list[str] = []
    # An unreadable worklist RAISES rather than degrading to an empty batch: the caller named
    # this file, and reading it as empty would silently narrow the batch it approved.
    text = Path(path).read_text(encoding="utf-8")  # bare-read-ok: an operator-named batch
    # source, not an artefact body - a silent empty read would narrow the approved batch
    for line in text.splitlines():
        line = line.strip().lstrip("-*").strip()
        if not line or line.startswith("#"):
            continue
        m = sdlc_md.ID_SEARCH_RE.search(line)
        if m:
            out.append(sdlc_md.norm_id(m.group(0)))
    return list(dict.fromkeys(out))


def scope_flag(args: argparse.Namespace) -> str:
    """The batch-scope flag the caller passed, or "" for a whole-workspace run.

    `--story`/`--id` are NOT scopes in this sense: they name one story and predate the
    batch forms, which is why they are excluded here and left exactly as they were.
    """
    if getattr(args, "ids", None):
        return "--ids"
    if getattr(args, "worklist", None):
        return "--worklist"
    if getattr(args, "from_run", False):
        return "--from-run"
    return ""


def _scope_ids(args: argparse.Namespace, repo_root: Path) -> tuple[list[str], str | None]:
    """(normalised ids the scope names, refusal). The refusal is a message, not an
    exception, so the caller returns exit 2 having written nothing."""
    flag = scope_flag(args)
    if flag == "--ids":
        wanted: list[str] = []
        for chunk in args.ids:
            wanted += [tok for tok in re.split(r"[,\s]+", chunk) if tok]
        return list(dict.fromkeys(sdlc_md.norm_id(w) for w in wanted)), None
    if flag == "--worklist":
        p = under_root(repo_root, args.worklist)
        if not p.is_file():
            return [], f"no worklist file at {p}"
        return worklist_ids(p), None
    if not run_state.is_open(repo_root):
        return [], ("no run is open, so --from-run has no approved batch to scope to. Open "
                    "one (`sprint plan --write`), or name the batch with --ids/--worklist")
    return list(dict.fromkeys(
        sdlc_md.norm_id(b) for b in (run_state.read(repo_root).get("batch") or []))), None


def _scoped_paths(args: argparse.Namespace, repo_root: Path) -> tuple[list[Path], str | None]:
    """Resolve a scope to story files under `--dir`, or a refusal message.

    An id resolving to nothing REFUSES: a silent skip is read by the completion gate as
    "that unit had nothing to fail". A batch source that legitimately carries non-delivery
    ids (`--worklist`, `--from-run` carry CRs and RFCs) has those dropped and SAID so; ids
    typed by hand into `--ids` are taken literally.

    Stories AND bugs resolve. A lane's return rule - verify your unit before returning - was
    unrunnable for every bug in a batch while this walked stories alone, so a bug lane could
    only return BLOCKED or claim a verification it had not performed.
    """
    flag = scope_flag(args)
    ids, refusal = _scope_ids(args, repo_root)
    if refusal:
        return [], refusal
    if flag != "--ids":
        units = [i for i in ids if i.startswith(VERIFIABLE_PREFIXES)]
        skipped = len(ids) - len(units)
        if skipped:
            print(f"{flag}: {skipped} non-delivery id(s) skipped - `run` verifies "
                  f"{'/'.join(VERIFIABLE_PREFIXES)}", file=sys.stderr)
        ids = units
    by_id: dict[str, Path] = {}
    for p in walk_units(unit_dirs(repo_root, under_root(repo_root, args.dir))):
        by_id.setdefault(sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or ""), p)
    missing = [i for i in ids if i not in by_id]
    if missing:
        return [], (f"{flag} names {len(missing)} id(s) with no unit file under "
                    f"{args.dir} or its sibling bugs/: {', '.join(missing)}")
    if not ids:
        return [], (f"{flag} resolved to no units - refusing to fall back to a "
                    f"whole-workspace run, which is the cost a scope exists to avoid")
    return [by_id[i] for i in ids], None


def cmd_run(args: argparse.Namespace) -> int:
    """Run verifiers across stories, update files, and write the report."""
    repo_root = resolve_root(args)

    flag = scope_flag(args)
    # `--story` / `--id` narrow the run exactly as the newer scopes do, so they carry exactly the
    # same hazard: a rebuild from a narrowed set deletes every verdict outside it. Excluding them
    # left the data loss this refusal exists to prevent one flag away - measured: a whole-workspace
    # report holding four stories, then `run --id US0001 --fresh`, exit 0, three verdicts gone
    # including a FAILING one, so the completion gate saw no failure record.
    narrowing = flag or ("--id" if getattr(args, "id", None)
                         else "--story" if getattr(args, "story", None) else "")
    if narrowing and getattr(args, "fresh", False):
        flag = narrowing
        # A rebuild keeps only THIS run's entries. Scoped, that silently deletes every
        # verdict outside the scope - including the freshness fields the completion gate
        # reads - and the loss is invisible until a gate reports a green story unverified.
        # Refused before any work, so the report on disk is byte-identical afterwards.
        print(f"error: --fresh with {flag} would rebuild the report from the scope alone, "
              f"discarding every verdict outside it. Drop the scope to rebuild the whole "
              f"report, or drop --fresh so the scoped run merges into it.", file=sys.stderr)
        return 2

    if flag:
        paths, refusal = _scoped_paths(args, repo_root)
        if refusal:
            print(f"error: {refusal}", file=sys.stderr)
            return 2
    elif args.story:
        paths = [Path(args.story)]
        if not paths[0].exists():
            # The natural first invocation passes a story ID here (the flag is named
            # --story, its sibling commands take --id): an id-shaped value that is not
            # a real path resolves as an id before erroring. A value that is neither
            # is an ERROR (exit 2) naming BOTH failed lookups, never a silent skip -
            # a typo'd --story read as "all ACs green" to a gate.
            rec = sdlc_md.extract_record_id(args.story)
            if rec and args.story == rec:
                target = sdlc_md.norm_id(rec)
                matches = [p for p in walk_stories(under_root(repo_root, args.dir))
                           if sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or "") == target]
                if matches:
                    paths = matches[:1]
                else:
                    print(f"no story file at {args.story}, and no story with that id "
                          f"under {args.dir}", file=sys.stderr)
                    return 2
            else:
                print(f"no story file at {args.story}", file=sys.stderr)
                return 2
    elif getattr(args, "id", None):  # resolve --id US/BGNNNN under --dir (case-insensitive)
        target = sdlc_md.norm_id(args.id)
        matches = [p for p in walk_units(unit_dirs(repo_root, under_root(repo_root, args.dir)))
                   if sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or "") == target]
        if not matches:
            print(f"no unit file for id {args.id} under {args.dir} or its sibling bugs/",
                  file=sys.stderr)
            return 2
        paths = matches[:1]
    else:
        paths = list(walk_stories(under_root(repo_root, args.dir)))

    if not paths:
        print("no stories found", file=sys.stderr)
        return 2

    # with --batch, run jest once and resolve jest verifiers from the cached assertions
    # instead of a cold `jest -t` start per AC (a field sprint measured ~48 cold starts / 70s).
    batch_on = getattr(args, "batch", False)
    jest_cache = jest_batch_cache(repo_root, args.timeout) if batch_on else None
    pytest_cache = (pytest_batch_cache(repo_root, args.timeout, pytest_verifier_files(paths))
                    if batch_on else None)
    pytest_collected = pytest_batch_collected(pytest_cache) if pytest_cache else None
    if pytest_cache is not None:
        print(f"batch: cached {len(pytest_cache)} pytest node(s) from one run", file=sys.stderr)
    if getattr(args, "batch", False):
        print(f"batch: cached {len(jest_cache)} jest assertion(s) from one run", file=sys.stderr)

    reports: list[StoryReport] = []
    overall_fail = 0
    overall_pass = 0
    for p in paths:
        if not p.exists():
            print(f"skip: {p} not found", file=sys.stderr)
            continue
        report = verify_story(
            p, args.dry_run, args.timeout, repo_root, jest_cache=jest_cache,
            pytest_cache=pytest_cache, pytest_collected=pytest_collected,
            allow_shell=not getattr(args, "no_shell", False),
            allow_external=getattr(args, "allow_external", False),
            allow_fallback=getattr(args, "allow_shell_fallback", False),
        )
        reports.append(report)
        overall_fail += report.failed
        overall_pass += report.verified
        tag = "DRY" if args.dry_run else "APL"
        print(
            f"[{tag}] {p.name}: "
            f"ac={report.ac_count} pass={report.verified} "
            f"fail={report.failed} manual={report.manual} "
            f"unspecified={report.unspecified} "
            f"changes={report.changed}"
        )
        for fail in report.failures:
            print(f"        FAIL {fail['ac']}: {fail['verifier']}")
            if fail["stderr"]:
                stderr_lines = fail["stderr"].splitlines()
                for line in stderr_lines[:3]:
                    print(f"          | {line}")

    # Write the report in dry-run too (to a distinct path, so the live report is
    # not clobbered) and append the run to the history log.
    report_path = under_root(repo_root, args.report)
    if args.dry_run:
        report_path = report_path.with_name(report_path.stem + ".dry-run" + report_path.suffix)
    write_report(report_path, reports, dry_run=args.dry_run, merge=not getattr(args, "fresh", False))
    append_history(repo_root / "sdlc-studio" / ".local" / "verify-history.jsonl", reports, args.dry_run)
    print(f"wrote {report_path}")

    # A UNIT THIS COMMAND COULD NOT READ IS NOT A UNIT THAT PASSED. Three states are refused,
    # and they are refused separately because they have different fixes:
    #   * a criteria section that parses to NOTHING - the writer and this parser disagree about
    #     a claim somebody did make. 75 bug files are in this state today.
    #   * criteria that parse but carry NO verifier at all - `ac=N pass=0 unspecified=N`, which
    #     is 36 files today and is where widening the parser MOVES the unreadable ones. Without
    #     this arm the fix converts a would-be refusal into a silent exit 0 while the count
    #     improves: the defect reproduced in a different costume. Named by a seat at plan review.
    #   * no criteria section at all - REPORTED, not refused. 232 files, most of them filed
    #     findings that never claimed a verifier, and nothing else in the tree refuses them.
    # Before this, every one of them printed a line byte-comparable to a clean pass and exited 0.
    # Which units carried a SECTION is read from the files, because the report does not carry
    # it - and the distinction is the whole of AC2. A unit with no section never claimed a
    # verifier; one whose section parses to nothing made a claim this parser cannot read.
    had_section = {str(q) for q in paths
                   if "## Acceptance Criteria" in sdlc_md.read_text_safe(q)}
    unreadable = [r for r in reports if r.ac_count == 0 and str(r.path) in had_section]
    vacuous = [r for r in reports
               if r.ac_count and not (r.verified or r.failed or r.manual)]
    for r in unreadable:
        print(f"REFUSED {Path(r.path).name}: it carries a `## Acceptance Criteria` section and this command "
              f"parsed NO criteria from it, so it executed nothing. Accepted shapes are a "
              f"`### ACn: title` heading or a `- [ ] **ACn** ...` bullet, each with a "
              f"`- **Verify:** <command>` line in bold.", file=sys.stderr)
    for r in vacuous:
        print(f"REFUSED {Path(r.path).name}: {r.ac_count} criterion/criteria parsed and NONE carries a "
              f"`Verify:` line, so nothing was executed. An omitted verifier is not a passed "
              f"one - declare `- **Verify:** manual <what a human checks>` if that is the "
              f"truth.", file=sys.stderr)
    if unreadable or vacuous:
        return 2

    return 1 if overall_fail > 0 else 0


def corpus_scan(repo_root, kind: str = "bugs") -> dict:
    """The three blind states across a whole artefact class, counted by SHIPPED code.

    Ships rather than living in a throwaway script, so the before and after figures of any fix
    are produced by the same routine. Kept as three counts rather than one total: they are
    different defects with different fixes, and a single number hides the vacuous state inside
    an improving trend.
    """
    root = Path(repo_root) / "sdlc-studio" / kind
    out = {"files": 0, "no_section": 0, "unreadable": 0, "no_verifier": 0, "ok": 0}
    for f in sorted(root.glob("*.md")):
        if f.name.startswith("_"):
            continue
        out["files"] += 1
        text = sdlc_md.read_text_safe(f)
        if "## Acceptance Criteria" not in text:
            out["no_section"] += 1
            continue
        blocks = parse_story(text)
        if not blocks:
            out["unreadable"] += 1
        elif not any(b.verifier for b in blocks):
            out["no_verifier"] += 1
        else:
            out["ok"] += 1
    return out


def cmd_corpus_scan(args: argparse.Namespace) -> int:
    res = corpus_scan(resolve_root(args), args.kind)
    print(f"corpus scan ({args.kind}): {res['files']} file(s) - {res['ok']} readable and "
          f"verifier-bearing, {res['unreadable']} with a section this parser cannot read, "
          f"{res['no_verifier']} parsed but carrying no verifier, {res['no_section']} with no "
          f"criteria section at all")
    return 0


_PASS_TOKENS = {"pass", "passing", "passed", "done", "verified", "covered", "green"}

# The section heading, used only to tell a BROKEN matrix from an unwritten one. The table
# itself is found structurally (`_matrix_header`), never by this - a matrix under a differently
# worded heading still counts.
_MATRIX_HEADING_RE = re.compile(r"(?im)^\s{0,3}#{1,6}\s*AC Coverage Matrix\b")


def _row_story_id(cell: str) -> str:
    """The normalised story id in a matrix Story cell (bare `US0001` or a `[US0001](..)`
    link), or "" if none - the matching key for the story-qualified cross-check."""
    m = re.search(r"[A-Za-z]{1,5}-?\d+", cell or "")
    return sdlc_md.norm_id(m.group(0)) if m else ""


def _report_failed_acs(report_path: Path | str) -> set[str]:
    """ACs the latest verify-report marks failing, keyed `STORYID::AC` (both upper-cased),
    for the matrix cross-check. Story-qualifying the key stops one story's failing AC1 from
    flagging every other story's AC1 in a merged report. Missing/unreadable report
    -> empty set (cross-check is then skipped)."""
    p = Path(report_path)
    if not p.exists():
        return set()
    try:
        data = json.loads(p.read_text(  # bare-read-ok: not an artefact body; the enclosing
                # except already catches UnicodeDecodeError via ValueError
                encoding="utf-8"))
    except (ValueError, OSError):
        return set()
    failed = set()
    stories = data.get("stories", {})
    # dict: keyed by story stem; list: each entry carries its own `path`.
    items = (stories.items() if isinstance(stories, dict)
             else [(st.get("path", ""), st) for st in stories])
    for key, st in items:
        stem = Path(str(key)).stem if key else ""
        sid = sdlc_md.norm_id(sdlc_md.extract_record_id(stem) or stem) if stem else ""
        for f in st.get("failures", []):  # each failure carries the failing AC id
            ac = str(f.get("ac", "")).upper()
            failed.add(f"{sid}::{ac}" if sid else ac)
    return failed


def ts_check(spec_path: Path | str, verify_report: Path | str | None = None) -> list[dict]:
    """Validate a test-spec's AC Coverage Matrix is not decorative: every AC row
    must map a Test Case and carry a passing Status, and no placeholders may remain. The
    matrix authored before code is what makes the AC and its test converge by construction.
    When `verify_report` is given, also cross-check: an AC the matrix calls passing but the
    verify-report marks failing is flagged (the matrix cannot claim green over a red runner).
    Returns a list of {ac, issue} findings (empty = the matrix is complete and honest).

    A spec with NO matrix is a finding, not a clean result. Zero rows and zero findings was
    the same output a fully mapped matrix produces, so a spec asserting no coverage was
    indistinguishable from one asserting complete coverage. Absence is read as NOT YET
    WRITTEN: of the three things it could mean - unwritten, malformed, or deliberately not
    applicable - only the last is clean, and a deliberate exemption is a decision somebody
    made, which nothing that is simply absent can evidence. A matrix table present but
    holding no AC rows is the same nothing and reports the same way, or the finding could be
    silenced with two lines that assert nothing.

    A spec that could not be read is a refusal, never a clean matrix - the two ways of
    failing to read one are kept apart because their callers differ:
      * ABSENT (no such file, or a directory) -> FileNotFoundError. A path that is not
        there is a broken invocation, and every caller must see that rather than [].
      * PRESENT but not valid UTF-8 -> a returned finding naming the file. A scanner
        walking a whole tree has to survive one wreck, so this one does not raise; it
        still makes the result non-empty, so nothing reads it as a passing matrix.
    """
    p = Path(spec_path)
    if not p.is_file():
        raise FileNotFoundError(f"no test-spec file at {p}")
    text = _read_body(p)
    if not text and p.stat().st_size:
        return [{"ac": "-", "issue": f"spec is unreadable or not valid UTF-8: {p}"}]
    failed_in_report = _report_failed_acs(verify_report) if verify_report else set()
    issues: list[dict] = []
    matrices = 0   # matrix TABLES found
    acs = 0        # AC rows read out of them
    def _matrix_header(cells: list) -> bool:
        low = [c.strip().lower() for c in cells]
        return "ac" in low and ("test cases" in low or "test case" in low)
    for tbl in sdlc_md.iter_tables(text, header_predicate=_matrix_header):
        if tbl["header"] is None or not _matrix_header(tbl["header"]):
            continue  # only the AC Coverage Matrix table(s); later tables never bleed in
        matrices += 1
        low = [c.strip().lower() for c in tbl["header"]]
        cols = {n: low.index(n) for n in ("ac", "test cases", "test case", "status") if n in low}
        story_col = low.index("story") if "story" in low else None
        for _ln, cells in tbl["rows"]:
            ac = cells[cols["ac"]].strip() if cols["ac"] < len(cells) else ""
            if not ac or ac.lower() == "ac":
                continue
            acs += 1
            if "{{" in "|".join(cells):
                issues.append({"ac": ac, "issue": "unfilled placeholder in the matrix row"})
                continue
            tc_col = cols.get("test cases", cols.get("test case"))
            tc = cells[tc_col].strip() if tc_col is not None and tc_col < len(cells) else ""
            st = cells[cols["status"]].strip() if "status" in cols and cols["status"] < len(cells) else ""
            # Story-qualify the cross-check key so a merged report matches THIS row's story,
            # not any story that happens to share the AC id.
            sid = _row_story_id(cells[story_col]) if story_col is not None and story_col < len(cells) else ""
            key = f"{sid}::{ac.upper()}" if sid else ac.upper()
            if not tc or tc in {"--", "-", "tbd", "TBD"}:
                issues.append({"ac": ac, "issue": "no test case mapped"})
            elif st.lower() not in _PASS_TOKENS:
                issues.append({"ac": ac, "issue": f"status {st!r} is not passing"})
            elif key in failed_in_report:
                issues.append({"ac": ac, "issue": "matrix says passing but the verify-report marks it failing"})
    if not matrices:
        issues.append({"ac": "-", "issue": _no_matrix_issue(text)})
    elif not acs:
        issues.append({"ac": "-", "issue": "the AC Coverage Matrix has no AC rows - a header "
                                           "with nothing under it maps no AC to any test"})
    return issues


def _no_matrix_issue(text: str) -> str:
    """Why the spec has no matrix, in the terms of the repair it needs.

    A heading with nothing parseable under it is a BROKEN section (wrong columns, or prose
    where the table should be); no heading at all is one nobody has written yet. Both are
    findings and neither is clean, but telling them apart is the difference between "fix the
    columns" and "write the matrix", and the reader cannot see which from the file.
    """
    if _MATRIX_HEADING_RE.search(text):
        return ("an AC Coverage Matrix heading with no matrix table under it - the table "
                "needs an `AC` column and a `Test Cases` column")
    return ("no AC Coverage Matrix section - the spec never says which test case covers "
            "which AC, so it asserts no coverage at all")


def epic_stories(repo_root: Path | str, epic_id: str) -> list[Path]:
    """Story files whose `Epic:` field links to `epic_id`, sorted by id. The same epic
    membership rule `epic_test_spec_check` uses for test-specs, applied to stories - so the
    matrix scaffold covers exactly the stories that belong to the epic, no more, no less."""
    root = Path(repo_root)
    eid = sdlc_md.norm_id(epic_id)
    out: list[Path] = []
    for p in sdlc_md.artifact_files("story", root):
        ef = sdlc_md.extract_field(sdlc_md.read_text_safe(p), "Epic") or ""
        m = sdlc_md.ID_SEARCH_RE.search(ef)
        if m and sdlc_md.norm_id(m.group(0)) == eid:
            out.append(p)
    return out


def scaffold_ac_matrix(repo_root: Path | str, epic_id: str) -> str:
    """Render an AC Coverage Matrix pre-filled with one row per AC across the epic's stories.

    Every AC in every story of the epic becomes exactly one row (Story, AC id, Description),
    with Test Cases and Status left blank for the model to map - determinism in the script,
    judgement in the model. The header matches the canonical matrix
    (`reference-test-spec.md`) so `ts-check` validates it unchanged once the model fills the
    two blank columns. This removes the manual AC hand-extraction the design rung otherwise
    requires (the missed-AC coverage gap the matrix exists to prevent).
    """
    header = ["Story", "AC", "Description", "Test Cases", "Status"]
    rows = [sdlc_md.join_row(header),
            sdlc_md.join_row(["---"] * len(header))]
    for story in epic_stories(repo_root, epic_id):
        story_id = sdlc_md.extract_record_id(story.stem) or story.stem
        for block in parse_story(sdlc_md.read_text_safe(story)):
            rows.append(sdlc_md.join_row([story_id, block.ac_id, block.title, "", ""]))
    return "### AC Coverage Matrix\n\n" + "\n".join(rows) + "\n"


#: Where the lane's measured yield accumulates, under `.local/` like every other hook-written
#: record. An earlier accumulator in this project wrote to a TRACKED path and dirtied the tree
#: on every commit with a file the author never touched; this follows the fix for that.
_LANE_YIELD_REL = "sdlc-studio/.local/lane-check-yield.json"


# ---------------------------------------------------------------------------
# TEST PLAN DERIVATION (US0629). The plan names, per criterion, the production change the
# test must fail on - and it is DERIVED rather than hand-assembled, because a hand-assembled
# plan is exactly where a criterion goes missing.
# ---------------------------------------------------------------------------

#: Overlap above which a mutant field is judged a restatement of its own criterion rather than a
#: change to production code. A STATED number with a stated basis: the discriminating pair on
#: US0629 AC2 measures 71% for a restatement and 24% for a legitimate mutant naming the same file
#: and the same verb, so the two differ in this property alone and the threshold is what is under
#: test rather than the examples. Measured on SUBSTANCE, after filler and punctuation come off,
#: following `_reason_substance` and its scar - a one-character `-` once passed a non-blank check.
TESTPLAN_OVERLAP_CEILING = 0.60

#: Verbs that denote a change to code. A mutant must carry one: "the feature does not work" is a
#: prediction about behaviour, not an edit somebody can make.
#: Verbs that name a production EDIT. An enumeration is a lower bound, never a boundary (LL0043),
#: and this one was both too narrow and skewed: it listed only SUBTRACTIVE edits, so a mutant that
#: ADDS or MOVES something could not be stated at all. Authoring the first real
#: test plans hit it five times on legitimate mutants - `move the affects check below the batch
#: write`, `print the bare message` - and again during the v5.0.1 release, where the mutant was
#: reworded to satisfy the list rather than the list corrected. A check that trains authors to
#: write for the checker rather than for the reader is worse than no check.
#:
#: Additive, positional and substitutive verbs are now all first-class. Kept as a list rather
#: than replaced by a part-of-speech test because the point is to refuse a mutant phrased as an
#: OUTCOME ("the suite goes red") rather than as an edit, and any verb at all distinguishes those.
_EDIT_VERBS = (
    # subtractive
    "delete", "remove", "drop", "omit", "truncate", "collapse", "strip", "clear", "unset",
    # substitutive
    "replace", "swap", "invert", "negate", "hard-code", "hardcode", "stub", "change", "set",
    "make it", "flip", "revert", "rename", "return", "reassign", "overwrite", "shadow",
    # additive - none of these existed, which is the defect
    "add", "insert", "append", "prepend", "introduce", "duplicate", "extend", "wrap", "emit",
    "print", "raise", "throw", "call", "register",
    # positional / ordering - a mutant that MOVES code changes behaviour without adding a token
    "move", "reorder", "hoist", "lower", "inline", "extract", "split", "merge", "reverse",
    # weakening
    "widen", "narrow", "loosen", "weaken", "disable", "bypass", "short-circuit", "skip",
    "comment out", "suppress", "ignore", "relax",
)

_TESTPLAN_HEADING = "## Test Plan"
_TESTPLAN_PLACEHOLDER = "{{name the production change this test must fail on}}"


def _substance_tokens(text: str) -> set:
    """The meaning-bearing tokens of a phrase, lowercased, filler and punctuation removed."""
    words = re.findall(r"[0-9a-z_]+", (text or "").lower())
    return {w for w in words if len(w) > 2 and w not in _TESTPLAN_STOPWORDS}


_TESTPLAN_STOPWORDS = {
    "the", "and", "that", "this", "with", "for", "from", "its", "it", "is", "are", "was", "were",
    "not", "but", "than", "then", "when", "given", "which", "who", "whom", "what", "into", "onto",
    "have", "has", "had", "will", "would", "can", "could", "should", "must", "may", "one", "all",
    "any", "each", "every", "because", "rather", "there", "their", "they", "them", "does", "did",
}


def _then_clause(lines: list, start: int, end: int) -> str:
    """The criterion's own `Then` clause - what it asserts, as opposed to how it is set up.

    Read from the source LINES between this criterion's heading and the next, because `ACBlock`
    carries no body: it holds the heading, the verifier and the stamp, and nothing of the prose.
    The first version of this helper read `block.body`, which does not exist, so it returned an
    empty string, every overlap measured 0% and the restatement limb accepted everything. The
    library test could not see it - it passes the `Then` clause in directly - and only the test
    that drives `verify_ac.py testplan derive` caught it. LL0040, in the guard written to enforce
    a criterion about guards that do not guard.
    """
    for line in lines[start:end]:
        # Strip ONE leading bullet marker, not every leading `-`/`*` character.
        # `lstrip("-*")` ate the bold markers off a NON-bulleted `**Then** ...` line, leaving
        # `Then** ...`, which matched nothing - so the clause fell through to the whole-block
        # fallback below. That block carries the criterion's own `- **Mutant:**` bullet, so the
        # mutant was measured for overlap against text CONTAINING the mutant, every honest plan
        # row read as a restatement of itself, and `testplan derive` refused it.
        stripped = re.sub(r"^\s*[-*]\s+", "", line).strip()
        if stripped.lower().startswith("**then**"):
            return stripped[len("**then**"):].strip()
    return " ".join(lines[start:end])


def _criteria_section_end(lines: list, blocks: list) -> int:
    """Where the LAST criterion stops - the next top-level heading, never the end of the file.

    The bound was `len(lines)`, so the final criterion's `Then` clause ran to the bottom of the
    artefact and swallowed everything after it: the Resolution prose, the Revision History, and -
    fatally - the `## Test Plan` table itself, which holds every mutant's own text. Its mutant was
    therefore measured for overlap against a passage CONTAINING that mutant, scored 1.0, and
    `testplan derive` refused the row as a restatement of itself. Deterministic and invisible: it
    struck only the last row, only once a plan already existed, so the first derive of a unit
    passed and every re-derive of it failed.

    That is the second time this exact shape has been paid for here - `_then_clause`'s own
    docstring records the first, where a mis-stripped bullet marker fell through to a block that
    carried the mutant. Both are one fault: a range wide enough to include the answer.

    Falls back to the end of the file when no heading follows, which is the honest reading of an
    artefact whose criteria genuinely run to the bottom.
    """
    start = blocks[-1].heading_line if blocks else 0
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            return i
    return len(lines)


def _overlap_ratio(mutant: str, then_clause: str, affects: list | None = None) -> float:
    """Fraction of the mutant's substance tokens that its criterion's `Then` clause already
    carries. 1.0 is a verbatim restatement; a legitimate mutant names an edit the criterion does
    not.

    THE PATH IS EXCLUDED from the measurement, and that is not a detail. Naming a file drawn from
    the unit's `Affects` is separately REQUIRED by another limb, so counting those tokens as novel
    substance lets a restatement buy headroom under the ceiling with the very words it was already
    obliged to write. Measured with the path included, US0629 AC2's discriminating pair reads 57%
    and 33% - the restatement passes - and the threshold stops being the thing under test, which
    is exactly what the criterion says it must remain. Excluded, the same pair reads 67% and 40%
    about the stated 60% ceiling.
    """
    m = _substance_tokens(mutant) - _path_tokens(affects or [])
    if not m:
        # A ratio over NOTHING is not a restatement. This returned 1.0, so a mutant made only of
        # path tokens - `verify_ac.py` and nothing else - was reported as restating a `Then`
        # clause it shares not one word with. The refusal was right and its stated reason was
        # false, which is worse than a wrong verdict: an author fixing the restatement it names
        # is fixing something that is not there. The real fault, that it carries no edit verb, is
        # reported by its own limb, and a guard that refuses for the wrong reason passes a
        # bare-refusal assertion - the constraint this module's own tests are written under.
        return 0.0
    return len(m & _substance_tokens(then_clause)) / len(m)


def _path_tokens(affects: list) -> set:
    """Substance tokens contributed by the unit's declared paths, which carry no argument."""
    out = set()
    for a in affects or []:
        # `/` and `.` split; `_` does NOT - `_substance_tokens` keeps `verify_ac` whole, so
        # splitting it here would produce `verify` and `ac` and match nothing the mutant wrote.
        out |= _substance_tokens(str(a).replace("/", " ").replace(".", " "))
    return out


def testplan_row_faults(mutant: str, then_clause: str, affects: list) -> list:
    """Which of the four properties this mutant field fails, named. Empty means it is a mutant.

    Named rather than counted: a guard that refuses for the wrong reason passes a bare-refusal
    assertion, so each limb has to be distinguishable in the message it produces.
    """
    faults = []
    text = (mutant or "").strip()
    if not text or text == _TESTPLAN_PLACEHOLDER or not _substance_tokens(text):
        return ["blank - a mutant is a change to production code, and no change is named"]
    lowered = text.lower()
    # MEMBERSHIP of the unit's own Affects, never path SHAPE: the mutant that defeated the
    # original wording named a real file, so a rule checking shape still accepts it.
    names = {Path(a).name.lower() for a in affects if a} | {str(a).strip().lower() for a in affects if a}
    if not any(n and n in lowered for n in names):
        faults.append(f"names no path from this unit's Affects ({', '.join(sorted(Path(a).name for a in affects)) or 'none declared'})")
    if not any(v in lowered for v in _EDIT_VERBS):
        faults.append("carries no edit verb - name what is changed, not what stops working")
    ratio = _overlap_ratio(text, then_clause, affects)
    # `>=`, not `>`: the ceiling is the first REFUSED value, so a mutant sitting exactly on it
    # is a restatement. A seat showed 0.60 is reachable (5 substance tokens, 3 shared) and that
    # `>` accepted it - an off-by-one on the one criterion whose whole point is the threshold.
    if ratio >= TESTPLAN_OVERLAP_CEILING:
        faults.append(f"restates its own criterion - {ratio:.0%} of its substance is the `Then` "
                      f"clause, over the {TESTPLAN_OVERLAP_CEILING:.0%} ceiling")
    return faults


def _testplan_rows(text: str) -> list:
    """Existing plan rows IN FILE ORDER, one entry per row, so authored mutants survive a
    re-derive even when a criterion carries several.

    Returns `[{"ac", "mutant", "row"}]`, `row` being the 0-based position of that mutant among
    the rows on its own criterion. It used to return `{ac: mutant}`, which silently kept the LAST
    row on each criterion: a plan declaring two mutants for one AC came back with one, and the
    author's first was destroyed at exit 0. The same key made `--from-plan` report a
    planned count equal to the number of distinct criteria rather than of declared rows, and print
    `every one executed and killed` over mutants it had never joined.

    A criterion that can be wrong in several distinct ways is exactly the one worth pinning
    several times, so the collapse fell hardest where the evidence mattered most.
    """
    rows, seen, in_plan = [], {}, False
    for line in text.splitlines():
        if line.startswith("## "):
            in_plan = line.strip() == _TESTPLAN_HEADING
            continue
        if not in_plan or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and re.fullmatch(r"AC\d+", cells[0] or ""):
            ac = cells[0]
            rows.append({"ac": ac, "mutant": cells[1], "row": seen.get(ac, 0)})
            seen[ac] = seen.get(ac, 0) + 1
    return rows


def testplan_rows_by_criterion(text: str) -> dict:
    """The plan grouped as `{ac: [mutant, ...]}`, order preserved within each criterion.

    The shape every caller that thinks in criteria wants, derived from the row list rather than
    parsed a second time - two parsers of one artefact are how the row count and the criterion
    count came to disagree in the first place.
    """
    out: dict = {}
    for r in _testplan_rows(text):
        out.setdefault(r["ac"], []).append(r["mutant"])
    return out


#: A criterion whose falsifying change nobody can name. A legitimate state - some criteria really
#: are not mechanically falsifiable - but it must COST something to enter, or it becomes the state
#: every awkward criterion ends up in. So it carries its reason, and a batch holding one is not
#: plannable until somebody decides.
UNNAMEABLE = "unnameable"


def testplan_unnameable(text: str) -> list:
    """Rows marked `unnameable`, each with its reason and whether it is malformed.

    A bare `unnameable` is MALFORMED rather than a declared exemption. The distinction is the
    whole control: a state that costs nothing to enter is free, and free is what every criterion
    with an awkward mutant will choose. Written as `unnameable: <why nobody can name one>`.
    """
    out, in_plan = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            in_plan = line.strip() == _TESTPLAN_HEADING
            continue
        if not in_plan or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not re.fullmatch(r"AC\d+", cells[0] or ""):
            continue
        cell = cells[1]
        if not cell.lower().startswith(UNNAMEABLE):
            continue
        reason = cell[len(UNNAMEABLE):].lstrip(" :-").strip()
        out.append({"ac": cells[0], "reason": reason,
                    "malformed": len(_reason_substance(reason)) < 12})
    return out


def testplan_derive(repo_root, unit: str, *, write: bool = True) -> dict:
    """Derive `unit`'s test plan: one row per criterion, each naming the production change its
    test must fail on.

    THE COUNT IS CHECKED BY TWO INDEPENDENT READERS, and that is part of the criterion rather
    than a detail of the implementation. `parse_story` reads the whole file for `### ACn` and
    `- **ACn**`, fence-aware; `sdlc_md.count_acs` reads only inside `## Acceptance Criteria`,
    also counts bare `- [ ]` items, and is not fence-aware. They genuinely disagree on four
    known shapes. Counting the rows from the list the rows were built from would make the
    equality tautological and the mutant that deletes it would survive every fixture.
    """
    found = sdlc_md.find_by_id(Path(repo_root), unit)
    if not found:
        return {"ok": False, "errors": [f"{unit}: no artefact with that id"]}
    path, _type = found
    text = sdlc_md.read_text_safe(path)
    blocks = parse_story(text)
    declared = sdlc_md.count_acs(text)
    ids = [b.ac_id for b in blocks]

    # A DUPLICATE id makes "one row per criterion" unrepresentable: two criteria would key to one
    # row and the plan would silently govern only the survivor. Refused before the count check, so
    # the message names the real fault rather than a mismatch it happens to cause.
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        return {"ok": False, "path": str(path), "rows": len(blocks), "criteria": declared,
                "errors": [f"{unit}: duplicate criterion id(s) {', '.join(dupes)} - a plan keyed "
                           f"by criterion cannot carry two rows under one id, so one criterion "
                           f"would go unplanned. Renumber them."]}
    if len(blocks) != declared:
        missing = ", ".join(ids) or "none"
        return {"ok": False, "path": str(path), "rows": len(blocks), "criteria": declared,
                "errors": [
                    f"{unit}: the plan would carry {len(blocks)} row(s) for {declared} "
                    f"criterion/criteria - refusing to write a plan that does not account for "
                    f"every one. Rows would cover: {missing}. Two independent readers disagree "
                    f"about this file, which is a defect in the file rather than in either "
                    f"reader: a duplicate `### ACn` id, a bare `- [ ]` item with no ACn, an "
                    f"`### ACn` outside the Acceptance Criteria section, or one inside a fence."]}

    affects = [a.strip() for a in (sdlc_md.extract_field(text, "Affects") or "").split(",")
               if a.strip()]
    existing = _testplan_rows(text)
    # A `## Test Plan` THIS PARSER CANNOT READ is never overwritten. `_testplan_rows` harvests
    # `| ACn | mutant |` table rows only, so a plan authored as prose - which is how the first
    # ones were written, US0629's own among them - yields no rows, and replacing the section
    # would silently destroy an independently-reviewed artefact and report exit 0. A seat ran
    # this against US0629's own file and watched 178 lines become 79. Refuse instead: naming the
    # mutant is the judgement, and judgement the tool cannot parse is still judgement.
    if _TESTPLAN_HEADING in text and not existing:
        body = re.search(r"^## Test Plan\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        if body and len(_reason_substance(body.group(1))) > 40:
            return {"ok": False, "path": str(path), "rows": 0, "criteria": declared,
                    "errors": [f"{unit} already has a `## Test Plan` this command cannot read - "
                               f"it carries no `| ACn | mutant |` rows, so deriving would replace "
                               f"an authored plan with placeholders. Convert it to the table "
                               f"shape by hand, or delete the section deliberately if it is "
                               f"stale. A plan the tool cannot parse is still a plan."]}
    lines = text.splitlines()
    bounds = [b.heading_line for b in blocks] + [_criteria_section_end(lines, blocks)]
    by_ac = testplan_rows_by_criterion(text)
    # AN ORPHAN ROW IS EVIDENCE, AND EVIDENCE IS NOT DROPPED SILENTLY. A row whose criterion is no
    # longer declared - what renumbering an AC produces - used to vanish at exit 0, the second
    # silent-loss path BG0597 found while its own criteria were being authored. Refuse instead:
    # the author decides whether that mutant is stale, not the parser.
    declared_ids = {b.ac_id for b in blocks}
    orphans = [f"`| {ac} | {m} |`" for ac, ms in sorted(by_ac.items())
               if ac not in declared_ids for m in ms]
    if orphans:
        return {"ok": False, "path": str(path), "rows": sum(len(v) for v in by_ac.values()),
                "criteria": declared,
                "errors": [f"{unit}: {len(orphans)} Test Plan row(s) name a criterion this unit "
                           f"no longer declares, and re-deriving would delete them at exit 0: "
                           f"{'; '.join(orphans[:6])}. Renumber them onto a live criterion, or "
                           f"remove them deliberately - a derive that loses an authored mutant "
                           f"must not report success."]}
    faults, rows = [], []
    for n, b in enumerate(blocks):
        mutants = by_ac.get(b.ac_id) or [_TESTPLAN_PLACEHOLDER]
        then = _then_clause(lines, b.heading_line, bounds[n + 1])
        for mutant in mutants:
            rows.append((b.ac_id, (b.title or "").strip(), mutant))
            if mutant != _TESTPLAN_PLACEHOLDER:
                for why in testplan_row_faults(mutant, then, affects):
                    faults.append(f"{unit} {b.ac_id}: {why}")
    if faults:
        return {"ok": False, "path": str(path), "rows": len(rows), "criteria": declared,
                "errors": faults}

    table = ["| Criterion | Mutant - the production change this test must fail on | Title |",
             "| --- | --- | --- |"]
    table += [f"| {i} | {m} | {t} |" for i, t, m in rows]
    section = _TESTPLAN_HEADING + "\n\n" + "\n".join(table) + "\n"
    rendered = _replace_testplan(text, section)
    unchanged = rendered == text
    if write and not unchanged:
        path.write_text(rendered, encoding="utf-8")
    return {"ok": True, "path": str(path), "rows": len(rows), "criteria": declared,
            "unchanged": unchanged, "authored": sum(1 for _i, _t, m in rows
                                                    if m != _TESTPLAN_PLACEHOLDER)}


def _replace_testplan(text: str, section: str) -> str:
    """Replace the ONE `## Test Plan` section, or insert it before Revision History.

    Replaced rather than appended: a regenerate-and-append leaves the authored section in place
    while the generated one governs, and an assertion that the authored string survives cannot
    tell the two apart.
    """
    lines = text.splitlines(keepends=True)
    out, i, replaced = [], 0, False
    while i < len(lines):
        if lines[i].rstrip() == _TESTPLAN_HEADING:
            if not replaced:
                out.append(section + "\n")
                replaced = True
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    if replaced:
        return "".join(out)
    body = "".join(out)
    marker = "## Revision History"
    if marker in body:
        return body.replace(marker, section + "\n" + marker, 1)
    return body.rstrip("\n") + "\n\n" + section


def cmd_testplan(args: argparse.Namespace) -> int:
    """`testplan derive` - write the unit's plan, or refuse and say which criterion is at fault."""
    root = resolve_root(args)
    res = testplan_derive(root, args.unit, write=not getattr(args, "dry_run", False))
    if not res.get("ok"):
        for e in res.get("errors", []):
            print(f"testplan derive refused: {e}", file=sys.stderr)
        return 2
    if res.get("unchanged"):
        print(f"testplan derive: {args.unit} unchanged - {res['rows']} row(s) already match its "
              f"{res['criteria']} criteria, and {res['authored']} authored mutant(s) were kept")
        return 0
    print(f"testplan derive: {args.unit} -> {res['rows']} row(s) for {res['criteria']} "
          f"criteria in {res['path']}")
    return 0


def cmd_lane_check(args: argparse.Namespace) -> int:
    """Report criteria verified only through the library. REPORTS, never fails.

    Ships advisory while its yield is measured, on the same terms the claim-drift lane shipped
    under: a new blocking check on a gate already over its ceiling earns its place on a number
    rather than on assertion.
    """
    root = Path(args.root)
    # BUGS ARE IN SCOPE. The sweep globbed `stories/US*.md` only, so every bug was outside the
    # count a blocking decision would rest on - and `--ids BG0487` printed "0 unit(s)" rather
    # than saying the type was out of scope, which reads as a clean bill of health for a unit
    # nothing looked at. Bugs carry executable criteria and reach a terminal status through the
    # same gate, so a lane that judges one and silently omits the other is measuring half the
    # corpus while reporting a whole-corpus number.
    units = sorted((root / "sdlc-studio" / "stories").glob("US*.md"))
    units += sorted((root / "sdlc-studio" / "bugs").glob("BG*.md"))
    units = [u for u in units if not u.name.startswith("_")]
    if getattr(args, "ids", None):
        wanted = {i.strip().upper() for i in args.ids.split(",") if i.strip()}
        units = [s for s in units
                 if (sdlc_md.extract_record_id(s.stem) or "").upper() in wanted]
    findings = lane_check(root, units)
    for f in findings:
        print(f"LANE-CHECK: {f['unit']} {f['ac']} -> {f['why']}", file=sys.stderr)
    try:
        import json as _json  # noqa: PLC0415
        path = root / _LANE_YIELD_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            raw = path.read_text(encoding="utf-8")  # bare-read-ok: own JSON accumulator
            rec = _json.loads(raw)
        except (OSError, ValueError):
            rec = {"runs": 0, "findings": 0}
        rec["runs"] = int(rec.get("runs", 0)) + 1
        rec["findings"] = int(rec.get("findings", 0)) + len(findings)
        path.write_text(_json.dumps(rec, indent=2), encoding="utf-8")
    except OSError:
        pass
    if not findings:
        print(f"lane-check: {len(units)} unit(s), no library-only verifiers")
    return 0  # ADVISORY - the exit code is never the finding


def cmd_scaffold(args: argparse.Namespace) -> int:
    """Emit the pre-filled AC Coverage Matrix for an epic to stdout (or a file)."""
    repo_root = resolve_root(args)
    matrix = scaffold_ac_matrix(repo_root, args.epic)
    if getattr(args, "out", None):
        out = under_root(repo_root, args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(matrix, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(matrix, end="")
    return 0


EPIC_TS_KEY = "quality.epic_requires_test_spec"


def epic_ts_enforced(repo_root: Path | str) -> bool:
    """Does a failing epic-scope test-spec check GATE this project?
    `quality.epic_requires_test_spec` in `sdlc-studio/.config.yaml`, default true.

    The key was documented as the opt-out from the epic-scope requirement and read by nothing,
    so a project staging the migration set it in good faith and got no effect and no warning.
    It is read here, once, and the reading is what the documentation now describes.

    Only a real YAML boolean decides. A value that is not one (`maybe`, `"false"`, a list) is
    the same failure in miniature - a setting acted on that cannot be honoured - so it WARNS on
    stderr and falls back to enforcing. Guessing that a non-boolean meant "off" would silently
    drop the gate on a typo; the safe direction is the documented default.
    """
    val = sdlc_md.project_override(repo_root, EPIC_TS_KEY, True)
    if isinstance(val, bool):
        return val
    print(f"warning: {EPIC_TS_KEY}: {val!r} is not true or false; the epic-scope test-spec "
          "requirement stays enforced (set the key to a boolean to change it)", file=sys.stderr)
    return True


def epic_test_spec_check(repo_root: Path | str, epic_id: str) -> dict:
    """Epic-scope test-spec requirement: an epic must have a test-spec (linked by its
    `Epic:` field) whose AC Coverage Matrix passes `ts-check`. Reuses `ts_check` - no new
    verification logic.

    Returns {epic, ok, specs, issues, enforced}. `ok` is the check's own verdict and never
    moves with configuration - the findings are the findings. `enforced` is
    `quality.epic_requires_test_spec` (default true), and it is what decides whether a false
    `ok` gates: `epic-ts` exits 1 only when the check failed AND the project enforces,
    otherwise it prints the same findings as advisory and exits 0. That split is the opt-out a
    project mid-migration needs - it can see the specs it owes without the gate stopping it.

    The check is epic-scope by construction: it is reached only through `epic-ts --epic`, so
    single-story work (`story implement`) never invokes it.
    """
    root = Path(repo_root)
    eid = sdlc_md.norm_id(epic_id)
    specs = []
    for p in sdlc_md.artifact_files("test-spec", root):
        ef = sdlc_md.extract_field(sdlc_md.read_text_safe(p), "Epic") or ""
        m = sdlc_md.ID_SEARCH_RE.search(ef)
        if m and sdlc_md.norm_id(m.group(0)) == eid:
            specs.append(p)
    enforced = epic_ts_enforced(root)
    if not specs:
        return {"epic": epic_id, "ok": False, "specs": [], "enforced": enforced,
                "issues": [{"issue": "no test-spec links to this epic (epic-scope TS required)"}]}
    issues = [{**i, "spec": sp.name} for sp in specs for i in ts_check(sp)]
    return {"epic": epic_id, "ok": not issues, "specs": [s.name for s in specs],
            "issues": issues, "enforced": enforced}


def cmd_epic_ts(args: argparse.Namespace) -> int:
    r = epic_test_spec_check(resolve_root(args), args.epic)
    advisory = not r["ok"] and not r["enforced"]
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        for it in r["issues"]:
            print(f"  {it.get('spec', args.epic)}: {it.get('ac', '')} {it['issue']}")
        # A FAIL that exits 0 must say why on the same line as the verdict. An exit code
        # that disagrees with the printed word, with the reason nowhere, reads as a bug.
        why = f" - advisory only ({EPIC_TS_KEY}: false)" if advisory else ""
        print(f"epic-ts: {args.epic} {'OK' if r['ok'] else 'FAIL'} "
              f"({len(r['specs'])} spec(s)){why}")
    return 0 if (r["ok"] or advisory) else 1


def cmd_ts_check(args: argparse.Namespace) -> int:
    repo_root = resolve_root(args)
    spec = under_root(repo_root, args.spec)
    report = under_root(repo_root, args.verify_report) if args.verify_report else None
    try:
        issues = ts_check(spec, report)
    except FileNotFoundError as exc:
        # Exit 2 (a broken invocation), never 1 (a matrix with findings) and never 0. The
        # resolved path is named because that is the only way the caller can see WHICH
        # path was wrong when --spec was relative to a root it did not expect.
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(issues, indent=2))
        return 1 if issues else 0
    for it in issues:
        print(f"  {it['ac']}: {it['issue']}")
    # "finding(s)", not "incomplete matrix row(s)": an unreadable spec is one finding and
    # no rows at all, and the summary must not describe it as a row it never read.
    print(f"ts-check: {len(issues)} finding(s) in {spec.name}")
    return 1 if issues else 0


#: Where the tolerated duplicate-verifier groups are recorded. A RATCHET: the set may only
#: shrink, so a group that is fixed cannot be spent again to admit a new one.
DUP_BASELINE_REL = "sdlc-studio/.verify-lint-baseline.json"

#: The most ACs one tolerated group may cover. A group that grows past this is not the group
#: that was baselined, whatever its selector says. Applied to the LIVE set as well as the
#: recorded one - capping only what the entry says about itself checks nothing.
DUP_ENTRY_AC_CAP = 8

#: Characters of substance a `reason` needs. `-`, `n/a` and `TODO` cleared a
#: non-blank test while stating nothing, so an exemption could be minted with one keystroke.
DUP_REASON_MIN = 20

#: Id prefixes that CARRY acceptance criteria. An `acs` entry naming an epic or a CR resolved
#: happily under a plain existence check and proved nothing, because only a story or a bug has
#: ACs that can share a selector.
DUP_AC_UNIT_PREFIXES = ("US", "BG")

#: Padding a `reason` may not count towards its substance.
_REASON_FILLER = re.compile(r"^(?:n/?a|tbd|todo|none|see above|as above|-+|\.+)$", re.I)


def _reason_substance(reason: str) -> str:
    """The part of a `reason` that carries meaning: punctuation and filler stripped.

    A one-character `-` passed a non-blank check, so the floor is measured on what is left after
    the padding comes off rather than on the raw length.
    """
    text = " ".join((reason or "").split())
    if _REASON_FILLER.match(text):
        return ""
    return re.sub(r"[^0-9a-z]", "", text, flags=re.I)


def dup_group_key(verifier: str) -> str:
    """The identity a tolerated group is recorded under: whitespace normalised, VERB lowercased.

    The SET of groups is what the ratchet compares, never the COUNT. A change that splits one
    baselined group and introduces a new one leaves the count flat, and a count-based guard
    passes it - which is the guard a rising total would already have caught, so it adds nothing.

    The verb is lowercased because the DSL lowercases it before dispatch, so `PyTest x` and
    `pytest x` run the IDENTICAL command. Comparing them case-sensitively made a case-only twin
    of a baselined selector a group of one under each spelling, reported as no duplicate at all.
    Only the leading token is folded: the rest is paths and node ids, and those are
    case-sensitive on every filesystem that matters.
    """
    parts = " ".join((verifier or "").split()).split(" ", 1)
    if not parts or not parts[0]:
        return ""
    head = parts[0].lower()
    written = head if len(parts) == 1 else f"{head} {parts[1]}"
    # Grouped on the command that RUNS, not the one that was typed. Two criteria can name the
    # identical run in different words - a flag written in a different order, a `-q` the runner
    # supplies anyway - and on the written string they formed a group of one under each spelling
    # and were reported as no duplicate at all. Two criteria sharing a selector cannot both
    # discriminate, whichever way each was spelled.
    #
    # Falls back to the written form whenever the expression does not resolve: an unrecognised
    # head is an invalid verifier reported elsewhere, and inventing a key for it here would
    # group two unrelated broken lines together.
    try:
        kind, cmd = _build_command(written)
    except (ValueError, OSError):
        return written
    if not isinstance(cmd, list) or not cmd:
        return written
    # Flags sorted and de-duplicated; positionals kept in order, because their order is what
    # distinguishes one selector from another. Deliberately conservative: this decides only what
    # counts as the SAME command, and over-merging would hide a real pair of distinct criteria.
    flags = sorted({a for a in cmd[1:] if a.startswith("-")})
    positional = [a for a in cmd[1:] if not a.startswith("-")]
    return " ".join([kind, *flags, *positional])


def read_dup_baseline(repo_root) -> dict:
    """`{"state", "entries", "detail"}` for the recorded baseline.

    `state` is one of `ok`, `not-baselined`, `corrupt`. Three DISTINCT states, because the
    remedy differs: an absent baseline wants a first stamp, an unreadable one wants a human,
    and neither may read as a clean scan. A ratchet that reports clean over a baseline it
    could not parse is a ratchet nobody is holding.
    """
    path = Path(repo_root) / DUP_BASELINE_REL
    if not path.is_file():
        return {"state": "not-baselined", "entries": {}, "detail": f"no {DUP_BASELINE_REL}"}
    # Through the shared reader, which the hygiene sweep requires: a bare `read_text` on an
    # artefact-workspace path is the class that turns an unreadable file into a crash instead of
    # a stated absence. Here the DISTINCTION is the whole point - absent and corrupt are
    # different states with different remedies - so the two are separated explicitly.
    # `read_text_safe` yields "" for a file it cannot read, and the ABSENT case is already
    # handled above - so an empty read here means unreadable, and `json.loads("")` lands it in
    # the same `corrupt` state as malformed content. Both want a human, and neither may pass.
    try:
        raw = json.loads(sdlc_md.read_text_safe(path))
    except ValueError as exc:
        return {"state": "corrupt", "entries": {}, "detail": f"{DUP_BASELINE_REL}: {exc}"}
    groups = raw.get("groups") if isinstance(raw, dict) else None
    if not isinstance(groups, dict):
        return {"state": "corrupt", "entries": {},
                "detail": f"{DUP_BASELINE_REL} has no `groups` object"}
    # Keys normalised on the way IN. The live side arrives already normalised, so applying
    # `dup_group_key` only there normalised the one side that did not need it: this file is the
    # side a human hand-edits, and a key with a double space was reported as BOTH new and stale -
    # two refusals describing one entry, neither naming the real cause.
    normalised: dict = {}
    collisions: list[str] = []
    for key, entry in groups.items():
        k = dup_group_key(str(key))
        if k in normalised:
            collisions.append(k)
        normalised[k] = entry
    if collisions:
        return {"state": "corrupt", "entries": {},
                "detail": f"{DUP_BASELINE_REL}: {len(collisions)} key(s) collide once normalised "
                          f"({', '.join(sorted(set(collisions))[:3])}) - two entries for one "
                          f"group means one of them is silently unused"}
    return {"state": "ok", "entries": normalised, "detail": ""}


def dup_entry_errors(repo_root, verifier: str, entry, live_acs=None) -> list:
    """Why a baseline entry may not silence the ratchet. Empty means it may.

    An exemption is machinery, not an assumption: it needs a REASON a human wrote, and every
    AC it names has to resolve, or the entry is a way past the guard rather than a record of a
    tolerated case.

    `live_acs` is the set of ACs that CURRENTLY share this selector. Pass it: without it the
    entry is judged only against itself, and an entry baselined at 2 ACs stays green while the
    selector spreads onto 30 - the exact class `duplicate_verifiers` names ("a whole-file
    selector spreads - copied onto every AC of a story"). It defaults to None only so a caller
    validating a baseline with no scan in hand can still check the entry's own shape.
    """
    errors = []
    if not isinstance(entry, dict):
        return [f"{verifier!r}: entry is not an object"]
    reason = str(entry.get("reason") or "").strip()
    if len(_reason_substance(reason)) < DUP_REASON_MIN:
        errors.append(f"{verifier!r}: `reason` is {len(_reason_substance(reason))} characters of "
                      f"substance, under the floor of {DUP_REASON_MIN} - `-` and `n/a` are a "
                      f"silence, not a decision")
    acs = entry.get("acs")
    if not isinstance(acs, list) or not acs:
        errors.append(f"{verifier!r}: no `acs` list naming what the group covers")
        return errors
    recorded = {str(r).strip() for r in acs if str(r).strip()}
    if len(recorded) != len([r for r in acs if str(r).strip()]):
        errors.append(f"{verifier!r}: names the same AC more than once, which inflates the "
                      f"recorded set without covering anything")
    if len(recorded) > DUP_ENTRY_AC_CAP:
        errors.append(f"{verifier!r}: covers {len(recorded)} ACs, over the cap of "
                      f"{DUP_ENTRY_AC_CAP} - a group this wide is not the one that was "
                      f"baselined")
    for ref in sorted(recorded):
        unit = str(ref).split()[0] if str(ref).strip() else ""
        found = sdlc_md.find_by_id(Path(repo_root), unit) if unit else None
        if not found:
            errors.append(f"{verifier!r}: names {ref!r}, whose unit resolves to no artefact")
        elif unit[:2] not in DUP_AC_UNIT_PREFIXES:
            errors.append(f"{verifier!r}: names {ref!r}, which is not a story or a bug - only a "
                          f"unit that CARRIES acceptance criteria can be part of a duplicate "
                          f"group, so an epic or CR id here resolves while proving nothing")
    # THE LIVE SET IS THE AUTHORITY, not the recorded one. Capping only the recorded list left
    # the class the ratchet exists to stop wide open: an entry baselined at 2 ACs stayed green
    # with the selector spread onto 30, because nothing compared the two. A tolerated group is
    # a specific set of ACs sharing a specific command, so the sets must match exactly.
    if live_acs is not None:
        live = {str(a).strip() for a in live_acs}
        if live != recorded:
            grew, shrank = sorted(live - recorded), sorted(recorded - live)
            detail = []
            if grew:
                detail.append(f"now also claimed by {', '.join(grew)}")
            if shrank:
                detail.append(f"no longer claimed by {', '.join(shrank)}")
            errors.append(f"{verifier!r}: the baselined set is {len(recorded)} AC(s) and the live "
                          f"set is {len(live)} ({'; '.join(detail)}) - a tolerated group is a "
                          f"specific set of ACs, so a selector that has spread since it was "
                          f"baselined is not the group anybody tolerated")
    return errors


def dup_ratchet(repo_root, paths) -> dict:
    """The ratchet verdict: `{"ok", "state", "new", "stale", "errors"}`.

    `new` is a duplicate group the baseline does not hold - refused. `stale` is a baselined
    group whose ACs no longer share a selector - also refused, because a tolerated set that
    keeps a fixed entry can be spent again to admit a new one, and then the ratchet only ever
    loosens.
    """
    base = read_dup_baseline(repo_root)
    live = {dup_group_key(d["verifier"]): d for d in duplicate_verifiers(paths)}
    if base["state"] != "ok":
        return {"ok": False, "state": base["state"], "new": sorted(live),
                "stale": [], "errors": [base["detail"]]}
    entries = base["entries"]
    errors = []
    for verifier, entry in sorted(entries.items()):
        # The LIVE group is handed in, so an entry is judged against what currently shares its
        # selector rather than only against its own recorded fields.
        group = live.get(verifier)
        errors.extend(dup_entry_errors(repo_root, verifier, entry,
                                       live_acs=group["acs"] if group else None))
    new = sorted(k for k in live if k not in entries)
    stale = sorted(k for k in entries if k not in live)
    return {"ok": not (new or stale or errors), "state": "ok",
            "new": new, "stale": stale, "errors": errors}


def cmd_lint(args: argparse.Namespace) -> int:
    """Flag Verify lines that would fall through to `shell` but look like a
    mis-written runner invocation. Catches the AC↔test drift at author time
    instead of discovering it 0/7 at verify time.

    Advisory EXCEPT for the markdown-evidence refusal, which exits non-zero: that class
    has already shipped four false passes past a human review, so an advisory it can be
    walked past is what already failed. The refusal applies only while the story is still
    being authored (Draft/Ready) - past that the criterion has shipped and refusing it
    retrospectively blocks a lint run over history without helping anyone."""
    repo_root = resolve_root(args)
    paths = [Path(args.story)] if args.story else list(walk_stories(under_root(repo_root, args.dir)))
    if getattr(args, "bugs", False) and not args.story:
        # `sdlc-studio/bugs` too, as `stamps --bugs` already scans it. Without this a shared
        # selector can be PARKED in a bug, where `duplicate_verifiers` never looked.
        # `("BG",)`, because `walk_stories` defaults to stories alone - passing the bugs
        # DIRECTORY without the prefix yields nothing and the scan silently covers no bugs,
        # which is the exemption-by-omission this flag exists to close.
        paths += list(walk_stories(under_root(repo_root, "sdlc-studio/bugs"), prefixes=("BG",)))
    flagged = 0
    refused = 0
    for p in paths:
        if not p.exists():
            continue
        text = sdlc_md.read_text_safe(p)
        status = (sdlc_md.extract_field(text, "Status") or "").strip().lower()
        authoring = status in _AUTHORING_STATUSES
        for block in parse_story(text):
            stacked = lint_stacked_verifiers(block) if authoring else None
            if stacked:
                refused += 1
                print(f"{p.name} {block.ac_id}: REFUSED: {stacked}")
        for line in text.splitlines():
            m = VERIFY_RE.match(line)
            if not m:
                continue
            expr = m.group(2).strip()
            markdown_only = lint_markdown_evidence(expr, repo_root) if authoring else None
            if markdown_only:
                refused += 1
                print(f"{p.name}: {expr!r}\n    -> REFUSED: {markdown_only}")
            reason = lint_verifier(expr)
            if reason:
                flagged += 1
                print(f"{p.name}: {expr!r}\n    -> {reason}")
            availability = lint_runner_available(expr)
            if availability:
                flagged += 1
                print(f"{p.name}: {expr!r}\n    -> {availability}")
    dupes = duplicate_verifiers(paths)
    # UNANSWERABLE groups, derived here by asking the resolver - never read from a list in a
    # document. `selector_resolves` answers None for a verifier whose selector no collection can
    # decide (`manual`, `grep`, `shell`, an absent runner), and a group of those cannot be split
    # into discriminating halves because nothing can say what either half selects. Deriving it at
    # lint time means a group that becomes answerable - or stops being - moves in and out of the
    # set without anybody editing prose, which a hand-kept list could never manage.
    unanswerable = []
    for d in dupes:
        if selector_resolves(d["verifier"]) is None:
            unanswerable.append(d)
    unanswerable_keys = {d["verifier"] for d in unanswerable}
    for d in dupes:
        flagged += 1
        if d["verifier"] in unanswerable_keys:
            continue
        print(f"duplicate verifier across {len(d['acs'])} ACs: {d['verifier']!r}\n"
              f"    -> {', '.join(d['acs'])}\n"
              f"    -> two ACs sharing a selector cannot both discriminate - a regression in "
              f"either fails both, and neither says which")
    if unanswerable:
        # ONE LINE PER MEMBER, with the verb that makes it unanswerable and every AC claiming
        # it. A count cannot be taken apart: a reader told "6 groups are exempt" cannot see
        # which, so cannot tell an exemption that is still true from one that quietly stopped
        # being. Each line is the whole fact.
        print(f"unanswerable duplicate group(s) - no collection can decide what these select, "
              f"so they cannot be split into discriminating halves:")
        for d in unanswerable:
            verb = (d["verifier"].split() or ["?"])[0]
            print(f"    [{verb}] {d['verifier']!r}\n"
                  f"        claimed by: {', '.join(d['acs'])}")
    print(f"verify-lint: {flagged} suspicious Verify line(s) (advisory)")
    if getattr(args, "stamp", False):
        return _stamp_dup_baseline(repo_root, paths)
    if getattr(args, "ratchet", False):
        verdict = dup_ratchet(repo_root, paths)
        if not verdict["ok"]:
            if verdict["state"] == "not-baselined":
                print(f"verify-lint RATCHET: {verdict['errors'][0]} - the tolerated set is "
                      f"unrecorded, so nothing can be held to it. Record it once with "
                      f"`verify_ac.py lint --ratchet --stamp`, then every later run may only "
                      f"shrink it.", file=sys.stderr)
            elif verdict["state"] == "corrupt":
                print(f"verify-lint RATCHET: {verdict['errors'][0]} - the baseline could not be "
                      f"parsed, and a ratchet that reports clean over a baseline it cannot read "
                      f"is a ratchet nobody is holding.", file=sys.stderr)
            for group in verdict["new"]:
                print(f"verify-lint RATCHET: REFUSED - {group!r} is shared by more than one AC "
                      f"and the baseline does not record it. Split the selector so each "
                      f"criterion discriminates, or record the group with a reason.",
                      file=sys.stderr)
            for group in verdict["stale"]:
                print(f"verify-lint RATCHET: STALE - {group!r} is recorded as tolerated and its "
                      f"ACs no longer share a selector. Remove the entry: a tolerated set that "
                      f"keeps a fixed group can spend it again to admit a new one.",
                      file=sys.stderr)
            for err in verdict["errors"][1:] if verdict["state"] != "ok" else verdict["errors"]:
                print(f"verify-lint RATCHET: {err}", file=sys.stderr)
            return 1
        print("verify-lint: ratchet clean - no duplicate group the baseline does not record")
    if refused:
        print(f"verify-lint: {refused} markdown-only verifier(s) REFUSED on a story still "
              f"being authored - each proves a sentence was written, not that the behaviour "
              f"exists", file=sys.stderr)
        return 1
    return 0


def _stamp_dup_baseline(repo_root, paths) -> int:
    """Record the CURRENT duplicate groups as the tolerated set.

    Refuses to mint an entry with no reason: a stamp that writes a reasonless exemption would
    make the reason field decoration, and the ratchet's whole value is that an exemption is a
    decision somebody recorded. The reason is seeded as a placeholder the author must replace,
    and `--ratchet` refuses it until they do.
    """
    live = duplicate_verifiers(paths)
    groups = {}
    for d in live:
        groups[dup_group_key(d["verifier"])] = {
            "acs": list(d["acs"]),
            "reason": "",   # deliberately EMPTY - the ratchet refuses it until a human writes one
        }
    path = Path(repo_root) / DUP_BASELINE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(path, json.dumps({"groups": groups}, indent=2) + "\n")
    print(f"verify-lint: baselined {len(groups)} duplicate group(s) -> {DUP_BASELINE_REL}")
    if groups:
        print("verify-lint: every entry carries an EMPTY reason and the ratchet REFUSES it "
              "until one is written - a stamp that minted a reasonless exemption would make "
              "the field decoration.", file=sys.stderr)
        return 1
    return 0


def cmd_stamps(args: argparse.Namespace) -> int:
    """Report stamped-green ACs whose verifier no longer selects anything.

    The routine this condition lacked. A stamp went green for two days against a test that
    did not exist, and nothing looked: freshness compared the AC text, which had not changed,
    and the only thing that would have caught it was a full suite run nobody had reason to do.
    Exits non-zero so it can gate rather than inform.
    """
    repo_root = resolve_root(args)
    paths = ([Path(args.story)] if args.story
             else list(walk_stories(under_root(repo_root, args.dir))))
    if args.bugs:
        bugs = under_root(repo_root, "sdlc-studio/bugs")
        if bugs.is_dir():
            paths += sorted(p for p in bugs.glob("*.md") if not p.name.startswith("_"))
    dead = 0
    for p in paths:
        if not p.exists():
            continue
        for row in unresolvable_stamps(p, repo_root):
            dead += 1
            print(f"{row['record']} {row['ac']}: stamped verified, but its verifier selects "
                  f"nothing\n    {row['verifier']}")
    if dead:
        print(f"verify-stamps: {dead} stamped AC(s) resting on a selector that resolves to "
              f"nothing - the stamp is STALE, not green", file=sys.stderr)
        return 1
    print(f"verify-stamps: {len(paths)} file(s) checked, every stamped verifier still resolves")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Print the latest verification report in text or JSON form."""
    report_path = under_root(resolve_root(args), args.report)
    if not report_path.exists():
        print(f"error: no report at {report_path}. Run `verify_ac.py run` first.", file=sys.stderr)
        return 2
    data = sdlc_md.read_json(report_path, None)
    if data is None:
        print(f"error: {report_path} is not valid JSON", file=sys.stderr)
        return 2
    stories = data.get("stories", {})
    total_fail_all = sum(s.get("failed", 0) for s in stories.values())
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 1 if total_fail_all else 0  # BG0088: JSON mode signals failure like text

    print(f"generated_at: {data.get('generated_at')}")
    if not stories:
        print("no stories in report")
        return 0
    total_pass = total_fail = total_manual = total_unspecified = 0
    for sid, s in stories.items():
        total_pass += s.get("verified", 0)
        total_fail += s.get("failed", 0)
        total_manual += s.get("manual", 0)
        total_unspecified += s.get("unspecified", 0)
        print(
            f"{sid}: ac={s.get('ac_count', 0)} "
            f"pass={s.get('verified', 0)} "
            f"fail={s.get('failed', 0)} "
            f"manual={s.get('manual', 0)} "
            f"unspecified={s.get('unspecified', 0)}"
        )
        for fail in s.get("failures", []):
            print(f"  FAIL {fail['ac']}: {fail['verifier']}")
    print(f"total: pass={total_pass} fail={total_fail} "
          f"manual={total_manual} unspecified={total_unspecified}")
    return 1 if total_fail > 0 else 0


# -----------------------------------------------------------------------------
# revert-check: do a unit's own verifiers reach its production change?
# -----------------------------------------------------------------------------


def is_test_path(path: str) -> bool:
    """Does this declared path hold TEST code rather than production code?

    Reverting a test file cannot answer the question this check asks. The tests ARE the
    measurement, so removing them removes the instrument rather than the thing under it.
    Decided in ONE place, because a second predicate that disagreed about `tests/helpers.py`
    would let a unit be judged against a surface nobody described - the same two-readers
    defect `_is_markdown` was collapsed to fix.
    """
    parts = str(path).replace("\\", "/").split("/")
    # `testing` is NOT here: `scripts/testing/engine.py` is a plausible production package, and
    # excluding it from a revert would judge a unit against a smaller surface than it declared
    # while reporting nothing. An independent review found that misclassification.
    if any(seg in ("test", "tests", "__tests__") for seg in parts[:-1]):
        return True
    name = parts[-1]
    stem = name.rsplit(".", 1)[0] if "." in name else name
    return (name.startswith("test_") or stem.endswith("_test")
            or stem.endswith(".test") or stem.endswith(".spec"))


def revert_targets(root, text: str) -> dict:
    """A unit's declared `Affects` split into what a revert may touch and what it may not.

    Existence is judged against the REPO ROOT rather than through `sdlc_md.resolve_affects`,
    which also searches the installed skill copy: a file that resolves outside this git tree
    cannot be reverted to a ref of it, and reporting it as revertible would revert nothing
    while claiming to have measured something.
    """
    root = Path(root)
    out: dict = {"production": [], "tests": [], "docs": [], "unresolvable": []}
    for raw in sdlc_md.affects_files(text):
        rel = raw.strip().strip("`")
        if _is_markdown(rel):
            out["docs"].append(rel)
        elif is_test_path(rel):
            out["tests"].append(rel)
        elif _revertible(root, rel):
            out["production"].append(rel)
        else:
            out["unresolvable"].append(rel)
    return out


def _revertible(root: Path, rel: str) -> bool:
    """May this declared path be reverted to a ref of THIS repository, and restored afterwards?

    Every answer here is a refusal to touch the file, and each one is a defect an independent
    review found by trying it rather than by reading:

      * OUTSIDE THE ROOT. `(root / rel)` resolves `..` segments and an absolute `rel` replaces
        the root outright, so `../victim/secret.py` and `/etc/thing` both looked like ordinary
        production files. `git show <ref>:<path>` then fails, the file is deleted as
        "absent at base", and it comes back with the process umask - a private file returned
        group- and world-readable. The docstring above promised this defence and the code did
        not have it.
      * A SYMLINK. `is_file()` follows one, so the link was classified production, deleted and
        recreated as a REGULAR FILE holding its target's bytes. Where the link existed at base,
        `write_bytes` wrote THROUGH it and reverted the target instead of the declared path -
        a wrong measurement, taken in silence.
      * UNREADABLE. The refusal already SAID "not a readable file here" while nothing tested
        readability, and the snapshot then raised out of the command.
    """
    path = root / rel
    try:
        if Path(rel).is_absolute() or not path.resolve().is_relative_to(root.resolve()):
            return False
        if path.is_symlink() or not path.is_file():
            return False
        return os.access(path, os.R_OK | os.W_OK)
    except OSError:
        return False


#: A declared, reasoned exemption from the revert check, e.g.
#: `> **Revert-check-exempt:** AC2 - the paired control asserts the pre-change behaviour`.
EXEMPT_FIELD = "Revert-check-exempt"
_AC_TOKEN_RE = re.compile(r"\bAC\d+\b", re.I)
#: A path INSIDE a test-plan mutant cell: at least one `/` and an extension, so ordinary prose
#: cannot be mistaken for a file the criterion is about.
#: A file named in a test-plan mutant cell, WITH OR WITHOUT a directory. The `/`-requiring
#: form missed a bare filename, and 272 of the 459 plan rows in this corpus name their file
#: that way - "in `verify_ac.py`, delete the ..." - so a row naming a production file beside a
#: test path read as test-code-only and silently exempted the criterion.
#: TWO forms, because the extension list is the part that goes out of date (LL0013). A token
#: carrying a `/` is a path whatever it ends in - that is what closed `config/settings.yaml`,
#: which the allowlist-only form could not see at all, so a row naming it beside a test path
#: read as test-code-only and exempted the criterion while `revert_targets` was reverting the
#: very same file. A BARE filename still needs the allowlist: without a `/` there is nothing
#: to tell `settings.yaml` from ordinary prose, and the list is widened to the config and
#: markup families this corpus actually ships rather than left at the source-code ones.
_MUTANT_PATH_EXTS = ("py|js|ts|tsx|jsx|mjs|cjs|go|sh|bash|rb|java|rs|c|h|hpp|cpp|cs|kt|php|lua|"
                     "pl|sql|yaml|yml|json|toml|cfg|ini|conf|env|md|rst|txt|html|css|scss|xml|"
                     "tf|hcl|proto|graphql|vue|svelte|gradle|properties")
_MUTANT_PATH_RE = re.compile(
    r"(?:[\w.-]*[\w-](?:/[\w.-]+)+\.[A-Za-z][\w+]{0,9}"      # any extension once a `/` is present
    rf"|[\w-][\w.-]*\.(?:{_MUTANT_PATH_EXTS}))\b")


def revert_exemptions(text: str) -> dict:
    """`{AC id: why}` for each criterion a PRODUCTION-only revert may legitimately leave green.

    The taxonomy is the difference between a gate people keep and one they switch off:
    RUN-01M0CT8P measured five such criteria across a single six-unit batch, so a check
    without it refuses correct work on its first outing. Three classes, each derived from
    something already written down rather than from a judgement made here:

      * a WELL-FORMED `unnameable` plan row - the plan already records that nobody can name a
        falsifying production change, so demanding one here contradicts that record;
      * a DECLARED exemption field carrying a reason with substance. A bare id list is
        malformed and exempts nothing, on `unnameable`'s precedent: a state that costs nothing
        to enter is the state every awkward criterion chooses;
      * a criterion whose SUBJECT is test code - its plan row names paths and every one of
        them is a test file, so no production revert can move it.
    """
    out: dict = {}
    by_criterion = testplan_rows_by_criterion(text)
    unnameable = [r for r in testplan_unnameable(text) if not r["malformed"]]
    for row in unnameable:
        ac = row["ac"].upper()
        # EVERY row on the criterion must be unnameable. One `unnameable` beside a nameable
        # production mutant exempted the criterion outright, so the second row cost nothing and
        # covered the first - and the whole design of this marker is that it costs something.
        rows_here = by_criterion.get(ac) or by_criterion.get(row["ac"]) or []
        named = {r["ac"].upper() for r in unnameable}
        if all(str(m).strip().lower().startswith(UNNAMEABLE) for m in rows_here) and ac in named:
            out[ac] = f"declared `unnameable`: {row['reason']}"
    for ac, mutants in testplan_rows_by_criterion(text).items():
        paths = [p for m in mutants for p in _MUTANT_PATH_RE.findall(m)]
        if paths and all(is_test_path(p) for p in paths):
            out.setdefault(ac.upper(),
                           "the plan row names only test code, so no production revert "
                           "can move it")
    raw = (sdlc_md.extract_field(text, EXEMPT_FIELD) or "").strip()
    if raw:
        ids = [m.upper() for m in _AC_TOKEN_RE.findall(raw)]
        reason = _AC_TOKEN_RE.sub("", raw).strip(" ,;-").strip()
        if ids and len(_reason_substance(reason)) >= 12:
            for ac in ids:
                out.setdefault(ac, f"declared exemption: {reason}")
    return out


#: Every environment variable that can point git at a different repository, index, object
#: store, namespace or path prefix. The FULL list rather than the three-name partial the other
#: read-only callers here carry, and the difference is the reason: they misreport when an escape
#: gets through, this one writes another repository's bytes into a production file.
#: `tools/tests/test_skill_tests_env.py` holds this copy equal to the one every other copy is
#: pinned to, so it cannot drift on its own.
_REPO_LOCATING_GIT_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)


def _git_env() -> dict:
    """The environment a git call here must run under.

    `git -C <path>` does NOT override an inherited repo-locating variable, and git hooks export
    them - this repository's own hooks run this code. Without the drop, `git show <ref>:<path>`
    answers for whatever the environment names, and this check then writes those bytes into the
    unit's production file. Reading the wrong repository is a false verdict; writing it is data
    loss, which is why the whole list goes rather than the usual three.
    """
    return {k: v for k, v in os.environ.items() if k not in _REPO_LOCATING_GIT_VARS}


#: `_base_blob` could not answer at all - distinct from "the path did not exist at that ref".
class _BaseUnreadable(RuntimeError):
    """Git could not be asked what `rel` was at `ref`."""


def _base_blob(root: Path, ref: str, rel: str) -> bytes | None:
    """The bytes of `rel` at `ref`, or None when the path genuinely did not exist there.

    ABSENT AND UNREADABLE ARE DIFFERENT ANSWERS, and reading the second as the first is how
    this check came to DELETE a production file and then pass the unit. Every git failure -
    a workspace nested below the repository root, so `show` exits 128 with `path exists, but
    not <rel>`; a timeout; git missing - returned None, which the revert loop reads as "this
    file did not exist at base" and unlinks. The file's real base content would have kept the
    criterion green, so the deletion manufactured the very red the gate is looking for.

    Existence is therefore asked SEPARATELY, of `ls-tree`, and anything that is not a clean
    yes-or-no raises.
    """
    def _git(*args):
        try:
            return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                  timeout=60, env=_git_env())
        except (OSError, subprocess.SubprocessError) as exc:
            raise _BaseUnreadable(f"git could not be run: {exc}") from exc

    listed = _git("ls-tree", "--name-only", "-z", ref, "--", rel)
    if listed.returncode != 0:
        raise _BaseUnreadable(
            f"`git ls-tree {ref} -- {rel}` failed: "
            f"{listed.stderr.decode('utf-8', 'replace').strip() or 'no message'}")
    if not listed.stdout.strip(b"\0").strip():
        return None  # a clean answer: the path is not in that tree
    shown = _git("show", f"{ref}:{rel}")
    if shown.returncode != 0:
        raise _BaseUnreadable(
            f"`git show {ref}:{rel}` failed for a path `ls-tree` says exists: "
            f"{shown.stderr.decode('utf-8', 'replace').strip() or 'no message'}")
    return shown.stdout


def _ref_exists(root: Path, ref: str) -> bool:
    try:
        cp = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "--quiet",
                             f"{ref}^{{commit}}"], capture_output=True, text=True, timeout=30,
                            env=_git_env())
    except (OSError, subprocess.SubprocessError):
        return False
    return cp.returncode == 0


def _purge_pyc(root: Path, rels: list[str]) -> None:
    """Drop cached bytecode for every reverted file's directory.

    A same-length replacement can land inside one filesystem timestamp granule, and CPython
    then reuses the stale `.pyc` - this repository has recorded that false verdict twice, both
    times as a SURVIVED mutant that had never actually run. Delegated to `mutation._purge_bytecode`
    rather than re-implemented, imported here rather than at module scope because `mutation`
    imports this module back.
    """
    try:
        import mutation as _mut  # noqa: PLC0415 - deferred; mutation imports verify_ac back
    except ImportError:  # pragma: no cover - the skill always ships both
        return
    for rel in rels:
        try:
            _mut._purge_bytecode(root / rel)
        except OSError:
            continue


def _guard_signals(restore):
    """Restore the tree on a signal the interpreter CAN handle, then die as it would have.

    A `finally` covers an exception and covers nothing else. A review measured the gap: SIGINT
    restored (Python raises `KeyboardInterrupt`, so the `finally` ran) while **SIGTERM left the
    unit's production change reverted on disk** - and SIGTERM is what `kill`, a CI job timeout
    and a harness cancel all send. The criterion's promise is that a check which dies cannot
    leave the tree reverted, so the signals Python can intercept are intercepted.

    The default disposition is restored and the signal re-raised, so the process still dies the
    way its caller asked. `signal.signal` works only on the main thread; off it, this is a
    no-op and the `finally` remains the whole defence.
    """
    previous: dict = {}

    def handler(signum, _frame):
        restore()
        signal.signal(signum, previous.get(signum) or signal.SIG_DFL)
        os.kill(os.getpid(), signum)

    for sig in (signal.SIGTERM, signal.SIGINT, getattr(signal, "SIGHUP", None)):
        if sig is None:
            continue
        try:
            previous[sig] = signal.signal(sig, handler)
        except (ValueError, OSError, RuntimeError):
            continue  # not the main thread, or the platform has no such signal
    return previous


def _release_signals(previous: dict) -> None:
    """Hand every signal back to whoever owned it before the revert window opened."""
    for sig, prior in previous.items():
        try:
            signal.signal(sig, prior if prior is not None else signal.SIG_DFL)
        except (ValueError, OSError, RuntimeError):
            continue


def revert_check(root, unit: str, base_ref: str | None = None, *,
                 timeout: int = 600, allow_shell: bool = True) -> dict:
    """Revert a unit's production files to `base_ref` and re-run ITS OWN verifiers.

    The question no other lane asks: if the change were removed, would this unit's tests
    notice? A unit can have every criterion green and every declared mutant recorded killed
    over a change no test reaches - because the tests rebuilt the thing under test in a
    fixture, or pinned a construct one step from the defect. A mutant applied to a call site
    dies against a test that never enters the function behind it, and the ledger records that
    as evidence. Measured on RUN-01M0CT8P: deleting BG0593's entire production change left all
    four of its criteria AND all 916 tests in its file green.

    GREEN AFTER THE REVERT IS THE REFUSAL. It is reported per criterion but decided per unit:
    one criterion going red proves the tests reach the change, and demanding it of every
    criterion refuses correct work (see `revert_exemptions`).

    Selector resolution is settled BEFORE the revert, against the intact tree. A criterion
    whose selector names nothing is a property of what the author wrote, not of the reverted
    state, and judging it afterwards would let a revert that breaks collection be read as
    evidence that the tests reached the change.

    The working tree is restored from a BYTE SNAPSHOT in a `finally`, never from HEAD: a
    `git checkout HEAD --` restore destroyed uncommitted work the first time this was built.
    """
    root = Path(root)
    found = sdlc_md.find_by_id(root, unit)
    if not found:
        return {"ok": False, "status": "error", "unit": unit, "criteria": [], "reverted": [],
                "errors": [f"{unit}: no artefact with that id"]}
    path, _kind = found
    text = sdlc_md.read_text_safe(path)
    uid = sdlc_md.norm_id(unit)
    result: dict = {"ok": False, "status": "error", "unit": uid, "path": str(path),
                    "criteria": [], "reverted": [], "errors": [], "base": ""}

    base = str(base_ref or run_state.base_ref(root) or "").strip()
    if not base:
        result["errors"].append(
            f"{uid}: no base ref - the open run recorded none. This check must not invent one: "
            f"a ref nobody owns is the defect, not the fix. Name it with `--base <ref>`")
        return result
    if not _ref_exists(root, base):
        result["errors"].append(f"{uid}: base ref `{base}` does not resolve to a commit here")
        return result
    result["base"] = base

    targets = revert_targets(root, text)
    reported: list[str] = []
    if targets["unresolvable"]:
        reported.append(
            f"{uid}: `Affects` names production path(s) that are not a readable file here - "
            f"{', '.join(targets['unresolvable'])}. Reverting the subset that does resolve "
            f"would test a change nobody described")
    if not targets["production"]:
        reported.append(
            f"{uid}: `Affects` names no production file "
            f"({len(targets['tests'])} test file(s), {len(targets['docs'])} markdown). "
            f"Nothing to revert is not evidence that the tests reach anything, so this is "
            f"REPORTED rather than passed")
    if reported:
        result["status"] = "reported"
        result["errors"] = reported
        return result

    exempt = revert_exemptions(text)
    story_allow_shell = shell_allowed_for(text, allow_shell=allow_shell)
    criteria: list[dict] = []
    to_run: list[tuple] = []
    for block in parse_story(text):
        ac = (block.ac_id or "").upper()
        expr = (block.verifier or "").strip()
        if ac in exempt:
            criteria.append({"ac": ac, "state": "exempt", "why": exempt[ac]})
        elif not expr:
            criteria.append({"ac": ac, "state": "unspecified"})
        elif _is_manual(expr):
            criteria.append({"ac": ac, "state": "manual", "verifier": expr})
        elif selector_resolves(expr, root) is False:
            criteria.append({"ac": ac, "state": "unresolved", "verifier": expr})
        else:
            entry = {"ac": ac, "state": "pending", "verifier": expr}
            criteria.append(entry)
            to_run.append(entry)

    snapshot: dict = {}
    restored = False

    def restore() -> None:
        """Put every snapshotted file back exactly as it was - CONTENT AND MODE.

        The mode is not incidental. A file absent at the base ref is deleted and then recreated
        by `write_bytes`, which applies the process umask: an independent review measured a
        tracked `100755` script coming back `100644` after a SUCCESSFUL run, with the content
        hash identical and `git status` reporting it modified. Every executable file in this
        repository is a script named in some unit's `Affects`, so that is the common case
        rather than an edge one - and this repository's own `repo-writes` lane refuses a commit
        whose run modified a tracked file, so the check would have broken the commit it was
        meant to inform.
        """
        nonlocal restored
        if restored:
            return
        restored = True
        for rel_, (blob_, mode_) in snapshot.items():
            target = root / rel_
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob_)
            try:
                os.chmod(target, mode_)
            except OSError:
                pass
        _purge_pyc(root, targets["production"])

    previous = _guard_signals(restore)
    try:
        for rel in targets["production"]:
            st = (root / rel).stat()
            snapshot[rel] = ((root / rel).read_bytes(), stat.S_IMODE(st.st_mode))
        for rel in targets["production"]:
            try:
                blob = _base_blob(root, base, rel)
            except _BaseUnreadable as exc:
                result["status"] = "reported"
                result["errors"].append(
                    f"{uid}: could not read `{rel}` at {base} - {exc}. REPORTED rather than "
                    f"treated as absent: reading a git failure as `did not exist at base` "
                    f"deletes the file and manufactures the red this gate looks for")
                return result
            if blob is None:
                (root / rel).unlink()
            else:
                (root / rel).write_bytes(blob)
            result["reverted"].append(rel)
        _purge_pyc(root, targets["production"])
        for entry in to_run:
            res = run_verifier(entry["verifier"], timeout, root,
                               allow_shell=story_allow_shell)
            entry["kind"] = res.kind
            if res.ok:
                entry["state"] = "green"
            elif res.kind in ("invalid", "blocked") or res.vacuous:
                # NOT RED. `run_verifier` already distinguishes an expression it could not
                # parse, one the trust boundary refused to execute, and a runner that exited
                # clean having run nothing - and every one of those is a verifier that did not
                # RUN, not a test that noticed the change. Counting them red made a unit whose
                # `Verify:` line was a typo pass the one check that asks whether its tests
                # reach anything. AC5 states the rule for an unresolvable selector; this is the
                # same rule, and the discriminating data was already in hand.
                entry["state"] = "unmeasured"
            else:
                entry["state"] = "red"
    finally:
        restore()
        _release_signals(previous)

    result["criteria"] = criteria
    result["unmeasured"] = [c["ac"] for c in criteria if c["state"] == "unmeasured"]
    counted = [c for c in criteria if c["state"] in ("red", "green")]
    green = [c["ac"] for c in counted if c["state"] == "green"]
    result["green"] = green
    result["red"] = [c["ac"] for c in counted if c["state"] == "red"]
    result["exempt"] = [c["ac"] for c in criteria if c["state"] == "exempt"]
    result["unresolved"] = [c["ac"] for c in criteria if c["state"] == "unresolved"]
    if counted and not result["red"]:
        result["status"] = "refused"
        result["errors"].append(
            f"{uid}: every measurable criterion stayed GREEN with "
            f"{', '.join(targets['production'])} reverted to {base} - "
            f"{', '.join(green)}. A test that passes without the change never reached it")
        return result
    if not counted:
        # An ABSENCE must not read as a pass - the same rule the empty-`Affects` branch above
        # enforces, one step further in. Nothing was measured here, and the reason is that the
        # selectors name nothing rather than that the criteria are exempt. Reported: a unit
        # whose every verifier is dead would otherwise come back green from the one check that
        # exists to ask whether its verifiers reach anything at all.
        # NOTHING WAS MEASURED, so there is nothing to pass. The empty-`Affects` branch above
        # already states the argument - an absence is not evidence that the tests reach
        # anything - and it applies here identically, including when every criterion is
        # EXEMPT: one self-authored `Revert-check-exempt` line listing every id would otherwise
        # turn the gate off for a whole unit and print PASSES. Reported (exit 3), never
        # REFUSED (exit 1): US0671 AC3's law is that a declared exemption must not refuse the
        # unit, and reporting that nothing could be measured is not a refusal.
        result["status"] = "reported"
        result["errors"].append(
            f"{uid}: nothing measurable - {len(result['exempt'])} exempt, "
            f"{len(result['unresolved'])} unresolvable selector(s), "
            f"{len(result['unmeasured'])} verifier(s) that did not run. No criterion was "
            f"executed, so this is REPORTED rather than passed")
        return result
    result["ok"] = True
    result["status"] = "pass"
    return result


def cmd_revert_check(args: argparse.Namespace) -> int:
    res = revert_check(args.root, args.unit, args.base, timeout=args.timeout)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        for line in res.get("errors", []):
            print(f"revert-check: {line}")
        for c in res.get("criteria", []):
            extra = c.get("why") or c.get("verifier") or ""
            print(f"  {c['ac']:<6} {c['state']:<11} {extra}")
        if res.get("note"):
            print(f"revert-check: {res['note']}")
        if res.get("ok"):
            print(f"revert-check: {res['unit']} PASSES - "
                  f"{len(res.get('red', []))} criterion/criteria go red without the change")
    if res["status"] == "reported":
        return 3
    return 0 if res["ok"] else 1


# -----------------------------------------------------------------------------
# Derived `Verification depth`
# -----------------------------------------------------------------------------

#: The delimiters around the DERIVED half of `Verification depth`. Visible rather than an HTML
#: comment: a fact a reader cannot see is one nobody checks, and this is the field a reviewer
#: reads first to decide how hard to look.
DERIVED_OPEN = "[[derived:"
DERIVED_CLOSE = "]]"
_DERIVED_RE = re.compile(r"\s*\[\[derived:.*?\]\]", re.S)
_DEPTH_LINE_RE = re.compile(r"^(>\s*\*\*Verification depth:\*\*[ \t]*)(.*)$", re.M)
#: The start of ANY blockquote field, used to tell a wrapped continuation line from the next
#: field. `_DEPTH_LINE_RE` is line-anchored, so without this a field that wraps keeps its
#: hand-typed counts on line two beside a derived span that contradicts them.
_FIELD_START_RE = re.compile(r"^>\s*\*\*[^*]+:\*\*")
#: The span's own contents, split into the facts and the fingerprint that seals them.
_DERIVED_SPAN_RE = re.compile(
    r"\[\[derived:(?P<facts>.*?)(?:\|\s*fp\s*(?P<fp>[0-9a-f]{6,}))?\s*\]\]", re.S)
#: How the derived half is regenerated. Named in the refusal, because a refusal with no stated
#: escape would leave a batch's own depth fields uncorrectable and its tree uncommittable.
DEPTH_REGEN_CMD = "verify_ac.py depth --unit {unit} --write"


def depth_fingerprint(facts: str) -> str:
    """The seal over a derived span's facts.

    A FINGERPRINT rather than a re-derivation, and that is the load-bearing choice. Re-deriving
    would need the mutation ledger, which lives in gitignored `sdlc-studio/.local/` - so the
    guard would report every unit as unsupported in a fresh clone and refuse the whole corpus.
    This repository has already shipped a repair with exactly that shape once. The seal travels
    in the artefact, so the check needs nothing but the file in front of it.
    """
    import hashlib  # noqa: PLC0415 - local: only the seal needs it
    return hashlib.sha256(" ".join(facts.split()).encode("utf-8")).hexdigest()[:12]


def depth_edit_faults(paths) -> list[dict]:
    """Units whose DERIVED span no longer matches its own seal.

    Scoped to fields that CARRY a span. A hand-authored `Verification depth` with no derived
    half is the pre-existing state of most of this corpus and is left alone - a guard that
    refused those would refuse 600 artefacts on the commit that shipped it, and a guard like
    that gets switched off rather than satisfied.
    """
    out: list[dict] = []
    for path in paths:
        path = Path(path)
        text = sdlc_md.read_text_safe(path)
        if not text:
            continue
        match = _DEPTH_LINE_RE.search(text)
        if not match:
            continue
        spans = list(_DERIVED_SPAN_RE.finditer(match.group(2)))
        if not spans:
            continue  # no derived half: nothing was sealed, so nothing can have been broken
        unit = sdlc_md.extract_record_id(path.stem) or path.stem
        # EVERY span is judged, not the first. A field carries exactly ONE derived half, so a
        # second one is an edit inside the delimiters by construction - and judging only
        # `search()`'s first hit made the verdict depend on WHERE the forged span was placed.
        if len(spans) > 1:
            why = (f"its field carries {len(spans)} derived halves and a field has exactly one, "
                   f"so all but the first are hand-added")
            actual = depth_fingerprint(spans[0].group("facts") or "")
            claimed = spans[0].group("fp") or ""
        else:
            span = spans[0]
            actual = depth_fingerprint(span.group("facts") or "")
            claimed = span.group("fp")
            if claimed == actual:
                continue
            why = ("its derived half carries no fingerprint" if not claimed
                   else f"its derived half was edited by hand (seal {claimed}, contents hash {actual})")
        out.append({"unit": unit, "path": str(path), "claimed": claimed or "", "actual": actual,
                    "why": f"{unit}: {why}. The counted half is DERIVED output - regenerate it "
                           f"with `{DEPTH_REGEN_CMD.format(unit=unit)}`, do not retype it. "
                           f"Run it in the workspace whose mutation ledger holds this unit's "
                           f"verdicts: the ledger is gitignored, so regenerating without it "
                           f"is refused rather than allowed to erase what is recorded here"})
    return out


def _entry_point_split(root, text: str) -> dict:
    """How many of a unit's criteria enter the SHIPPED entry point, and how many run in-process.

    Derived by the detector `lane-check` already uses, per criterion and scoped to the node the
    selector names. CR0548's motivating defect was a `Verification depth` claiming shipped-CLI
    coverage that did not exist, and that claim is PROSE: deriving only the mutation counts
    would leave it standing in the half no tool touches.
    """
    root = Path(root)
    through = in_process = undetermined = unlocatable = 0
    for block in parse_story(text):
        expr = (block.verifier or "").strip()
        if not expr or _is_manual(expr):
            continue
        node = next((tok.rsplit("::", 1)[-1] for tok in expr.split() if "::" in tok), "")
        targets = [root / t for t in _lane_test_paths(expr)]
        targets = [t for t in targets if t.exists()]
        if not targets:
            unlocatable += 1
            continue
        # NODE-SCOPED ONLY. `_enters_the_lane` falls back to reading the WHOLE FILE when the
        # named node cannot be isolated, and that fallback is right for `lane_check`, which is
        # per-unit and report-only. Here it would be a per-criterion COUNT presented as derived
        # fact: measured over this corpus, 185 of 311 through-CLI counts came from the fallback
        # rather than from the criterion's own test. CR0548 was raised on a prose claim of
        # shipped-CLI coverage that did not exist, and deriving the same claim from a detector
        # that never read the criterion's node would re-manufacture it with the authority of
        # derivation. What cannot be determined is REPORTED as undetermined.
        scoped = [_node_source(sdlc_md.read_text_safe(t), node) for t in targets] if node else []
        if not node or not any(s is not None for s in scoped):
            undetermined += 1
        elif any(_enters_the_lane(t, node) for t in targets):
            through += 1
        else:
            in_process += 1
    return {"located": through + in_process + undetermined, "through_cli": through,
            "in_process": in_process, "undetermined": undetermined,
            "unlocatable": unlocatable}


def _unit_ledger_rows(root, uid: str) -> list[dict]:
    """Every LIVE ledger mutant recorded against `uid`, whether or not a plan row claims it.

    Read independently of the plan join, because the two answer different questions and the
    field was asserting one from the other: a unit with no `## Test Plan` joined to nothing and
    was rendered `EVIDENCE ABSENT - the ledger holds no executed row`, which is a claim about
    the LEDGER derived from the absence of a PLAN. Measured over this corpus, 484 of the 561
    units carrying a depth field have no test plan, so that was the majority case - and it hid
    registered SURVIVORS, which is the one thing the gate exists to surface.
    """
    import mutation as _mut  # noqa: PLC0415 - deferred; mutation imports verify_ac back
    out: list[dict] = []
    try:
        entries = _mut.ledger_entries(root)
    except Exception:  # noqa: BLE001 - an unreadable ledger is reported, never raised here
        return out
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        for m in entry.get("mutants", []) or []:
            if isinstance(m, dict) and m.get("unit") == uid and not m.get("withdrawn"):
                out.append({"criterion": m.get("criterion"), "row": m.get("row"),
                            "verdict": m.get("verdict"), "target": entry.get("target")})
    return out


def depth_facts(root, unit: str) -> dict:
    """Every COUNT that belongs in a `Verification depth`, read from the artefact and the ledger.

    A field nobody types cannot lie, and this one lied on five of six units in a single batch
    while being the field a reviewer reads first. Counts come from `mutation.plan_execution`,
    which joins the plan's rows to the ledger on the criterion and row recorded at
    registration - never on the mutant's prose.

    An ABSENT ledger and a ledger of noughts are different facts and are reported differently:
    a reader who cannot tell them apart cannot judge the unit.
    """
    import mutation as _mut  # noqa: PLC0415 - deferred; mutation imports verify_ac back
    root = Path(root)
    found = sdlc_md.find_by_id(root, unit)
    if not found:
        return {"ok": False, "unit": unit, "errors": [f"{unit}: no artefact with that id"]}
    path, _kind = found
    text = sdlc_md.read_text_safe(path)
    join = _mut.plan_execution(root, unit)
    rows = join.get("rows", []) or []
    verdicts = [str(r.get("verdict") or "") for r in rows]
    uid = sdlc_md.norm_id(unit)
    facts = {
        "ok": True,
        "unit": uid,
        "path": str(path),
        "criteria": sdlc_md.count_acs(text),
        "rows": len(rows),
        "killed": verdicts.count("killed"),
        "survived": verdicts.count("survived"),
        "equivalent": verdicts.count(_mut.EQUIVALENT_VERDICT),
        "unnameable": verdicts.count("unnameable"),
        "not_run": [{"ac": r["ac"], "row": r.get("row", 0)} for r in rows
                    if r.get("verdict") == _mut.NOT_RUN],
        "retracted": len(join.get("retracted") or []),
        # THREE DIFFERENT FACTS, and conflating any two of them is the defect this field
        # exists to remove. `ledger_absent` once meant "nothing executed", which made a unit
        # whose every row was declared-but-unrun read as one with no ledger at all - and that
        # is the single case where a reader most needs the unrun rows NAMED.
        "plan_absent": not rows,
        "ledger_absent": not _unit_ledger_rows(root, uid),
        "ledger_rows": _unit_ledger_rows(root, uid),
        "entry_point": _entry_point_split(root, text),
        "errors": join.get("errors", []) or [],
    }
    facts["executed"] = facts["killed"] + facts["survived"] + facts["equivalent"]
    return facts


def render_depth(facts: dict) -> str:
    """The derived half, as one line of readable prose. Never a claim the ledger does not hold.

    THE ROW ARITHMETIC CLOSES: killed + survived + equivalent + unnameable + not-run equals the
    declared row count, always. An earlier cut counted only killed and survived as executed, so
    a plan whose second row was ruled `equivalent` rendered `plan rows 2; executed 1` with
    nothing saying where the other row went - a reader cannot audit a sum that does not add up.
    """
    ep = facts["entry_point"]
    parts = [f"criteria {facts['criteria']}"]
    if facts["plan_absent"]:
        parts.append("NO TEST PLAN - no row was declared, so nothing was declared to execute")
    else:
        parts.append(f"plan rows {facts['rows']}")
    if facts["ledger_absent"]:
        parts.append("EVIDENCE ABSENT - the mutation ledger holds no entry for this unit, "
                     "which is not the same fact as nought killed")
    else:
        parts += [f"executed {facts['executed']}", f"killed {facts['killed']}",
                  f"survived {facts['survived']}"]
        if facts["equivalent"]:
            parts.append(f"ruled equivalent {facts['equivalent']}")
    # NAMED WHATEVER THE LEDGER HOLDS. This sat inside the `else` above, so a unit whose every
    # declared row was unrun - the single case where a reader most needs the row ids - was the
    # single case that printed EVIDENCE ABSENT and named none of them.
    if facts["not_run"]:
        named = ", ".join(f"{r['ac']} row {r['row']}" for r in facts["not_run"])
        parts.append(f"NOT RUN {len(facts['not_run'])} ({named})")
    elif not facts["plan_absent"]:
        parts.append("not-run 0")
    if not facts["ledger_absent"]:
        if facts["plan_absent"]:
            # A ledger holding rows no plan claims. Reported rather than folded into the counts
            # above, because those counts are per PLAN ROW and there are none.
            live = facts["ledger_rows"]
            surv = sum(1 for r in live if r.get("verdict") == "survived")
            parts.append(f"ledger holds {len(live)} registered mutant(s) joined to no plan row"
                         + (f", {surv} SURVIVED" if surv else ""))
    if facts["unnameable"]:
        parts.append(f"declared unnameable {facts['unnameable']}")
    if facts["retracted"]:
        parts.append(f"retracted {facts['retracted']}")
    parts.append(f"entry point {ep['through_cli']} of {ep['located']} criteria through the "
                 f"shipped CLI, {ep['in_process']} in-process")
    if ep["undetermined"]:
        parts.append(f"{ep['undetermined']} undetermined (the named node could not be isolated)")
    if ep["unlocatable"]:
        parts.append(f"{ep['unlocatable']} with no locatable test file")
    facts_line = "; ".join(parts)
    return f"{DERIVED_OPEN} {facts_line} | fp {depth_fingerprint(facts_line)} {DERIVED_CLOSE}"


def depth_field_value(current: str, derived: str) -> str:
    """Rebuild the field's value with a fresh derived half.

    The author's judgement - the tier, and the honest statement of what was deliberately not
    covered - is the part no tool can supply, so it is carried through BYTE FOR BYTE rather
    than re-rendered. Only the delimited span is replaced.
    """
    stripped = _DERIVED_RE.sub("", current).strip()
    tier, sep, rest = stripped.partition(" ")
    tail = f" {rest.strip()}" if sep and rest.strip() else ""
    return f"{tier} {derived}{tail}" if tier else derived


def write_depth(root, unit: str) -> dict:
    """Derive the field and write it back, or report why it cannot be written."""
    facts = depth_facts(root, unit)
    if not facts.get("ok"):
        return facts
    path = Path(facts["path"])
    text = sdlc_md.read_text_safe(path)
    derived = render_depth(facts)
    match = _DEPTH_LINE_RE.search(text)
    if not match:
        facts["ok"] = False
        facts["errors"] = list(facts["errors"]) + [
            f"{facts['unit']}: no `> **Verification depth:**` field to derive into - the tier "
            f"and the judgement half are the author's, so this command amends a field rather "
            f"than inventing one"]
        return facts
    if not _DERIVED_RE.sub("", match.group(2)).strip():
        facts["ok"] = False
        facts["errors"] = list(facts["errors"]) + [
            f"{facts['unit']}: the `Verification depth` field carries no tier, so there is "
            f"nothing to derive INTO. Writing the derived span alone would leave `{DERIVED_OPEN}` "
            f"standing where the tier belongs - a field that parses as a tier while naming none, "
            f"which is worse than the unparseable field it replaced"]
        return facts
    tail = text[match.end():].lstrip("\n").splitlines()
    if tail and tail[0].lstrip().startswith(">") and not _FIELD_START_RE.match(tail[0]):
        facts["ok"] = False
        facts["errors"] = list(facts["errors"]) + [
            f"{facts['unit']}: the `Verification depth` field WRAPS onto a second line, and "
            f"only its first line would be rewritten - the continuation's hand-typed counts "
            f"would stand beside a derived span contradicting them. Join the field onto one "
            f"line, then regenerate"]
        return facts
    prior = _DERIVED_SPAN_RE.search(match.group(2))
    if facts["ledger_absent"] and prior and "EVIDENCE ABSENT" not in (prior.group("facts") or ""):
        # REFUSE rather than overwrite. The ledger lives in gitignored `sdlc-studio/.local/`,
        # so a fresh clone, a CI runner and every review worktree have none - and rewriting a
        # recorded set of counts as EVIDENCE ABSENT there, at exit 0 and in silence, destroys
        # the evidence rather than reporting its absence. The one thing this command must never
        # do is make a unit's record LESS true than it found it.
        facts["ok"] = False
        facts["errors"] = list(facts["errors"]) + [
            f"{facts['unit']}: this workspace has no mutation ledger, and the field already "
            f"carries derived counts. Writing here would replace them with EVIDENCE ABSENT - "
            f"that is the ledger missing HERE, not the evidence being missing. Run this where "
            f"the ledger lives, or run the mutants first"]
        return facts
    new_value = depth_field_value(match.group(2), derived)
    text = text[:match.start()] + match.group(1) + new_value + text[match.end():]
    path.write_text(text, encoding="utf-8")
    facts["derived"] = derived
    facts["written"] = True
    return facts


def cmd_depth_check(args: argparse.Namespace) -> int:
    root = Path(args.root)
    units = walk_units(unit_dirs(root, root / "sdlc-studio" / "stories"))
    faults = depth_edit_faults(units)
    for f in faults:
        print(f"depth-check: {f['why']}", file=sys.stderr)
    if not faults:
        print(f"depth-check: {len(units)} unit(s), every derived half matches its own seal")
    return 1 if faults else 0


def cmd_depth(args: argparse.Namespace) -> int:
    facts = write_depth(args.root, args.unit) if args.write else depth_facts(args.root, args.unit)
    if facts.get("ok") and not args.write:
        facts["derived"] = render_depth(facts)
    if args.format == "json":
        print(json.dumps(facts, indent=2))
    else:
        for line in facts.get("errors", []):
            print(f"depth: {line}")
        if facts.get("derived"):
            print(facts["derived"])
    return 0 if facts.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for the run and report subcommands."""
    p = argparse.ArgumentParser(
        prog="verify_ac.py",
        description="Execute acceptance-criterion verifiers and update Verified state.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Run verifiers and update story files")
    r.add_argument("--dir", default="sdlc-studio/stories", help="Stories directory")
    # One selector at a time. The batch forms below verify a sprint's units in ONE process
    # instead of a whole-workspace run or one invocation per story.
    sel = r.add_mutually_exclusive_group()
    sel.add_argument("--story", "--file", dest="story",
                     help="Single story file - or a story ID (an id-shaped value that is "
                          "not a real path resolves under --dir)")
    sel.add_argument("--id", help="Single story by id, e.g. US0001 (resolved under --dir)")
    sel.add_argument("--ids", action="append", metavar="US0001,US0003",
                     help="Scope the run to these story ids (comma-separated, repeatable, "
                          "case-insensitive); an id with no story file is an error")
    sel.add_argument("--worklist", metavar="PATH",
                     help="Scope the run to the ids a worklist/tranche file names (markdown "
                          "bullets and `#` comment lines tolerated, repeats de-duplicated)")
    sel.add_argument("--from-run", dest="from_run", action="store_true",
                     help="Scope the run to the story units of the open run's approved "
                          "batch; refuses when no run is open")
    r.add_argument("--dry-run", action="store_true", help="Do not modify story files")
    r.add_argument("--fresh", action="store_true",
                   help="rebuild the report from this run only (default merges into it)")
    r.add_argument("--batch", action="store_true",
                   help="run jest once and resolve jest verifiers from the cached result")
    r.add_argument("--timeout", type=int, default=120, help="Per-verifier timeout in seconds")
    r.add_argument("--no-shell", dest="no_shell", action="store_true",
                   help="block shell-backed verifiers (shell/eval/http); run only structured "
                        "DSL verbs - for CI over less-trusted content")
    r.add_argument("--allow-external", dest="allow_external", action="store_true",
                   help="run shell verifiers even on stories stamped `Provenance: external` "
                        "(off by default - the trust boundary)")
    r.add_argument("--allow-shell-fallback", dest="allow_shell_fallback", action="store_true",
                   help="legacy: treat an unrecognised Verify line as a shell command "
                        "(off by default - unrecognised lines are invalid verifiers)")
    r.add_argument(
        "--report",
        default="sdlc-studio/.local/verify-report.json",
        help="Report output path",
    )
    r.add_argument(
        "--root", "--repo-root",
        dest="root",
        default=".",
        help="Repository root used as cwd for verifier commands (--repo-root is a legacy "
             "alias); binds the family-standard `root` dest so a global --root before the "
             "verb and the flag after it resolve to one root, never diverge",
    )
    r.set_defaults(func=cmd_run)

    st = sub.add_parser("stamps", help="Flag stamped-green ACs whose verifier selects nothing")
    st.add_argument("--root", default=".", help="Repo root --dir is resolved under")
    st.add_argument("--dir", default="sdlc-studio/stories", help="Stories directory")
    st.add_argument("--story", "--file", dest="story", help="Single story or bug file")
    st.add_argument("--bugs", action="store_true",
                    help="also check sdlc-studio/bugs, which walk_stories does not reach")
    st.set_defaults(func=cmd_stamps)

    ln = sub.add_parser("lint", help="Advisory: flag non-DSL / mis-written Verify lines")
    ln.add_argument("--root", default=".", help="Repo root --dir is resolved under")
    ln.add_argument("--dir", default="sdlc-studio/stories", help="Stories directory")
    ln.add_argument("--story", "--file", dest="story", help="Single story file (overrides --dir)")
    ln.add_argument("--bugs", action="store_true",
                    help="scan sdlc-studio/bugs too, as `stamps --bugs` does - without it a "
                         "shared selector can be parked in a bug where the scan never looked")
    ln.add_argument("--ratchet", action="store_true",
                    help="REFUSE a duplicate-verifier group the baseline does not record, and a "
                         "recorded group that is no longer duplicated. The tolerated SET may "
                         "only shrink, so a fixed group cannot be spent to admit a new one")
    ln.add_argument("--stamp", action="store_true",
                    help="(with --ratchet) record the current groups as the tolerated set. Each "
                         "entry is minted with an EMPTY reason and the ratchet refuses it until "
                         "a human writes one")
    ln.set_defaults(func=cmd_lint)

    tc = sub.add_parser("ts-check", help="Validate a test-spec's AC Coverage Matrix")
    tc.add_argument("--spec", required=True, help="Path to the test-spec file")
    tc.add_argument("--verify-report", dest="verify_report",
                    help="cross-check the matrix against this verify-report.json")
    tc.add_argument("--format", choices=("text", "json"), default="text")
    tc.set_defaults(func=cmd_ts_check)

    et = sub.add_parser("epic-ts", help="Require an epic to have a ts-check-passing test-spec")
    et.add_argument("--epic", required=True, help="Epic id, e.g. EP0001")
    et.add_argument("--root", default=".")
    et.add_argument("--format", choices=("text", "json"), default="text")
    et.set_defaults(func=cmd_epic_ts)

    sc = sub.add_parser("scaffold-matrix",
                        help="Emit an epic's AC Coverage Matrix pre-filled (one row per AC)")
    sc.add_argument("--epic", required=True, help="Epic id, e.g. EP0001")
    sc.add_argument("--root", default=".")
    sc.add_argument("--out", help="Write the matrix here instead of stdout")
    sc.set_defaults(func=cmd_scaffold)

    tp = sub.add_parser("testplan", help="Derive a unit's test plan from its criteria")
    tp.add_argument("action", choices=["derive"])
    tp.add_argument("--unit", required=True)
    tp.add_argument("--dry-run", action="store_true",
                    help="report what would be written, and write nothing")
    tp.add_argument("--root", default=".")
    tp.set_defaults(func=cmd_testplan)
    cs = sub.add_parser("corpus-scan",
                        help="Count the three blind states across an artefact class")
    cs.add_argument("--kind", default="bugs", choices=("bugs", "stories", "change-requests"))
    cs.add_argument("--root", default=".")
    cs.set_defaults(func=cmd_corpus_scan)
    lc = sub.add_parser("lane-check",
                        help="Advisory: criteria whose verifiers never enter the shipped "
                             "entry point")
    lc.add_argument("--ids", help="scope to these unit ids (comma-separated)")
    lc.add_argument("--root", default=".")
    lc.set_defaults(func=cmd_lane_check)

    rc = sub.add_parser("revert-check",
                        help="Revert a unit's production files to the run's base ref and "
                             "re-run its own verifiers - green is the refusal")
    rc.add_argument("--unit", required=True)
    rc.add_argument("--base", help="base ref to revert to (default: the open run's)")
    rc.add_argument("--timeout", type=int, default=600)
    rc.add_argument("--format", choices=("text", "json"), default="text")
    rc.add_argument("--root", default=".")
    rc.set_defaults(func=cmd_revert_check)

    dp = sub.add_parser("depth",
                        help="Derive the counted half of a unit's `Verification depth` from "
                             "the mutation ledger")
    dp.add_argument("--unit", required=True)
    dp.add_argument("--write", action="store_true",
                    help="amend the field in place, keeping the author's judgement half")
    dp.add_argument("--format", choices=("text", "json"), default="text")
    dp.add_argument("--root", default=".")
    dp.set_defaults(func=cmd_depth)

    dc = sub.add_parser("depth-check",
                        help="Refuse a hand-edit inside the derived half of a "
                             "`Verification depth`")
    dc.add_argument("--root", default=".")
    dc.set_defaults(func=cmd_depth_check)

    rep = sub.add_parser("report", help="Print the latest verification report")
    rep.add_argument(
        "--report",
        default="sdlc-studio/.local/verify-report.json",
        help="Report path",
    )
    rep.add_argument("--format", choices=("text", "json"), default="text")
    rep.set_defaults(func=cmd_report)

    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to, not on the cwd the run happened to start in. Per-verb resolution is
    # left in place; this makes the anchor true of a verb that forgets to ask.
    args.root = str(resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
