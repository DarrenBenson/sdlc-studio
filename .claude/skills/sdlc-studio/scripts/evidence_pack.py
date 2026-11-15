#!/usr/bin/env python3
"""Evidence pack: one release's change-board evidence, built from committed records alone.

`release_cut.py evidence-pack --version X.Y.Z --reports RPT0001,RPT0002` delegates here. The
pack lists each unit the named signed reports delivered, and for each one states what changed
(its title and points), which criteria passed (its ticked criteria and their Verify lines), who
reviewed it independently (the latest verdict of each reviewing seat that `critic.independence`,
the project's one independence rule, accepts), what is known wrong with it (the reports' known issues that name it) and who is
accountable for it (the principal on its report's signature, with the signing date). Known
issues that name no listed change are carried in one release-level list, so none is lost.

Every record is read as a commit holds it (`git show <rev>:<path>`), never from the working
tree and never from `sdlc-studio/.local`: an uncommitted edit to a unit, a report or the verdict
ledger cannot change the pack. A verify run is recorded only in local state, so the pack reads
the committed ticks instead and says so.

A report that is unknown at the revision, carries no signature, or is signed by a blank principal,
one that reads as an agent, or one the committed review ledgers record as an author refuses the
whole build and no pack is written: the text is composed in full before the one write.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import critic  # noqa: E402
import verify_ac  # noqa: E402
from lib import sdlc_md  # noqa: E402

REPORTS_REL = "sdlc-studio/reports"
LEDGER_REL = "sdlc-studio/reviews/critic-verdicts.md"
SELF_CHECKS_REL = f"sdlc-studio/reviews/{critic.SELF_CHECK_FILE}"
#: A release version: semantic, with an optional pre-release or build suffix. It names the
#: pack's file, so nothing that could leave the reports folder is accepted.
_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
_REPORT_RE = re.compile(r"^RPT\d{4,}$")
#: A principal that reads as an agent rather than a person: the word agent (or subagent) anywhere
#: in it, as in `the agent`, `sub-agent`, `an AI agent`, `Agent (builder)`, `agent-<id>` and the
#: typed authorship `name; agent; v1`. A letter on either side is not the word, so a person whose
#: name merely contains the letters (Agnes, Agentha, Reagent) is not matched.
_AGENT_RE = re.compile(r"(?<![a-z])(?:sub)?agents?(?![a-z])", re.IGNORECASE)
#: A criterion heading ticked with a checkbox: `- [x] **AC1:** ...`.
_TICKED_BOX_RE = re.compile(r"^\s*[-*]\s+\[[xX]\]")


class PackError(Exception):
    """A refusal: the pack cannot be built, and nothing is written."""


def pack_rel(version: str) -> str:
    """The pack's path, relative to the project root."""
    return f"{REPORTS_REL}/evidence-pack-{version}.md"


def _git(root: Path, *args: str) -> str | None:
    """A read-only git command's output, run from `root`; None when git or the command fails."""
    try:
        proc = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                              encoding="utf-8", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def _show(root: Path, sha: str, rel: str) -> str | None:
    """The committed text of `rel` (relative to `root`) at `sha`, or None when it is absent."""
    return _git(root, "show", f"{sha}:./{rel}")


def _resolve(root: Path, rev: str) -> str:
    if not rev or rev.startswith("-"):
        raise PackError(f"revision {rev!r} is not a revision")
    sha = (_git(root, "rev-parse", "--verify", "--quiet", "--end-of-options",
                f"{rev}^{{commit}}") or "").strip()
    if not sha:
        raise PackError(f"no commit {rev!r} to read the committed records from")
    return sha


def parse_reports(text: str) -> list[str]:
    """The report ids a comma-separated list names, normalised, in order, each once."""
    out: list[str] = []
    for part in (text or "").split(","):
        rid = part.strip().upper()
        if rid and rid not in out:
            out.append(rid)
    return out


def _val(row: dict, key: str):
    cell = row.get(key)
    return cell.get("value") if isinstance(cell, dict) else cell


