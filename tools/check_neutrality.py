#!/usr/bin/env python3
"""Fail if a private project / product / repo name leaks into a tracked file.

The repo is domain-neutral: specific consuming-project names must never appear in committed
docs or artifacts. The blocklist is stored as **SHA-256 hashes**, never plaintext, so this
checker (itself a tracked, public file) does not reveal the very names it guards - and its
output redacts matches to a hash prefix rather than echoing the term.

Matching is sub-token aware: a hyphenated identifier is checked against every contiguous
hyphen-join of its parts, so a base name (e.g. its hash) also catches longer variants
(`<base>-studio`, `<base>-ha`) without listing them.

Coverage is every tracked file minus a small binary denylist, never an allowlist of suffixes:
an allowlist exempts whatever nobody enumerated, and a file nobody thought of is the one a name
leaks through. A file that cannot be read is a refusal, not a clean pass.

Usage:
    python3 tools/check_neutrality.py            # scan every tracked file; exit 1 on any hit
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

# SHA-256 of lowercased blocklisted base names. Hashes (not plaintext) so the names are not
# revealed here. To add one: `printf '%s' name | sha256sum`. Sub-token matching covers variants.
_BLOCKED: set[str] = {
    "356fe489ae7623827b74454d02449d3ee3d524e3eb6fb9f688761e523ecb6ae6",
    "606938bb66d543079e4388b6921d4988e7f9b42d802c6e6e3f1fe305dd7f041c",
    "450dcf23e621ff10542114dd8f622660cc8b96bdb2abb02af641e69f94c7b2da",
    "09d3bbfa840850aa66cf189464b355d0e592a0dbf84070fe10dec9b11a27fbc3",
}

# Every tracked file is scanned. The filter is a DENYLIST, not an allowlist of suffixes: an
# allowlist exempts whatever nobody thought to enumerate, and what it exempted here was the
# shipped .template payload (instantiated by every consuming project, so the highest-risk leak
# site), the evidence logs, and every extensionless script. A suffix absent from this set is
# scanned; a payload that is binary in fact rather than by suffix is caught by the NUL sniff
# in `check`.
_BINARY_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svgz",
                    ".woff", ".woff2", ".ttf", ".otf", ".eot",
                    ".zip", ".gz", ".tgz", ".bz2", ".xz", ".tar", ".7z", ".rar",
                    ".mp3", ".mp4", ".mov", ".wav", ".webm", ".ogg",
                    ".pyc", ".pyo", ".so", ".dll", ".dylib", ".exe", ".bin",
                    ".class", ".jar", ".wasm",
                    ".db", ".sqlite", ".sqlite3"}
_SKIP_NAMES = {"package-lock.json"}
# This checker and its test legitimately reference the mechanism - never scan them for names.
_SELF = {"tools/check_neutrality.py",
         ".claude/skills/sdlc-studio/scripts/tests/test_check_neutrality.py"}
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _candidates(text: str):
    """Every contiguous hyphen-join of every lowercased token (so a base name catches variants)."""
    for m in _TOKEN_RE.finditer(text.lower()):
        parts = m.group(0).split("-")
        for i in range(len(parts)):
            for j in range(i, len(parts)):
                yield "-".join(parts[i:j + 1])


def scan_text(text: str, blocked: set[str]) -> set[str]:
    """Redacted hash prefixes of any blocklisted name in `text` - never the term itself."""
    return {h[:12] for c in _candidates(text) if (h := _h(c)) in blocked}


def _scannable(rels: list[str]) -> list[str]:
    """The tracked paths this guard is responsible for: everything except its own source,
    lockfiles, and suffixes that are binary by definition."""
    return [rel for rel in rels
            if rel not in _SELF
            and Path(rel).name not in _SKIP_NAMES
            and Path(rel).suffix.lower() not in _BINARY_SUFFIXES]


def _tracked_text_files(root: Path) -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=str(root), capture_output=True,
                             text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        # LL0008: a guard that cannot list files must fail loud, never silently pass.
        raise SystemExit("neutrality: could not `git ls-files` - run from inside the repo; "
                         "refusing to report a clean scan of nothing")
    return [root / rel for rel in _scannable(out.splitlines())]


def check(root: Path | str, blocked: set[str] | None = None,
          files: list[Path] | None = None) -> list[dict]:
    """Findings: {file, line, hashes} - `hashes` are redacted prefixes, not the matched term."""
    blocked = _BLOCKED if blocked is None else blocked
    root = Path(root)
    targets = files if files is not None else _tracked_text_files(root)
    findings: list[dict] = []
    unreadable: list[str] = []
    for f in targets:
        try:
            raw = Path(f).read_bytes()
        except OSError as exc:
            # LL0008 again, and the same refusal `_tracked_text_files` already makes above: a
            # file the guard could not open is NOT a file it scanned clean. `read_bytes` is the
            # only failure left - decoding below cannot raise, because errors='replace'.
            unreadable.append(f"{f} ({exc.strerror or exc.__class__.__name__})")
            continue
        if b"\x00" in raw[:8192]:
            continue  # binary payload whatever its suffix - there is no text here to scan
        for n, line in enumerate(raw.decode("utf-8", errors="replace").splitlines(), 1):
            hits = scan_text(line, blocked)
            if hits:
                findings.append({"file": str(f), "line": n, "hashes": sorted(hits)})
    if unreadable:
        raise SystemExit(
            f"neutrality: {len(unreadable)} tracked file(s) could not be read, so this scan "
            f"covers less than it claims - refusing to report on it "
            f"({len(findings)} finding(s) in what WAS read):\n  "
            + "\n  ".join(unreadable))
    return findings


def main(argv: list[str] | None = None) -> int:
    findings = check(Path("."))
    if not findings:
        print("neutrality: no blocklisted project names in tracked files")
        return 0
    print(f"neutrality: {len(findings)} blocklisted-name occurrence(s) - generalise these:",
          file=sys.stderr)
    for f in findings:
        print(f"  {f['file']}:{f['line']} (redacted: {', '.join(f['hashes'])})", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
