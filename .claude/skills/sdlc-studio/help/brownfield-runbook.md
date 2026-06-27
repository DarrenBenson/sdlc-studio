<!--
Load when: adopting an existing codebase, or asking "how do I get a spec out of this code?"
Dependencies: SKILL.md (always loaded first)
Related: help/getting-started.md, reference-philosophy.md, help/prd.md, reference-verify.md
-->

# Brownfield Runbook - From Existing Code to a Validated Spec

## You can just ask

SDLC Studio is model-invoked - say it in plain language:

| Just say... | Runs |
| --- | --- |
| "Set this project up around the existing code" | `/sdlc-studio init --detect` |
| "Extract the spec from this code" | `/sdlc-studio prd generate` |
| "Break the extracted PRD into epics" | `/sdlc-studio epic` |
| "Write stories with testable acceptance criteria" | `/sdlc-studio story --epic EPxx` |
| "Prove the spec against the real code" | `/sdlc-studio test-spec` then `code verify` |
| "Check the backlog is wired and clean" | `/sdlc-studio reconcile` then `validate` |

The canonical order for adopting an existing codebase: extract a specification, then **validate it
against the running code** before you trust it. This is the part that makes generate mode different
from documentation - read the create-vs-generate distinction in `reference-philosophy.md` first.

## Generate mode is a migration blueprint, not documentation

The output is a complete, testable specification - detailed enough to rebuild the system in another
stack, refactor internals freely, or modernise a legacy codebase piece by piece. A generated
specification is worthless until validated: extract the spec, write tests from it, run those tests
against the existing code, and only when they pass do you have a valid spec. If a test fails, either
the spec is wrong (fix the spec) or the code has a bug (record it as a known issue).

Acceptance criteria must be implementation-ready, not vague. "Search works" is documentation;
"GET /search?q=alice returns alice-smith and alice-wong, sorted by match_score descending, exact
slug match >= 0.9" is a specification a test can check.

## 1. Extraction - code to a validated backlog

| # | Step | Command | Produces / unblocks |
| --- | --- | --- | --- |
| 1 | **Adopt the repo** | `init --detect` | the `sdlc-studio/` tree and indexes, fitted around the code already present |
| 2 | **Extract the PRD** | `/sdlc-studio prd generate` | `prd.md` reverse-engineered from the implementation - features, behaviours, NFRs |
| 3 | **Technical + test design** | `/sdlc-studio trd` then `tsd` | `trd.md`, `tsd.md` - the architecture as built and the test strategy |
| 4 | **Epics** | `/sdlc-studio epic` | epics decomposed from the extracted PRD |
| 5 | **Stories** | `/sdlc-studio story --epic EPxx` | stories with implementation-ready Given/When/Then and DSL `Verify:` lines |
| 6 | **Test specs** | `/sdlc-studio test-spec` | every AC mapped to a named test case (the AC-to-test bridge) |
| 7 | **Test code** | `/sdlc-studio test-automation` | the executable tests scaffolded from the spec |
| 8 | **Validate against the code** | `/sdlc-studio code verify` | the `Verify:` lines run against the real implementation - the spec is now trusted |
| 9 | **Reconcile + validate** | `/sdlc-studio reconcile` then `validate` | a wired, drift-free, reviewable backlog |

Record load-bearing decisions as you discover them with `decisions.py add` (the conventions the code
already follows - error-envelope shape, ID scheme, migration strategy). Delegated agents read it as
their handoff context.

## 2. Then change with confidence

Once the spec is validated, the implementation is free to change as long as the tests still pass:

- **Refactor or modernise** - tests preserve behaviour while internals change.
- **Migrate stacks** - the spec, not the code, is the source of truth; rebuild in another language
  and validate against the same criteria.
- **Hand to the sprint loop** - with working tests and a runnable gate, `sprint --epic EPxx --goal
  done` can drive new work on the adopted codebase.

> **Rule: do not trust a generated spec until its tests pass against the existing code.** An
> unvalidated extraction is a guess, not a specification.

## See Also

- `help/getting-started.md` - the greenfield path (empty repo to shipped)
- `reference-philosophy.md` - the create-vs-generate distinction and the validation requirement
- `help/prd.md` - `prd generate` in detail
- `reference-verify.md` - the test-spec AC-to-test bridge and the `Verify:` DSL
