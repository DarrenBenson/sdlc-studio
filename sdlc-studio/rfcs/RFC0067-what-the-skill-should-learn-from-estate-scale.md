# RFC-0067: What the skill should learn from estate-scale autonomous delivery: impact analysis before refine, tests before brownfield change, runtime inputs and running-app evidence

> **Status:** Accepted
> **Forced-override:** 2026-11-17: --force waived 1 gate(s) on Accepted - RFC0067 cannot be Accepted: its status is DERIVED from its children, and 4 is/are not yet resolved: CR0735 (Proposed), CR0736 (Proposed), CR0737 (Proposed), CR0738 (Proposed). Finish or close them first
> **Decomposed-into:** CR0735, CR0736, CR0737, CR0738
> **Evidence:** competitor review 2026-11-17: published accounts of a commercial autonomous-delivery platform (Blitzy), chiefly its CEO and CTO interview on The Cognitive Revolution (January 2026) and the Quesma audit of its SWE-Bench Pro run; compared against this skill by grep
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T21:37:59Z

## Summary

A review of a commercial autonomous-delivery platform found four practices this skill lacks, each needing a design choice before it becomes work. First, impact analysis: before any plan the platform reports what a request touches and asks about near-identical modules, where `refine` here decomposes a request without consulting the repo map. Second, test harness first: on legacy code the platform builds the automated suite before it changes anything, where the brownfield runbook validates a generated spec against tests but has no stage that pins existing behaviour ahead of a change. Third, runtime inputs: the platform reads database schema, stored procedures and traces because some business logic exists only at run time, where generate mode reads source files alone. Fourth, running-app evidence: the platform drives the built application and attaches screenshots, where the verification depth tiers here are advice no gate reads. The skill is ecosystem-neutral, stdlib-only and priced per point, so none of these can be copied as built.

## Design Options

- **Impact analysis is advisory: `refine` prints, per proposed story, the files that import its Affects and any near-duplicate symbols the repo map finds, and decomposes regardless; or it refuses a breakdown whose Affects leave a known dependant uncovered**
- **Tests before brownfield change is a runbook stage with a readiness warning: a story whose Affects have no test that reaches them is reported at plan time; or it is a gate that refuses such a story until a pinning test exists**
- **Runtime inputs are files: generate mode accepts schema dumps, stored-procedure source and trace exports placed in a declared folder, and never connects to a running system; or the skill ships connectors**
- **Running-app evidence is orchestrate-only: a criterion may name a `Verify: app` command the project supplies, and the review records the screenshots or log it produced; or the skill ships a browser driver**

## Recommendation

Take the first half of each option. Advisory impact analysis costs one repo-map query per story and removes the surprise the platform's own example describes. A plan-time warning for unpinned brownfield code is cheap and can be armed to refuse by config later. Runtime inputs as files keep the skill off production systems and free of third-party drivers. Orchestrate-only app evidence follows the pattern `deploy` already uses. Do not adopt the platform's embedding graph or its many-agent iteration: at one repository's scale the deterministic map is cheaper and reproducible, and iteration by volume runs against the cost bar in RFC0062.

## Decision

**The first half of each option is taken** (operator, 2026-11-17, D0516 to D0518). Impact analysis at refine is advisory. A story that changes code no test reaches is warned about at plan time, and a project may arm that to refuse. Runtime inputs are files in a declared folder, and running-app evidence comes from a project-supplied command. The skill ships no connector and no browser driver, and adopts neither an embedding graph nor iteration by volume.

**Spawned CRs:** CR0735, CR0736, CR0737, CR0738.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Choose between: Impact analysis is advisory: `refine` prints, per proposed story, the files that import its Affects and any near-duplicate symbols the repo map finds, and decomposes regardless; or it refuses a breakdown whose Affects leave a known dependant uncovered, Tests before brownfield change is a runbook stage with a readiness warning: a story whose Affects have no test that reaches them is reported at plan time; or it is a gate that refuses such a story until a pinning test exists, Runtime inputs are files: generate mode accepts schema dumps, stored-procedure source and trace exports placed in a declared folder, and never connects to a running system; or the skill ships connectors or Running-app evidence is orchestrate-only: a criterion may name a `Verify: app` command the project supplies, and the review records the screenshots or log it produced; or the skill ships a browser driver | Resolved: Take the first half of each option (operator, 2026-11-17): advisory impact analysis (D0516), a plan-time warning for unpinned code that config can arm (D0517), runtime inputs as files and app evidence from a project command (D0518) -> CR0735, CR0736, CR0737, CR0738 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
| 2026-11-17 | rfc resolve (operator decision) | resolve: D1 - Take the first half of each option (operator, 2026-11-17): advisory impact analysis (D0516), a plan-time warning for unpinned code that config can arm (D0517), runtime inputs as files and app evidence from a project command (D0518) |
| 2026-11-17 | transition set --force | forced RFC0067 -> Accepted, waiving 1 gate(s): RFC0067 cannot be Accepted: its status is DERIVED from its children, and 4 is/are not yet resolved: CR0735 (Proposed), CR0736 (Proposed), CR0737 (Proposed), CR0738 (Proposed). Finish or close them first |
