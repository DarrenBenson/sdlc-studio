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
  * UNDERSTATEMENT IN A SHARED COMMIT was a disclosed limit, now closable with a commit-id
    convention. When a unit shares its commit with another judged id, git cannot attribute a file
    to one id among several, so a bare co-named subject is still skipped. But a `Refs: <id>` trailer
    in the commit body is an explicit statement of which id owns the change: the git leg reads it
    and attributes that commit's files to each id a trailer names, even in a shared commit. So the
    understatement IS caught once the owning unit carries a `Refs:` trailer. Absent the trailer the
    shared commit is still skipped (the pre-convention behaviour, unchanged); the `check-commit-msg`
    hook nudges an author to add one.

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

The git leg does not attribute a BATCH commit (one whose SUBJECT names several ids) to any of them
UNLESS a `Refs: <id>` trailer names the id: it otherwise cannot know which file belongs to which id,
so a bare batch commit feeds no id's count (the declared `Affects` carries a genuinely multi-file
unit instead). The batch test looks at the subject line only, so a body `Refs:` trailer can only ADD
attribution to the ids it names, never remove the solo cross-check from a commit whose subject names
one id - the explicit per-id ownership statement lifts the skip, it never imposes one.

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
# A `Refs:` commit trailer line. Grammar: a line beginning `Refs:` (case-insensitive), then one or
# more judged ids separated by commas and/or whitespace; repeatable across lines. A trailer is an
# explicit statement of which id owns the change, so the git leg trusts it to attribute a shared
# commit's files per id where a bare co-named subject cannot be apportioned.
_REFS_LINE_RE = re.compile(r"^[ \t]*Refs:[ \t]*(.+)$", re.MULTILINE | re.IGNORECASE)
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


def _refs_ids(message: str) -> set[str]:
    """The judged-type ids named in a commit's `Refs:` trailer line(s), normalised. Empty when the
    message carries no such trailer. Both the comma-list and repeated-line spellings accumulate, so
    `Refs: US0301, US0302` and two `Refs:` lines mean the same set."""
    ids: set[str] = set()
    for m in _REFS_LINE_RE.finditer(message):
        for i in _JUDGED_ID_RE.findall(m.group(1)):
            ids.add(sdlc_md.norm_id(i))
    return ids


