# SDLC Studio Reference - Decisions

Cross-stage decision guidance, impact analysis, and validation checkpoints.

<!-- Load when: Any workflow step needs decision guidance or validation -->

## Related References

| Document | Content |
|----------|---------|
| `reference-prd.md, reference-trd.md, reference-persona.md` | PRD, TRD, Persona workflows |
| `reference-epic.md, reference-story.md, reference-bug.md` | Epic, Story, Bug workflows |
| `reference-code.md` | Code plan, implement, review workflows |
| `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` | Test workflows |

---

# Decision Timeline {#decision-timeline}

Decisions flow downstream through the pipeline. Early decisions constrain later choices.

```
PRD                 TRD                 Epic                Story               Plan                Test-Spec
 │                   │                   │                   │                   │                    │
 │ Project scope     │ Architecture      │ Feature           │ Implementation    │ Approach           │ Coverage
 │ NFRs              │ Tech stack        │ boundaries        │ approach          │ TDD/Test-After     │ validation
 │ Personas          │ Patterns          │ Dependencies      │ Edge cases        │ Phasing            │ AC mapping
 │ Constraints       │ Data model        │ Risks             │ AC detail         │                    │
 │                   │                   │                   │                   │                    │
 └──────────────────►└──────────────────►└──────────────────►└──────────────────►└───────────────────►│
```

**Key principle:** Information at each stage MUST propagate to downstream stages. Losing context causes implementation errors.

---

# Decision Impact Matrix {#decision-impact-matrix}

How decisions at each stage constrain downstream choices.

## PRD Decisions {#prd-decisions}

| Decision | Impacts | Guidance |
|----------|---------|----------|
| Project type (web, CLI, API) | TRD architecture, story AC format, test approach | Web apps need frontend AC; APIs need contract tests |
| NFR: Performance target | Story AC, test fixtures, plan considerations | "Response <200ms" propagates to all API stories |
| NFR: Security level | TRD auth pattern, story validation AC, test cases | High security = auth tests, input validation AC |
| NFR: Scalability | TRD architecture, epic boundaries | Microservices = more epics, more integration tests |
| Persona definitions | Story persona binding, AC perspective | Missing persona = vague, untestable stories |
| Constraint: Memory limit | Story AC, test assertions | "Agent memory <50MB" must appear in relevant stories |
| Constraint: Browser support | Story AC, test matrix | IE11 support = polyfill AC, cross-browser tests |

## TRD Decisions {#trd-decisions}

| Decision | Impacts | Guidance |
|----------|---------|----------|
| Architecture pattern | Epic boundaries, deploy strategy, test types | Monolith = fewer epics; microservices = contract tests |
| Database choice | Story data AC, test fixtures, migration stories | NoSQL = eventual consistency AC; SQL = transaction AC |
| Language/framework | Plan best practices, test framework | Python/FastAPI = pytest; TypeScript/React = vitest |
| API style (REST/GraphQL) | Story AC format, test approach | REST = endpoint AC; GraphQL = query AC |
| Auth mechanism | Story auth AC, test fixtures | JWT = token validation tests; OAuth = flow tests |
| Caching strategy | Story cache AC, test invalidation | Redis = cache invalidation tests needed |

## Epic Decisions {#epic-decisions}

| Decision | Impacts | Guidance |
|----------|---------|----------|
| Feature boundaries | Story scope, test spec scope | Clear boundaries prevent story overlap |
| Epic dependencies | Story ordering, plan phasing | Blocked-by must resolve before story starts |
| Risk identification | Story dependencies, plan mitigations | Risks MUST propagate to affected stories |
| Success metrics | Story AC, test assertions | Metrics define what tests validate |

## Story Decisions {#story-decisions}

| Decision | Impacts | Guidance |
|----------|---------|----------|
| AC detail level | Test complexity, plan precision | Vague AC = untestable; precise AC = clear tests |
| Edge case coverage | Test case count, plan handling | Documented edge cases = required test cases |
| Persona binding | AC perspective, test scenarios | Wrong persona = wrong validation focus |
| Dependency identification | Plan ordering, implementation sequence | Missing deps = blocked implementation |

## Plan Decisions {#plan-decisions}

| Decision | Impacts | Guidance |
|----------|---------|----------|
| TDD vs Test-After | Artifact creation order, implementation rhythm | See TDD Decision Tree below |
| Implementation phasing | Test granularity, review checkpoints | Small phases = easier debugging |
| Library choices | Test mocking strategy, fixture design | External libs = mock boundaries needed |

