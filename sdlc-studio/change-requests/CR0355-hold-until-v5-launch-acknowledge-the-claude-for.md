# CR-0355: HOLD UNTIL v5 LAUNCH - acknowledge the Claude for Open Source programme in the README

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** README.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

DO NOT APPLY BEFORE THE v5 RELEASE. This is a user-facing README change and must ship with v5, not before it. A release freeze is in force and the repo lands work unreleased on main; applying this early puts a sponsorship acknowledgement in front of users of a version that has not launched.

The project was accepted into the Claude for Open Source programme (six months of Claude Max). Acknowledging it in the README at the v5 launch.

TWO THINGS CHECKED BEFORE FILING, both of which shape the work:

1. The programme page states NO attribution, badge, logo or wording requirements. Nothing is owed. This is voluntary, so the project chooses the form and the tone.

2. Anthropic's terms require PRIOR WRITTEN PERMISSION for third-party use of its name or logos in any way implying affiliation, endorsement or sponsorship, with requests to <marketing@anthropic.com>. A logo in the README is squarely that. Plain factual prose - that the project received support from the programme - is a different matter and is simply true. So the text can ship at v5 regardless; the LOGO ships only if permission comes back in time, and its absence must not block the release.

## Impact

Nobody is harmed if this never happens - nothing is owed. Getting it wrong the other way does carry cost: a logo used without permission is a trademark issue, and a sponsorship banner above the fold reads as vendor marketing on a project whose positioning is engineering discipline. The README's opening is doing positioning work already.

## Acceptance Criteria

- [ ] NOT APPLIED until the v5 release is being cut - this CR stays open through the freeze and is picked up as part of the v5 release checklist, never as a drive-by edit
- [ ] a short Acknowledgements section near the foot of the README beside the licence, not in the masthead and not above the fold
- [ ] the text is factual and states what is true: the project received support from the Claude for Open Source programme. Tone is the operator's call, not the drafting agent's
- [ ] the Claude logo is included ONLY if written permission has been obtained from <marketing@anthropic.com> by the time v5 is cut; without it the section ships as text alone and the release is not delayed for it
- [ ] whether to state that the project is developed WITH Claude Code is an explicit operator decision recorded before the release, not assumed - it is true and relevant to a skill for coding agents, and it also invites the reading that the tool only works for its authors

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
