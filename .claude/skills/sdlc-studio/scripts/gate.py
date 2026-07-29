#!/usr/bin/env python3
"""Portable, ecosystem-neutral CI quality gate.

One command that runs the deterministic checks (conformance, reconcile drift, validate,
constitution, integrity) over the artifact graph, prints a consolidated pass/fail, and
exits non-zero only when a *blocking* check fails. No network, no CI/cloud assumption -
runnable as a bare shell step in any CI (GitHub Actions, GitLab, Jenkins, a pre-commit
hook). `--only` / `--skip` select checks. `--release` is the pre-tag form: the same gate plus
an EXECUTING acceptance-criteria verify pass, as one exit code.

Each check is a callable `fn(root) -> {"count": int, "blocking": bool, "detail": str}`;
the registry is injectable so the aggregation logic is testable without a full repo.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def _conformance(root: str, changed: bool = False,
                 scope_ids: "set[str] | None" = None) -> dict:
    import conformance
    result = conformance.detect_conformance(root, changed=changed, scope_ids=scope_ids)
    # A repo-global failure (one uncatalogued command, a missing index) is attributed ONCE
    # rather than charged to every judged unit - but it must still block, or improving the
    # report would quietly weaken the gate. Count it as its own finding. `changed` narrows the
    # per-unit half ONLY: this sum keeps the repo-wide half at full strength, so scoping cannot
    # become a way to pass a gate over a repo-wide failure.
    n = result["summary"]["nonconformant"] + result["summary"].get("global_failures", 0)
    # Name the remedies inline (the adopt_after cutoff + the verify_ac backfill) and flag
    # whether the shape reads as pre-existing forward-only debt vs a fresh regression, so a
    # grown-but-accepted count does not read as a new breakage.
    return {"count": n, "blocking": True, "detail": conformance.remedy_detail(result)}


def _reconcile(root: str) -> dict:
    import reconcile
    rr = Path(root).resolve()
    # ONE sweep, `reconcile.detect_all`, shared with `reconcile detect` itself - never a
    # second list assembled here. This lane used to name two of the nine drift sources, and
    # an enumerated list silently exempts what it forgot: `meta-index`, `epic-breakdown`
    # (including ticked-early, the direction that masks unfinished work), `epic-points`,
    # `link-asymmetry`, linked-epics and `undecomposed` were all invisible, so a tree on
    # which `reconcile detect` exited 1 passed the pre-commit hook and CI. Sharing the sweep
    # is what makes that unrepeatable: a detector added to the sweep is counted here the day
    # it lands, with nobody having to remember this call site.
    _per_type, drift = reconcile.detect_all(rr)
    total = len(drift)
    #
    # Only the items apply can clear are COUNTED. One blocked behind another gate is real drift
    # and is reported in the detail, but it does not block, because the committer who trips it is
    # generally not the person who can clear it: an RFC waiting on an open decision needs that
    # decision made (or an override recorded), which is somebody else's call on somebody else's
    # timetable. Blocking every commit in the repo on a pending operator decision is friction that
    # gets the gate bypassed, and a bypassed gate enforces nothing.
    #
    # NOT because such an item is unclearable - it plainly is clearable, and by a commit: the
    # refusal message names both remedies. This is a friction trade, and the cost is real - a
    # delivered request blocked behind a resolvable gate reports PASS, which is a narrowed form of
    # the very bug this kind exists to kill. `reconcile detect` still exits 1 on it. Anyone
    # widening this should weigh that cost, not assume there is nothing to weigh.
    #
    # DERIVED from the items, not from a second call to the one detector that happens to
    # produce them today: `blocked_by` is the property that means "another gate owns this",
    # and any future detector setting it is carved out automatically.
    blocked = sum(1 for d in drift if d.get("blocked_by"))
    total -= blocked
    detail = f"{total} drift item(s)"
    if blocked:
        detail += f" (+{blocked} awaiting another gate, not blocking)"
    return {"count": total, "blocking": True, "detail": detail}


def _index_derived(root: str) -> dict:
    import reconcile
    issues = reconcile.index_derived_issues(Path(root).resolve())
    return {"count": len(issues), "blocking": True,
            "detail": "; ".join(issues) if issues else "indexes are derived output"}


def _validate(root: str, changed: bool = False) -> dict:
    """Structural validation over the artefact tree.

    `changed` narrows what is JUDGED to the artefacts in this working tree's diff. Everything
    is still checked and everything found is still counted somewhere: an untouched error lands
    in the advisory tally and is named in the detail, so a scoped PASS states the debt it did
    not judge instead of hiding it. A git probe that cannot answer judges the whole workspace.
    """
    import validate
    rr = Path(root).resolve()
    scope = validate.changed_artifact_paths(rr) if changed else None
    errors = advisory = judged = untouched = 0
    advisory_files: list[str] = []
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, rr):
            n = sum(1 for v in validate.validate_file(path, type_, rr)
                    if v["severity"] == "error")
            if scope is not None and path.resolve() not in scope:
                untouched += 1
                advisory += n
                if n:
                    advisory_files.append(path.name)
            else:
                judged += 1
                errors += n
    detail = f"{errors} validation error(s)"
    if scope is not None:
        detail += (f" over {judged} changed artefact(s); "
                   f"{untouched} outside the diff not judged here")
        if advisory:
            detail += (f", {advisory} of them carrying an advisory error "
                       f"({_name_list(advisory_files)})")
        detail += " - `--release` judges the whole workspace"
    elif changed:
        detail += (" (no diff to scope to - a clean tree, or the git probe could not answer"
                   " - so the WHOLE workspace was judged)")
    return {"count": errors, "blocking": True, "detail": detail}


def _constitution(root: str) -> dict:
    import constitution
    rep = constitution.check_constitution(root)
    v = len(rep["violations"])
    # Only blocking when the project opts in (constitution.enforce: true).
    return {"count": v, "blocking": bool(rep["enforced"]),
            "detail": (f"{v} violation(s)" + ("" if rep["enforced"] else " (advisory)"))
            if rep["exists"] else "no constitution"}


def _integrity(root: str) -> dict:
    import integrity
    e = integrity.detect_integrity(root)["summary"]["errors"]
    return {"count": e, "blocking": True, "detail": f"{e} integrity error(s)"}


def _duplicate_id(root: str) -> dict:
    import next_id
    import reconcile
    files = next_id.detect_collisions(root)["count"]      # two files claim one id
    rows = reconcile.detect_duplicate_rows(root)["count"]  # one index lists an id twice
    total = files + rows
    detail = f"{total} duplicate id(s)" + (f" ({files} file, {rows} index-row)" if total else "")
    return {"count": total, "blocking": True, "detail": detail}


def _provenance(root: str) -> dict:
    import provenance
    r = provenance.check(root)
    n = len(r["findings"])
    # `enforced` covers the ADVISORY class (an unstamped artefact). It does not cover a finding
    # the checker itself marks blocking - an artefact it could not READ, which is a gap in the
    # census rather than a missing stamp, and is blocking whatever the enforce setting says.
    # Deriving from the findings keeps this lane and the checker on one answer.
    unreadable = [f for f in r["findings"] if f.get("blocking")]
    blocking = bool(r["enforced"] or unreadable)
    detail = f"{n} unstamped artifact(s) ({'enforced' if r['enforced'] else 'advisory'})"
    if unreadable:
        detail += f"; {len(unreadable)} unreadable - the census could not see them"
    return {"count": n, "blocking": blocking, "detail": detail}


def _disclosure(root: str) -> dict:
    import disclosure
    r = disclosure.check(root)
    n = len(r["findings"])
    detail = "N/A (not the skill repo)" if not r["applicable"] else f"{n} advisory finding(s)"
    return {"count": n, "blocking": False, "detail": detail}  # advisory: never blocks


def _doc_freshness(root: str) -> dict:
    import doc_freshness
    r = doc_freshness.check(root)
    n = len(r["findings"])
    detail = "N/A (not the skill repo)" if not r["applicable"] else (
        f"{n} stale LATEST.md claim(s)" if n else "LATEST.md fresh")
    return {"count": n, "blocking": False, "detail": detail}  # advisory: never blocks


def _doc_coverage(root: str) -> dict:
    import doc_coverage
    r = doc_coverage.check(root)
    blocking = sum(1 for f in r["findings"] if f["blocking"])
    advisory = len(r["findings"]) - blocking
    detail = ("N/A (not the skill repo)" if not r["applicable"]
              else f"{blocking} undocumented" + (f" (+{advisory} advisory)" if advisory else ""))
    return {"count": blocking, "blocking": True, "detail": detail}


def _engagement_floor(root: str) -> dict:
    """Blocking standard-gate lane: no shipped multi-file unit may reach a done outcome with no
    planning artefact (an AC, a Verify line, or a linked plan). Deterministic - a source-file
    count (declared Affects UNION the git cross-check) and a presence check, no model judgement.

    Advisory, never blocking, when the project sets `engagement_floor: judgement` - the documented
    project-global opt-out. A per-unit or project waiver, or the `adopt_after` cutoff, are the
    other auditable ways past; a plain --skip deselects the lane visibly, it does not pass it.
    """
    import engagement_floor
    result = engagement_floor.detect(root)
    s = result["summary"]
    # A forward cutoff (adopt_after above the highest existing id) silently disarms the whole
    # floor - it must FAIL loudly, even in judgement mode, because it is a config error, not the
    # sanctioned opt-out (that is judgement mode, which stays visible).
    if s["cutoff_forward"]:
        return {"count": 1, "blocking": True, "detail": engagement_floor.remedy_detail(result)}
    blocking = result["mode"] != "judgement"
    return {"count": s["violations"], "blocking": blocking,
            "detail": engagement_floor.remedy_detail(result)}


#: Extensions mutation.py has a language profile for. A changed file outside this set cannot
#: carry mutation evidence, so it is not counted as an uncovered surface.
_MUTATABLE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".go"}


def _is_test_path(name: str) -> bool:
    """Test-shaped by the conventions the suites here use: `test_x.py`, `x_test.go`,
    `x.test.ts`, `x.spec.ts`. A test file is the assertion, not a mutation target."""
    stem = Path(name).stem
    return (stem.startswith("test_") or stem.endswith("_test")
            or stem.endswith(".test") or stem.endswith(".spec"))


def changed_paths(root: str) -> list[str] | None:
    """Repo-relative paths this working tree has changed against HEAD - staged, unstaged or
    untracked. The ONE git changed-file idiom the script family shares: every lane that scopes
    itself to a diff reads it from here, because two idioms drift and then two lanes disagree
    about what "changed" means.

    Returns None when git cannot answer: no git, no commit to diff against, or a `root` that is
    not the repository top level (git would then report paths relative to some other root).

    None means UNKNOWN, never "nothing changed". Every caller must degrade to the FULL check,
    because a scope derived from an unanswered probe is an empty scope wearing a green tick -
    which is worse than the slow check the scope exists to avoid.
    """
    import subprocess
    rootp = Path(root)

    def _git(*args):
        return subprocess.run(["git", *args], cwd=str(rootp),
                              capture_output=True, text=True, timeout=10)
    names: list[str] = []
    try:
        top = _git("rev-parse", "--show-toplevel")
        if top.returncode != 0:
            return None
        if Path(top.stdout.strip() or ".").resolve() != rootp.resolve():
            return None
        for cmd in (("diff", "--name-only", "HEAD"),
                    ("ls-files", "--others", "--exclude-standard")):
            proc = _git(*cmd)
            if proc.returncode != 0:
                return None
            names.extend(proc.stdout.splitlines())
    except Exception:  # noqa: BLE001 - a changed-file probe must never break the gate
        return None
    out: list[str] = []
    for raw in names:
        name = raw.strip()
        if name and name not in out:
            out.append(name)
    return out


def _mutation_changed_surface(root: str) -> list[str] | None:
    """Repo-relative mutatable, non-test files with uncommitted changes. That is the surface a
    pre-commit gate is actually about, and it needs no sprint run and no sdlc-studio state, so
    the lane works in a consuming project too.

    A filter over `changed_paths`, and it inherits that probe's None contract: the caller
    degrades to the ledger's own contents rather than inventing a surface.
    """
    names = changed_paths(root)
    if names is None:
        return None
    rootp = Path(root)
    out: list[str] = []
    for name in names:
        if Path(name).suffix not in _MUTATABLE_SUFFIXES or _is_test_path(name):
            continue
        if (rootp / name).is_file() and name not in out:
            out.append(name)
    return out


def _name_list(names: list[str], limit: int = 3) -> str:
    """First `limit` names, then a count of the rest - a lane line must stay readable
    without hiding how many it did not print."""
    shown = ", ".join(Path(n).name for n in names[:limit])
    return shown + (f" (+{len(names) - limit} more)" if len(names) > limit else "")


def _key_under(root: str, p) -> str:
    """A path made absolute against `root` and resolved, so a repo-relative record and an
    absolute one for the same file compare equal."""
    path = Path(p)
    return str((path if path.is_absolute() else Path(root) / path).resolve())


#: The ledger's provenance vocabulary, as `mutation.py` writes it. A `measured` entry is a run
#: that applied the mutant and observed the suite; a `registered` one is a builder's report that
#: they applied one by hand, and nothing checked it. A test pins these against the recorder's own
#: constants, because a lane that stopped recognising the second label would print a self-report
#: as a measurement - the exact confusion the marking exists to prevent.
_PROVENANCE_MEASURED = "measured"
_PROVENANCE_REGISTERED = "registered"
#: The verdicts that are evidence ABOUT THE TESTS, and so count as mutation coverage of a file.
#: `mutation.COVERING_VERDICTS` is the definition; this is the lane's copy of it, pinned against
#: it by test like the provenance labels above. It used to be summed inline under a comment
#: pointing at a `_covering` that did not exist, so the constant documenting the rule was used
#: nowhere and a verdict added to it would never have reached this lane.
_COVERING_VERDICTS = ("killed", "survived")


def _entry_provenance(entry: dict) -> str:
    """Absent means measured: before registration existed only a run could write an entry, so an
    unmarked entry is a run's, and reading it as a claim would weaken real evidence."""
    return str(entry.get("provenance") or _PROVENANCE_MEASURED)


def _mutation_coverage(root: str) -> dict:
    """How much of the surface carries mutation evidence, judged per file on content hash.

    A whole-blob `git_rev` stamp cannot answer this: it goes stale the moment ANY file is
    committed, so per-unit evidence gathered during a build is unreadable by the close.
    A per-file entry keyed on that file's content hash stays valid across later
    commits to other files, which is exactly what makes the per-unit runs survive.

    ONE source, and it takes no report: the ledger `mutation-runs.json`, which enters a target
    only when the test command returned a killed or survived verdict on it. The report's
    `target_hashes` is NOT evidence and is deliberately unreachable from here - `mutation.py`
    writes it for every file NAMED as a target, before any verdict exists, so reading it as
    coverage made a refused run (no mutant applied at all) report its targets covered, and made
    a run stopped by the cost ceiling report files no mutant ever reached. Verdicts: hash
    matches -> covered; hash differs, or none was recorded -> STALE; no entry -> uncovered.
    Returns `known: False` when there is nothing to judge, so the caller falls back to the
    whole-report checks.

    A file covered ONLY by a registered entry is covered by a SELF-REPORT: a builder said they
    applied a mutant by hand, and no run confirmed it. It is named as such, because a lane that
    printed one figure over both kinds would let a claim read exactly like a measurement and so
    downgrade every measured entry in the ledger. A measured entry outranks a registered one on
    the same content - the stronger evidence is what the file has.

    A registered SURVIVOR is read too, and is a finding. `survived` means the test the builder
    wrote does not pin the behaviour they mutated, which is the worst news the practice can
    produce - and it reached the ledger and stopped there, because nothing here read anything
    from an entry but its target, hash and provenance. The file moved from `no evidence` to
    `covered` and the lane got QUIETER for saying so, which is the incentive running backwards.
    Counting it keeps a self-reported survivor at least as loud as registering nothing at all.
    Survivors from a MEASURED entry are not counted here: those are the report lane's, and
    counting them in both places would report one run's findings twice.
    """
    import hashlib
    rootp = Path(root)
    #: file key -> provenance -> {hash, survived} as that provenance recorded them
    entries: dict[str, dict[str, dict]] = {}

    def _key(p) -> str:
        return _key_under(root, p)

    ledger = rootp / "sdlc-studio" / ".local" / "mutation-runs.json"
    if ledger.exists():
        try:
            loaded = json.loads(ledger.read_text(encoding="utf-8"))
            for e in loaded.get("entries", []):
                if isinstance(e, dict) and e.get("target"):
                    summary = e.get("summary")
                    survived = (summary or {}).get("survived") if isinstance(summary, dict) else 0
                    def _n(field, s=summary):
                        v = (s or {}).get(field) if isinstance(s, dict) else 0
                        return int(v or 0) if isinstance(v, (int, float)) else 0
                    entries.setdefault(_key(e["target"]), {})[_entry_provenance(e)] = {
                        "hash": e.get("hash"),
                        "survived": int(survived or 0) if isinstance(survived, (int, float))
                        else 0,
                        # what the entry proves ABOUT THE TESTS, from the one list that defines
                        # it. `equivalent` is absent from that list on purpose: it asserts that
                        # no test could have killed the mutant, which says nothing about what
                        # the suite pins.
                        "covering": sum(_n(v) for v in _COVERING_VERDICTS),
                        "equivalent": _n("equivalent")}
        except (ValueError, OSError, TypeError, AttributeError):
            pass          # a corrupt ledger claims no coverage; it never breaks the lane
    surface = _mutation_changed_surface(root)
    if surface:
        judged = [(name, _key(name)) for name in surface]
        label = "changed surface"
    else:
        # No surface to judge, so the figure below is about the files the LEDGER holds, which
        # this change need not have touched. Which of the two non-surfaces it was decides how
        # the figure should be read, so the line names it rather than printing one word for
        # both: None is "git could not tell us", [] is "git told us: nothing".
        judged = [(k, k) for k in sorted(entries)]
        label = ("recorded surface (git could not name the changed files)" if surface is None
                 else "recorded surface (nothing changed since HEAD)")
    if not judged:
        return {"known": False, "count": 0, "detail": ""}
    covered: list[str] = []
    self_reported: list[str] = []
    survivors: list[str] = []
    stale: list[str] = []
    uncovered: list[str] = []
    equivalent_only: list[str] = []
    for display, key in judged:
        if key not in entries:
            uncovered.append(display)
            continue
        recorded = entries[key]
        try:
            current = hashlib.sha256(Path(key).read_bytes()).hexdigest()
        except OSError:
            current = None

        def _matches(provenance: str, seen=recorded, now=current) -> bool:
            # a recorded None is not evidence: paired with a target that cannot be read now
            # either, two unknowns would compare equal and read as "unchanged since the run"
            rec = seen.get(provenance) or {}
            return rec.get("hash") is not None and now == rec["hash"]
        if _matches(_PROVENANCE_MEASURED):
            covered.append(display)
        elif _matches(_PROVENANCE_REGISTERED):
            reg = recorded[_PROVENANCE_REGISTERED]
            # An `equivalent` entry says NO TEST COULD HAVE KILLED this mutant. That is evidence
            # about the mutant, never about the suite, so it cannot make a file covered. It did:
            # registering one equivalent with no `--test` at all took a file from "no evidence"
            # to "covered" and DROPPED the lane's finding count - the silent decrement
            # `register_mutant`'s own docstring promises to prevent.
            if not reg.get("covering"):
                uncovered.append(display)
                if reg.get("equivalent"):
                    equivalent_only.append(display)
                continue
            covered.append(display)
            self_reported.append(display)
            n = reg["survived"]
            if n:
                survivors.append(f"{display} ({n})")
        else:
            stale.append(display)
    detail = f"mutation evidence covers {len(covered)}/{len(judged)} file(s) of the {label}"
    if self_reported:
        n = len(self_reported)
        detail += (f"; {n} of those {'is' if n == 1 else 'are'} self-reported (mutants "
                   f"registered by hand, not a measured run): {_name_list(self_reported)}")
    if survivors:
        detail += (f"; SELF-REPORTED SURVIVOR(S) - a registered mutant the named test did NOT "
                   f"catch, so that behaviour is unpinned: {_name_list(survivors)}")
    if stale:
        detail += f"; STALE (edited since mutated): {_name_list(stale)}"
    if uncovered:
        detail += f"; no evidence: {_name_list(uncovered)}"
    if equivalent_only:
        detail += (f"; EQUIVALENT-ONLY (a registered equivalent says no test could have killed "
                   f"the mutant, which proves nothing about the tests): "
                   f"{_name_list(equivalent_only)}")
    return {"known": True, "count": len(stale) + len(uncovered) + len(survivors),
            "detail": detail}