---

# TDD vs Test-After Decision Tree {#tdd-decision-tree}

**Default:** Plan recommends based on story characteristics. User can override.

```
                            Story Characteristics
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              Clear AC?        Complex?        Exploratory?
                    │               │               │
              ┌─────┴─────┐   ┌────┴────┐    ┌────┴────┐
              │           │   │         │    │         │
             Yes         No  Yes       No   Yes        No
              │           │   │         │    │         │
              │           │   │         │    │         │
         ┌────┴────┐      │   │         │    │         │
         │         │      │   │         │    │         │
    API Story?  UI-heavy? │   │         │    │         │
         │         │      │   │         │    │         │
        Yes       Yes     │   │         │    │         │
         │         │      │   │         │    │         │
        TDD    Test-After │  TDD   Test-After│    Test-After
                          │                  │
                     Test-After         Test-After
```

## Prefer TDD When {#prefer-tdd}

| Condition | Rationale |
|-----------|-----------|
| Story has >5 edge cases | Tests catch edge cases before implementation |
| AC involves complex business rules | Tests define expected behaviour precisely |
| API contracts are well-defined | Contract tests drive implementation |
| Refactoring existing code | Tests ensure behaviour preserved |
| Critical path functionality | Tests provide safety net |
| Story AC is clear and stable | Tests won't need constant rewriting |

## Prefer Test-After When {#prefer-test-after}

| Condition | Rationale |
|-----------|-----------|
| Exploratory implementation | Design may evolve during coding |
| UI-heavy stories | Visual testing harder to specify upfront |
| Integration-focused work | Need running system to test against |
| Tight deadline with clear requirements | Faster initial implementation |
| AC may evolve during implementation | Avoid rewriting tests |
| Prototyping new features | Tests constrain exploration |

## Override Flags {#override-flags}

| Flag | Effect |
|------|--------|
| `--tdd` | Force TDD even if plan recommends Test-After |
| `--no-tdd` | Force Test-After even if plan recommends TDD |

**Plan generation:** When creating a plan, assess story characteristics and set `Recommended Approach:` to TDD, Test-After, or Hybrid with rationale.

---

# Status Transition Rules {#status-transition-rules}

**"Done" is always a user decision, never auto-assigned.**

This applies to all artifact types:
- **Epics:** Even when all stories complete, user confirms Done
- **Stories:** Even when all AC met, user confirms Done

**Rationale:** "Done" implies no further work needed - a business judgment. The system suggests Done based on criteria, but the user decides.

**Brownfield projects:** Use "Ready" not "Done" - user may want to rebuild, refactor, or add coverage. "Done" implies no work needed, which is a user judgment.

---

# Ready Status Criteria {#ready-status-criteria}

Explicit checklists for when each artifact type is ready for the next stage.

## PRD Ready {#prd-ready}

PRD can proceed to Epic generation when:

- [ ] Problem Statement clearly defines the problem being solved
- [ ] All personas referenced exist in personas.md
- [ ] Feature Inventory has no TBD items
- [ ] NFRs have measurable targets (not "fast", "secure" but "< 200ms", "OWASP Top 10")
- [ ] Constraints are specific and verifiable
- [ ] Success Metrics defined with measurement methods

**Blocking conditions:**
- TBD in any feature description
- NFR without measurable target
- Referenced persona doesn't exist

## TRD Ready {#trd-ready}

TRD can proceed to Epic generation when:

- [ ] Architecture pattern selected with rationale
- [ ] Technology stack specified (language, framework, database)
- [ ] All PRD NFRs addressed with technical approach
- [ ] Data model defined (at least high-level entities)
- [ ] Integration points identified
- [ ] Security approach documented
- [ ] No unresolved technical questions

**Blocking conditions:**
- Architecture pattern not selected
- PRD NFR not addressed
- Critical technical question unresolved

## Epic Ready {#epic-ready}

Epic can proceed to Story generation when:

- [ ] Summary describes user value (not technical implementation)
- [ ] Acceptance Criteria are observable outcomes (not implementation details)
- [ ] All dependencies identified with status
- [ ] Risks documented with mitigations
- [ ] Affected personas listed with impact description
- [ ] No critical blocking dependencies unresolved

**Blocking conditions:**
- AC uses implementation language ("uses Redis", "calls API")
- Dependency marked Blocked with no resolution plan
- Risk without mitigation strategy

## Story Ready {#story-ready}

Story can proceed to Planning/Implementation when:

- [ ] All AC in Given/When/Then format with concrete values
- [ ] No TBD or placeholder text in AC
- [ ] Persona reference valid (exists in personas.md)
- [ ] Edge cases table complete (minimum 8 for API stories)
- [ ] No ambiguous language ("should", "might", "handles errors")
- [ ] All critical Open Questions resolved
- [ ] Dependencies identified with status

**Blocking conditions:**
- TBD in acceptance criteria
- Edge case count below minimum (8 for API, 5 for others)
- Ambiguous language in AC (see Ambiguous Language Detection)
- Critical Open Question unresolved

## Plan Ready {#plan-ready}

Plan can proceed to Implementation when:

- [ ] All story ACs mapped to implementation phases
- [ ] All edge cases have handling strategy documented
- [ ] Open questions resolved (all checkboxes checked)
- [ ] API contracts verified (for API-consuming code)
- [ ] Library documentation queried via Context7
- [ ] Best practices loaded for language

**Blocking conditions:**
- AC not mapped to any phase
- Edge case without handling strategy
- Open question unchecked
- API-consuming code without verified contract

## Test-Spec Ready {#test-spec-ready}

Test-Spec can proceed to Automation when:

- [ ] All story ACs have at least one test case
- [ ] AC Coverage Matrix shows no UNCOVERED ACs
- [ ] Test data fixtures defined for all test cases
- [ ] No placeholder assertions ("verify result", "check response")
- [ ] Test types appropriate for story (unit for logic, API for endpoints)

**Blocking conditions:**
- AC without mapped test case
- Placeholder assertion text
- Missing fixture for test case

---

# Ambiguous Language Detection {#ambiguous-language}

These phrases indicate specification gaps. Replace before marking Ready.

| Avoid | Replace With |
|-------|--------------|
| "handles errors" | "Returns 400 with `{\"detail\": \"validation failed\"}`" |
| "returns data" | "Returns 200 with `{\"id\": string, \"name\": string, ...}`" |
| "validates input" | "Rejects if slug < 2 chars, returns 422" |
| "appropriate response" | Exact status code and body |
| "as expected" | Specific observable outcome |
| "correctly" | Measurable criteria |
| "should work" | Specific pass condition |
| "might fail" | Specific failure condition and handling |
| "processes request" | Specific transformation with I/O shapes |
| "updates state" | Exact state changes with before/after |

**Detection rule:** Grep story AC for these phrases. Any match = not Ready.

---

# Validation Checkpoints {#validation-checkpoints}

When to validate decisions and what to check.

## PRD → Epic Validation {#prd-epic-validation}

**Check:** Do epics capture all PRD features?

| Validation | Method |
|------------|--------|
| Feature coverage | Every PRD feature appears in at least one Epic |
| NFR inheritance | Epic technical considerations reference PRD NFRs |
| Persona coverage | Epic affected personas match PRD personas |
| Constraint propagation | PRD constraints appear in Epic scope or AC |

**Tool support:** `/sdlc-studio status` shows PRD-to-Epic coverage.

## Epic → Story Validation {#epic-story-validation}

**Check:** Do stories cover all Epic AC?

| Validation | Method |
|------------|--------|
| AC coverage | Every Epic AC maps to at least one Story AC |
| Risk inheritance | Epic risks appear in Story dependencies or edge cases |
| Dependency inheritance | Epic dependencies propagate to Story dependencies |
| Persona consistency | Story persona matches Epic affected personas |

**Tool support:** `/sdlc-studio story review` checks AC coverage.

## Story → Plan Validation {#story-plan-validation}

**Check:** Does plan address all story requirements?

| Validation | Method |
|------------|--------|
| AC mapping | Every Story AC mapped to implementation phase |
| Edge case coverage | Every Story edge case has handling strategy |
| Technical notes | Plan considers Story technical notes |
| Dependency awareness | Plan accounts for Story dependencies |

**Tool support:** `/sdlc-studio code plan` validates AC coverage.

## Story → Test-Spec Validation {#story-test-spec-validation}

**Check:** Do tests cover all story AC?

| Validation | Method |
|------------|--------|
| AC coverage | AC Coverage Matrix shows all ACs covered |
| Edge case testing | Story edge cases have corresponding test cases |
| Error scenario coverage | Story error scenarios have test cases |

**Tool support:** `/sdlc-studio test-spec` generates AC Coverage Matrix.

## Test → Story Validation (Backward Traceability) {#test-story-validation}

**Check:** Do test results reflect in story status?

