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

    in_fence = False
    fence = ""
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        # A fenced code block inside an AC is an ILLUSTRATION, not a directive: a
        # `- **Verify:**` line shown as an example inside ``` must never be picked up and
        # executed. Skip fenced contents (the fence does not end the current AC block).
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_fence, fence = True, stripped[:3]
            continue
        if in_fence:
            if stripped.startswith(fence):
                in_fence = False
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
# Only `go` and `jest` need a counter-signature at all, because only they report PER UNIT and
# can say "nothing here" beside a real result. `unittest` and `pytest` each print exactly one
# summary, and their empty and non-empty forms are mutually exclusive ("Ran 0 tests" vs
# "Ran 9 tests"; "no tests ran" vs "3 passed, 90 deselected"), so they are judged on their own
# line with no veto.

# unittest: one summary line, exclusive.
_UNITTEST_ZERO = re.compile(r"^Ran 0 tests? in ", re.M)
# pytest: one summary line, exclusive. `--collect-only` reports "collected".
_PYTEST_ZERO = re.compile(r"^(?:=+ )?no tests (?:ran|collected)\b", re.M | re.I)
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
                or _jest_ran_nothing(blob))


_VACUOUS_MSG = ("verifier exited 0 but ran NO tests - a filter that matches nothing "
                "(renamed or deleted test, stale -k/-run pattern) proves nothing. "
                "Re-point the Verify line at a test that exists.")


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
        return VerifierResult(
            ok=(result.returncode == 0 and not vacuous),
            kind=kind,
            exit_code=result.returncode,
            stdout=stdout,
            stderr=(f"{stderr}\n{_VACUOUS_MSG}".strip() if vacuous else stderr),
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
    # argv is `pytest -q <target> [-k pat]`. Split the file target from the -k filter.
    target = next((a for a in argv[1:] if "::" in a or a.endswith(".py")), None)
    if target is None:
        return None
    test_file = target.split("::", 1)[0]
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
        expr = " ".join(
            tok if tok in ("and", "or", "not", "(", ")")
            else str(tok.lower() in low) for tok in tokens)
        try:
            if eval(expr):  # noqa: S307 - operands are only True/False/and/or/not/parens
                return True
        except (SyntaxError, NameError):
            return True  # an expression we cannot evaluate: assume it selects, never false-dead
    return False


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
    for p in paths:
        if not p.exists():
            continue
        text = sdlc_md.read_text_safe(p)  # a corrupt story must not abort the duplicate scan
        rec = sdlc_md.extract_record_id(p.stem) or p.stem
        for block in parse_story(text):
            if not block.verifier:
                continue
            expr = " ".join(block.verifier.split())
            if _is_manual(expr):
                continue
            seen.setdefault(expr, []).append(f"{rec} {block.ac_id}")
    return [{"verifier": expr, "acs": acs}
            for expr, acs in sorted(seen.items()) if len(acs) > 1]


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


def resolve_jest_from_cache(verifier: str, asserts: list[dict]) -> VerifierResult | None:
    """Resolve a `jest <pattern>` verifier against cached assertions, mirroring `jest -t`:
    pass iff >=1 assertion name contains the pattern and all matching pass. None when the verb is
    not jest or nothing matches -> the caller runs the authoritative per-AC subprocess."""
    head, _, tail = verifier.strip().partition(" ")
    if head.lower() != "jest" or not tail:
        return None
    pat = tail.strip().strip('"\'')
    matches = [a for a in asserts if pat in a["name"]]
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


def verify_story(
    story_path: Path,
    dry_run: bool,
    timeout: int,
    repo_root: Path,
    jest_cache: list[dict] | None = None,
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
    provenance = (sdlc_md.extract_field(text, "Provenance") or "").strip().lower()
    story_allow_shell = allow_shell and (allow_external or provenance != "external")
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


def walk_stories(stories_dir: Path) -> Iterable[Path]:
    """Yield every US story file in a directory, sorted, EXCLUDING companion docs. Matches the
    shared `sdlc_md.iter_artifact_files` discipline: a file counts only when its stem resolves
    to a `US` record id and it does not carry a declared companion suffix (a
    `US0001-login-consultations.md` note must not be verified - executing its quoted example
    `Verify:` lines runs arbitrary shell from a non-story document). Case-insensitive."""
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
        if sdlc_md.norm_id(rec).startswith("US"):
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
    "that story had nothing to fail". A batch source that legitimately carries other unit
    types (`--worklist`, `--from-run`) has its non-story ids dropped and SAID so; ids typed
    by hand into `--ids` are taken literally, so a bug id there is an unresolved story.
    """
    flag = scope_flag(args)
    ids, refusal = _scope_ids(args, repo_root)
    if refusal:
        return [], refusal
    if flag != "--ids":
        stories = [i for i in ids if i.startswith("US")]
        skipped = len(ids) - len(stories)
        if skipped:
            print(f"{flag}: {skipped} non-story id(s) skipped - `run` verifies stories",
                  file=sys.stderr)
        ids = stories
    by_id: dict[str, Path] = {}
    for p in walk_stories(under_root(repo_root, args.dir)):
        by_id.setdefault(sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or ""), p)
    missing = [i for i in ids if i not in by_id]
    if missing:
        return [], (f"{flag} names {len(missing)} id(s) with no story file under "
                    f"{args.dir}: {', '.join(missing)}")
    if not ids:
        return [], (f"{flag} resolved to no stories - refusing to fall back to a "
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
    elif getattr(args, "id", None):  # resolve --id USNNNN under --dir (case-insensitive)
        target = sdlc_md.norm_id(args.id)
        matches = [p for p in walk_stories(under_root(repo_root, args.dir))
                   if sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or "") == target]
        if not matches:
            print(f"no story file for id {args.id} under {args.dir}", file=sys.stderr)
            return 2
        paths = matches[:1]
    else:
        paths = list(walk_stories(under_root(repo_root, args.dir)))

    if not paths:
        print("no stories found", file=sys.stderr)
        return 2

    # with --batch, run jest once and resolve jest verifiers from the cached assertions
    # instead of a cold `jest -t` start per AC (a field sprint measured ~48 cold starts / 70s).
    jest_cache = jest_batch_cache(repo_root, args.timeout) if getattr(args, "batch", False) else None
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

    return 1 if overall_fail > 0 else 0


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
    for d in dupes:
        flagged += 1
        print(f"duplicate verifier across {len(d['acs'])} ACs: {d['verifier']!r}\n"
              f"    -> {', '.join(d['acs'])}\n"
              f"    -> two ACs sharing a selector cannot both discriminate - a regression in "
              f"either fails both, and neither says which")
    print(f"verify-lint: {flagged} suspicious Verify line(s) (advisory)")
    if refused:
        print(f"verify-lint: {refused} markdown-only verifier(s) REFUSED on a story still "
              f"being authored - each proves a sentence was written, not that the behaviour "
              f"exists", file=sys.stderr)
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
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
