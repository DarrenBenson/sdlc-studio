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
from lib import sdlc_md, tiers  # noqa: E402
import persona_gen  # noqa: E402  (the provenance stamp/reviewed grammar - one source)
import file_finding  # noqa: E402  (the pseudo-`Verify:` detector the creators refuse on - one authority)

_AC_SECTION_RE = re.compile(r"^#{2,}\s+.*acceptance criteria", re.I | re.M)

# Scaffold tiers an artefact may declare in `> **Template:**`. From lib.tiers - the one
# authority the creator, the gate and the backstop all read, so none of them can be working
# from a different vocabulary than the others.
TEMPLATE_TIERS = tiers.TEMPLATE_TIERS


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
    # A valid id is either a v2 sequential (id_number resolves) or a v3 short-ULID (BG-01JQK3F8).
    if rec is None or (sdlc_md.id_number(rec) is None and not sdlc_md.is_v3_id(rec)):
        add("error", "id-format",
            f"filename '{path.name}' does not start with a valid {prefix} ID (v2 {prefix}NNNN or v3 ULID)")

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

    # An RFC that reached Accepted with a decision still Open. The transition gate refuses
    # this going forward, but a gate on the change alone leaves every file that predates it
    # untouched while still reporting the workspace clean - which is how six RFCs came to be
    # Accepted, decomposed and delivered carrying only the boilerplate Open row. Reuses
    # transition's reader so the two cannot drift into disagreeing about what Open means.
    if type_ == "rfc" and status is not None and status.strip().lower().startswith("accepted"):
        import transition  # noqa: PLC0415 - local: keep transition off validate's cold paths
        still_open = transition._rfc_open_decisions(text)
        if still_open:
            recorded = transition._rfc_override_reason(text)
            add("warning" if recorded else "error", "accepted-open-decision",
                f"RFC is Accepted but {len(still_open)} decision row(s) are still Open "
                f"({', '.join(still_open)}) - close each with what actually shipped"
                + (f"; override recorded: {recorded}" if recorded else ""))

    # The scaffold tier the artefact was rendered at. Absent is valid and means "not the
    # planning tier" (every artefact predating the tier). A value outside the known set is
    # an error, not a shrug: `plannning` would read as not-planning and switch the
    # promotion gate silently off - a lane with nothing to prove reading as proof.
    tier = sdlc_md.extract_field(text, "Template")
    if tier is not None and tier.strip().lower() not in TEMPLATE_TIERS:
        add("error", "template-tier",
            f"template tier '{tier}' is not one of {', '.join(TEMPLATE_TIERS)} - an "
            "unrecognised tier reads as 'not planning' and would silently disable the "
            "promotion gate")

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

    # A CR/bug acceptance criterion is prose. A command-shaped `Verify:` written into it is
    # executed by nothing (verify_ac only runs a STORY's canonical `- **Verify:**` line), so it is
    # assurance with no proof behind it: a wrong command is a permanent false red, and a loose one
    # (a grep that matches unrelated prose) is a false green on a feature nobody built. The
    # creators now REFUSE to write one; this reports the ones already on disk. A warning, not an
    # error: the instances predate the guard, and the gate must not fail unrelated work - but they
    # are named, with their line, rather than silently tolerated.
    if type_ in ("cr", "bug"):
        for lineno, line, cmd in file_finding.scan_prose_acs(text):
            add("warning", "pseudo-verify",
                f"line {lineno}: acceptance criterion carries a command-shaped `Verify:` "
                f"({cmd!r}) that NOTHING executes - only a story's `- **Verify:**` line is run. "
                f"Restate it as the observable outcome; executable proof belongs on the stories "
                f"this is actioned into. Offending line: {line.strip()}")

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

        # Separation of duties: the triager must not be the raiser (the adversarial-review
        # discipline compiled into a check). A solo human self-triaging only WARNS - a lone
        # operator with no second identity must not deadlock (solo-first stays primary).
        triaged = sdlc_md.parse_authorship(text, "Triaged-by")
        if auth and triaged and triaged["name"]:
            same = (sdlc_md.norm_id(auth["name"]) == sdlc_md.norm_id(triaged["name"])
                    and auth["type"] == triaged["type"])
            if same:
                sev = "warning" if triaged["type"] == "human" else "error"
                add(sev, "duties-separated",
                    f"triaged_by '{triaged['name']}' is the same as raised_by - a different "
                    "seat must triage (hand off to another reviewer)")

        # Optional, record-only tranche reference (orchestrator pass-through). Absent is fine;
        # a present-but-empty value is a malformed record. sdlc-studio never allocates it - it
        # only reads it (the "what shipped in tranche X" query). `tranche_ref` captures the value
        # newline-safely, and the query reads through the same helper so the two agree.
        if re.search(r"\*\*Tranche:\*\*", text) and sdlc_md.tranche_ref(text) is None:
            add("error", "tranche-shape",
                "tranche reference present but empty - give it a value or remove the field "
                "(sdlc-studio reads a tranche reference, never allocates it)")

        # Evidence-or-it-did-not-happen, per type. Presence only (truth stays with reviewers
        # and verify_ac); a placeholder counts as absent.
        if type_ == "bug" and not _bug_has_evidence(text):
            add("error", "evidence-present",
                "bug has no evidence - cite a file:line reference, command output, or "
                "reproduction steps")
        elif type_ == "cr" and not _cr_has_evidence(text):
            add("error", "evidence-present",
                "CR needs both an impact statement and a size - `> **Size:** <"
                + "|".join(sdlc_md.SIZE_SCALE) + ">` (a T-shirt size: a CR is a request, "
                "sized before it is decomposed; story points belong on the delivery unit)")

    # An ungroomed (pre-Ready) story's AC placeholders are a WARNING, not an error: refine seeds
    # them and validate must not block the refine commit that creates the Draft backlog, while the
    # placeholder still keeps the story out of Ready/Done. Every other type/status: error.
    _canon = sdlc_md.canonical_status(status, sdlc_md.status_vocab(type_, repo_root)) if status else None
    _pre_ready_story = type_ == "story" and _canon in ("Proposed", "Draft")
    _check_placeholders(text, add, ac_severity="warn" if _pre_ready_story else "error")
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


