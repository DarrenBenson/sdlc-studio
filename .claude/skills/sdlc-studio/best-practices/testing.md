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