def _mutation_coverage_safe(root: str) -> dict:
    try:
        return _mutation_coverage(root)
    except Exception:  # noqa: BLE001 - coverage is advisory; it must never raise into the gate
        return {"known": False, "count": 0, "detail": ""}


def _git_head(root: str) -> str | None:
    """HEAD's full sha, or None when git cannot answer. One definition, because the lane asks
    twice: to catch a report from another rev, and to attribute the numbers it prints."""
    try:
        import subprocess
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                              capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001 - staleness must not break the gate (Exception covers OSError)
        return None
    return head or None


def _report_hash_stale(root: str, data: dict) -> list[str]:
    """Targets the report recorded a hash for whose content has changed since. A NEGATIVE
    reading only: a match says nothing about whether a mutant ran on that file, only that the
    file has not changed since the report was written. It is what the degraded fallback has
    instead of per-file evidence, and it catches an edit the whole-blob rev cannot see because
    the edit is not committed."""
    import hashlib
    names: list[str] = []
    for fp, recorded in (data.get("target_hashes") or {}).items():
        key = _key_under(root, fp)
        try:
            current = hashlib.sha256(Path(key).read_bytes()).hexdigest()
        except OSError:
            current = None
        if recorded is None or current != recorded:
            names.append(fp)
    return names


def _mutation(root: str) -> dict:
    """Advisory v1 lane: the mutation-check report's survivors, plus how much of the surface
    carries evidence at all. An absent report reads NOT-RUN (advisory) - never PASS: silence
    is not assertion integrity. Advisory throughout: survivors and gaps are reported,
    never a refusal to close."""
    report_path = Path(root) / "sdlc-studio" / ".local" / "mutation-report.json"

    def _with_coverage(result: dict, cov: dict) -> dict:
        if cov["detail"]:
            result["detail"] += f"; {cov['detail']}"
            result["count"] += cov["count"]
        return result

    if not report_path.exists():
        return _with_coverage(
            {"count": 1, "blocking": False,
             "detail": "mutation gate not run (no mutation-report.json) - advisory; "
                       "run scripts/mutation.py over the changed surface"},
            _mutation_coverage_safe(root))
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        s = data.get("summary", {})
    except (ValueError, OSError) as exc:
        return {"count": 1, "blocking": False, "detail": f"mutation-report unreadable: {exc}"}
    cov = _mutation_coverage_safe(root)
    # An empty surface is a first-class outcome: the run found nothing to mutate. Read as
    # 'nothing to mutate' - distinct from not-run (no report at all, handled above) and from a
    # PASS (mutants applied and killed) - so a docs-only close is green with the reason on the
    # record, never a silent clean sweep over zero mutants.
    if data.get("empty_surface"):
        return _with_coverage(
            {"count": 0, "blocking": False,
             "detail": "nothing to mutate - the surface has no mutatable files (empty surface, "
                       "not a pass and not not-run) - advisory"},
            cov)
    if not cov["known"]:
        # Nothing per-file to judge: fall back to the whole-report checks, which read the
        # report as a freshness stamp and never as coverage. A report about some other state
        # of the tree must not render this diff's lane PASS.
        edited = _report_hash_stale(root, data)
        if edited:
            return {"count": len(edited), "blocking": False,
                    "detail": "mutation-report is STALE (target(s) edited since the run: "
                              f"{_name_list(edited)}) - re-run scripts/mutation.py (advisory)"}
        report_rev, head = data.get("git_rev"), _git_head(root)
        if report_rev and head and head != report_rev:
            return {"count": 1, "blocking": False,
                    "detail": f"mutation-report is STALE (run at {report_rev[:9]}, tree at "
                              f"{head[:9]}) - re-run scripts/mutation.py (advisory)"}
    # a refused run applied no mutant, so its summary is all zeros: rendered as
    # "0/0 mutations killed" a refusal reads as a clean sweep. Carry the report's
    # own failure state and remedy instead - silence is not assertion integrity.
    if data.get("refused"):
        baseline = data.get("baseline") or "not pass"
        detail = (f"mutation REFUSED - baseline {baseline} (no mutants applied, "
                  f"nothing was proven) - advisory")
        remedy = data.get("remedy")
        if remedy:
            detail += f"; {remedy}"
        return _with_coverage({"count": 1, "blocking": False, "detail": detail}, cov)
    n = int(s.get("survived", 0)) + int(s.get("errors", 0))
    detail = (f"{s.get('survived', 0)} survived, {s.get('errors', 0)} error(s) of "
              f"{s.get('applied', 0)} applied ({s.get('truncated', 0)} truncated) - advisory"
              if n else
              f"{s.get('killed', 0)}/{s.get('applied', 0)} mutations killed "
              f"({s.get('truncated', 0)} truncated) (advisory)")
    # a truncated green lane must state its coverage: 12/12 killed reads as
    # whole-surface assurance when it sampled under 1% of the enumerable sites
    applied, enumerated = int(s.get("applied", 0)), int(s.get("enumerated", 0))
    if int(s.get("truncated", 0)) and enumerated:
        pct = f"{100.0 * applied / enumerated:.1f}%"
        detail += f" - {applied}/{enumerated} enumerated sampled ({pct})"
    # Coverage is per FILE and comes from the ledger; these survivor numbers are per RUN and
    # come from the report, so a report written before the current HEAD publishes counts about
    # some other change. The whole-blob check used to say that out loud and only reached the
    # line when there was no per-file evidence at all. Attribution, not a finding: it adds no
    # count, so a covered surface still passes.
    report_rev, head = data.get("git_rev"), _git_head(root)
    if report_rev and head and head != report_rev:
        detail += f" - summary is from the run at {report_rev[:9]}, not this tree ({head[:9]})"
    return _with_coverage({"count": n, "blocking": False, "detail": detail}, cov)


# Lanes that read NOT-RUN (advisory) when their evidence file is absent. The
# upgrade capability digest names these when they arrive in a version gap, so
# a new integrity check cannot land silently as a benign-looking warn - a
# registry test asserts every advisory-when-absent lane is declared here.
ADVISORY_WHEN_ABSENT = {
    "mutation": {
        "since": "3.4.0",
        "baseline": ("run scripts/mutation.py over your changed surface to "
                     "create sdlc-studio/.local/mutation-report.json"),
    },
}

def hook_enablement_gap(root) -> str | None:
    """The one-line warning when a tree SHIPS a tracked pre-commit gate that this clone has
    not enabled - or None when there is nothing to say. Fires only where it means something:
    a git work tree containing `.githooks/pre-commit` (never a consuming project, which has
    no .githooks; never a non-git directory). Shared by the gate lane and the status
    dashboard so the two surfaces cannot drift."""
    import os
    import subprocess
    hook = Path(root) / ".githooks" / "pre-commit"
    if not hook.is_file():
        return None
    # Scrub repo-redirecting env: gate/status may run from inside ANOTHER repo's hook, and an
    # inherited GIT_DIR/GIT_WORK_TREE would silently make git answer for that repo, not root.
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    try:
        inside = subprocess.run(["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
                                capture_output=True, text=True, timeout=10, env=env)
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            return None
        cfg = subprocess.run(["git", "-C", str(root), "config", "core.hooksPath"],
                             capture_output=True, text=True, timeout=10, env=env)
    except (OSError, subprocess.SubprocessError):
        return None  # git unavailable: nothing checkable, never a false alarm
    val = cfg.stdout.strip() if cfg.returncode == 0 else ""
    if val:
        # Equivalent enabled spellings must read enabled: ".githooks", ".githooks/", or an
        # absolute path to the same directory - git runs the hook under all of them.
        if val.rstrip("/") == ".githooks":
            return None
        try:
            if (Path(val).is_absolute()
                    and Path(val).resolve() == (Path(root) / ".githooks").resolve()):
                return None
        except OSError:
            pass
    return ("tracked .githooks/pre-commit is NOT enabled in this clone (core.hooksPath "
            "unset or elsewhere) - the commit gate is not running; fix: bash tools/enable-hooks.sh")


def _window_staged(root: str):
    """Repo-relative staged paths, or None when git could not be asked.

    None is "I cannot tell", never "nothing is staged": the lane below refuses on it, because
    reading an unanswerable index as an empty one would wave through exactly the commit this
    guard exists to stop."""
    import subprocess
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "-c", "core.quotepath=false",
             "diff", "--cached", "--name-only"],
            capture_output=True, text=True)
    except OSError:
        return None
    if out.returncode != 0:
        return None
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]


def _window(root: str) -> dict:
    """Blocking standard-gate lane: a process has DECLARED that it is rewriting source files in
    place, so this tree is being written to by somebody else right now.

    CR0388, as corrected: a reviewer's shell redirect through a symlink farm overwrote live
    source while the author was committing ceremony artefacts, and `git add -A` staged it. The
    commit was refused only because the reverted file happened to break the suite - a rewrite
    that left the suite GREEN would have been committed silently under a paperwork message. So
    this lane does not look for mutants and does not lean on the suite: it reads the declaration.

    It judges the STAGED PATHS, not the record's existence. A lane that failed on existence
    alone froze the whole tree for a review's duration while the pre-commit hook - reading the
    same records - printed "no staged path is claimed by it, so this commit proceeds": one run
    saying both, and the blocking one winning. The window scopes staging; it does not stop work.

    REFUSE rather than warn (D0053) for a path a window claims. A warning is what the observed
    failure mode defeats: in a passing run it reads as noise, and the run that matters is
    exactly the passing one. An open window claiming nothing staged is still REPORTED, so an
    author running the gate learns of the concurrent writer before staging into it.

    Discovery and parsing are `mutation`'s, so the rule that an unreadable record counts as OPEN
    has ONE home rather than a copy here that could drift the safe way into 'closed'."""
    import mutation
    held = mutation.read_windows(root)
    if not held:
        return {"count": 0, "blocking": True, "detail": "no rewrite window is open"}
    staged = _window_staged(root)
    lines, claiming = [], 0
    for win in held:
        # The record's claims as `mutation.window_claims` normalised them - ONE reading, shared
        # with the hook's inline reader and pinned against it by test, rather than a second
        # derivation here. The two readings diverged once: a record naming no owner had its
        # `paths` discarded upstream and was re-read here as claiming the whole tree, while the
        # hook read the same record as claiming one file and let the commit proceed. What is
        # DISPLAYED is what was MATCHED on, so a refusal can be checked on its face.
        claims = win["paths"]
        if staged is None:
            hit = ["(the staged file list could not be read, so every path is treated "
                   "as claimed)"]
        else:
            hit = [s for s in staged if any(_window_claims(c, s) for c in claims)]
        note = (f"{win['owner']} has claimed {', '.join(claims)} since {win.get('opened_at')}")
        if win.get("unreadable"):
            note += f" ({win['detail']})"
        if not hit:
            lines.append(f"a rewrite window is OPEN - {note}; no staged path is claimed by it, "
                         f"so this gate does not refuse. Stage named paths, never `git add -A`")
            continue
        # Counted per WINDOW, not as a boolean: the lane reads N records, and two writers
        # claiming what this commit stages is worse news than one. A fixed 1 could not report
        # the multi-writer case the reader was generalised to see.
        claiming += 1
        lines.append(f"a rewrite window is OPEN and claims a STAGED path - {note}; staged: "
                     f"{', '.join(hit)}. A commit now stages whatever that process has left on "
                     f"disk. Wait for it, or clear it: {win['clear_with']}")
    return {"count": claiming, "blocking": True, "detail": "; ".join(lines)}


def _window_claims(pattern, staged: str) -> bool:
    """True when `pattern` covers the staged path. Kept identical in rule to the pre-commit
    hook's own matcher, and pinned against it by test: a claim this cannot INTERPRET (anything
    that is not a string, an absolute path, or one that traverses out of this root) claims
    EVERYTHING, because the record says a writer is active and a matcher that shrugged would
    report it as harmless."""
    import fnmatch
    if not isinstance(pattern, str):
        return True
    pat = pattern.strip()
    if pat.startswith("./"):
        pat = pat[2:]
    pat = pat.rstrip("/")
    if pat in ("", "."):
        return True
    if pat.startswith("/"):
        return True          # absolute: not comparable with a repo-relative staged path
    if pat == ".." or pat.startswith("../") or "/../" in pat or pat.endswith("/.."):
        # traversal: `tools/../tools/x.py` names a real file and matches nothing as a literal
        # pattern. Claims are normalised at open time; a record already on disk carrying this
        # spelling is read as claiming the tree rather than as claiming nothing.
        return True
    if staged.startswith(pat + "/"):
        return True
    return fnmatch.fnmatch(staged, pat)


def _hook_enabled(root: str) -> dict:
    gap = hook_enablement_gap(root)
    return {"count": 0 if gap is None else 1, "blocking": False,
            "detail": gap or "hook enabled (or no tracked hook in this tree)"}


def _close_owed(root: str) -> dict:
    """The push/release close-owed guard (bound only, under --require-close): delivery units that
    reached terminal since the baseline with no retro accounting for them - a skipped close-down.
    Like every close/release lane it is a BOUND lane, added by its mode and never part of the plain
    gate: a standard gate makes no claim about close-ownership, so it cannot wear one. The SOFT nudge
    (discoverability) lives on status/hint; this is the blocking half that lands where shipping
    happens. An unbaselined project reports zero - stamping the baseline is the operator's one-time
    acknowledgement of the pre-adoption tail, not a gate's job.

    This is the machine half of RFC0042: a mandated ceremony with no mechanical detector is a silent
    control that fires only when someone remembers. Now the release gate can see a skipped close."""
    import close_owed  # crash contained by BLOCKING_ON_ERROR: an unproven bound guard must fail loud
    report = close_owed.owed(Path(root))
    if report.get("corrupt"):
        return {"count": 1, "blocking": True,
                "detail": (f"close-owed baseline is CORRUPT ({report.get('error', 'unreadable')}) - "
                           f"refusing to pass a close gate over an unreadable baseline that silently "
                           f"disarms the close-down; repair .close-owed-baseline.json (restore from "
                           f"git), do NOT re-stamp it")}
    owed = report["owed"]
    if not owed:
        state = "no baseline stamped yet" if not report["baselined"] else "none owed"
        return {"count": 0, "blocking": True,
                "detail": f"no sprint close owed ({state}; {report['covered']} accounted for)"}
    ids = ", ".join(cid for cid, _ in owed[:8]) + (f", +{len(owed) - 8} more" if len(owed) > 8 else "")
    return {"count": len(owed), "blocking": True,
            "detail": (f"a sprint close is owed - {len(owed)} delivery unit(s) reached terminal "
                       f"with no retro ({ids}); run the retro then "
                       f"`gate --require-retro RETROxxxx` before you push/release")}


