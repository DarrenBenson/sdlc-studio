#!/usr/bin/env python3
"""Deterministic project initialiser.

`init` is the executable greenfield bootstrap - previously a manual checklist. It:
  1. creates the full `sdlc-studio/` directory tree,
  2. pre-creates every per-type `_index.md` (reusing the index helper),
  3. seeds the config, a `.gitignore` for the runtime-state dir, and the agent-instructions files,
  4. with `--scaffold`, seeds the singleton docs (prd/trd/tsd/personas).

Idempotent: never overwrites an existing file (reported and skipped) unless `--force`.
Config is load-bearing and stack detection is a guess on greenfield, so `--dry-run`
previews every write (the workflow shows it and confirms once) before a real run - the
non-judgement steps (tree, indexes, agent-instructions) need no confirmation. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import file_finding  # noqa: E402  (reuse ensure_index - the index helper)

SKILL = Path(__file__).resolve().parent.parent
SDLC = "sdlc-studio"
# The full tree: the 8 numbered-artifact dirs plus the cross-cutting workspaces.
DIRS = ["epics", "stories", "plans", "bugs", "change-requests", "rfcs", "test-specs",
        "workflows", "retros", "handoffs", "decisions", "reviews", ".local"]
INDEX_TYPES = ["epic", "story", "plan", "bug", "cr", "rfc", "test-spec", "workflow"]
SINGLETONS = ["prd", "trd", "tsd", "personas"]
AGENT_FILES = [("agent-instructions.md", "AGENTS.md"),
               ("agent-instructions.CLAUDE.md", "CLAUDE.md")]
# Stack detection: marker file -> (language, framework hint).
DETECT = [("package.json", "typescript/node"), ("pyproject.toml", "python"),
          ("go.mod", "go"), ("Cargo.toml", "rust"), ("pom.xml", "java"),
          ("build.gradle", "java/kotlin")]
# DoR/DoD tailoring suggestions per detected profile key (language, test framework,
# deploy surface). OFFERED at init, applied only on --accept-tailoring - never
# auto-applied. Untagged (human-judged) unless a registered check id fits, so the
# tailored result always passes the check-id registry validation.
TAILOR_SUGGESTIONS = {
    "python": [
        {"kind": "done", "level": "Story",
         "criterion": "- [ ] The Python test suite is green for the touched modules"},
        {"kind": "ready", "level": "Story",
         "criterion": "- [ ] A Verify line names the exact test command (pytest/unittest selector)"},
    ],
    "typescript/node": [
        {"kind": "done", "level": "Story",
         "criterion": "- [ ] The JS/TS test suite is green for the touched modules"},
        {"kind": "done", "level": "Story",
         "criterion": "- [ ] Type checks pass (tsc/linter) on the touched files"},
    ],
    "go": [{"kind": "done", "level": "Story",
            "criterion": "- [ ] go test ./... is green and go vet reports nothing"}],
    "rust": [{"kind": "done", "level": "Story",
              "criterion": "- [ ] cargo test is green and clippy reports nothing new"}],
    "java": [{"kind": "done", "level": "Story",
              "criterion": "- [ ] The JVM test suite is green for the touched modules"}],
    "java/kotlin": [{"kind": "done", "level": "Story",
                     "criterion": "- [ ] The JVM test suite is green for the touched modules"}],
    "csharp/dotnet": [{"kind": "done", "level": "Story",
                       "criterion": "- [ ] dotnet test is green for the touched projects"}],
    "docker": [{"kind": "done", "level": "Release",
                "criterion": "- [ ] The container image builds cleanly and the deploy-readiness "
                             "checks (cold-spawn, smoke, rollback) are satisfied"}],
}


def detect_stack(root: Path) -> str | None:
    for marker, lang in DETECT:
        if (root / marker).exists():
            return lang
    if list(root.glob("*.csproj")):
        return "csharp/dotnet"
    return None


def tailor_suggestions(root: Path, lang: str | None) -> list[dict]:
    """Stack/profile-derived DoR/DoD criteria to OFFER (language, plus the deploy
    surface when a Dockerfile is present). Deterministic; the operator accepts or
    edits - nothing here writes."""
    out = list(TAILOR_SUGGESTIONS.get(lang or "", []))
    if (root / "Dockerfile").exists():
        out += TAILOR_SUGGESTIONS["docker"]
    return out


def _append_to_level(text: str, level: str, criterion: str) -> str:
    """Insert a criterion at the end of the document's `## <level>` section (word-exact
    heading match, same rule as the gates' resolver)."""
    lines = text.splitlines()
    head_re = re.compile(rf"^##\s+{re.escape(level)}(?:\s|$)", re.IGNORECASE)
    start = next((i for i, ln in enumerate(lines) if head_re.match(ln)), None)
    if start is None:  # no such level: append a new section - never drop an accepted edit
        return text.rstrip("\n") + f"\n\n## {level}\n\n{criterion}\n"
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")),
               len(lines))
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1  # insert before the section's trailing blank(s)
    lines.insert(end, criterion)
    return "\n".join(lines) + "\n"