def _section(report: dict, key: str) -> list[dict]:
    for sec in report.get("sections") or []:
        if isinstance(sec, dict) and sec.get("key") == key:
            return [r for r in sec.get("rows") or [] if isinstance(r, dict)]
    return []


def _signed(report: dict) -> bool:
    sig = report.get("signature")
    return isinstance(sig, dict) and bool(str(sig.get("signed_at") or "").strip())


def unit_authors(ledger_root: Path, units: list[str]) -> list[str]:
    """The author ids the review ledgers under `ledger_root` record on `units`: the Author cell
    of each live verdict row (`critic.unit_review_rounds`, which drops a superseded row) and of
    each self-check row, with a typed author's name beside its cell, less any typed `human`."""
    want = {sdlc_md.norm_id(u) for u in units if str(u).strip()}
    cells = [str(r.get("author") or "") for unit in sorted(want)
             for r in critic.unit_review_rounds(ledger_root, unit)]
    cells += [str(r.get("author") or "") for r in critic.read_self_checks(ledger_root)
              if sdlc_md.norm_id(str(r.get("unit") or "")) in want]
    out: list[str] = []
    for cell in cells:
        typed = sdlc_md.parse_authorship_value(cell.strip()) or {}
        if typed.get("type") == "human":
            continue
        for name in (cell, typed.get("name") or ""):
            if critic._id(name) and name not in out:
                out.append(name)
    return out


def principal_refusal(signature: dict, authors: list[str] | tuple[str, ...] = ()) -> str | None:
    """Why a signature's principal cannot be named accountable, or None when it names a person.

    Refused: a blank principal (no letter or digit); one holding the word agent; and one that
    `authors` (the ids the committed review ledgers record as a live author of the report's own
    units, `unit_authors`) names, the author `sprint sign` refuses. Such an author, other than a
    typed `human` one, is taken as the agent session that wrote the unit, so a builder's model
    name no word rule can see is caught; an author of any other unit is not refused."""
    principal = str((signature or {}).get("principal") or "").strip()
    if not any(ch.isalnum() for ch in principal):
        return "its signature names no principal, so no person is accountable"
    if _AGENT_RE.search(principal):
        return (f"its signature principal {principal!r} reads as an agent, and an agent is "
                "never the accountable person")
    if any(critic.same_identity(principal, author) for author in authors):
        return (f"its signature principal {principal!r} is recorded as an author of the "
                "report's own units in the committed review ledgers, so it is an authoring "
                "agent and never the accountable person")
    return None


def _read_reports(root: Path, sha: str, ids: list[str], ledger_root: Path) -> list[dict]:
    """Each named report as committed; every refusal is collected before one is raised. A
    report's own units are every unit row its delivered section records, delivered or not, as
    `sprint sign` judges every unit of the run."""
    out, refusals = [], []
    for rid in ids:
        if not _REPORT_RE.match(rid):
            refusals.append(f"{rid}: not a report id")
            continue
        text = _show(root, sha, f"{REPORTS_REL}/{rid}.json")
        if text is None:
            refusals.append(f"{rid}: no committed report {REPORTS_REL}/{rid}.json at {sha[:12]}")
            continue
        try:
            data = json.loads(text)
        except ValueError as exc:
            refusals.append(f"{rid}: the committed report could not be read ({exc})")
            continue
        if not isinstance(data, dict) or str(data.get("report_id") or "").upper() != rid:
            refusals.append(f"{rid}: the committed file does not hold report {rid}")
        elif not _signed(data):
            refusals.append(f"{rid}: the report is not signed, so it is not evidence")
        elif reason := principal_refusal(data["signature"], unit_authors(
                ledger_root, [str(_val(r, "unit_id") or "") for r in _section(data, "delivered")])):
            refusals.append(f"{rid}: {reason}")
        else:
            out.append(data)
    if refusals:
        raise PackError("; ".join(refusals))
    return out


def _delivered(report: dict) -> list[dict]:
    """The report's delivered rows: outcome `delivered`, never planned, dropped or carried."""
    return [r for r in _section(report, "delivered")
            if re.match(r"delivered\b", str(_val(r, "unit_outcome") or "").strip().lower())
            and str(_val(r, "unit_id") or "").strip()]