_FILE_LINE = re.compile(r"[\w./-]+\.\w+:\d+")


def _section_has_content(text: str, *names: str) -> bool:
    """True when a `## Name` heading exists with non-placeholder body text under it."""
    for name in names:
        m = re.search(rf"^#{{1,4}}\s+{re.escape(name)}\b.*$", text, re.M | re.I)
        if not m:
            continue
        body = text[m.end():]
        nxt = re.search(r"^#{1,4}\s", body, re.M)
        body = body[:nxt.start()] if nxt else body
        if body.strip() and not _unfilled(body):
            return True
    return False


def _bug_has_evidence(text: str) -> bool:
    """A bug carries evidence: a file:line reference, a code/output block, or reproduction steps."""
    if _FILE_LINE.search(text) or "```" in text:
        return True
    return _section_has_content(text, "Steps to Reproduce", "Reproduction", "Evidence")


def _cr_has_evidence(text: str) -> bool:
    """A CR carries an impact statement AND a size.

    A CR is sized by a T-shirt `Size` (S/M/L/XL) - a CR is a REQUEST, sized coarsely before it is
    decomposed, and story points belong on the delivery unit it becomes. TWO legacy shapes are
    still ACCEPTED here, and only here: a `Points` value (CRs filed under the earlier gate that
    forced points onto the request) and an `Effort` S/M/L (older still). This is a read over
    artefacts already on disk, and a validator that turned every CR filed before a vocabulary
    change into an error would be reporting a fact about history, not a defect anyone can fix.
    Nothing WRITES a Points or an Effort onto a CR any more, so the tolerance drains as the
    backlog is re-estimated rather than living on as a second vocabulary.
    """
    has_impact = _section_has_content(text, "Impact", "Impact Assessment", "Motivation")
    legacy_effort = bool(re.search(r"effort", text, re.I)) and bool(
        re.search(r"\b[SML]\b|small|medium|large", text, re.I))
    has_size = (sdlc_md.read_size(text) is not None            # the current shape: a T-shirt Size
                or sdlc_md.read_points(text) is not None       # legacy: points on a request
                or legacy_effort)                              # legacy: Effort S/M/L
    return has_impact and has_size


