# US0629: a test plan is DERIVED from the unit's criteria by the tooling, naming per criterion the production change the test must fail on

> **Status:** Ready
> **Delivers:** CR0525
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/templates/core/test-spec.md
> **Epic:** EP0207
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer about to write a unit's tests
**I want** the test plan derived from the unit's own acceptance criteria by the tooling, one row per criterion, each naming the production change its test must fail on
**So that** a criterion cannot be silently missing from the plan, which is how four mechanisms shipped in one sprint with passing suites that survived their own deletion

## Acceptance Criteria

### AC1: the plan has exactly one row per criterion, and the count is enforced rather than intended

- **Given** a unit carrying N acceptance criteria
- **When** `verify_ac.py testplan derive --unit <id>` runs
- **Then** it emits exactly N rows keyed by criterion id, and refuses to write a plan whose row count differs from the criteria it read, because a plan assembled by hand is exactly where a criterion goes missing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanDeriveTests::test_every_criterion_gets_exactly_one_row
- **Caller:** `verify_ac.py testplan derive` (the CLI verb), reached by `transition.py set --status "In Progress"` via US0630
- **Verification target:** functional
- **Mutation-checked:** yes (2026-08-06). Deleting the equality KILLED; making the count tautological (`declared = len(parse_story(text))`) KILLED - the mutant revision 1 would have missed. Collapsing rows into a dict by `ac_id` is EQUIVALENT rather than uncovered: the duplicate-id refusal added here reads `ids`, computed before any collapse, so the collapse can no longer reach an outcome
- **Verified:** yes (2026-08-06)

### AC2: each row names a concrete production edit, and a row that merely restates its criterion is refused

> **RESTATED under BG0525**, before implementation, because the original wording was not
> mechanically decidable. It asked `derive` to refuse a mutant that is "that criterion's own text
> with the polarity flipped", and an independent seat produced the mutant that defeats it: a field
> reading ``in `verify_ac.py`, make it so the plan does not have exactly one row per criterion``
> names a real file, names an edit, and IS the criterion with its polarity flipped. Every proxy -
> path presence, negation words, token overlap - either accepts it or needs a tuned threshold.
> Implementing the old wording would have produced BG0523's class exactly: a criterion marked
> Verified against a verifier pinning a proxy rather than the property.

- **Given** a derived plan whose mutant field for a criterion is (a) blank, (b) names no path drawn from the unit's own `Affects`, (c) carries no edit verb, or (d) shares more than **60%** of its meaningful tokens with that criterion's own `Then` clause
- **When** the plan is written
- **Then** `derive` refuses that row, naming the criterion and which of the four properties it failed, because a mutant is a change to production code and "the feature does not work" is not one
- **The discriminating pair, stated here rather than left to the implementer.** REFUSE: `in verify_ac.py, make it so the plan does not have exactly one row per criterion` - a real path, a real edit verb, and 71% token overlap with its criterion. ACCEPT: `in verify_ac.py, delete the len(rows) == len(criteria) equality` - the same path and verb, 24% overlap. The two differ in ONE property, which is what makes the threshold the thing under test rather than the example
- **The near-miss ACCEPT is required, not optional.** A legitimate mutant that happens to share the criterion's vocabulary must still be accepted, or `derive` becomes a guard that refuses honest work while its refusal test passes for exactly that reason
- **The 60% ceiling is a stated number with a stated basis**, following `_reason_substance` in `verify_ac.py:2264` - measure substance after filler and punctuation come off, never raw text. That helper carries the scar of a one-character `-` passing a non-blank check, which is the same failure a raw-text comparison would repeat here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanDeriveTests::test_a_restated_criterion_is_not_a_mutant
- **Caller:** `verify_ac.py testplan derive`
- **Verification target:** functional
- **Mutation-checked:** yes (2026-08-06). Accepting a blank field KILLED; accepting the restatement KILLED; checking path SHAPE rather than `Affects` MEMBERSHIP KILLED, once a path-shaped non-member was added to the fixtures. The measured pair is 67%/40%, not the 71%/24% on the criterion: the path tokens are EXCLUDED from the overlap, because naming a file is separately required and counting it as novel substance lets a restatement buy headroom with obliged words. Counting them again KILLED
- **Verified:** yes (2026-08-06)

### AC3: the plan lives in the unit's own file, so it travels with the unit and files stay truth

- **Given** a unit with no `## Test Plan` section
- **When** `derive` runs, and then runs a second time over its own result
- **Then** the section is written into the unit's own markdown, the second run is a no-op that says so, and an existing hand-authored mutant is preserved rather than overwritten, because naming the mutant is the judgement and only the row set is derived
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanDeriveTests::test_derive_is_idempotent_and_preserves_authored_mutants
- **Caller:** `verify_ac.py testplan derive`
- **Verification target:** functional
- **Mutation-checked:** yes (2026-08-06). Overwriting an authored mutant KILLED; regenerate-and-append KILLED; printing the no-op unconditionally KILLED; folding the plan into `ac_fingerprint` KILLED
- **Verified:** yes (2026-08-06)

## Test Plan

> Authored by hand BEFORE any implementation, reviewed by an independent seat, and
> revised against that review. This is US0629's own mechanism performed manually -
> the unit that automates it cannot yet derive its own plan.

Revision 1 was rejected before any code was written. All three rows named a wrong-reason risk
that was either factually false (AC1) or a decoy standing in front of a worse mutant (AC2, AC3).
Every change below is the seat's, not mine; where I have added anything of my own it says so.

