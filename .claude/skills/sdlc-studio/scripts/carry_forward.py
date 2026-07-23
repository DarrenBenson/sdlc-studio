#!/usr/bin/env python3
"""Carry-forward review policy (EP0113 / CR0404).

A REJECT blocks: `conformance.sprint_covers_independently` accepts a sprint-level review as
evidence only on an APPROVE, so there is no path that says "these findings are real, they are
filed as bugs, the sprint carries on". Some teams want the loop to run until it is clean; some
want the findings on the backlog and the sprint shipped. The project supported only the first
and did not say so.

This adds the second as a DECLARED policy. Under `review.policy: carry-forward` a REJECT no
longer blocks, provided every finding is FILED as an artefact or explicitly WAIVED with a
reason - the same fail-forward idiom `reference-review.md` already mandates for a missing
review leg, and forbids resolving by narrative downgrade. The close records which policy was
in force and lists the findings carried, and a carried finding names the units it was found
against so it cannot be lost when the sprint closes.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import config  # noqa: E402

#: The policies a project may declare. `block` is today's behaviour and the default, so an
#: upgrading project's close does not change. An unrecognised value is REFUSED, never
#: defaulted: a typo that quietly selected carry-forward would ship a sprint nobody meant to.
POLICIES = ("block", "carry-forward")
POLICY_KEY = "review.policy"


class PolicyError(ValueError):
    """A review-policy violation - an unrecognised policy, or a finding neither filed nor
    waived under carry-forward."""


def review_policy(root: Path | str) -> str:
    """The project's declared review policy. `block` unless `review.policy: carry-forward` is
    set. An unrecognised value is refused, naming the accepted set (US0332 AC3)."""
    try:
        val = config.get(root, POLICY_KEY, "block")
    except Exception:  # noqa: BLE001 - config must never break the gate
        val = "block"
    norm = str(val).strip().lower()
    if norm not in POLICIES:
        raise PolicyError(
            f"unrecognised review policy {val!r}. Accepted: {POLICIES}. A policy is refused "
            f"rather than defaulted, because a typo that quietly selected carry-forward would "
            f"ship a sprint nobody meant to ship")
    return norm


def _resolves(root: Path | str, ref: str) -> bool:
    """Does this finding reference resolve to an artefact on disk? A carried finding must be a
    real filed artefact, not a sentence."""
    return sdlc_md.find_by_id(root, ref) is not None


#: A narrative downgrade: resolving a finding by restating it as an observation, or downgrading
#: a required leg to optional, rather than filing or waiving it. Forbidden in both directions,
#: exactly as reference-review.md forbids it for a missing leg.
_DOWNGRADE_MARKERS = ("downgrade", "just an observation", "not really a finding",
                      "reword as optional", "no longer required", "soften to")


def is_narrative_downgrade(resolution: str) -> bool:
    """True when a finding's resolution is a narrative downgrade rather than a file-or-waive.
    A carried finding gets exactly two exits and no third (US0333 AC3)."""
    low = " ".join(str(resolution or "").split()).lower()
    return any(marker in low for marker in _DOWNGRADE_MARKERS)


def validate_carried(root: Path | str, findings) -> None:
    """Refuse a carry-forward close unless EVERY finding is filed or explicitly waived.

    A finding is a dict: {ref, units, waiver} where `ref` is the filed artefact id (or empty
    when waived), `units` are the units it was found against, and `waiver` is a non-empty reason
    when the finding is waived rather than filed. Raises PolicyError naming the first offender.

    - a finding neither filed nor waived blocks the close, so the policy changes WHAT blocks -
      the verdict no longer does, the unfiled finding still does (US0333 AC1);
    - a waiver with no reason is refused (US0333 AC2);
    - a resolution that is a narrative downgrade is refused (US0333 AC3);
    - a filed finding that names no unit is refused, so it cannot become an orphan when the
      sprint closes (US0335 AC1).
    """
    for f in findings:
        ref = str(f.get("ref", "")).strip()
        waiver = str(f.get("waiver", "")).strip()
        units = [u for u in (f.get("units") or []) if str(u).strip()]
        if is_narrative_downgrade(waiver) or is_narrative_downgrade(f.get("resolution", "")):
            raise PolicyError(
                f"a carried finding may be FILED or explicitly WAIVED - not resolved by "
                f"narrative downgrade ({waiver or f.get('resolution')!r}). reference-review.md "
                f"forbids the same for a missing leg (US0333 AC3)")
        if ref:
            if not _resolves(root, ref):
                raise PolicyError(
                    f"carried finding names {ref!r}, which resolves to no artefact on disk - a "
                    f"carried finding must be a real filed artefact, not a sentence (US0333 AC1)")
            if not units:
                raise PolicyError(
                    f"carried finding {ref!r} names no unit it was found against; it would "
                    f"become an orphan when the sprint closes (US0335 AC1)")
            continue
        if not waiver:
            raise PolicyError(
                "a carried finding is neither filed (no `ref`) nor waived (no `waiver` reason). "
                "Under carry-forward every finding is filed or explicitly waived - the verdict "
                "no longer blocks, but an unhandled finding still does (US0333 AC1/AC2)")


def reject_carries_forward(root: Path | str, findings) -> bool:
    """Does a REJECT carry forward rather than block? True only under the carry-forward policy
    AND when every finding is validly filed or waived. Raises PolicyError otherwise, so the
    caller learns WHY it still blocks (US0332 AC2)."""
    if review_policy(root) != "carry-forward":
        return False
    validate_carried(root, findings)
    return True


def carried_finding_units(root: Path | str, ref: str) -> list[str]:
    """The units a carried finding names, read from the artefact on disk. Because it is read
    from the finding's own file - not from the run state - the link survives the close of the
    sprint that produced it and the units going terminal (US0335 AC2): closing a run does not
    strand a finding filed against it."""
    hit = sdlc_md.find_by_id(root, ref)
    if not hit:
        return []
    text = sdlc_md.read_text_safe(hit[0])
    found = sdlc_md.extract_field(text, "Found-against") or sdlc_md.extract_field(text, "Affects-units")
    if not found:
        return []
    return [u.strip() for u in found.split(",") if u.strip()]