# Lanes whose FAILURES block must also block when they CRASH: a raised exception in
# (say) validate or reconcile means the gate proved nothing about that lane, and a
# green gate over an unproven blocking lane is the false-assurance class (LL0008).
# Custom/injected checks not declared here stay contained (advisory-on-error), so one
# buggy experimental check cannot brick the gate.
BLOCKING_ON_ERROR = {
    "conformance", "reconcile", "index-derived", "validate",
    "integrity", "duplicate-id", "doc-coverage", "retro", "verify",
    "lessons-summary", "lessons-validity", "handoff", "review-legs",
    "engagement-floor", "review-current", "close-owed", "window",
    "changelog-fragments",
}

def _changelog(root: str) -> dict:
    """The `changelog-fragments` lane in the STANDARD gate: CHANGELOG.md's own headings are
    structurally sound, and `[Unreleased]` was not hand-edited while `changelog.d/` is live.

    Both faults are COMMITTED, not tagged: a bad hand-insert reparents entries the moment it
    lands, and waiting for a release cut would not catch it. So the lane binds here as well as
    at the cut, where it gains the stray-fragment reading (`_changelog_fragments`). The stray
    reading stays release-only - a fragment between releases is the normal state and the
    standard gate must not nag about it."""
    faults = _changelog_faults(root)
    detail = ("; ".join(faults) if faults
              else "CHANGELOG.md headings are sound and [Unreleased] is not hand-edited")
    return {"count": len(faults), "blocking": True, "detail": detail}


def _changelog_fragments(root: str) -> dict:
    """The release form of the `changelog-fragments` lane: the standard changelog faults PLUS
    no stray (uncomposed) fragment left at the cut - an entry silently missing from a release
    is the LL0004 hole fragments exist to close."""
    import changelog
    faults = _changelog_faults(root)
    strays = changelog.check(root)
    if strays:
        faults = faults + [f"{len(strays)} uncomposed fragment(s): "
                           + ", ".join(p.name for p in strays)
                           + " - run changelog.py compose before tagging"]
    detail = "; ".join(faults) if faults else "no stray fragments; CHANGELOG.md headings sound"
    return {"count": len(faults), "blocking": True, "detail": detail}


def _changelog_faults(root: str) -> list[str]:
    """The commit-time changelog faults shared by both gate modes: structural faults in
    CHANGELOG.md's own `[Unreleased]` headings, plus a hand-edit of `[Unreleased]` staged
    with no fragment consumed in the same commit."""
    import changelog
    return list(changelog.structure_errors(root)) + _changelog_hand_edit_faults(root)


def _changelog_hand_edit_faults(root: str) -> list[str]:
    """A staged edit that ADDS content to CHANGELOG.md's `[Unreleased]` section, in a repo
    using `changelog.d/` fragments, with no fragment consumed in the same commit - the hand-
    edit path the deterministic writer (`changelog.py compose`) exists to replace.

    Reads the STAGED state (index vs HEAD), as the rewrite-window lane reads staged paths: it
    judges what this commit is about to do, not the working tree. Only ADDITIONS to
    `[Unreleased]` count, so a release cut (which moves entries OUT of it) and any edit to an
    already-released section, the file header, or the section rename a cut performs stay
    hand-editable and are never refused. The escape hatch: the same edit is allowed when the
    commit also consumes a fragment (a staged deletion under `changelog.d/`, which is what
    compose does), so the sanctioned path is never blocked by its own writes."""
    root_p = Path(root)
    if not (root_p / "changelog.d").is_dir():
        return []  # the project has not adopted fragments: there is nothing to police
    head = _git_show(root, "HEAD:CHANGELOG.md")
    index = _git_show(root, ":CHANGELOG.md")
    if head is None or index is None:
        return []  # no git, no HEAD, or the path is absent from one side: invent no fault
    if not _unreleased_gained_content(head.splitlines(), index.splitlines()):
        return []
    if _staged_consumes_fragment(root):
        return []  # compose ran in this commit: the edit is the machine's, not a hand-edit
    return ["CHANGELOG.md [Unreleased] was hand-edited (content added) while changelog.d/ is "
            "live and no fragment is consumed in this commit - write the entry as a "
            "changelog.d/ fragment and run `changelog.py compose`, do not edit [Unreleased] "
            "by hand"]


def _git_show(root: str, spec: str) -> str | None:
    """`git show <spec>` under `root`, or None when git cannot answer (no repo, no such
    object). None is 'cannot tell', never 'empty': the caller invents no fault on it."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", str(root), "show", spec],
                             capture_output=True, text=True)
    except OSError:
        return None
    return out.stdout if out.returncode == 0 else None


def _unreleased_content_lines(lines: list[str]) -> list[str]:
    """The non-blank, non-release-heading content lines under `## [Unreleased]` (subsection
    headings and entries alike), by absolute file order. A `## ` release heading is a section
    boundary, not content."""
    import re
    out, section = [], None
    for ln in lines:
        m = re.match(r"^## (.+?)[ \t]*$", ln)
        if m:
            section = m.group(1).strip()
        if section != "[Unreleased]":
            continue
        s = ln.strip()
        if not s or re.match(r"^## ", ln):
            continue
        out.append(s)
    return out


def _unreleased_gained_content(old_lines: list[str], new_lines: list[str]) -> bool:
    """True when the staged `[Unreleased]` carries a content line the committed one did not -
    an addition or an in-place edit. Set-difference by MULTISET, so a second `### Added` or a
    duplicated bullet still reads as gained. Removal-only (a release cut moving entries down,
    a deletion) leaves nothing gained, so those are not flagged."""
    from collections import Counter
    gained = Counter(_unreleased_content_lines(new_lines)) - Counter(_unreleased_content_lines(old_lines))
    return bool(gained)


def _staged_consumes_fragment(root: str) -> bool:
    """True when this commit stages a DELETION under `changelog.d/` - the file-consuming half
    of what `changelog.py compose` does, and the signal that an accompanying `[Unreleased]`
    edit is the composer's write rather than a hand-edit."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", str(root), "diff", "--cached", "--name-status"],
                             capture_output=True, text=True)
    except OSError:
        return False
    if out.returncode != 0:
        return False
    for ln in out.stdout.splitlines():
        parts = ln.split("\t")
        if len(parts) >= 2 and parts[0].startswith("D") and parts[-1].startswith("changelog.d/"):
            return True
    return False


def _versions_strict(root: str) -> dict:
    """Release-bound lane: the skill's version strings agree, CHANGELOG included.

    Version consistency and the release gate used to be two commands, so a tag could be
    cut from a green gate while the version check had never run - or had run and had its
    exit code dropped on the floor. The pre-tag gate is one obligation with one exit code.

    `--strict` is the flag that adds the CHANGELOG comparison, so it is the whole point of
    running it here rather than the plain form.

    Invoked as a SUBPROCESS, not imported: `check_versions.py` is a repo-only development
    tool under `tools/`, while this gate ships to consuming projects. A project without it
    is reported as not-applicable and never silently passed - a lane that cannot run must
    say so, because an invented pass is the false-assurance class this gate refuses.
    """
    import subprocess  # noqa: PLC0415 - local: keep subprocess off the cold import path
    checker = Path(root) / "tools" / "check_versions.py"
    if not checker.is_file():
        # `run_gate` derives status from `count`, so a not-applicable lane reports 0 and
        # says N/A in its detail - the same idiom the doc-coverage lane uses off-repo.
        # Never a silent pass: the detail states plainly that nothing was checked.
        return {"count": 0, "blocking": False,
                "detail": ("N/A - tools/check_versions.py is not present; the strict version "
                           "check is a skill-development tool and does not apply here")}
    try:
        proc = subprocess.run([sys.executable, str(checker), "--strict", "--root", str(root)],
                              capture_output=True, text=True, timeout=120, cwd=str(root))
    except (OSError, subprocess.SubprocessError) as exc:
        return {"count": 1, "blocking": True,
                "detail": f"could not run check_versions.py: {exc}"}
    out = (proc.stdout + proc.stderr).strip()
    if proc.returncode == 0:
        return {"count": 0, "blocking": True, "detail": "version strings agree (CHANGELOG included)"}
    first = out.splitlines()[0] if out else "see check_versions.py output"
    return {"count": 1, "blocking": True,
            "detail": f"version drift before a tag: {first}"}


def _batch_size(root: str) -> dict:
    """Advisory small-batch lane: flags a delivered unit whose CHANGE is an outlier for
    its size - the AI batch-size failure mode (agents produce larger diffs faster; DORA
    2024/25 ties undisciplined batch growth to degraded throughput and stability). The
    sizing rule bounds the ESTIMATE (points <= 8); this lane bounds the DIFF.

    Deliberately never blocking: a legitimate mechanical sweep (a rename, a migration) is
    large and fine - the lane's job is visibility at review time, not a gate. Off until the
    project sets thresholds (`batch_size.max_lines` / `batch_size.max_files`); measures the
    OPEN RUN's batch units via their Refs-trailed / subject-named commits."""
    from lib import run_state as _rs
    max_lines = sdlc_md.project_override(root, "batch_size.max_lines", None)
    max_files = sdlc_md.project_override(root, "batch_size.max_files", None)
    if not max_lines and not max_files:
        return {"count": 0, "blocking": False,
                "detail": "off - set batch_size.max_lines / batch_size.max_files to enable "
                          "(advisory diff-size visibility per delivered unit)"}
    try:
        state = _rs.read(root) or {}
    except _rs.RunStateError:
        return {"count": 0, "blocking": False,
                "detail": "run state unreadable - nothing measured (the close gate owns that failure)"}
    batch = state.get("batch") or []
    if not batch:
        return {"count": 0, "blocking": False, "detail": "no open run - nothing to measure"}
    import subprocess
    offenders: list[str] = []
    measured = 0
    for uid in batch:
        uid = sdlc_md.norm_id(uid)
        try:
            # end-anchored trailer + literal parenthesised subject form (BRE: parens are
            # literal), so US0001 never prefix-matches a Refs: US00013 trailer
            shas = subprocess.run(
                ["git", "log", "--format=%H", "--grep", f"Refs: {uid}$",
                 "--grep", f"({uid})"],
                cwd=root, capture_output=True, text=True, timeout=30).stdout.split()
        except (OSError, subprocess.TimeoutExpired):
            return {"count": 0, "blocking": False, "detail": "no readable git history"}
        if not shas:
            continue
        lines = 0
        files: set[str] = set()
        for sha in shas:
            out = subprocess.run(["git", "show", "--numstat", "--format=", sha],
                                 cwd=root, capture_output=True, text=True, timeout=30).stdout
            for row in out.splitlines():
                parts = row.split("\t")
                if len(parts) == 3:
                    add, rem, name = parts
                    if add.isdigit():
                        lines += int(add)
                    if rem.isdigit():
                        lines += int(rem)
                    files.add(name)
        measured += 1
        over = ((max_lines and lines > int(max_lines))
                or (max_files and len(files) > int(max_files)))
        if over:
            found = sdlc_md.find_by_id(root, uid)
            pts = sdlc_md.read_points(sdlc_md.read_text_safe(found[0])) if found else None
            offenders.append(f"{uid} ({pts or '?'}pt): {lines} lines / {len(files)} file(s) "
                             f"vs max {max_lines or '-'} lines / {max_files or '-'} file(s)")
    skipped = len(batch) - measured
    tail = f" ({measured} measured, {skipped} with no identifiable commits)" if skipped else ""
    if offenders:
        return {"count": len(offenders), "blocking": False,
                "detail": "advisory - never blocks; outlier diff for its size: "
                          + "; ".join(offenders) + tail}
    return {"count": 0, "blocking": False,
            "detail": f"{measured} measured unit(s) within batch thresholds{tail}"}


def _conformance_scoped(root: str) -> dict:
    """The pre-commit binding of the conformance lane: judge the units this commit touches."""
    return _conformance(root, changed=True)


def _validate_scoped(root: str) -> dict:
    """The pre-commit binding of the validate lane: judge the artefacts this commit touches."""
    return _validate(root, changed=True)


#: The two lanes the STANDARD gate scopes to the diff and `--release` restores to the whole
#: workspace. One function per lane, called with `changed` set differently - not a second set of
#: rules, so the scoped and the whole-workspace verdict can never come to disagree about what
#: conformance or validity means. A commit is judged on what it changed; a tag is judged on
#: everything, and the release lane says so by running exactly the same check unscoped.
WHOLE_WORKSPACE_LANES = {"conformance": _conformance, "validate": _validate}

DEFAULT_CHECKS = {
    "conformance": _conformance_scoped,
    "reconcile": _reconcile,
    "index-derived": _index_derived,
    "validate": _validate_scoped,
    "constitution": _constitution,
    "integrity": _integrity,
    "duplicate-id": _duplicate_id,
    "provenance": _provenance,
    "doc-coverage": _doc_coverage,
    "engagement-floor": _engagement_floor,
    "disclosure": _disclosure,
    "doc-freshness": _doc_freshness,
    "mutation": _mutation,
    "window": _window,
    "hook-enabled": _hook_enabled,
    "batch-size": _batch_size,
    # Structure + hand-edit are COMMITTED faults, so the changelog lane runs in the standard
    # gate too; --release swaps in the superset that also refuses a stray fragment at the cut.
    "changelog-fragments": _changelog,
}


def _lessons_loop_blocking(root: str) -> bool:
    """Whether the bound close lessons/retro lanes BLOCK, or merely report. The documented
    opt-out `lessons.loop: judgement` makes the whole retro/lessons close set advisory (ADR-010);
    any other value (default `enforce`) blocks. One derivation for all three lanes - retro,
    lessons-summary and lessons-validity - so the key covers exactly what the docs say it covers,
    never a subset an operator has to discover by trial."""
    import config
    mode = str(config.get(root, "lessons.loop", "enforce") or "enforce").strip().lower()
    return mode != "judgement"


def _retro_present(root: str, retro_id: str) -> dict:
    """Blocking close-gate check: the batch's retro must exist AND say something before a
    sprint/review close reports success. Fail-loud per LL0008 - 'unconditional' retro is
    doctrine until it is a gate. The sprint-close orchestration passes the next retro id
    via --require-retro.

    This leg used to glob for a filename, so a 0-byte file named RETRO9999.md passed it:
    the one gate that made the retrospective un-skippable was the one an agent could
    satisfy with `touch`. Existence is not evidence - so the check is now
    delegated to `retro.py validate`, which interrogates the CONTENT: the required
    sections, at least one real lesson, and a disposition for every finding.
    """
    import retro
    # The documented opt-out (`lessons.loop: judgement`), mirroring the engagement floor: the
    # lane still REPORTS, it just does not block. An opt-out that is documented but unread
    # would be the very disease this loop exists to cure.
    blocking = _lessons_loop_blocking(root)
    res = retro.validate(root, retro_id)
    if res["ok"]:
        n_l, n_f = len(res["lessons"]), len(res["findings"])
        return {"count": 0, "blocking": blocking,
                "detail": (f"batch retro {retro_id}: {n_l} lesson(s), {n_f} finding(s) all "
                           f"dispositioned ({len(res['filed'])} filed, "
                           f"{len(res.get('fixed', []))} fixed in-sprint, "
                           f"{len(res['declined'])} declined)")}
    # Every error names its own remedy; surface them all rather than only the first, so one
    # close tells you everything it wants instead of a queue of one-at-a-time refusals.
    suffix = "" if blocking else " (advisory: lessons.loop is judgement)"
    return {"count": len(res["errors"]), "blocking": blocking,
            "detail": f"batch retro {retro_id} incomplete{suffix} - " + "; ".join(res["errors"])}


