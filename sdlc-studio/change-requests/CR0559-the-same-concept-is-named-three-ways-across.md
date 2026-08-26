# CR-0559: the same concept is named three ways across the toolchain and twice inside one script, so every invocation is a guess the caller pays for in a refusal

> **Status:** Proposed
> **Priority:** Medium
> **Type:** enhancement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/decisions.py, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_decisions.py
> **Evidence:** Hit five times while closing RUN-01M0WCCG on 2026-08-25 and 2026-08-26. Flag surface measured by reading --help for six verbs across four scripts; the two document-key refusals are quoted from the tools' own messages.
> **Date:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A unit id is `--unit` in `critic` (brief, record, repair, signoff), in `mutation register`, and in `verify_ac depth` and `verify_ac testplan`. It is `--id` and `--ids` in `transition set`. And `verify_ac run` - the same script as depth and testplan - takes `--story`, `--id` and `--ids` and REFUSES `--unit`. Measured across the six verbs on 2026-08-26. The `--fields-file` surface diverges from the flag surface in the same way: `file_finding file` offers a `--ac` flag while its document key is `acs`, and offers `--option` while the key is `options`, so a document written from the --help output is refused; `decisions add` accepts `--status` as a flag and refuses `status` as a document key, with the message `known fields are decision, rationale`. Each refusal is clear and each is a round trip, and they land on the recommended path rather than the deprecated one.

## Impact

These are the deterministic entry points the doctrine tells every consuming project and every headless agent to call instead of hand-editing. An agent picks a flag by analogy with the sibling verb it just used, so an inconsistent surface converts each call into a guess, a refusal and a retry. It is a tax on exactly the behaviour the project is trying to make the default, and it is paid most heavily by the callers least able to read the source.

## Acceptance Criteria

- [ ] Given any verb that identifies a unit, when it is invoked with `--unit <id>`, then it is accepted - including `verify_ac run`, where it is refused today
- [ ] Given a `--fields-file` document whose keys are spelled as the verb's own flags, when it is read, then those keys are accepted rather than refused as unknown - measured on `file_finding file` with `ac` and `option`, and on `decisions add` with `status`
- [ ] Given the canonical name is chosen, when the deprecated alias is used, then it still works and says once that it is deprecated - a rename that breaks existing callers costs more than the inconsistency it removes
- [ ] Given the surface reference is regenerated, then it names the accepted flags and document keys per verb, so the divergence cannot silently return

## Recommendation

Option 2, with option 1 as its first step. `--unit` is the majority name and the one the doctrine's prose uses, so it should be canonical; `--id` survives as a hidden alias. Do `verify_ac` first - a single script answering two names for one concept across three verbs is the instance that costs most, because a caller who has just used `depth --unit` has every reason to expect `run --unit` to work. For the document keys, accept the flag spelling as an alias rather than renaming the key, since documents already written should keep parsing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Raised |
