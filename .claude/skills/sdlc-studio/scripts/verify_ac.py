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

Anything unrecognised is routed to `shell`.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# -----------------------------------------------------------------------------
# AC parsing
# -----------------------------------------------------------------------------

AC_HEADING_RE = re.compile(r"^###\s+(AC\d+)(?::\s*(.*))?$")
VERIFY_RE = re.compile(r"^(\s*)-\s*\*\*Verify:\*\*\s*(.+?)\s*$")
VERIFIED_RE = re.compile(
    r"^(\s*)-\s*\*\*Verified:\*\*\s*(yes|no|stale|manual)\s*(?:\(([^)]*)\))?\s*$",
    re.IGNORECASE,
)


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
        if current is not None:
            blocks.append(current)

    for i, line in enumerate(lines):
        m = AC_HEADING_RE.match(line)
        if m:
            flush()
            current = ACBlock(
                heading_line=i,
                ac_id=m.group(1),
                title=(m.group(2) or "").strip(),
            )
            continue

        if current is None:
            continue

        # Stop the current AC at the next non-indented heading or the next top-level heading
        if line.startswith("## ") or line.startswith("### AC"):
            # Heading guard already handled, but blank below also ends
            pass

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
        # insert a new Verified line if we need to create one later.
        if line.strip().startswith("-") and current.insert_after is None:
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


def run_verifier(expression: str, timeout: int, cwd: Path) -> VerifierResult:
    """Parse a verifier expression and execute it."""
    expr = expression.strip()
    start = time.time()
    try:
        kind, cmd = _build_command(expr)
    except ValueError as e:
        return VerifierResult(False, "invalid", 2, "", str(e), 0)

    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
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


def _build_command(expr: str) -> tuple[str, list[str] | str]:
    """Translate a verifier expression into a subprocess command.

    Returns (kind, command) where command is a list for argv-style runs or
    a string for shell=True runs.
    """
    # Split first token
    parts = expr.split(None, 1)
    head = parts[0].lower() if parts else ""
    tail = parts[1] if len(parts) > 1 else ""

    if head == "pytest" and tail:
        return "pytest", ["pytest", "-q", tail]
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

    # Fallback: treat the whole expression as a shell command
    return "shell", expr


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
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_line = None

    if block.verified_line is not None:
        orig = lines[block.verified_line]
        indent_match = re.match(r"^(\s*)", orig)
        indent = indent_match.group(1) if indent_match else ""
        new_line = f"{indent}- **Verified:** {new_state} ({today})"
        lines = lines.copy()
        lines[block.verified_line] = new_line
        return lines

    # Insert after the Verify line or last bullet
    insert_at = block.insert_after if block.insert_after is not None else block.heading_line
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


def verify_story(
    story_path: Path,
    dry_run: bool,
    timeout: int,
    repo_root: Path,
) -> StoryReport:
    text = story_path.read_text()
    lines = text.splitlines()
    blocks = parse_story(text)
    report = StoryReport(path=str(story_path), ac_count=len(blocks))

    for block in blocks:
        if block.verifier is None:
            report.manual += 1
            continue

        result = run_verifier(block.verifier, timeout, repo_root)

        if result.ok:
            report.verified += 1
            report.passed.append(block.ac_id)
            if block.verified_state != "yes" and not dry_run:
                lines = update_verified(lines, block, "yes")
                report.changed += 1
            elif block.verified_state != "yes":
                report.changed += 1
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
                }
            )
            if block.verified_state == "yes" and not dry_run:
                lines = update_verified(lines, block, "no")
                report.changed += 1
            elif block.verified_state == "yes":
                report.changed += 1

    if report.changed and not dry_run:
        new_text = "\n".join(lines)
        if text.endswith("\n"):
            new_text += "\n"
        story_path.write_text(new_text)

    return report


def walk_stories(stories_dir: Path) -> Iterable[Path]:
    if not stories_dir.exists():
        return []
    return sorted(p for p in stories_dir.glob("US*.md") if p.is_file())


def write_report(path: Path, stories: list[StoryReport]) -> None:
    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stories": {
            os.path.basename(s.path).replace(".md", ""): {
                "ac_count": s.ac_count,
                "verified": s.verified,
                "failed": s.failed,
                "stale": s.stale,
                "manual": s.manual,
                "passed": s.passed,
                "failures": s.failures,
            }
            for s in stories
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def cmd_run(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()

    if args.story:
        paths = [Path(args.story)]
    else:
        paths = list(walk_stories(Path(args.dir)))

    if not paths:
        print("no stories found", file=sys.stderr)
        return 2

    reports: list[StoryReport] = []
    overall_fail = 0
    overall_pass = 0
    for p in paths:
        if not p.exists():
            print(f"skip: {p} not found", file=sys.stderr)
            continue
        report = verify_story(p, args.dry_run, args.timeout, repo_root)
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

    if not args.dry_run:
        write_report(Path(args.report), reports)
        print(f"wrote {args.report}")

    return 1 if overall_fail > 0 else 0


def cmd_report(args: argparse.Namespace) -> int:
    report_path = Path(args.report)
    if not report_path.exists():
        print(f"error: no report at {report_path}. Run `verify_ac.py run` first.", file=sys.stderr)
        return 2
    data = json.loads(report_path.read_text())
    if args.format == "json":
        print(json.dumps(data, indent=2))
        return 0

    print(f"generated_at: {data.get('generated_at')}")
    stories = data.get("stories", {})
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
    p = argparse.ArgumentParser(
        prog="verify_ac.py",
        description="Execute acceptance-criterion verifiers and update Verified state.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Run verifiers and update story files")
    r.add_argument("--dir", default="sdlc-studio/stories", help="Stories directory")
    r.add_argument("--story", help="Single story file (overrides --dir)")
    r.add_argument("--dry-run", action="store_true", help="Do not modify story files")
    r.add_argument("--timeout", type=int, default=120, help="Per-verifier timeout in seconds")
    r.add_argument(
        "--report",
        default="sdlc-studio/.local/verify-report.json",
        help="Report output path",
    )
    r.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used as cwd for verifier commands",
    )
    r.set_defaults(func=cmd_run)

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
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
