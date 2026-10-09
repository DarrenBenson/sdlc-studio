# CR-0613: Make a clone that cannot run the gates say so at setup, not 50 minutes into a push

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0278
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** tools/enable-hooks.sh, AGENTS.md, .githooks/pre-push, tools/tests/test_pre_push_hook.py
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. Push gate runs on 65e36b98 and fb1ce886.
> **Date:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:08Z

## Summary

This clone ran with its hooks off (no `core.hooksPath`), which is how two commits reached main unchecked on 2026-10-05/06. Once enabled, the push gate needed pytest, pytest-xdist and coverage in the system interpreter and markdownlint from `npm ci`; each absence surfaced only as a refused gate, one after a 52-minute full suite, and the first run's estimate said 'about five minutes'. `tools/enable-hooks.sh` installs the hooks but checks none of the prerequisites, and nothing tells a session its clone's hooks are off.

## Impact

Every contributor and agent on a fresh clone or a new machine; the cost is commits that bypass the gates and gate runs lost to a missing tool.

## Acceptance Criteria

- [ ] `enable-hooks.sh` names each missing gate prerequisite (pytest, pytest-xdist, coverage, markdownlint, gh) with the command that installs it
- [ ] A session can tell in one command that a clone's hooks are off
- [ ] The pre-push gate refuses in seconds, before the suite, when a prerequisite it needs is missing, and its first-run estimate is not a fixed five minutes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Raised |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- At the push, an externally-managed interpreter with no pip and a refusing-class gap: refuse (fail-closed) with the route that works there, or name it and run the gate anyway? The panel recommends refusing wherever the machine is, which is what the pre-push story drafts.
- CR0613's second criterion: close it with the evidence above. Whether to also gate 'a session ran `status`' (for example a pre-commit lane failing when core.hooksPath is unset, which cannot gate itself from a hook that is not enabled) is the operator's call; the panel does not recommend adding it here, and nor does this draft.
