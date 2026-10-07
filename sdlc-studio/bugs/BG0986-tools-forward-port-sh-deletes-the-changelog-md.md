# BG0986: `tools/forward-port.sh` deletes the CHANGELOG.md the installer ships into the skill, so `project upgrade` loses its changelog digest after every forward-port

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** tools/forward-port.sh, tools/tests/test_forward_port_changelog.py
> **Evidence:** Forward-port dry run on 2026-10-07 after pushing 34a7ee59, while shipping BG0962.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T14:55:59Z

## Summary

`install.sh`'s `ship_changelog` copies the repository's CHANGELOG.md into the installed skill on purpose: `project upgrade` digests the changelog between a project's recorded version and the installed one, offline (install.sh:487-495). `tools/forward-port.sh` mirrors the skill source with `rsync -rci --delete`, excluding only `.local`, `__pycache__` and `.pytest_cache` (forward-port.sh:102), and the skill source has no CHANGELOG.md, so every forward-port deletes it: the dry run on 2026-10-07 listed `*deleting CHANGELOG.md`. After that, every consuming project on the machine upgrades without the digest, degrading to the tool's 'absent' message. AGENTS.md tells contributors to forward-port after each fix lands, so this runs often.

## Steps to Reproduce

`./install.sh --local` (or any install that ships CHANGELOG.md), then `bash tools/forward-port.sh` -> the itemised diff shows `*deleting CHANGELOG.md`; with `--yes` the installed copy loses it.

## Proposed Fix

Exclude CHANGELOG.md from the --delete sweep, or have forward-port ship it the way install.sh does (copy the repository's CHANGELOG.md into the target after the sync), so a forward-ported copy matches an installed one.

## Acceptance Criteria

- [ ] **AC1** A forward-port into a copy that holds the installer's CHANGELOG.md leaves it in place, or replaces it with the repository's current one, and never deletes it
  - **Verify:** pytest tools/tests/test_forward_port_changelog.py -k changelog_survives_the_sweep
- [ ] **AC2** Every other file absent from the source is still swept, so the mirror stays exact
  - **Verify:** pytest tools/tests/test_forward_port_changelog.py -k other_strays_are_still_swept

## Triage

- Reproduced on 2026-10-07 by the forward-port dry run after 34a7ee59 (`*deleting CHANGELOG.md`); the port was not applied for that reason, and the BG0962 code it would have shipped was already in the installed copy. Reconcile's CR0370 advisory dismissed: CR0370 added the test-cache exclusions to the same sweep, not the changelog.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