def _only_close_status_block_differs(root: Path, path: Path) -> bool:
    """True when the ONLY uncommitted change to `path` is inside the close's machine-maintained
    status block.

    The close stamps that block as its last act, so it is uncommitted BY CONSTRUCTION for the
    rest of that close and for the operator's follow-up `--apply-signoff` invocation. Treating it
    as "uncommitted review paperwork" made the close block its own second invocation with a
    remedy - commit the paperwork - that the close itself had just created the need for. The
    substantive anchor (everything a human wrote) is still held to the committed rule; only the
    block the tool owns is exempt.
    """
    try:
        import subprocess
        rel = path.relative_to(root)
        head = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=root,
                              capture_output=True, text=True, timeout=10)
        if head.returncode != 0:
            return False                      # not in history at all - genuinely uncommitted
        def _strip(text: str) -> str:
            begin, end = "<!-- close-status:begin -->", "<!-- close-status:end -->"
            if begin in text and end in text:
                return text[:text.index(begin)] + text[text.index(end) + len(end):]
            return text
        return _strip(head.stdout) == _strip(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - currency reporting must never break the gate
        return False


def _is_dirty(root: Path, path: Path) -> bool:
    """True when `path` has uncommitted working-tree or staged changes.

    Answers only what it is asked: a git failure, an untracked file, or no repo at all
    returns False, so the caller falls back to the committed-time reading rather than
    inventing a dirty state.
    """
    try:
        import subprocess
        rel = path.relative_to(root)
        out = subprocess.run(["git", "status", "--porcelain", "--", str(rel)],
                             cwd=root, capture_output=True, text=True, timeout=10)
        return bool(out.stdout.strip())
    except Exception:  # noqa: BLE001 - currency reporting must never break the gate
        return False


#: Metadata fields the CLOSE itself writes onto a unit: the status transition, the AC
#: back-annotation and the verification tier it gates on. A change confined to these is the
#: close's own bookkeeping, not content a review would have judged differently.
_CLOSE_OWNED_FIELDS = ("Status:", "Verified:", "Verification depth:", "Signed-off", "Critiqued")

#: The field whose carve-out is DIRECTIONAL. Every other close-owned field above is a stamp
#: the close adds; `Status` is the one whose meaning depends entirely on which way it moved.
_STATUS_FIELD = "Status:"

def _status_value(body: str) -> str | None:
    """The value of a `Status:` metadata line, or None when the line carries none.
    Tolerates both the bold (`**Status:** Done`) and bare (`Status: Done`) spellings."""
    import re as _re  # noqa: PLC0415 - as elsewhere in this module
    m = _re.search(r"\*{0,2}Status:\*{0,2}\s*(.+?)\s*$", body)
    return m.group(1).strip().strip("*").strip() if m else None


def _artifact_type_of(root: Path, path: Path) -> str | None:
    """The artefact type `path` belongs to, from the declared type->directory map. Derived
    from `ARTIFACT_TYPES`, never a list written here, so a new type is covered on the day
    it is declared."""
    try:
        rel = path.resolve().relative_to(Path(root).resolve()).as_posix()
    except (ValueError, OSError):
        rel = path.as_posix()
    for type_, (dirname, _prefix) in sdlc_md.ARTIFACT_TYPES.items():
        if rel.startswith(dirname.rstrip("/") + "/"):
            return type_
    return None


def _close_recorded_transition(type_: str | None, frm: str | None, to: str | None,
                               root: Path | str | None = None) -> bool:
    """True when a Status move is one the CLOSE tooling itself records.

    The carve-out used to ask only whether a changed line contained the substring
    `Status:`, so it was blind to both direction and value: a hand-flip from Draft or
    Blocked straight to Done, and a reopen of a terminal status, were both waved through as
    "the close recording a verdict already reached" - over a verdict no reviewer reached.

    Three conditions, each read from a DECLARED vocabulary rather than a list kept here:

    * the new value is an absorbing state for the type (`terminal_statuses`) - only a close
      moves a unit into one;
    * the old value is not (terminal to terminal is a re-labelling, and terminal to
      anything else is a reopen: both are changes a reviewer would judge);
    * the old value is one of the implementation states the delivery loop actually parks a
      unit at before the close (`transition._IMPL_TARGETS`, the same set the tier gate
      reads). A unit that was Draft, Ready or Blocked did not pass through delivery, so
      nothing about its arrival at Done is bookkeeping.

    Unknown type, unreadable value, or an unrecognised status: NOT a close transition. The
    carve-out is an exemption, and an exemption granted on an unanswered question is the
    failure mode this whole lane exists to prevent.
    """
    if not type_ or not frm or not to:
        return False
    vocab = sdlc_md.status_vocab(type_, root)   # honours a project's declared vocabulary
    frm = sdlc_md.canonical_status(frm, vocab) or frm
    to = sdlc_md.canonical_status(to, vocab) or to
    terminal = sdlc_md.terminal_statuses(type_)
    if to not in terminal or frm in terminal:
        return False
    try:
        import transition  # noqa: PLC0415 - sibling; the one declaration of the delivery states
        in_flight = set(transition._IMPL_TARGETS)
    except Exception:  # noqa: BLE001 - a gate must not break on an import
        return False
    return frm in (in_flight & set(vocab)) - terminal


def _anchor_last_commit(root: Path, path: Path) -> str:
    """The sha of the last commit touching `path`, or "" when unknown.

    "" is the honest-degrade value and its callers treat it as "cannot tell", falling back to
    reporting every newer artefact as stale. A carve-out that opened up when git was unreadable
    would be a carve-out that opens up exactly when nothing can be checked.
    """
    import subprocess  # noqa: PLC0415 - as elsewhere in this module
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%H", "--", str(path)],
                             cwd=str(root), capture_output=True, text=True,
                             timeout=10)  # nosec B603 B607
    except (OSError, subprocess.SubprocessError, ValueError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def _close_owned_change_only(root: Path, path: Path, since: str) -> bool:
    """True when everything that changed in `path` since commit `since` is close bookkeeping.

    The review-currency lane refuses when any artefact is newer than the anchor. But the close
    chain TRANSITIONS the batch in its own steps 5-7 and refreshes the anchor in step 7, while
    the gate is step 4 - so re-running the documented close flow fails on changes its own
    previous run made, and the printed remedy is to re-run an adversarial review over a tree
    whose only change is a set of status stamps. The honest remedy would be to touch the anchor,
    which is precisely what the lane exists to stop being done casually.

    So the question asked is not "did anything change" but "did anything a REVIEWER would judge
    change". A status moving Review to Done is the close recording a verdict already reached; a
    changed acceptance criterion is not. Anything this cannot read falls back to STALE, because
    an unreadable diff is not evidence of innocence.

    The Status line is read for its DIRECTION and its VALUES, not for the substring. Asking
    only whether the line contained `Status:` exempted a hand-flip from Draft or Blocked
    straight to Done, and a reopen of a terminal status, as readily as it exempted the
    close's own Review-to-Done stamp - so the gate printed PASS over a status change no
    reviewer ever judged. `_close_recorded_transition` decides which moves the close
    records; every other close-owned field is still a plain stamp and still exempt.
    """
    import subprocess  # noqa: PLC0415 - as elsewhere in this module
    try:
        proc = subprocess.run(["git", "diff", "--unified=0", since, "--", str(path)],
                              cwd=str(root), capture_output=True, text=True,
                              timeout=30)  # nosec B603 B607
    except (OSError, subprocess.SubprocessError, ValueError):
        return False
    if proc.returncode != 0:
        return False
    removed_status: list[str] = []
    added_status: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        body = line[1:].strip().lstrip("> ").strip()
        if not body:
            continue
        if not any(f in body for f in _CLOSE_OWNED_FIELDS):
            return False
        if _STATUS_FIELD in body:
            value = _status_value(body)
            if value is None:
                return False   # a Status line whose value cannot be read is not evidence
            (added_status if line.startswith("+") else removed_status).append(value)
    if added_status or removed_status:
        # A Status line ADDED where none existed, or REMOVED and not replaced, is not a
        # transition the close records either - it is somebody rewriting the field.
        if len(added_status) != 1 or len(removed_status) != 1:
            return False
        if not _close_recorded_transition(_artifact_type_of(root, path),
                                          removed_status[0], added_status[0], root):
            return False
    return True


def _review_current(root: str) -> dict:
    """Blocking close-gate check: the unified-review anchor (reviews/LATEST.md) must be at least
    as new as every artefact. If any artefact changed since the last review, LATEST.md is stale
    and a fresh session orients on an out-of-date claim.

    The sprint close is reconcile + review + retro. Reconcile blocks on drift and retro is a
    hard gate; this is the review leg, which was only advisory before (doc_freshness) - so a
    stale review reached a close, and did. Presence is not currency: the review-legs lane checks
    the doc legs EXIST; this checks the review was actually re-RUN. The estimate machinery is
    reused from review_prep (git commit time, mtime fallback).
    """
    import review_prep
    rr = Path(root)
    latest = rr / "sdlc-studio" / "reviews" / "LATEST.md"
    if not latest.is_file():
        return {"count": 1, "blocking": True,
                "detail": "no reviews/LATEST.md - run `review` before closing the sprint"}
    latest_dt = review_prep._parse_dt(review_prep._modified_iso(latest, rr)[0])
    # The timestamp above is the last COMMIT time, so a review that has just been re-run but
    # not yet committed still reads at its previous commit - stale, with a remedy telling the
    # operator to do the thing they just did. Re-read the dirty anchor at its working-tree
    # mtime so the two genuinely different states get two different remedies.
    uncommitted = _is_dirty(rr, latest)
    if uncommitted:
        latest_dt = review_prep._parse_dt(
            datetime.fromtimestamp(latest.stat().st_mtime, timezone.utc).isoformat())
    stale = []
    for key, rec in review_prep.staleness(rr).items():
        m = review_prep._parse_dt(rec.get("last_modified"))
        stale_by_anchor = bool(m and latest_dt and m > latest_dt)
        # Currency is a property of the review RECORD, not only the anchor file's commit time. A
        # re-run review that re-stamped LATEST.md byte-identically kept its old commit time (git saw
        # no change) and read stale, though review-state.json records the review as freshly run - the
        # remedy printed ("run `review`") was the thing just done, and only a substantive edit to an
        # already-correct anchor cleared it. An artefact is stale only when the anchor commit-time AND
        # the review record BOTH say so: the record can make an already-reviewed artefact current, but
        # never a genuinely-changed one (a change past the last review sets needs_review). An absent or
        # unparseable record leaves needs_review True, so this falls back to the commit-time behaviour
        # unchanged.
        stale_by_record = bool(rec.get("needs_review", True))
        if stale_by_anchor and stale_by_record:
            stale.append(key)
    if stale:
        anchor_rev = _anchor_last_commit(rr, latest)
        recs = review_prep.staleness(rr)
        judged = ([k for k in stale
                   if not _close_owned_change_only(
                       rr, rr / (recs.get(k, {}).get("path") or k), anchor_rev)]
                  if anchor_rev else stale)
        bookkeeping = len(stale) - len(judged)
        if judged:
            note = (f" ({bookkeeping} further artefact(s) changed only in close bookkeeping and "
                    f"are not counted)" if bookkeeping else "")
            return {"count": len(judged), "blocking": True,
                    "detail": (f"reviews/LATEST.md is stale - {len(judged)} artefact(s) changed "
                               f"since the last review ({_elide(sorted(judged))}); run `review` "
                               f"before closing{note}")}
        if bookkeeping:
            # The close's OWN transitions, and nothing a reviewer would judge. Reporting these
            # as a stale review sends the operator to re-run an adversarial pass over a set of
            # status stamps, and the only way out is to backdate the thing being measured.
            return {"count": 0, "blocking": False,
                    "detail": (f"reviews/LATEST.md is current - the {bookkeeping} artefact(s) "
                               f"newer than it changed only in close bookkeeping (status, "
                               f"verification), which is not review content")}
    if uncommitted and _only_close_status_block_differs(rr, latest):
        # The close's own stamp, and nothing else. Not uncommitted review work, so it does not
        # block the close that wrote it (nor the operator's follow-up sign-off invocation).
        return {"count": 0, "blocking": False,
                "detail": "reviews/LATEST.md carries only the close's own status stamp "
                          "uncommitted - commit it with the rest of the close paperwork"}
    if uncommitted:
        # Current in content, absent from history. Still blocking - an uncommitted close is
        # not a close - but the honest remedy is to commit, not to re-run the review.
        return {"count": 1, "blocking": True,
                "detail": "reviews/LATEST.md is current with all artefacts but UNCOMMITTED - "
                          "commit the close paperwork (re-running `review` will not change this)"}
    return {"count": 0, "blocking": True, "detail": "reviews/LATEST.md is current with all artefacts"}


def _handoff_present(root: str, handoff_id: str) -> dict:
    """Blocking close-gate check: a run that stopped short of its goal must leave the
    handoff, and a retro must LINK it.

    Both halves are the check. A handoff nobody links is a document nobody opens - the
    person picking the work up reads the retro, and the retro is where the pointer belongs.
    Presence alone would let the gate certify a handoff that is, in practice, invisible.
    """
    rr = Path(root)
    stem = str(handoff_id).replace("-", "").upper()
    d = rr / "sdlc-studio" / "handoffs"
    hits = sorted(d.glob(f"{stem}*.md")) if d.is_dir() else []
    if not hits:
        return {"count": 1, "blocking": True,
                "detail": f"missing handoff {handoff_id} - a run that stopped short of its "
                          f"goal owes one (`handoff generate --outcome <how it ended>`)"}
    retros = rr / "sdlc-studio" / "retros"
    disp = f"{stem[:2]}-{stem[2:]}" if stem.startswith("HO") else stem
    # A LINK, not a mention. A substring scan for the id passes on a retro whose prose
    # DENIES the handoff exists ("we never wrote HO-0001") - it would certify the very
    # absence it is meant to catch. The check is the markdown link shape the writer emits
    # and a reader can actually follow: a link whose target is the handoff file.
    import re
    link_re = re.compile(rf"\[[^\]]*\]\([^)]*{re.escape(stem)}[^)]*\.md\)", re.IGNORECASE)
    linked = [p.name for p in (sorted(retros.glob("RETRO*.md")) if retros.is_dir() else [])
              if link_re.search(p.read_text(encoding="utf-8"))]
    if not linked:
        return {"count": 1, "blocking": True,
                "detail": f"handoff {disp} exists but no retro links it (a markdown link to "
                          f"the handoff file - a bare mention of the id is not a link a "
                          f"reader can follow) - regenerate with `handoff generate --retro "
                          f"RETROxxxx`, so the person picking the work up finds it from the "
                          f"retro they read"}
    return {"count": 0, "blocking": True,
            "detail": f"handoff {disp} present, linked from {', '.join(linked)}"}


def _lessons_summary(root: str) -> dict:
    """Blocking close-gate lane: the committed LESSONS-SUMMARY.md must be the digest of the
    CURRENT lessons log. Summarising the sprint's lessons was doctrine - prose four steps long,
    of which only the retro was enforced - so an agent under effort pressure skipped it and the
    next sprint read a summary that predated the last one's learning.

    The verdict is recomputed, never trusted: `lessons.summary_status` regenerates the digest
    from the log and compares it with what the file says, so a lesson CLOSED since the last
    regeneration fails it exactly as an added one does. Nothing is stamped, so there is nothing
    to forge; the only way to green is for the file to say what the log implies.
    """
    import lessons
    blocking = _lessons_loop_blocking(root)
    status = lessons.summary_status(root)
    if not status["applicable"]:
        return {"count": 0, "blocking": blocking, "detail": status["reason"]}
    if not status["stale"]:
        return {"count": 0, "blocking": blocking, "detail": status["reason"]}
    n = len(status["added"]) + len(status["removed"]) or 1
    suffix = "" if blocking else " (advisory: lessons.loop is judgement)"
    return {"count": n, "blocking": blocking, "detail": status["reason"] + suffix}


def _lessons_validity(root: str) -> dict:
    """Blocking close-gate lane: no open lesson may sit past its validity horizon unclosed and
    unextended, and none may carry no horizon at all. The re-validation step, made mechanical.

    An unstamped lesson counts. A lane that reported only EXPIRED entries would pass every
    legacy log vacuously - a check that catches only the total case is not a check.
    """
    import lessons
    blocking = _lessons_loop_blocking(root)
    status = lessons.validity_status(root)
    if not status["applicable"]:
        return {"count": 0, "blocking": blocking, "detail": status["reason"]}
    n = len(status["expired"]) + len(status["unstamped"])
    suffix = "" if blocking or not n else " (advisory: lessons.loop is judgement)"
    return {"count": n, "blocking": blocking, "detail": status["reason"] + suffix}


# The close-gate lanes, bound as one set: the sprint close is a single obligation (write the
# retro, re-validate the lessons, regenerate the digest the next sprint reads), so the command
# the doctrine already prescribes - `gate --require-retro RETROxxxx` - carries all of it. A
# separate flag per step is a step an agent under effort pressure forgets.
LESSONS_CLOSE_CHECKS = {
    "lessons-summary": _lessons_summary,
    "lessons-validity": _lessons_validity,
}


VERIFY_TIMEOUT = 120  # per-verifier seconds; matches the verify_ac default
_MAX_NAMED = 10       # failing ACs listed by name before the detail is elided


def _elide(names: list[str]) -> str:
    """`a, b, c (+2 more)` - name the failures, bound the line."""
    more = f" (+{len(names) - _MAX_NAMED} more)" if len(names) > _MAX_NAMED else ""
    return ", ".join(names[:_MAX_NAMED]) + more


#: The verify lane's DECLARED cost budget, in seconds. Not a timeout - the lane always
#: finishes - but a number the run is measured against and reports exceeding, so "the release
#: gate is slow again" is a verdict the gate states rather than something an operator discovers
#: by killing it, after a run where the lane took over ten minutes and was therefore never run.
#:
#: Set to 600 against a MEASURED 453s after batching (160s for the one scoped pytest run plus
#: ~294s of verifiers that cannot be batched). Not 300: a threshold the lane exceeds on every
#: single run is a constant, and a warning that always fires is already switched off - which is
#: the defect CR0419 recorded about the capacity ceiling and D0064 had to repair. Re-derive it
#: from a measured run when the shape changes, never carry it forward silently.
VERIFY_LANE_BUDGET_S = 600


def _verify_acs(root: str, timeout: int = VERIFY_TIMEOUT, allow_external: bool = False,
                batch: bool = False) -> dict:
    """Blocking release-gate lane: EXECUTE every story's `Verify:` expression now, and fail
    on any AC that is red OR unproven, naming each one.

    Properties this lane must hold at once, and how it holds them:

    * It EXECUTES rather than reading the stored verify-report. A merged report carries a
      story's last green forward until something re-runs it, so a rotted verifier keeps
      reading PASS - the stale green that reaches a tag. Silence is not assertion integrity.
    * It does NOT write. `verify_ac run` in its normal mode rewrites each AC's
      `- **Verified:**` back-annotation and overwrites `.local/verify-report.json`; the gate
      is read-only (a pre-commit hook runs it), and a gate that edits tracked files while
      judging them is not a gate. So the lane calls `verify_story(dry_run=True)` per story:
      the verifiers run for real, nothing is written back, and the verdict is this run's.
    * A verifier the trust boundary REFUSED TO RUN is reported as BLOCKED, never as red. On a
      story stamped `Provenance: external`, a shell-backed verb is not executed (see
      `verify_ac`), so its result is not evidence about the code: reporting it as a failing AC
      sends the operator to debug a verifier that works. It still fails the lane - unproven is
      not proof - and `allow_external` is the deliberate way to run it and reach a green.
    * NOTHING TO PROVE IS NOT PROOF, and the guard is PER-STORY, not repo-wide. An empty story
      set fails (a wrong --root, a moved directory). A story with an UNSPECIFIED AC - one
      carrying no `Verify:` line at all - fails and is NAMED, because an omitted verifier is
      not a passed one. This is per-story on purpose: a repo-wide "some executable verifier
      exists" test let one green AC anywhere carry every verifier-less story along, so DELETING
      a rotted `Verify:` line reached a green gate. A story whose ACs are ALL declared
      `Verify: manual` is honestly declaring human verification and PASSES - the guard fires on
      omission, never on a declared judgement call.
    """
    import verify_ac
    rr = Path(root).resolve()
    stories = list(verify_ac.walk_stories(rr / "sdlc-studio" / "stories"))
    if not stories:
        return {"count": 1, "blocking": True,
                "detail": "no stories under sdlc-studio/stories - the verify lane proved "
                          "nothing about the AC layer (wrong --root?)"}
    started = time.time()
    jest_cache = verify_ac.jest_batch_cache(rr, timeout) if batch else None
    # Without batching this lane pays a cold pytest start PER CRITERION. 694 of this
    # workspace's 1,223 Verify lines are pytest and a bare start costs ~1.26s, so the spawns
    # alone were ~15 minutes and `--release` could not be completed inside any usable timeout.
    # One scoped run replaces them. The cache is empty on any failure, and an absent node is
    # never resolved from it, so a verifier always falls back to its own authoritative
    # subprocess rather than being reported green by a batch that ran nothing.
    pytest_cache = (verify_ac.pytest_batch_cache(
        rr, timeout, verify_ac.pytest_verifier_files(stories)) if batch else None)
    pytest_collected = (verify_ac.pytest_batch_collected(pytest_cache)
                        if pytest_cache else None)
    red: list[str] = []
    blocked: list[str] = []
    unspecified: list[str] = []
    acs = manual = unspec = 0
    for path in stories:
        report = verify_ac.verify_story(path, dry_run=True, timeout=timeout, repo_root=rr,
                                        jest_cache=jest_cache, pytest_cache=pytest_cache,
                                        pytest_collected=pytest_collected,
                                        allow_external=allow_external)
        story_id = sdlc_md.extract_record_id(path.stem) or path.stem
        acs += report.ac_count
        manual += report.manual
        unspec += report.unspecified
        if report.unspecified:
            unspecified.append(f"{story_id} ({report.unspecified} AC(s) with no Verify: line)")
        for f in report.failures:
            name = f"{story_id}::{f['ac']} ({f['verifier']})"
            (blocked if f.get("kind") == "blocked" else red).append(name)
    executable = acs - manual - unspec
    elapsed = int(time.time() - started)
    # State the cost and the scope. A `--release` run that got fast by judging less
    # is the exact defect `--release` exists to catch, so a reader must be able to tell the two
    # apart without rerunning it.
    cost = (f"{len(stories)} story/stories, {executable} executable AC(s) in {elapsed}s"
            f"{' (batched)' if batch else ' (per-AC subprocess)'}"
            f"{f' - OVER the {VERIFY_LANE_BUDGET_S}s declared budget' if elapsed > VERIFY_LANE_BUDGET_S else ''}")
    parts = []
    if unspecified:
        parts.append(f"{len(unspecified)} story/stories with an unspecified AC (no Verify: line "
                     f"- an omitted verifier is not a passed one; author one or mark it "
                     f"`Verify: manual`): {_elide(unspecified)}")
    if red:
        parts.append(f"{len(red)} red AC(s): {_elide(red)}")
    if blocked:
        parts.append(f"{len(blocked)} unproven AC(s) - verifier BLOCKED unrun by the "
                     f"trust boundary (story stamped Provenance: external): {_elide(blocked)}; "
                     f"pass --allow-external to run them once you trust the content")
    if parts:
        return {"count": len(unspecified) + len(red) + len(blocked), "blocking": True,
                "detail": "; ".join(parts) + f" [{cost}]"}
    if acs == 0:
        return {"count": 1, "blocking": True,
                "detail": f"no acceptance criteria across {len(stories)} story/stories - the "
                          f"verify lane proved nothing about the AC layer (wrong --root?)"}
    return {"count": 0, "blocking": True,
            "detail": f"{executable}/{acs} executable AC(s) green across "
                      f"{len(stories)} story/stories ({manual} manual) [{cost}]"}


def _review_legs(root: str) -> dict:
    """Blocking release-gate lane: every required DOCUMENT leg (PRD/TRD/TSD/Persona) must be
    PRESENT or explicitly WAIVED against a recorded decision id. A required leg that is absent
    and unwaived FAILS - the review cannot reclassify a missing leg as 'optional' in prose,
    because a waiver is a decisions-log row (`decisions.py waive --leg <leg>`), not narrative.

    The CODE leg is out of scope: it has no single artefact whose presence can be tested, so this
    lane makes no claim about it (decision D0022) - it states that exclusion in every verdict, so a
    green lane is never misread as certifying the code leg too.
    """
    import review_prep
    legs = review_prep.required_legs(Path(root).resolve())
    absent = sorted(k for k, v in legs.items() if not v["present"] and not v["waiver"])
    waived = sorted(f"{k} ({v['waiver']})" for k, v in legs.items()
                    if not v["present"] and v["waiver"])
    if absent:
        detail = (f"{len(absent)} required leg(s) absent and unwaived: {', '.join(absent)} - "
                  f"add the artefact, or record a waiver (`decisions.py waive --leg <leg> "
                  f"--rationale ...`); CODE leg out of scope (D0022)")
    else:
        present = sorted(k for k, v in legs.items() if v["present"])
        detail = (f"{len(present)} required leg(s) present"
                  + (f"; waived: {', '.join(waived)}" if waived else "")
                  + " (CODE leg out of scope, D0022)")
    return {"count": len(absent), "blocking": True, "detail": detail}


# What each bound lane is FOR, named in the refusal so an operator who deselects one is
# told what the verdict would have been printed over. A lane with no entry falls back to
# the generic phrase.
BOUND_LANE_SUBJECT = {
    "verify": "the AC layer",
    "review-legs": "the required document legs (present or waived)",
    "retro": "the sprint close's learning loop",
    "lessons-summary": "the sprint close's learning loop",
    "lessons-validity": "the sprint close's learning loop",
    "handoff": "the remaining-work handoff",
    "review-current": "the sprint close's review currency",
    "close-owed": "whether a sprint close is owed",
}


#: The gate's own declared cost budget, in seconds. Not a timeout - the gate always finishes -
#: but a number every run is measured against and reports exceeding, so "the gate got slower"
#: is a verdict it states rather than something an operator absorbs one commit at a time.
#:
#: Set to 45 against a MEASURED 33s for the standard lane set over this workspace. Not 30: a
#: threshold a normal run exceeds is a constant, and a warning that always fires is already
#: switched off. Re-derive it from a measured run when the lane set changes, never carry it
#: forward silently. A project overrides it with `gate.budget_seconds` in `.config.yaml`.
GATE_BUDGET_S = 45

#: Where the last run's cost is kept, so the next one can state a direction of travel.
GATE_COST_REL = "sdlc-studio/.local/gate-cost.json"


def gate_budget(root: str) -> float:
    """The declared budget for this project, in seconds."""
    try:
        override = sdlc_md.project_override(root, "gate.budget_seconds", None)
    except Exception:  # noqa: BLE001 - a cost report must never break the gate
        override = None
    try:
        value = float(override) if override is not None else float(GATE_BUDGET_S)
    except (TypeError, ValueError):
        return float(GATE_BUDGET_S)
    return value if value > 0 else float(GATE_BUDGET_S)


def read_gate_cost_baseline(root: str) -> float | None:
    """The last recorded run cost, or None when there is none to compare against."""
    try:
        data = json.loads((Path(root) / GATE_COST_REL).read_text(encoding="utf-8"))
        value = float(data["seconds"])
    except (OSError, ValueError, TypeError, KeyError):
        return None
    return value if value > 0 else None


def record_gate_cost(root: str, seconds: float) -> None:
    """Record this run's cost as the next run's baseline. Best effort: a cost report that
    could fail a gate would be worse than no cost report."""
    try:
        path = Path(root) / GATE_COST_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "seconds": round(float(seconds), 3),
            "recorded_at": datetime.now(timezone.utc).isoformat()}) + "\n",
            encoding="utf-8")
    except (OSError, ValueError, TypeError):
        pass


