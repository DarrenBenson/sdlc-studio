#!/usr/bin/env python3
"""SDLC Studio artifact-structure validator.

A deterministic linter for sdlc-studio artifacts: ID format, a title, a
metadata block, a Status drawn from the type's allowed vocabulary, and (for
stories) at least one acceptance criterion. Reports violations as JSON so
Claude consumes findings instead of eyeballing files. The analogue of Spec
Kit's `check-prerequisites`: the deterministic constraints layer.

Subcommands:
  check  Validate a file, a directory, or every artifact under the repo root.

Exit code is non-zero when any error-severity violation is found.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# Directory basename -> artifact type, for inferring a file's type from path.
_DIR_TO_TYPE = {
    Path(rel).name: type_ for type_, (rel, _prefix) in sdlc_md.ARTIFACT_TYPES.items()
}


def infer_type(path: Path) -> str | None:
    """Infer artifact type from the file's parent directory, else its ID prefix."""
    by_dir = _DIR_TO_TYPE.get(path.parent.name)
    if by_dir:
        return by_dir
    rec = sdlc_md.extract_record_id(path.stem)
    if not rec:
        return None
    for type_, (_rel, prefix) in sdlc_md.ARTIFACT_TYPES.items():
        if rec.replace("-", "").startswith(prefix):
            return type_
    return None


def validate_file(path: Path, type_: str) -> list[dict]:
    """Return a list of violation dicts for one artifact file."""
    out: list[dict] = []

    def add(severity: str, rule: str, message: str) -> None:
        out.append({
            "file": str(path), "type": type_,
            "severity": severity, "rule": rule, "message": message,
        })

    rec = sdlc_md.extract_record_id(path.stem)
    prefix = sdlc_md.ARTIFACT_TYPES[type_][1]
    if rec is None or sdlc_md.id_number(rec) is None:
        add("error", "id-format",
            f"filename '{path.name}' does not start with a valid {prefix}NNNN ID")

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        add("error", "unreadable", str(exc))
        return out

    if sdlc_md.extract_h1_title(text) is None:
        add("error", "no-title", "no `# Title` heading found")

    status = sdlc_md.extract_field(text, "Status")
    if status is None:
        add("error", "no-status", "no `> **Status:**` metadata line found")
    elif status not in sdlc_md.STATUS_VOCAB[type_]:
        allowed = ", ".join(sdlc_md.STATUS_VOCAB[type_])
        add("error", "status-vocab",
            f"status '{status}' is not one of the allowed {type_} statuses ({allowed})")

    if type_ == "story":
        ac_ids = [
            sdlc_md.extract_ac_id(line)
            for line in text.splitlines()
            if sdlc_md.extract_ac_id(line)
        ]
        if not ac_ids:
            add("error", "no-ac", "story has no `### ACn` acceptance criteria")

    return out


def collect_targets(args: argparse.Namespace) -> list[tuple[Path, str]]:
    """Resolve the (file, type) pairs to validate from the CLI args."""
    repo_root = Path(args.root).resolve()
    targets: list[tuple[Path, str]] = []
    if args.file:
        path = Path(args.file)
        type_ = args.type or infer_type(path)
        if type_:
            targets.append((path, type_))
        return targets
    types = [args.type] if args.type else list(sdlc_md.ARTIFACT_TYPES)
    for type_ in types:
        for path in sdlc_md.artifact_files(type_, repo_root):
            targets.append((path, type_))
    return targets


def cmd_check(args: argparse.Namespace) -> int:
    """Validate the selected artifacts and report violations."""
    targets = collect_targets(args)
    violations: list[dict] = []
    for path, type_ in targets:
        violations.extend(validate_file(path, type_))

    errors = sum(1 for v in violations if v["severity"] == "error")
    warnings = sum(1 for v in violations if v["severity"] == "warning")

    if args.format == "json":
        print(json.dumps({
            "generated_at": sdlc_md.now_iso8601(),
            "checked": len(targets),
            "violations": violations,
            "summary": {"errors": errors, "warnings": warnings},
        }, indent=2))
    else:
        for v in violations:
            print(f"{v['severity'].upper():7} {v['file']}: [{v['rule']}] {v['message']}")
        print(f"checked={len(targets)} errors={errors} warnings={warnings}")
    return 1 if errors else 0