def _strip_comment(text: str) -> str:
    return re.sub(r"^<!--.*?-->\n+", "", text, count=1, flags=re.DOTALL)


def _fill_known(text: str, fields: dict) -> str:
    """Fill only the placeholders init can know; leave high-judgement fields (e.g.
    {{problem_description}}) visibly empty so a default is never mistaken for a decision."""
    for key in ("project_name", "language", "date", "last_updated"):
        if key in fields:
            text = text.replace("{{" + key + "}}", fields[key])
    return text


def init(repo_root: Path | str, detect: bool = False, scaffold: bool = False,
         force: bool = False, dry_run: bool = False,
         accept_tailoring: bool = False) -> dict:
    root = Path(repo_root)
    today = date.today().isoformat()
    lang = detect_stack(root) if detect else None
    fields = {"project_name": root.resolve().name, "date": today, "last_updated": today}
    if lang:
        fields["language"] = lang
    created: list[str] = []
    skipped: list[str] = []

    def _write(rel: str, content: str) -> None:
        p = root / rel
        if p.exists() and not force:
            skipped.append(rel)
            return
        created.append(rel)
        if not dry_run:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

    # 1. directory tree
    for d in DIRS:
        rel = f"{SDLC}/{d}"
        if (root / rel).is_dir():
            skipped.append(rel + "/")
        else:
            created.append(rel + "/")
            if not dry_run:
                (root / rel).mkdir(parents=True, exist_ok=True)

    # 2. per-type indexes (reuse the index helper; idempotent)
    for t in INDEX_TYPES:
        idx_rel = f"{sdlc_md.ARTIFACT_TYPES[t][0]}/_index.md"
        if (root / idx_rel).exists():
            skipped.append(idx_rel)
        elif dry_run:
            created.append(idx_rel)
        elif file_finding.ensure_index(root, t, today):
            created.append(idx_rel)

    # 3. config (seeded from the template; detected stack noted as an active header)
    cfg_tmpl = SKILL / "templates" / "config.yaml"
    if cfg_tmpl.exists():
        header = f"# Project: {fields['project_name']}\n"
        if lang:
            header += f"# Detected stack: {lang}\n"
        _write(f"{SDLC}/.config.yaml", header + "\n" + cfg_tmpl.read_text(encoding="utf-8"))

    # 3b. gitignore the runtime-state dir so derived caches/reports/lessons are never committed
    #. Self-contained in sdlc-studio/ - never touches the project's own root .gitignore.
    _write(f"{SDLC}/.gitignore",
           "# SDLC Studio runtime state (caches, verify reports, lessons) - derived, not source\n"
           ".local/\n")

    # 4. agent-instructions (tool-neutral starters; copied verbatim if absent)
    for src, dst in AGENT_FILES:
        st = SKILL / "templates" / src
        if st.exists():
            _write(dst, _fill_known(_strip_comment(st.read_text(encoding="utf-8")), fields))

    # 5. decisions log (project infrastructure, always seeded empty)
    dec_tmpl = SKILL / "templates" / "decisions.md"
    if dec_tmpl.exists():
        _write(f"{SDLC}/decisions.md", _strip_comment(dec_tmpl.read_text(encoding="utf-8")))

    # 5b. the DoR/DoD documents (project infrastructure, like the decisions log): the
    # shipped defaults ARE the enforced bar, so a new project starts with them named.
    # The tailoring pass OFFERS stack-derived criteria; only --accept-tailoring writes
    # them (offer, never auto-apply - the persona team-gen pattern).
    for kind in ("ready", "done"):
        tmpl = SKILL / "templates" / "core" / f"definition-of-{kind}.md"
        if tmpl.exists():
            _write(f"{SDLC}/definition-of-{kind}.md",
                   _strip_comment(tmpl.read_text(encoding="utf-8")))
    suggestions = tailor_suggestions(root, lang) if detect else []
    written: list[dict] = []
    if suggestions and accept_tailoring and not dry_run:
        for s in suggestions:
            doc = root / SDLC / f"definition-of-{s['kind']}.md"
            if not doc.is_file():
                continue
            text = doc.read_text(encoding="utf-8")
            if s["criterion"] in text:  # idempotent: a re-accept never duplicates
                continue
            doc.write_text(_append_to_level(text, s["level"], s["criterion"]),
                           encoding="utf-8")
            written.append(s)
    applied = bool(written)  # True only when something was actually written

    # 6. singleton docs (opt-in)
    if scaffold:
        for name in SINGLETONS:
            st = SKILL / "templates" / "core" / f"{name}.md"
            if st.exists():
                _write(f"{SDLC}/{name}.md",
                       _fill_known(_strip_comment(st.read_text(encoding="utf-8")), fields))

    return {"created": created, "skipped": skipped, "language": lang,
            "scaffold": scaffold, "dry_run": dry_run,
            "tailoring": {"suggestions": suggestions, "applied": applied,
                          "written": written,
                          "accepted": bool(accept_tailoring and not dry_run)}}


