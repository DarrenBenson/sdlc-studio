# BG1545: The tag push gate never compares the pushed tag name with the version the tagged tree declares

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-push, tools/check_versions.py, tools/tests/test_pre_push_hook.py, tools/tests/test_check_versions.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at .githooks/pre-push lines 27-36 (the ref loop: `remote_ref` is read only by `case "$remote_ref" in refs/tags/*)` to pick the boundary) and lines 76-86 (the known-issues check); gate.py registry lines ~2176-2208 (`versions` strict is bound under `--release`, not under `--boundary release`)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:40Z

## Summary

At a tag push the pre-push hook reads the remote ref only to choose the release boundary, and the tag's name is never used again. The release boundary in gate.py adds the full suite, the release rehearsal and the module-alone lane, but the strict versions lane is bound only under the manual `--release` flag, and that lane compares the version homes with each other, never with a tag. The known-issues check renders for the series its own page heading names, and tools/`check_versions.py` takes no tag input. A tag named for one version over a tree that declares another therefore passes the whole tag gate. The release workflow then archives and publishes it under the tag name, while install.sh reports and compares by the version inside the payload, so the downgrade guard and the upgrade prompt work from the wrong number.

## Steps to Reproduce

1. In a scratch clone with the hooks enabled, leave package.json, templates/version.yaml, SKILL.md and CHANGELOG.md declaring 6.4.0.
2. Create a tag named v6.5.0 on that commit.
3. Feed the pre-push hook a ref line for refs/tags/v6.5.0, with the gate lanes stubbed green as `test_pre_push_hook.py` does.
4. Observed: the hook exits 0. Nothing in it, in gate.py with the release boundary, in `known_issues.py` check or in `check_versions.py` reads the name v6.5.0.
5. Expected: a refusal saying the tag names 6.5.0 and the tagged tree declares 6.4.0.
6. Positive control: a tag named v6.4.0 on the same commit passes.

## Proposed Fix

In the ref loop of .githooks/pre-push keep each pushed tag's name beside its commit. For each one, strip the leading refs/tags/v and refuse the push unless the version the tagged commit declares is exactly that string. Give tools/`check_versions.py` an option that takes an expected version and a commit to read, so the hook asks one script and the strict agreement of the version homes is checked at the same time. Have the known-issues check confirm that the page series matches the tag as well. Add a hook test for a mismatched tag with a matching tag as its control, and a `check_versions` test for the new option.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: At a tag push the pre-push hook reads the remote ref only to choose the release boundary, and the tag's name is never used again.
- [ ] **AC2** The proposed fix lands, pinned by a test: In the ref loop of .githooks/pre-push keep each pushed tag's name beside its commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