def _git_touched_source_files(root: Path, rid: str) -> set[str]:
    """Source files the commits mentioning `rid` touched (`git log --grep`). Empty when not a git
    repo or git is unavailable - the floor then rests on the declared `Affects` alone.

    A commit's files attribute to `rid` when EITHER a `Refs: <id>` trailer names `rid` (an explicit
    per-id ownership statement, so a shared commit becomes attributable), OR the commit SUBJECT LINE
    names at most one judged id (the original solo cross-check). A BATCH commit - a subject naming
    more than one judged id, with no `Refs:` trailer naming `rid` - is still skipped: git cannot
    apportion its files by id, so attributing the whole set to each would inflate every id in it.

    The batch test reads the SUBJECT LINE only, never the body. This is what makes a `Refs:` trailer
    strictly ADDITIVE: because a body `Refs:` line cannot enlarge the subject's judged-id count, it
    can never turn a solo-subject commit into a pseudo-batch and so strip the subject id's own
    attribution - the failure that would void the solo-id cross-check for the conventional see-also
    use of `Refs:`. A trailer only ever raises a count, never lowers one, for any body content; and
    each id it names gets the commit's FULL file set (never a divided share), so it cannot understate
    a real footprint either.
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
        refs = _refs_ids(message)
        subject = message.split("\n", 1)[0]
        subject_ids = {sdlc_md.norm_id(i) for i in _JUDGED_ID_RE.findall(subject)}
        # Attribute when a `Refs:` trailer names this id (explicit ownership of a shared commit),
        # OR when the SUBJECT LINE names at most one judged id (the solo cross-check). The batch
        # test reads the subject ONLY, never the body: a body `Refs:` line can then only ADD
        # attribution (raise-direction) - it can never inflate a solo-subject commit into a
        # pseudo-batch and so strip the subject id's own count. A genuine multi-id SUBJECT with no
        # trailer naming us is still skipped (git cannot apportion its files). So a trailer can
        # raise a count but never lower one, for any body content.
        if norm not in refs and len(subject_ids) > 1:
            continue
        for line in file_blob.splitlines():
            f = line.strip()
            if f and Path(f).suffix in SOURCE_SUFFIXES:
                files.add(f)
    return files


def _git_touched_by_id(root: Path) -> dict[str, set[str]]:
    """One pass over history returning {id: touched source files} for EVERY judged id at once.

    `_git_touched_source_files` answers the same question for a single id, by running
    `git log --grep` over the whole history. `detect` needs the answer for every shipped unit,
    so it ran that once per unit: 842 git subprocesses on this repo, 10.5s of an 11.0s lane,
    all of it spent waiting on a process that re-read the same history each time.

    The attribution rule is unchanged - a commit's files attach to an id when a `Refs:` trailer
    names it, or when the SUBJECT names at most one judged id - and is applied here per commit
    rather than per id.

    One deliberate difference from the per-id function: candidate ids come from the judged-id
    regex (which requires word boundaries) rather than from git's `--grep` substring match. A
    commit mentioning `US02845` or `XUS0284` matched the grep and had its files attributed to
    `US0284`; here it does not. That is stricter, and correct - but it IS a difference, so
    `test_batch_and_single_id_git_attribution_agree` pins the two against each other on real
    commit shapes rather than leaving the claim to this comment.

    Two limits, stated rather than left to be found. A commit message containing a literal
    record separator (`\\x1e`) splits its own record, so an id in the resulting fragment loses
    attribution here but keeps it per-id; and the single timeout now disables the git
    cross-check for EVERY id at once rather than for one, so on a very large history the floor
    silently falls back to declared `Affects` alone. Both are conservative - they can only
    UNDER-attribute, never inflate a unit's footprint - which is the safe direction for a gate
    that blocks on the result.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=false", "log",
             f"--format={_REC}%B{_MSGEND}", "--name-only"],
            capture_output=True, text=True, timeout=_GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return {}
    if out.returncode != 0:
        return {}
    by_id: dict[str, set[str]] = {}
    for record in out.stdout.split(_REC):
        if _MSGEND not in record:
            continue
        message, _, file_blob = record.partition(_MSGEND)
        mentioned = {sdlc_md.norm_id(i) for i in _JUDGED_ID_RE.findall(message)}
        if not mentioned:
            continue
        files = {f for f in (line.strip() for line in file_blob.splitlines())
                 if f and Path(f).suffix in SOURCE_SUFFIXES}
        if not files:
            continue
        refs = _refs_ids(message)
        subject_ids = {sdlc_md.norm_id(i)
                       for i in _JUDGED_ID_RE.findall(message.split("\n", 1)[0])}
        batch = len(subject_ids) > 1
        for rid in mentioned:
            if batch and rid not in refs:
                continue    # git cannot apportion a batch commit's files by id
            by_id.setdefault(rid, set()).update(files)
    return by_id


class StagedIndexUnreadable(RuntimeError):
    """git could not be asked what is staged. Raised rather than returned so no caller can
    treat an unreadable index as an empty one and print a clean."""