def cmd_run(args: argparse.Namespace) -> int:
    r = init(args.root, detect=args.detect, scaffold=args.scaffold,
             force=args.force, dry_run=args.dry_run,
             accept_tailoring=getattr(args, "accept_tailoring", False))
    if args.format == "json":
        print(json.dumps(r, indent=2))
        return 0
    verb = "would create" if r["dry_run"] else "created"
    print(f"init: {verb} {len(r['created'])}, skipped {len(r['skipped'])} existing"
          + (f" (stack: {r['language']})" if r["language"] else ""))
    for c in r["created"]:
        print(f"  + {c}")
    if r["skipped"]:
        print(f"  ({len(r['skipped'])} existing left untouched)")
    tailoring = r.get("tailoring") or {}
    if tailoring.get("suggestions"):
        if tailoring["applied"]:
            print("tailoring accepted - appended to the DoR/DoD documents "
                  "(the static documents remain the source of truth; edit them freely):")
            for s in tailoring["written"]:  # only what was actually written, never a skip
                print(f"  + definition-of-{s['kind']}.md / {s['level']}: {s['criterion']}")
            skipped_n = len(tailoring["suggestions"]) - len(tailoring["written"])
            if skipped_n:
                print(f"  ({skipped_n} suggestion(s) already present - skipped)")
        elif tailoring.get("accepted"):
            print("tailoring: every suggested criterion is already present - "
                  "nothing to apply")
        else:
            print("tailoring offer (derived from the detected stack - nothing is applied "
                  "without acceptance):")
            for s in tailoring["suggestions"]:
                print(f"  ? definition-of-{s['kind']}.md / {s['level']}: {s['criterion']}")
            print("  accept: re-run with --accept-tailoring; or edit the documents by hand")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic project initialiser.")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="Create the tree, indexes, config, and agent-instructions.")
    r.add_argument("--root", default=".")
    r.add_argument("--detect", action="store_true", help="infer the stack from project files")
    r.add_argument("--scaffold", action="store_true", help="also seed prd/trd/tsd/personas")
    r.add_argument("--force", action="store_true", help="overwrite existing files")
    r.add_argument("--dry-run", action="store_true", dest="dry_run", help="preview; write nothing")
    r.add_argument("--accept-tailoring", action="store_true", dest="accept_tailoring",
                   help="apply the stack-derived DoR/DoD tailoring suggestions (with "
                        "--detect); without this flag they are only offered")
    r.add_argument("--format", choices=("text", "json"), default="text")
    r.set_defaults(func=cmd_run)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
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