def check_instructions(root: Path) -> list[dict]:
    """Hygiene-check a project's agent-instructions files (AGENTS.md / CLAUDE.md).

    AGENTS.md is the canonical instructions file; CLAUDE.md should be a thin
    `@AGENTS.md` pointer. Warns when the exemplar elements are missing or when the
    file looks bloated with per-ship narrative (which belongs in LATEST.md).
    """
    out: list[dict] = []

    def add(severity: str, rule: str, message: str) -> None:
        out.append({"severity": severity, "rule": rule, "message": message})

    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"

    if not agents.exists():
        add("error", "no-agents",
            "no AGENTS.md (the canonical instructions file); seed it from "
            "templates/agent-instructions.md")

    if claude.exists():
        ctext = claude.read_text(encoding="utf-8")
        if "@AGENTS.md" not in ctext:
            add("warning", "claude-not-pointer",
                "CLAUDE.md exists but does not import `@AGENTS.md`; it should be a thin "
                "pointer so the canonical instructions live in AGENTS.md")

    if not agents.exists():
        return out

    text = agents.read_text(encoding="utf-8")
    lower = text.lower()
    for rule, present, message in [
        ("no-doctrine-pointer",
         "reference-doctrine" in text or "operating doctrine" in lower,
         "no operating-doctrine pointer (reference `reference-doctrine.md`, do not restate it)"),
        ("no-latest-pointer",
         "latest.md" in lower,
         "no pointer to `sdlc-studio/reviews/LATEST.md` (the current-state anchor)"),
        ("no-release-gate",
         "reconcile --verify" in text or "pre-release" in lower or "release gate" in lower,
         "no pre-release gate (`reconcile --verify` + the review legs)"),
        ("no-compaction-rule",
         "compact" in lower or "compaction" in lower,
         "no context-compaction re-read rule (re-read LATEST.md + run status after a reset)"),
    ]:
        if not present:
            add("warning", rule, message)

    n_lines = text.count("\n") + 1
    if n_lines > 300:
        add("warning", "bloat-length",
            f"AGENTS.md is {n_lines} lines; instructions should stay lean - move "
            "current-state/history into sdlc-studio/reviews/LATEST.md")
    n_versions = len(re.findall(r"\bv?\d+\.\d+\.\d+\b", text))
    if n_versions >= 12:
        add("warning", "bloat-narrative",
            f"{n_versions} version strings in AGENTS.md - looks like per-ship narrative; "
            "move it to LATEST.md")

    return out


def cmd_instructions(args: argparse.Namespace) -> int:
    """Validate the project's agent-instructions files and report."""
    violations = check_instructions(Path(args.root).resolve())
    errors = sum(1 for v in violations if v["severity"] == "error")
    warnings = sum(1 for v in violations if v["severity"] == "warning")
    if args.format == "json":
        print(json.dumps({
            "generated_at": sdlc_md.now_iso8601(),
            "violations": violations,
            "summary": {"errors": errors, "warnings": warnings},
        }, indent=2))
    else:
        for v in violations:
            print(f"{v['severity'].upper():7} [{v['rule']}] {v['message']}")
        if not violations:
            print("agent-instructions files look good.")
        print(f"errors={errors} warnings={warnings}")
    return 1 if errors else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for the check and instructions subcommands."""
    p = argparse.ArgumentParser(
        prog="validate.py",
        description="Validate sdlc-studio artifact structure.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Validate artifacts.")
    c.add_argument("--type", choices=sorted(sdlc_md.ARTIFACT_TYPES),
                   help="Limit to one artifact type (default: all)")
    c.add_argument("--file", help="Validate a single file (type inferred if --type omitted)")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)

    i = sub.add_parser("instructions",
                       help="Validate the project's agent-instructions files (AGENTS.md / CLAUDE.md).")
    i.add_argument("--root", default=".", help="Repo root (default: .)")
    i.add_argument("--format", choices=("text", "json"), default="text")
    i.set_defaults(func=cmd_instructions)
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