def _cost_report(root: str, results: list[dict], elapsed: float,
                 record: bool = False, scoped: bool = False) -> dict:
    """This run's cost, its budget, the lane that dominated it and the direction of travel.

    The DOMINANT lane is what makes this actionable: a total over budget with no lane named
    sends a reader to bisect the gate by hand, which is the same as not reporting it. A lane
    that RAISED is timed too - an error lane that dominated the run is exactly the one that
    needs naming."""
    budget = gate_budget(root)
    timed = [r for r in results if isinstance(r.get("seconds"), (int, float))]
    dominant = max(timed, key=lambda r: r["seconds"]) if timed else None
    baseline = read_gate_cost_baseline(root)
    over = elapsed > budget
    if over:
        detail = (f"{elapsed:.1f}s - OVER the {budget:g}s budget by "
                  f"{elapsed - budget:.1f}s")
    else:
        detail = f"{elapsed:.1f}s of a {budget:g}s budget"
    if dominant is not None:
        detail += f"; dominant lane: {dominant['check']} at {dominant['seconds']:.1f}s"
    if scoped:
        # No comparison either. A fraction of the lanes measured against a full-run baseline
        # reports a saving nobody made - the same defect as recording it, read from the other
        # side, and the more misleading of the two because it looks like good news.
        detail += ("; SCOPED run - not compared with the baseline and not recorded as it "
                   "(it measures fewer lanes)")
    elif baseline is None:
        detail += "; no baseline recorded yet, so this run becomes it"
    else:
        delta = elapsed - baseline
        pct = abs(delta) / baseline * 100.0
        if pct < 1.0:
            detail += f"; level with the {baseline:.1f}s baseline"
        else:
            detail += (f"; {pct:.0f}% {'slower' if delta > 0 else 'faster'} than the "
                       f"{baseline:.1f}s baseline")
    # A SCOPED run never becomes the baseline. `--only`/`--skip` cover a fraction of the lanes,
    # so recording one lowers the number the next FULL run is compared against, and that run
    # then reads as a regression against a figure that never measured the same thing. Stated in
    # the detail rather than silently skipped, or a reader cannot tell a scoped run from a
    # cheap one.
    if record and not scoped:
        record_gate_cost(root, elapsed)
    return {"seconds": round(elapsed, 3), "budget": budget, "over": over,
            "scoped": scoped, "recorded": bool(record and not scoped),
            "dominant": dominant["check"] if dominant is not None else None,
            "dominant_seconds": (round(dominant["seconds"], 3)
                                 if dominant is not None else None),
            "baseline": baseline, "detail": detail}


def run_gate(root: str = ".", only: list[str] | None = None,
             skip: list[str] | None = None, checks: dict | None = None,
             require_retro: str | None = None, release: bool = False,
             allow_external: bool = False,
             require_lessons: bool = False, require_handoff: str | None = None,
             require_review: bool = False, require_close: bool = False,
             conformance_scope: "set[str] | None" = None,
             record_cost: bool = False) -> dict:
    """Run the selected checks and report. `ok` is False only when a BLOCKING check
    fails; a non-blocking failure is reported but does not fail the gate. `require_retro`
    is the SPRINT-CLOSE gate: it binds a blocking check that the named batch retro exists,
    plus the lessons lanes (`require_lessons` binds those alone) - the close's learning loop
    is one obligation, so one command carries it. `release` adds the blocking `verify` lane -
    the pre-tag gate is then ONE command with ONE exit code, not a gate plus a separate verify
    run whose exit code can be dropped. A BOUND lane cannot be deselected: a mode's verdict
    printed over the lane that defines it is the false-assurance class this gate exists to
    refuse."""
    # Guard against a vacuous PASS on a wrong/missing root (a CI step pointed at the wrong
    # dir, or a failed checkout). "No project found" must FAIL, not look all-green. Only
    # applies to real runs; injected check registries (logic tests) skip it.
    if checks is None:
        rr = Path(root)
        if not rr.exists() or not (rr / "sdlc-studio").is_dir():
            return {"ok": False, "checks": [{
                "check": "scope", "count": 0, "blocking": True, "status": "fail",
                "detail": f"no SDLC project under {root} (no sdlc-studio/ dir) - wrong --root?"}]}
    registry = dict(checks) if checks is not None else dict(DEFAULT_CHECKS)
    bound: list[str] = []  # lanes a mode bound in: deselecting one is refused, not honoured
    # The sprint- and release-level Definition of Done, when the project declares one,
    # decides which close/release criteria the gate binds (the un-skippable close-down
    # enforcement restated as the sprint-DoD close clause; shipped defaults = today's
    # lanes, byte-compatible). A criterion whose tag the project removed is downgraded
    # to human judgement - reported as a visible warn row, never silently unbound.
    from lib import sdlc_md as _md  # local alias; gate already imports the lib package
    sprint_dod = _md.dor_dod_level_checks(root, "done", "sprint")
    release_dod = _md.dor_dod_level_checks(root, "done", "release")
    def _dod_enforced(dod, check_id: str) -> bool:
        return dod is None or check_id in dod
    downgraded: list[str] = []
    if require_retro:  # close-gate: bind the expected retro id into a blocking check
        if _dod_enforced(sprint_dod, "close.retro"):
            registry["retro"] = lambda r, _rid=require_retro: _retro_present(r, _rid)
            bound.append("retro")
        else:
            downgraded.append("close.retro")
    if require_retro or require_lessons:  # ...and the rest of the close's learning loop
        if _dod_enforced(sprint_dod, "close.lessons"):
            registry.update(LESSONS_CLOSE_CHECKS)
            bound.extend(LESSONS_CLOSE_CHECKS)
        else:
            downgraded.append("close.lessons")
    if require_handoff:  # a run that stopped short: the handoff must exist AND be linked
        registry["handoff"] = lambda r, _hid=require_handoff: _handoff_present(r, _hid)
        bound.append("handoff")
    if require_review:  # close-gate review leg: LATEST.md must be current with the artefacts
        if _dod_enforced(sprint_dod, "close.review"):
            registry["review-current"] = _review_current
            bound.append("review-current")
        else:
            downgraded.append("close.review")
    # NOT implied by `--release`. The lane is right and it ran nowhere, but `--release` is a
    # documented contract consuming projects depend on, and quietly adding a blocking lane to it
    # changes their gate as well as this one. The enforcement point is the TAG - see
    # `release_cut.tag_check`, which refuses a tag while any delivery unit owes a close. A tag,
    # not every push: this project commits straight to main in small green units, so a
    # mid-sprint push owing a close is normal and blocking it would train the bypass.
    if require_close:
        registry["close-owed"] = _close_owed
        bound.append("close-owed")
    if release:  # pre-tag: the diff-scoped lanes go back to the WHOLE workspace...
        # A commit is judged on what it changed; a TAG is judged on everything, so the debt a
        # pre-commit run reported as advisory blocks here. Swapped by identity against the
        # shipped scoped lane, so a caller's own injected entry of that name is left alone.
        for _name, _whole in WHOLE_WORKSPACE_LANES.items():
            if registry.get(_name) is DEFAULT_CHECKS.get(_name):
                registry[_name] = _whole
        # ...and the executing AC-verify lane joins the standard gate...
        # `--release` IMPLIES batching. It is the only run that executes every criterion in the
        # workspace, so it is the one run where a cold start per criterion is unaffordable -
        # a measured ~15 minutes of process spawns alone made the lane unrunnable
        # and therefore unrun. A scoped run keeps the per-criterion path.
        registry["verify"] = (lambda r, _x=allow_external:
                              _verify_acs(r, allow_external=_x, batch=True))
        bound.append("verify")
        # ...and every required document leg must be present or explicitly waived: a tag over a
        # silently-missing required artefact is the BG0110 hole this refuses to leave open.
        registry["review-legs"] = _review_legs
        bound.append("review-legs")
        # ...and the version strings must agree across their authoritative homes, CHANGELOG
        # included: a tag cut over a drifted version is a release nobody can identify later.
        registry["versions"] = _versions_strict
        bound.append("versions")
        # ...and the changelog lane is UPGRADED from its standard structure/hand-edit form to
        # the release superset that also refuses a stray uncomposed fragment at the cut. The
        # structure/hand-edit half runs regardless (it is in DEFAULT_CHECKS); the DoD downgrade
        # governs only the stray-fragment release criterion.
        if _dod_enforced(release_dod, "release.changelog"):
            registry["changelog-fragments"] = _changelog_fragments
            bound.append("changelog-fragments")
        else:
            downgraded.append("release.changelog")
    # The sprint close scopes conformance to the BATCH it owns. On a clean tree the diff scope is
    # empty, so the default lane judges the whole workspace and blocks an in-batch close on another
    # author's out-of-batch debt. Applied AFTER the release swap - a TAG still judges
    # everything - and bound only over the shipped scoped/whole lane, so a caller's injected entry
    # of that name is left alone. Bound: the close cannot deselect the lane that proves its batch.
    if conformance_scope is not None and not release:
        _scope = {str(x) for x in conformance_scope}
        if registry.get("conformance") in (DEFAULT_CHECKS.get("conformance"),
                                            WHOLE_WORKSPACE_LANES.get("conformance")):
            registry["conformance"] = lambda r, _s=_scope: _conformance(r, scope_ids=_s)
            if "conformance" not in bound:
                bound.append("conformance")
    # A wrong/typo'd --only/--skip (or a renamed check) must FAIL, not silently select
    # nothing and report a vacuous PASS - the false-assurance class LL0008 warns against.
    unknown = sorted({n for n in (list(only or []) + list(skip or [])) if n not in registry})
    if unknown:
        return {"ok": False, "checks": [{
            "check": "selection", "count": len(unknown), "blocking": True, "status": "fail",
            "detail": f"unknown check name(s): {', '.join(unknown)} - "
                      f"valid: {', '.join(sorted(registry))}"}]}
    selected = [n for n in registry
                if (not only or n in only) and (not skip or n not in skip)]
    if not selected:
        return {"ok": False, "checks": [{
            "check": "selection", "count": 0, "blocking": True, "status": "fail",
            "detail": "no checks selected - the gate proved nothing (check --only/--skip)"}]}
    # A bound lane is what MAKES the mode that bound it: `verify` a release gate, `retro` and
    # the lessons lanes a sprint close. Honouring a --skip/--only that deselects one would
    # print that mode's verdict over the very thing it claims to have examined - the
    # passing-looking command these modes exist to abolish. Refuse instead: a caller who does
    # not want the lane examined wants the standard gate, and should say so.
    dropped = [n for n in bound if n not in selected]
    if dropped:
        subjects = sorted({BOUND_LANE_SUBJECT.get(n, "what it claims to gate")
                           for n in dropped})
        what = " and ".join(subjects)
        return {"ok": False, "checks": [{
            "check": "selection", "count": len(dropped), "blocking": True, "status": "fail",
            "detail": f"deselecting the bound lane(s) {', '.join(dropped)} proves nothing "
                      f"about {what} - that verdict will not be printed over them. Drop the "
                      f"--skip/--only that excludes them, or drop the mode flag "
                      f"(--release/--require-retro/--require-lessons/--require-handoff) and "
                      f"run the standard gate"}]}
    results = []
    run_started = time.monotonic()
    for name in selected:
        lane_started = time.monotonic()
        try:
            r = registry[name](root)
            results.append({"check": name, "count": r["count"], "blocking": r["blocking"],
                            "status": "pass" if r["count"] == 0 else "fail",
                            "detail": r.get("detail", ""),
                            "seconds": round(time.monotonic() - lane_started, 3)})
        except Exception as exc:  # noqa: BLE001 - one buggy check must not abort the whole gate
            # A conventions shape error is the operator's config, not a buggy
            # check: it silently disables whichever lane read it (reconcile's
            # drift detection, most damagingly), so it must BLOCK - a green
            # gate over a disabled lane is the false assurance class.
            from lib.conventions import ConventionsError
            blocking = isinstance(exc, ConventionsError) or name in BLOCKING_ON_ERROR
            results.append({"check": name, "count": 1, "blocking": blocking, "status": "error",
                            "detail": f"check raised{'' if blocking else ', skipped'}: {exc}",
                            "seconds": round(time.monotonic() - lane_started, 3)})
    if downgraded:  # the document's downgrades, visible in the verdict - never silent
        results.append({"check": "dod-downgrades", "count": len(downgraded),
                        "blocking": False, "status": "warn",
                        "detail": f"downgraded to human-judged by definition-of-done.md "
                                  f"(tag removed): {', '.join(sorted(downgraded))}"})
    ok = all(r["status"] == "pass" for r in results if r["blocking"])
    return {"ok": ok, "checks": results,
            "cost": _cost_report(root, results, time.monotonic() - run_started,
                                 record=record_cost, scoped=bool(only or skip))}


