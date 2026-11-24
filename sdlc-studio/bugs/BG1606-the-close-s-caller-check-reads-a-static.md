# BG1606: The close's caller-check reads a static site's page and component changes as mechanisms no caller consumes

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_caller_check_rendered_paths.py, changelog.d/BG1606.md
> **Evidence:** the website's RUN-01M7R7KN close, 2026-11-19: orchestrator. Reproduced at cecc9dfe through `critic.py caller-check` in a throwaway project, 2026-11-24.
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T07:50:28Z

## Summary

`sprint close` on the website's run printed caller-unnamed for six of seven units, each a change to an Astro page, an MDX page, a component or a data file the build renders: 'adds a mechanism ... and no criterion names the caller that consumes it'. On a static site the built page is the deliverable and the reader is its consumer, so the advisory is noise on every content unit and buries the case it exists for.

At HEAD `mechanism_files` (critic.py) subtracts only `.md` files and the files a unit's own verifiers name, so an `.mdx` page is read as a mechanism, although the self-check already treats `.mdx` as a page (`CLAIM_PAGE_SUFFIXES`). Its docstring refuses a list of code extensions on principle, so a fix that exempts `.astro` or `.json` by suffix would repeat the failure it warns of; a project naming its rendered paths does not.

## Steps to Reproduce

In a throwaway project, give four stories one Affects file each beside a changelog fragment: `src/pages/index.astro`, `src/content/blog/post.mdx`, `src/components/Card.astro` with `src/data/nav.json`, and `src/lib/util.ts`. `critic.py caller-check --unit <id>` exits 1 for every one with `[caller-unnamed]: <id> adds a mechanism (...) and no criterion names the caller that consumes it`. `sprint close` prints the same finding through `critic.caller_findings`.

## Proposed Fix

Read an `.mdx` file as a page, as `.md` is (`CLAIM_PAGE_SUFFIXES`). Add `review.rendered_paths`, a list of globs matched as `review.spec_paths` is and empty by default, naming the files a project's build renders (its pages, components, content and the data they read); `mechanism_files` subtracts a declared file matching one, so the caller-check judges only code a caller must reach. The `caller-indeterminate` branch of `caller_findings`, which reads every non-`.md` Affects file as code, must apply the same subtraction, or an emptied surface is reported as indeterminate instead. Document the key in config-defaults.yaml and reference-config.md.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects are `src/content/blog/post.mdx` and its changelog fragment, when `critic.py caller-check --unit <id>` runs, then it reports no finding and exits 0. Fails on: `[caller-unnamed]` naming `post.mdx` as a mechanism, exit 1.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_caller_check_rendered_paths.py::CallerCheckRenderedPathsTests::test_an_mdx_page_is_not_a_mechanism
- [ ] **AC2** Given a project whose `sdlc-studio/.config.yaml` sets `review.rendered_paths` to globs covering `src/pages/`, `src/components/` and `src/data/`, when `critic.py caller-check` runs over units changing only `src/pages/index.astro`, `src/components/Card.astro` and `src/data/nav.json`, then it reports no finding and exits 0. Fails on: `[caller-unnamed]` for each unit, exit 1.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_caller_check_rendered_paths.py::CallerCheckRenderedPathsTests::test_a_declared_rendered_path_is_consumed_by_the_build
- [ ] **AC3** Given the same config, a unit changing `src/lib/util.ts` is still reported `[caller-unnamed]`; and given no `review.rendered_paths`, a unit changing `src/pages/index.astro` is still reported. Fails on: a fix that exempts by file suffix or exempts every unit, so the check stops catching an unconsumed mechanism (this guard holds today).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_caller_check_rendered_paths.py::CallerCheckRenderedPathsTests::test_code_outside_the_rendered_paths_is_still_asked_for_a_caller
- [ ] **AC4** Given the shipped defaults, when a reader looks up `review.rendered_paths`, then config-defaults.yaml sets it to an empty list and reference-config.md documents it with that default. Fails on: the key exists in neither.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_caller_check_rendered_paths.py::CallerCheckRenderedPathsTests::test_the_key_is_documented_with_an_empty_default

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe through `critic.py caller-check`; generated criteria replaced by four executable ones (`.mdx` as a page, a declared `review.rendered_paths`, a guard that code outside it is still checked, and the documented default); Proposed Fix chooses the config key over a suffix list; Affects gains the config defaults, the config reference and a new test file and drops test_critic.py; Points stay 2 |
