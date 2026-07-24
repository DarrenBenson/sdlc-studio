# BG0290: refine's ungroomed placeholder fails validate's no-ac check, so refine produces a story that cannot be committed

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Severity:** High
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit planning RUN-01KYA8CF. `refine apply --request CR0413 --epic-title ...` minted US0413 and
US0414 with an Acceptance Criteria section holding only the ungroomed marker:

```markdown
## Acceptance Criteria

> **Ungroomed - acceptance criteria are a grooming placeholder** - author each criterion and its
> Verify check against this story's slice while grooming, before it is planned to Done.
```

That is refine's own designed output for an ungroomed story, and `conformance.story_is_ungroomed`
reads it correctly. But `validate` rejects the same file:

```text
ERROR US0413: [no-ac] story has no acceptance criteria (`### ACn`, `- **ACn:**`, or a populated
`## Acceptance Criteria` section)
```

So the artefact gate refuses to let a story refine just created be committed. The pre-commit
hook blocks, and there is no groom-before-commit path because the story must exist to be groomed.

Two guards hold different definitions of the same state. `conformance` says "ungroomed, and that
is a legitimate status before the Definition-of-Ready bar"; `validate` says "no acceptance
criteria, which is an error". Both are shipped, both run in the same gate, and they disagree.

Note the asymmetry that hid this: the same command with `--into EP0156` seeded placeholder ACs
with real `### ACn` headings, which validate accepts. So four of the six stories refined in this
session passed and two failed, from the same tool in the same minute.

## Impact

Every refine that mints a new epic. The failure lands on the commit, not the refine, so the tool
reports success and the gate blames the artefact.

## Acceptance Criteria

### AC1: the ungroomed marker satisfies validate

- **Given** a story whose Acceptance Criteria section holds only `sdlc_md.UNGROOMED_AC_TOKEN`
- **When** `validate check` reads it
- **Then** it is not a `no-ac` error - an explicitly-marked ungroomed story is a known pre-Ready state, not a malformed artefact; a story with an EMPTY section and no marker is still an error
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::UngroomedMarkerTests::test_the_ungroomed_marker_is_not_a_no_ac_error

### AC2: the two guards read the same definition

- **Given** `conformance.story_is_ungroomed` and validate's AC check
- **When** both are asked about the same story text
- **Then** neither can call a story ungroomed-and-fine while the other calls it malformed - the ungroomed test is imported from one place, not restated in two
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::UngroomedMarkerTests::test_validate_and_conformance_agree_on_every_shipped_story

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
