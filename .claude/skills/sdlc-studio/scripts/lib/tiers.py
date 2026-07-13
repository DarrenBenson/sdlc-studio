"""Template tiers, and the section deficit the planning tier defers.

One authority, shared by the creator (`artifact`), the validator, the transition gate and the
conformance backstop - so the gate cannot be told a different story from the thing that wrote
the artefact.

The design lesson this module encodes: **do not trust a marker the subject can rewrite; check
the thing you actually care about.** The tier stamp is a CLAIM. What matters is whether the
artefact carries the sections implementation needs. So:

* `planning`, or any tier outside the known set, is unpromoted - fail closed, because a typo'd
  tier that read as "not planning" would silently switch off both the gate and its backstop.
* a `full` claim is CHECKED against the sections. Nothing legitimately carries a `full` stamp
  except an artefact `promote` built (creation stamps only `planning`), so verifying the claim
  costs no existing artefact and closes the forged-stamp route.
* an artefact with NO stamp is not judged by default. This is not an oversight - it is the
  measured boundary: 103 of this repo's 119 stories carry none of the deferred sections and
  reach Done today, and an unstamped bare story is structurally identical to them. Refusing it
  by default would refuse them. `quality.require_full_sections: true` drops the stamp from the
  decision entirely and judges every artefact on its sections - the structural close, as a
  project's choice rather than a silent breaking change.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from . import sdlc_md

MINIMAL, PLANNING, FULL = "minimal", "planning", "full"
TEMPLATE_TIERS = (MINIMAL, PLANNING, FULL)
TIER_FIELD = "Template"

# The types with a lean tier: the two whose full template has a structural floor a planning
# artefact cannot get under. Every other type's minimal scaffold is already that lean.
TIERED_TYPES = ("story", "epic")

_SKILL_ROOT = Path(__file__).resolve().parent.parent.parent  # lib/ -> scripts/ -> skill root
_HEADING_RE = re.compile(r"^##\s+(.*)$", re.M)


def core_template(type_: str) -> Path:
    return _SKILL_ROOT / "templates" / "core" / f"{type_}.md"


def planning_template(type_: str) -> Path:
    return _SKILL_ROOT / "templates" / "core" / f"{type_}-planning.md"


def _headings(text: str) -> list[str]:
    return [h.strip().lower() for h in _HEADING_RE.findall(text)]


@lru_cache(maxsize=None)
def deferred_sections(type_: str) -> tuple[str, ...]:
    """The `## ` sections the full template mandates that the planning tier defers.

    Derived from the two templates rather than hardcoded, so editing a template cannot leave
    the gate enforcing a list nobody maintains. Empty for a type with no planning tier, which
    is what makes every other type provably unaffected by the gate."""
    core, plan = core_template(type_), planning_template(type_)
    if not core.exists() or not plan.exists():
        return ()
    deferred = set(_headings(plan.read_text(encoding="utf-8")))
    return tuple(h for h in _headings(core.read_text(encoding="utf-8")) if h not in deferred)


def tier_of(text: str) -> str | None:
    """The artefact's declared tier, lowercased - or None when it carries no stamp."""
    return (sdlc_md.extract_field(text, TIER_FIELD) or "").strip().lower() or None


def missing_sections(text: str, type_: str) -> list[str]:
    """The deferred sections this artefact does not carry."""
    have = set(_headings(text))
    return [s for s in deferred_sections(type_) if s not in have]


def require_full_sections(repo_root) -> bool:
    """`quality.require_full_sections` - judge EVERY artefact on its sections, stamp or no
    stamp. Off by default (see the module docstring for the measurement behind that)."""
    return bool(sdlc_md.project_override(repo_root, "quality.require_full_sections", False))


def promotion_deficit(text: str, type_: str, strict: bool = False) -> str | None:
    """Why this artefact is not ready for an implementation status, or None if it is.

    `strict` is the project-wide `quality.require_full_sections` policy: judge on sections
    alone and ignore the stamp entirely."""
    if type_ not in TIERED_TYPES or not deferred_sections(type_):
        return None
    tier = tier_of(text)
    missing = missing_sections(text, type_)
    remedy = ("Promote it: `artifact.py promote --id <id> --to full` adds the section "
              "scaffolds (as empty `{{placeholder}}` blocks for you to fill - promotion gives "
              "you the headings and the obligation, not the content)")
    if not strict:
        if tier is not None and tier not in TEMPLATE_TIERS:
            return (f"its template tier '{tier}' is not one of {', '.join(TEMPLATE_TIERS)}, so it "
                    f"is treated as unpromoted (fail closed - a typo must never be the thing "
                    f"that switches this gate off). {remedy}")
        if tier == PLANNING:
            return (f"it is a planning-tier scaffold: it defers {len(deferred_sections(type_))} "
                    f"sections the full template carries ({', '.join(deferred_sections(type_))}). "
                    f"{remedy}")
        if tier == FULL and missing:
            # The stamp is a claim, and here it is false. Creation never writes a `full` stamp -
            # only `promote` does, and it adds the sections - so a `full` claim over missing
            # sections means the stamp was rewritten without the work.
            return (f"it claims the `full` tier but is missing {len(missing)} of the sections "
                    f"that tier carries ({', '.join(missing)}). A stamp is a claim, not the "
                    f"work. {remedy}")
        return None
    if missing:
        return (f"quality.require_full_sections is set and it is missing {len(missing)} "
                f"section(s) ({', '.join(missing)}). {remedy}")
    return None
