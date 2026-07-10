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
from lib import sdlc_md  # noqa: E402

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
        if vm and current.verify_line is None:
            current.verify_line = i
            current.verifier = vm.group(2).strip()
            current.insert_after = i
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
        kind, cmd = _build_command(expr, allow_fallback=allow_fallback)
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
        return VerifierResult(
            ok=(result.returncode == 0),
            kind=kind,
            exit_code=result.returncode,
            stdout=result.stdout[-4000:],
            stderr=result.stderr[-4000:],
            duration_ms=duration,
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


def _build_command(expr: str, allow_fallback: bool = False) -> tuple[str, list[str] | str]:
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
        # grep <regex> <path_glob>
        try:
            args = shlex.split(tail)
        except ValueError as e:
            raise ValueError(f"grep: {e}")
        if len(args) < 2:
            raise ValueError("grep: expected <regex> <path>")
        pattern, *paths = args
        tool = "rg" if shutil.which("rg") else "grep"
        if tool == "rg":
            return "grep", ["rg", "-q", pattern] + paths
        return "grep", ["grep", "-rqE", pattern] + paths
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
    manual: int = 0
    passed: list[str] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)
    changed: int = 0
    flips: list[dict] = field(default_factory=list)  # pending/applied (ac, old_state, new_state)


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
    text = story_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    blocks = parse_story(text)
    report = StoryReport(path=str(story_path), ac_count=len(blocks))
    provenance = (sdlc_md.extract_field(text, "Provenance") or "").strip().lower()
    story_allow_shell = allow_shell and (allow_external or provenance != "external")
    pending: list = []  # (block, new_state) - applied bottom-up after the loop

    for block in blocks:
        # No verifier, or a human-checked AC authored as `Verify: manual ...` -> count it MANUAL,
        # never shell it out. Shelling prose timed out and reported "failed" instead of "manual"
        #: "manual/unverified" is honest; "failed" is not.
        if block.verifier is None or _is_manual(block.verifier):
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
                }
            )
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
            "passed": s.passed,
            "failures": s.failures,
            "flips": s.flips,
            # when THIS story was verified, so the Done gate can tell a fresh green from a
            # stale one carried forward by the merge.
            "verified_at": stamp,
        }
        for s in stories
    }
    merged = new_stories
    if merge and path.exists():
        try:
            prior = json.loads(path.read_text(encoding="utf-8")).get("stories", {})
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


def _under_root(repo_root: Path, rel: str) -> Path:
    """Resolve a --dir/--report value against the repo root when it is relative, so a run
    from any cwd discovers stories and writes the report where the Done gate reads them
    (root/sdlc-studio/.local/...). An absolute path the caller passed is honoured as-is."""
    p = Path(rel)
    return p if p.is_absolute() else repo_root / p


def cmd_run(args: argparse.Namespace) -> int:
    """Run verifiers across stories, update files, and write the report."""
    repo_root = Path(args.repo_root).resolve()

    if args.story:
        paths = [Path(args.story)]
        if not paths[0].exists():
            # An explicitly-named story that does not exist is an ERROR (exit 2), never a
            # silent skip that returns 0 - a typo'd --story path read as "all ACs green" to a
            # gate. Mirrors the --id branch below.
            print(f"no story file at {args.story}", file=sys.stderr)
            return 2
    elif getattr(args, "id", None):  # resolve --id USNNNN under --dir (case-insensitive)
        target = sdlc_md.norm_id(args.id)
        matches = [p for p in walk_stories(_under_root(repo_root, args.dir))
                   if sdlc_md.norm_id(sdlc_md.extract_record_id(p.stem) or "") == target]
        if not matches:
            print(f"no story file for id {args.id} under {args.dir}", file=sys.stderr)
            return 2
        paths = matches[:1]
    else:
        paths = list(walk_stories(_under_root(repo_root, args.dir)))

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
    report_path = _under_root(repo_root, args.report)
    if args.dry_run:
        report_path = report_path.with_name(report_path.stem + ".dry-run" + report_path.suffix)
    write_report(report_path, reports, dry_run=args.dry_run, merge=not getattr(args, "fresh", False))
    append_history(repo_root / "sdlc-studio" / ".local" / "verify-history.jsonl", reports, args.dry_run)
    print(f"wrote {report_path}")

    return 1 if overall_fail > 0 else 0


