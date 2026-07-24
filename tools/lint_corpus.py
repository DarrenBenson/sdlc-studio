#!/usr/bin/env python3
"""Lint the WHOLE tracked markdown corpus under the strict rule set, with attribution.

A skill-development CI tool (lives in tools/). It exists because of a config split, not
because anything lints only changed files: both `npm run lint:md` and the pre-commit
`markdown` lane already glob the whole tree. A `**/*.md` glob cannot match a path inside a
dot-directory, so everything under `.claude/` is reached only by a second lane running the
payload config - which switches MD025, MD035, MD040, MD051, MD055, MD056 and MD060 off. An
unescaped table pipe in the shipped help sat green for an unknown number of commits: the
strict lane could not see the file, and the lane that could see it had the rule disabled.

Two decisions follow from that.

**Enumeration comes from the tracked file list**, never from a shell glob. `git ls-files`
sees dot-directories and does not see `node_modules/` or an agent worktree, which is
exactly the set wanted.

**Attribution comes from a baseline revision.** The corpus carries hundreds of findings
that predate any given change. A lane reporting only the total blocks whoever next touches
a file rather than whoever introduced the defect, which is the failure this lane exists to
end. The same enumeration and the same rule set are run at the baseline, and each finding
is fingerprinted by file, rule and offending text - not by line, so unrelated content
inserted above a finding does not relabel it. A baseline that cannot be read yields
`unattributed`, never `pre-existing`: failing the other way would forgive every finding on
a shallow clone.

Usage:
    python3 tools/lint_corpus.py [--root DIR] [--baseline REF] [--all] [--json]

Exit code: non-zero when a finding was introduced, or when a finding could not be
attributed. A run whose findings are all pre-existing exits zero.
"""
from __future__ import annotations

import argparse
import collections
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

#: The strict rule set. Deliberately the ROOT config for every file, payload included -
#: applying each tree's nearest config is what produced the split in the first place.
ROOT_CONFIG = ".markdownlint.json"

#: markdownlint over ~1800 files fits in one argv on Linux, but not on every platform.
CHUNK = 500

INTRODUCED = "introduced"
PRE_EXISTING = "pre-existing"
UNATTRIBUTED = "unattributed"


class LinterUnavailable(RuntimeError):
    """markdownlint could not be found. Never degraded to a clean report."""


class BaselineUnreadable(RuntimeError):
    """The baseline revision could not be materialised."""


@dataclass(frozen=True)
class Finding:
    """One markdownlint violation, with the offending text kept for fingerprinting."""

    path: str
    rule: str
    line: int
    context: str
    description: str

    @property
    def fingerprint(self) -> tuple[str, str, str]:
        """Identity across revisions: file, rule and offending text. NOT the line - a
        finding whose line moved because content was inserted above it is the same
        finding, and treating it as a new one blames the wrong commit."""
        return (self.path, self.rule, self.context)

    def as_dict(self, status: str) -> dict:
        return {"path": self.path, "rule": self.rule, "line": self.line,
                "context": self.context, "description": self.description,
                "status": status}


def find_linter(root: Path) -> str:
    """The markdownlint binary. `MARKDOWNLINT_BIN`, then the nearest `node_modules/.bin`
    walking up from `root`, then `PATH`.

    Walking up is node's own resolution order, and it is what makes the tool work from an
    agent worktree, whose `node_modules/` sits in the parent checkout.
    """
    override = os.environ.get("MARKDOWNLINT_BIN")
    if override:
        return override
    here = Path(root).resolve()
    for directory in [here, *here.parents]:
        candidate = directory / "node_modules" / ".bin" / "markdownlint"
        if candidate.is_file():
            return str(candidate)
    found = shutil.which("markdownlint")
    if found:
        return found
    raise LinterUnavailable(
        "markdownlint not found. It is a devDependency: run `npm install`, or set "
        "MARKDOWNLINT_BIN to its path.")


