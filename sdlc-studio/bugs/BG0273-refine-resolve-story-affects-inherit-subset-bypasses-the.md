# BG0273: refine resolve_story_affects inherit:subset bypasses the parent-declares-none refusal and never checks the subset is within the parent's Affects; bare 'inherit' is matched case-sensitively so INHERIT falls through to the explicit path

> **Status:** Fixed
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py,.claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Verification depth:** functional (unit: inherit:subset is refused when the parent declares none, and the subset is checked to be within the parent's set)
> **Severity:** Medium
> **Points:** 3

## Summary

`refine.resolve_story_affects` handled the narrowed `inherit:paths` form with
`if subset: return subset, "inherited"` placed BEFORE the parent-declares-none refusal, so
three things went wrong at once:

1. **The refusal was bypassed.** `inherit:src/a.py` against a request that declares no
   `Affects` returned the subset and reported mode `inherited` - an inheritance from a parent
   with nothing to inherit. The bare `inherit` form refuses that case loudly.
2. **The subset was never checked against the parent.** `inherit:` is a NARROWING, but any
   path at all was accepted, so it could ADD a path the parent never declared and the minted
   story's footprint claimed a provenance it had not got.
3. **The bare keyword was matched case-sensitively.** `a == INHERIT_TOKEN` fails for
   `INHERIT`, and `a.lower().startswith("inherit:")` does not match it either, so `INHERIT`
   fell through to the explicit path and minted a story whose declared `Affects` was the
   literal word - which the Affects parser reads as no path list at all, so the resolvable
   check waved it through as prose and the planner cannot size or collision-check it.

## Steps to Reproduce

1. `refine apply --request CR0001 --story 'S|3|inherit:src/a.py'` where CR0001 declares no
   `Affects`. Observed: minted. Expected: the same refusal the bare `inherit` raises.
2. `resolve_story_affects("CR0001", "src/a.py", "inherit:src/elsewhere.py")`. Observed:
   `("src/elsewhere.py", "inherited")`. Expected: refused - that path is not the parent's.
3. `refine apply --request CR0001 --story 'S|3|INHERIT'` where CR0001 declares three files.
   Observed: a story whose `Affects` is the word `INHERIT`. Expected: the parent's three files.

## Proposed Fix

Match the keyword case-insensitively, run the parent-declares-none refusal FIRST so it covers
the narrowed form too, and check every path a subset names is already in the parent's
`Affects` - read by the one Affects parser every writer uses, so the narrowing is judged
against exactly the paths the planner will see. A subset token that parser cannot read as a
path is outside as well: it is not one of the parent's paths either.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed (symptom, repro, fix) and the AC split into three executable criteria in place of `manual`. |
| 2026-07-24 | sdlc-studio | Fixed: keyword lowered before matching, declares-none refusal hoisted above the subset return, containment checked via a new `_outside_parent` helper. Four mutants killed; every pre-existing refine test still green. |

## Acceptance Criteria

### AC1: inherit:subset from a request that declares no Affects is refused

- **Given** a story declares `inherit:paths` against a request with no `Affects`
- **When** refine resolves it
- **Then** it is refused naming the request, before anything is minted - the same refusal the bare `inherit` raises
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::InheritSubsetTests::test_inherit_subset_from_a_request_that_declares_none_is_refused

### AC2: a subset naming a path outside the parent's Affects is refused

- **Given** a story declares `inherit:paths` naming a path the parent never declared, or a token the Affects parser cannot read as a path
- **When** refine resolves it
- **Then** it is refused, naming the offending path - `inherit:` narrows a footprint, it does not add to one - while a genuine narrowing still resolves to the subset
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::InheritSubsetTests::test_a_subset_naming_a_path_outside_the_parent_is_refused

### AC3: the inherit keyword is matched in any case

- **Given** a story declares `INHERIT` or `INHERIT:paths` in any capitalisation
- **When** refine resolves it
- **Then** it is treated as the inherit token, and the minted story carries the parent's paths rather than the literal word
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine.py::InheritSubsetTests::test_the_inherit_keyword_is_matched_in_any_case
