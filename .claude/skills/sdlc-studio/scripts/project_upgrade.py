#!/usr/bin/env python3
"""project upgrade: migrate a consuming project to the current skill conventions.

`skill-update` updates the skill (the tool); this updates a consuming PROJECT's artefacts to match
what the new skill expects. It DETECTS the version/convention gap, AUDITS the project, and reports a
migration plan split into **auto-correctable** (safe, deterministic) and **needs-judgment** (a
report - never auto-applied, never filed as CRs). Only with `--apply` does it perform the safe set:
scaffold `sdlc-studio/.config.yaml` (with a `provenance.adopt_after` cutoff so existing artefacts
are exempt) and `.version`, then `reconcile` index/status drift. Dry-run by default; idempotent;
nothing destructive. Reuses reconcile / validate / next_id / version_check. Pure stdlib.
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
import version_check  # noqa: E402
import reconcile  # noqa: E402
import validate  # noqa: E402
import next_id  # noqa: E402

CURRENT_SCHEMA = 2  # templates/config-defaults.yaml schema_version
# Dirs newer projects carry; absent ones are advisory (created on first use), not auto-made
# (empty dirs do not persist in git, and guessing per-type index headers would over-reach).
STANDARD_DIRS = ("change-requests", "rfcs", "decisions", "retros")
# The v3.1 default amigo cards (templates/personas/amigos/, RFC0020). Installed into a project's
# persona dir when absent so it gets an editable engineering team; never overwritten once present.
AMIGO_CARDS = ("engineering.md", "qa.md", "product.md")

_CONFIG = ("# Project configuration for sdlc-studio (merged over templates/config-defaults.yaml).\n"
           "provenance:\n"
           "  # Stamping postdates this project's existing artefacts; exempt them so `provenance\n"
           "  # check` judges only new work (cutoff = the highest id present at upgrade).\n"
           "  adopt_after: {cutoff}\n"
           "  enforce: false\n")
_VERSION = ("# SDLC Studio Project Version (sdlc-studio/.version)\n"
            "schema_version: {schema}\n"
            "upgraded_from: {prev}\n"
            "upgraded_at: {today}\n"
            'skill_version: "{skill}"\n')


def _sdlc(root: Path) -> Path:
    return Path(root) / "sdlc-studio"


def _amigos_source() -> Path:
    """The skill's shipped amigo cards (templates/personas/amigos/)."""
    return version_check.skill_root() / "templates" / "personas" / "amigos"


def _missing_amigos(root: Path) -> list[str]:
    """The default amigo cards a project lacks (present source, absent in the project's
    personas/amigos/). A card already in the project - default or customised - is left alone."""
    src = _amigos_source()
    dest = _sdlc(root) / "personas" / "amigos"
    return [name for name in AMIGO_CARDS
            if (src / name).exists() and not (dest / name).exists()]


def _bump_version_text(text: str, installed: str, prev_skill: str | None,
                       today: str | None = None) -> str:
    """Surgically bump an EXISTING .version - update schema/skill, stamp upgraded_from/upgraded_at,
    and PRESERVE every other line (e.g. an author's `created_at`). `today` is injectable
    for deterministic tests."""
    def setline(t: str, key: str, value: str) -> str:
        pat = re.compile(rf"^{key}:.*$", re.M)
        line = f"{key}: {value}"
        return pat.sub(line, t, count=1) if pat.search(t) else t.rstrip("\n") + f"\n{line}\n"
    t = setline(text, "schema_version", str(CURRENT_SCHEMA))
    t = setline(t, "skill_version", f'"{installed}"')
    t = setline(t, "upgraded_from", prev_skill or "null")
    t = setline(t, "upgraded_at", today or date.today().isoformat())
    return t


def _read_version(root: Path) -> tuple[int | None, str | None]:
    v = _sdlc(root) / ".version"
    if not v.exists():
        return None, None
    t = v.read_text(encoding="utf-8")
    sm = re.search(r"^schema_version:\s*(\d+)", t, re.M)
    km = re.search(r'^skill_version:\s*"?([\d.]+)"?', t, re.M)
    return (int(sm.group(1)) if sm else None), (km.group(1) if km else None)


def detect(root: Path | str) -> dict:
    """The version gap: project `.version` (schema + skill) vs the installed skill + CURRENT_SCHEMA."""
    root = Path(root)
    proj_schema, proj_skill = _read_version(root)
    installed = version_check.installed_version(version_check.skill_root())
    behind = (proj_schema is None) or (proj_schema < CURRENT_SCHEMA) or version_check._gt(installed, proj_skill)
    return {"has_version_file": (_sdlc(root) / ".version").exists(),
            "project_schema": proj_schema, "project_skill": proj_skill,
            "current_schema": CURRENT_SCHEMA, "installed_skill": installed, "behind": behind}


_OLD_PERSONA_HEADING = re.compile(r"^##+\s+(Backstory|Psychology|Decision Drivers|Personality|Interaction Guide)",
                                  re.M | re.I)


