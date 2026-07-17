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

# The upgrade target: the CURRENT schema version, derived from the single source of truth
# (templates/config.yaml, what `init` seeds new projects with) - never the config-defaults.yaml
# fallback, which is the legacy stamp for un-stamped workspaces. A hardcoded 2 here contradicted
# init seeding 3 and would move an upgraded project to the wrong version.
CURRENT_SCHEMA = sdlc_md.current_schema()
# Dirs newer projects carry; absent ones are advisory (created on first use), not auto-made
# (empty dirs do not persist in git, and guessing per-type index headers would over-reach).
STANDARD_DIRS = ("change-requests", "rfcs", "decisions", "retros")
# The v3.1 default amigo cards (templates/personas/amigos/, RFC0020). Installed into a project's
# persona dir GREENFIELD ONLY - when no review seat already fills the role; never overwritten once
# present.
AMIGO_CARDS = ("engineering.md", "qa.md", "product.md")
# The machine-readable seat-role declaration the resolver keys on. Same form as
# persona_resolve._ROLE_RE - matched here, not the filename, so a person-named seat maps to a role.
_ROLE_RE = re.compile(r"<!--\s*role:\s*([a-z][a-z0-9-]*)\s*-->", re.I)

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


def _seat_roles(root: Path) -> set[str]:
    """The roles covered by the project's existing review seats (personas/seats/*.md), read from
    each card's declared `<!-- role: ... -->` field, never the filename - seats are
    named after people. Used to make the upgrade seat-aware: a seat-covered role is not a missing
    amigo, and generic cards are scaffolded greenfield only."""
    sdir = _sdlc(root) / "personas" / "seats"
    if not sdir.is_dir():
        return set()
    roles: set[str] = set()
    for p in sorted(sdir.glob("*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        m = _ROLE_RE.search(text)
        if m:
            roles.add(m.group(1).lower())
    return roles


def _legacy_amigo_cards(root: Path) -> list[str]:
    """Markdown cards still living in the retired personas/amigos/ home (any name)."""
    adir = _sdlc(root) / "personas" / "amigos"
    if not adir.is_dir():
        return []
    return sorted(p.name for p in adir.glob("*.md"))


def _missing_amigos(root: Path) -> list[str]:
    """The default amigo cards a project lacks AND no existing review seat covers.
    A card already in personas/amigos/ - default or customised - is left alone; a role already
    filled by a role-matched seat in personas/seats/ is NOT reported as a missing amigo, so the
    upgrade enriches in place rather than manufacturing a parallel set. Generic cards are therefore
    installed greenfield only - when no seat or amigo fills the role."""
    src = _amigos_source()
    dest = _sdlc(root) / "personas" / "amigos"
    covered = _seat_roles(root)  # role names: engineering / qa / product
    return [name for name in AMIGO_CARDS
            if (src / name).exists()
            and not (dest / name).exists()
            and Path(name).stem not in covered]


def _seat_amigo_overlap(root: Path) -> list[str]:
    """The roles where an existing review seat and a project amigo BOTH claim the same role - the
    silent-collision CR0120 was raised for. Named in an explicit heads-up (even in --dry-run) so
    the operator is never left to notice two parallel role systems unaided. Read-only."""
    seats = _seat_roles(root)
    if not seats:
        return []
    adir = _sdlc(root) / "personas" / "amigos"
    amigo_roles = {Path(name).stem for name in AMIGO_CARDS if (adir / name).is_file()}
    return sorted(seats & amigo_roles)


def _bump_version_text(text: str, installed: str, prev_skill: str | None,
                       today: str | None = None, schema: int | None = None) -> str:
    """Surgically bump an EXISTING .version - update schema/skill, stamp upgraded_from/upgraded_at,
    and PRESERVE every other line (e.g. an author's `created_at`). `today` is injectable
    for deterministic tests. `schema` is the value to stamp - an upgrade may only ever RAISE
    the schema stamp, so callers pass max(project effective schema, CURRENT_SCHEMA); the old
    blind CURRENT_SCHEMA constant rewrote a migrated v3 project's stamp back to 2."""
    def setline(t: str, key: str, value: str) -> str:
        pat = re.compile(rf"^{key}:.*$", re.M)
        line = f"{key}: {value}"
        return pat.sub(line, t, count=1) if pat.search(t) else t.rstrip("\n") + f"\n{line}\n"
    t = setline(text, "schema_version", str(schema if schema is not None else CURRENT_SCHEMA))
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


def _effective_schema(root: Path) -> int:
    """The project's true schema: the `.version` value if it has one, else the authoritative
    `sdlc_md.schema_version` (`.config.yaml`, default 2). A fresh project (e.g. from `init`, which
    writes `.config.yaml` but no `.version`) has its schema in `.config.yaml` only, so reading
    `.version` alone would misreport it as unknown - the source split that made a fresh v3 project
    look like it still needed the v2 to v3 migration."""
    sv, _ = _read_version(root)
    return sv if sv is not None else sdlc_md.schema_version(root)


def detect(root: Path | str) -> dict:
    """The version gap: project schema (`.version`, else `.config.yaml`) + skill vs the installed
    skill + CURRENT_SCHEMA."""
    root = Path(root)
    _, proj_skill = _read_version(root)
    proj_schema = _effective_schema(root)
    has_version = (_sdlc(root) / ".version").exists()
    installed = version_check.installed_version(version_check.skill_root())
    # An unversioned project (no `.version`) is behind (it needs the version file stamped), as is a
    # schema- or skill-behind one. project_schema now reads the authoritative config, so a fresh
    # v3 project reports schema 3 (not None) - it is still "behind" only in needing its `.version`.
    behind = (not has_version) or (proj_schema < CURRENT_SCHEMA) or version_check._gt(installed, proj_skill)
    return {"has_version_file": has_version,
            "project_schema": proj_schema, "project_skill": proj_skill,
            "current_schema": CURRENT_SCHEMA, "installed_skill": installed, "behind": behind}


def migration_walk(root: Path | str) -> list[dict]:
    """The v2 -> v3 schema migration presented as a directed sequence, not a single opaque
    step. Empty for a project already on schema 3+ (read from the authoritative `.config.yaml`,
    not just `.version` - a fresh v3 project has no `.version` yet). Each step is {step, detail};
    the schema flip itself is the deliberate `migrate_v3` id migration, never a routine auto-apply."""
    if _effective_schema(Path(root)) >= 3:
        return []
    return [
        {"step": "OPERATOR DECISION: switch the id numbering scheme?",
         "detail": "schema v3 replaces sequential ids (US0001) with collision-free ULID ids "
                   "(US-01JQK3F8) so multiple users and agents on different machines - with "
                   "different git states - can file work concurrently without minting clashing "
                   "ids. THREE choices, all fully supported, ASKED explicitly and never "
                   "auto-applied: (a) full migration - every artefact renumbered, links "
                   "rewritten, old ids kept as aliases (`migrate_v3.py apply --confirm`); "
                   "(b) FORWARD-ONLY - existing artefacts keep their sequential ids (still valid "
                   "wherever they are referenced outside the system) and only new artefacts mint "
                   "ULIDs (`migrate_v3.py adopt --confirm`); (c) stay on v2 sequential numbering "
                   "- decline, and every other upgrade step still applies."},
        {"step": "migrate_v3 dry-run",
         "detail": "if migrating fully: dry-run the id migration (preview, no writes): "
                   "`migrate_v3.py plan`"},
        {"step": "migrate_v3 apply or adopt",
         "detail": "with the operator's explicit go-ahead: `migrate_v3.py apply --confirm` "
                   "(full renumber) or `migrate_v3.py adopt --confirm` (forward-only) - both "
                   "refuse without the confirmation; the switch is never headless"},
        {"step": "re-baseline",
         "detail": "backfill/re-review the migrated artefacts: `project upgrade --apply` "
                   "(runs the same whether or not you switched numbering)"},
    ]


_OLD_PERSONA_HEADING = re.compile(r"^##+\s+(Backstory|Psychology|Decision Drivers|Personality|Interaction Guide)",
                                  re.M | re.I)


def _old_persona_signals(sd: Path) -> list[str]:
    """The legacy-persona-model signals that actually fired, each naming its own trigger so the
    operator fixes the right thing first time. Two kinds of drift surface distinctly:
    structural layout (nested dirs, the word 'amigo' in index.md) needs a dir move / index reword;
    content-model (old-model section headings) needs a content rewrite. Empty list = no signal."""
    pdir = sd / "personas"
    if not pdir.is_dir():
        return []
    signals: list[str] = []
    nested = [name for name in ("team", "stakeholders") if (pdir / name).is_dir()]
    if nested:
        dirs = ", ".join(f"personas/{n}/" for n in nested)
        signals.append(f"structural layout drift: nested persona dir(s) {dirs} present - "
                       f"move personas flat under personas/ (a content rewrite alone does not "
                       f"clear this)")
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
                signals.append("structural layout drift: index.md names the old two-category "
                               "model (team/stakeholder personas, or 'amigo') - reword index.md "
                               "(a content rewrite alone does not clear this)")
            continue
        if p.name.lower() in {"readme.md", "consult-guide.md"} or p.name.startswith("_"):
            continue
        if _OLD_PERSONA_HEADING.search(text):
            signals.append(f"content-model drift: old-model heading found in {p.name} - rewrite "
                           f"it to the Cooper model (persona-template.md) / enriched seat schema "
                           f"(amigo-template.md)")
    return signals


def _old_persona_model(sd: Path) -> bool:
    """True if any legacy-persona-model signal fired. See `_old_persona_signals` for the detail."""
    return bool(_old_persona_signals(sd))


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
        if installed is None:
            # BG0150: apply() cannot stamp a version it cannot read, and must not fabricate
            # "unknown". So audit must NOT advertise `missing-version` as an auto-fix here - it is a
            # needs-human blocker (fix the skill install), matching what apply actually does. This
            # keeps the dry-run preview honest: it never promises a stamp apply will skip.
            manual.append({"kind": "version-unresolvable",
                           "detail": "cannot read the installed skill version from its SKILL.md "
                                     "(frontmatter `version:` missing) - sdlc-studio/.version "
                                     "cannot be stamped; fix the skill install, then re-run"})
        else:
            auto.append({"kind": "missing-version", "detail": "no sdlc-studio/.version (records the skill/schema version)"})
    elif (installed and pv_skill != installed) or (pv_schema or 0) < CURRENT_SCHEMA:
        # present but stale - apply() bumps it, so the dry-run must report it too
        auto.append({"kind": "stale-version",
                     "detail": f"sdlc-studio/.version records skill {pv_skill or '?'}; bump to {installed or '?'}"})
    legacy_amigos = _legacy_amigo_cards(root)
    if legacy_amigos:
        auto.append({"kind": "legacy-amigo-home", "names": legacy_amigos,
                     "detail": f"legacy personas/amigos/ card(s) ({', '.join(legacy_amigos)}) - "
                               "migrate mechanically to personas/seats/ (the converged home; "
                               "the resolver now prefers seats/)"})
    missing_amigos = _missing_amigos(root)
    if missing_amigos:
        # RFC0028: the OFFER precedes the defaults. Ask the operator to meet their team
        # before installing generic cards - generation is recommended, defaults are opt-in.
        manual.append({"kind": "team-offer", "names": missing_amigos,
                       "detail": f"uncovered seat role(s): {', '.join(Path(n).stem for n in missing_amigos)}. "
                                 "MEET YOUR TEAM (recommended): `persona generate --team` grows "
                                 "project-native seats from the PRD/repo. Or install the generic "
                                 "defaults with `--apply --with-default-amigos`. Never auto-applied."})
    overlap = _seat_amigo_overlap(root)
    if overlap:
        # CR0120 AC4: amigos and seats both claim these roles - name the overlap (no silent
        # collision), even in --dry-run. The resolver prefers the amigo override; converge on one.
        manual.append({"kind": "seat-amigo-overlap", "names": overlap,
                       "detail": f"overlap: review seat(s) and legacy amigo card(s) both cover "
                                 f"{', '.join(overlap)} - the resolver now prefers the seats/ "
                                 "card; `--apply` migrates or retires the legacy amigos/ copy"})
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
    signals = _old_persona_signals(sd)
    if validate.check_personas(root):
        signals.append("content-model drift: a flat persona is not well-formed against the Cooper "
                       "model - rewrite it (persona-template.md)")
    if signals:
        manual.append({"kind": "personas", "signals": signals,
                       "detail": "old persona model present - " + "; ".join(signals)})
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


def apply(root: Path | str, with_reconcile: bool = False, today: str | None = None,
          with_default_amigos: bool = False) -> list[str]:
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
    # The installed skill version comes from the skill's own SKILL.md frontmatter. When that cannot
    # be read (a malformed or partial install - no `version:` line), DO NOT stamp a bogus "unknown"
    # into `.version`: that silently corrupts the metadata skill-update/migrate compare against, and
    # reads to an operator as "the version is missing". Warn loudly and SKIP the stamp
    # instead - an honest gap the operator can fix, not a fabricated value.
    installed = version_check.installed_version(version_check.skill_root())
    if installed is None:
        actions.append("WARNING: could not read the installed skill version from its SKILL.md "
                       "(frontmatter `version:` missing or unparseable) - sdlc-studio/.version was "
                       "NOT stamped. Check the skill install, then re-run `project upgrade --apply`.")
    elif not ver.exists():
        # Stamp the project's ACTUAL schema (from .config.yaml), not CURRENT_SCHEMA - a fresh v3
        # project must not have its .version mirror written as 2, which would diverge the metadata
        # from behaviour and make a spurious migration walk sticky.
        stamp_schema = _effective_schema(root)
        ver.write_text(_VERSION.format(schema=stamp_schema, prev="null",
                                       today=today, skill=installed), encoding="utf-8")
        actions.append(f"created sdlc-studio/.version (schema {stamp_schema}, skill {installed})")
    elif prev_skill != installed:
        # Never lower the stamp, and never force schema UP to CURRENT_SCHEMA: schema advancement is
        # the explicit v2 -> v3 switch's job (it rewrites `.config.yaml`), not an automatic side
        # effect of a skill-version bump. The stamp follows the project's own effective/config
        # schema, so a project that DECLINES the switch stays on its version.
        stamp = max(_effective_schema(root), sdlc_md.schema_version(root))
        ver.write_text(_bump_version_text(ver.read_text(encoding="utf-8"), installed, prev_skill,
                                          today, schema=stamp), encoding="utf-8")
        actions.append(f"updated sdlc-studio/.version (skill {prev_skill or '?'} -> {installed})")
    elif (prev_schema or 0) < sdlc_md.schema_version(root):
        # Repair a `.version` schema that lags the config's schema (the switch rewrote `.config.yaml`
        # but the stamp was not caught up) - not a blanket bump to CURRENT_SCHEMA.
        stamp = max(_effective_schema(root), sdlc_md.schema_version(root))
        ver.write_text(_bump_version_text(ver.read_text(encoding="utf-8"), installed, prev_skill,
                                          today, schema=stamp), encoding="utf-8")
        actions.append(f"repaired sdlc-studio/.version (schema -> {stamp})")
    # Converged home: migrate legacy personas/amigos/ cards into
    # personas/seats/ mechanically - a role comment is ensured (from the filename stem for the
    # default-named cards), an existing seats/ filename is never overwritten (skip + report),
    # and the emptied amigos/ dir is removed. Idempotent.
    adir = sd / "personas" / "amigos"
    migrated, skipped, role_skipped = [], [], []
    if adir.is_dir():
        sdir = sd / "personas" / "seats"
        # roles already claimed by seats/ cards - a legacy card claiming one of these
        # must never migrate into a duplicate-role collision (the lexical tiebreak
        # could flip resolution away from the authored seat: the shadowing this
        # migration exists to kill)
        claimed = set()
        if sdir.is_dir():
            for seat in sdir.glob("*.md"):
                m = _ROLE_RE.search(seat.read_text(encoding="utf-8"))
                if m:
                    claimed.add(m.group(1).lower())
        for card in sorted(adir.glob("*.md")):
            target = sdir / card.name
            if target.exists():
                skipped.append(card.name)
                continue
            text = card.read_text(encoding="utf-8")
            m = _ROLE_RE.search(text)
            role = (m.group(1).lower() if m else card.stem.lower())
            if role in claimed:
                role_skipped.append(f"{card.name} (role {role})")
                continue
            if not m:
                # role synthesised from the filename stem; a non-role name lands
                # outside the allowed set and validate seats flags it loudly
                text = f"<!-- role: {card.stem} -->\n" + text
            sdir.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            card.unlink()
            claimed.add(role)
            migrated.append(card.name)
        if migrated:
            actions.append(f"migrated {len(migrated)} card(s) from the retired personas/amigos/ "
                           f"to personas/seats/ ({', '.join(migrated)})")
        if skipped:
            actions.append(f"SKIPPED migrating {', '.join(skipped)}: personas/seats/ already has "
                           f"that filename - reconcile the pair by hand")
        if role_skipped:
            actions.append(f"SKIPPED migrating {', '.join(role_skipped)}: a personas/seats/ card "
                           f"already claims that role - retire the legacy card or reconcile the "
                           f"pair by hand (never migrated into a role collision)")
        if not any(adir.iterdir()):
            adir.rmdir()
    # The default cards are OPT-IN now - the offer to generate a project-native team
    # precedes them (see the report's team-offer entry). --with-default-amigos installs the
    # generic cards into the converged seats/ home for the still-uncovered roles only.
    missing_amigos = _missing_amigos(root)
    if missing_amigos and with_default_amigos:
        src = _amigos_source()
        dest = sd / "personas" / "seats"
        dest.mkdir(parents=True, exist_ok=True)
        installed_cards = []
        for name in missing_amigos:
            if (dest / name).exists():
                continue
            (dest / name).write_text((src / name).read_text(encoding="utf-8"), encoding="utf-8")
            installed_cards.append(name)
        if installed_cards:
            actions.append(f"installed {len(installed_cards)} default amigo card(s) to "
                           f"sdlc-studio/personas/seats/ ({', '.join(installed_cards)})")
    elif missing_amigos:
        actions.append(f"team roles uncovered ({', '.join(Path(n).stem for n in missing_amigos)}): "
                       f"run `persona generate --team` to meet your project's team, or re-run "
                       f"--apply --with-default-amigos for the generic defaults")
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


_VER_HEAD_RE = re.compile(r"^##\s*\[(\d+\.\d+\.\d+)\]")
# `### Kind`, `### Kind Words`, or `### Kind (qualifier)` - the qualifier is
# dropped but the heading still RESETS the kind, so a qualified heading never
# leaks its bullets into the previous group.
_KIND_HEAD_RE = re.compile(r"^###\s+([A-Za-z][A-Za-z ]*?)\s*(?:\([^)]*\))?\s*$")
_KIND_ORDER = ("Added", "Changed", "Fixed", "Deprecated", "Removed", "Security")
_GROUP_CAP = 6  # keep the digest a digest; the tail names what was dropped


def _changelog_path() -> Path:
    """The CHANGELOG shipped with the installed skill (install.sh copies it)."""
    return Path(version_check.skill_root()) / "CHANGELOG.md"


def changelog_digest(recorded: str | None, installed: str | None,
                     changelog: Path) -> dict:
    """The capability delta between the project's recorded skill_version
    (exclusive) and the installed version (inclusive), grouped by change kind.

    The migrator corrects files; this says what the skill can now DO. Degrades
    honestly: an absent/unparseable CHANGELOG or an unknown version range
    yields {available: False, reason} - never silence, never a crash."""
    if not recorded or not installed:
        return {"available": False,
                "reason": f"version range unknown (recorded {recorded or '?'}, "
                          f"installed {installed or '?'})"}
    if not changelog.exists():
        return {"available": False,
                "reason": f"no CHANGELOG.md shipped with the installed skill "
                          f"(expected {changelog})"}
    versions: list[str] = []
    groups: dict[str, list[str]] = {}
    extra: dict[str, int] = {}
    cur_ver: str | None = None
    cur_kind: str | None = None
    for line in changelog.read_text(encoding="utf-8").splitlines():
        vm = _VER_HEAD_RE.match(line)
        if vm:
            v = vm.group(1)
            in_range = version_check._gt(v, recorded) and not version_check._gt(v, installed)
            cur_ver = v if in_range else None
            cur_kind = None
            if in_range:
                versions.append(v)
            continue
        if cur_ver is None:
            continue
        km = _KIND_HEAD_RE.match(line)
        if km:
            cur_kind = km.group(1).capitalize()
            continue
        if cur_kind and line.startswith("- "):
            bucket = groups.setdefault(cur_kind, [])
            if len(bucket) < _GROUP_CAP:
                bucket.append(line[2:].strip())
            else:
                extra[cur_kind] = extra.get(cur_kind, 0) + 1
    if not versions:
        return {"available": False,
                "reason": f"no parseable CHANGELOG entries between "
                          f"{recorded} and {installed}"}
    return {"available": True, "versions": versions, "groups": groups, "extra": extra}


def _render_digest(digest: dict) -> list[str]:
    """The digest's text lines: known kinds in canonical order, then any
    project-specific kinds (Proposed, Migration, ...) - a captured group is
    never silently unprinted."""
    lines: list[str] = []
    known = [k for k in _KIND_ORDER if digest["groups"].get(k)]
    rest = sorted(k for k in digest["groups"] if k not in _KIND_ORDER)
    for kind in known + rest:
        lines.append(f"  {kind}:")
        for it in digest["groups"][kind]:
            lines.append(f"    - {it}")
        if digest["extra"].get(kind):
            lines.append(f"    (+{digest['extra'][kind]} more - see CHANGELOG.md)")
    return lines


def new_advisory_lanes(recorded: str | None, installed: str | None) -> list[dict]:
    """Gate lanes that arrived in the version gap and read not-run when their
    evidence is absent - each named with its one-line baseline pointer, so an
    accidental discovery becomes a directed next step."""
    import gate
    out: list[dict] = []
    if not recorded or not installed:
        return out
    for name, meta in sorted(gate.ADVISORY_WHEN_ABSENT.items()):
        since = meta.get("since")
        if since and version_check._gt(since, recorded) and not version_check._gt(since, installed):
            out.append({"lane": name, "since": since, "baseline": meta["baseline"]})
    return out


_REBASELINE_BUCKETS = ("backfill", "re-review", "residual")
_VERIFY_LINE = re.compile(r"(?m)^\s*-\s*\*\*Verify:\*\*")
_AC_SECTION = re.compile(r"(?ms)^##\s+Acceptance Criteria\b(.*?)(?=^##\s|\Z)")


def _ac_has_missing_verify(text: str) -> bool:
    """True when a story declares ACs but at least one lacks a `Verify:` line (residual -
    the tooling can name the gap but authoring the verifier is judgement). Verify lines are
    counted WITHIN the Acceptance Criteria section only, so a stray `Verify:` line in a Notes
    or Test-Plan section cannot mask a genuinely missing AC verifier (the under-report
    direction)."""
    acs = sdlc_md.count_acs(text)
    m = _AC_SECTION.search(text)
    verifies = len(_VERIFY_LINE.findall(m.group(1))) if m else 0
    return acs > 0 and verifies < acs


def rebaseline(root: Path | str) -> dict:
    """Census every NON-TERMINAL artifact against the capability delta, per artifact, bucketed.
    Read-only, deterministic (no model judgement - TRD ADR-006). Era-gated: a no-op (all buckets
    empty) unless the project is schema v3 (the one adoption watermark).

    Buckets: `backfill` (mechanical stamps computable now, e.g. a missing `Difficulty`),
    `re-review` (matches a gate's trigger but lacks the verdict, e.g. a spec-derived story with
    no plan-review verdict), `residual` (judgement gaps the tooling can only name)."""
    root = Path(root)
    out: dict = {b: [] for b in _REBASELINE_BUCKETS}
    if not sdlc_md.is_schema_v3(root):
        return out
    import plan_review  # lazy: pulls route/critic; keep them off the cold upgrade path
    import critic
    for type_ in ("story", "cr", "bug"):
        vocab = sdlc_md.status_vocab(type_, root)
        terminal = sdlc_md.terminal_statuses(type_)
        for p in sdlc_md.artifact_files(type_, root):
            text = p.read_text(encoding="utf-8")
            status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"), vocab)
            if status in terminal:
                continue                                   # completed transitions untouched
            rid = sdlc_md.extract_record_id(p.stem) or p.stem

            def _add(bucket, cap):
                out[bucket].append({"id": rid, "type": type_, "capability": cap,
                                    "path": str(p)})

            if not _has_field(text, "Difficulty"):
                _add("backfill", "difficulty")             # route.estimate can stamp it on --apply
            if type_ == "story":
                if plan_review.triggers(text, root, p)["fired"]:
                    v = critic.verdict_for(root, rid, phase="plan-review")
                    ok = bool(v) and v["verdict"] == critic.APPROVE and critic.is_independent(v)
                    if not ok and not plan_review.override(text):
                        _add("re-review", "plan-review")
                if _ac_has_missing_verify(text):
                    _add("residual", "ac-verify")
    for b in out:
        out[b].sort(key=lambda e: e["id"])
    return out


def rebaseline_apply(root: Path | str) -> list[str]:
    """Perform ONLY the mechanical `backfill` bucket (never `re-review`/`residual`): stamp a
    deterministic, computable-now field on a non-terminal artifact that lacks it. Today that is
    a `> **Difficulty:**` stamp from `route.estimate`. Idempotent - a stamped unit is no longer
    in the backfill bucket, so a second run does nothing. No fabricated history: only fields
    deterministically computable from the artifact NOW are written; no back-dated telemetry or
    metrics rows are invented. Returns the actions taken. A no-op unless schema v3."""
    root = Path(root)
    if not sdlc_md.is_schema_v3(root):
        return []
    import route
    actions: list[str] = []
    for e in rebaseline(root)["backfill"]:
        if e["capability"] != "difficulty":
            continue
        p = Path(e["path"])
        try:
            band = route.estimate(root, p)["difficulty_band"]
        except Exception:  # noqa: BLE001 - a difficulty read must never break the apply pass
            continue
        # newline="" preserves the file's existing terminators (universal-newline mode would
        # translate CRLF->LF on read, rewriting the whole file); only the inserted line is
        # added. open() is used because Path.read_text/write_text only grew a newline=
        # keyword in Python 3.13 and the floor is 3.10.
        with open(p, encoding="utf-8", newline="") as fh:
            text = fh.read()
        new_text, ok = _stamp_after_status(text, "Difficulty", band)
        if ok:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(new_text)
            actions.append(f"stamped Difficulty: {band} on {e['id']}")
    return actions


def _has_field(text: str, field: str) -> bool:
    """True when a `> **field:**` metadata line is present, case-insensitively - so a
    non-canonical `> **difficulty:**` is recognised and not duplicated."""
    return bool(re.search(rf"(?im)^>\s*\*\*{re.escape(field)}:\*\*", text))


def _stamp_after_status(text: str, field: str, value: str) -> tuple[str, bool]:
    """Insert `> **field:** value` immediately after the Status metadata line (idempotent - a
    no-op if the field already exists, any case). Preserves the file's existing line endings
    (only the inserted line is added; the rest is byte-unchanged). Returns (text, changed)."""
    if _has_field(text, field):
        return text, False
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    for i, ln in enumerate(lines):
        if re.match(r"^>\s*\*\*Status:\*\*", ln):
            lines.insert(i + 1, f"> **{field}:** {value}{nl}")
            return "".join(lines), True
    return text, False


def rebaseline_report(root: Path | str) -> list[str]:
    """Render the re-baseline census as report lines; an empty bucket prints an explicit
    `none` (never silently omitted, so the operator sees the gate was checked)."""
    r = rebaseline(root)
    lines = ["Re-baseline - non-terminal artifacts vs the capability delta:"]
    for b in _REBASELINE_BUCKETS:
        lines.append(f"  {b}:")
        if not r[b]:
            lines.append("    - none")
        else:
            for e in r[b]:
                lines.append(f"    - {e['id']} ({e['type']}): {e['capability']}")
    return lines


def cmd_upgrade(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if not _sdlc(root).is_dir():
        print(f"error: no sdlc-studio/ under {root} - not an sdlc-studio project", file=sys.stderr)
        return 1
    d = detect(root)
    a = audit(root)
    has_work = d["behind"] or bool(a["auto"]) or bool(a["manual"])
    applied: list[str] = []
    # apply whenever there is safe work, even if "current"; --with-default-amigos is
    # itself requested work (the documented decline path must never be a silent no-op)
    if args.apply and (d["behind"] or a["auto"] or args.with_default_amigos):
        applied = apply(root, with_reconcile=args.with_reconcile,
                        with_default_amigos=args.with_default_amigos)
    if args.apply and sdlc_md.is_schema_v3(root):   # mechanical re-baseline backfill (schema v3)
        applied += rebaseline_apply(root)
    digest = (changelog_digest(d["project_skill"], d["installed_skill"], _changelog_path())
              if d["behind"] else None)
    lanes = (new_advisory_lanes(d["project_skill"], d["installed_skill"])
             if d["behind"] else [])
    walk = migration_walk(root)
    if args.format == "json":
        print(json.dumps({"detect": d, "audit": a, "applied": applied,
                          "capability_delta": digest, "new_advisory_lanes": lanes,
                          "migration_walk": walk}, indent=2))
        return 0
    sk = d["installed_skill"] or "?"
    if not has_work:
        print(f"project upgrade: already current (schema {d['project_schema']}, skill {d['project_skill'] or '?'}).")
        return 0
    if d["behind"]:
        print(f"project upgrade: BEHIND - project schema {d['project_schema']} / skill "
              f"{d['project_skill'] or 'unknown'} vs skill {sk} (schema {CURRENT_SCHEMA}).\n")
        if digest and digest["available"]:
            print(f"Changed since {d['project_skill']} (recorded) -> {sk} (installed):")
            for line in _render_digest(digest):
                print(line)
        elif digest:
            print(f"capability delta unavailable ({digest['reason']})")
        for lane in lanes:
            print(f"  new advisory gate lane '{lane['lane']}' (since {lane['since']}): "
                  f"reports not-run until you {lane['baseline']}")
        if digest or lanes:
            print()
    else:
        print(f"project upgrade: version current (skill {d['project_skill'] or '?'}), but conventions drift:\n")
    if walk:
        print("Schema v2 -> v3 migration walk (run in order; the schema flip is the deliberate "
              "migrate_v3 id migration, never an auto-apply):")
        for i, s in enumerate(walk, 1):
            print(f"  {i}. {s['step']}: {s['detail']}")
        print()
    print("Auto-correctable (apply with --apply):")
    for f in a["auto"]:
        print(f"  [auto]   {f['detail']}")
    print("\nNeeds judgement (do by hand - reported, not filed as CRs):")
    for f in a["manual"]:
        print(f"  [manual] {f['detail']}")
    if sdlc_md.is_schema_v3(root):   # the per-artifact re-baseline census (schema v3 only)
        print()
        for line in rebaseline_report(root):
            print(line)
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
    p.add_argument("--with-default-amigos", dest="with_default_amigos", action="store_true",
                   help="install the generic default seat cards for uncovered roles (opt-in: "
                        "the recommended path is `persona generate --team`)")
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