def _unit_text(root: Path, sha: str, unit: str, row: dict) -> str | None:
    """The unit's committed file: the path its report row cites, else the one file in the
    committed tree named for the unit (a renamed or archived artefact)."""
    cell = row.get("unit_id")
    source = str(cell.get("source") or "") if isinstance(cell, dict) else ""
    if source.endswith(".md") and (text := _show(root, sha, source)) is not None:
        return text
    names = (_git(root, "ls-tree", "-r", "--name-only", sha, "--", "sdlc-studio") or "")
    hits = [n for n in names.splitlines() if Path(n).name.startswith(f"{unit}-")
            and n.endswith(".md")]
    return _show(root, sha, hits[0]) if len(hits) == 1 else None


def _title(unit: str, text: str | None) -> str:
    for line in (text or "").splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            return re.sub(rf"^{re.escape(unit)}\s*[:.-]\s*", "", title) or title
    return "(no committed file found for this unit)"


def _criteria(text: str | None) -> tuple[list[tuple[str, str, str]], list[str]]:
    """(passed, not ticked): each ticked criterion as (id, words, verify), and the ids of the
    rest. A criterion is ticked by a `[x]` box on its heading or a `Verified: yes` line."""
    if not text:
        return [], []
    lines = text.splitlines()
    passed, open_ = [], []
    for block in verify_ac.parse_story(text):
        heading = lines[block.heading_line] if block.heading_line < len(lines) else ""
        ticked = bool(_TICKED_BOX_RE.match(heading)) or (
            str(block.verified_state or "").strip().lower() == "yes")
        if ticked:
            words = verify_ac._criterion_words(block, text)
            passed.append((block.ac_id, words, (block.verifier or "").strip()))
        else:
            open_.append(block.ac_id)
    return passed, open_


def _independent_reviews(ledger_root: Path, unit: str) -> list[dict]:
    """The latest live verdict of each reviewing seat that `critic.independence`, the one
    authority, calls independent: never a self-review, the pre-gate sentinel or a row with no
    recorded author or reviewer."""
    latest: dict[str, dict] = {}
    for row in critic.unit_review_rounds(ledger_root, unit):
        reviewer = str(row.get("reviewer") or "")
        if critic.independence(reviewer, str(row.get("author") or ""),
                               str(row.get("source") or ""))[0]:
            latest[critic._id(reviewer)] = row
    return list(latest.values())


def _known_issues(reports: list[dict]) -> list[tuple[str, str, str]]:
    """Every known-issue row of the reports, as (id, priority, detail), each once, in order."""
    out: list[tuple[str, str, str]] = []
    for rep in reports:
        for row in _section(rep, "known_issues"):
            issue = tuple(str(_val(row, k) or "").strip()
                          for k in ("issue_id", "issue_priority", "issue_detail"))
            if (issue[0] or issue[2]) and issue not in out:
                out.append(issue)
    return out


def _names(unit: str, issue: tuple[str, str, str]) -> bool:
    """True when the issue's id or detail names the unit as a whole id, not a prefix of one."""
    pattern = re.compile(rf"(?<![A-Za-z0-9]){re.escape(unit)}(?![A-Za-z0-9])", re.IGNORECASE)
    return bool(pattern.search(issue[0]) or pattern.search(issue[2]))


def _issue_text(issue: tuple[str, str, str]) -> str:
    iid, priority, detail = issue
    label = f"{iid} ({priority})" if priority else iid
    return f"{label}: {detail.rstrip('.') or 'no detail recorded'}."


