# EP0234: The specs learn about a shipped gate, and the guards that say so can fail

> **Status:** Draft
> **Derived Point Total:** 16
> **Parent:** CR0536
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0536. Delivers the work CR0536 requested.

## Story Breakdown

- [ ] [US0764: A verb that gains a refusal fails a spec lane until the TRD's gate inventory names it](../stories/US0764-a-verb-that-gains-a-refusal-fails-a.md)
- [ ] [US0765: The TSD's test-strategy rows for a shipped gate are DERIVED from the same source](../stories/US0765-the-tsd-s-test-strategy-rows-for-a.md)
- [ ] [US0766: Each of BG0457's four spec-agreement guards is shown RED under the mutation its criterion names](../stories/US0766-each-of-bg0457-s-four-spec-agreement-guards.md)
- [ ] [US0767: The lane regenerates and DIFFS rather than searching for prose](../stories/US0767-the-lane-regenerates-and-diffs-rather-than-searching.md)
- [ ] [US0768: The count of shipped refusing verbs not named in the spec is reported as a number](../stories/US0768-the-count-of-shipped-refusing-verbs-not-named.md)

## Acceptance Criteria (Epic Level)

- [ ] A verb that gains a refusal causes a spec lane to fail until the TRD's gate inventory names it, and that inventory is GENERATED from the contract reporter rather than typed
- [ ] The TSD's test-strategy rows for a shipped gate are derived from the same source, so a sprint plan reading the TSD learns about a bar the tooling will actually apply
- [ ] The spec-agreement guards can FAIL: each of BG0457's four is shown red under the mutation its criterion names, and a guard satisfied by a Revision History row describing the change is refused - the defect that recurred independently on US0567
- [ ] The lane regenerates and diffs rather than searching for prose, so a claim cannot be satisfied by text elsewhere in the file
- [ ] The count of shipped refusing verbs NOT named in the spec is reported, so the gap is a number that can be driven to zero rather than an impression

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
