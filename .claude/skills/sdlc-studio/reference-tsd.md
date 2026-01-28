# SDLC Studio Reference - Test Strategy Document

Detailed workflows for test strategy creation and the status dashboard.

<!-- Load when: creating TSD, running status command, understanding coverage targets -->

---

## Coverage Targets and Rationale

### Default Targets

| Level | Target | Rationale |
|-------|--------|-----------|
| Unit | 90% | Core business logic must be thoroughly tested |
| Integration | 85% | API and database interactions |
| E2E | 100% feature coverage | Every user-visible feature has at least one spec file |

### Why 90%?

AI-assisted development changes the economics of testing:

1. **AI produces code faster** - More code requires more quality gates
2. **AI can hallucinate** - Higher coverage catches incorrect implementations
3. **AI assists with test writing** - Makes high coverage achievable with reasonable effort
4. **Proven achievable** - Projects using AI assistance have demonstrated 90%+ coverage

This target has been proven achievable across multiple projects with AI assistance (e.g., 1,027+ tests achieving 90% backend coverage, 90%+ frontend coverage).

### Language-Agnostic Principles

These principles apply regardless of technology stack:

| Principle | Description |
|-----------|-------------|
| Test at boundaries | Unit tests for logic, integration tests for APIs, E2E for user flows |
| Mock at system edges | Network, filesystem, time - not internal libraries |
| Contract tests bridge gaps | Pair mocked E2E tests with backend contract tests |
| Feature-based organisation | Group tests by feature, not by test type |
| Coverage by layer | Different targets for different test levels |

### Test Runner Recommendations (Not Mandates)

| Language | Unit/Integration | E2E | Coverage |
|----------|------------------|-----|----------|
| Python | pytest | pytest / Playwright | pytest-cov |
| TypeScript | vitest / jest | Playwright / Cypress | v8 / istanbul |
| Go | testing | testing | go test -cover |
| Rust | cargo test | - | cargo-llvm-cov |
| Java | JUnit | Selenium | JaCoCo |

**Note:** These are recommendations based on ecosystem norms. Use whatever tools work best for your project.

---

## Test Organisation (Language-Agnostic)

All tests reside in a unified `tests/` directory at the project root:

```text
tests/
  unit/
    backend/          # Python unit tests
    frontend/         # TypeScript unit tests
  integration/        # Cross-component tests
  api/               # API endpoint tests
  e2e/               # End-to-end browser tests
  contracts/         # API contract tests (bridge E2E mocks to backend)
  fixtures/          # Shared test data (JSON, YAML)
```

**Naming conventions within unified structure:**

| Language | Pattern | Example |
|----------|---------|---------|
| Python | `test_*.py` | `tests/unit/backend/test_auth.py` |
| TypeScript | `*.test.ts` | `tests/unit/frontend/auth.test.ts` |
| E2E (any) | `*.spec.ts` | `tests/e2e/dashboard.spec.ts` |
| Go | `*_test.go` | `tests/unit/backend/auth_test.go` |

**Key principles:**

- **Single root:** All tests in `tests/` at project root, not scattered across `backend/tests/`, `frontend/__tests__/`
- **By type first:** Subdirectories by test type (`unit/`, `integration/`, `api/`, `e2e/`, `contracts/`)
- **Then by component:** Language/component subdirectories within type (`unit/backend/`, `unit/frontend/`)
- **Shared fixtures:** Common test data in `tests/fixtures/`

---

## Status Dashboard Workflow

### /sdlc-studio status - Visual Dashboard

**CRITICAL: You MUST use this exact ASCII format. Do NOT use markdown tables.**

The status command produces a visual dashboard across three pillars:

```text
══════════════════════════════════════════════════════════
                      SDLC STATUS
══════════════════════════════════════════════════════════

📋 REQUIREMENTS (PRD Status)        ▓▓▓▓▓▓▓▓░░ 85%
   ✅ PRD: 14 features defined
   ✅ Personas: 4 documented
   ⚠️ Epics: 2/3 Ready (1 Draft)
   ✅ Stories: 12/12 Done

💻 CODE (TRD Status)                ▓▓▓▓▓▓▓▓▓░ 90%
   ✅ TRD: Architecture documented
   ⚠️ Lint: 4 issues (backend/tests/)
   ⚠️ TODOs: 5 remaining

🧪 TESTS (TSD Status)               ▓▓▓▓▓▓▓▓▓░ 94%
   ✅ Backend (1,027 tests):        ▓▓▓▓▓▓▓▓▓░ 90%
   ✅ Frontend:                     ▓▓▓▓▓▓▓▓▓░ 90%
   ⚠️ E2E (7/7 features):           1 flaky test

──────────────────────────────────────────────────────────
📌 NEXT STEPS
   1. ⚠️ Fix lint: 4 unused imports in tests/
   2. ⚠️ Investigate flaky test in task-list.spec.js
   3. ❌ Add CI/CD pipeline (gap identified in TSD)

▶️ SUGGESTED: /sdlc-studio code review
══════════════════════════════════════════════════════════
```

### Step-by-Step Implementation

#### 1. Gather Requirements Pillar Data

```text
a) Check PRD:
   - Glob for `sdlc-studio/prd.md`
   - Parse feature count (count ## headings or feature markers)

b) Check Personas:
   - Glob for `sdlc-studio/personas.md`
   - Count persona sections

c) Check Epics:
   - Glob `sdlc-studio/epics/EP*.md`
   - Parse status from frontmatter (Draft/Ready/Done)
   - Calculate: Ready+Done / Total

d) Check Stories:
   - Glob `sdlc-studio/stories/US*.md`
   - Parse status from frontmatter
   - Calculate: Done / Total
```

#### 2. Gather Code Pillar Data

```text
a) Check TRD:
   - Glob for `sdlc-studio/trd.md`

b) Check Lint Status:
   - Detect language (pyproject.toml → Python, package.json → JS/TS)
   - Run: `ruff check` or `npm run lint`
   - Capture exit code AND issue count
   - If issues found: Note count and file location (e.g., "4 issues (backend/tests/)")

c) Count TODOs:
   - Grep source directories for TODO/FIXME
   - Exclude: node_modules, .venv, __pycache__, dist
   - Count occurrences

d) Check Type Status (optional):
   - If mypy configured: `mypy --quiet`
   - If tsconfig: `tsc --noEmit --quiet`
```

#### 3. Gather Tests Pillar Data

