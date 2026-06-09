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


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for the check subcommand."""
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
