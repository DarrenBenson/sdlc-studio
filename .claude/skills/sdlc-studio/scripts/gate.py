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
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402


def _conformance(root: str) -> dict:
    import conformance
    result = conformance.detect_conformance(root)
    # A repo-global failure (one uncatalogued command, a missing index) is attributed ONCE
    # rather than charged to every judged unit - but it must still block, or improving the
    # report would quietly weaken the gate. Count it as its own finding.
    n = result["summary"]["nonconformant"] + result["summary"].get("global_failures", 0)
    # Name the remedies inline (the adopt_after cutoff + the verify_ac backfill) and flag
    # whether the shape reads as pre-existing forward-only debt vs a fresh regression, so a
    # grown-but-accepted count does not read as a new breakage.
    return {"count": n, "blocking": True, "detail": conformance.remedy_detail(result)}


def _reconcile(root: str) -> dict:
    import reconcile
    rr = Path(root).resolve()
    # detect_type returns a dict; the drift items live under "drift" (not len(dict)).
    total = sum(len(reconcile.detect_type(t, rr)["drift"]) for t in reconcile.DEFAULT_TYPES)
    # `request-derivable` is assembled in the sweep, not in `detect_type`, so it was invisible
    # here - the gate passed on a tree where `reconcile detect` exited 1.
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
    blocked = 0
    if sdlc_md.two_backlog_enforced(rr):
        derivable = reconcile.derivable_request_drift(rr)
        blocked = sum(1 for d in derivable if d.get("blocked_by"))
        total += len(derivable) - blocked
    detail = f"{total} drift item(s)"
    if blocked:
        detail += f" (+{blocked} awaiting another gate, not blocking)"
    return {"count": total, "blocking": True, "detail": detail}


def _index_derived(root: str) -> dict:
    import reconcile
    issues = reconcile.index_derived_issues(Path(root).resolve())
    return {"count": len(issues), "blocking": True,
            "detail": "; ".join(issues) if issues else "indexes are derived output"}


def _validate(root: str) -> dict:
    import validate
    rr = Path(root).resolve()
    errors = 0
    for type_ in sdlc_md.ARTIFACT_TYPES:
        for path in sdlc_md.artifact_files(type_, rr):
            errors += sum(1 for v in validate.validate_file(path, type_, rr)
                          if v["severity"] == "error")
    return {"count": errors, "blocking": True, "detail": f"{errors} validation error(s)"}


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
    r = provenance.check(root)  # blocking only when provenance.enforce (the constitution pattern)
    n = len(r["findings"])
    return {"count": n, "blocking": r["enforced"],
            "detail": f"{n} unstamped artifact(s) ({'enforced' if r['enforced'] else 'advisory'})"}


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