```text
a) Check TSD:
   - Glob for `sdlc-studio/tsd.md`

b) Get Backend Coverage:
   - Primary: Parse `.coverage` SQLite or `coverage.xml`
   - Fallback: Parse coverage % from TSD "Current Coverage" line
   - Check file age vs source files for staleness

c) Get Frontend Coverage:
   - Primary: Parse `coverage/lcov.info` or `coverage/coverage-summary.json`
   - Fallback: Parse from TSD

d) Get E2E Feature Coverage:
   - Glob `e2e/*.spec.ts` or `frontend/e2e/*.spec.ts`
   - Count spec files
   - Compare to expected features (from PRD or TSD)

e) Detect Flaky/Failing Tests:
   - Check recent test run results if available
   - Parse CI logs or test reports for failures
   - Identify flaky tests (intermittent failures)
   - Note specific test names if found
```

#### 4. Calculate Health Scores

```python
# Requirements health (PRD Status)
req_health = (
    (20 if prd_exists else 0) +
    (10 if personas_count > 0 else 0) +
    (30 * epics_ready_pct / 100) +
    (40 * stories_done_pct / 100)
)

# Code health (TRD Status)
code_health = (
    (30 if trd_exists else 0) +
    (35 if lint_passes else 0) +
    (35 if todo_count < 10 else 35 * max(0, (20 - todo_count)) / 20)
)

# Tests health (TSD Status)
tests_health = (
    (10 if tsd_exists else 0) +
    (30 * min(backend_coverage, 90) / 90) +
    (30 * min(frontend_coverage, 90) / 90) +
    (30 * e2e_feature_pct / 100)
)
```

#### 5. Generate Progress Bars

```python
def progress_bar(percent, width=10):
    filled = round(percent / 100 * width)
    return "▓" * filled + "░" * (width - filled)

# Example: 85% → ▓▓▓▓▓▓▓▓░░
```

#### 6. Determine Status Indicators

```text
✅ = Complete/Passing/On target (>=90% or exists when required)
⚠️ = Partial/Warning (50-89% or minor issues)
❌ = Missing/Failing/Critical (<50% or required item missing)
```

#### 7. Prioritise Next Steps

Priority order:

1. **Missing foundations** (PRD, TRD, TSD not created)
2. **Blocking items** (Epics in Draft blocking stories)
3. **Below-target coverage** (Backend/Frontend < 90%)
4. **Quality issues** (Lint failures, flaky tests, > 10 TODOs)
5. **Automation gaps** (E2E features missing specs)

#### 8. Determine Suggested Command

Map the highest-priority next step to an sdlc-studio command:

| Next Step Type | Suggested Command |
|----------------|-------------------|
| Missing PRD | `/sdlc-studio prd create` or `prd generate` |
| Missing TRD | `/sdlc-studio trd create` or `trd generate` |
| Missing TSD | `/sdlc-studio tsd create` |
| Epic incomplete | `/sdlc-studio epic review --epic {id}` |
| Stories ready | `/sdlc-studio story implement --story {id}` |
| Lint failures | `/sdlc-studio code review` |
| Flaky/failing tests | `/sdlc-studio test-spec review` |
| Coverage gaps | `/sdlc-studio test-automation generate` |
| All complete | `/sdlc-studio prd review` |

#### 9. Output Dashboard

Use the visual format shown above. Key formatting:

- Unicode box drawing for borders
- Progress bars using ▓░ characters
- Emoji indicators for quick scanning
- Right-aligned percentage in brackets
- Indented details under each pillar

### Cache-Aware Status Workflow

```text
1. Check for --full flag
   - If --full: Skip to step 3 (gather fresh data)

2. Check cache (quick mode)
   - Read sdlc-studio/.local/status-cache.json
   - If exists and valid:
     a) Load cached pillars
     b) Quick-refresh static checks (file existence only)
     c) Display with "(cached: {date})" subtitle
     d) Done
   - If missing: Continue to step 3

3. Gather fresh data (full mode)
   - Execute all pillar data collection (as documented)
   - Calculate health scores
   - Prioritise next steps

4. Write cache
   - Write results to sdlc-studio/.local/status-cache.json
   - Include ISO timestamp

5. Output dashboard
   - Full mode: No subtitle
   - Quick mode fallback: No subtitle (cache just created)
```

**Cache file format:**

```json
{
  "version": 1,
  "generated_at": "2026-01-26T10:30:00Z",
  "pillars": {
    "requirements": {
      "health": 85,
      "prd": { "exists": true, "features": 14 },
      "personas": { "count": 4 },
      "epics": { "ready": 2, "total": 3 },
      "stories": { "done": 12, "total": 12 }
    },
    "code": {
      "health": 90,
      "trd": { "exists": true },
      "lint": { "passing": true },
      "todos": { "count": 5 }
    },
    "tests": {
      "health": 94,
      "tsd": { "exists": true },
      "backend": { "coverage": 90, "tests": 1027 },
      "frontend": { "coverage": 90 },
      "e2e": { "covered": 7, "total": 7 }
    }
  },
  "next_steps": [
    "Complete Epic EP0003 → unblocks 4 stories",
    "Clear 5 TODOs in backend/",
    "Add CI/CD pipeline"
  ]
}
```

### Output Format Rules (CRITICAL - MUST FOLLOW)

**You MUST use the exact ASCII art format above. NEVER use markdown tables.**

The status dashboard MUST match this exact structure:

1. **Border width:** 58 characters (═ and ─)
2. **Title:** "SDLC STATUS" centred, on its own line
3. **Cached mode:** Add "(cached: {date})" below title when using cache
4. **Sections:** Three pillars + Next Steps + Suggested Command
5. **Suggested command:** `▶️ SUGGESTED: /sdlc-studio {command}` before bottom border
6. **Ending:** Bottom border (══) - nothing after
7. **No extras:** No Summary tables, no narrative text

**MUST surface these warnings (use ⚠️ indicator):**
- Lint failures or issues (show count and location)
- Flaky tests (show test name)
- Failing tests (show count)
- TODOs/FIXMEs (show count)
- Coverage below 90% target

**Output with cache (quick mode):**

```
══════════════════════════════════════════════════════════
                      SDLC STATUS
                 (cached: 26 Jan 2026, 10:30)
══════════════════════════════════════════════════════════
[... rest of dashboard unchanged ...]
```

**FORBIDDEN - Do NOT use:**
- Markdown tables (use ASCII art only)
- Summary sections at the end
- Narrative paragraphs ("Project State:", "Summary:")
- Additional formatting beyond the template

---

## TSD Workflows

### /sdlc-studio tsd - Step by Step

1. **Check Prerequisites**
   - Verify PRD exists at sdlc-studio/prd.md
   - Create sdlc-studio/ directory if needed

2. **Gather Context**
   Use AskUserQuestion to collect:
   - Testing objectives and priorities
   - Test level expectations (unit, integration, E2E)
   - Framework preferences
   - CI/CD environment

3. **Analyse PRD**
   - Extract non-functional requirements
   - Identify testability considerations
   - Note integration points requiring testing

4. **Generate Strategy**
   - Use `templates/core/tsd.md`
   - Fill test levels based on architecture
   - Define automation candidates
   - Set quality gates

5. **Write File**
   - Write to `sdlc-studio/tsd.md`

6. **Report**
   - Test levels defined
   - Automation approach
   - Quality gates configured

---

### /sdlc-studio tsd generate - Step by Step

1. **Analyse Codebase**
   Use Task tool with Explore agent:

   ```text
   Analyse codebase for testing patterns:
   1. Existing test files and frameworks
   2. Test configuration (pytest.ini, jest.config, etc.)
   3. CI/CD pipeline test stages
   4. Coverage configuration
   5. Test utilities and helpers
   Return: Current testing landscape
   ```

2. **Infer Strategy**
   - Document existing test levels
   - Identify gaps in coverage
   - Note automation opportunities

3. **Write Strategy**
   - Use template with [INFERRED] confidence markers
   - Include recommendations for gaps

---

### /sdlc-studio tsd review - Step by Step {#tsd-review-workflow}

1. **Load TSD**
   - Read existing TSD from `sdlc-studio/tsd.md`
   - Parse coverage targets, framework versions, quality gates

2. **Analyse Current Testing State**

   ```text
   a) Coverage data:
      - Primary: Parse .coverage (Python) or lcov.info (JS/TS)
      - Fallback: Use TSD documented values

   b) Framework versions:
      - Parse pyproject.toml, package.json
      - Compare to TSD documented versions

   c) CI/CD quality gates:
      - Parse .github/workflows/*.yml or .gitlab-ci.yml
      - Check for coverage thresholds, test commands
   ```

3. **Identify Gaps**

   | Gap Type | Detection | Severity |
   |----------|-----------|----------|
   | Coverage below target | Actual < target | ❌ if >5% gap |
   | Missing test type | No tests for type | ⚠️ |
   | Outdated framework | Package newer than TSD | ⚠️ |
   | Missing quality gate | PRD NFR without gate | ❌ |

4. **Update TSD with Findings**
   - Update coverage percentages with actual values
   - Update framework versions
   - Add [GAP] markers for missing items

5. **Report Strategy Currency**

   ```text
   TSD Currency:
   ├─ Coverage targets: Current
   ├─ Framework versions: 1 update available
   ├─ Quality gates: 1 missing
   └─ Last sync: 2026-01-20 (7 days ago)
   ```

---

## See Also

- `reference-test-spec.md` - Test specification workflows
- `reference-test-automation.md` - Test automation and environment workflows
- `reference-test-best-practices.md` - Test generation pitfalls and validation
- `reference-test-e2e-guidelines.md` - E2E and mocking patterns
- `help/tsd.md` - TSD command quick reference
- `help/status.md` - Status command quick reference
