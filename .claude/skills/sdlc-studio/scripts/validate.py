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

_AC_SECTION_RE = re.compile(r"^#{2,}\s+.*acceptance criteria", re.I | re.M)


def _has_ac_section(text: str) -> bool:
    """True if an 'Acceptance Criteria' heading is followed by at least one line
    of content (bullet, numbered item, or prose) before the next heading.

    Accepts the common plain-bullet-list AC style, not only labelled `ACn` ids.
    """
    m = _AC_SECTION_RE.search(text)
    if not m:
        return False
    for line in text[m.end():].splitlines():
        s = line.strip()
        if s.startswith("#"):
            break  # next heading — section ended with no content
        if s and not s.startswith(">"):
            return True
    return False

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


def validate_file(path: Path, type_: str, repo_root: Path | None = None) -> list[dict]:
    """Return a list of violation dicts for one artifact file. Pass repo_root so a
    project's `.config.yaml` status_vocab extensions count as valid."""
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
    elif sdlc_md.canonical_status(status, sdlc_md.status_vocab(type_, repo_root)) is None:
        # Decorated statuses ('Done (v2.66.0)') are valid — only a status whose
        # leading token is not in the vocabulary at all is flagged.
        allowed = ", ".join(sdlc_md.status_vocab(type_, repo_root))
        add("error", "status-vocab",
            f"status '{status}' is not one of the allowed {type_} statuses ({allowed}); "
            f"an established project status can be declared in sdlc-studio/.config.yaml "
            f"under status_vocab.{type_} - see reference-config.md")

    if type_ == "story":
        ac_ids = [
            sdlc_md.extract_ac_id(line)
            for line in text.splitlines()
            if sdlc_md.extract_ac_id(line)
        ]
        if not ac_ids and not _has_ac_section(text) and not _ac_exempt(rec, repo_root):
            add("error", "no-ac",
                "story has no acceptance criteria (`### ACn`, `- **ACn:**`, or a "
                "populated `## Acceptance Criteria` section)")

    # Schema-v3 team-schema: a typed, resolvable `raised_by`. v2 artefacts are exempt, so the
    # rule cannot fail an existing sequential-id project until it opts into v3.
    if repo_root is not None and sdlc_md.is_schema_v3(repo_root):
        auth = sdlc_md.parse_authorship(text, "Raised-by")
        if auth is None:
            add("error", "authorship-structured",
                "schema-v3 artefact has no `> **Raised-by:** Name; type; version` line "
                "(type is one of human | persona | agent)")
        elif auth["type"] not in ("human", "persona", "agent"):
            add("error", "authorship-type",
                f"raised_by type '{auth['type']}' must be one of human | persona | agent")
        elif not sdlc_md.resolve_author(auth["name"], auth["type"], repo_root):
            add("error", "authorship-unresolved",
                f"raised_by persona '{auth['name']}' does not resolve to a document under "
                "sdlc-studio/personas/")

    _check_placeholders(text, add)
    return out


_PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
_GWT = re.compile(r"\s*[-*]\s+\*\*(Given|When|Then)\b")
_META = re.compile(r">\s*\*\*[\w ]+:\*\*")
_CHECKBOX = re.compile(r"\s*[-*]\s+\[[ xX]\]")  # `- [ ] {{criterion}}` (change-request / story AC checklist)
_BULLET_VAL = re.compile(r"^\s*[-*]\s+(?:\[[ xX]\]\s+)?(?:\*\*[^*]+\*\*:?\s*)?(.*)$")


def _unfilled(value: str | None) -> bool:
    """True when a value is a placeholder slot, not real content: nothing of substance
    remains after the `{{...}}` and surrounding punctuation are removed. Mirrors
    conformance._real so the two gates agree on what counts as filled."""
    residue = _PLACEHOLDER.sub("", value or "")
    return re.sub(r"[\s.,;:!?*_`>~\-]+", "", residue) == ""


def _ac_value(line: str) -> str:
    """The fillable value of an AC structural line (text after the heading/marker)."""
    for rx in (sdlc_md.AC_HEADING_RE, sdlc_md.AC_BULLET_RE, sdlc_md.VERIFY_RE):
        m = rx.match(line)
        if m:
            return m.group(2) or ""
    m = _BULLET_VAL.match(line)  # Given/When/Then or `- [ ]` checkbox bullet
    return m.group(1) if m else line