| Test Result | Story Update |
|-------------|--------------|
| All AC tests pass | Story remains Done |
| Any AC test fails | Story marked Regression |
| New test added | Story AC coverage updated |

**Tool support:** `/sdlc-studio code test` propagates results to story status.

## Story Terminal Status Validation {#story-terminal-validation}

**Check:** When a story reaches any terminal status (Done, Won't Implement, Deferred, Superseded), verify that the [Story Completion Cascade](reference-outputs.md#story-completion-cascade) was executed correctly.

| Validation | Method | Pass Condition |
|------------|--------|----------------|
| Plan cascade | Check plan's `> **Status:**` header | Matches target from cascade table |
| Test spec cascade | Check spec's `> **Status:**` header | Matches target from cascade table |
| Workflow cascade | Check workflow's `> **Status:**` header | Matches target from cascade table |
| Index counts current | Compare `_index.md` counts with file statuses | Counts match reality |
| Reason documented | Check story file for reason (non-Done terminals only) | Reason present for Won't Implement/Deferred/Superseded |

**Tool support:** `/sdlc-studio status --full` detects stale statuses where a story is terminal but linked artifacts are not. See `help/status.md` → Index Reconciliation.

---

# Cross-Story Dependency Detection {#cross-story-dependencies}

Identifying dependencies between stories based on code patterns.

## Detection Patterns {#detection-patterns}

| Pattern | Indicates | Dependency Type |
|---------|-----------|-----------------|
| Config schema defined in Story A, used in Story B | B depends on A | Schema |
| API endpoint in Story A, called by Story B | B depends on A | API |
| Data model in Story A, referenced by Story B | B depends on A | Data Model |
| Service in Story A, injected in Story B | B depends on A | Service |

## Workflow Change {#workflow-change}

Story generation (`/sdlc-studio story`) must:

1. Detect config schemas defined in other stories
2. Detect API calls to other stories
3. Auto-populate dependency table
4. Warn if dependent story not Done

Example output in story template:

```markdown
## Dependencies

### Story Dependencies

| Story | Dependency Type | What's Needed | Status |
|-------|-----------------|---------------|--------|
| US0013 | Schema | NotificationsConfig | Done |
| US0023 | API | GET /api/settings | In Progress |

### Detected Automatically

- US0013 defines `NotificationsConfig` schema used by this story
- US0023 provides `/api/settings` endpoint this story consumes

**Warning:** US0023 is not Done. This story may be blocked.
```

---

# Inherited Constraints {#inherited-constraints}

How constraints flow through the pipeline.

## From PRD to Epic {#prd-to-epic}

| PRD Section | Epic Section | What Inherits |
|-------------|--------------|---------------|
| NFRs - Performance | Technical Considerations | Response time targets |
| NFRs - Security | Technical Considerations | Auth requirements |
| NFRs - Scalability | Technical Considerations | Load handling approach |
| Constraints | Scope - Out of Scope | Hard limits |
| Success Metrics | Success Metrics | Measurement targets |

## From TRD to Epic {#trd-to-epic}

| TRD Section | Epic Section | What Inherits |
|-------------|--------------|---------------|
| Architecture Pattern | Technical Considerations | Pattern constraints |
| Technology Stack | Technical Considerations | Framework constraints |
| Data Model | Technical Considerations | Schema constraints |

## From Epic to Story {#epic-to-story}

| Epic Section | Story Section | What Inherits |
|--------------|---------------|---------------|
| Risks | Edge Cases | Risk scenarios |
| Dependencies | Dependencies | Blocking items |
| Success Metrics | Test Scenarios | Validation targets |
| Acceptance Criteria | Scope context | Boundary awareness |

## From Story to Plan {#story-to-plan}

| Story Section | Plan Section | What Inherits |
|---------------|--------------|---------------|
| Edge Cases | Edge Cases (with handling) | Must all be addressed |
| Technical Notes | Technical Context | Implementation guidance |
| Dependencies | Dependencies | Ordering constraints |
| AC | Implementation Steps | Must all be covered |

## From Story to Test-Spec {#story-to-test-spec}

| Story Section | Test-Spec Section | What Inherits |
|---------------|-------------------|---------------|
| AC | Test Cases | One test per AC minimum |
| Edge Cases | Test Cases | Edge case tests |
| Error scenarios | Test Cases | Error handling tests |
| Technical Notes | Environment | Setup requirements |

---

# Workflow Checkpoints {#workflow-checkpoints}

Validation gates for automated workflow execution.

## Story Workflow Checkpoints {#story-workflow-checkpoints}

Each phase in `story implement` validates before proceeding:

### Phase 1: Plan {#phase-1-plan}

| Checkpoint | Validation |
|------------|------------|
| Story Ready | Status = Ready, all criteria met |
| Dependencies | All dependent stories Done |
| No blockers | No unresolved critical Open Questions |

**Failure:** Workflow pauses, reports missing criteria.

### Phase 2: Test Spec {#phase-2-test-spec}

| Checkpoint | Validation |
|------------|------------|
| Plan exists | Phase 1 completed successfully |
| AC coverage | All AC mappable to test cases |
| Fixtures defined | Test data requirements clear |

**Failure:** Workflow pauses, reports coverage gaps.

### Phase 3: Tests {#phase-3-tests}

| Checkpoint | Validation |
|------------|------------|
| Spec exists | Phase 2 completed successfully |
| Framework available | Test framework detected and working |
| Generation success | Tests compile/parse without errors |

**Failure:** Workflow pauses, reports generation errors.

### Phase 4: Implement {#phase-4-implement}

| Checkpoint | Validation |
|------------|------------|
| Plan loaded | Implementation plan available |
| Context7 queried | Library docs fetched |
| Best practices loaded | Language-specific guide read |

**Failure:** Workflow pauses, reports missing context.

### Phase 5: Verify {#phase-5-verify}

| Checkpoint | Validation |
|------------|------------|
| Tests exist | Test files from Phase 3 |
| All tests pass | No failures or errors |
| No warnings | Warnings treated as errors |

**Failure:** Workflow pauses, reports test failures.

### Phase 6: Review {#phase-6-review}

| Checkpoint | Validation |
|------------|------------|
| AC coverage | All AC verified in code |
| Edge cases | All edge cases handled |
| Best practices | No violations detected |

**Failure:** Workflow pauses, reports review issues.

### Phase 7: Check {#phase-7-check}

| Checkpoint | Validation |
|------------|------------|
| Lint passes | No lint errors remaining |
| Type check | Type checker passes (if applicable) |
| Manual verification | User confirms (if UI/API changes) |

**Failure:** Workflow pauses, reports quality issues.

---

## Epic Workflow Checkpoints {#epic-workflow-checkpoints}

### Pre-execution {#epic-pre-execution}

| Checkpoint | Validation |
|------------|------------|
| Stories exist | At least one Ready story |
| No cycles | Dependency graph is acyclic |
| Dependencies resolvable | No external blockers |
| Agentic wave analysis | If `--agentic`: `epic plan --agentic` must have run first |

### Per-story {#epic-per-story}

| Checkpoint | Validation |
|------------|------------|
| Dependencies Done | All story dependencies complete |
| Story Ready | Individual story meets Ready criteria |
| Story workflow | 7 phases complete successfully |

### Per-wave (agentic mode only) {#epic-per-wave}

| Checkpoint | Validation |
|------------|------------|
| No hub file conflicts | Stories in wave share no hub files |
| Wave tests pass | Full test suite after each wave completes |

### Post-execution {#epic-post-execution}

| Checkpoint | Validation |
|------------|------------|
| All stories Done | Every story in epic completed |
| Epic AC met | Epic acceptance criteria satisfied |
| User confirms | Epic marked Done by user decision |

---

## Checkpoint Recovery {#checkpoint-recovery}

When a checkpoint fails, workflow provides:

1. **Clear error message** - What failed and why
2. **Resolution steps** - How to fix the issue
3. **Resume command** - Exact command to continue

Example:
```
## Checkpoint Failed: Phase 5 - Verify

**Story:** US0024 - Action Queue API
**Error:** 2 of 15 tests failed

### Failed Tests
1. test_action_queue_empty
   - Expected: 200
   - Got: 500
   - Location: tests/test_action_queue_api.py:45

2. test_action_invalid_id
   - Expected: 404
   - Got: 422
   - Location: tests/test_action_queue_api.py:78

### To Resume
1. Fix the implementation or test expectations
2. Run: /sdlc-studio story implement --story US0024 --from-phase 5
```

---

# See Also

- `reference-prd.md, reference-trd.md, reference-persona.md` - PRD, TRD, Persona workflows
- `reference-epic.md, reference-story.md, reference-bug.md` - Epic, Story, Bug workflows
- `reference-code.md` - Code plan, implement, review workflows (includes workflow orchestration)
- `reference-tsd.md`, `reference-test-spec.md`, `reference-test-automation.md` - Test workflows
- `reference-philosophy.md` - Create vs Generate philosophy
