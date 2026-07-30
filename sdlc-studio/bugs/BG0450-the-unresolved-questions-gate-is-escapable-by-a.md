# BG0450: the unresolved-questions gate is escapable by a heading suffix, a second section, or a self-citation, and the AC claiming it is type-general is verified by a tautology

> **Status:** Fixed
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, sdlc-studio/stories/US0465-no-artefact-reaches-a-terminal-status-carrying-unchecked.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** US0465 was the ONE unit of this batch that had never been independently reviewed - 36 of the other units carried some review record and it carried none. The first reviewer pointed at it found a stop-ship within minutes, which is the argument for the coverage gate being accurate rather than merely present: the single genuinely unreviewed unit was also the one hiding a mutant that survives 5489 tests. A correction to the story's own record while here - its Affects list and AC5's Given both overstate the corpus: the delivering commit touched 11 stories plus CR0019 and BG0421, not the 14 stories and EP0010 the AC names, five listed artefacts were never touched but reclassified as false positives by an exemption the same commit introduced, and US0293 was modified but is absent from Affects.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** independent round-2 reviewer (isolated worktree); agent; v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

US0465's contract is that no artefact reaches a terminal status carrying an unchecked Open Question. The shipped code is broadly correct and the workspace really is swept - 1631 terminal artefacts, 0 offenders - but the gate has three live escapes in UNMUTATED code, and the acceptance criterion asserting its central property is verified by a test that cannot fail on it.

The escapes: the heading anchor is `^#+\s*Open Questions\s*$`, so `## Open Questions (deferred)` hides the whole section; `_OPEN_Q_RE.search` rather than `finditer` reads only the FIRST such section, so a second one is never scanned; and the follow-up route uses `find_by_id`, which accepts the artefact's OWN id, so a question ticked off citing itself satisfies a docstring promising 'the escape hatch cannot be a tick pointing at nothing'.

The tautology: AC4 claims 'every terminal status is derived from the map rather than from an enumerated Done, so a CR reaching Superseded is held to the same rule as a story reaching Done'. Its verifier loops ~24 type-and-status combinations calling `sdlc_md.unresolved_questions(body, None)` - arguments that depend on neither the type nor the status. It is one identical call repeated, and it never invokes validate or the transition gate.

## Steps to Reproduce

Executed at d7a1ad8f, 2026-07-30, by an independent reviewer in an isolated worktree, with the key results re-confirmed by the author.

AC4's claim is untested. Mutant `is_terminal_status(type_, target_canon)` -> `target_canon == "Done"` at `transition.py:774` SURVIVES the full suite: `Ran 5489 tests ... OK`. It is a real CLI escape, not merely a surviving mutant. A fixture bug at Open carrying `- [ ] should we do X?`:

```text
unmutated:  transition.py set BG0001 Fixed  ->  rc=1, blocked, 1 unresolved Open Question(s)
mutated:    transition.py set BG0001 Fixed  ->  rc=0, file on disk reads Status: Fixed
```

Author's confirmation of the blast radius:

```text
bug/Fixed:      terminal=True   gate fires under mutant=False
cr/Superseded:  terminal=True   gate fires under mutant=False
story/Done:     terminal=True   gate fires under mutant=True
```

So a bug reaches Fixed and a CR reaches Superseded carrying unanswered questions - exactly what the story's title says cannot happen - with 5489 tests green.

The unmutated escapes, at the CLI: a story with `## Open Questions (deferred)` and an unchecked item transitions to Done with rc=0 and `validate check` reports `errors=0`. A question ticked `- [x] ... See US0001.` on US0001 itself likewise passes. The second-section escape was found independently by the QA amigo seat with a positive control - the same question in the FIRST section kills the test, in the second it survives.

AC5's verifier has no positive control: `return offending` -> `return []` (a fully blind detector) SURVIVES it, as does changing the heading regex to `Open Queries` so no section ever matches. Its `assertGreater(swept, 100)` counts terminal ARTEFACTS, not questions found, and stories alone supply 525 of the 1631.

## Proposed Fix

Three separable pieces, in this order.

1. Rewrite AC4's verifier so it drives `transition.transition()` and `validate` over a fixture of each type in each terminal status and asserts the refusal - a test the `== "Done"` mutant kills. The current one asserts a helper's behaviour and calls it a gate.
2. Give AC5's sweep a positive control: plant an offender the sweep MUST find. Without it a clean run is equally consistent with a detector that scans nothing, which is this repo's own recorded lesson and is exactly what the two surviving mutants demonstrate.
3. Close the three live escapes. Allow a heading suffix, use `finditer` so every section is scanned, and refuse a self-citation in `find_by_id`.

Also owed, smaller: AC1's Verify line names a test that calls the helper directly and never invokes validate - the behaviour IS covered, by the un-named sibling `test_validate_ITSELF_reports_the_finding_not_only_the_helper`, so this is a mis-pointed selector rather than a hole and is fixed by swapping the line. AC3's validate half is unverified (its selector names a transition-only test); the mutation proving it survives the whole suite is `validate.py:339`.

One latent issue worth recording rather than fixing now: `find_by_id` checks existence, never status, and 18 real corpus items resolve their questions by citing BG0421. When BG0421 closes, those 18 stay marked resolved whether or not anyone answered them.

> **Verification depth:** functional - the gate is driven through the real `transition` command for a bug reaching Fixed and a CR reaching Superseded, not through the helper. The stop-ship mutant (`is_terminal_status` -> `target_canon == "Done"`) that survived all 5489 tests is KILLED, as are the two blind-detector mutants that previously survived the corpus sweep. Corpus re-swept: 1631 terminal artefacts, 0 offenders.

## Acceptance Criteria

### AC1: a heading carrying a suffix no longer hides its section

- **Given** a terminal artefact whose heading reads `## Open Questions (deferred)` and which carries an unchecked item
- **When** the detector runs
- **Then** the item is reported - the heading anchored to end-of-line, so one token of author edit turned the gate off and the artefact read clean rather than refused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::OpenQuestionsTests::test_a_heading_with_a_suffix_still_hides_nothing
- **Verified:** yes (2026-07-30)

### AC2: every Open Questions section is scanned, not the first

- **Given** a terminal artefact whose first section is fully resolved and whose second carries the live question
- **When** the detector runs
- **Then** the second section's item is reported - `search` read one section, so the question was never seen; found independently by two reviewers, one with a positive control proving the same item KILLS the test when placed in the first section
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::OpenQuestionsTests::test_a_second_open_questions_section_is_scanned_too
- **Verified:** yes (2026-07-30)

### AC3: a tick citing only the artefact itself is refused, and a real follow-up is not

- **Given** one artefact resolving its question by citing its own id, and one citing a different artefact
- **When** each is checked
- **Then** the self-citation is reported and the genuine follow-up still passes - `find_by_id` proves only that an id resolves, and an artefact always resolves to itself, which is the tick-pointing-at-nothing the docstring promises cannot happen; the control is what stops this fix simply breaking the escape hatch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::OpenQuestionsTests::test_a_tick_citing_only_itself_is_not_a_follow_up
- **Verified:** yes (2026-07-30)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | independent round-2 reviewer (isolated worktree) | Filed |