def _check_placeholders(text: str, add) -> None:
    """Flag an unresolved `{{...}}` slot left in a metadata line or an acceptance-criteria
    structural line (AC heading, ACn / Given / When / Then / checkbox bullet, Verify) - an
    unfilled scaffold. Flags only a line whose *value* is placeholder-ONLY, so prose
    that legitimately discusses `{{placeholder}}` syntax, and a real AC that merely references
    a token, are never flagged (consistent with conformance._real)."""
    in_ac = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if not _PLACEHOLDER.search(line):
            continue
        if _META.match(line):
            if _unfilled(line[_META.match(line).end():]):
                add("error", "placeholder", f"unresolved placeholder in metadata: {line.strip()}")
        elif in_ac and (sdlc_md.AC_HEADING_RE.match(line) or sdlc_md.AC_BULLET_RE.match(line)
                        or sdlc_md.VERIFY_RE.match(line) or _GWT.match(line) or _CHECKBOX.match(line)):
            if _unfilled(_ac_value(line)):
                add("error", "placeholder",
                    f"unresolved placeholder in acceptance criteria: {line.strip()}")


def _ac_exempt(rec: str | None, repo_root: Path | None) -> bool:
    """A story is exempt from the no-ac check when its id is at or before the project's
    forward-only adoption cutoff (`.config.yaml` `conformance.adopt_after`). Shares the
    one cutoff parser (`sdlc_md.parse_cutoff`) and the `<=` boundary with conformance and
    provenance - a bare int or a prefixed id both parse, and an unparseable value raises
    loud rather than silently exempting nothing - so a project that adopts the
    executable-AC discipline partway does not retroactively fail every shipped story."""
    if repo_root is None or rec is None:
        return False
    cutoff_num = sdlc_md.parse_cutoff(sdlc_md.project_override(repo_root, "conformance.adopt_after"))
    rid_num = sdlc_md.id_number(rec)
    return cutoff_num is not None and rid_num is not None and rid_num <= cutoff_num


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


def excluded_id_files(repo_root: Path, types=None) -> list[dict]:
    """Warnings for id-named files the census EXCLUDES (no artifact header and
    no declared companion suffix) - exclusion must be visible, never silent:
    the operator either restores the artifact header or declares the suffix
    under conventions.companion_suffixes."""
    from lib import conventions
    out: list[dict] = []
    for type_ in (types or list(sdlc_md.ARTIFACT_TYPES)):
        rel, prefix = sdlc_md.ARTIFACT_TYPES[type_]
        want = prefix.upper()
        counted = set(sdlc_md.artifact_files(type_, repo_root))
        suffixes = tuple(f"-{s}" for s in conventions.companion_suffixes(repo_root))
        for p in sdlc_md.walk_glob(Path(repo_root) / rel, "*.md"):
            if p.name == "_index.md" or p in counted:
                continue
            if suffixes and p.stem.endswith(suffixes):
                continue  # a declared companion is fine by design
            rec = sdlc_md.extract_record_id(p.stem)
            if rec and sdlc_md.norm_id(rec).startswith(want):
                out.append({"file": str(p), "rule": "not-an-artifact",
                            "severity": "warning",
                            "message": (f"id-named file carries no artifact header - if it is "
                                        f"an artifact, add the `# {sdlc_md.norm_id(rec)}: <title>` "
                                        f"title or a `> **Status:**` line; if it is a companion "
                                        f"doc, declare its suffix under "
                                        f"conventions.companion_suffixes")})
    return out


def cmd_check(args: argparse.Namespace) -> int:
    """Validate the selected artifacts and report violations."""
    targets = collect_targets(args)
    repo_root = Path(args.root).resolve()
    violations: list[dict] = []
    for path, type_ in targets:
        violations.extend(validate_file(path, type_, repo_root))
    if not args.file:  # whole-tree (or per-type) runs also sweep the excluded
        violations.extend(excluded_id_files(
            repo_root, [args.type] if args.type else None))

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


def _persona_cast_role(text: str) -> str | None:
    """The cast role declared in a persona's Quick Reference, or None."""
    m = re.search(r"\|\s*\*\*Cast role\*\*\s*\|\s*([^|]+?)\s*\|", text, re.I)
    if not m:
        return None
    val = m.group(1).strip().lower()
    # the role whose word appears EARLIEST in the cell (not by our tuple order, so
    # "secondary supporting the primary" reads as secondary, not primary)
    found = [(val.find(r), r) for r in ("primary", "secondary", "supplemental", "negative",
                                        "customer", "served") if r in val]
    return min(found)[1] if found else None


def _headings(text: str) -> list[str]:
    return [h.strip().lower() for h in re.findall(r"^##+\s+(.*)$", text, re.M)]


