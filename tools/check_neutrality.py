#!/usr/bin/env python3
"""Fail if a private project / product / repo name leaks into a tracked file.

The repo is domain-neutral: specific consuming-project names must never appear in committed
docs or artifacts. The blocklist is stored as **SHA-256 hashes**, never plaintext, so this
checker (itself a tracked, public file) does not reveal the very names it guards - and its
output redacts matches to a hash prefix rather than echoing the term.

Matching is sub-token aware: a hyphenated identifier is checked against every contiguous
hyphen-join of its parts, so a base name (e.g. its hash) also catches longer variants
(`<base>-studio`, `<base>-ha`) without listing them.

Usage:
    python3 tools/check_neutrality.py            # scan tracked text files; exit 1 on any hit
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
}

# Text files worth scanning; binaries and lockfiles are skipped.
_TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".yaml", ".yml", ".json", ".toml", ".cfg",
                  ".ini", ".sh", ".py", ".ps1"}
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


def _tracked_text_files(root: Path) -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=str(root), capture_output=True,
                             text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    files = []
    for rel in out.splitlines():
        if rel in _SELF or Path(rel).name in _SKIP_NAMES:
            continue
        if Path(rel).suffix.lower() in _TEXT_SUFFIXES:
            files.append(root / rel)
    return files


def check(root: Path | str, blocked: set[str] | None = None,
          files: list[Path] | None = None) -> list[dict]:
    """Findings: {file, line, hashes} - `hashes` are redacted prefixes, not the matched term."""
    blocked = _BLOCKED if blocked is None else blocked
    root = Path(root)
    targets = files if files is not None else _tracked_text_files(root)
    findings: list[dict] = []
    for f in targets:
        try:
            lines = Path(f).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            hits = scan_text(line, blocked)
            if hits:
                findings.append({"file": str(f), "line": n, "hashes": sorted(hits)})
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
