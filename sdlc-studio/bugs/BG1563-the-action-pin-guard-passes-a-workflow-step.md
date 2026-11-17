# BG1563: The action-pin guard passes a workflow step that uses a mutable docker image tag

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/check_action_pins.sh, tools/tests/test_check_action_pins.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at tools/check_action_pins.sh lines 24-26 (the grep collector that extracts only uses values containing an at sign)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:29:45Z

## Summary

The guard tools/`check_action_pins.sh` exists to ensure every Action in a workflow is pinned to an immutable reference. Its collector at lines 24 to 26 only extracts `uses:` values that contain an at sign, so a step that uses a docker image by tag, which has no at sign, is never collected. A workflow with such a step passes, and the guard prints that all Actions are pinned to commit SHAs, although a tag can be repointed, which is the threat the script's header describes. The reverse also holds: an image pinned by sha256 digest would be reported as unpinned, because only a 40-hex commit SHA is accepted. The impact is latent, since the repository's workflows use no docker steps today, but the guard would not stop one being added.

## Steps to Reproduce

1. Create a throwaway directory holding .github/workflows/x.yml with two steps: one checkout Action pinned to a 40-hex commit SHA, and one step whose uses value is a docker reference to the alpine image at its latest tag.
2. Run tools/`check_action_pins.sh` with the throwaway directory as its argument.
3. Observe that it prints that all Actions are pinned to commit SHAs and exits 0.
4. Change the docker step to reference the image by a sha256 digest and run the guard again: it reports the digest-pinned step as unpinned.

## Proposed Fix

Collect every `uses:` value, not only those containing an at sign. Skip local references that begin with a dot and a slash. Require a 40-hex commit SHA after the at sign for repository Actions and reusable workflows, and a sha256 digest of 64 hex characters for docker references; report anything else, including a docker reference by tag or with no tag. Add cases to tools/tests/`test_check_action_pins.py`: a docker reference by tag fails, a docker reference by digest passes, a local reference passes, and the existing SHA-pinned and tag-pinned Action cases still behave as before.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The guard tools/`check_action_pins.sh` exists to ensure every Action in a workflow is pinned to an immutable reference.
- [ ] **AC2** The proposed fix lands, pinned by a test: Collect every `uses:` value, not only those containing an at sign.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