_PASS_TOKENS = {"pass", "passing", "passed", "done", "verified", "covered", "green"}


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
        data = json.loads(p.read_text(encoding="utf-8"))
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
    Returns a list of {ac, issue} findings (empty = the matrix is complete and honest)."""
    text = Path(spec_path).read_text(encoding="utf-8")
    failed_in_report = _report_failed_acs(verify_report) if verify_report else set()
    issues: list[dict] = []
    def _matrix_header(cells: list) -> bool:
        low = [c.strip().lower() for c in cells]
        return "ac" in low and ("test cases" in low or "test case" in low)
    for tbl in sdlc_md.iter_tables(text, header_predicate=_matrix_header):
        if tbl["header"] is None or not _matrix_header(tbl["header"]):
            continue  # only the AC Coverage Matrix table(s); later tables never bleed in
        low = [c.strip().lower() for c in tbl["header"]]
        cols = {n: low.index(n) for n in ("ac", "test cases", "test case", "status") if n in low}
        story_col = low.index("story") if "story" in low else None
        for _ln, cells in tbl["rows"]:
            ac = cells[cols["ac"]].strip() if cols["ac"] < len(cells) else ""
            if not ac or ac.lower() == "ac":
                continue
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
    return issues


def epic_stories(repo_root: Path | str, epic_id: str) -> list[Path]:
    """Story files whose `Epic:` field links to `epic_id`, sorted by id. The same epic
    membership rule `epic_test_spec_check` uses for test-specs, applied to stories - so the
    matrix scaffold covers exactly the stories that belong to the epic, no more, no less."""
    root = Path(repo_root)
    eid = sdlc_md.norm_id(epic_id)
    out: list[Path] = []
    for p in sdlc_md.artifact_files("story", root):
        ef = sdlc_md.extract_field(p.read_text(encoding="utf-8"), "Epic") or ""
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
        for block in parse_story(story.read_text(encoding="utf-8")):
            rows.append(sdlc_md.join_row([story_id, block.ac_id, block.title, "", ""]))
    return "### AC Coverage Matrix\n\n" + "\n".join(rows) + "\n"


def cmd_scaffold(args: argparse.Namespace) -> int:
    """Emit the pre-filled AC Coverage Matrix for an epic to stdout (or a file)."""
    matrix = scaffold_ac_matrix(args.root, args.epic)
    if getattr(args, "out", None):
        Path(args.out).write_text(matrix, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(matrix, end="")
    return 0


def epic_test_spec_check(repo_root: Path | str, epic_id: str) -> dict:
    """Hard epic-scope test-spec requirement: an epic must have a test-spec (linked by
    its `Epic:` field) whose AC Coverage Matrix passes `ts-check`. Returns {epic, ok, specs,
    issues}. The caller gates on it per `quality.epic_requires_test_spec` (default true);
    single-story work is exempt. Reuses `ts_check` - no new verification logic."""
    root = Path(repo_root)
    eid = sdlc_md.norm_id(epic_id)
    specs = []
    for p in sdlc_md.artifact_files("test-spec", root):
        ef = sdlc_md.extract_field(p.read_text(encoding="utf-8"), "Epic") or ""
        m = sdlc_md.ID_SEARCH_RE.search(ef)
        if m and sdlc_md.norm_id(m.group(0)) == eid:
            specs.append(p)
    if not specs:
        return {"epic": epic_id, "ok": False, "specs": [],
                "issues": [{"issue": "no test-spec links to this epic (epic-scope TS required)"}]}
    issues = [{**i, "spec": sp.name} for sp in specs for i in ts_check(sp)]
    return {"epic": epic_id, "ok": not issues, "specs": [s.name for s in specs], "issues": issues}


def cmd_epic_ts(args: argparse.Namespace) -> int:
    r = epic_test_spec_check(args.root, args.epic)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    else:
        for it in r["issues"]:
            print(f"  {it.get('spec', args.epic)}: {it.get('ac', '')} {it['issue']}")
        print(f"epic-ts: {args.epic} {'OK' if r['ok'] else 'FAIL'} ({len(r['specs'])} spec(s))")
    return 0 if r["ok"] else 1


def cmd_ts_check(args: argparse.Namespace) -> int:
    issues = ts_check(args.spec, args.verify_report)
    if args.format == "json":
        print(json.dumps(issues, indent=2))
        return 1 if issues else 0
    for it in issues:
        print(f"  {it['ac']}: {it['issue']}")
    print(f"ts-check: {len(issues)} incomplete matrix row(s) in {Path(args.spec).name}")
    return 1 if issues else 0


def cmd_lint(args: argparse.Namespace) -> int:
    """Advisory: flag Verify lines that would fall through to `shell` but look like a
    mis-written runner invocation. Catches the AC↔test drift at author time
    instead of discovering it 0/7 at verify time. Never fails the build."""
    paths = [Path(args.story)] if args.story else list(walk_stories(_under_root(repo_root, args.dir)))
    flagged = 0
    for p in paths:
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            m = VERIFY_RE.match(line)
            if not m:
                continue
            expr = m.group(2).strip()
            reason = lint_verifier(expr)
            if reason:
                flagged += 1
                print(f"{p.name}: {expr!r}\n    -> {reason}")
            availability = lint_runner_available(expr)
            if availability:
                flagged += 1
                print(f"{p.name}: {expr!r}\n    -> {availability}")
    print(f"verify-lint: {flagged} suspicious Verify line(s) (advisory)")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Print the latest verification report in text or JSON form."""
    report_path = Path(args.report)
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
    total_pass = total_fail = total_manual = 0
    for sid, s in stories.items():
        total_pass += s.get("verified", 0)
        total_fail += s.get("failed", 0)
        total_manual += s.get("manual", 0)
        print(
            f"{sid}: ac={s.get('ac_count', 0)} "
            f"pass={s.get('verified', 0)} "
            f"fail={s.get('failed', 0)} "
            f"manual={s.get('manual', 0)}"
        )
        for fail in s.get("failures", []):
            print(f"  FAIL {fail['ac']}: {fail['verifier']}")
    print(f"total: pass={total_pass} fail={total_fail} manual={total_manual}")
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
    r.add_argument("--story", help="Single story file (overrides --dir)")
    r.add_argument("--id", help="Single story by id, e.g. US0001 (resolved under --dir)")
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
        "--repo-root", "--root",
        dest="repo_root",
        default=".",
        help="Repository root used as cwd for verifier commands (--root is an alias, "
             "matching the flag grammar of every sibling script)",
    )
    r.set_defaults(func=cmd_run)

    ln = sub.add_parser("lint", help="Advisory: flag non-DSL / mis-written Verify lines")
    ln.add_argument("--dir", default="sdlc-studio/stories", help="Stories directory")
    ln.add_argument("--story", help="Single story file (overrides --dir)")
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
