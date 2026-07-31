# BG0468: Three high-severity advisories reach the tree through the markdown lint chain, and surfaced only because 208 commits were finally pushed

> **Status:** Fixed
> **Verification depth:** functional (the lockfile floors and the linter probe are pinned by tests; the probe itself was written after two false all-clears - the first piped through `head` so `$?` reported head's status, and the second used a lazy continuation that is not a CommonMark violation)
> **Severity:** High
> **Points:** 1
> **Affects:** ./package-lock.json
> **Evidence:** GitHub dependabot, reported on the first push in five days: GHSA-v245-v573-v5vm (linkify-it), GHSA-52cp-r559-cp3m (js-yaml), GHSA-3jxr-9vmj-r5cp (brace-expansion).
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`linkify-it` at 5.0.1, `js-yaml` at 4.2.0 and `brace-expansion` at 5.0.6 all sit in the tree transitively through `markdownlint-cli`, the repo's only devDependency, and all three carry high-severity advisories.

The delivery half matters as much as the versions. They were reported the moment 208 unpushed commits reached the remote, because dependabot reads the pushed graph. The tree had gone five days without a push, so the alerts existed and nobody could see them - the same window in which CI had not run either. A dependency alert is only as timely as the last push.

## Steps to Reproduce

```text
gh api repos/.../dependabot/alerts:
  high  npm/linkify-it       <= 5.0.1              -> 5.0.2
  high  npm/js-yaml          >= 4.0.0, < 4.3.0    -> 4.3.0
  high  npm/brace-expansion  >= 3.0.0, < 5.0.7    -> 5.0.7

lockfile before: linkify-it 5.0.1, js-yaml 4.2.0, brace-expansion 5.0.6
npm audit: 4 high (the three above plus markdownlint-cli), all fixAvailable
```

## Proposed Fix

Lockfile only. `package.json` stays untouched, because `^0.49.0` already covers the markdownlint-cli 0.49.1 that carries the fixed transitives - no semver range is widened to make an advisory go away.

Because `js-yaml` crosses a major version and markdownlint drives the gate's markdown lane, the check is not that the linter still RUNS but that it still LINTS: a probe carrying trailing whitespace, consecutive blank lines and a bare URL must trip MD009, MD012 and MD034 and exit non-zero. A silently neutered linter passes every gate it is in.

## Acceptance Criteria

### AC1: the patched transitives are in the lockfile, and no range was widened

- **Given** the three advised packages
- **When** the lockfile is read
- **Then** each is at or above its patched version, and `package.json` still declares `^0.49.0` - the cheap wrong fix is to loosen a range until the resolver picks something clean, and this pins that it was not taken
- **Verify:** pytest tools/tests/test_dependency_advisories.py::LockfileTests::test_the_patched_transitives_are_at_or_above_their_fixed_versions
- **Verified:** yes (2026-07-31)

### AC2: the linter still LINTS after a major dependency bump

- **Given** a probe carrying trailing whitespace, consecutive blank lines and a bare URL
- **When** markdownlint runs over it
- **Then** it exits non-zero naming MD009, MD012 and MD034 - `js-yaml` crossed a major version to clear its advisory, and a linter that runs but detects nothing passes every gate it is in
- **Verify:** pytest tools/tests/test_dependency_advisories.py::TheLinterStillLintsTests::test_a_file_with_known_violations_is_REFUSED
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed AFTER the diff, for the second time today, having flagged the same ordering error on BG0467 an hour earlier. Recorded rather than backdated. |
