# US0470: sprint batch swap trades units in one recorded call, in the house id grammar, reporting whether the points balanced

> **Status:** Done
> **Closed with findings in:** BG0497 - AC5's verifier never invokes batch swap; two named grammar forms do not exist
> **Delivers:** CR0441
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py, .claude/skills/sdlc-studio/scripts/tests/test_cli_grammar.py, changelog.d/US0470.md
> **Epic:** EP0171
> **Points:** 3

## User Story

**As a** operator rebalancing a sprint that has met reality
**I want** a single swap call that takes named units out while bringing one in and tells me whether the sizes balanced
**So that** a trade is one recorded decision rather than two blind calls that cannot see each other

## Acceptance Criteria

### AC1: AC1: one call applies both sides, records them as one swap, and lands exactly what drop-then-add would

- **Given** two identical open runs holding the outgoing units
- **When** one runs `sprint.py batch swap <IN_ID> --out <ID> --out <ID> --reason "..."` and the other runs the equivalent drops followed by the add
- **Then** both end with the same batch and the same capacity line and totals, and the swapped run's `batch_changes` carries the drops and the add linked as one swap entry with the reason - the composite verb and the primitives cannot diverge
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::SwapTests::test_swap_records_one_pair_and_matches_the_drop_then_add_equivalent
- **Verified:** yes (2026-08-02)

### AC2: AC2: a swap that does not balance warns with the points delta and still applies

- **Given** an open run and a swap whose incoming points exceed the outgoing points
- **When** the swap runs
- **Then** it applies, exits 0, and the output states the points delta and warns that the totals did not balance; an equal-points swap over the same fixture reports balanced with no warning
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::SwapTests::test_an_unbalanced_swap_warns_with_the_delta_and_a_balanced_one_does_not
- **Verified:** yes (2026-08-02)

### AC3: AC3: an outgoing unit that is not in the batch refuses before anything is written

- **Given** an open run and a swap naming one resident and one absent outgoing unit
- **When** the swap runs
- **Then** it exits non-zero naming the absent unit, and run-state.json is byte-identical to its pre-call state - no half-applied swap and no batch_changes entry
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::SwapTests::test_an_absent_out_unit_refuses_atomically_and_changes_nothing
- **Verified:** yes (2026-08-02)

### AC4: AC4: a swap without a reason is refused

- **Given** an open run and a swap with every id resolvable but no `--reason`
- **When** the swap runs
- **Then** it exits non-zero saying a drop inside a swap is still a recorded drop, and run-state.json is unchanged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::SwapTests::test_a_swap_without_a_reason_is_refused
- **Verified:** yes (2026-08-02)

### AC5: AC5: the swap takes ids in the house grammar and joins the conformance sweep

- **Given** the shipped parser: both sides of the trade as flags, `--out` and `--in`, each repeatable and each accepting a comma list - the house grammar `sdlc_md.split_id_list` defines
- **When** `swap --out A --out B --in C` and `swap --out A,B --in C` are run THROUGH THE CLI against a temp run
- **Then** both reach the identical batch and record the identical outgoing set, and `batch swap` is registered in test_cli_grammar's conformance sweep so a future id verb that reinvents the grammar fails it. A literal ID_VERBS row does not fit because `resolve_ids` hard-reads the `--id`/`--ids` pair and swap carries a second list, so the sweep gains a second table rather than the verb being left uncovered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::SwapTests::test_the_out_list_accepts_every_house_form_identically
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
| 2026-08-11 | Claude Opus 5 (BG0497) | AC5 corrected to the grammar that shipped. It named a positional incoming id and an `--outs` alias, and neither was built: the positional would collide with the `id` positional `drop`/`add` use for a different thing, and `--outs` would be a second spelling of a list the comma form already covers - the second grammar the conformance sweep exists to prevent. What the criterion asserts is unchanged and now stronger: both house forms are driven through the CLI rather than read off `split_id_list` beside an unused parser, so a swap dispatch that never runs no longer passes it |
