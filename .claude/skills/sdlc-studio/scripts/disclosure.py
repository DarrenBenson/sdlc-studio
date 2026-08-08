#!/usr/bin/env python3
"""Progressive-disclosure + Claude Code best-practice check.

The skill is loaded into agent sessions, so disclosure discipline is a token lever. This is an
**advisory** check (it never blocks the gate): it surfaces where reference/help files lack a
`Load when:` trigger or are orphaned from every index, and a few `best-practices/claude-skill.md`
structure items. It holds NEW files to the discipline and reports the existing backlog.

Skill-development check: it inspects the SKILL itself, so for a CONSUMING project (no SKILL.md under
the root) it is a no-op (ok, N/A) - mirrors doc_coverage.py. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

_SKILL_REL = Path(".claude") / "skills" / "sdlc-studio"
_NON_SCRIPTS = {"__init__"}
# leading boundary so "Download:" / "Payload:" / "Preload:" do not false-match the marker
_LOAD_MARKER = re.compile(r"(?:^|[\s>*_|#-])Load\s*(?:when)?\s*:", re.I)


def _skill_dir(repo_root: Path) -> Path | None:
    d = Path(repo_root) / _SKILL_REL
    return d if (d / "SKILL.md").exists() else None


def _read(p: Path) -> str:
    """Read text defensively - a non-UTF-8 or unreadable file must never crash an advisory
    check (it would abort the whole gate). Degrades to '' / replacement chars."""
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _indexed(name: str, index_text: str) -> bool:
    """True if the filename appears as a whole token in an index (boundary-matched, so a short
    name like `code.md` is not masked by `qrcode.md`)."""
    return re.search(r"(?<![\w./-])" + re.escape(name) + r"(?![\w])", index_text) is not None


def _disclosable(skill_dir: Path) -> list[Path]:
    """The on-demand docs that should each declare a load trigger: reference-*.md + help/*.md."""
    out = sorted(skill_dir.glob("reference-*.md"))
    out += sorted((skill_dir / "help").glob("*.md"))
    return out


def nesting_depth(repo_root: Path | str = ".") -> dict:
    """How many hops from SKILL.md a reader takes to reach the FURTHEST file, by shortest path.

    BREADTH-FIRST, so each file is measured by the shortest route to it. A depth-first longest
    path measures how far a reader could WANDER - 37 hops here - which is a wrong answer wearing
    a number: nobody reads the graph that way, and the figure would be about the link density
    rather than about the disclosure.

    MEASURED, never asserted. The depth is reported and nothing is gated on it: the path is not
    fixable without a rewrite this change is not doing, and a number somebody can act on is the
    honest disposition where a silence reads as absence.

    ADVISORY - the caller exits 0 whatever the depth. `disclosure.py` runs inside the blocking
    `lint` chain, so refusing here would turn a reported measurement into a gate nobody agreed
    to.
    """
    import collections  # noqa: PLC0415
    import re as _re  # noqa: PLC0415
    skill = _depth_root(Path(repo_root))
    if skill is None or not (skill / "SKILL.md").is_file():
        return {"applicable": False, "depth": 0, "furthest": None, "reached": 0}

    def links(name: str) -> set:
        target = skill / name
        if not target.is_file():
            return set()
        try:
            body = target.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return set()
        # BOTH shapes. SKILL.md points at most of its family by bare filename in a table cell
        # (`reference-prd.md`), not as a markdown link - a link-only matcher measures a depth of
        # zero over a document that names fifty files.
        out = set(_re.findall(r"\]\(([^)#]+\.md)[^)]*\)", body))
        out |= set(_re.findall(r"[\w./-]*(?:reference|help)[\w./-]*\.md", body))
        return {n.lstrip("./") for n in out if (skill / n.lstrip("./")).is_file()}

    dist = {"SKILL.md": 0}
    q = collections.deque(["SKILL.md"])
    while q:
        name = q.popleft()
        for nxt in sorted(links(name)):
            if nxt not in dist:
                dist[nxt] = dist[name] + 1
                q.append(nxt)
    furthest = max(dist, key=lambda k: dist[k])
    return {"applicable": True, "depth": dist[furthest], "furthest": furthest,
            "reached": len(dist)}


def _depth_root(root: Path) -> Path | None:
    """The skill tree for the DEPTH measurement, which accepts a bare skill dir as well.

    Deliberately NOT named `_skill_dir`: that name belongs to `check()`, which requires a repo
    root, and a widened copy under the same name silently changed what `check()` considers an
    applicable tree - in a script the lint chain now blocks on.
    """
    for cand in (root / ".claude/skills/sdlc-studio", root):
        if (cand / "SKILL.md").is_file():
            return cand
    return None


def check(repo_root: Path | str = ".") -> dict:
    """Advisory findings (all blocking=False). {findings, ok, applicable}."""
    skill_dir = _skill_dir(Path(repo_root))
    if skill_dir is None:  # not the skill repo - nothing to check
        return {"findings": [], "ok": True, "applicable": False}
    findings: list[dict] = []

    def warn(kind: str, name: str, detail: str) -> None:
        findings.append({"kind": kind, "name": name, "detail": detail, "blocking": False})

    # the reachability indexes: a file is "indexed" if its name appears in any of these
    index_text = "".join(_read(skill_dir / rel)
                         for rel in ("SKILL.md", "help/references.md", "help/help.md"))

    for f in _disclosable(skill_dir):
        head = "\n".join(_read(f).splitlines()[:20])
        if not _LOAD_MARKER.search(head):
            warn("missing-load-marker", f.name,
                 f"{f.name} has no `Load when:` trigger near the top (on-demand discipline)")
        # help/<type>.md files are reached via the templated `help/{type}.md` reference in the
        # Progressive Loading Guide / references.md, so the pattern entry vouches for them.
        reachable = _indexed(f.name, index_text) or (
            f.parent.name == "help" and "help/{type}.md" in index_text)
        if not reachable:
            warn("orphan", f.name,
                 f"{f.name} is not referenced from SKILL.md / help/references.md / help/help.md")

    # CR0108: every command help file leads with a natural-language "You can just ask" block - the
    # skill is model-invoked, so plain language is the real interface. Meta catalogues are exempt.
    for h in sorted((skill_dir / "help").glob("*.md")):
        if h.name in ("arguments.md", "references.md"):
            continue
        if "## You can just ask" not in _read(h):
            warn("help-missing-nl-block", h.name,
                 f"help/{h.name} has no `## You can just ask` natural-language block")

    # best-practice (best-practices/claude-skill.md): scripts hygiene
    for s in sorted((skill_dir / "scripts").glob("*.py")):
        if s.stem in _NON_SCRIPTS or s.stem.startswith("test"):
            continue
        text = _read(s)
        if not os.access(s, os.X_OK):
            warn("script-not-executable", s.name, f"scripts/{s.name} is not executable (chmod +x)")
        if "argparse" not in text and "--help" not in text:
            warn("script-no-help", s.name, f"scripts/{s.name} exposes no --help / argparse")

    # best-practice: fill-in artifact scaffolds should use {{placeholder}}. Scope to templates/core/
    # (the scaffolds); modules/prompts/pointers are guidance/example content, legitimately fixed.
    for t in sorted((skill_dir / "templates" / "core").glob("*.md")):
        if "{{" not in _read(t):
            warn("template-no-placeholder", t.name,
                 f"templates/core/{t.name} has no {{{{placeholder}}}} (hardcoded?)")

    # best-practice: SKILL.md carries a When to Use section
    skill_text = _read(skill_dir / "SKILL.md")
    if not re.search(r"^##+\s+When to Use", skill_text, re.M | re.I):
        warn("skill-missing-section", "SKILL.md", "SKILL.md has no `When to Use` section")

    return {"findings": findings, "ok": True, "applicable": True}  # advisory: always ok


def cmd_check(args: argparse.Namespace) -> int:
    r = check(args.root)
    # The measured depth travels WITH the findings. `nesting_depth` had no caller outside its
    # own tests - a measurement nothing invokes reports to nobody, which is the shape this
    # project already filed once as BG0541, and the criterion asks for a number a reader can
    # act on rather than a function that could produce one.
    r = dict(r, nesting=nesting_depth(args.root))
    if args.format == "json":
        print(json.dumps(r, indent=2))
    elif not r["applicable"]:
        print("disclosure: N/A (not the skill repo)")
    else:
        for f in r["findings"]:
            print(f"  [warn] [{f['kind']}] {f['detail']}")
        n = r["nesting"]
        if n["applicable"]:
            print(f"  [info] nesting depth {n['depth']} hop(s) from SKILL.md to "
                  f"{n['furthest']}, over {n['reached']} reachable file(s) - MEASURED and "
                  f"reported, gated on nothing")
        print(f"disclosure: {len(r['findings'])} advisory finding(s)")
    # advisory: exit 0 unless --strict (opt-in enforcement)
    return 1 if (args.strict and r["findings"]) else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Progressive-disclosure + best-practice check.")
    p.add_argument("--root", default=".")
    p.add_argument("--strict", action="store_true", help="exit non-zero if any finding (opt-in)")
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
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
