#!/usr/bin/env python3
"""Audit the skill command surface against the process spine.

The surface has grown organically; this tool ENUMERATES every command and route
deterministically, maps each to the process spine, and assigns a keep / fold / retire
disposition - the map a cleanup acts on, kept re-runnable so the surface cannot silently
drift again. It does NOT itself retire anything (that is a reviewed, editorial step); it
produces the evidence.

The process spine (CR reference): raise a bug/CR/RFC/Issue -> break it down into the delivery
backlog -> run sprints with independent reviews. The top-level human levers are the documents
(PRD, TRD, TSD, Personas); reconcile / review / audit are support. A command that does not serve
that spine is a candidate to fold or retire.

Three signals feed the disposition, all structural (facts, not taste):
  - SPINE      : the curated category a command serves (or `unmapped` - a review candidate)
  - DRIFT      : a command in the help catalogue but not the SKILL Type Reference, or vice versa
  - TOOLING    : (with --check-tools) does the backing script's `--help` run? a dead route is a
                 help entry whose tool is broken or missing

Skill-development tool: it inspects the SKILL itself, so for a CONSUMING project (no SKILL.md
under the root) it is a no-op. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doc_coverage  # noqa: E402  (reuse the enumerators the gate already trusts)

# The process-spine category each command serves. Curated - the one editorial input - so the
# disposition is reproducible and reviewable in one place. A command in the surface but absent
# here is reported `unmapped`, a fold/retire candidate for the human to rule on. Keep in sync as
# commands are added: a NEW command lands `unmapped` until it is placed, which is the nudge to ask
# "does this serve the spine?".
SPINE: dict[str, str] = {
    # RAISE - intake into the Discovery backlog
    "bug": "raise", "cr": "raise", "rfc": "raise", "issue": "raise",
    # BREAK DOWN - Discovery -> Delivery
    "refine": "break-down", "triage": "break-down", "epic": "break-down", "story": "break-down",
    # SPRINT + REVIEW - the delivery loop
    "sprint": "sprint+review", "handoff": "sprint+review", "review": "sprint+review",
    # LEVERS - the top-level human direction documents
    "prd": "lever", "trd": "lever", "tsd": "lever", "persona": "lever", "pvd": "lever",
    "consult": "lever", "chat": "lever",
    # SUPPORT - keep the backlog honest and visible
    "reconcile": "support", "status": "support", "hint": "support", "gate": "support",
    "decisions": "support", "lessons": "support", "audit": "support",
    # UTILITY / lifecycle - legitimate, off the delivery spine
    "init": "utility", "help": "utility", "skill-update": "utility", "upgrade": "utility",
    "migrate": "utility", "project": "utility", "repo": "utility", "plan": "utility",
    "code": "utility", "test-spec": "utility", "test-automation": "utility", "test-env": "utility",
    "deploy": "utility", "mutation": "utility", "retro": "utility",
}

# The spine categories, in the order the audit report groups them.
SPINE_ORDER = ("raise", "break-down", "sprint+review", "lever", "support", "utility", "unmapped")


# A folded command's signpost: it is NOT a catalogue entry. Folding takes a command out of the
# surface while keeping the route alive - an operator following an old habit lands on the command
# that replaced it instead of a dead end. Counting the signpost as a catalogue entry would make a
# fold indistinguishable from leaving the command in place, so these lines are stripped before the
# catalogue is enumerated, and parsed separately as redirects.
_REDIRECT_RE = re.compile(
    r"^- Folded: `/sdlc-studio ([a-z][a-z-]*)` -> `/sdlc-studio ([a-z][a-z-]*)`")


def _redirects(skill_dir: Path) -> dict[str, str]:
    """Folded command -> the command that replaced it, read from the help catalogue's redirect
    lines. One entry per folded command."""
    text = (skill_dir / "help" / "help.md").read_text(encoding="utf-8")
    return {m.group(1): m.group(2)
            for ln in text.splitlines() if (m := _REDIRECT_RE.match(ln))}


def _help_commands(skill_dir: Path) -> list[str]:
    """Distinct `/sdlc-studio <cmd>` tokens in the help catalogue - the commands an operator is
    actually told they can run. The complement of the Type Reference: a command in one but not the
    other is drift. Redirect lines are excluded: a signpost to a folded command's replacement is
    not an offer to run it."""
    text = (skill_dir / "help" / "help.md").read_text(encoding="utf-8")
    text = "\n".join(ln for ln in text.splitlines() if not _REDIRECT_RE.match(ln))
    # rstrip a trailing hyphen so `/sdlc-studio foo-` (a wrapped/placeholder token) does not mint a
    # phantom `foo-` command; empty captures are dropped.
    return sorted({t for m in re.finditer(r"/sdlc-studio ([a-z][a-z-]*)", text)
                   if (t := m.group(1).rstrip("-"))})


def _tool_alive(skill_dir: Path, name: str, timeout: float = 10.0) -> bool:
    """True when `scripts/<name>.py --help` exits 0 - the backing tool is present and parses. A
    command with no same-named script is not a dead route (many commands are natural-language
    routes, not a 1:1 script), so a missing script is reported UNKNOWN, never dead; only a script
    that exists and fails `--help` is a broken tool."""
    p = skill_dir / "scripts" / f"{name}.py"
    if not p.is_file():
        return None
    try:
        r = subprocess.run([sys.executable, str(p), "--help"],
                           capture_output=True, timeout=timeout)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def audit(repo_root: Path | str = ".", *, check_tools: bool = False) -> dict:
    """Enumerate the command surface and disposition each command. Returns
    `{applicable, commands: [{command, spine, in_type_ref, in_help, drift, tool, disposition}],
      scripts: {...}, summary: {...}}`. `check_tools` additionally runs each backing script's
    `--help` (slower; a subprocess per script)."""
    skill_dir = doc_coverage._skill_dir(Path(repo_root))
    if skill_dir is None:
        return {"applicable": False, "commands": [], "scripts": {}, "redirects": {}, "summary": {}}
    type_ref = set(doc_coverage._type_ref_commands(skill_dir))
    help_cmds = set(_help_commands(skill_dir))
    redirects = _redirects(skill_dir)
    scripts = set(doc_coverage._scripts(skill_dir))
    documented_scripts = _documented_scripts(skill_dir)

    rows: list[dict] = []
    for cmd in sorted(type_ref | help_cmds):
        spine = SPINE.get(cmd, "unmapped")
        in_tr, in_help = cmd in type_ref, cmd in help_cmds
        drift = None
        if in_tr and not in_help:
            drift = "in-type-ref-not-in-help"
        elif in_help and not in_tr:
            drift = "in-help-not-in-type-ref"
        tool = _tool_alive(skill_dir, cmd) if check_tools else None
        # Disposition: keep a spine-mapped command with no drift and no broken tool; everything
        # else is a REVIEW candidate (the human rules fold vs retire vs promote). `tool is False`
        # is a genuine broken route - the strongest review signal.
        if tool is False or spine == "unmapped" or drift:
            disposition = "review"
        else:
            disposition = "keep"
        rows.append({"command": cmd, "spine": spine, "in_type_ref": in_tr, "in_help": in_help,
                     "drift": drift, "tool": tool, "disposition": disposition})

    # Scripts are the tooling BEHIND the commands. An undocumented script (no reference entry) is a
    # fold/document candidate; a script whose --help fails is a broken tool.
    script_rows = []
    for s in sorted(scripts):
        alive = _tool_alive(skill_dir, s) if check_tools else None
        script_rows.append({"script": s, "documented": s in documented_scripts, "alive": alive})

    summary = {
        "commands": len(rows),
        "keep": sum(1 for r in rows if r["disposition"] == "keep"),
        "review": sum(1 for r in rows if r["disposition"] == "review"),
        "unmapped": sum(1 for r in rows if r["spine"] == "unmapped"),
        "drift": sum(1 for r in rows if r["drift"]),
        "broken_tools": sum(1 for r in rows if r["tool"] is False)
                        + sum(1 for r in script_rows if r["alive"] is False),
        "scripts": len(script_rows),
        "undocumented_scripts": sum(1 for r in script_rows if not r["documented"]),
        "redirects": len(redirects),
    }
    return {"applicable": True, "checked": check_tools, "commands": rows, "scripts": script_rows,
            "redirects": redirects, "summary": summary}


def _documented_scripts(skill_dir: Path) -> set[str]:
    """Scripts that carry a `### \\`name.py\\`` entry in any reference-scripts*.md page - the
    same authority `doc_coverage` uses, so 'documented' means one thing across both tools."""
    refscripts = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(skill_dir.glob("reference-scripts*.md")))
    return {s for s in doc_coverage._scripts(skill_dir) if f"### `{s}.py`" in refscripts}


def render_markdown(result: dict) -> str:
    """The audit document body: a per-spine command table with dispositions, then the script
    tooling table, then a summary. What a cleanup slice reads to decide what moves."""
    if not result["applicable"]:
        return "# Command-surface audit\n\n_Not a skill repo - nothing to audit._\n"
    s = result["summary"]
    checked = result.get("checked")
    # Only claim tooling health when it was actually verified (--check-tools). Without it, the
    # disposition still stands on spine + drift, but the doc must not certify "0 broken" - that
    # would be an unverified claim persisted to disk.
    tool_note = (f"{s['broken_tools']} broken tool(s)" if checked else "tooling not checked")
    out = ["# Command-surface audit",
           "",
           "_Generated by `scripts/command_audit.py` - re-run to refresh. Dispositions are "
           "structural signals (spine mapping, catalogue drift, tooling health); the keep / fold / "
           "retire DECISION is the reviewer's, recorded here._",
           "",
           f"**{s['commands']} commands** - {s['keep']} keep, {s['review']} to review "
           f"({s['unmapped']} unmapped, {s['drift']} drift, {tool_note}). "
           f"**{s['scripts']} scripts**, {s['undocumented_scripts']} undocumented.",
           ""]
    by_spine: dict[str, list[dict]] = {}
    for r in result["commands"]:
        by_spine.setdefault(r["spine"], []).append(r)
    for spine in SPINE_ORDER:
        rows = by_spine.get(spine)
        if not rows:
            continue
        out += [f"## {spine}", "", "| Command | In Type Ref | In help | Drift | Disposition |",
                "| --- | --- | --- | --- | --- |"]
        for r in rows:
            out.append(f"| `{r['command']}` | {'yes' if r['in_type_ref'] else 'no'} | "
                       f"{'yes' if r['in_help'] else 'no'} | {r['drift'] or '-'} | "
                       f"{r['disposition']} |")
        out.append("")
    # Folded commands - out of the catalogue, still routed. Recorded so a reader can tell a fold
    # (a live route under a new front door) from a deletion (no route at all).
    if result.get("redirects"):
        out += ["## folded", "", "| Command | Redirects to |", "| --- | --- |"]
        out += [f"| `{c}` | `{t}` |" for c, t in sorted(result["redirects"].items())]
        out.append("")
    # Recommended actions - derived from the structural findings, for the cleanup slice to act on.
    help_only = [r["command"] for r in result["commands"]
                 if r["drift"] == "in-help-not-in-type-ref"]
    tr_only = [r["command"] for r in result["commands"]
               if r["drift"] == "in-type-ref-not-in-help"]
    broken = [r["command"] for r in result["commands"] if r["tool"] is False]
    undoc = [r["script"] for r in result["scripts"] if not r["documented"]]
    out += ["## Recommended actions (for the cleanup slice)", ""]
    if help_only:
        out.append(f"- **Promote or retire {len(help_only)} help-only command(s)** "
                   f"(in the help catalogue, not the SKILL Type Reference): "
                   f"{', '.join(f'`{c}`' for c in help_only)}. Promote the ones that serve the "
                   f"spine to the Type Reference; retire the rest.")
    if tr_only:
        out.append(f"- **Document {len(tr_only)} Type-Reference-only command(s)** "
                   f"(no help catalogue entry): {', '.join(f'`{c}`' for c in tr_only)}.")
    if broken:
        out.append(f"- **Fix {len(broken)} broken tool(s)**: {', '.join(f'`{c}`' for c in broken)}.")
    if undoc:
        out.append(f"- **Document {len(undoc)} script(s)** with no reference-scripts entry: "
                   f"{', '.join(f'`{s}`' for s in undoc)}.")
    if not checked:
        out.append("- Re-run with `--check-tools` to verify the tooling behind each command runs "
                   "(this pass did not check).")
    if not (help_only or tr_only or broken or undoc):
        tail = "every tool runs" if checked else "tooling unchecked this pass"
        out.append(f"- No catalogue/spine issues: the surface is spine-mapped and catalogued both "
                   f"ways ({tail}).")
    # exactly one trailing newline - the per-section trailing blanks must not stack into an MD012
    # double-blank at EOF.
    return "\n".join(out).rstrip("\n") + "\n"


def cmd_run(args: argparse.Namespace) -> int:
    result = audit(args.root, check_tools=args.check_tools)
    if not result["applicable"]:
        print("command_audit: not a skill repo (no SKILL.md) - nothing to audit.")
        return 0
    if args.write:
        out = Path(args.root) / "sdlc-studio" / "reviews" / "command-audit.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        from lib import sdlc_md
        sdlc_md.atomic_write(out, render_markdown(result))
        print(f"wrote {out}")
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    if not args.write:
        print(render_markdown(result), end="")
    # exit non-zero under --strict when a broken tool exists (a dead route is a real defect); the
    # unmapped/drift review candidates are advisory - a report, not a gate, unless asked.
    if args.strict and result["summary"]["broken_tools"]:
        print(f"\ncommand_audit: {result['summary']['broken_tools']} broken tool(s) "
              f"(--strict)", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="command_audit", description=__doc__)
    p.add_argument("--root", default=".", help="repo root")
    p.add_argument("--check-tools", action="store_true",
                   help="run each backing script's --help (slower; detects a broken tool)")
    p.add_argument("--write", action="store_true",
                   help="write sdlc-studio/reviews/command-audit.md instead of stdout")
    p.add_argument("--strict", action="store_true",
                   help="exit non-zero when a broken tool is found (with --check-tools)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
