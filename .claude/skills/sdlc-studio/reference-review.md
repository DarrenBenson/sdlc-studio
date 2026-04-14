# SDLC Studio Unified Review Reference

Workflows for the unified document review command that analyses PRD, TRD, and TSD together.

## Overview

The unified review command runs document reviews across all three specification layers and checks cross-document consistency.

---

## /sdlc-studio review - Step by Step {#review-workflow}

### 1. Parse Arguments

| Flag | Effect | Default |
| --- | --- | --- |
| (none) | Run all document reviews | - |
| `--quick` | Use cached data, skip codebase analysis | false |
| `--focus prd` | Run only PRD review | all |
| `--focus trd` | Run only TRD review | all |
| `--focus tsd` | Run only TSD review | all |

### 2. Run Document Reviews

Execute reviews in sequence, collecting findings:

#### PRD Review

```text
1. Load sdlc-studio/prd.md
2. Scan codebase for feature implementation
3. Compare features against code
4. Calculate status percentages
5. Identify gaps and stale content
```

See `reference-prd.md#prd-review-workflow` for details.

#### TRD Review

```text
1. Load sdlc-studio/trd.md
2. Analyse architecture against implementation
3. Check ADRs are current
4. Verify tech stack matches reality
5. Identify drift from documented design
```

See `reference-trd.md#trd-review-workflow` for details.

#### TSD Review

```text
1. Load sdlc-studio/tsd.md
2. Parse coverage data (.coverage, lcov.info)
3. Check framework versions against package files
4. Verify CI/CD quality gates
5. Identify coverage and strategy gaps
```

See `reference-tsd.md#tsd-review-workflow` for details.

### 3. Cross-Document Consistency Check

Only in full mode (not `--quick`):

#### PRD → TRD Coverage

```text
For each PRD feature:
  - Check TRD has architecture section addressing it
  - Flag features without technical design
```

#### TRD → TSD Coverage

```text
For each TRD component:
  - Check TSD has test strategy for it
  - Flag components without test coverage plan
```

#### PRD NFRs → TSD Quality Gates

```text
For each PRD non-functional requirement:
  - Check TSD has corresponding quality gate
  - Examples:
    - PRD "p95 < 200ms" → TSD performance gate
    - PRD "99.9% uptime" → TSD availability gate
```

#### CR Staleness Check

```text
If sdlc-studio/change-requests/ exists:

For each CR with status "Proposed":
  - Check created date against today
  - If older than 14 days: flag as stale
  - Suggest: approve, reject, or defer

For each CR with status "In Progress":
  - Check linked epic statuses from "Linked Epics" section
  - If ALL linked epics Done: suggest marking CR Complete
  - If SOME Done: report progress (e.g. "2/3 linked epics Done")
```

### 3a. Persona Consultation (default when personas exist)

If `sdlc-studio/personas/` contains persona files and `--skip-personas` was NOT passed:

1. Load persona index (`sdlc-studio/personas/index.md`)
2. For each reviewed document, identify relevant personas from the consultation guide:
   - **PRD:** Darren (scope, priorities), Cora (API shape, errors), Webapp Dev (API docs, schema), HA (health, sensors)
   - **TRD:** Claude Code (patterns, testability), Marcus Johnson (architecture), Cora (error contracts)
   - **TSD:** Priya Sharma (coverage, risk), Claude Code (test structure, runnable locally)
3. Consult each relevant persona on the review findings from their perspective:
   - Does the implementation meet their stated needs?
   - Are their frustrations addressed?
   - Are their "push back" triggers present in the findings?
4. Append persona verdicts to the consolidated report under a "Persona Consultation" section
5. Flag persona concerns as priority actions

**Default behaviour:** When `sdlc-studio/personas/` exists and contains persona files, persona consultation runs automatically. Use `--skip-personas` to opt out. Use `--with-personas` to force consultation even when no persona files exist (uses archetype defaults).

### 3b. Auto-Apply Mechanical Fixes

After detecting findings, automatically apply fixes that are purely mechanical (not judgment calls):

**Auto-applied (no confirmation needed):**

- PRD feature status updates matching verified epic completion
- PRD AC checkboxes matching verified implementation
- Dependency table status corrections (fact, not judgment)
- Index summary count recalculations
- Story/epic index status entries matching file statuses
- Epic AC checkboxes for criteria verified against the codebase
- Epic story breakdown checkboxes matching story statuses

**Reported only (requires user judgment):**

- Spec-to-code naming drift (e.g. interface names in TRD vs code)
- TSD test tree vs actual test file structure
- Content accuracy issues (stale descriptions, outdated architecture claims)
- Status transitions to Done (always a user decision)

