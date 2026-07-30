#!/usr/bin/env python3
"""Where the test suite's cost goes, and which tests still earn it.

This repository carries thousands of tests against a few dozen source modules, and the
full suite runs on every commit. Every test added is therefore a tax paid on every
future change, and nothing has ever asked whether a given test still repays it. Two
questions have to be answerable before anything can be pruned:

1. **Cost.** Which module does a test cover, how many tests cover it, and what do they
   cost? A number nobody can attribute is a number nobody acts on (US0506).
2. **Value.** Does the test discriminate? A test that no mutation of its own module can
   kill protects nothing measurable, whatever its coverage percentage says (US0507).

The dangerous answer in both halves is a confident wrong one, so the refusals are the
design:

- A test the census cannot attribute is NAMED in an `unattributed` list and counted in
  the totals. Dropping it would shrink the reported suite below the suite that ran, and
  a total that quietly excludes its awkward cases is worse than no total.
- A test is nominated for removal only against evidence that could have convicted it:
  the module must have at least one mutant something killed, and the run must say which
  tests it ran. Otherwise "killed nothing" is indistinguishable from "never ran", and
  acting on it deletes live tests.
- Evidence that could reach no verdict at all is refused with exit 1, never answered with
  "no removal candidates". A `mutation.py` report runs the whole command per mutant, so
  it knows a mutant died and not by whose hand; read as "no test killed it", it nominates
  every test of the module.
- Recording a removal demands what the test asserted AND why that is safe now. A refusal
  writes no file at all, because a half-written record is what makes pruning quietly
  become coverage loss.

Attribution is by convention, in two passes, and it says which pass placed each module
so a reader can disagree with it:

- `name`: `<dir>/tests/test_foo.py` covers `<dir>/foo.py` (or `foo.sh`; hyphens and
  underscores are folded, because `test_lint_style.py` covers `lint-style.sh`).
- `reference`: no matching name, but the test text mentions exactly one sibling module
  more often than any other. `test_two_backlogs.py` is not named after anything.

Anything else is unattributed. A tie between two modules is a guess, and a guess in a
cost report is how an area gets pruned on another area's evidence.

Subcommands:
  report          per-module test count and seconds, dearest first, plus the unattributed
  candidates      tests no mutation of their own module killed, from mutation evidence
  record-removal  append the justification for removing a test to the tracked ledger
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

#: Directories that hold no tests this repo runs, or holds copies of ones it does. A
#: fixture suite under bench/ is a payload, not part of the gate's cost.
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache", "worktrees"}

#: Extensions a test file may cover. Shell is here because several guards are shell and
#: their tests are the expensive ones.
MODULE_SUFFIXES = (".py", ".sh")

#: Where a removal justification is kept. Under retros/evidence/ because that tree is
#: COMMITTED: a record living in .local/ is not a record, it is a note on one machine.
REMOVALS_REL = "sdlc-studio/retros/evidence/test-removals.jsonl"


def removal_record_path(root: Path | str) -> Path:
    """The tracked ledger of removed tests."""
    return Path(root) / REMOVALS_REL


def _norm(stem: str) -> str:
    """Fold the two ways this repo spells the same name (`lint-style` / `lint_style`)."""
    return stem.replace("-", "_").lower()


def _skipped(rel: Path) -> bool:
    """True for a path INSIDE the census root that lies under a skipped directory.

    Takes the path RELATIVE to the root, never the absolute one. The skip list names
    directories the census should not descend into; matched against the absolute path, a name
    that merely appears somewhere ABOVE the root skipped every file beneath it. This repo runs
    its reviewers and parallel delivery agents in `.claude/worktrees/`, so the census counted
    zero files there and the lane reported an all-clear over nothing - inert in exactly the
    environment it is relied on. The same shape was waiting for any root under a path
    containing `node_modules` or `.git`.
    """
    return any(part in SKIP_DIRS for part in rel.parts)


def test_files(root: Path | str) -> list[Path]:
    """Every `test_*.py` under `root`, as paths relative to it."""
    base = Path(root)
    return sorted(rel for rel in (p.relative_to(base) for p in base.rglob("test_*.py"))
                  if not _skipped(rel))


def dotted(rel: Path | str) -> str:
    """The dotted form pytest puts in a JUnit `classname` for this file.

    pytest emits no `file` attribute, only a dotted path in which the directory
    separators and the module boundary are indistinguishable. Rather than guess at the
    boundary, every test file on disk is converted here once and the classname is matched
    against that set - the same trick verify_ac.py uses, for the same reason.
    """
    return str(rel).removesuffix(".py").replace("/", ".")


def _module_dir(rel: Path) -> Path:
    """The directory whose modules a test file is presumed to cover."""
    return rel.parent.parent if rel.parent.name == "tests" else rel.parent


def _sibling_modules(root: Path, rel: Path) -> list[Path]:
    """Candidate source modules for `rel`, relative to `root`.

    Only the test file itself is excluded, never every `test_*.py` name. This repo has
    real modules called `test_noise.py` and `test_census.py`, so a rule that skipped the
    prefix would leave the cost of the suite's own guards permanently unattributable -
    the census would be blind to itself first.
    """
    d = root / _module_dir(rel)
    if not d.is_dir():
        return []
    return sorted(
        p.relative_to(root) for p in d.iterdir()
        if p.is_file() and p.suffix in MODULE_SUFFIXES
        and p.relative_to(root) != rel and p.name not in ("__init__.py", "conftest.py"))


def attribute(root: Path | str, rel: Path | str) -> tuple[str | None, str]:
    """Which module does test file `rel` cover, and which pass decided?

    Returns `(module_or_None, how)`. When nothing is placed, `how` is the reason, phrased
    for a reader who has to judge whether the census is being fair to that file.
    """
    base, rel = Path(root), Path(rel)
    mods = _sibling_modules(base, rel)
    if not mods:
        return None, f"no source module sits beside {rel.as_posix()} to attribute it to"
    stem = _norm(rel.stem.removeprefix("test_"))
    by_name = [m for m in mods if _norm(m.stem) == stem]
    if by_name:
        return by_name[0].as_posix(), "name"
    text = ""
    try:
        text = (base / rel).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, f"{rel.as_posix()} could not be read, so it cannot be attributed"
    counts = {}
    for m in mods:
        hits = len(re.findall(r"\b" + re.escape(m.stem) + r"\b", text))
        if hits:
            counts[m.as_posix()] = hits
    if not counts:
        return None, (f"{rel.as_posix()} matches no module by name and references none of "
                      f"the {len(mods)} modules beside it")
    best = max(counts.values())
    tops = sorted(m for m, c in counts.items() if c == best)
    if len(tops) > 1:
        return None, (f"{rel.as_posix()} references " + " and ".join(tops)
                      + " equally, so attributing it would be a guess")
    return tops[0], "reference"


def parse_junit(text: str) -> list[dict]:
    """Flatten a pytest JUnit report into `{classname, name, seconds}` rows.

    A report that will not parse raises. This is a measurement tool, and an unreadable
    input has to stop it rather than produce a report over zero tests that reads exactly
    like a suite that got much cheaper.
    """
    root = ET.fromstring(text)  # nosec B314 - our own pytest output, not external input
    out = []
    for case in root.iter("testcase"):
        cname, name = case.get("classname") or "", case.get("name") or ""
        if not name:
            continue
        try:
            seconds = float(case.get("time") or 0.0)
        except ValueError:
            seconds = 0.0
        out.append({"classname": cname, "name": name, "seconds": seconds})
    return out


def _node_id(rel: Path, classname: str, name: str) -> str:
    """`path::Class::test`, or `path::test` for a module-level test function."""
    tail = classname[len(dotted(rel)):].lstrip(".")
    return f"{rel.as_posix()}::{tail}::{name}" if tail else f"{rel.as_posix()}::{name}"


def census(junit_text: str | list[str], root: Path | str) -> dict:
    """Attribute a completed run's tests and seconds to the module each test covers.

    Every case in the report lands somewhere: in a module row, or in `unattributed` with
    its node id and the reason. `totals` counts both, so the report's arithmetic can be
    checked against the run it came from.

    A list of reports is read as ONE run. This repo's gate is two pytest invocations
    because its two test directories are both packages named `tests` and cannot be
    collected together, so a census that took a single report could only ever cost half
    the suite while presenting itself as the suite.
    """
    base = Path(root)
    by_dotted = {dotted(p): p for p in test_files(base)}
    resolved: dict[str, tuple[str | None, str]] = {}
    modules: dict[str, dict] = {}
    unattributed: list[dict] = []
    total_seconds = 0.0
    texts = [junit_text] if isinstance(junit_text, str) else list(junit_text)
    cases = [c for text in texts for c in parse_junit(text)]
    for case in cases:
        cname, name, seconds = case["classname"], case["name"], case["seconds"]
        total_seconds += seconds
        rel = by_dotted.get(cname)
        if rel is None:
            # A class-based test: strip the class segment and try the module again.
            head = cname.rsplit(".", 1)[0] if "." in cname else ""
            rel = by_dotted.get(head)
        if rel is None:
            unattributed.append({
                "test": f"{cname}::{name}" if cname else name,
                "seconds": round(seconds, 3),
                "reason": f"classname {cname!r} matches no test file under {base}"})
            continue
        key = rel.as_posix()
        if key not in resolved:
            resolved[key] = attribute(base, rel)
        module, how = resolved[key]
        node = _node_id(rel, cname, name)
        if module is None:
            unattributed.append({"test": node, "seconds": round(seconds, 3), "reason": how})
            continue
        row = modules.setdefault(module, {"module": module, "tests": 0, "seconds": 0.0,
                                          "how": how, "test_files": [], "test_ids": []})
        row["tests"] += 1
        row["seconds"] += seconds
        row["test_ids"].append(node)
        if key not in row["test_files"]:
            row["test_files"].append(key)
    rows = sorted(modules.values(), key=lambda r: (-r["seconds"], r["module"]))
    for row in rows:
        row["seconds"] = round(row["seconds"], 3)
    return {
        "modules": rows,
        "unattributed": unattributed,
        "totals": {
            "tests": len(cases),
            "seconds": round(total_seconds, 3),
            "attributed": sum(r["tests"] for r in rows),
            "unattributed": len(unattributed),
            "modules": len(rows),
        },
    }


#: The two spellings of the mutant list. `mutants` is this tool's own input shape;
#: `mutations` is what scripts/mutation.py writes, so its report can be handed straight
#: over on the day it records what killed each mutant.
MUTANT_KEYS = ("mutants", "mutations")

#: How many mutants a refusal names before it starts counting instead.
NAMED_IN_REFUSAL = 5


def mutant_id(m: dict) -> str:
    """Name a mutant by its id, or by where it sits when the producer gave it none."""
    given = str(m.get("id") or "").strip()
    if given:
        return given
    return ":".join(str(p) for p in (Path(m["file"]).as_posix(),
                                     m.get("line", "?"), m.get("class", "?")))


def mutant_rows(evidence: dict) -> list[dict]:
    """The mutants in `evidence`, or a `ValueError` saying why it can judge nobody.

    Three shapes cannot convict anything, and all three used to read as a clean sweep:

    - no mutant list under either key. The file is not mutation evidence at all;
    - a mutant list that is empty. This repo's own report looks exactly like this after a
      refused run, and "no candidates" from it means "no run", not "every test earns its
      place";
    - killed mutants that do not record what killed them. `mutation.py` runs the whole
      test command per mutant, so its report knows a mutant died and not by whose hand.
      Reading that as "no test killed it" nominates every test of the module for deletion.

    Each is raised rather than returned, because the caller's only honest move is to stop.
    """
    present = [k for k in MUTANT_KEYS if k in evidence]
    if not present:
        raise ValueError(
            "this evidence has no mutant list under 'mutants' or 'mutations', so it is "
            "not a mutation run and can judge no test")
    rows = [m for key in present for m in (evidence.get(key) or [])
            if isinstance(m, dict) and m.get("file")]
    if not rows:
        raise ValueError(
            f"this evidence records no mutant against a file under {' or '.join(present)}, "
            "so nothing was mutated and no test can be judged by it")
    blind = [mutant_id(m) for m in rows
             if m.get("verdict") == "killed" and not (m.get("killed_by") or [])]
    if blind:
        named = ", ".join(sorted(blind)[:NAMED_IN_REFUSAL])
        more = len(blind) - NAMED_IN_REFUSAL
        raise ValueError(
            f"{len(blind)} killed mutant(s) carry no killed_by, so this evidence says a "
            f"mutant died but not what killed it: {named}"
            + (f" and {more} more" if more > 0 else "")
            + ". Reading that as 'no test killed it' would nominate every test of the "
              "module; re-run the mutation with per-test attribution instead")
    return rows


def prune_candidates(report: dict, evidence: dict) -> dict:
    """Tests that killed no mutant of the module they cover, from mutation evidence.

    `evidence` is `{"tests_run": [node_id, ...], "mutants": [{"id", "file", "verdict",
    "killed_by": [node_id, ...]}]}`; `mutations` is accepted for the same list, so a
    `mutation.py` report can be handed over unedited. Evidence that can judge nobody at
    all raises `ValueError` from `mutant_rows` rather than returning an empty verdict.

    Two facts have to hold before any test of a module is judged, and both are absences
    that a naive implementation reads as a clean sweep:

    - the run must say which tests it RAN. Without that list, a test that killed nothing
      is indistinguishable from one the mutation command never selected, and nominating
      the second for deletion removes a live test on no evidence at all;
    - the module must have at least one mutant something killed. If every mutant survived,
      the run discriminated nothing there, so it convicts nobody - it indicts itself.

    Where neither holds the module is reported `inconclusive` with the reason, never as
    zero candidates. Zero candidates and no evidence look identical to a caller.
    """
    mutants = mutant_rows(evidence)
    by_module: dict[str, list[dict]] = {}
    for m in mutants:
        by_module.setdefault(Path(m["file"]).as_posix(), []).append(m)
    tests_run = evidence.get("tests_run")
    module_tests = {r["module"]: list(r.get("test_ids") or []) for r in report["modules"]}

    candidates: list[dict] = []
    inconclusive: list[dict] = []
    unjudged: list[dict] = []
    judged = 0
    for module in sorted(by_module):
        entries = by_module[module]
        if tests_run is None:
            inconclusive.append({"module": module, "why": (
                "the evidence does not say which tests ran, so a test that killed nothing "
                "cannot be told apart from one that never ran")})
            continue
        killed = [m for m in entries if m.get("verdict") == "killed"]
        if not killed:
            inconclusive.append({"module": module, "why": (
                f"no mutant of {module} was killed by anything in this run, so it "
                "discriminated nothing here and can convict no test")})
            continue
        ran = set(tests_run)
        for test in module_tests.get(module, []):
            if test not in ran:
                unjudged.append({"test": test, "module": module,
                                 "why": "the mutation run did not select this test"})
                continue
            judged += 1
            uncaught = sorted(mutant_id(m) for m in killed
                              if test not in (m.get("killed_by") or []))
            if len(uncaught) == len(killed):
                candidates.append({"test": test, "module": module, "uncaught": uncaught,
                                   "killed_mutants": len(killed)})
    # `judged` is the count the CALLER must act on. Without it, "no candidates" and "this
    # evidence judged nobody" are the same empty list, and the second was being reported as
    # a clean sweep - found by running the command, not by reading it.
    return {"candidates": candidates, "inconclusive": inconclusive, "unjudged": unjudged,
            "judged": judged}


#: Every removal record must state what the test asserted, and one of these must say why
#: losing that assertion is safe. Two fields rather than one: "covered elsewhere" and "no
#: longer true" are different claims, and a reader auditing the prune later needs to know
#: which was made.
JUSTIFICATIONS = ("superseded_by", "no_longer_true")


def record_removal(root: Path | str, removal: dict) -> Path:
    """Append one removal to the tracked ledger. Refuses an unjustified one.

    Raises `ValueError` naming the missing fields, having written nothing. Removing a
    test is a coverage decision, and a decision with no stated reason is indistinguishable
    from an accident six months later.
    """
    missing = [f for f in ("test", "module", "asserted")
               if not str(removal.get(f) or "").strip()]
    if not any(str(removal.get(f) or "").strip() for f in JUSTIFICATIONS):
        missing.append(" or ".join(JUSTIFICATIONS))
    if missing:
        raise ValueError(
            "a removal record needs " + ", ".join(missing) + ": state what the test "
            "asserted and why that is now covered elsewhere or no longer true, or the "
            "prune is coverage loss nobody can review")
    row = {k: removal.get(k) for k in
           ("test", "module", "asserted", "superseded_by", "no_longer_true", "evidence")
           if removal.get(k)}
    row["recorded_at"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    path = removal_record_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    return path


def format_report(report: dict, limit: int = 20) -> str:
    """The census as text: dearest modules first, then the tests nothing claimed."""
    t = report["totals"]
    lines = [f"{t['tests']} tests, {t['seconds']:.1f}s, {t['modules']} modules "
             f"({t['attributed']} attributed, {t['unattributed']} unattributed)", ""]
    lines.append(f"{'seconds':>9}  {'tests':>6}  {'how':<9}  module")
    for row in report["modules"][:limit]:
        lines.append(f"{row['seconds']:>9.2f}  {row['tests']:>6}  {row['how']:<9}  "
                     f"{row['module']}")
    if len(report["modules"]) > limit:
        lines.append(f"{'':>9}  {'':>6}  {'':<9}  ... and "
                     f"{len(report['modules']) - limit} more")
    if report["unattributed"]:
        # Named, never a bare count: an unattributed total is a number to ignore, whereas
        # a named test is either a gap in the convention or a test covering nothing.
        # Grouped by file here because the reason is per file and repeating it per node
        # buries the report; every node id is still named individually in --json.
        lines += ["", f"unattributed ({len(report['unattributed'])} tests):"]
        for group in unattributed_by_file(report)[:limit]:
            lines.append(f"  {group['file']}  ({group['tests']} tests, "
                         f"{group['seconds']:.2f}s) - {group['reason']}")
            lines.append(f"      e.g. {group['example']}")
        extra = len(unattributed_by_file(report)) - limit
        if extra > 0:
            lines.append(f"  ... and {extra} more file(s)")
    return "\n".join(lines)


def unattributed_by_file(report: dict) -> list[dict]:
    """The unattributed tests grouped by the file they came from, dearest first."""
    groups: dict[str, dict] = {}
    for u in report["unattributed"]:
        key = u["test"].split("::", 1)[0]
        g = groups.setdefault(key, {"file": key, "tests": 0, "seconds": 0.0,
                                    "reason": u["reason"], "example": u["test"]})
        g["tests"] += 1
        g["seconds"] += u["seconds"]
    return sorted(groups.values(), key=lambda g: (-g["seconds"], g["file"]))


def _junit_texts(paths: list[str]) -> list[str]:
    """Read every JUnit report the gate produced for one run."""
    return [Path(p).read_text(encoding="utf-8") for p in paths]


def cmd_report(args: argparse.Namespace) -> int:
    report = census(_junit_texts(args.junit), Path(args.root))
    print(json.dumps(report, indent=2) if args.json else format_report(report))
    return 0


def cmd_candidates(args: argparse.Namespace) -> int:
    """Report removal candidates.

    Exit 0 whatever the verdict, because this nominates and never prunes. Exit 1 when the
    evidence could reach no verdict at all: printing "no removal candidates" over a file
    that judged nobody is the false green this tool exists to refuse, and the caller has
    to be able to tell the two apart without reading the prose.
    """
    report = census(_junit_texts(args.junit), Path(args.root))
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    try:
        out = prune_candidates(report, evidence)
    except ValueError as exc:
        print(f"test-census: {args.evidence} cannot nominate anything - {exc}",
              file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    for c in out["candidates"]:
        print(f"candidate: {c['test']}\n  killed none of the {c['killed_mutants']} killed "
              f"mutant(s) of {c['module']}: {', '.join(c['uncaught'])}")
    for i in out["inconclusive"]:
        print(f"inconclusive: {i['module']} - {i['why']}")
    for u in out["unjudged"]:
        print(f"unjudged: {u['test']} - {u['why']}")
    if not out["candidates"]:
        # Only claim a sweep over tests that were actually judged. An empty candidate list
        # over zero judged tests says nothing about the suite, and saying otherwise is the
        # false green this whole tool exists to refuse.
        print(f"no removal candidates: every judged test killed a mutant of its own module "
              f"({out['judged']} judged)" if out["judged"]
              else "no removal candidates because nothing was judged: this evidence matched "
                   "no test in the run - check the node ids agree with the suite")
    return 0


def cmd_record_removal(args: argparse.Namespace) -> int:
    """Record one removal, or refuse it. Exit 1 on a refusal, with nothing written."""
    try:
        path = record_removal(Path(args.root), {
            "test": args.test, "module": args.module, "asserted": args.asserted,
            "superseded_by": args.superseded_by, "no_longer_true": args.no_longer_true,
            "evidence": args.evidence})
    except ValueError as exc:
        print(f"test-census: refusing to record this removal - {exc}", file=sys.stderr)
        return 1
    print(f"test-census: recorded the removal of {args.test} in {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".", help="repo root (default: .)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("report", help="per-module test count and seconds, dearest first")
    r.add_argument("--junit", required=True, action="append",
                   help="a pytest --junit-xml report; repeat once per gate invocation")
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_report)

    c = sub.add_parser("candidates", help="tests no mutation of their own module killed")
    c.add_argument("--junit", required=True, action="append")
    c.add_argument("--evidence", required=True,
                   help="mutation evidence: tests_run plus per-mutant killed_by")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_candidates)

    m = sub.add_parser("record-removal", help="record what a removed test no longer protects")
    m.add_argument("--test", required=True, help="the node id being removed")
    m.add_argument("--module", required=True)
    m.add_argument("--asserted", help="what the test asserted")
    m.add_argument("--superseded-by", help="the test that covers it now")
    m.add_argument("--no-longer-true", help="why the assertion no longer holds")
    m.add_argument("--evidence", help="the mutation run that nominated it")
    m.set_defaults(func=cmd_record_removal)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