def enumerate_corpus(root: Path) -> list[str]:
    """Every tracked `.md` file, repo-relative and sorted.

    From the index, so a dot-directory is visible and an ignored or untracked tree is not.
    """
    out = subprocess.run(["git", "ls-files", "-z", "--", "*.md"],
                         cwd=str(root), capture_output=True, text=True, check=True).stdout
    return sorted(p for p in out.split("\0") if p)


def _parse(payload: str) -> list[Finding]:
    """markdownlint's `--json` output. It is written to stderr, not stdout."""
    findings = []
    for item in json.loads(payload or "[]"):
        rules = item.get("ruleNames") or ["?"]
        findings.append(Finding(
            path=item["fileName"],
            rule=rules[0],
            line=int(item["lineNumber"]),
            # Either field identifies the offending text; both are line-number free.
            context=str(item.get("errorContext") or item.get("errorDetail") or ""),
            description=str(item.get("ruleDescription") or ""),
        ))
    return findings


def lint_files(files, *, cwd: Path, config: Path, linter: str) -> list[Finding]:
    """Run the linter over `files` (relative to `cwd`) under `config`."""
    files = list(files)
    findings: list[Finding] = []
    for start in range(0, len(files), CHUNK):
        chunk = files[start:start + CHUNK]
        if not chunk:
            continue
        proc = subprocess.run([linter, "-j", "-c", str(config), "--", *chunk],
                              cwd=str(cwd), capture_output=True, text=True)
        if proc.returncode not in (0, 1):
            raise RuntimeError(f"markdownlint failed ({proc.returncode}): "
                               f"{proc.stderr.strip()[:500]}")
        findings.extend(_parse(proc.stderr))
    return sorted(findings, key=lambda f: (f.path, f.line, f.rule, f.context))


def lint_corpus(root: Path, *, config: Path | None = None,
                linter: str | None = None) -> list[Finding]:
    """The tracked markdown corpus of `root`, under the strict rule set."""
    root = Path(root)
    return lint_files(enumerate_corpus(root), cwd=root,
                      config=config or (root / ROOT_CONFIG),
                      linter=linter or find_linter(root))


def baseline_corpus(root: Path, ref: str, *, config: Path, linter: str) -> list[Finding]:
    """The same corpus at `ref`, linted under the CURRENT config.

    The current config on purpose: comparing two revisions under two rule sets would let a
    config edit reclassify every finding in the repo.
    """
    root = Path(root)
    archive = subprocess.run(["git", "archive", "--format=tar", ref],
                             cwd=str(root), capture_output=True)
    if archive.returncode != 0:
        raise BaselineUnreadable(
            archive.stderr.decode("utf-8", "replace").strip()
            or f"git archive {ref} failed")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
                tar.extractall(tmp, filter="data")
        except (tarfile.TarError, OSError) as exc:
            raise BaselineUnreadable(f"could not unpack {ref}: {exc}") from exc
        base = Path(tmp)
        files = sorted(str(p.relative_to(base)) for p in base.rglob("*.md"))
        return lint_files(files, cwd=base, config=config.resolve(), linter=linter)


def classify(current: list[Finding],
             baseline: list[Finding] | None) -> list[tuple[Finding, str]]:
    """Each current finding against the baseline set.

    Counted, not set-membership: three identical findings at the baseline and four now
    means one was introduced. A set would call all four pre-existing.
    """
    if baseline is None:
        return [(f, UNATTRIBUTED) for f in current]
    remaining = collections.Counter(f.fingerprint for f in baseline)
    classified = []
    for finding in current:
        key = finding.fingerprint
        if remaining[key] > 0:
            remaining[key] -= 1
            classified.append((finding, PRE_EXISTING))
        else:
            classified.append((finding, INTRODUCED))
    return classified


