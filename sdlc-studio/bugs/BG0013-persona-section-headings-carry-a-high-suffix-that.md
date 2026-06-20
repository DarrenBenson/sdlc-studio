# BG-0013: Persona section headings carry a [HIGH] suffix that breaks every story anchor and the review_prep persona-usage oracle

> **Status:** Fixed
> **Severity:** Medium
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

All four persona H2 headings end with a confidence marker (e.g. '## Orchestrator / Operator  [HIGH]'), so GitHub slugs include '--high'; all five story persona links point at the suffix-free slug and resolve to a 404, and review_prep.persona_usage() captures the full heading (including [HIGH]) so its 'defined' names can never match any reference.

## Problem

personas.md:31/128 headings carry trailing '  [HIGH]'. Story links target #orchestrator--operator and #ai-agent-executing-the-skill (US0001-US0005:27), which omit the suffix and so do not resolve - every persona back-link in the story layer is broken (check_links.py flags them among the 25). review_prep.py:82-85 regex ^##\s+(.+?)\s*$ captures 'Orchestrator / Operator  [HIGH]' including the tag, so the persona-usage unused-signal is structurally guaranteed never to match.

## Proposed Fix

Strip the [HIGH]/[MEDIUM] confidence markers from the persona H2 headings (move them to a body line, e.g. '> Confidence: HIGH'). This single fix makes the existing story anchors resolve and gives review_prep clean role-only names. (If headings cannot change, strip a trailing \s*\[(HIGH|MEDIUM|LOW)\]\s*$ in persona_usage() and update the five story anchors - but cleaning the headings is the durable fix.)

## Evidence

personas.md:31 '## Orchestrator / Operator  [HIGH]' vs stories/US0001-reconcile-census-autofix.md:27 link '#orchestrator--operator' (and review_prep.py:83 regex capturing the full heading)

## Impact

Persona traceability from every story is dead on click, the Story Quality 'persona reference valid' check is only nominally met, and the persona-usage oracle's defined names are permanently unusable for matching.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: traceability) |
