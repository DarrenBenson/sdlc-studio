# BG1591: The author self-check refuses a documentation page the unit's Affects declares as a claim surface, so a docs unit's claims in its own page cannot be recorded and the land refuses its self-check

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py, changelog.d/BG1591.md
> **Evidence:** .local/run17/land-US1321.log (2026-11-18): US1321 landed at 42fc6eb5 and its self-check was refused on claim 27, surface docs/evidence.md. The refusal was fixed in b1d236935 (BG1512); the remainder was reproduced at cecc9dfe through `critic.py brief` in a throwaway project, 2026-11-24.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:00:52Z

## Summary

As filed: `check_self_check` (critic.py) accepted claims only on the commit message, the unit's changelog fragments, Resolutions, docstrings, comments and CHANGELOG. A documentation unit makes most of its claims in the page it writes, so a builder that inventoried them under that page's path (for example docs/evidence.md) had its whole self-check refused at `sprint lane land`, and the orchestrator had to drop the claim by hand to record it. Met on US1321 in run seventeen; every docs unit in CR0742's run (US1316 to US1320) declares a page.

b1d236935 (BG1512) fixed the refusal: `claim_surfaces` now returns each `.md` or `.mdx` page the unit's Affects declares as an optional surface, `check_self_check` accepts a claim naming one, and the lane brief (`sprint.py`) lists them. The rest of the Proposed Fix, naming the page in the claim-inventory list, is still missing from `critic.py brief`'s AUTHOR SELF-CHECK section. `author_self_check` (critic.py, around line 2985) builds its step 1 list from the commit message, `CLAIM_SURFACES` and the changelog fragments, a copy of the list rather than `claim_surfaces` itself, so it leaves out the declared pages. An author working from the critic brief is not told that a page counts as a surface, although the `claim_surfaces` docstring says the record and the brief cannot name different sets.

## Steps to Reproduce

1. In a throwaway project, give US0801 the Affects `docs/evidence.md, docs/guide.mdx, changelog.d/US0801.md`.
2. `critic.py brief --unit US0801 --seat qa --tier full`: the AUTHOR SELF-CHECK section on stderr reads `1. Claim inventory, over: the commit message; Resolutions; docstrings; comments; CHANGELOG; changelog.d/US0801.md.`, naming neither page.
3. `critic.claim_surfaces` over the same Affects returns both pages among its optional surfaces, and `critic.py self-check record` accepts a claim naming `docs/evidence.md`.

## Proposed Fix

Build `author_self_check`'s step 1 surfaces from `claim_surfaces(affects)`, required then optional, keeping the commit message's leading "the" and the existing order, so a declared page is named and the critic brief's list cannot drift from what the record accepts. The line scoping the brief's own instruction to the four prose surfaces is unchanged.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose Affects declare `docs/evidence.md`, `docs/guide.mdx` and its changelog fragment, when `critic.py brief --unit <id> --seat qa` runs, then the AUTHOR SELF-CHECK section's `1. Claim inventory, over:` line names both pages. Fails on: the line lists only the commit message, the four prose surfaces and the fragment.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_a_declared_page_is_named_in_the_inventory
- [ ] **AC2** Given units declaring no page, an `.md` page, an `.mdx` page, and a page beside a fragment, when `author_self_check` prints step 1, then its surfaces, each read as `_surface_key` reads a claim's surface, are exactly the commit message, then `claim_surfaces(affects)`'s optional surfaces in order, then its fragments; and with `claim_surfaces` patched to return one more optional surface, the line names it. Fails on: the section's list is copied from `CLAIM_SURFACES` and the fragments, so it omits the pages `claim_surfaces` returns and ignores the patch.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_the_inventory_is_read_from_claim_surfaces
- [ ] **AC3** Given a unit declaring `src/widget.py, tests/test_widget.py, changelog.d/US0802.md` and no page, when `critic.py brief` runs, then step 1 reads exactly `1. Claim inventory, over: the commit message; Resolutions; docstrings; comments; CHANGELOG; changelog.d/US0802.md.` as today. Fails on: a fix that lists the changelog fragment again as a page, or reorders or renames the existing surfaces (this control holds today).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py::AuthorStepsTests::test_a_unit_declaring_no_page_prints_as_before

## Impact

A docs unit's own page, where its claims live, is a surface the record accepts but the critic brief does not name, so an author working from that brief leaves the page's claims out of the inventory.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: b1d236935 (BG1512) fixed the land refusal and lists a declared page in the lane brief, so the unit is narrowed to `critic.py brief`'s AUTHOR SELF-CHECK section, which still omits the page; reproduced at cecc9dfe; three executable criteria (the page named, the list read from `claim_surfaces`, and a no-page control); Affects now critic.py, test_critic_author_self_check.py and the fragment, dropping test_critic_self_check_refusal.py and test_critic.py; Points 2 to 1 |
| 2026-11-24 | orchestrator | AC2 reworded to AC3's order (commit message, optional surfaces, then fragments): 'required then optional' put the fragment before Resolutions, which AC3 pins against (the CR builder) |