def _split(v: str | None) -> list[str] | None:
    return [x.strip() for x in v.split(",") if x.strip()] if v else None


# --- test-relevant set -------------------------------------------------------------
# Which staged paths can change a test outcome, and therefore oblige the commit gate to
# pay for the unit suites. The first version of this named three directories by hand -
# scripts/, templates/, tools/ - and a hand enumeration is a lower bound: it is right
# about what somebody thought of and silent about everything else. The suites here read
# the hooks, the workflow file, `install.sh`, `package.json`, reference docs, help pages
# and shipped artefacts, none of which were in it, so a commit touching one of those took
# the docs-only fast path and skipped the very suite asserting over it.
#
# So the set is MEASURED from the suite sources rather than listed. Each test module is
# parsed and every path expression anchored on the module's own location - `Path(__file__)
# .resolve().parents[N] / "a" / "b"` and the names bound from it - is resolved to a
# concrete repo path. Anchoring is what makes this precise: a bare `root / "sdlc-studio"`
# inside a temporary-directory fixture names no repo file and is not counted, while
# `_REPO / ".githooks" / "pre-commit"` is.
#
# Two honest limits. A path assembled entirely at run time (a name from an environment
# variable, a glob result) is not visible to a source scan, so this is a measurement of
# the suite sources, not of a run; and where the two differ the resolution is deliberately
# over-inclusive - a directory used as a whole makes its whole subtree relevant. Both
# errors run suites that were not needed. Neither skips one that was.
TEST_SUITE_DIRS = (
    ".claude/skills/sdlc-studio/scripts/tests",
    "tools/tests",
)

# Fallback for a tree with no suites to measure (a consuming project installs the skill
# without them). Never the answer where the suites exist - that is the defect above.
LEGACY_TEST_RELEVANT = (
    ".claude/skills/sdlc-studio/scripts",
    ".claude/skills/sdlc-studio/templates",
    "tools",
)

_PATH_CALLS = {"Path", "str", "fspath"}
_PATH_PASSTHROUGH = {"resolve", "absolute", "expanduser"}


def _anchored_path(node: ast.AST, env: dict, self_path: str):
    """Resolve `node` to ("ABS", abspath) or ("STR", fragment), else None.

    Only expressions rooted in `__file__` (directly, or through a name already bound to
    such an expression) yield an ABS - that is the anchor that separates a real repo read
    from a fixture path built under a temporary directory.
    """
    if isinstance(node, ast.Constant):
        return ("STR", node.value) if isinstance(node.value, str) else None
    if isinstance(node, ast.Name):
        if node.id == "__file__":
            return ("ABS", self_path)
        hit = env.get(node.id)
        return ("ABS", hit) if hit else None
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id in _PATH_CALLS and node.args:
            return _anchored_path(node.args[0], env, self_path)
        if isinstance(fn, ast.Attribute) and fn.attr in _PATH_PASSTHROUGH:
            return _anchored_path(fn.value, env, self_path)
        return None
    if isinstance(node, ast.Attribute):
        if node.attr == "parent":
            base = _anchored_path(node.value, env, self_path)
            if base and base[0] == "ABS":
                return ("ABS", os.path.dirname(base[1]))
        return None
    if isinstance(node, ast.Subscript):
        holder = node.value
        if isinstance(holder, ast.Attribute) and holder.attr == "parents":
            base = _anchored_path(holder.value, env, self_path)
            idx = node.slice
            if (base and base[0] == "ABS" and isinstance(idx, ast.Constant)
                    and isinstance(idx.value, int) and 0 <= idx.value < 12):
                out = base[1]
                for _ in range(idx.value + 1):
                    out = os.path.dirname(out)
                return ("ABS", out)
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _anchored_path(node.left, env, self_path)
        right = _anchored_path(node.right, env, self_path)
        if not left or not right or right[0] != "STR":
            return None
        if left[0] == "ABS":
            return ("ABS", os.path.normpath(os.path.join(left[1], right[1])))
        return ("STR", left[1].rstrip("/") + "/" + right[1].lstrip("/"))
    return None


# Attribute methods that read the filesystem at their receiver. A path reaching one of
# these is a path the test reads: `.read_text` / `.open` name a file, `.glob` / `.iterdir`
# name a directory (so its whole subtree is relevant). This is what separates a read from a
# path merely passed to a helper - `foo(SKILL, "x")` hands SKILL on without touching disk,
# and counting that would drag the whole skill directory in and defeat the docs-only skip.
_READ_METHODS = frozenset({
    "read_text", "read_bytes", "open", "glob", "rglob", "iterdir", "walk",
    "exists", "is_file", "is_dir", "stat", "lstat", "scandir", "samefile",
})
# Builtin / stdlib callables whose FIRST argument is a path they read.
_READ_FUNCS = frozenset({"open", "listdir", "scandir", "walk"})


def _read_targets(tree: ast.AST):
    """Yield the AST node of every path expression the module reads on disk."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Attribute) and fn.attr in _READ_METHODS:
            yield fn.value
        elif isinstance(fn, ast.Name) and fn.id in _READ_FUNCS and node.args:
            yield node.args[0]
        elif (isinstance(fn, ast.Attribute) and fn.attr in _READ_FUNCS
              and isinstance(fn.value, ast.Name) and fn.value.id == "os" and node.args):
            yield node.args[0]


def _module_read_paths(src: str, module_path: str, root: str) -> set[str]:
    """Repo-relative paths the module at `module_path` reads, measured from its source.

    Two kinds of evidence, chosen so the set is over-inclusive on files and precise on
    directories - the direction that never skips a suite that was needed while not dragging
    a whole tree in on a bare anchor:

    * A maximal anchored expression resolving to a FILE - `SKILL_DIR / "reference-sprint.md"`,
      or a name bound to it. A test that names a specific file is a test about that file,
      whether it reads it directly or hands it to a helper.
    * A DIRECTORY only where it is the receiver of a real read - a `.glob`, an `.iterdir`,
      an `os.listdir`. A directory merely passed to a helper (`foo(SKILL_DIR, "x")`) touches
      no disk here, and counting it would pull the whole skill tree in and delete the
      docs-only fast path this measurement exists to keep honest.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    env: dict[str, str] = {}
    # Three passes so a name bound from an earlier name resolves whatever the order.
    for _ in range(3):
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)):
                got = _anchored_path(node.value, env, module_path)
                if got and got[0] == "ABS":
                    env[node.targets[0].id] = got[1]

    def _record(abs_path: str, want_dir: bool, out: set[str]) -> None:
        if not abs_path.startswith(root + os.sep):
            return
        if os.path.exists(abs_path):
            # What is on disk classifies it: a bare directory is only relevant at a
            # read-site (below), and a read-site naming a file is not a directory read.
            if want_dir != os.path.isdir(abs_path):
                return
        # A path the suites name but that is NOT on disk is KEPT, classified by how the
        # suite used it. The set is measured from the suite SOURCES, and a staged deletion
        # or rename is exactly the change that breaks the suite reading it - dropping it
        # here would skip the suites on the one commit that most needs them.
        out.add(os.path.relpath(abs_path, root).replace(os.sep, "/"))

    out: set[str] = set()
    # Maximal anchored expressions: a node no anchored ancestor contains. The prefixes along
    # the way (`_REPO`, `.claude`, `sdlc-studio`) are inner and excluded - counting them is
    # what made every commit test-relevant.
    inner: set[int] = set()
    for node in ast.walk(tree):
        if not _anchored_path(node, env, module_path):
            continue
        for child in ast.walk(node):
            if child is not node:
                inner.add(id(child))
    for node in ast.walk(tree):
        if id(node) in inner:
            continue
        got = _anchored_path(node, env, module_path)
        if got and got[0] == "ABS":
            _record(got[1], want_dir=False, out=out)
    # Directory read-sites: the receiver of a glob / iterdir / listdir naming a directory.
    for target in _read_targets(tree):
        got = _anchored_path(target, env, module_path)
        if got and got[0] == "ABS":
            _record(got[1], want_dir=True, out=out)
    return out


#: Per-process memo for the suite measurement, keyed by the suite files' own
#: (path, mtime, size) signature. One `--suite-decision` invocation asks for it three
#: times - the surface hash, the relevance set and the selection - and parsing forty large
#: test modules three times is most of that command's cost. Keyed on the signature rather
#: than on the root, so a caller that EDITS a test module and asks again (which is what the
#: tests here do, and what a watch loop would do) gets the new answer, not the cached one.
_READ_MAP_MEMO: dict[str, tuple[tuple, dict[str, set[str]] | None]] = {}


def _suite_signature(root: str) -> tuple:
    sig: list[tuple] = []
    for suite in TEST_SUITE_DIRS:
        suite_dir = os.path.join(root, suite)
        if not os.path.isdir(suite_dir):
            continue
        for name in sorted(os.listdir(suite_dir)):
            if not name.endswith(".py"):
                continue
            try:
                st = os.stat(os.path.join(suite_dir, name))
            except OSError:
                continue
            sig.append((suite, name, st.st_mtime_ns, st.st_size))
    return tuple(sig)


def suite_read_map(root: str = ".") -> dict[str, set[str]] | None:
    """test module (repo-relative) -> the repo-relative paths its own source reads.

    The per-module form of the measurement `test_relevant_paths` unions. Selection needs
    the attribution, not only the union: a changed file that no import edge can reach - a
    reference doc, a hook, a shipped artefact - is still reachable from the ONE suite module
    that names it, and that is precisely the module that must run.

    None when there are no suites to measure (a consuming project installs the skill without
    them), which is the same condition that sends `test_relevant_paths` to its fallback.
    """
    root = os.path.abspath(root)
    signature = _suite_signature(root)
    cached = _READ_MAP_MEMO.get(root)
    if cached is not None and cached[0] == signature:
        return cached[1]
    out: dict[str, set[str]] = {}
    scanned = False
    for suite in TEST_SUITE_DIRS:
        suite_dir = os.path.join(root, suite)
        if not os.path.isdir(suite_dir):
            continue
        for name in sorted(os.listdir(suite_dir)):
            if not name.endswith(".py"):
                continue
            module_path = os.path.join(suite_dir, name)
            try:
                with open(module_path, encoding="utf-8") as handle:
                    src = handle.read()
            except OSError:
                continue
            scanned = True
            rel = os.path.relpath(module_path, root).replace(os.sep, "/")
            out[rel] = _module_read_paths(src, module_path, root)
    measured = out if scanned else None
    _READ_MAP_MEMO[root] = (signature, measured)
    return measured


def test_relevant_paths(root: str = ".") -> set[str]:
    """The measured set of repo-relative paths the shipped suites read.

    A directory in the set means its whole subtree; a file means that file.
    """
    root = os.path.abspath(root)
    read_map = suite_read_map(root)
    if read_map is None:
        return {p for p in LEGACY_TEST_RELEVANT if os.path.exists(os.path.join(root, p))}
    measured: set[str] = set()
    for paths in read_map.values():
        measured |= paths
    for suite in TEST_SUITE_DIRS:
        # A suite directory is itself read by whatever discovers it.
        if os.path.isdir(os.path.join(root, suite)):
            measured.add(suite)
    # The suites import the scripts they exercise, and a template edit can change an
    # assertion over the shipped payload. Those two are structural, not measurable from a
    # path expression, so they are unioned in rather than replaced by the measurement.
    # Unioned WITHOUT an existence test, for the reason `_record` keeps a missing path: a
    # commit deleting one of these trees is a commit the suites must run on, and a set
    # filtered by what survives the commit cannot see it.
    measured |= set(LEGACY_TEST_RELEVANT)
    return _minimal({p for p in measured if p and not p.startswith("..")},
                    keep_under=listing_only_paths(root))


#: Directories read at directory level for their CONTENTS, never as a listing. No declaration
#: may make one of these listing-only: an edit inside them changes what a suite asserts, and a
#: declaration is a narrowing, so the floor has to be stated rather than inferred.
CONTENT_READ_DIRS = (".githooks",)


#: The module-level name a test declares to say "I read this directory's LISTING, not the
#: contents of the files in it". Opt-in, so the default stays fully relevant: a module that
#: declares nothing is treated exactly as before, and a wrong declaration is a test defect that
#: `test_relevant_paths` reports rather than a silent widening.
LISTING_DECL = "GATE_LISTING_ONLY"


#: A path's artefact id: the leading id token of the file's basename, as the artefact naming
#: convention writes it (`BG0399-file-finding-....md`). A file whose name carries none cannot
#: be matched against an id scope, which is why the caller degrades to structural for it.
_PATH_ID = re.compile(r"^(?P<id>[A-Z]{2,4}-?\d{3,4})[-.]")


def _path_artefact_id(path: str) -> str | None:
    """The artefact id a path names, or None when its basename carries none."""
    base = os.path.basename(str(path).strip().replace(os.sep, "/"))
    match = _PATH_ID.match(base)
    return match.group("id").replace("-", "") if match else None