def _starts(headings: list[str], *prefixes: str) -> bool:
    """True if any heading STARTS WITH any prefix (case-insensitive). Prefix, not substring,
    so a bare `## Context` does not satisfy `Behaviours & Context`, and `## Why End Goals
    Matter` does not satisfy `End Goals`."""
    return any(h.startswith(pfx) for h in headings for pfx in prefixes)


def check_personas(root: Path) -> list[dict]:
    """Cast-role-aware well-formedness check for goal-directed personas.

    Advisory only - a persona is a design aid, and a draft is legitimate; this never errors and
    is not in the hard gate. Scans `sdlc-studio/personas/*.md` (skips index.md). A standard
    persona (primary/secondary/supplemental) wants Who They Are, End Goals, Experience Goals,
    Behaviours & Context, Frustrations, Scenario; a **Negative** persona swaps Experience Goals
    for a Why-not (and keeps a Scenario/how-to-handle); Customer/Served make Experience + Scenario
    optional. No-op for a repo with no personas dir. When the flat glob inspects nothing but
    persona-shaped files sit nested in subdirs, emit a `persona-layout` advisory rather than a
    clean pass on an empty inspection (LL0008).
    """
    out: list[dict] = []
    pdir = Path(root) / "sdlc-studio" / "personas"
    if not pdir.is_dir():
        return out
    inspected = 0
    for p in sorted(pdir.glob("*.md")):
        # design personas only - skip index / readme / a consult-guide / underscore files, and the
        # seats/ subdir (review-seat charters, a different schema) is already excluded by the flat glob
        if p.name.lower() in {"index.md", "readme.md", "consult-guide.md"} or p.name.startswith("_"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        inspected += 1
        role = _persona_cast_role(text)
        hs = _headings(text)
        if role is None:
            out.append({"severity": "warning", "rule": "persona-cast-role", "file": str(p),
                        "message": "no Cast role in the Quick Reference "
                                   "(primary/secondary/supplemental/negative/customer/served)"})
        checks = [("Who They Are", _starts(hs, "who they are")),
                  ("End Goals", _starts(hs, "end goals")),
                  ("Behaviours & Context", _starts(hs, "behaviour")),
                  ("Frustrations", _starts(hs, "frustrations"))]
        if role == "negative":
            # the rationale heading, not any heading with "why" (e.g. "Why this matters")
            why_not = any(h.startswith("why") and "not" in h for h in hs)
            checks.append(("Why we are not designing for them", why_not))
            checks.append(("Scenario / how to handle", _starts(hs, "scenario", "how to handle", "how we handle")))
        elif role not in ("customer", "served"):  # standard, or unknown role
            checks.append(("Experience Goals", _starts(hs, "experience goals")))
            checks.append(("Scenario", _starts(hs, "scenario")))
        for name, ok in checks:
            if not ok:
                out.append({"severity": "warning", "rule": "persona-section", "file": str(p),
                            "message": f"missing section: {name}"})

    # LL0008: a pass must mean "inspected and well-formed", never "found nothing to inspect". When
    # the flat glob found no design personas but persona-shaped files sit in subdirs (e.g.
    # personas/team/, personas/stakeholders/, personas/amigos/), emit an advisory rather than a
    # vacuous clean pass. seats/ (review-seat charters, a different schema) is excluded by design.
    if inspected == 0:
        nested = [p for p in pdir.rglob("*.md")
                  if p.parent != pdir
                  and "seats" not in p.relative_to(pdir).parts
                  and p.name.lower() not in {"index.md", "readme.md", "consult-guide.md"}
                  and not p.name.startswith("_")]
        if nested:
            out.append({"severity": "warning", "rule": "persona-layout", "file": str(pdir),
                        "message": f"personas present but not in the flat Cooper layout "
                                   f"({len(nested)} nested files found); not validated"})
    return out


def cmd_personas(args: argparse.Namespace) -> int:
    """Report persona well-formedness (advisory; exits 0)."""
    violations = check_personas(Path(args.root).resolve())
    if args.format == "json":
        print(json.dumps({"generated_at": sdlc_md.now_iso8601(), "violations": violations,
                          "summary": {"warnings": len(violations)}}, indent=2))
    else:
        for v in violations:
            print(f"{v['severity'].upper():7} {v['file']}: [{v['rule']}] {v['message']}")
        print("personas look well-formed." if not violations
              else f"warnings={len(violations)}")
    return 0  # advisory - never blocks


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

    pp = sub.add_parser("personas",
                        help="Well-formedness check for goal-directed personas (advisory).")
    pp.add_argument("--root", default=".", help="Repo root (default: .)")
    pp.add_argument("--format", choices=("text", "json"), default="text")
    pp.set_defaults(func=cmd_personas)
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
