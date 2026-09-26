# BG0789: The release workflow publishes a release-candidate tag as the latest release, so every installed copy is prompted to upgrade to it

> **Status:** Open
> **Severity:** High
> **Points:** 1
> **Affects:** .github/workflows/release.yml, tools/tests/test_release_prerelease.py, changelog.d/BG0789.md
> **Created:** 2026-09-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-26T16:24:43Z

## Summary

release.yml runs gh release create without --prerelease, so a tag such as v6.0.0-rc.1 becomes the forge's latest release; `version_check.latest_release` reads that, so every v5.1 install would be prompted to upgrade to a release candidate. Found preparing v6.0.0-rc.1; it must be fixed before that tag is pushed.

## Steps to Reproduce

Read .github/workflows/release.yml lines 96-102: neither gh release create passes --prerelease for a tag carrying a pre-release suffix.

## Proposed Fix

Pass --prerelease (and --latest=false) when the tag carries a pre-release suffix (-rc., -beta., -alpha.), with a tools/tests test that reads release.yml and asserts both branches carry it for a suffixed tag and not for a plain one.

## Acceptance Criteria

- [ ] **AC1** Given `.github/workflows/release.yml`, when the publish step runs for a tag carrying a pre-release suffix (`v6.0.0-rc.1`), then both `gh release create` branches pass `--prerelease` and `--latest=false`, so the forge's latest release stays the last final one. Fails on: a `gh release create` with no pre-release flag
  - **Verify:** pytest tools/tests/test_release_prerelease.py::ReleasePrereleaseTests::test_a_suffixed_tag_is_published_as_a_prerelease
- [ ] **AC2** Given a plain tag (`v6.0.0`), then neither branch passes `--prerelease`, so a final release still becomes the latest. Fails on: a workflow that marks every release a pre-release
  - **Verify:** pytest tools/tests/test_release_prerelease.py::ReleasePrereleaseTests::test_a_final_tag_is_published_as_the_latest

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-26 | sdlc-studio | Filed |