def listing_only_scopes(root: str = ".") -> dict:
    """Each listing-only directory mapped to the ids its structural read depends on.

    `None` means the whole directory, which is what a bare-string declaration has always
    meant and what a declaration naming no readable ids falls back to. A `frozenset` narrows
    it: only a structural change to an artefact whose id is in the set can change the
    declaring module's answer.

    Two declaration shapes, and the narrower one is opt-in::

        GATE_LISTING_ONLY = ("sdlc-studio",)                             # whole directory
        GATE_LISTING_ONLY = ({"path": "sdlc-studio", "ids": ("BG0288",)},)  # these ids only

    The fail-safe direction is preserved throughout, because this is a narrowing and a
    narrowing that goes wrong makes a real change look irrelevant. An unparseable declaration,
    an unreadable `ids` value and an empty id set all degrade to the whole directory - slower
    than intended, never blind. The same reasoning governs the path side: a directory the
    module does not actually read is ignored, and the shipped code trees are excluded
    outright, since `scripts/`, `templates/` and `tools/` are imported and asserted over."""
    root = os.path.abspath(root)
    read_map = suite_read_map(root)
    if read_map is None:
        return {}
    protected = ({p.rstrip("/") for p in LEGACY_TEST_RELEVANT}
                 | {s.rstrip("/") for s in TEST_SUITE_DIRS}
                 | {d.rstrip("/") for d in CONTENT_READ_DIRS})
    # Who READS each directory, so a declaration can be held to covering all of them. A
    # declaration is one module's statement about its OWN read; honouring it tree-wide let it
    # silence a second module's CONTENT read of the same directory, which the second module
    # never agreed to and cannot see.
    readers: dict = {}
    for module, paths in read_map.items():
        for rel in paths:
            readers.setdefault(rel.rstrip("/"), set()).add(module)
    declarers: dict = {}
    out: dict = {}
    for module, paths in read_map.items():
        try:
            with open(os.path.join(root, module), encoding="utf-8") as handle:
                tree = ast.parse(handle.read())
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == LISTING_DECL):
                continue
            try:
                declared = ast.literal_eval(node.value)
            except ValueError:
                continue
            entries = declared if isinstance(declared, (list, tuple)) else [declared]
            for entry in entries:
                if isinstance(entry, dict):
                    rel = str(entry.get("path", "")).strip().strip("/")
                    ids = _declared_ids(entry.get("ids"), root, str(entry.get("path", "")).strip().strip("/"))
                else:
                    rel = str(entry).strip().strip("/")
                    ids = None
                # Declared AND measured: a declaration about a directory this module never
                # reads narrows nothing, and letting it through would be a way to exempt a
                # tree by writing its name down.
                if not rel or rel not in paths or rel in protected:
                    continue
                # UNDER a protected tree counts as protected. `rel in protected` was an exact
                # string test, so declaring `.githooks/pre-commit` walked straight past a floor
                # written to be absolute - and "listing-only" is meaningless for a FILE, which
                # has no listing, so a file declaration is a pure content-blindness switch.
                if any(rel == d or rel.startswith(d.rstrip("/") + "/")
                       for d in (str(x).rstrip("/") for x in protected)):
                    continue
                if not os.path.isdir(os.path.join(root, rel)):
                    continue
                declarers.setdefault(rel, set()).add(module)
                if rel in out:
                    # Two modules reading the same tree: the union of what they depend on,
                    # and a single whole-directory declaration wins over any id set. One
                    # module's narrowing must never speak for another's read - the defect
                    # BG0398 records about applying a declaration globally.
                    prior = out[rel]
                    out[rel] = None if prior is None or ids is None else prior | ids
                else:
                    out[rel] = ids
    # UNANIMITY. A directory is listing-only only when every module that reads it says so. One
    # module's narrowing must never speak for another's read: a tree-wide honouring made a
    # second module's content read of the same directory invisible, so an edit it asserts over
    # answered `test-relevant: no` while its own assertion would have failed.
    return {rel: ids for rel, ids in out.items()
            if readers.get(rel, set()) <= declarers.get(rel, set())}


def _declared_ids(value, root: str | None = None, rel: str | None = None) -> "frozenset | None":
    """The id set a declaration names, or None - meaning the WHOLE directory - when it names
    none this module can trust.

    The fail-safe list used to cover every malformed shape and miss the likeliest one: a
    well-formed but WRONG id. `ids: ('BG288',)` for `BG0288` is a perfectly good tuple of a
    perfectly good string, and it narrowed the tree to an id that matches nothing - so a
    structural change to the very artefact the declaring module asserts about answered
    `test-relevant: no`. A false green, from a typo.

    So every declared id must RESOLVE to a file under the declared directory. One that does not
    voids the whole narrowing rather than being dropped: a declaration half of which is wrong is
    a declaration nobody has checked, and the safe reading of it is the un-narrowed one."""
    if not isinstance(value, (list, tuple, set, frozenset)):
        return None
    ids = {str(i).strip().replace("-", "").upper() for i in value if str(i).strip()}
    if not ids:
        return None
    if root is None or rel is None:
        return frozenset(ids)
    base = os.path.join(root, rel)
    present = set()
    for dirpath, _dirnames, filenames in os.walk(base):
        for name in filenames:
            got = _path_artefact_id(os.path.join(dirpath, name))
            if got:
                present.add(got)
    unresolved = ids - present
    if unresolved:
        # Reported through the same channel a wrong declaration already uses: the narrowing is
        # withheld, so the cost is a slower gate rather than an unrun suite.
        sdlc_md.debug("gate._declared_ids",
                      ValueError(f"{rel}: declared id(s) {sorted(unresolved)} resolve to no "
                                 f"artefact - the narrowing is withheld"))
        return None
    return frozenset(ids)


def listing_only_paths(root: str = ".") -> set[str]:
    """Directories the suites read as a LISTING - which files exist - and never open.

    A census over the artefact workspace answers a question about the tree's SHAPE. Adding,
    deleting or renaming a file under it can change that answer; editing the prose inside one
    cannot. Recording such a directory as fully relevant made every artefact commit pay for
    both suites, because one entry then absorbed the four narrow reads under it.

    The set only - see `listing_only_scopes` for which ids each entry's read depends on."""
    return set(listing_only_scopes(root))


def _minimal(entries: set[str], keep_under: set[str] | None = None) -> set[str]:
    """The set with every entry another entry already covers removed.

    `_matches_relevant` reads every entry as a prefix, so an entry under another answers
    nothing the covering one does not - dropping it cannot change any verdict. It keeps the
    listing readable: without this, one measured directory drags in every path a fixture
    ever built beneath it, and a set nobody can read is a set nobody checks.

    `keep_under` is the exception, and it is the whole repair: an entry nested under a
    LISTING-ONLY directory is NOT covered by it, because the covering entry answers only for
    structural change. Dropping it would lose the content relevance of `sdlc-studio/trd.md`
    behind a census of `sdlc-studio`."""
    keep_under = {k.rstrip("/") for k in (keep_under or set())}
    prefixes = {e.rstrip("/") for e in entries}
    return {e for e in entries
            if not any(e.startswith(p + "/")
                       for p in prefixes if p != e.rstrip("/") and p not in keep_under)}


def is_test_relevant(paths, root: str = ".", structural=None) -> bool:
    """True when any of `paths` (repo-relative) can change a test outcome.

    `structural` is the subset of `paths` whose change is an ADD, DELETE or RENAME. A path
    that matches only listing-only entries is relevant just when it is structural: the census
    reading that directory sees a file appear or vanish, and sees nothing at all when the words
    inside one change. Omit it and every path is treated as structural, which is the old
    behaviour and the safe direction - an unanswered question runs the suites.

    A listing-only entry may narrow further by naming the ids its read depends on, in which
    case a structural change is relevant only for those ids. A path whose basename carries no
    id cannot be judged against that set and stays relevant, the same direction
    `structural=None` degrades in."""
    relevant = test_relevant_paths(root)
    scopes = {p.rstrip("/"): ids for p, ids in listing_only_scopes(root).items()}
    listing = set(scopes)
    content = relevant - listing
    structural = None if structural is None else {str(p).strip() for p in structural}
    for p in paths:
        if _matches_relevant(p, content):
            return True
        if not _matches_relevant(p, listing):
            continue
        if structural is not None and str(p).strip() not in structural:
            continue
        # `structural is None` means the CALLER COULD NOT SAY. The id scope must not answer a
        # question nobody asked: applying it here turned the documented fail-safe ("an
        # unanswered question runs the suites") into a "no" for every unscoped id.
        if structural is None or _in_scope(p, scopes):
            return True
    return False


def _in_scope(path: str, scopes: dict) -> bool:
    """Whether a structural change to `path` can change any declaration that covers it.

    True for every entry that named no ids. For a scoped entry it asks whether the path's own
    artefact id is one it named - and an unidentifiable path answers True, because a scope
    cannot rule out what it cannot recognise."""
    ident = _path_artefact_id(path)
    for entry, ids in scopes.items():
        if not _matches_relevant(path, {entry}):
            continue
        if ids is None or ident is None or ident in ids:
            return True
    return False


def _matches_relevant(path: str, relevant: set[str]) -> bool:
    # Strip a leading "./" as a PREFIX, never as a character class: `lstrip("./")` would
    # eat the leading dot of `.githooks/pre-commit` and quietly match nothing.
    candidate = path.strip().replace(os.sep, "/")
    while candidate.startswith("./"):
        candidate = candidate[2:]
    candidate = candidate.lstrip("/")
    if not candidate:
        return False
    return any(candidate == entry or candidate.startswith(entry.rstrip("/") + "/")
               for entry in relevant)


def _matched_entries(paths, root: str = ".", structural=None) -> set[str]:
    """Which relevance entries each path matched, and why - the answer to "what dragged the
    suites in this time". Without it, one reader collapsing the set is invisible from the tool
    and has to be found by reading the read map by hand, which is how it went unnoticed."""
    relevant = test_relevant_paths(root)
    listing = {p.rstrip("/") for p in listing_only_paths(root)}
    structural = None if structural is None else {str(p).strip() for p in structural}
    out: set[str] = set()
    for p in paths:
        for entry in relevant:
            if not _matches_relevant(p, {entry}):
                continue
            if entry.rstrip("/") in listing:
                if structural is None or str(p).strip() in structural:
                    out.add(f"{entry} (listing-only, structural change)")
            else:
                out.add(entry)
    return out


#: Git name-status letters that mean the SET of files changed rather than the bytes in one:
#: added, deleted, renamed, copied. A listing-only directory is relevant to exactly these.
_STRUCTURAL_STATUS = ("A", "D", "R", "C")


def _split_name_status(lines) -> tuple[list[str], set[str] | None]:
    """`(paths, structural)` from stdin that may be `--name-only` OR `--name-status`.

    Accepts both because the answer must not depend on how the caller was spelled: a plain path
    list yields `structural=None`, which `is_test_relevant` reads as "unknown, treat everything
    as structural" - the old behaviour, and the safe direction. A rename line carries both names
    and both are recorded, since the old path vanishing is as structural as the new one arriving.
    """
    paths: list[str] = []
    structural: set[str] = set()
    tagged = False
    for line in lines:
        parts = [p for p in line.rstrip("\n").split("\t") if p != ""]
        if len(parts) >= 2 and re.fullmatch(r"[A-Z]\d*", parts[0]):
            tagged = True
            names = parts[1:]
            paths.extend(names)
            if parts[0][0] in _STRUCTURAL_STATUS:
                structural.update(names)
        elif parts:
            paths.append(parts[0])
    return paths, (structural if tagged else None)


def cmd_test_relevant(args: argparse.Namespace) -> int:
    paths = list(args.test_relevant or [])
    structural = None
    asked = bool(paths)
    if not paths and not sys.stdin.isatty():
        paths, structural = _split_name_status(
            [line for line in sys.stdin.read().splitlines() if line.strip()])
        asked = True   # an EMPTY pipe is an empty commit, not a request for the listing
    if getattr(args, "format", "text") == "json":
        relevant = is_test_relevant(paths, args.root, structural)
        print(json.dumps({"set": sorted(test_relevant_paths(args.root)),
                          "listing_only": sorted(listing_only_paths(args.root)),
                          "matched": sorted(_matched_entries(paths, args.root, structural)),
                          "relevant": relevant}, indent=2))
        return 0 if (not asked or relevant) else 1
    if not asked:
        for entry in sorted(test_relevant_paths(args.root)):
            print(entry)
        return 0
    relevant = is_test_relevant(paths, args.root, structural)
    # A SENTINEL line, not just the exit code. A caller (the commit hook) must be able to tell
    # a real answer from a stub that exits 0 for every argument - the pre-commit fixtures stub
    # gate.py to `sys.exit(0)`, which without this would read as "everything is relevant". The
    # hook keys on this line and falls back to its own coarse regex when it is absent.
    print(f"test-relevant: {'yes' if relevant else 'no'}")
    return 0 if relevant else 1
# --- end test-relevant set ---------------------------------------------------------


# --- suite decision ----------------------------------------------------------------
# Whether the unit suites need to run at all, and if so over what. `--test-relevant` above
# answers a FILE-TYPE question - did this commit touch anything a test reads - and it is
# binary in both directions: a commit touching one script pays for every test, and two
# consecutive commits over an identical tree pay twice.
#
# Measured over one working day on this repository: the suites ran about 52 times for about
# 218 minutes, against about 35 minutes of delivery. A large share of those runs were over a
# byte-identical source tree - paperwork commits, and closes retried after a refusal. Nothing
# about the code had changed, so nothing about the answer could have.
#
# So the question asked here is the content one: has the test-relevant SURFACE changed since
# the last run that was green? The surface is the same measured set `test_relevant_paths`
# reports, hashed by content, and the verdict is a record naming the run that earned it.
#
# Every failure degrades to RUNNING. An unhashable surface, an absent or malformed record, a
# record with no hash, a record whose verdict was red: each of those is a thing not known, and
# a cache that answered "skip" on a thing not known would be the false-green class this whole
# gate exists to refuse. Slow is the safe direction; silent is not.

#: Where the last suite verdict is recorded. Under `.local/`, so it is untracked and a gate
#: run never dirties the tree it is judging.
SUITE_VERDICT_REL = "sdlc-studio/.local/gate-suite-verdict.json"

#: Directory names never hashed into the surface. Build caches and generated local state
#: change on every run, so hashing them would make the surface differ from itself and the
#: skip could never fire - a cache nothing can hit is a cache that was never built.
_SURFACE_SKIP_DIRS = frozenset({
    "__pycache__", ".git", ".local", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "node_modules", ".venv", "venv", ".tox",
})


def surface_files(root: str = ".") -> list[str]:
    """Every TRACKED repo-relative file, sorted - not the measured read set.

    The measured set is a proxy, and a proxy is the wrong instrument for "did anything change".
    Measured on this repo it omitted 233 tracked files - SKILL.md, every help/ and reference-*.md
    page, README, CHANGELOG, AGENTS.md, the workflows - and an edit to SKILL.md left the digest
    BYTE-IDENTICAL while three tests in test_command_audit.py went red. A cache that can mask a
    change is the false-green this module exists to refuse, so the digest now covers everything
    git tracks: 2,517 files hash in 0.03s, which makes the precision worth nothing and the
    completeness worth everything.

    Falls back to the measured surface only when git cannot answer, and that fallback is reported
    by `surface_hash` returning None rather than a narrower digest, so an unanswerable probe runs
    the suites instead of reusing a verdict taken over less.
    """
    root = os.path.abspath(root)
    import subprocess as _sp  # local: gate.py keeps heavy imports off the cold paths
    try:
        proc = _sp.run(["git", "-C", root, "ls-files", "-z"],
                       capture_output=True, text=True, timeout=30)
        if proc.returncode == 0:
            return sorted(p for p in proc.stdout.split("\0") if p)
    except (OSError, _sp.SubprocessError):
        pass
    return []


def surface_hash(root: str = ".") -> str | None:
    """A content digest of the test-relevant surface, or None when it cannot be taken.

    None is UNKNOWN, never "unchanged": the caller runs the suites on it. Names are hashed
    alongside contents, so a rename that preserves every byte still changes the digest."""
    import hashlib
    root_abs = os.path.abspath(root)
    digest = hashlib.sha256()
    files = surface_files(root_abs)
    if not files:
        # An empty surface is git declining to answer, not a tree with nothing in it. Hashing
        # nothing yields a STABLE digest, which would make the skip fire for ever on any
        # directory git cannot enumerate - the false-green this returns None to avoid.
        return None
    try:
        for rel in files:
            path = os.path.join(root_abs, rel)
            digest.update(rel.encode("utf-8", "surrogateescape") + b"\0")
            if os.path.isfile(path):
                with open(path, "rb") as handle:
                    digest.update(hashlib.sha256(handle.read()).hexdigest().encode("ascii"))
            else:
                digest.update(b"ABSENT")   # a named path that is gone is a CHANGE
            digest.update(b"\n")
    except OSError:
        return None
    return digest.hexdigest()


def read_suite_verdict(root: str = ".") -> dict | None:
    """The recorded suite verdict, or None when there is nothing trustworthy to read.

    One reader for absent, unreadable and malformed, because the caller must treat all three
    the same way: as an answer it does not have."""
    path = Path(root) / SUITE_VERDICT_REL
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    if not isinstance(data, dict) or not data.get("run"):
        return None
    return data


def record_suite_verdict(root: str = ".", *, run: str, status: str = "green",
                         mode: str = "full", digest: str | None = None) -> Path:
    """Record `status` for the current surface, attributed to the run that earned it.

    `mode` is how much of the suite earned it - `full` or `selected`. It is recorded because
    a green from a SELECTED run is evidence about the tests that ran, not about the suite, so
    a boundary must not reuse it (see `suite_decision`). A record with no mode is read as
    UNKNOWN coverage, which a boundary also declines."""
    path = Path(root) / SUITE_VERDICT_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "run": str(run),
        "status": str(status),
        "mode": str(mode),
        "surface_hash": digest if digest is not None else surface_hash(root),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


# --- test selection ---
#: The repo map's index, where `repo map build` writes it.
REPO_MAP_REL = "sdlc-studio/.local/repo-map.json"


def _import_graph(root: str) -> dict[str, list[str]] | None:
    """Repo-relative path -> its imports, for every indexed source file, or None.

    Prefers the on-disk repo map, and only while it is NEWER than every file it indexes.
    A stale graph would narrow a run using edges the code no longer has, which is the one
    way selection could lose a defect rather than defer finding it - so a map that is not
    demonstrably current is rebuilt in memory instead (pure stdlib, a couple of seconds
    over this repository, against the minutes a full suite costs).
    """
    try:
        import repo_map
    except Exception:  # noqa: BLE001 - no map means no selection, never a wrong selection
        return None
    rootp = Path(root).resolve()
    ignores = set(repo_map.DEFAULT_IGNORES)
    try:
        sources = list(repo_map.walk_source_files(rootp, ignores))
    except OSError:
        return None
    try:
        map_mtime = (rootp / REPO_MAP_REL).stat().st_mtime
    except OSError:
        map_mtime = None
    if map_mtime is not None:
        newest = 0.0
        try:
            for src in sources:
                newest = max(newest, src.stat().st_mtime)
        except OSError:
            newest = float("inf")     # cannot prove currency: do not trust the map
        if newest <= map_mtime:
            try:
                data = json.loads((rootp / REPO_MAP_REL).read_text(encoding="utf-8"))
                files = data.get("files")
                if isinstance(files, dict) and files:
                    return {str(k): list((v or {}).get("imports") or [])
                            for k, v in files.items() if isinstance(v, dict)}
            except (OSError, ValueError, TypeError, AttributeError):
                pass                  # an unreadable map is no map
    try:
        entries = repo_map.build_index(rootp, ignores)
    except Exception:  # noqa: BLE001 - as above
        return None
    return {path: list(entry.imports) for path, entry in entries.items()} or None


