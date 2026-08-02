# Test Strategy

Quality heuristics for deciding *what* to test, not just how. Distilled from
recurring cross-project lessons: the same five gaps keep letting bugs through unit
tests. Each has a one-line trigger ("when X, write test Y"). Read this before
writing a test spec or closing a bug.

## The five heuristics

### 1. Production-state-shape integration tests

**When** a path's behaviour depends on the *shape* of production state (multi-turn
history arrays, partially-populated records, resolve-then-cancel races), **write**
at least one integration test that injects the non-trivial shape.

Unit tests construct trivial state and pass while the real bug only manifests under
production shape. A whole class of silent-misleading failures escapes unit tests
this way (see [LL0009](../lessons/_index.md)).

### 2. A named regression test per production bug

**When** a production bug is fixed, **write** a regression test at the integration
level (the router -> dispatcher -> channel loop, the seam where it actually broke),
not a unit test on the root-cause file.

Unit tests prove a piece works in isolation; the bug lived in the seams between
pieces. The deterministic checker (below) flags a Fixed/Done bug whose recorded
tests show no integration- or regression-level case.

### 3. Contract changes ship a rejects-old-shape test

**When** you change a contract (a wire format, an API shape, a schema), **write** a
`rejects_OLD_shape` test beside the `parses_NEW_shape` one.

A contract drift can sit undetected for weeks; one test that asserts the old shape
is now rejected catches it on the first push.

### 4. Resource-count regression tests for subscriptions

**When** code subscribes to something (event listeners, watchers, connections),
**write** a test that baselines the count, exercises the full lifecycle, and
asserts the baseline is restored.

A `.off` that does not match its `.on` leaks silently; only a count assertion
surfaces it.

### 5. Extract pure functions; test those

**When** IO-free logic is embedded in an IO wrapper, **extract** it, type the
in/out, and unit-test the pure core, leaving the wrapper thin.

Testing logic through its IO wrapper needs an order-of-magnitude more expensive
fixture harness for no extra coverage of the logic itself.

### 6. A message and its verdict are driven by one test

**When** a printed sentence describes a verdict some other code decides (a guard's scope, a
gate's lane), **write** ONE test that drives the message and the verdict from one shared
battery of inputs and asserts they agree.

Asserting the message's text on its own is the counter-example this replaces: a substring
check passes for an input the sentence does not describe, so a clause reworded to deny the
verdict beside it - while keeping the word the assertion pinned - stays green. Driving both
over one battery fails on the input where they disagree, and names it.

## Name the ENTRY POINT before writing the test {#name-the-entry-point}

Beside naming the mutant, name the door the test goes in through - and write it down before
the first assertion.

**If the criterion describes a COMMAND, the test must enter that command.** A library import
standing in for a command is not evidence for a claim about the command, however green it is.
The wiring between an entry point and the function it calls is exactly the part an in-process
test does not exercise, and that is where this defect class lives.

Measured, not asserted. One sprint shipped `brief_fingerprint` with a passing acceptance test
and a feature that did not work: the test computed `brief_fingerprint(brief(...))` in-process
while the command that issues a brief never called it at all. The changelog and the commit
message both said the command emitted it. Three of five findings in that batch were the same
shape, and it cost a second review round - which is verification handed to the reviewer.

`verify_ac.py lane-check` reports a unit that changes a command where none of its verifiers
enters the entry point. Over this repository it reports 167 of 615 units, so the size of the
class is a number rather than an impression.

The question to ask, in this order:

1. What does the criterion claim - a library behaviour, or a command's?
2. Which door does my test go in through?
3. If those differ, the test is not evidence for the claim. Fix the test, or fix the claim.

## Name the mutant BEFORE writing the test {#name-the-mutant-first}

A mutation run proves a test can fail. This is the habit that makes it pass first time.

**In the test's docstring, state the production change the test must fail on. Then write the
test to fail on it.** If the mutant cannot be named, there is nothing to test yet.

The rule is measured, not asserted. One sprint returned five REJECTs across five reviews with
the production code right in most of them - an evidence problem, not a code-quality one, and
the two need different remedies. About two thirds of every finding was a test that passes
identically whether the feature is present or absent, from eight distinct mechanisms:

| Mechanism | What it looks like |
| --- | --- |
| Bypassing the surface under test | a hand-built `argparse.Namespace`, hiding a required-flag defect |
| Asserting text the code supplies for free | a `def` line carrying the call site's own string |
| A fixture shape the product cannot produce | the state asserted is unreachable in practice |
| A TYPE lacking the state under test | the assertion is vacuous for that type |
| An exception type two guards both raise | the test cannot say which one fired |
| Testing the helper, not the caller | five findings in ONE sprint were this alone |
| A whole-file assertion | an unrelated sentence satisfies it |
| A positive control already passing | it proves nothing about the change |

Every one is visible **on the page**, before any mutation run, if the question is asked in that
order. Two rules follow directly:

- **Test the surface the user invokes** - the command, not the helper it delegates to.
- **For every reader you add, name its writer.** A reader requiring a key nothing emits is a
  dead path, and the question costs one line.

**The honest limit of a pre-implementation design review:** it catches the two structural
classes above (the guard placed in the library while the unguarded read stayed in the command;
the reader requiring a key no writer emits) and it is cheap. It cannot see a test that does not
exist yet, so it addresses roughly a third of this and is not a general cure.

## Mechanisation and its boundary

Per the determinism doctrine ([LL0008](../lessons/_index.md)), heuristic 2 is
enforced, not left as prose an agent may forget: `audit` raises
`missing-regression-test` for a bug at a terminal status (Fixed/Verified/Closed/...)
whose recorded tests carry no `regression`/`integration`/`e2e` signal.

The signal is a **name-level** heuristic: it confirms a test of that level is
*named*, it cannot prove the test truly exercises the seams. That judgement stays
with the review code leg ([LL0005](../lessons/_index.md)). Heuristics 1 and 3 are
surfaced as AC stubs in the test-spec template (`templates/core/test-spec.md`) so a
generated spec prompts for them; heuristics 4 and 5 stay advisory here.

## See also

- `reference-test-spec.md`, `reference-verify.md` - the test-spec and AC-verifier workflows
- `reference-test-best-practices.md` - verification-depth tiers
- Lessons: [LL0005](../lessons/_index.md) (a review set includes a code leg),
  [LL0008](../lessons/_index.md) (deterministic tools fail loud),
  [LL0009](../lessons/_index.md) (a silent misleading failure - the class these tests catch)