def _mutation_changed_surface(root: str) -> list[str] | None:
    """Repo-relative mutatable, non-test files with uncommitted changes - staged, unstaged or
    untracked. That is the surface a pre-commit gate is actually about, and it needs no sprint
    run and no sdlc-studio state, so the lane works in a consuming project too.

    Returns None when git cannot answer: no git, no commit to diff against, or a `root` that
    is not the repository top level (git would then report paths relative to some other root).
    The caller degrades to the ledger's own contents rather than inventing a surface.
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
    except Exception:  # noqa: BLE001 - a surface probe must never break the gate
        return None
    out: list[str] = []
    for raw in names:
        name = raw.strip()
        if not name or Path(name).suffix not in _MUTATABLE_SUFFIXES or _is_test_path(name):
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
                        # what the entry proves ABOUT THE TESTS. `equivalent` is excluded on
                        # purpose - see `_covering` below.
                        "covering": _n("killed") + _n("survived"),
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
    lines, claimed_any = [], False
    for win in held:
        raw = win.get("paths")
        if isinstance(raw, str):
            raw = [raw]
        if not isinstance(raw, list):
            raw = []          # `paths` that is not a list names nothing this can match
        # str() for DISPLAY only, never for matching: str()-ing a claim into a pattern is how
        # an uninterpretable one came to match nothing and wave the commit through.
        paths = ", ".join(str(x) for x in raw) or "(unstated paths)"
        if staged is None:
            hit = ["(the staged file list could not be read, so every path is treated "
                   "as claimed)"]
        else:
            claims = raw or [_WINDOW_EVERYTHING]
            hit = [s for s in staged if any(_window_claims(c, s) for c in claims)]
        note = (f"{win['owner']} has claimed {paths} since {win.get('opened_at')}")
        if win.get("unreadable"):
            note += f" ({win['detail']})"
        if not hit:
            lines.append(f"a rewrite window is OPEN - {note}; no staged path is claimed by it, "
                         f"so this gate does not refuse. Stage named paths, never `git add -A`")
            continue
        claimed_any = True
        lines.append(f"a rewrite window is OPEN and claims a STAGED path - {note}; staged: "
                     f"{', '.join(hit)}. A commit now stages whatever that process has left on "
                     f"disk. Wait for it, or clear it: {win['clear_with']}")
    return {"count": 1 if claimed_any else 0, "blocking": True, "detail": "; ".join(lines)}


#: A window that names no paths has not said it may rewrite nothing.
_WINDOW_EVERYTHING = "*"


def _window_claims(pattern, staged: str) -> bool:
    """True when `pattern` covers the staged path. Kept identical in rule to the pre-commit
    hook's own matcher, and pinned against it by test: a claim this cannot INTERPRET (anything
    that is not a string, or an absolute path outside this root) claims EVERYTHING, because the
    record says a writer is active and a matcher that shrugged would report it as harmless."""
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
}

def _changelog_fragments(root: str) -> dict:
    """Release-bound lane: a stray (uncomposed) changelog fragment fails the cut -
    an entry silently missing from a release is the LL0004 hole fragments exist to
    close. Runs only under --release; the standard gate never nags about fragments
    (they are the normal between-releases state)."""
    import changelog
    strays = changelog.check(root)
    detail = ("no stray fragments" if not strays else
              f"{len(strays)} uncomposed fragment(s): "
              + ", ".join(p.name for p in strays)
              + " - run changelog.py compose before tagging")
    return {"count": len(strays), "blocking": True, "detail": detail}


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


DEFAULT_CHECKS = {
    "conformance": _conformance,
    "reconcile": _reconcile,
    "index-derived": _index_derived,
    "validate": _validate,
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
                           f"{len(res['declined'])} declined)")}
    # Every error names its own remedy; surface them all rather than only the first, so one
    # close tells you everything it wants instead of a queue of one-at-a-time refusals.
    suffix = "" if blocking else " (advisory: lessons.loop is judgement)"
    return {"count": len(res["errors"]), "blocking": blocking,
            "detail": f"batch retro {retro_id} incomplete{suffix} - " + "; ".join(res["errors"])}


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
        if m and latest_dt and m > latest_dt:
            stale.append(key)
    if stale:
        return {"count": len(stale), "blocking": True,
                "detail": (f"reviews/LATEST.md is stale - {len(stale)} artefact(s) changed since "
                           f"the last review ({_elide(sorted(stale))}); run `review` before closing")}
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
    jest_cache = verify_ac.jest_batch_cache(rr, timeout) if batch else None
    red: list[str] = []
    blocked: list[str] = []
    unspecified: list[str] = []
    acs = manual = unspec = 0
    for path in stories:
        report = verify_ac.verify_story(path, dry_run=True, timeout=timeout, repo_root=rr,
                                        jest_cache=jest_cache, allow_external=allow_external)
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
                "detail": "; ".join(parts)}
    if acs == 0:
        return {"count": 1, "blocking": True,
                "detail": f"no acceptance criteria across {len(stories)} story/stories - the "
                          f"verify lane proved nothing about the AC layer (wrong --root?)"}
    return {"count": 0, "blocking": True,
            "detail": f"{executable}/{acs} executable AC(s) green across "
                      f"{len(stories)} story/stories ({manual} manual)"}


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


def run_gate(root: str = ".", only: list[str] | None = None,
             skip: list[str] | None = None, checks: dict | None = None,
             require_retro: str | None = None, release: bool = False,
             allow_external: bool = False, verify_batch: bool = False,
             require_lessons: bool = False, require_handoff: str | None = None,
             require_review: bool = False, require_close: bool = False) -> dict:
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
    if require_close:  # push/release guard: no delivery unit may owe a close (bound, blocking)
        registry["close-owed"] = _close_owed
        bound.append("close-owed")
    if release:  # pre-tag: the executing AC-verify lane joins the standard gate...
        registry["verify"] = (lambda r, _x=allow_external, _b=verify_batch:
                              _verify_acs(r, allow_external=_x, batch=_b))
        bound.append("verify")
        # ...and every required document leg must be present or explicitly waived: a tag over a
        # silently-missing required artefact is the BG0110 hole this refuses to leave open.
        registry["review-legs"] = _review_legs
        bound.append("review-legs")
        # ...and the version strings must agree across their authoritative homes, CHANGELOG
        # included: a tag cut over a drifted version is a release nobody can identify later.
        registry["versions"] = _versions_strict
        bound.append("versions")
        # ...and no changelog fragment may be left uncomposed at a cut
        if _dod_enforced(release_dod, "release.changelog"):
            registry["changelog-fragments"] = _changelog_fragments
            bound.append("changelog-fragments")
        else:
            downgraded.append("release.changelog")
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
    for name in selected:
        try:
            r = registry[name](root)
            results.append({"check": name, "count": r["count"], "blocking": r["blocking"],
                            "status": "pass" if r["count"] == 0 else "fail",
                            "detail": r.get("detail", "")})
        except Exception as exc:  # noqa: BLE001 - one buggy check must not abort the whole gate
            # A conventions shape error is the operator's config, not a buggy
            # check: it silently disables whichever lane read it (reconcile's
            # drift detection, most damagingly), so it must BLOCK - a green
            # gate over a disabled lane is the false assurance class.
            from lib.conventions import ConventionsError
            blocking = isinstance(exc, ConventionsError) or name in BLOCKING_ON_ERROR
            results.append({"check": name, "count": 1, "blocking": blocking, "status": "error",
                            "detail": f"check raised{'' if blocking else ', skipped'}: {exc}"})
    if downgraded:  # the document's downgrades, visible in the verdict - never silent
        results.append({"check": "dod-downgrades", "count": len(downgraded),
                        "blocking": False, "status": "warn",
                        "detail": f"downgraded to human-judged by definition-of-done.md "
                                  f"(tag removed): {', '.join(sorted(downgraded))}"})
    ok = all(r["status"] == "pass" for r in results if r["blocking"])
    return {"ok": ok, "checks": results}


def _split(v: str | None) -> list[str] | None:
    return [x.strip() for x in v.split(",") if x.strip()] if v else None


def cmd_gate(args: argparse.Namespace) -> int:
    release = getattr(args, "release", False)
    report = run_gate(args.root, only=_split(args.only), skip=_split(args.skip),
                      require_retro=getattr(args, "require_retro", None), release=release,
                      allow_external=getattr(args, "allow_external", False),
                      verify_batch=getattr(args, "verify_batch", False),
                      require_lessons=getattr(args, "require_lessons", False),
                      require_handoff=getattr(args, "require_handoff", None),
                      require_review=getattr(args, "require_review", False),
                      require_close=getattr(args, "require_close", False))
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        for c in report["checks"]:
            mark = "PASS" if c["status"] == "pass" else ("FAIL" if c["blocking"] else "warn")
            print(f"  [{mark}] {c['check']}: {c['detail']}")
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
    p.add_argument("--verify-batch", dest="verify_batch", action="store_true",
                   help="--release: run jest once and resolve jest verifiers from the cached "
                        "result, instead of a cold start per AC")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_gate)
    return p


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
