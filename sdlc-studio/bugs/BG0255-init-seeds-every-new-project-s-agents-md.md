# BG0255: init seeds every new project's AGENTS.md with a literal {{PROJECT_NAME}} placeholder, because the filler matches lowercase and the template ships uppercase

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py,.claude/skills/sdlc-studio/templates/agent-instructions.md
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found while grooming US0293 and then proven by running the code rather than reading it. `init._fill_known` substitutes only the four keys it knows, spelled lowercase - `project_name`, language, date, `last_updated` - while templates/agent-instructions.md heads with the uppercase {{`PROJECT_NAME`}}. The two never meet, so the substitution silently does nothing and the placeholder ships. Demonstrated by calling `_fill_known` directly with `project_name` set to ACME against the real shipped template: the placeholder is still present in the output and the string ACME appears nowhere in it. init.py line 182 runs every file in `AGENT_FILES` through this filler, and `AGENT_FILES` is exactly AGENTS.md and CLAUDE.md, so BOTH agent-instructions files are affected. The severity is about who sees it and when: AGENTS.md is the first file a project adopting this skill reads, it is the file that tells every coding agent how the project works, and it is produced by init, the very first command anyone runs. The failure is silent and fails open - nothing warns, nothing exits non-zero, and the file looks finished apart from an unfilled name. It becomes worse the moment CR0352 ships, because migrate --apply will then seed the same template through the same path onto brownfield projects, multiplying the blast radius from new projects to every upgrading one.

## Acceptance Criteria

- [x] **AC1:** Seeding a project fills the project name in `AGENTS.md`, whatever the case of the
      placeholder the template carries.
      Pinned by `test_init.PlaceholderFillTests`.
- [x] **AC2:** A placeholder the filler CLAIMS to know that survives a seed raises, rather than
      shipping a file with an unfilled name.
      Pinned by `test_init.PlaceholderFillTests`.
- [x] **AC3:** Both agent-instructions files are covered, since the filler runs over every entry
      in `AGENT_FILES`.
      Pinned by `test_init.PlaceholderFillTests`.

## Steps to Reproduce

1. From the repo root, import init from the skill scripts directory. 2. Read the shipped template at .claude/skills/sdlc-studio/templates/agent-instructions.md. 3. Call `init._fill_known` on that text with a fields mapping whose `project_name` key is set to ACME, alongside language, date and `last_updated.` 4. Inspect the returned text. Observed: the uppercase project-name placeholder is still present, and the substituted value ACME appears nowhere in the output. Expected: the placeholder is replaced by the project name. The same result follows end to end by running init run in an empty directory and reading the AGENTS.md it writes, whose first heading still carries the unfilled placeholder.

## Proposed Fix

Match on a case-insensitive placeholder, or normalise the template to the lowercase spelling the filler already uses. Prefer fixing the FILLER rather than only the template: the template is one of many and a future template author will reach for the natural uppercase form again, so a case-sensitive filler leaves the trap armed. Whichever is chosen, add an assertion that no placeholder the filler claims to know survives a seed, so this class cannot return silently - the defect here is not the mismatch itself but that nothing noticed a documented substitution doing nothing.

## Resolution

Fixed in the FILLER, not only the template, so a future template author reaching for the natural
uppercase form does not re-arm the trap. `init._fill_known` now substitutes case-insensitively
(`_placeholder_re` + `re.IGNORECASE`), and it asserts its own postcondition: `init.unfilled_known`
returns any placeholder the filler CLAIMS to know - a `KNOWN_FIELDS` key the caller supplied a
value for - that survived, and a non-empty result raises rather than writing the file. The defect
was never the case mismatch; it was that a documented substitution did nothing and nothing
noticed.

Verified functionally, end to end:

- `_fill_known` called on the REAL shipped `templates/agent-instructions.md` with
  `project_name=ACME` now yields text containing ACME and no `{{project_name}}` in any case
  (`test_shipped_template_gets_its_project_name_filled`) - the exact reproduction from Steps to
  Reproduce, which failed before the change.
- A full `init.init()` into a temp directory: both files `AGENT_FILES` seeds (AGENTS.md and
  CLAUDE.md) come back with no surviving known placeholder and AGENTS.md carries the project name
  (`test_seeded_agent_files_carry_no_known_placeholder`).
- The postcondition itself raises when a placeholder survives
  (`test_fill_known_refuses_to_return_a_surviving_known_placeholder`), and `unfilled_known` reports
  only keys the caller actually supplied (`test_unfilled_known_reports_only_the_survivors_it_claims`).

Mutation-tested (3 mutants, all killed first time): dropping `re.IGNORECASE` from the substitution;
`unfilled_known` returning `[]` unconditionally; the postcondition short-circuited to never raise.
The template keeps its uppercase `{{PROJECT_NAME}}` deliberately, so the shipped exemplar exercises
the case-insensitive path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
| 2026-07-22 | sdlc-studio | Fixed: case-insensitive filler + postcondition guard; verified functional |