def _old_persona_model(sd: Path) -> bool:
    """True if the project uses the legacy persona model: the nested two-category structure
    (personas/team or personas/stakeholders), or a persona with old-model section headings. Catches
    nested personas that the flat Cooper well-formedness check (validate.check_personas) misses."""
    pdir = sd / "personas"
    if not pdir.is_dir():
        return False
    if (pdir / "team").is_dir() or (pdir / "stakeholders").is_dir():
        return True
    # top-level design personas only: the seats/ subdir holds review-seat charters (a different
    # schema) and a consult-guide - none of those are "old design personas".
    # sorted() for filesystem-independent, reproducible scanning.
    for p in sorted(pdir.glob("*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if p.name == "index.md":  # personas catalogued inline in the old two-category index
            if re.search(r"team personas?|stakeholder personas?|\bamigo\b", text, re.I):
                return True
            continue
        if p.name.lower() in {"readme.md", "consult-guide.md"} or p.name.startswith("_"):
            continue
        if _OLD_PERSONA_HEADING.search(text):
            return True
    return False


def _max_id(root: Path) -> int:
    return max((max(ids, default=0) for ids in
                (next_id.local_ids(t, root) for t in sdlc_md.ARTIFACT_TYPES)), default=0)


def audit(root: Path | str) -> dict:
    """Findings split into auto-correctable vs needs-judgment. Read-only."""
    root = Path(root)
    sd = _sdlc(root)
    auto: list[dict] = []
    manual: list[dict] = []
    if not (sd / ".config.yaml").exists():
        auto.append({"kind": "missing-config", "detail": "no sdlc-studio/.config.yaml (provenance cutoff, overrides)"})
    pv_schema, pv_skill = _read_version(root)
    installed = version_check.installed_version(version_check.skill_root())
    if not (sd / ".version").exists():
        auto.append({"kind": "missing-version", "detail": "no sdlc-studio/.version (records the skill/schema version)"})
    elif (installed and pv_skill != installed) or (pv_schema or 0) < CURRENT_SCHEMA:
        # present but stale - apply() bumps it, so the dry-run must report it too
        auto.append({"kind": "stale-version",
                     "detail": f"sdlc-studio/.version records skill {pv_skill or '?'}; bump to {installed or '?'}"})
    missing_amigos = _missing_amigos(root)
    if missing_amigos:
        auto.append({"kind": "missing-amigos", "names": missing_amigos,
                     "detail": f"missing v3.1 default amigo cards ({', '.join(missing_amigos)}) - "
                               "install to sdlc-studio/personas/amigos/ (editable, never overwritten)"})
    drift = sum(len(reconcile.detect_type(t, root)["drift"]) for t in sdlc_md.ARTIFACT_TYPES)
    if drift:
        # NOT auto-applied by upgrade: reconcile can be destructive on multi-schema / inline-row
        # projects. Review it deliberately with `/sdlc-studio reconcile`.
        manual.append({"kind": "index-drift", "count": drift,
                       "detail": f"{drift} index/status drift item(s) - review with `/sdlc-studio reconcile` "
                                 "(not auto-applied by upgrade)"})
    # advisory dirs (report, not auto - see module docstring)
    missing = [d for d in STANDARD_DIRS if not (sd / d).is_dir()]
    if missing:
        manual.append({"kind": "missing-dirs", "names": missing,
                       "detail": f"no {', '.join(missing)} dir(s) - created when you first use them"})
    if _old_persona_model(sd) or validate.check_personas(root):
        manual.append({"kind": "personas",
                       "detail": "old persona model present - rewrite to the Cooper model "
                                 "(persona-template.md) / review-seat charters (review-seat-charter.md)"})
    instr = validate.check_instructions(root)
    if instr:
        manual.append({"kind": "agents", "count": len(instr),
                       "detail": f"{len(instr)} AGENTS.md/CLAUDE.md hygiene finding(s) - refresh from "
                                 "templates/agent-instructions.md, preserving project sections"})
    verrs = sum(1 for t in sdlc_md.ARTIFACT_TYPES for p in sdlc_md.artifact_files(t, root)
                for v in validate.validate_file(p, t, root) if v["severity"] == "error")
    if verrs:
        manual.append({"kind": "validate-errors", "count": verrs,
                       "detail": f"{verrs} validate error(s) - missing AC/Verify, status vocab, unfilled placeholders"})
    return {"auto": auto, "manual": manual}


def apply(root: Path | str, with_reconcile: bool = False, today: str | None = None) -> list[str]:
    """Perform the SAFE deterministic corrections (scaffold .config.yaml, bump .version). Idempotent.
    Reconcile is NOT run unless with_reconcile=True - it can rewrite indexes destructively on
    multi-schema/inline-convention projects, so it is a separate, deliberate step. `today`
    is injectable for deterministic tests. Returns the actions taken. Refuses a path that is
    not already an sdlc-studio project so a mistyped --root cannot scaffold a phantom project."""
    today = today or date.today().isoformat()
    root = Path(root)
    sd = _sdlc(root)
    if not sd.is_dir():
        raise FileNotFoundError(f"no sdlc-studio/ under {root} - not an sdlc-studio project")
    actions: list[str] = []
    cfg = sd / ".config.yaml"
    if not cfg.exists():
        cutoff = _max_id(root)
        cfg.write_text(_CONFIG.format(cutoff=cutoff), encoding="utf-8")
        actions.append(f"created sdlc-studio/.config.yaml (provenance.adopt_after: {cutoff})")
    ver = sd / ".version"
    prev_schema, prev_skill = _read_version(root)
    installed = version_check.installed_version(version_check.skill_root()) or "unknown"
    if not ver.exists():
        ver.write_text(_VERSION.format(schema=CURRENT_SCHEMA, prev="null",
                                       today=today, skill=installed), encoding="utf-8")
        actions.append(f"created sdlc-studio/.version (schema {CURRENT_SCHEMA}, skill {installed})")
    elif prev_skill != installed:
        ver.write_text(_bump_version_text(ver.read_text(encoding="utf-8"), installed, prev_skill, today), encoding="utf-8")
        actions.append(f"updated sdlc-studio/.version (skill {prev_skill or '?'} -> {installed})")
    elif (prev_schema or 0) < CURRENT_SCHEMA:
        ver.write_text(_bump_version_text(ver.read_text(encoding="utf-8"), installed, prev_skill, today), encoding="utf-8")
        actions.append(f"repaired sdlc-studio/.version (schema -> {CURRENT_SCHEMA})")
    # v3.1 amigo defaults: install each missing default card into the project's personas/amigos/.
    # Idempotent - a card already present (default or customised) is never overwritten.
    missing_amigos = _missing_amigos(root)
    if missing_amigos:
        src = _amigos_source()
        dest = sd / "personas" / "amigos"
        dest.mkdir(parents=True, exist_ok=True)
        for name in missing_amigos:
            (dest / name).write_text((src / name).read_text(encoding="utf-8"), encoding="utf-8")
        actions.append(f"installed {len(missing_amigos)} v3.1 amigo card(s) to "
                       f"sdlc-studio/personas/amigos/ ({', '.join(missing_amigos)})")
    # Reconcile is OFF by default: it can rewrite indexes, and on multi-schema/inline-convention
    # projects that is destructive - so an "upgrade" must not bundle it. Opt in with with_reconcile, or
    # run `/sdlc-studio reconcile` deliberately after reviewing its report.
    if with_reconcile:
        rows = counts = 0
        for t in sdlc_md.ARTIFACT_TYPES:
            r = reconcile.apply_type(t, root)
            rows += len(r.get("changes", []))
            counts += int(bool(r.get("counts_updated")))
        if rows or counts:
            actions.append(f"reconciled {rows} index row(s)" + (f", {counts} count block(s)" if counts else ""))
    return actions


def cmd_upgrade(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if not _sdlc(root).is_dir():
        print(f"error: no sdlc-studio/ under {root} - not an sdlc-studio project", file=sys.stderr)
        return 1
    d = detect(root)
    a = audit(root)
    has_work = d["behind"] or bool(a["auto"]) or bool(a["manual"])
    applied: list[str] = []
    if args.apply and (d["behind"] or a["auto"]):  # apply whenever there is safe work, even if "current"
        applied = apply(root, with_reconcile=args.with_reconcile)
    if args.format == "json":
        print(json.dumps({"detect": d, "audit": a, "applied": applied}, indent=2))
        return 0
    sk = d["installed_skill"] or "?"
    if not has_work:
        print(f"project upgrade: already current (schema {d['project_schema']}, skill {d['project_skill'] or '?'}).")
        return 0
    if d["behind"]:
        print(f"project upgrade: BEHIND - project schema {d['project_schema']} / skill "
              f"{d['project_skill'] or 'unknown'} vs skill {sk} (schema {CURRENT_SCHEMA}).\n")
    else:
        print(f"project upgrade: version current (skill {d['project_skill'] or '?'}), but conventions drift:\n")
    print("Auto-correctable (apply with --apply):")
    for f in a["auto"]:
        print(f"  [auto]   {f['detail']}")
    print("\nNeeds judgement (do by hand - reported, not filed as CRs):")
    for f in a["manual"]:
        print(f"  [manual] {f['detail']}")
    if applied:
        print("\nApplied:")
        for x in applied:
            print(f"  + {x}")
    elif args.apply:
        print("\n(nothing auto-correctable to apply)")
    else:
        print("\nRe-run with --apply to perform the auto-correctable set; then run the gate.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Migrate a consuming project to current skill conventions.")
    p.add_argument("--root", default=".")
    p.add_argument("--apply", action="store_true", help="perform the safe deterministic corrections (default: dry-run)")
    p.add_argument("--with-reconcile", action="store_true",
                   help="also run reconcile --apply (OFF by default - it can rewrite indexes; review first)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_upgrade)
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
