#!/usr/bin/env python3
"""SDLC Studio engagement floor: a deterministic planning floor for multi-file work.

The 2026-07 benchmark rerun showed weaker models judging a multi-file, spec-interacting
change "too small for ceremony" and shipping the hidden-requirement defect the planning pass
catches, while stronger models engaged unprompted. Leaving the threshold to the model's own
judgement rebuilds that failure. This floor is NOT a judgement: it is a file count and a
presence check, with no model call anywhere in the fire/skip decision.

Rule: a shipped unit (a story Done, a bug Fixed/Verified/Closed, a CR Complete) may skip the
planning pass ONLY by showing it is below the floor. It shows this one of two ways - it carries a
planning artefact (an acceptance criterion, a `Verify:` expression, or a linked plan PL), or it
DECLARES what it touched in an `Affects` field that lists a single source file. A unit that does
neither fails as `undeclared`: the blank ticket and the terse commit the weak model produces
cannot buy a silent pass. A unit whose declared/touched source count is more than one and that
carries no planning artefact fails as `unplanned`.

The exact guarantee (D0026 - do not overstate it):
  * PURE OMISSION is caught deterministically. A shipped unit that neither planned nor declares a
    real single-file footprint fails as `undeclared`. A declaration must be a CHECKABLE file path
    (`src/x.py`), not prose - `n/a`, `various`, `see the commits` can be held to nothing, so they
    are omission-equivalent and do not count.
  * UNDERSTATEMENT IN A SOLO-ID COMMIT is caught. Where a unit declares one file but its commit
    (naming only that unit) touched more, the git cross-check raises the count and the floor fires.
  * UNDERSTATEMENT IN A SHARED COMMIT is NOT caught, and this is a known limit, not a bug. When a
    unit shares its commit with another judged id, the batch is skipped (git cannot attribute a
    file to one id among several without a commit-id convention), so an understated declaration
    stands. Closing this needs the per-id commit convention tracked as CR0239. The floor does not
    claim to catch it.

The two file-count signals are the declared `Affects` field and the git cross-check, and they
share a blind spot (git sees a unit only when its commit solely names its id), so requiring the
declaration is what closes PURE omission: with no way to skip planning except by declaring, an
omitted or prose-only `Affects` is itself the failure. This still catches the benchmark's observed
failure - a weak model shipping a multi-file change with NO planning.

Escape valves, each auditable, none a silent judgement:
  * `engagement_floor.adopt_after` (`.config.yaml`) exempts ids at or below a cutoff - the
    `conformance.adopt_after` precedent - so turning the floor on does not redden the backlog of
    units closed before it existed. A cutoff ABOVE the highest existing id is not grandfathering
    but a silent forward disarm, and is refused (use judgement mode to opt out visibly). Exempt
    units that WOULD violate stay counted in the report, so a cutoff cannot hide them.
  * `engagement_floor: judgement` (`.config.yaml`) is the project-global opt-out the doctrine and
    agent-instructions already document: the floor still reports, but its gate lane is advisory.
  * a recorded waiver (`decisions.py waive`) - `rule:engagement-floor` waives the whole floor for
    a project whose operator accepts the risk; `rule:engagement-floor:<id>` waives one unit. A
    waiver is a decisions-log row with a rationale, greppable and machine-detectable, not a silent
    config boolean.

The git leg does not attribute a BATCH commit (one naming several ids) to any of them: it cannot
know which file belongs to which id, so such a commit feeds no id's count (the declared `Affects`
carries a genuinely multi-file unit instead).

Read-only; pure stdlib core (git is a soft dependency: absent, the floor rests on the declared
`Affects` signal alone).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import decisions  # noqa: E402  (sibling scripts; scripts dir is on sys.path)

# The implementation-unit types the floor judges, and the shipped-outcome statuses that trigger
# it per type. A negative outcome (Won't Fix, Rejected, Superseded, Won't Implement) shipped no
# code, so the floor does not apply. Story + bug + CR are the units the defect appeared in;
# epics/RFCs/test-specs/plans are not code-shipping units in this sense.
SHIPPED_STATUS: dict[str, set[str]] = {
    "story": {"Done"},
    "bug": {"Fixed", "Verified", "Closed"},
    "cr": {"Complete"},
}

# "Source file" = a code file. Reuse complexity.py's one definition so the floor and the
# risk/estimation signals agree on what counts; a `.md`/`.yaml` doc change is not a source change.
def _source_suffixes() -> set[str]:
    try:
        import complexity
        return set(complexity.CODE_SUFFIXES)
    except Exception:  # noqa: BLE001 - never let an import failure disable the floor
        return {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".rb", ".c",
                ".cc", ".cpp", ".cs", ".rs", ".php", ".swift", ".kt"}


SOURCE_SUFFIXES = _source_suffixes()
FLOOR_THRESHOLD = 1  # "multi-file" = strictly more than one source file
WAIVER_RULE = "rule:engagement-floor"           # the whole-project opt-out subject
_PLAN_LINK_RE = re.compile(r"\bPL-?\d{4}\b")     # a reference to a plan artefact
_JUDGED_ID_RE = re.compile(r"\b((?:US|BG|CR)-?\d{4})\b")  # a judged-type id in a commit message
_REC = "\x1e"    # per-commit record separator in the git format
_MSGEND = "\x1f"  # message/file-list separator within a record
_GIT_TIMEOUT = 30


def _mode_and_cutoff(root: Path) -> tuple[str, int | None]:
    """Read the floor's config once. `engagement_floor` accepts two shapes so the scalar the
    prose half shipped (`engagement_floor: judgement`) and a cutoff can both be expressed without
    colliding on one YAML key:
      * a scalar string -> the mode (`floor` default, or `judgement`); no cutoff.
      * a mapping -> `mode` (default `floor`) and/or `adopt_after` (the grandfather cutoff).
    An unparseable cutoff raises loud (parse_cutoff), never silently disabling the floor."""
    raw = sdlc_md.project_override(root, "engagement_floor")
    if isinstance(raw, dict):
        mode = str(raw.get("mode", "floor")).strip().lower() or "floor"
        cutoff = sdlc_md.parse_cutoff(raw.get("adopt_after"))
    elif raw is None:
        mode, cutoff = "floor", None
    else:
        mode, cutoff = str(raw).strip().lower() or "floor", None
    if mode not in ("floor", "judgement"):
        mode = "floor"  # an unknown value fails safe to the default (the floor is on)
    return mode, cutoff


def _git_touched_source_files(root: Path, rid: str) -> set[str]:
    """Source files the commits mentioning `rid` touched (`git log --grep`). Empty when not a git
    repo or git is unavailable - the floor then rests on the declared `Affects` alone.

    A BATCH commit (one whose message names more than one judged-type id) is skipped: git cannot
    know which of its files belongs to which id, so attributing the whole file set to each would
    inflate every id in the batch. Such a unit is carried by its declared `Affects` instead.
    """
    # Match either commit-message spelling of the id (`CR0234` and `CR-0234`), since a repo's
    # convention may differ from its filename convention - a spelling mismatch would silently
    # zero the git signal and reopen the omit-and-escape hole for that repo.
    norm = sdlc_md.norm_id(rid)
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", norm)
    pattern = f"{m.group(1)}-?{m.group(2)}" if m else re.escape(norm)
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=false", "log", "-E",
             f"--grep={pattern}", f"--format={_REC}%B{_MSGEND}", "--name-only"],
            capture_output=True, text=True, timeout=_GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return set()
    if out.returncode != 0:
        return set()
    files: set[str] = set()
    for record in out.stdout.split(_REC):
        if _MSGEND not in record:
            continue
        message, _, file_blob = record.partition(_MSGEND)
        distinct = {sdlc_md.norm_id(i) for i in _JUDGED_ID_RE.findall(message)}
        if len(distinct) > 1:  # a batch commit: cannot apportion its files, so it feeds no id
            continue
        for line in file_blob.splitlines():
            f = line.strip()
            if f and Path(f).suffix in SOURCE_SUFFIXES:
                files.add(f)
    return files


def _declared_source_files(text: str) -> set[str]:
    """The source files a unit declares in its `Affects` field (doc paths dropped)."""
    return {f for f in sdlc_md.affects_files(text) if Path(f).suffix in SOURCE_SUFFIXES}


# A declaration must name at least one CHECKABLE footprint - a real file path, not prose. What
# makes a token a file is its BASENAME (the segment after the final `/`): it carries a real
# extension, or is a known extension-less filename, or is a dotfile. This rejects the
# omission-equivalent noise a weak model writes into the field - `n/a`, `various`, `multiple
# files`, `see the commits`, `TBD`, a version string like `v1.2` - which can be held to nothing
# and so is not a declaration. `n/a` bears a `/`, so a bare separator cannot buy a pass: its
# basename `a` is not a file.

# A file extension is a dot then a LETTER then alphanumerics (`.py`, `.md`, `.tsx`). Anchoring on
# a leading letter is what rejects a version string: `v1.2` ends `.2`, a numeric-only suffix, so
# it is not read as a file.
_FILE_EXT_RE = re.compile(r"\.[A-Za-z][A-Za-z0-9]*$")
# Real files that carry no extension. Matched case-insensitively (LICENSE, Makefile, dockerfile).
_KNOWN_EXTENSIONLESS = {"makefile", "dockerfile", "containerfile", "license", "licence"}
# A dotfile: a leading `.` then a name (`.gitignore`, `.env`, `.env.local`), no path separator.
_DOTFILE_RE = re.compile(r"\.[A-Za-z0-9][\w.-]*$")


def _is_file_token(tok: str) -> bool:
    """True when `tok` names a checkable file rather than prose. The final path segment must look
    like a file: it carries a real extension (`src/x.py`, `a/b.md`), is a known extension-less
    filename (`Makefile`, `Dockerfile`, `LICENSE`, `Containerfile`), or is a dotfile
    (`.gitignore`, `.env`). A bare word (`various`, `TBD`), `n/a`, or a version string (`v1.2`) is
    not a file. This is the invariant that keeps a declaration a checkable footprint, not prose."""
    if not tok or any(ch.isspace() for ch in tok):
        return False
    base = tok.rsplit("/", 1)[-1]  # the basename - the segment after the final `/`
    if not base:
        return False
    if _FILE_EXT_RE.search(base):
        return True
    if base.lower() in _KNOWN_EXTENSIONLESS:
        return True
    return bool(_DOTFILE_RE.fullmatch(base))


def _affects_declared(text: str) -> bool:
    """True when the unit's `Affects` field names at least one real file path. A blank field, an
    unfilled `{{placeholder}}`, or bare prose (`n/a`, `various`) is NOT a declaration: it cannot be
    held to a footprint, so it is omission-equivalent and must not satisfy the floor. (Does not
    match the story template's unrelated `**Affects production runtime:**` boolean - `extract_field`
    anchors on `Affects:`.)"""
    val = sdlc_md.extract_field(text, "Affects")
    if val is None:
        return False
    for tok in val.split(","):
        tok = re.sub(r"\s*\(.*\)\s*$", "", tok.strip()).strip().strip("`").strip()
        if tok and "{{" not in tok and _is_file_token(tok):
            return True
    return False


def _max_judged_id(root: Path) -> int:
    """The highest sequential id number among all judged-type artefacts present. A cutoff above
    this exempts ids that do not exist yet - a forward disarm, not grandfathering."""
    top = 0
    for type_ in SHIPPED_STATUS:
        for path in sdlc_md.artifact_files(type_, root):
            n = sdlc_md.id_number(sdlc_md.extract_record_id(path.stem) or path.stem)
            if n is not None and n > top:
                top = n
    return top


def _has_planning(text: str) -> bool:
    """The floor is satisfied by any planning artefact: an acceptance criterion, an executable
    `Verify:` expression, or a linked plan (PL). Broad on purpose - the floor's target is a unit
    with NO planning trace at all, not one whose planning is shaped unusually."""
    if sdlc_md.count_acs(text) > 0:
        return True
    if any(sdlc_md.VERIFY_RE.match(ln) for ln in text.splitlines()):
        return True
    return bool(_PLAN_LINK_RE.search(text))


def _unit_waiver(root: Path, rid: str) -> str | None:
    """The id of a per-unit waiver `rule:engagement-floor:<id>`, or None. The subject uses the
    normalised id so `US0100`/`US-0100` match one waiver."""
    subject = f"{WAIVER_RULE}:{sdlc_md.norm_id(rid)}"
    return decisions.waiver_for(root, subject)


def _classify(multi_file: bool, has_planning: bool, declared: bool) -> str | None:
    """The floor verdict for one unit, ignoring exemption/waiver. `None` = passes. A unit passes
    only by showing it is below the floor: it planned (any planning artefact), or it declared a
    single-file footprint. Otherwise `unplanned` (multi-file, no plan) or `undeclared` (no plan and
    no declaration - it cannot be shown below the floor, so omission does not buy a pass)."""
    if has_planning:
        return None
    if multi_file:
        return "unplanned"
    if not declared:
        return "undeclared"
    return None


def detect(repo_root: Path | str) -> dict:
    """Per-unit engagement-floor state over the shipped story/bug/CR units.

    Returns {"mode": floor|judgement, "units": [...], "summary": {...}}. Each judged unit carries
    its source-file count, whether it is multi-file, whether it has a planning artefact, whether it
    DECLARED its footprint, its violation kind, and whether it is exempt (cutoff) or waived. A live
    violation is a would-violate unit that is neither exempt nor waived. An adopt_after cutoff above
    the highest existing id is a silent forward disarm and is flagged (`cutoff_forward`).
    """
    root = Path(repo_root)
    mode, cutoff = _mode_and_cutoff(root)
    project_waived = decisions.waiver_for(root, WAIVER_RULE) is not None
    max_id = _max_judged_id(root)
    cutoff_forward = cutoff is not None and max_id > 0 and cutoff > max_id
    units: list[dict] = []
    for type_, shipped in SHIPPED_STATUS.items():
        vocab = sdlc_md.status_vocab(type_, root)
        for path in sdlc_md.artifact_files(type_, root):
            text = path.read_text(encoding="utf-8")
            rid = sdlc_md.extract_record_id(path.stem) or path.stem
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)
            if status not in shipped:
                continue
            source_files = _declared_source_files(text) | _git_touched_source_files(root, rid)
            multi_file = len(source_files) > FLOOR_THRESHOLD
            has_planning = _has_planning(text)
            declared = _affects_declared(text)
            kind = _classify(multi_file, has_planning, declared)
            rid_num = sdlc_md.id_number(rid)
            exempt = cutoff is not None and rid_num is not None and rid_num <= cutoff
            waived = project_waived or (_unit_waiver(root, rid) is not None)
            violation = kind is not None and not exempt and not waived
            units.append({
                "id": rid,
                "type": type_,
                "status": status,
                "source_files": len(source_files),
                "multi_file": multi_file,
                "has_planning": has_planning,
                "declared": declared,
                "kind": kind,
                "exempt": exempt,
                "waived": waived,
                "violation": violation,
            })
    units.sort(key=lambda u: u["id"])
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "mode": mode,
        "units": units,
        "summary": {
            "judged": len(units),
            "multi_file": sum(1 for u in units if u["multi_file"]),
            "violations": sum(1 for u in units if u["violation"]),
            "waived": sum(1 for u in units if u["waived"]),
            "exempt": sum(1 for u in units if u["exempt"]),
            # Exempt units that WOULD violate but for the cutoff - kept visible so a grandfather
            # (or a forward) cutoff cannot silently hide the debt it is exempting.
            "exempt_would_violate": sum(1 for u in units
                                        if u["exempt"] and not u["waived"] and u["kind"]),
            "cutoff": cutoff,
            "max_id": max_id,
            "cutoff_forward": cutoff_forward,
        },
    }


# The two whole-project levers plus the per-unit remedy, named at the gate so an operator does not
# have to already know they exist.
REMEDY_ADD = ("plan the unit (one acceptance criterion, a `Verify:` line, or a linked plan) or, if "
              "it is genuinely small, DECLARE its footprint in an `Affects:` field - the floor is "
              "the planning pass, not paperwork")
REMEDY_CUTOFF = ("set `engagement_floor.adopt_after` in sdlc-studio/.config.yaml to grandfather "
                 "pre-adoption ids forward-only (a bare id `238` or prefixed `CR0238`; ids <= it "
                 "are exempt; a cutoff above the highest existing id is refused)")
REMEDY_WAIVER = ("record a waiver (`decisions.py waive --subject rule:engagement-floor:<id> "
                 "--rationale ...` for one unit, or `--subject rule:engagement-floor` for the "
                 "whole project), or set `engagement_floor: judgement` to opt out everywhere")
_MAX_NAMED = 10


def _forward_cutoff_detail(s: dict) -> str:
    return (f"adopt_after {s['cutoff']} exceeds the highest existing id {s['max_id']} - a cutoff "
            f"above it exempts units that do not exist yet (a silent forward disarm), not "
            f"grandfathering. Lower it to <= {s['max_id']}, or set `engagement_floor: judgement` "
            f"to opt out visibly")


def remedy_detail(result: dict) -> str:
    """Gate-facing one-liner: the violation count, the offending ids, and the remedies. A forward
    cutoff is reported as its own failure (it hides the whole project); `judgement` mode is named
    so an advisory warn is never misread; any exempted-would-violate debt stays visible."""
    s = result["summary"]
    if s["cutoff_forward"]:
        return _forward_cutoff_detail(s)
    mode_note = " (advisory - engagement_floor: judgement)" if result["mode"] == "judgement" else ""
    hidden = (f"; {s['exempt_would_violate']} exempt unit(s) would violate (grandfathered by "
              f"adopt_after {s['cutoff']})" if s["exempt_would_violate"] else "")
    n = s["violations"]
    if not n:
        return f"no live violation across {s['judged']} shipped unit(s){hidden}{mode_note}"
    ids = [u["id"] for u in result["units"] if u["violation"]]
    named = ", ".join(ids[:_MAX_NAMED]) + (f" (+{len(ids) - _MAX_NAMED} more)"
                                           if len(ids) > _MAX_NAMED else "")
    return (f"{n} shipped unit(s) below the engagement floor (no plan and not shown small): "
            f"{named}{hidden}{mode_note}. Remedies: {REMEDY_ADD}; or {REMEDY_CUTOFF}; or "
            f"{REMEDY_WAIVER}")


def cmd_check(args: argparse.Namespace) -> int:
    """Run the floor; exit non-zero on a violation unless the project is in judgement mode."""
    result = detect(args.root)
    s = result["summary"]
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if s["cutoff_forward"]:
            print(f"engagement floor: {_forward_cutoff_detail(s)}")
            return 1
        extra = (f", {s['exempt']} exempt" if s["exempt"] else "") + \
                (f", {s['waived']} waived" if s["waived"] else "")
        advisory = " [advisory: judgement mode]" if result["mode"] == "judgement" else ""
        print(f"engagement floor: {s['violations']} violation(s) across {s['judged']} shipped "
              f"unit(s) ({s['multi_file']} multi-file){extra}{advisory}")
        for u in result["units"]:
            if u["violation"]:
                print(f"  {u['id']} ({u['status']}): {u['source_files']} source file(s), "
                      f"{u['kind']}")
        if s["exempt_would_violate"]:
            print(f"  note: {s['exempt_would_violate']} exempt unit(s) would violate "
                  f"(grandfathered by adopt_after {s['cutoff']})")
        if s["violations"]:
            print("Remedies:")
            for r in (REMEDY_ADD, REMEDY_CUTOFF, REMEDY_WAIVER):
                print(f"  - {r}")
    # Judgement mode reports but never fails; a forward cutoff always fails (handled above).
    return 1 if (s["violations"] and result["mode"] != "judgement") else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio deterministic engagement floor.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Flag shipped multi-file units with no plan/AC artefact.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