def _check_placeholders(text: str, add, ac_severity: str = "error") -> None:
    """Flag an unresolved `{{...}}` slot left in a metadata line or an acceptance-criteria
    structural line (AC heading, ACn / Given / When / Then / checkbox bullet, Verify) - an
    unfilled scaffold. Flags only a line whose *value* is placeholder-ONLY, so prose
    that legitimately discusses `{{placeholder}}` syntax, and a real AC that merely references
    a token, are never flagged (consistent with conformance._real).

    Metadata placeholders are always an error. An AC placeholder uses `ac_severity`: the caller
    passes `warn` for an ungroomed (pre-Ready) story - a fresh refine output whose ACs are still
    scaffolds - so the refine commit that creates it lands, while the placeholder still
    blocks the story from reaching Ready/Done (conformance's specified/verifiable bar, unchanged)."""
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
                add(ac_severity, "placeholder",
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


def check_dor_dod(root: Path) -> list[dict]:
    """Validate the project's DoR/DoD documents when present: every `[check: <id>]`
    tag must resolve through the registered vocabulary. An unknown id is an ERROR -
    a tag nothing enforces is human intent silently unenforced. Untagged criteria
    are explicitly human-judged and never flagged."""
    out: list[dict] = []
    for name in ("definition-of-ready.md", "definition-of-done.md"):
        path = root / "sdlc-studio" / name
        if not path.is_file():
            continue
        text = sdlc_md.read_text_safe(path)
        for bad in sdlc_md.unknown_check_ids(text or ""):
            known = ", ".join(sorted(sdlc_md.DOR_DOD_CHECK_IDS))
            out.append({"file": str(path), "severity": "error", "rule": "unknown-check-id",
                        "message": f"[check: {bad}] resolves to no registered check - "
                                   f"an unenforced tag is a silently weakened bar; "
                                   f"registered ids: {known}"})
        for nm in sdlc_md.check_tag_near_misses(text or ""):
            out.append({"file": str(path), "severity": "error", "rule": "malformed-check-tag",
                        "message": f"{nm} is shaped like a check tag but does not parse "
                                   f"(wrong case or spacing) - it would read as no tag, leaving "
                                   f"its criterion silently unenforced; use the exact form "
                                   f"[check: <id>]"})
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
        violations.extend(check_dor_dod(repo_root))

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

    Advisory - a persona is a design aid, and a draft is legitimate; not in the hard
    gate. One finding errors: two Primary personas declaring the same `Interface:` (the
    elastic user reborn - Cooper's one-Primary-per-interface rule); everything else warns. Scans `sdlc-studio/personas/*.md` (skips index.md). A standard
    persona (primary/secondary/supplemental) wants Who They Are, End Goals, Experience Goals,
    Behaviours & Context, Frustrations, Scenario; a **Negative** persona swaps Experience Goals
    for a Why-not (and keeps a Scenario/how-to-handle); Customer/Served make Experience + Scenario
    optional. When the flat glob inspects nothing but
    persona-shaped files sit nested in subdirs, emit a `persona-layout` advisory rather than a
    clean pass on an empty inspection (LL0008). The same rationale covers the legacy flat
    layout: a project whose only personas live in `sdlc-studio/personas.md` (the file the
    story workflow reads when no registry cards exist) gets a `persona-layout` advisory plus
    a light structural check (`persona-legacy`: unfilled boilerplate, no persona sections) -
    never a vacuous clean pass on the one persona file actually consumed. No-op only when
    neither layout holds any personas.
    """
    out: list[dict] = []
    pdir = Path(root) / "sdlc-studio" / "personas"
    if not pdir.is_dir():
        return _check_legacy_personas_md(Path(root))
    inspected = 0
    primaries: list[tuple[Path, str | None]] = []
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
        if role == "primary":
            im = re.search(r"\|\s*\*\*Interface\*\*\s*\|\s*([^|]+?)\s*\|", text, re.I)
            primaries.append((p, im.group(1).strip().casefold() if im else None))

    # Cooper: exactly one Primary per interface - two Primaries means two interfaces.
    # A multi-Primary cast is a warning (the project may genuinely have two interfaces);
    # two Primaries DECLARING the same optional Interface: is the elastic user reborn
    # and the one place this check errors.
    if len(primaries) > 1:
        declared = [(p, i) for p, i in primaries if i]
        shared = {i for _, i in declared if sum(1 for _, j in declared if j == i) > 1}
        if shared:
            names = ", ".join(p.name for p, i in declared if i in shared)
            out.append({"severity": "error", "rule": "persona-one-primary", "file": str(pdir),
                        "message": f"two Primary personas declare the same Interface "
                                   f"({', '.join(sorted(shared))}): {names} - one Primary "
                                   "per interface; merge them or split the interface"})
        elif any(i is None for _, i in primaries):
            names = ", ".join(p.name for p, _ in primaries)
            out.append({"severity": "warning", "rule": "persona-one-primary", "file": str(pdir),
                        "message": f"{len(primaries)} Primary personas ({names}) - Cooper's "
                                   "rule is one Primary per interface; declare an "
                                   "`| **Interface** | ... |` row in each Quick Reference "
                                   "or demote all but one"})

    # The stakeholder panel (personas/stakeholders/) has its own schema - the other side
    # of the table: type declared, goals, veto lines, evidence read, Cooper Cast
    # designation. Same advisory contract as design personas: warnings only, never gated.
    sdir = pdir / "stakeholders"
    if sdir.is_dir():
        for p in sorted(sdir.glob("*.md")):
            if p.name.startswith("_") or p.name.lower() in {"index.md", "readme.md"}:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                continue
            m = _STAKEHOLDER_TYPE_RE.search(text)
            if not m or m.group(1).lower() not in STAKEHOLDER_TYPES_ALLOWED:
                out.append({"severity": "warning", "rule": "stakeholder-type", "file": str(p),
                            "message": "no machine-readable `<!-- stakeholder: ... -->` type "
                                       f"in the allowed set ({', '.join(sorted(STAKEHOLDER_TYPES_ALLOWED))}) "
                                       "- the consult cannot group this card"})
            hs = _headings(text)
            for name in ("Who They Are", "What They Want", "Veto Lines", "Evidence They Read"):
                if not _starts(hs, name.lower()):
                    out.append({"severity": "warning", "rule": "stakeholder-section",
                                "file": str(p), "message": f"missing section: {name}"})
            if not re.search(r"\*\*Cast:\*\*\s*(Customer|Served)\b", text, re.I):
                out.append({"severity": "warning", "rule": "stakeholder-cast", "file": str(p),
                            "message": "no Cooper Cast designation (**Cast:** Customer | "
                                       "Served) - the buyer-never-overrides-the-Primary "
                                       "arbitration cannot be applied"})

    # LL0008: a pass must mean "inspected and well-formed", never "found nothing to inspect". When
    # the flat glob found no design personas but persona-shaped files sit in subdirs (e.g.
    # personas/team/, personas/amigos/), emit an advisory rather than a vacuous clean pass.
    # seats/ (review-seat charters) and stakeholders/ (the generated panel) are the generator's
    # canonical output homes - different schemas, excluded by design.
    if inspected == 0:
        nested = [p for p in pdir.rglob("*.md")
                  if p.parent != pdir
                  and "seats" not in p.relative_to(pdir).parts
                  and "stakeholders" not in p.relative_to(pdir).parts
                  and p.name.lower() not in {"index.md", "readme.md", "consult-guide.md"}
                  and not p.name.startswith("_")]
        if nested:
            out.append({"severity": "warning", "rule": "persona-layout", "file": str(pdir),
                        "message": f"personas present but not in the flat Cooper layout "
                                   f"({len(nested)} nested files found); not validated"})
        # no design cards in the registry - the story pipeline falls back to the legacy
        # flat personas.md, so that file must not escape unexamined (LL0008)
        out.extend(_check_legacy_personas_md(Path(root)))
    return out


def _check_legacy_personas_md(root: Path) -> list[dict]:
    """Light structural check for the legacy flat `sdlc-studio/personas.md` - the file the
    story workflow reads when the personas/ registry holds no design cards. Advisory only
    (a looser schema than the registry cards): its use gets a `persona-layout` advisory,
    and an unfilled or persona-less file gets a `persona-legacy` flag. Returns [] when the
    file is absent - a project with no personas at all is the prerequisite checks' problem,
    not a validation finding."""
    flat = root / "sdlc-studio" / "personas.md"
    if not flat.is_file():
        return []
    out = [{"severity": "warning", "rule": "persona-layout", "file": str(flat),
            "message": "legacy flat personas.md in use (no personas/ registry design cards) "
                       "- story generation reads this file and only a light structural check "
                       "applies here; consider migrating to the personas/ registry "
                       "(reference-persona.md)"}]
    try:
        text = flat.read_text(encoding="utf-8")
    except OSError as exc:
        out.append({"severity": "warning", "rule": "persona-legacy", "file": str(flat),
                    "message": f"personas.md exists but cannot be read ({exc})"})
        return out
    if "{{" in text:
        out.append({"severity": "warning", "rule": "persona-legacy", "file": str(flat),
                    "message": "unfilled template placeholders ({{...}}) remain - "
                               "personas.md is boilerplate, not a populated persona set"})
    sections = [h for h in re.findall(r"^##\s+(.+)$", text, re.M) if "{{" not in h]
    if not sections:
        out.append({"severity": "warning", "rule": "persona-legacy", "file": str(flat),
                    "message": "no persona sections (## <name>) found - the file the story "
                               "workflow reads is empty of personas"})
    return out


_SERVES_RE = re.compile(r"^>?\s*\*\*Serves:\*\*\s*(.+?)\s*$", re.M)


def _persona_name_index(root: Path) -> dict[str, str]:
    """casefolded resolvable persona names -> filename: each H1's leading name (before
    any ` - role` suffix) and each file stem (hyphens as spaces)."""
    idx: dict[str, str] = {}
    pdir = root / "sdlc-studio" / "personas"
    if not pdir.is_dir():
        return idx
    for p in sorted(pdir.glob("*.md")):
        if p.name.lower() in {"index.md", "readme.md", "consult-guide.md"} or p.name.startswith("_"):
            continue
        try:
            first = next((ln for ln in p.read_text(encoding="utf-8").splitlines()
                          if ln.startswith("# ")), "")
        except OSError:
            continue
        h1 = first.lstrip("# ").split(" - ")[0].strip()
        if h1:
            idx[h1.casefold()] = p.name
        idx[p.stem.replace("-", " ").casefold()] = p.name
    return idx


def check_serves(root: Path) -> dict:
    """Persona-tagged requirements coverage (the Serves: convention) - DORMANT until the
    project carries at least one `**Serves:**` tag or opts in with `serves_coverage: true`
    in .config.yaml, so untagged projects never see a new warning. When active: every
    named persona must resolve to a persona file (a tag pointing nowhere reads as covered
    and is worse than no tag), a story serving nobody is flagged, and a coverage table
    (persona -> tagged-unit count) is emitted. Advisory - warnings only, never gated."""
    findings: list[dict] = []
    coverage: dict[str, int] = {}
    tagged = 0
    units: list[tuple[Path, list[str]]] = []
    for sub in ("stories", "prd.md"):
        base = root / "sdlc-studio" / sub
        files = sorted(base.glob("*.md")) if base.is_dir() else ([base] if base.is_file() else [])
        for p in files:
            if p.name.startswith("_"):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                continue
            # strip fenced code blocks first - a story QUOTING the convention must not
            # activate the check or mint phantom warnings
            prose = re.sub(r"^```.*?^```\s*?$", "", text, flags=re.M | re.S)
            names = [n.strip() for m in _SERVES_RE.finditer(prose)
                     for n in m.group(1).split(",") if n.strip()]
            if names:
                tagged += 1
            units.append((p, names))
    active = tagged > 0 or bool(sdlc_md.project_override(root, "serves_coverage"))
    if not active:
        return {"active": False, "findings": [], "coverage": {}}
    idx = _persona_name_index(root)
    for p, names in units:
        if not names:
            findings.append({"severity": "warning", "rule": "serves-nobody", "file": str(p),
                             "message": "no **Serves:** tag - which persona's End Goals "
                                        "does this serve? (a unit serving nobody is a "
                                        "feature-creep candidate)"})
            continue
        for n in names:
            resolved = idx.get(n.casefold())
            if resolved is None:
                findings.append({"severity": "warning", "rule": "serves-unresolved",
                                 "file": str(p),
                                 "message": f"Serves: '{n}' resolves to no persona file - "
                                            "fix the name or create the persona"})
            else:
                # key coverage on the resolved file, not the tag's raw spelling, so
                # case variants of one persona never fragment into separate rows
                coverage[resolved] = coverage.get(resolved, 0) + 1
    return {"active": True, "findings": findings, "coverage": coverage}


def cmd_serves(args: argparse.Namespace) -> int:
    """Report Serves: coverage (advisory; exits 0)."""
    res = check_serves(Path(args.root).resolve())
    if getattr(args, "format", "text") == "json":
        print(json.dumps(res, indent=2))
        return 0
    if not res["active"]:
        print("serves: dormant (no **Serves:** tags and no serves_coverage opt-in)")
        return 0
    for v in res["findings"]:
        print(f"{v['severity'].upper():7} [{v['rule']}] {v['file']}: {v['message']}")
    if res["coverage"]:
        print("\n| Persona | Units served |\n| --- | --- |")
        for name, n in sorted(res["coverage"].items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"| {name} | {n} |")
    print(f"serves: warnings={len(res['findings'])} personas-covered={len(res['coverage'])}")
    return 0


STAKEHOLDER_TYPES_ALLOWED = {"buyer", "compliance", "ops", "served"}
_STAKEHOLDER_TYPE_RE = re.compile(r"<!--\s*stakeholder:\s*([a-z][a-z0-9-]*)\s*-->", re.I)

SEAT_ROLES_ALLOWED = {"engineering", "qa", "product", "security", "sre", "data", "ux"}
_SEAT_ROLE_RE = re.compile(r"<!--\s*role:\s*([a-z][a-z0-9-]*)\s*-->", re.I)
_SEAT_REVIEW_SECTIONS = ("Lens", "Pushes Back When", "Shadow")
# Tight, word-boundary demographic denylist (Cooper: a characteristic that influences no
# design decision is omitted; demographics are the canonical fluff). Deliberately short to
# avoid false positives - the broader judgement lives in persona review, not this check.
_DEMOGRAPHIC_RE = re.compile(
    r"\b(\d+\s+years\s+old|married|husband|wife|hobbies|her gender|his gender)\b", re.I)


_PROVENANCE_LINE_RE = re.compile(r"<!--\s*provenance\s*:", re.I)


def check_seats(root: Path, require_stamp: list[Path] | None = None) -> list[dict]:
    """Error-level well-formedness for the working-team seat cards (personas/seats/) - the
    mechanical floor of team generation (the review-render hard error given an owner).

    Per card: a declared role comment in the allowed set; the review-render section
    headings; a clean demographic denylist; one card per role (a duplicate claim is an
    error - the resolver would tiebreak lexically, which is deterministic but arbitrary);
    and any provenance comment must parse as the generation stamp or the reviewed marker
    (a malformed one silently classifies as authored, dropping out of the provisional
    advisory). `require_stamp` names files the flow just generated: each MUST carry a
    valid stamp or reviewed marker - authored cards are never in that list, so the check
    stays non-circular - and a named path that matches no scanned card is itself an
    error (the guard fails loudly on input it cannot verify, never vacuously passes). Cast size: >5 seats is an error (persona proliferation); missing
    core roles is a warning (a project mid-authoring is legal). Runs standalone
    (`validate seats`) and is REQUIRED at the end of a team-generation flow; it is not in
    the default hard gate, so existing projects are never bricked by adoption."""
    out: list[dict] = []
    required = {p.resolve(): p for p in (require_stamp or [])}
    required_seen: set[Path] = set()
    sdir = root / "sdlc-studio" / "personas" / "seats"
    if not sdir.is_dir() and not required:
        return out
    # no seats/ at all is legal for a --stakeholders-only run: the required-path
    # reconciliation below still verifies stamps and fails loudly on misses
    cards = sorted(sdir.glob("*.md")) if sdir.is_dir() else []
    roles_seen: dict[str, str] = {}
    for p in cards:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError as exc:
            out.append({"severity": "error", "rule": "seat-unreadable", "file": str(p),
                        "message": f"unreadable seat card: {exc}"})
            continue
        m = _SEAT_ROLE_RE.search(text)
        if not m:
            out.append({"severity": "error", "rule": "seat-no-role", "file": str(p),
                        "message": "no machine-readable `<!-- role: ... -->` - the resolver "
                                   "cannot map this seat"})
        else:
            role = m.group(1).lower()
            if role not in SEAT_ROLES_ALLOWED:
                out.append({"severity": "error", "rule": "seat-unknown-role", "file": str(p),
                            "message": f"role '{role}' not in the allowed set "
                                       f"({', '.join(sorted(SEAT_ROLES_ALLOWED))})"})
            elif role in roles_seen:
                out.append({"severity": "error", "rule": "seat-duplicate-role", "file": str(p),
                            "message": f"role '{role}' already claimed by {roles_seen[role]} - "
                                       "one card per role (the lexical tiebreak is arbitrary)"})
            else:
                roles_seen[role] = p.name
        missing = [h for h in _SEAT_REVIEW_SECTIONS
                   if not re.search(rf"^##+\s+{re.escape(h)}\b", text, re.M)]
        if missing:
            out.append({"severity": "error", "rule": "seat-no-review-render", "file": str(p),
                        "message": f"missing review-render section(s): {', '.join(missing)} - "
                                   "a seat that cannot review is not a seat"})
        dm = _DEMOGRAPHIC_RE.search(text)
        if dm:
            out.append({"severity": "error", "rule": "seat-demographic-fluff", "file": str(p),
                        "message": f"demographic token '{dm.group(0)}' - a characteristic that "
                                   "influences no engineering decision is omitted (goals, not "
                                   "demographics)"})
        stamped = bool(persona_gen.STAMP_RE.search(text)
                       or persona_gen.REVIEWED_RE.search(text))
        for ln in text.splitlines():
            if (_PROVENANCE_LINE_RE.search(ln)
                    and not persona_gen.STAMP_RE.search(ln)
                    and not persona_gen.REVIEWED_RE.search(ln)):
                out.append({"severity": "error", "rule": "seat-malformed-stamp",
                            "file": str(p),
                            "message": f"provenance comment does not parse ({ln.strip()!r}) - "
                                       "it would silently classify as authored and drop out "
                                       "of the provisional advisory"})
                break
        if p.resolve() in required:
            required_seen.add(p.resolve())
            if not stamped:
                out.append({"severity": "error", "rule": "seat-no-stamp", "file": str(p),
                            "message": "generated card carries no provenance stamp or "
                                       "reviewed marker - run persona_gen.py stamp before "
                                       "completing the flow"})
    # Stakeholder cards share the malformed-stamp rule (the silent-declassify failure
    # mode is identical), though never the seat schema.
    stakedir = (root / "sdlc-studio" / "personas" / "stakeholders").resolve()
    if stakedir.is_dir():
        for p in sorted(stakedir.glob("*.md")):
            try:
                text = p.read_text(encoding="utf-8")
            except OSError:
                continue
            for ln in text.splitlines():
                if (_PROVENANCE_LINE_RE.search(ln)
                        and not persona_gen.STAMP_RE.search(ln)
                        and not persona_gen.REVIEWED_RE.search(ln)):
                    out.append({"severity": "error", "rule": "seat-malformed-stamp",
                                "file": str(p),
                                "message": f"provenance comment does not parse "
                                           f"({ln.strip()!r}) - it would silently classify "
                                           "as authored and drop out of the provisional "
                                           "advisory"})
                    break
    # The stakeholder flow shares this gate: a required path under personas/stakeholders/
    # is stamp-verified (never seat-schema-checked), so --stakeholders gets the same loud
    # floor instead of a parallel one.
    for res, orig in required.items():
        if res in required_seen or res.parent != stakedir or not res.is_file():
            continue
        required_seen.add(res)
        try:
            text = res.read_text(encoding="utf-8")
        except OSError as exc:
            out.append({"severity": "error", "rule": "seat-unreadable", "file": str(orig),
                        "message": f"unreadable stakeholder card: {exc}"})
            continue
        if not (persona_gen.STAMP_RE.search(text) or persona_gen.REVIEWED_RE.search(text)):
            out.append({"severity": "error", "rule": "seat-no-stamp", "file": str(orig),
                        "message": "generated card carries no provenance stamp or "
                                   "reviewed marker - run persona_gen.py stamp before "
                                   "completing the flow"})
    # A guard must fail loudly on input it cannot verify, never vacuously pass: every
    # required path that matched no scanned card (typo, cwd-relative from elsewhere,
    # outside seats/ or stakeholders/) is an error, not a silent skip.
    for res, orig in required.items():
        if res not in required_seen:
            out.append({"severity": "error", "rule": "seat-require-miss", "file": str(orig),
                        "message": "required-stamp path matches no scanned card - the "
                                   "stamp guarantee cannot be verified for it (check the "
                                   "path; it must be a card under personas/seats/ or "
                                   "personas/stakeholders/)"})
    if len(cards) > 5:
        out.append({"severity": "error", "rule": "seat-cast-size", "file": str(sdir),
                    "message": f"{len(cards)} seat cards (> 5) - persona proliferation; the "
                               "cast is 3 core + at most 2 signal-earned extras"})
    core_missing = {"engineering", "qa", "product"} - set(roles_seen)
    if cards and core_missing:
        out.append({"severity": "warning", "rule": "seat-core-missing", "file": str(sdir),
                    "message": f"core role(s) uncovered: {', '.join(sorted(core_missing))}"})
    return out


def cmd_seats(args: argparse.Namespace) -> int:
    """Error-level seat-card check; exits 1 on any error (the generation flow's floor)."""
    required = [Path(f) for f in (getattr(args, "require_stamp", None) or [])]
    violations = check_seats(Path(args.root).resolve(), require_stamp=required)
    errors = sum(1 for v in violations if v["severity"] == "error")
    if getattr(args, "format", "text") == "json":
        print(json.dumps({"violations": violations,
                          "summary": {"errors": errors,
                                      "warnings": len(violations) - errors}}, indent=2))
    else:
        for v in violations:
            print(f"{v['severity'].upper():7} [{v['rule']}] {v['file']}: {v['message']}")
        print(f"seats: errors={errors} warnings={len(violations) - errors}")
    return 1 if errors else 0


def cmd_personas(args: argparse.Namespace) -> int:
    """Report persona well-formedness (advisory; exits 1 only on the one error-level
    finding, two Primaries declaring the same Interface)."""
    violations = check_personas(Path(args.root).resolve())
    errors = sum(1 for v in violations if v["severity"] == "error")
    if args.format == "json":
        print(json.dumps({"generated_at": sdlc_md.now_iso8601(), "violations": violations,
                          "summary": {"errors": errors,
                                      "warnings": len(violations) - errors}}, indent=2))
    else:
        for v in violations:
            print(f"{v['severity'].upper():7} {v['file']}: [{v['rule']}] {v['message']}")
        print("personas look well-formed." if not violations
              else f"errors={errors} warnings={len(violations) - errors}")
    return 1 if errors else 0  # advisory except the same-Interface duplicate Primary


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
    sv = sub.add_parser("serves",
                        help="Serves: persona-coverage report (dormant until first tag or opt-in).")
    sv.add_argument("--root", default=".", help="Repo root (default: .)")
    sv.add_argument("--format", choices=("text", "json"), default="text")
    sv.set_defaults(func=cmd_serves)
    st = sub.add_parser("seats",
                        help="Error-level check for working-team seat cards (the generation floor).")
    st.add_argument("--root", default=".", help="Repo root (default: .)")
    st.add_argument("--require-stamp", nargs="+", metavar="FILE", dest="require_stamp",
                    help="Files the flow just generated - each must carry a valid "
                         "provenance stamp or reviewed marker (missing = error).")
    st.add_argument("--format", choices=("text", "json"), default="text")
    st.set_defaults(func=cmd_seats)
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
