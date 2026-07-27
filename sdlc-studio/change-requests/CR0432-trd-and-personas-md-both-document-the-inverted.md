# CR-0432: TRD and personas.md both document the inverted porting flow: installed copy as back-port source vs the shipped forward-p

> **Status:** In Progress
> **Decomposed-into:** EP0168
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** sdlc-studio/trd.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Both files state production fixes land first in the installed copy and back-port to the repo, while current doctrine is the exact reverse: fixes land in the dev repo and mirror out via tools/forward-port.sh, whose --check fails on drift. personas.md additionally carries other checkable stale facts (SKILL.md '~195 lines' vs 270; 'only the scripts have unit tests' vs the tools/tests suite), untouched since 2026-06-20.

## Impact

Both files state production fixes land first in the installed copy and back-port to the repo, while current doctrine is the exact reverse: fixes land in the dev repo and mirror out via tools/forward-port.sh, whose --check fails on drift. personas.md additionally carries other checkable stale facts (SKILL.md '~195 lines' vs 270; 'only the scripts have unit tests' vs the tools/tests suite), untouched since 2026-06-20.

## Acceptance Criteria

- [ ] Rewrite trd.md section 8 and the personas.md Skill Maintainer card to the forward-port doctrine (repo is source, installed copy is the derived mirror, forward-port.sh --check is the drift gate), refreshing the other stale facts in the same pass.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Raised |
