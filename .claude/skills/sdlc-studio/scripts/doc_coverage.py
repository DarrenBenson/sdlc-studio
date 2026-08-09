#!/usr/bin/env python3
"""Deterministic documentation-coverage check.

The `documented` half of the sprint Definition of Done. Enforces the discoverability
floor so docs cannot drift (the gap the self-audit found - pvd/gate/skill-update shipped
without a help-catalogue entry):
  - every command in SKILL.md's Type Reference has a help/help.md catalogue entry  (HARD)
  - every scripts/*.py (non-test, non-lib) has a reference-scripts.md entry          (HARD)
  - CHANGELOG [Unreleased] is non-empty when there is undocumented release work      (soft warn)

Skill-development check: it inspects the SKILL itself, so for a CONSUMING project (no
SKILL.md under the root) it is a no-op (ok, N/A). Wired into the gate (blocking) and the
conformance `documented` stage. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

_SKILL_REL = Path(".claude") / "skills" / "sdlc-studio"
_NON_SCRIPTS = {"__init__"}


def _skill_dir(repo_root: Path) -> Path | None:
    d = Path(repo_root) / _SKILL_REL
    return d if (d / "SKILL.md").exists() else None


def is_skill_repo(repo_root: Path | str = ".") -> bool:
    """Whether `repo_root` is the skill's OWN repository, and so whether a lane that measures the
    skill's documentation has anything to measure at all.

    THE ONE READER of that question. Every lane and report row that measures the skill's own
    corpus asks it here, because the alternative is each deciding for itself and the answers
    drifting: one lane reported `N/A (not the skill repo)` on a consuming project while its
    neighbour raised `ModuleNotFoundError` on the same tree in the same run, and the second
    reported a permanent non-zero advisory naming an internal Python module the operator had no
    way to act on.

    Deliberately asked HERE rather than inside the measurement. `command_audit` resolves a BARE
    skill tree - one passed as the root itself rather than nested under `.claude/skills/` - and
    measures it, which is what `command_audit.py --coverage` is for. Pushing this test down into
    the measurement would switch that off, and no fixture shaped like a consuming project could
    see it happen."""
    return _skill_dir(Path(repo_root)) is not None


def _type_ref_commands(skill_dir: Path) -> list[str]:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if "## Type Reference" not in text:
        return []
    sec = text.split("## Type Reference", 1)[1].split("## Full Reference")[0]
    return [m.group(1) for m in re.finditer(r"^\| `([^`]+)`", sec, re.M)]


def _scripts(skill_dir: Path) -> list[str]:
    sd = skill_dir / "scripts"
    return sorted(p.stem for p in sd.glob("*.py")
                  if p.stem not in _NON_SCRIPTS and not p.stem.startswith("test"))


#: Commands with no `help/<cmd>.md` page, each with the reason it is legitimate. A waiver is
#: on the page rather than in somebody's memory, and it is CHECKED: a waiver naming a command
#: that now has a page is stale and reported, so the list can only shrink.
HELP_PAGE_WAIVERS: dict = {
    "decisions": "a log verb, documented where the decisions themselves are - not a workflow "
                 "a reader arrives at needing a page (known debt, 2026-08-02)",
    "repo": "the repo-map builder, whose surface is `repo map build` and is covered by "
            "reference-scripts.md (known debt, 2026-08-02)",
    "migrate": "the upgrade orchestrator, documented in reference-upgrade.md which a migration "
               "reads first (known debt, 2026-08-02)",
}


def help_page_findings(skill_dir: Path) -> list[dict]:
    """Every Type Reference command with no help page, and every stale waiver.

    Derived from the Type Reference rather than a hand-kept list of pages: a command added
    there without a page is the gap this catches, and a second list would drift from the first.

    Fails LOUD on an unreadable tree. Returning "no findings" when the directory cannot be read
    is indistinguishable from a clean result, and this check exists precisely because a silent
    pass is what let a missing page ship.
    """
    out: list[dict] = []
    try:
        commands = _type_ref_commands(skill_dir)
        pages = {p.stem for p in (skill_dir / "help").glob("*.md")}
    except OSError as exc:
        return [{"kind": "help-page", "severity": "error",
                 "detail": f"the skill tree could not be read ({exc.__class__.__name__}) - "
                           f"reporting the failure rather than a clean pass"}]
    if not commands:
        return [{"kind": "help-page", "severity": "error",
                 "detail": "SKILL.md names no Type Reference commands - a check that reads "
                           "nothing reports clean, which is the failure it exists to remove"}]
    for cmd in commands:
        if cmd in pages:
            continue
        if cmd in HELP_PAGE_WAIVERS:
            continue
        out.append({"kind": "help-page", "severity": "error",
                    "detail": f"command `{cmd}` is in the Type Reference and has no "
                              f"`help/{cmd}.md` page"})
    for waived in sorted(HELP_PAGE_WAIVERS):
        if waived in pages:
            out.append({"kind": "help-page", "severity": "error",
                        "detail": f"the waiver for `{waived}` is STALE - the page now exists, "
                                  f"so the waiver hides nothing and must be dropped"})
    return out


def _changelog_unreleased_empty(repo_root: Path) -> bool | None:
    # A pending fragment IS the entry (the changelog.d convention): work whose
    # entry awaits compose is documented, not missing.
    frag_dir = Path(repo_root) / "changelog.d"
    if frag_dir.is_dir() and any(frag_dir.glob("*.md")):
        return False
    p = Path(repo_root) / "CHANGELOG.md"
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return None  # no changelog -> not applicable
    if "## [Unreleased]" not in text:
        return None
    after = text.split("## [Unreleased]", 1)[1]
    section = re.split(r"\n## \[", after, maxsplit=1)[0]  # up to the next release header
    return section.strip() == ""


def check(repo_root: Path | str = ".") -> dict:
    if not is_skill_repo(repo_root):  # not the skill repo - nothing to check
        return {"findings": [], "ok": True, "applicable": False}
    skill_dir = _skill_dir(Path(repo_root))
    help_text = (skill_dir / "help" / "help.md").read_text(encoding="utf-8")
    # The script catalogue is a lean index (reference-scripts.md) plus grouped detail pages
    # (reference-scripts-*.md); a script's `### ` entry may live in any of them, so union them.
    refscripts = "\n".join(
        p.read_text(encoding="utf-8")
        for p in sorted(skill_dir.glob("reference-scripts*.md")))
    findings = []
    for cmd in _type_ref_commands(skill_dir):
        # Must be an actual catalogue entry (`/sdlc-studio <cmd>`), not a coincidental
        # backtick mention in prose (which would falsely mark it documented).
        if not re.search(rf"/sdlc-studio {re.escape(cmd)}\b", help_text):
            findings.append({"kind": "command-uncatalogued", "name": cmd, "blocking": True,
                             "detail": f"command `{cmd}` is in the Type Reference but not in help/help.md"})
    for s in _scripts(skill_dir):
        if f"### `{s}.py`" not in refscripts:
            findings.append({"kind": "script-undocumented", "name": s, "blocking": True,
                             "detail": f"scripts/{s}.py has no reference-scripts*.md entry "
                                       "(the lean index or a grouped detail page)"})
    if _changelog_unreleased_empty(Path(repo_root)) is True:
        findings.append({"kind": "changelog-empty", "name": "CHANGELOG", "blocking": False,
                         "detail": "CHANGELOG [Unreleased] is empty - add an entry for the release work (LL0004)"})
    return {"findings": findings, "ok": not any(f["blocking"] for f in findings), "applicable": True}


def cmd_check(args: argparse.Namespace) -> int:
    r = check(args.root)
    if args.format == "json":
        print(json.dumps(r, indent=2))
    elif not r["applicable"]:
        print("doc-coverage: N/A (no SKILL.md under root)")
    else:
        for f in r["findings"]:
            print(f"  [{'FAIL' if f['blocking'] else 'warn'}] {f['detail']}")
        print(f"doc-coverage: {'PASS' if r['ok'] else 'FAIL'}")
    return 0 if r["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Documentation-coverage check.")
    p.add_argument("--root", default=".")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_check)
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
        args = build_parser().parse_args()
        sys.exit(args.func(args))
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