To skip auto-fix: `--no-fix` flag.

### 4. Update Review State and Metadata

**CRITICAL:** After generating findings, update `sdlc-studio/.local/review-state.json` to track the review. This ensures the status dashboard recognises reviews have been conducted.

```text
1. Create sdlc-studio/.local/ directory if it doesn't exist
2. Load existing review-state.json (or create empty structure)
3. For each reviewed document (prd, trd, tsd):
   a) Set artifacts.{doc}.last_reviewed = current ISO timestamp
   b) Set artifacts.{doc}.last_modified = file's git log timestamp
   c) Set artifacts.{doc}.review_findings_ref = RV{NNNN} ID
4. Add review entry to reviews.{RV_ID} with timestamp and findings summary
5. Write updated review-state.json
6. For each reviewed document that was modified (status updates, AC checkboxes, auto-fixes):
   a) Update `**Last Updated:**` date in the document header to today's date
   b) Add a changelog/revision history entry summarising the review changes
   c) Format: `| {date} | Claude | {type} review: {summary of changes} |`
5. Write updated review-state.json
```

**review-state.json schema:** See `reference-outputs.md#review-state-json`.

### 5. Generate Consolidated Report

```text
══════════════════════════════════════════════════════════
                   DOCUMENT REVIEW SUMMARY
══════════════════════════════════════════════════════════

📋 PRD REVIEW                          ▓▓▓▓▓▓▓▓░░ 85%
   Features: 14 defined
   Status: 10 Complete | 2 Partial | 1 Stubbed | 1 Not Started
   ⚠️ 2 features need attention

📐 TRD REVIEW                          ▓▓▓▓▓▓▓▓▓░ 92%
   Components: 8 documented
   ADRs: 5 (1 new since last review)
   ✅ Architecture current

🧪 TSD REVIEW                          ▓▓▓▓▓▓▓░░░ 78%
   Coverage Target: 90% (Actual: 78%)
   ⚠️ 3 gaps identified

──────────────────────────────────────────────────────────
📝 CHANGE REQUESTS
   Proposed: 2 (1 stale > 14 days)
   In Progress: 1 (all epics Done -- suggest close)
   Complete: 7

──────────────────────────────────────────────────────────
🔗 CROSS-DOCUMENT CONSISTENCY

   PRD → TRD: ✅ 14/14 features have architecture
   TRD → TSD: ⚠️ API tests but no contract tests
   PRD → TSD: ⚠️ NFR "p95 < 200ms" not in quality gates

──────────────────────────────────────────────────────────
📌 PRIORITY ACTIONS

   1. ❌ Increase test coverage to 90% target
   2. ⚠️ Add contract tests for API endpoints
   3. ⚠️ Add performance quality gate to CI

▶️ NEXT: /sdlc-studio test-automation generate
══════════════════════════════════════════════════════════
```

---

## Quick Mode

When `--quick` is specified:

```text
1. Load cached status data from sdlc-studio/.local/status-cache.json
2. Skip codebase analysis
3. Skip cross-document consistency check
4. Display cached results with "(cached: {date})" subtitle
```

Quick mode is useful for:

- Fast status checks during development
- CI/CD quick gates
- When codebase hasn't changed

---

## Focus Mode

When `--focus {document}` is specified:

```text
1. Run only the specified document review
2. Skip cross-document consistency check
3. Display focused output for that document only
```

Example:

```bash
/sdlc-studio review --focus tsd
```

Output:

```text
══════════════════════════════════════════════════════════
                      TSD REVIEW
══════════════════════════════════════════════════════════

🧪 TEST STRATEGY                       ▓▓▓▓▓▓▓░░░ 78%

   Coverage:
   ├─ Unit:        ▓▓▓▓▓▓▓▓▓░ 90% (target: 90%)  ✅
   ├─ Integration: ▓▓▓▓▓▓▓▓░░ 82% (target: 85%)  ⚠️
   └─ E2E:         ▓▓▓▓▓▓▓░░░ 7/10 features      ⚠️

   Frameworks:
   ├─ pytest:      8.0.0 (current: 8.1.0)        ⚠️ Update available
   └─ playwright:  1.40.0 (current)              ✅

   Quality Gates:
   ├─ Unit coverage:    ✅ Configured
   ├─ Integration pass: ✅ Configured
   └─ Performance:      ❌ Not configured

──────────────────────────────────────────────────────────
📌 ACTIONS

   1. ❌ Add 3 E2E specs for uncovered features
   2. ⚠️ Increase integration coverage by 3%
   3. ⚠️ Update pytest to 8.1.0
   4. ❌ Add performance quality gate

▶️ NEXT: /sdlc-studio test-automation generate
══════════════════════════════════════════════════════════
```