def _staged_paths(root: Path) -> list[str] | None:
    """Repo-relative paths in the index (`git diff --cached`), or None when git could not be
    asked at all.

    THE TWO CASES ARE NOT THE SAME and must not share a return value. An empty list is git
    ANSWERING that nothing is staged; None is git failing to answer. Both used to be `[]`, so
    a lane that could not read the index printed the same clean line as a lane that read it
    and found nothing - a false clean on the one signal this leg exists to provide. That is
    the defect class the floor itself was built to catch, in the floor."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=false", "diff", "--cached",
             "--name-only"], capture_output=True, text=True, timeout=_GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]


def _pending_touched_by_id(root: Path) -> dict[str, set[str]]:
    """{id: source files THIS commit is about to attribute to it}, read from the index.

    Why this exists. The git leg reads `git log`, so a commit's files attach to a
    unit only once that commit exists. The pre-commit gate could therefore never see a
    violation the commit it is gating was about to create: the floor reported clean, the
    commit landed, and the same check immediately afterwards reported new violations in
    files nothing had touched.

    What is available at pre-commit time is the INDEX, and that is what this reads. The
    ids are those whose own artefact file is staged - a delivery commit stages the
    artefact that reaches Done/Fixed/Complete alongside the code - and each gets this
    commit's staged source files, which is what the history leg will attribute to them the
    moment the commit exists.

    What is NOT available is the commit MESSAGE. Git writes `COMMIT_EDITMSG` AFTER the
    pre-commit hook runs, so at hook time that file still holds the previous commit's
    message; reading it would judge the wrong commit. A unit this commit names in prose
    alone, staging no artefact for it, therefore cannot be judged until the commit exists.
    That case remains one commit behind, is stated at the lane, and has its own test.

    One deliberate asymmetry with the history leg, in the strict direction: the history leg
    skips a commit whose SUBJECT names more than one judged id, because it cannot apportion
    the files. The subject is unknown here, so nothing is skipped. A unit escaping only
    through that blind spot is refused here instead. The blind spot is a disclosed limit of
    the git leg, not an entitlement, and the remedy is the floor's ordinary one: one
    acceptance criterion, or a declared footprint.
    """
    staged = _staged_paths(root)
    if staged is None:
        raise StagedIndexUnreadable(
            "the staged index could not be read, so this commit's own attribution is unknown")
    if not staged:
        return {}
    files = {f for f in staged if Path(f).suffix in SOURCE_SUFFIXES}
    if not files:
        return {}
    ids: set[str] = set()
    for path in staged:
        if Path(path).suffix.lower() != ".md":
            continue
        rid = sdlc_md.extract_record_id(Path(path).stem)
        if not rid:
            continue
        norm = sdlc_md.norm_id(rid)
        if _JUDGED_ID_RE.fullmatch(norm):
            ids.add(norm)
    return {rid: set(files) for rid in ids}


def _declared_source_files(text: str) -> set[str]:
    """The source files a unit declares in its `Affects` field (doc/non-source paths dropped).

    Recognises files through `_declared_file_tokens` - the SAME recogniser `_affects_declared`
    uses - so the declared boolean and this count never disagree about what is a real footprint.
    A real file that is not a code file (a `Makefile`, a `.md` doc) is a valid
    declaration but not a source change, so it is dropped here by the source-suffix filter, not by
    a second, narrower file recogniser."""
    return {f for f in _declared_file_tokens(text) if Path(f).suffix in SOURCE_SUFFIXES}


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


def _declared_file_tokens(text: str) -> list[str]:
    """The tokens in the unit's `Affects` field that name a real, checkable file, in declared
    order. This is the ONE recogniser both `_affects_declared` (the declared boolean) and
    `_declared_source_files` (the file count) share, so they can never disagree about what counts
    as a real footprint. Each token is stripped of a trailing `(parenthetical)` and
    backticks; an unfilled `{{placeholder}}` and any token `_is_file_token` rejects as prose
    (`n/a`, `various`) or a version string (`v1.2`) is dropped."""
    val = sdlc_md.extract_field(text, "Affects")
    if val is None:
        return []
    out: list[str] = []
    for tok in val.split(","):
        tok = re.sub(r"\s*\(.*\)\s*$", "", tok.strip()).strip().strip("`").strip()
        if tok and "{{" not in tok and _is_file_token(tok):
            out.append(tok)
    return out


def _affects_declared(text: str) -> bool:
    """True when the unit's `Affects` field names at least one real file path. A blank field, an
    unfilled `{{placeholder}}`, or bare prose (`n/a`, `various`) is NOT a declaration: it cannot be
    held to a footprint, so it is omission-equivalent and must not satisfy the floor. (Does not
    match the story template's unrelated `**Affects production runtime:**` boolean - `extract_field`
    anchors on `Affects:`.)"""
    return bool(_declared_file_tokens(text))


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


def detect(repo_root: Path | str, include_staged: bool = False) -> dict:
    """Per-unit engagement-floor state over the shipped story/bug/CR units.

    Returns {"mode": floor|judgement, "units": [...], "summary": {...}}. Each judged unit carries
    its source-file count, whether it is multi-file, whether it has a planning artefact, whether it
    DECLARED its footprint, its violation kind, and whether it is exempt (cutoff) or waived. A live
    violation is a would-violate unit that is neither exempt nor waived. An adopt_after cutoff above
    the highest existing id is a silent forward disarm and is flagged (`cutoff_forward`).

    `include_staged` folds the pending commit in (`_pending_touched_by_id`), so a violation the
    commit in hand is about to create is visible BEFORE it lands rather than one commit later.
    Each unit then carries `staged_new`: True when it is clean on committed evidence and a
    violation once this commit's staged files are attributed. Default off, so every existing
    caller sees exactly what it saw before.
    """
    root = Path(repo_root)
    mode, cutoff = _mode_and_cutoff(root)
    project_waived = decisions.waiver_for(root, WAIVER_RULE) is not None
    max_id = _max_judged_id(root)
    cutoff_forward = cutoff is not None and max_id > 0 and cutoff > max_id
    git_touched = _git_touched_by_id(root)   # ONE pass, not one `git log --grep` per unit
    staged_unreadable = False
    try:
        pending = _pending_touched_by_id(root) if include_staged else {}
    except StagedIndexUnreadable:
        pending, staged_unreadable = {}, True
    units: list[dict] = []
    for type_, shipped in SHIPPED_STATUS.items():
        vocab = sdlc_md.status_vocab(type_, root)
        for path in sdlc_md.artifact_files(type_, root):
            text = path.read_text(encoding="utf-8")
            rid = sdlc_md.extract_record_id(path.stem) or path.stem
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)
            if status not in shipped:
                continue
            norm = sdlc_md.norm_id(rid)
            committed = _declared_source_files(text) | git_touched.get(norm, set())
            source_files = committed | pending.get(norm, set())
            multi_file = len(source_files) > FLOOR_THRESHOLD
            has_planning = _has_planning(text)
            declared = _affects_declared(text)
            kind = _classify(multi_file, has_planning, declared)
            rid_num = sdlc_md.id_number(rid)
            exempt = cutoff is not None and rid_num is not None and rid_num <= cutoff
            waived = project_waived or (_unit_waiver(root, rid) is not None)
            violation = kind is not None and not exempt and not waived
            # Was it already a violation without this commit? The difference is what the
            # commit in hand CREATES, and is the only thing the pending lane reports.
            committed_kind = _classify(len(committed) > FLOOR_THRESHOLD, has_planning, declared)
            committed_violation = committed_kind is not None and not exempt and not waived
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
                "staged_new": violation and not committed_violation,
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
            # Whether the pending commit was folded in at all, and how many violations it
            # creates. `staged_evaluated` false means these zeros are "not looked at",
            # never "looked at and found none".
            "staged_evaluated": include_staged,
            "staged_new": sum(1 for u in units if u["staged_new"]),
            "staged_unreadable": staged_unreadable,
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
        # Say what the green means. It is "no ALREADY-COMMITTED unit violates", not "this
        # commit is compliant" - the pending commit is judged by `check --pending`.
        return (f"no live violation across {s['judged']} shipped unit(s) on committed "
                f"evidence{hidden}{mode_note}")
    ids = [u["id"] for u in result["units"] if u["violation"]]
    named = ", ".join(ids[:_MAX_NAMED]) + (f" (+{len(ids) - _MAX_NAMED} more)"
                                           if len(ids) > _MAX_NAMED else "")
    return (f"{n} shipped unit(s) below the engagement floor (no plan and not shown small): "
            f"{named}{hidden}{mode_note}. Remedies: {REMEDY_ADD}; or {REMEDY_CUTOFF}; or "
            f"{REMEDY_WAIVER}")


def _subject_line(message: str) -> str:
    """The commit subject: the first line that is neither blank nor a git comment (`#`). git may
    scaffold a message file with instructions and, in verbose mode, a diff; both start `#`."""
    for line in message.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def _strip_comments(message: str) -> str:
    """Drop git comment lines (`#`) so a `Refs:` in the scaffolding cannot be mistaken for one the
    author wrote, and a commented-out subject cannot be mistaken for the real one."""
    return "\n".join(ln for ln in message.splitlines() if not ln.lstrip().startswith("#"))


def check_commit_message(message: str, *, strict: bool = False) -> tuple[int, str | None]:
    """The commit-msg hook's decision, as pure logic (so it is unit-testable without a hook).

    Warns when the subject names more than one judged id and a `Refs:` trailer does not cover them
    all - the case where the engagement floor's git leg would otherwise skip the commit and an
    understated `Affects` would stand. The nudge is to add `Refs: <id>` per owning id.

    Returns (exit_code, warning). A clean message returns (0, None). A warning returns its text and
    exits 1 only under `strict` (an explicit opt-in); otherwise it exits 0 - the hook advises, it
    does not block on a heuristic. Any message this cannot parse returns (0, None): the hook must
    never block a legitimate commit on its own confusion.
    """
    body = _strip_comments(message)
    subject = _subject_line(message)
    subject_ids = {sdlc_md.norm_id(i) for i in _JUDGED_ID_RE.findall(subject)}
    if len(subject_ids) <= 1:
        return 0, None  # solo or no judged id: the floor handles it, nothing to nudge
    uncovered = sorted(subject_ids - _refs_ids(body))
    if not uncovered:
        return 0, None  # every co-named id has an explicit Refs trailer
    warning = (
        "commit subject names more than one work-item id but "
        + ("some lack" if len(uncovered) < len(subject_ids) else "none carry")
        + " a Refs: trailer: " + ", ".join(uncovered) + ". Without it the engagement floor cannot "
        "attribute this commit's files per id (a shared commit is skipped), so an understated "
        "Affects would go uncaught. Add a trailer line per owning id, e.g. `Refs: "
        + uncovered[0] + "`."
    )
    return (1 if strict else 0), warning


def cmd_check_commit_msg(args: argparse.Namespace) -> int:
    """Read a commit message file (the argument git passes a commit-msg hook) and apply
    `check_commit_message`. Degrades honestly: an unreadable file is not the author's fault, so it
    warns to stderr and exits 0 (never blocks) regardless of strict."""
    try:
        message = Path(args.file).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"engagement floor (commit-msg): could not read {args.file}: {exc}", file=sys.stderr)
        return 0
    code, warning = check_commit_message(message, strict=args.strict)
    if warning:
        print(f"engagement floor (commit-msg): {warning}", file=sys.stderr)
        if code != 0:
            print("  (blocked by strict mode; commit with --no-verify to override, or add Refs:)",
                  file=sys.stderr)
    return code


#: What `--pending` can and cannot see, printed at the lane rather than left in a docstring.
#: A green lane that reads as "this commit is compliant" would be the same overclaim the
#: standing lane made before BG0251.
PENDING_SCOPE = (
    "Scope: the STAGED index. Git writes the commit message after a pre-commit hook runs, "
    "so this lane cannot read the message it is gating - a unit named only in that message, "
    "whose artefact this commit does not stage, is still judged one commit later."
)


def _cmd_check_pending(result: dict) -> int:
    """`check --pending`: report only what the commit in hand CREATES.

    Deliberately silent about violations that already exist on committed evidence - the
    standing gate lane fails on those, and a lane that repeats them teaches an author to
    read past both.
    """
    s = result["summary"]
    if result["summary"].get("staged_unreadable"):
        print("engagement floor (pending commit): REFUSED - the staged index could not be "
              "read, so what this commit attributes is unknown. This is not a clean: the lane "
              "reports nothing rather than reporting no violations.")
        return 1
    new = [u for u in result["units"] if u["staged_new"]]
    advisory = result["mode"] == "judgement"
    if not new:
        print(f"engagement floor (pending commit): no new violation from the "
              f"{s['judged']} shipped unit(s) judged. {PENDING_SCOPE}")
        return 0
    note = " [advisory: judgement mode]" if advisory else ""
    print(f"engagement floor (pending commit): {len(new)} unit(s) this commit puts below "
          f"the floor{note}: " + ", ".join(u["id"] for u in new))
    for u in new:
        print(f"  {u['id']} ({u['status']}): {u['source_files']} source file(s) once this "
              f"commit lands, {u['kind']}")
    print("Remedies:")
    for r in (REMEDY_ADD, REMEDY_CUTOFF, REMEDY_WAIVER):
        print(f"  - {r}")
    print(PENDING_SCOPE)
    return 0 if advisory else 1


def cmd_check(args: argparse.Namespace) -> int:
    """Run the floor; exit non-zero on a violation unless the project is in judgement mode."""
    result = detect(args.root, include_staged=args.pending)
    s = result["summary"]
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if s["cutoff_forward"]:
            print(f"engagement floor: {_forward_cutoff_detail(s)}")
            return 1
        if args.pending:
            return _cmd_check_pending(result)
        extra = (f", {s['exempt']} exempt" if s["exempt"] else "") + \
                (f", {s['waived']} waived" if s["waived"] else "")
        advisory = " [advisory: judgement mode]" if result["mode"] == "judgement" else ""
        print(f"engagement floor: {s['violations']} violation(s) across {s['judged']} shipped "
              f"unit(s) on committed evidence ({s['multi_file']} multi-file)"
              f"{extra}{advisory}")
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
    if args.pending:   # the --format json path; the text path returned above
        return 1 if (s["staged_new"] and result["mode"] != "judgement") else 0
    return 1 if (s["violations"] and result["mode"] != "judgement") else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio deterministic engagement floor.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Flag shipped multi-file units with no plan/AC artefact.")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.add_argument("--pending", action="store_true",
                   help="Judge the commit in hand: fold the staged index in and report only "
                        "the violations THIS commit would create (the pre-commit lane).")
    c.set_defaults(func=cmd_check)
    m = sub.add_parser("check-commit-msg",
                       help="Commit-msg hook: warn on a multi-id subject with no Refs: trailer.")
    m.add_argument("file", help="Path to the commit message file git passes the hook.")
    m.add_argument("--strict", action="store_true",
                   help="Block (exit 1) instead of warning - an explicit opt-in.")
    m.set_defaults(func=cmd_check_commit_msg)
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
