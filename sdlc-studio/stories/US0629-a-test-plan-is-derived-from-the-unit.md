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
- **Mutation-checked:** to be recorded at delivery - dropping the row-count equality must turn this test red
- **Verified:** no

### AC2: each row names a concrete production edit, and a row that merely restates its criterion is refused

- **Given** a derived plan whose mutant field for a criterion is blank, or is that criterion's own text with the polarity flipped
- **When** the plan is written
- **Then** `derive` refuses that row, naming the criterion and demanding a named file plus the edit to make in it, because a mutant is a change to production code and "the feature does not work" is not one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanDeriveTests::test_a_restated_criterion_is_not_a_mutant
- **Caller:** `verify_ac.py testplan derive`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - accepting a blank mutant field must turn this test red
- **Verified:** no

### AC3: the plan lives in the unit's own file, so it travels with the unit and files stay truth

- **Given** a unit with no `## Test Plan` section
- **When** `derive` runs, and then runs a second time over its own result
- **Then** the section is written into the unit's own markdown, the second run is a no-op that says so, and an existing hand-authored mutant is preserved rather than overwritten, because naming the mutant is the judgement and only the row set is derived
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::TestPlanDeriveTests::test_derive_is_idempotent_and_preserves_authored_mutants
- **Caller:** `verify_ac.py testplan derive`
- **Verification target:** functional
- **Mutation-checked:** to be recorded at delivery - overwriting an authored mutant must turn this test red
- **Verified:** no

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

### AC2 - BLOCKED on BG0525, not implemented in this pass

The criterion asks `derive` to refuse a mutant that is "that criterion's own text with the
polarity flipped". That is not mechanically decidable, and the seat produced the mutant that
proves it: a field reading ``in `verify_ac.py`, make it so the plan does not have exactly one
row per criterion`` names a real file, names an edit, and IS the criterion with its polarity
flipped. Every proxy - path presence, negation words, token overlap - accepts it or needs a
tuned threshold with boundary rows on both sides.

**BG0525 carries the restatement.** Implementing AC2 against the current wording would produce
precisely the BG0523 defect: a criterion marked Verified against a verifier pinning a proxy
rather than the property. The blank-field half is decidable and could ship alone, but shipping
half of AC2 while ticking it whole is BG0490's class, so the row waits.

When BG0525 restates it, the plan needs: the minimal discriminating pair (genuine mutant naming
`verify_ac.py` -> ACCEPT; restatement naming `verify_ac.py` -> REFUSE, differing in one property
only), plus a **near-miss accept** - a legitimate mutant that happens to share the criterion's
vocabulary must still be accepted, or `derive` becomes a guard that refuses honest work while
its refusal test passes for that reason.

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