---

### AC1 - exactly one row per criterion, count enforced not intended

**DESIGN CONSTRAINT, promoted out of the implementation and into the plan.** The row count and
the criteria count must be produced by **two independent readers**. If `derive` counts criteria
from the same list it builds rows from, the equality is tautological and the mutant that deletes
it survives every fixture. This is part of the criterion, not a detail.

The repo already ships the two readers, and they genuinely disagree:

- `verify_ac.parse_story` - whole file, matches `### ACn` and `- **ACn**`, fence-aware.
- `sdlc_md.count_acs` - only inside `## Acceptance Criteria`, also counts bare `- [ ]` items,
  not fence-aware.

**Fixtures, all measured by the seat against the real parsers, not hypothesised:**

| Fixture | rows | criteria | direction |
| --- | --- | --- | --- |
| a `- [ ]` checkbox criterion beside two `### ACn` | 2 | 3 | rows < criteria |
| a duplicate `### AC1:` heading | 2 | 3 | rows < criteria, via id collapse |
| `### AC7:` under `## Notes` | 3 | 2 | **rows > criteria** |
| `### AC9:` inside a fenced block in the AC section | 2 | 3 | rows < criteria |

**Tests.** Both directions - the criterion says "differs", which is symmetric, and revision 1
only contemplated one side. Each asserts the refusal NAMES the unaccounted-for criterion, not
merely that it refused.

**Mutants to apply.** (a) delete the equality; (b) count criteria from the row list itself, so
the equality is tautological - this is the one revision 1 would have missed entirely; (c) key
rows into a dict by `ac_id`, silently collapsing the duplicate-id case to one row.

**DROPPED from revision 1:** the "heading whose body cannot be read" fixture, which produces no
mismatch at all - `parse_story` builds the block from the heading alone, so the test would have
gone green having exercised nothing. And the "injected row set", which is a library-level
fabrication unreachable from the CLI verb: the `brief_fingerprint(brief(...))` failure recommitted.

### AC2 - UNBLOCKED: BG0525 restated the criterion in decidable terms

Revision 2 recorded AC2 as blocked, because the criterion asked `derive` to refuse a mutant that
is "that criterion's own text with the polarity flipped" and no implementation can decide that.
BG0525 has now restated it on four checkable properties: a blank field, a path not drawn from the
unit's own `Affects`, no edit verb, or more than 60% meaningful-token overlap with the criterion's
own `Then` clause.

**Tests, and each names the property it pins.** One per refusal limb, each asserting the refusal
NAMES which property failed rather than merely that it refused - a guard that refuses for the
wrong reason passes a bare-refusal assertion.

**The discriminating pair is on the criterion, not chosen here.** REFUSE at 71% overlap, ACCEPT
at 24%, both naming `verify_ac.py` and both carrying an edit verb, so the pair differs in exactly
one property and the THRESHOLD is what is under test.

**The near-miss ACCEPT is a test in its own right.** A legitimate mutant sharing the criterion's
vocabulary must be accepted. Without it, a threshold tuned to refuse everything passes every
refusal row for exactly the wrong reason - which is the shape of the defect this whole revision
exists to avoid.

**Mutants to apply.** (a) accept a blank field; (b) accept the 71% restatement; (c) drop the
`Affects` constraint so any path-shaped token passes - the seat's defeating mutant relied on
naming a REAL file, so a rule that checks path SHAPE rather than membership still accepts it.

**Substance, not raw text.** The overlap is measured after filler and punctuation come off,
following `_reason_substance` (`verify_ac.py:2264`) and its scar: a one-character `-` passed a
non-blank check there, and a raw-text comparison would repeat it here.

### AC3 - the plan lives in the unit's file; idempotent; authored mutants preserved

Revision 1's "distinctive authored text" is necessary and **not sufficient**. The seat
constructed three overwrite mutants that all preserve a distinctive string:

1. **Regenerate-and-append** - a fresh `## Test Plan` section is written and the old one left in
   place. The authored string survives; the governing row is the generated one.
2. **Reassign** - the authored mutant is preserved but attached to a different criterion's row.
3. **Append-within-the-cell** - the cell becomes `<authored>; regenerated: <derived>`.

**Assertions, therefore:** exactly ONE `## Test Plan` section; the assertion is KEYED (the row
for AC2 carries X, not "X appears somewhere"); and it is cell EQUALITY, not containment.

**Idempotency needs a negative control.** Asserting the no-op message on run 2 alone leaves a
mutant that prints it unconditionally while still rewriting the file. Require all three: run 1
must NOT emit it, run 2 must, and run 2's bytes must equal run 1's.

**Mine, not the seat's:** state what "no-op" means when the unit gained a criterion between
runs - append the new row, leave authored cells untouched. The seat flagged the silence as
non-blocking; naming it now costs nothing and it is otherwise found at review.

---

### Carried forward unchanged

- No claim that `derive` is reachable from `transition.py set --status "In Progress"` - that
  wiring is US0630's, and the `Caller:` field says so.
- `Mutation-checked:` fields get what actually happened at delivery, survivors included.
- One assertion that writing `## Test Plan` does not move `ac_fingerprint` (it covers
  ac_id/title/verifier only), so a derived plan cannot falsely stale a green verify entry.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | sdlc-studio | Groomed: criteria authored against the `verify_ac.py testplan` slice |