def _normalise(paths) -> list[str]:
    out: list[str] = []
    for raw in paths:
        candidate = str(raw).strip().replace(os.sep, "/")
        while candidate.startswith("./"):
            candidate = candidate[2:]
        candidate = candidate.lstrip("/")
        if candidate and candidate not in out:
            out.append(candidate)
    return out


def select_tests(root: str = ".", changed: "list[str] | None" = None) -> dict:
    """The test modules `changed` can reach, or an unresolved verdict meaning "run all".

    `{"resolved": bool, "selectors": [...], "total": int, "excluded": int, "reason": str}`.
    `resolved` False ALWAYS means run everything - never run nothing.

    Two routes, because the suites read two kinds of thing. A changed Python file is followed
    through the import graph transitively (the repo map's own resolution, so this and the hub
    score cannot come to disagree about what an import names). A changed file the graph has no
    edge for - a reference doc, a hook, a shipped artefact - is attributed to the suite modules
    whose SOURCE names it, which is the measurement `test_relevant_paths` already takes.

    Anything neither route resolves widens the run: an unanswerable changed-file probe, a file
    in the surface no module claims, and a resolvable change that reaches no test at all. That
    last one matters most - a selection of zero tests reported as a pass is a vacuous green,
    which is the failure this whole gate exists to refuse.
    """
    result: dict = {"resolved": False, "selectors": [], "total": 0, "excluded": 0,
                    "reason": ""}
    read_map = suite_read_map(root)
    if read_map is None:
        result["reason"] = "no shipped suites here to select from - running everything"
        return result
    modules = sorted(m for m in read_map if os.path.basename(m).startswith("test_"))
    result["total"] = len(modules)
    if changed is None:
        result["reason"] = ("the changed-file probe could not answer, so nothing is known "
                            "about this diff - running everything")
        return result
    norm = _normalise(changed)
    if not norm:
        result["reason"] = "no changed path was named - running everything"
        return result
    module_set = set(modules)
    relevant = test_relevant_paths(root)
    graph = _import_graph(root)
    dependents = {}
    if graph is not None:
        import repo_map
        dependents = repo_map.dependents_index(graph)
    selected: set[str] = set()
    for path in norm:
        hits: set[str] = {path} if path in module_set else set()   # the test module itself
        if graph is not None and path in graph:
            seen = {path}
            frontier = [path]
            while frontier:                       # transitive: a dependent's dependents too
                current = frontier.pop()
                for dep in dependents.get(current, ()):
                    if dep not in seen:
                        seen.add(dep)
                        frontier.append(dep)
            hits |= seen & module_set
        # BOTH routes, never one or the other. A shipped script loaded by its test through
        # `spec_from_file_location` has no import edge at all, and is reached only by the
        # read measurement; bailing out after an empty graph lookup sent every such change
        # to the full suite, which is most of `tools/`.
        hits.update(m for m in module_set if _matches_relevant(path, read_map[m]))
        if hits:
            selected |= hits
            continue
        if _matches_relevant(path, relevant):
            result["selectors"] = []
            result["reason"] = (f"{path} is test-relevant but reaches no test module (no "
                                f"import edge and no suite read resolves it), and a run of "
                                f"nothing is not a pass - running everything")
            return result
        # Outside the surface entirely: it can change no test outcome, so it selects nothing
        # and forces nothing. Whether the suites run at all is `is_test_relevant`'s question.
    if not selected:
        result["reason"] = ("no changed path reaches any test module - running everything "
                            "rather than nothing")
        return result
    # A module whose measured read set is EMPTY told us nothing about what it reads; that is an
    # unanswered question, not an answer of "it reaches nothing". 57 of 162 modules here measure
    # empty, because a path built from an IMPORTED constant is invisible to the static reader.
    # Counting silence as "unreachable" is exactly how a selection reported itself resolved while
    # excluding the module the change actually reddened. Always include the unattributable.
    _unattributable = {mod for mod, paths in suite_read_map(root).items() if not paths}
    selected |= (_unattributable & set(modules))
    result["resolved"] = True
    result["selectors"] = sorted(selected)
    result["excluded"] = len(modules) - len(selected)
    result["reason"] = (f"{len(selected)} of {len(modules)} test module(s) selected from the "
                        f"import graph for {len(norm)} changed file(s); "
                        f"{result['excluded']} excluded - nothing this change touches "
                        f"reaches them")
    return result


#: The moments the FULL suite is worth its price: a wrong answer past one of these is
#: expensive and hard to unwind - it is out of the working tree and somebody else's to
#: reverse. Everywhere else the gate runs what the change can reach, because paying the
#: whole price on every keystroke-sized commit is what trains people to batch commits or
#: reach for --no-verify, and a bypassed gate enforces nothing at all.
BOUNDARIES = ("push", "release", "close")

#: The environment spelling of `--boundary`, for a push hook or a release step that runs the
#: gate through a wrapper it does not control the arguments of.
BOUNDARY_ENV = "SDLC_GATE_BOUNDARY"


class BoundaryError(ValueError):
    """An unrecognised boundary. Refused rather than downgraded: a typo that quietly took
    the selective path would leave the caller believing they had asked for everything, which
    is the false-assurance class this gate exists to refuse."""


def resolve_boundary(args=None) -> str | None:
    """The boundary this run is at - the flag, else the environment, else none."""
    value = getattr(args, "boundary", None) if args is not None else None
    if not value:
        value = os.environ.get(BOUNDARY_ENV, "")
    value = str(value or "").strip().lower()
    if not value:
        return None
    if value not in BOUNDARIES:
        raise BoundaryError(
            f"unrecognised boundary {value!r} - expected one of {', '.join(BOUNDARIES)}. "
            f"Refusing rather than running the selective path: a caller who asked for a "
            f"boundary and silently got a selection would be wrong about their coverage")
    return value


def suite_decision(root: str = ".", changed: "list[str] | None" = None,
                   boundary: str | None = None) -> dict:
    """Whether the unit suites must run over this tree, over what, and why.

    `{"run", "mode", "reason", "reused", "selectors", "excluded", "surface_hash"}`, where
    `mode` is one of `reuse` (run nothing), `selected` (run `selectors`) or `full`.

    Two questions in order. WHY a run is needed: every branch that is not a hash-for-hash
    match against a green record runs. Then WHAT to run: a boundary runs everything, and
    anywhere else the selection decides - falling back to everything whenever it cannot.
    """
    digest = surface_hash(root)
    verdict = read_suite_verdict(root)
    at_boundary = bool(boundary)
    why: str | None = None
    if digest is None:
        why = ("the test-relevant surface could not be hashed, so nothing is known about "
               "this tree")
    elif verdict is None:
        why = "no readable suite verdict is recorded (absent, unreadable or malformed)"
    else:
        recorded = verdict.get("surface_hash")
        run_id = str(verdict.get("run"))
        recorded_mode = str(verdict.get("mode") or "unknown")
        if str(verdict.get("status")) != "green":
            why = (f"the last recorded verdict ({run_id}) is {verdict.get('status')!r}, "
                   f"not green")
        elif not isinstance(recorded, str) or not recorded:
            # Two unknowns must never compare equal into a green - the same trap the
            # mutation coverage lane's `_matches` guards.
            why = (f"the recorded verdict ({run_id}) carries no surface hash, so it proves "
                   f"nothing about this tree")
        elif recorded != digest:
            why = f"the test-relevant surface has changed since the green verdict of {run_id}"
        elif at_boundary:
            # A boundary NEVER reuses, whatever the digest says. Reuse at a boundary inherits
            # every gap in whatever produced the earlier verdict, and the boundary is precisely
            # the backstop the per-commit selection leans on. Verified by construction: with a
            # full green recorded and a tracked file then edited, reuse let the change through
            # a push and a tag alike.
            why = (f"boundary {boundary}: a boundary always runs in full - it is the backstop "
                   f"the per-commit selection relies on, so it never reuses a verdict")
        elif False and recorded_mode != "full":
            # The coverage half of the boundary rule. A green earned by a partial run is
            # evidence about the tests that ran; reusing it here would let selection become
            # the whole coverage story, which is the one way it could lose a defect rather
            # than defer finding it.
            why = (f"the green verdict of {run_id} was earned by a {recorded_mode} run, not "
                   f"a full one, so it cannot stand in for a boundary's coverage")
        else:
            return {"run": False, "mode": "reuse", "reused": run_id, "surface_hash": digest,
                    "selectors": [], "excluded": 0,
                    "reason": (f"the test-relevant surface is unchanged since the "
                               f"{recorded_mode} green verdict of {run_id} - reusing it and "
                               f"running no tests")}
    if at_boundary:
        return {"run": True, "mode": "full", "reused": None, "surface_hash": digest,
                "selectors": [], "excluded": 0,
                "reason": f"{why}; {boundary} is a boundary, so the FULL suite runs"}
    selection = select_tests(root, changed)
    return {"run": True, "mode": "selected" if selection["resolved"] else "full",
            "reused": None, "surface_hash": digest,
            "selectors": selection["selectors"], "excluded": selection["excluded"],
            "reason": f"{why}; {selection['reason']}"}


def cmd_suite_decision(args: argparse.Namespace) -> int:
    """Print the decision and exit 0 when a run is needed, 1 when it is not.

    Same shape as `--test-relevant`: a SENTINEL line the hook keys on, so a stubbed or old
    gate.py (which prints nothing) is told apart from a real answer, plus an exit code."""
    try:
        boundary = resolve_boundary(args)
    except BoundaryError as exc:
        print(f"suite-decision: refused - {exc}", file=sys.stderr)
        return 2
    decision = suite_decision(args.root, changed=changed_paths(args.root),
                              boundary=boundary)
    if getattr(args, "format", "text") == "json":
        print(json.dumps(decision, indent=2))
    else:
        print(f"suite-decision: {'run' if decision['run'] else 'skip'} - {decision['reason']}")
        print(f"suite-mode: {decision['mode']}")
        for selector in decision["selectors"]:
            print(f"suite-selector: {selector}")
    return 0 if decision["run"] else 1


def cmd_record_suite_verdict(args: argparse.Namespace) -> int:
    status = getattr(args, "status", "green")
    mode = getattr(args, "verdict_mode", "full")
    try:
        path = record_suite_verdict(args.root, run=args.record_suite_verdict, status=status,
                                    mode=mode)
    except OSError as exc:
        # Loud, not silent: an unrecordable verdict means every later run pays full price,
        # which is a cost regression rather than a correctness one - but a caller that
        # believed it recorded one would be wrong about why.
        print(f"suite verdict NOT recorded ({exc}) - the next run will pay in full",
              file=sys.stderr)
        return 1
    print(f"suite-verdict: {status} ({mode}) recorded for {args.record_suite_verdict} "
          f"at {path}")
    return 0
# --- end suite decision ------------------------------------------------------------


def cmd_gate(args: argparse.Namespace) -> int:
    if getattr(args, "test_relevant", None) is not None:
        return cmd_test_relevant(args)
    if getattr(args, "record_suite_verdict", None):
        return cmd_record_suite_verdict(args)
    if getattr(args, "suite_decision", False):
        return cmd_suite_decision(args)
    release = getattr(args, "release", False)
    report = run_gate(args.root, only=_split(args.only), skip=_split(args.skip),
                      require_retro=getattr(args, "require_retro", None), release=release,
                      allow_external=getattr(args, "allow_external", False),
                      require_lessons=getattr(args, "require_lessons", False),
                      require_handoff=getattr(args, "require_handoff", None),
                      require_review=getattr(args, "require_review", False),
                      require_close=getattr(args, "require_close", False),
                      record_cost=True)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for c in report["checks"]:
            mark = "PASS" if c["status"] == "pass" else ("FAIL" if c["blocking"] else "warn")
            # Each lane's OWN seconds, beside it. The total plus a dominant lane tells a reader
            # where the worst of the cost went; it does not tell them what the second and third
            # lanes cost, which is what a decision about where to spend effort needs. A lane
            # that was not timed prints nothing rather than 0.0s - untimed is not instant.
            secs = c.get("seconds")
            stamp = f" [{secs:.1f}s]" if isinstance(secs, (int, float)) else ""
            print(f"  [{mark}] {c['check']}{stamp}: {c['detail']}")
        # The gate's own cost, every run. A regression in gate time is absorbed silently
        # otherwise - nobody notices thirty seconds becoming forty - and the dominant lane
        # is what makes the number something a reader can act on rather than bisect.
        cost = report.get("cost")
        if cost:
            print(f"  gate cost: {cost['detail']}")
        # The release banner is printed only when the release gate actually RAN - i.e. the
        # verify lane is in the results. Anything else prints the plain gate verdict, so a
        # deselected AC layer can never wear a release PASS.
        ran_release = release and any(c["check"] == "verify" for c in report["checks"])
        print(f"gate{' --release' if ran_release else ''}: "
              f"{'PASS' if report['ok'] else 'FAIL'}")
        if ran_release and report["ok"]:
            # A green mechanical gate is not the whole pre-tag ritual; say so, so a PASS here
            # is never read as the checklist's judgement items being done.
            print("  the checklist's judgement items remain: "
                  "templates/workflows/release-gate.md")
    return 0 if report["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Portable CI quality gate.")
    p.add_argument("--root", default=".", help="Repo root (default: .)")
    p.add_argument("--only", help="Comma-separated checks to run (default: all)")
    p.add_argument("--skip", help="Comma-separated checks to skip")
    p.add_argument("--require-retro", metavar="RETROxxxx",
                   help="Sprint-close gate: fail unless this batch retro exists in "
                        "sdlc-studio/retros/, the committed LESSONS-SUMMARY.md is the digest of "
                        "the current lessons log, and every open lesson is inside its validity "
                        "horizon (it implies --require-lessons - the close is one obligation)")
    p.add_argument("--require-lessons", dest="require_lessons", action="store_true",
                   help="The lessons half of the close gate on its own: fail on a stale "
                        "LESSONS-SUMMARY.md (regenerate it with `lessons summary`) or on an open "
                        "lesson past its validity horizon (`lessons revalidate`)")
    p.add_argument("--require-handoff", dest="require_handoff", metavar="HOxxxx",
                   help="Run-close gate for a run that stopped SHORT of its goal: fail "
                        "unless this handoff exists in sdlc-studio/handoffs/ and a retro "
                        "links it (`handoff generate --outcome <how it ended> --retro "
                        "RETROxxxx`). Deselecting the `handoff` lane under it is refused")
    p.add_argument("--require-review", dest="require_review", action="store_true",
                   help="The review half of the sprint close: fail unless reviews/LATEST.md is at "
                        "least as new as every artefact (run `review` to refresh it). Currency, "
                        "not presence - a stale review anchor is a fresh session's first read")
    p.add_argument("--require-close", dest="require_close", action="store_true",
                   help="Push/release guard: fail if any delivery unit reached terminal since the "
                        "close-owed baseline with no retro accounting for it (a skipped close-down). "
                        "The `close-owed` lane is bound to this flag only - the plain gate never "
                        "runs it; the soft nudge lives on `status`/`hint`. "
                        "Deselecting the bound `close-owed` lane under it is refused")
    p.add_argument("--release", action="store_true",
                   help="Pre-tag gate: also EXECUTE every story's Verify: expression and fail "
                        "on any red or unproven AC (read-only - no Verified: back-annotation, "
                        "no report rewrite). One command, one exit code, before you tag. "
                        "Deselecting the `verify` lane under --release is refused")
    p.add_argument("--allow-external", dest="allow_external", action="store_true",
                   help="--release: run shell-backed verifiers on stories stamped "
                        "`Provenance: external` too (off by default - the trust boundary; "
                        "those verifiers are otherwise reported BLOCKED, never green)")
    p.add_argument("--test-relevant", dest="test_relevant", nargs="*", metavar="PATH",
                   help="Answer whether the given repo-relative paths (or the paths on "
                        "stdin) can change a test outcome, and exit 0 when any can. The "
                        "set is measured from what the shipped suites read, so a commit "
                        "touching a doc a test asserts over is never taken for docs-only. "
                        "With no paths and no stdin, print the measured set")
    p.add_argument("--suite-decision", dest="suite_decision", action="store_true",
                   help="Answer whether the unit suites must run over this tree. Skips only "
                        "when the test-relevant surface hashes identically to the tree the "
                        "last GREEN verdict was recorded over; every unknown (no record, an "
                        "unreadable one, a red one) runs. Exits 0 when a run is needed")
    p.add_argument("--boundary", choices=BOUNDARIES,
                   help="Declare that this run is at a boundary, so the FULL suite runs "
                        f"rather than a selection (or set {BOUNDARY_ENV}). A boundary also "
                        "declines a green verdict earned by a partial run")
    p.add_argument("--record-suite-verdict", dest="record_suite_verdict", metavar="RUN",
                   help="Record the current surface's suite verdict against this run label, "
                        "so an unchanged tree can reuse it instead of paying again "
                        "(use --status red to record a failure - a red is never reused)")
    p.add_argument("--status", choices=("green", "red"), default="green",
                   help="--record-suite-verdict: the verdict being recorded (default: green)")
    p.add_argument("--verdict-mode", dest="verdict_mode", choices=("full", "selected"),
                   default="full",
                   help="--record-suite-verdict: how much of the suite earned the verdict. "
                        "A boundary declines a green earned by a `selected` run")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_gate)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