---

## TSD Review Workflow (Detailed) {#tsd-review-workflow}

### 1. Load TSD

```text
a) Read sdlc-studio/tsd.md
b) Parse coverage targets from document
c) Parse framework versions
d) Parse quality gate configuration
```

### 2. Analyse Current Testing State

```text
a) Coverage data:
   - Primary: Parse .coverage SQLite or coverage.xml (Python)
   - Primary: Parse coverage/lcov.info or coverage-summary.json (JS/TS)
   - Fallback: Use TSD documented values

b) Framework versions:
   - Python: Parse pyproject.toml, requirements.txt
   - JS/TS: Parse package.json
   - Compare to TSD documented versions

c) CI/CD quality gates:
   - Parse .github/workflows/*.yml
   - Parse .gitlab-ci.yml
   - Check for coverage thresholds, test commands
```

### 3. Identify Gaps

| Gap Type | Detection | Severity |
| --- | --- | --- |
| Coverage below target | Actual < target | ❌ if >5% gap, ⚠️ otherwise |
| Missing test type | No tests for documented type | ⚠️ |
| Outdated framework | Current > documented | ⚠️ |
| Missing quality gate | PRD NFR without gate | ❌ |
| Stale TSD content | Document older than tests | ⚠️ |
| Test tree drift | Files in codebase not in TSD tree (or vice versa) | ⚠️ |

### 3a. Validate Test Organisation Tree

If the TSD contains a "Test Organisation" section with a file tree:

1. Glob `src/__tests__/**/*.test.ts` (or project-appropriate test pattern)
2. Compare actual test file tree against the TSD's documented tree
3. Report discrepancies:
   - Files in codebase but not in TSD tree → "undocumented test"
   - Files in TSD tree but not in codebase → "planned test" or "stale entry"
4. If `--no-fix` not set and significant drift found, offer to regenerate the test tree section:
   - Current files annotated with descriptions
   - Missing planned files annotated with `(EP00XX)` epic reference
   - Split into "Current Test Files" and "Planned Test Files" sections

### 4. Update TSD

If gaps found and user confirms:

```text
a) Update coverage percentages with actual values
b) Update framework versions
c) Add [GAP] markers for missing items
d) Update revision history
```

### 5. Report Strategy Currency

```text
TSD Currency:
├─ Coverage targets: Current
├─ Framework versions: 1 update available
├─ Quality gates: 1 missing
└─ Last sync: 2026-01-20 (7 days ago)
```

---

## Cross-Document Rules

### PRD → TRD Mapping

Each PRD feature should have:

- At least one TRD component addressing it
- Clear API contracts (if feature involves API)
- Data model documentation (if feature involves data)

### TRD → TSD Mapping

Each TRD component should have:

- Test strategy defined (unit/integration/E2E)
- Coverage targets appropriate to risk
- Automation approach documented

### PRD NFR → TSD Gate Mapping

| PRD NFR Type | Required TSD Gate |
| --- | --- |
| Response time | Performance threshold |
| Availability | Uptime monitoring |
| Security | Security scan stage |
| Scalability | Load test stage |

---

## Review Output Formats

### Console Output (Default)

ASCII art dashboard as shown above.

### JSON Output (CI/CD)

```bash
/sdlc-studio review --output json > review.json
```

```json
{
  "timestamp": "2026-01-27T10:30:00Z",
  "overall_health": 85,
  "documents": {
    "prd": { "health": 85, "findings": 2 },
    "trd": { "health": 92, "findings": 1 },
    "tsd": { "health": 78, "findings": 3 }
  },
  "cross_document": {
    "prd_trd": { "covered": 14, "total": 14 },
    "trd_tsd": { "issues": ["API tests but no contract tests"] },
    "prd_tsd": { "issues": ["NFR 'p95 < 200ms' not in quality gates"] }
  },
  "priority_actions": [
    { "severity": "critical", "action": "Increase test coverage to 90% target" },
    { "severity": "important", "action": "Add contract tests for API endpoints" }
  ]
}
```

---

## See Also

- `help/review.md` - Command quick reference
- `reference-prd.md#prd-review-workflow` - PRD review details
- `reference-trd.md#trd-review-workflow` - TRD review details
- `reference-tsd.md#tsd-review-workflow` - TSD review details
