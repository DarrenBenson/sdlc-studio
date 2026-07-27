# CR-0425: The mandated creation path bypasses the persona registry entirely: registry personas unconsulted since the day the layer

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-07-27)
> **Decomposed-into:** EP0166
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/personas/index.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The 2026-07-16 fix made story create/generate resolve the registry first, but the mandated deterministic path (artifact.py new/batch) treats --persona as optional free text with no registry lookup, so of 246 stories created since, zero reference Maya, Jonah, or any registry persona - the RV0010 condition ('registry personas unused') recurs at larger scale and the registry describes a design target nothing downstream consumes.

## Impact

The 2026-07-16 fix made story create/generate resolve the registry first, but the mandated deterministic path (artifact.py new/batch) treats --persona as optional free text with no registry lookup, so of 246 stories created since, zero reference Maya, Jonah, or any registry persona - the RV0010 condition ('registry personas unused') recurs at larger scale and the registry describes a design target nothing downstream consumes.

## Acceptance Criteria

- [ ] Make artifact.py resolve --persona against personas/index.md, defaulting to the declared Primary when omitted and warning (or refusing under strict) on a name not in the registry, so the pipeline that actually mints every story performs persona selection.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |

## Amigo Consult

_Consulted 2026-07-27: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Should a story naming the Negative persona (Trevor) be refused outright, or warned about as a design-target signal?