def _entry(unit: str, rid: str, row: dict, text: str | None, reviews: list[dict],
           issues: list[tuple[str, str, str]], signature: dict) -> list[str]:
    title = _title(unit, text)
    points = _val(row, "unit_points")
    pts = f"{points} point{'' if points == 1 else 's'}" if points not in (None, "") else (
        "points not recorded")
    passed, open_ = _criteria(text)
    out = [f"### {unit}: {title}", "", f"- What changed: {title} ({pts})."]
    if passed:
        out.append("- Criteria passed:")
        out += [f"  - {ac}: {words} Verify: `{verify}`" if verify else f"  - {ac}: {words}"
                for ac, words, verify in passed]
    else:
        out.append("- Criteria passed: none ticked.")
    if open_:
        out.append(f"- Criteria not ticked: {', '.join(open_)}.")
    seen = "; ".join(f"{r['reviewer'].strip()} {str(r.get('verdict') or '').strip().upper()} "
                     f"({str(r.get('date') or '').strip()})" for r in reviews)
    out.append(f"- Independent review: {seen or 'none recorded'}.")
    if issues:
        out.append("- Known issues:")
        out += [f"  - {_issue_text(i)}" for i in issues]
    else:
        out.append("- Known issues: none recorded.")
    signed_on = str(signature.get("signed_at") or "").strip()[:10]
    out.append(f"- Accountable: {str(signature.get('principal')).strip()}, who signed its report "
               f"on {signed_on}.")
    out.append(f"- Report: {rid}.")
    return out + [""]


def build_pack(root: Path | str, version: str, reports: list[str], rev: str = "HEAD") -> str:
    """The pack's markdown, from the records committed at `rev`; raises PackError to refuse."""
    root = Path(root)
    if not _VERSION_RE.match(version or ""):
        raise PackError(f"version {version!r} is not a release version such as 6.4.0")
    if not reports:
        raise PackError("name at least one signed report with --reports")
    sha = _resolve(root, rev)
    body: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        # The ledgers' one reader takes a project root, so it is handed the COMMITTED ledgers in
        # a scratch root of its own, so a superseded row is dropped by the reader the review
        # rounds are counted with (`critic.unit_review_rounds`).
        for rel in (LEDGER_REL, SELF_CHECKS_REL):
            sdlc_md.atomic_write(Path(tmp) / rel, _show(root, sha, rel) or "")
        data = _read_reports(root, sha, reports, Path(tmp))
        changes = [(str(rep["report_id"]).upper(), rep["signature"], row,
                    sdlc_md.norm_id(str(_val(row, "unit_id")).strip()))
                   for rep in data for row in _delivered(rep)]
        issues = _known_issues(data)
        tied = {i for i in issues if any(_names(unit, i) for _, _, _, unit in changes)}
        for rid, sig, row, unit in changes:
            body += _entry(unit, rid, row, _unit_text(root, sha, unit, row),
                           _independent_reviews(Path(tmp), unit),
                           [i for i in issues if _names(unit, i)], sig)
    head = [
        f"# Evidence pack: release {version}", "",
        f"Built by `release_cut.py evidence-pack` from the records committed at `{sha[:12]}`, "
        f"over the signed reports {', '.join(reports)}. Uncommitted edits and the tool's local "
        "state are not read.", "",
        "Passed criteria are each unit's ticked criteria and their Verify lines, as its "
        "committed file holds them. A verify run is recorded only in local state, which is not "
        "a committed record, so this pack does not read one.", "",
        "An independent review is the latest verdict of each reviewing seat whose reviewer is "
        "not the unit's recorded author, never a self-review or a unit closed before the "
        "review gate.", "",
        "## Changes", ""]
    if not body:
        body = ["The named reports record no delivered unit.", ""]
    rest = [f"- {_issue_text(i)}" for i in issues if i not in tied] or ["- None recorded."]
    tail = ["## Known issues not tied to one change", "",
            "The reports' known issues whose id and detail name none of the changes above.", "",
            *rest, "",
            "## Accountability", "",
            "Each change names the principal recorded on its report's signature, with the signing "
            "date. No record names an accountable person per unit, so every change of a report "
            "names that report's signer; a blank principal, one that reads as an agent or one the "
            "review ledgers record as an author of that report's own units refuses the pack.",
            ""]
    return "\n".join(head + body + tail).rstrip("\n") + "\n"


def write_pack(root: Path | str, version: str, reports: list[str], rev: str = "HEAD") -> Path:
    """Build the pack in full, then write it once; a refusal raises before anything is written."""
    text = build_pack(root, version, reports, rev)
    path = Path(root) / pack_rel(version)
    sdlc_md.atomic_write(path, text)
    return path