def default_baseline(root: Path) -> str | None:
    """The most recent tag reachable from HEAD - "what has this release introduced".

    None when the repo has no tags, which the caller must read as unreadable rather than
    as "nothing to compare, so everything is fine".
    """
    proc = subprocess.run(["git", "describe", "--tags", "--abbrev=0"],
                          cwd=str(root), capture_output=True, text=True)
    return proc.stdout.strip() or None


def analyse(root: Path, *, baseline: str | None = None, config: Path | None = None,
            linter: str | None = None) -> dict:
    """Lint the corpus and classify every finding against `baseline`."""
    root = Path(root)
    linter = linter or find_linter(root)
    config = config or (root / ROOT_CONFIG)
    files = enumerate_corpus(root)
    current = lint_files(files, cwd=root, config=config, linter=linter)

    reason = ""
    base_findings: list[Finding] | None = None
    if baseline is None:
        reason = "no baseline revision could be determined (no tag, and none given)"
    else:
        try:
            base_findings = baseline_corpus(root, baseline, config=config, linter=linter)
        except BaselineUnreadable as exc:
            reason = str(exc)

    classified = classify(current, base_findings)
    counts = {"introduced": 0, "pre_existing": 0, "unattributed": 0}
    key = {INTRODUCED: "introduced", PRE_EXISTING: "pre_existing",
           UNATTRIBUTED: "unattributed"}
    for _, status in classified:
        counts[key[status]] += 1
    return {
        "files": len(files),
        "findings": [f.as_dict(status) for f, status in classified],
        "counts": counts,
        "baseline": {"ref": baseline, "readable": base_findings is not None,
                     "reason": reason},
    }


def exit_code(result: dict) -> int:
    """Non-zero when something was introduced, or when nothing could be attributed."""
    counts = result["counts"]
    return 1 if counts["introduced"] or counts["unattributed"] else 0


def render(result: dict, *, show_all: bool = False) -> str:
    """The report. The summary line names every count, because a lane that reports only a
    total is one nobody can act on."""
    counts = result["counts"]
    base = result["baseline"]
    where = f"baseline {base['ref']}" if base["readable"] else "no usable baseline"
    lines = [
        f"corpus lint: {result['files']} tracked markdown files, "
        f"{len(result['findings'])} findings - "
        f"{counts['introduced']} introduced, {counts['pre_existing']} pre-existing, "
        f"{counts['unattributed']} unattributed ({where})"
    ]
    if not base["readable"]:
        lines.append(f"  the baseline could not be read ({base['ref']}): {base['reason']}")
        lines.append("  every finding is reported unattributed - none is forgiven as "
                     "pre-existing")
    for f in result["findings"]:
        if f["status"] == PRE_EXISTING and not show_all:
            continue
        detail = f" {f['context']}" if f["context"] else ""
        lines.append(f"  {f['status']:<13} {f['path']}:{f['line']} {f['rule']} "
                     f"{f['description']}{detail}")
    if counts["pre_existing"] and not show_all:
        lines.append(f"  ({counts['pre_existing']} pre-existing findings not listed; "
                     f"re-run with --all)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--baseline", default=None,
                        help="revision to attribute against (default: the latest tag)")
    parser.add_argument("--linter", default=None, help="path to markdownlint")
    parser.add_argument("--all", action="store_true",
                        help="list pre-existing findings too")
    parser.add_argument("--json", action="store_true", help="emit the classified findings")
    args = parser.parse_args(argv)

    root = Path(args.root)
    try:
        linter = args.linter or find_linter(root)
        if not Path(linter).is_file() and shutil.which(linter) is None:
            raise LinterUnavailable(f"markdownlint not found at {linter}")
    except LinterUnavailable as exc:
        print(f"lint_corpus: {exc}", file=sys.stderr)
        return 2

    baseline = args.baseline if args.baseline is not None else default_baseline(root)
    result = analyse(root, baseline=baseline, linter=linter)
    print(json.dumps(result, indent=2) if args.json else render(result, show_all=args.all))
    return exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
