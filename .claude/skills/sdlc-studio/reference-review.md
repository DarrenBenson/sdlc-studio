# SDLC Studio Unified Review Reference

Workflows for the unified document review command that analyses PRD, TRD, and TSD together.

## Overview

The unified review command runs document reviews across all three specification layers and checks cross-document consistency.

---

## /sdlc-studio review - Step by Step {#review-workflow}

### 1. Parse Arguments

| Flag | Effect | Default |
|------|--------|---------|
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

### 4. Generate Consolidated Report

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
|----------|-----------|----------|
| Coverage below target | Actual < target | ❌ if >5% gap, ⚠️ otherwise |
| Missing test type | No tests for documented type | ⚠️ |
| Outdated framework | Current > documented | ⚠️ |
| Missing quality gate | PRD NFR without gate | ❌ |
| Stale TSD content | Document older than tests | ⚠️ |

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
|--------------|-------------------|
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
