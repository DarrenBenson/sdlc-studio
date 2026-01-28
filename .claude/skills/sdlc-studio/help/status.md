<!--
Load: On /sdlc-studio status or /sdlc-studio status help
Dependencies: SKILL.md (always loaded first)
Related: reference-tsd.md (status workflow details)
-->

# /sdlc-studio status

Shows a visual dashboard of project health across three pillars: Requirements, Code, and Tests.

## Usage

```bash
/sdlc-studio status              # Quick status (uses cache if available)
/sdlc-studio status --full       # Full refresh, updates cache
/sdlc-studio status --testing    # Testing pillar only
/sdlc-studio status --workflows  # Workflow state only
/sdlc-studio status --brief      # One-line summary
```

## Pre-flight: Version Check

**First tool call:** `Glob: sdlc-studio/.version`

| Result | Action |
|--------|--------|
| No sdlc-studio/ directory | Proceed (new project) |
| .version exists, schema_version: 2 | Proceed |
| .version missing or schema_version < 2 | Check `sdlc-studio/.local/upgrade-dismissed.json` |
| └─ dismissed: true | Proceed |
| └─ not dismissed | Prompt user (see below) |

**Prompt if needed:**

```
question: "Project uses v1 format. Upgrade to v2?"
header: "Upgrade"
options:
  - "Preview" → run upgrade --dry-run, then continue
  - "Not now" → continue
  - "Don't ask again" → write dismissal file, continue
```

**Output prefix:** Start response with `**Version:** v2 ✓` or `**Version:** v1 (reason)`

## Visual Dashboard

The status command displays an at-a-glance dashboard with four pillars:

```
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
   ✅ Lint: Passing
   ⚠️ TODOs: 5 remaining

🧪 TESTS (TSD Status)               ▓▓▓▓▓▓▓▓▓░ 94%
   ✅ Backend (1,027 tests):        ▓▓▓▓▓▓▓▓▓░ 90%
   ✅ Frontend:                     ▓▓▓▓▓▓▓▓▓░ 90%
   ✅ E2E (7/7 features):           ▓▓▓▓▓▓▓▓▓▓ 100%

🔍 REVIEWS                          ▓▓▓▓▓▓▓▓░░ 80%
   ✅ PRD: Reviewed (2026-01-15)
   ✅ TRD: Reviewed (2026-01-18)
   ⚠️ EP0001: 3 stories changed since review
   ⚠️ EP0002: 1 critical finding unaddressed
   ✅ EP0003: Reviewed (2026-01-26)

──────────────────────────────────────────────────────────
📌 NEXT STEPS
   1. ⚠️ Complete Epic EP0003 → unblocks 4 stories
   2. ⚠️ Clear 5 TODOs in backend/
   3. ⚠️ Review EP0001 (stories changed)
   4. ❌ Add CI/CD pipeline (gap identified in TSD)

▶️ SUGGESTED: /sdlc-studio epic review --epic EP0001
══════════════════════════════════════════════════════════
```

## Four Pillars

### 📋 Requirements (PRD Status)

Tracks specification completeness:

| Metric | Source | Calculation |
|--------|--------|-------------|
| PRD | `sdlc-studio/prd.md` | Exists + feature count |
| Personas | `sdlc-studio/personas.md` | Count defined |
| Epics | `sdlc-studio/epics/EP*.md` | % in Ready/Done status |
| Stories | `sdlc-studio/stories/US*.md` | % in Done status |

**Health score:** Weighted average (PRD 20%, Personas 10%, Epics 30%, Stories 40%)

### 💻 Code (TRD Status)

Tracks implementation quality:

| Metric | Source | Calculation |
|--------|--------|-------------|
| TRD | `sdlc-studio/trd.md` | Exists |
| Lint | `ruff check` / `npm run lint` | Pass/Fail |
| TODOs | Grep source directories | Count of TODO/FIXME |
| Type check | `mypy` / `tsc --noEmit` | Pass/Fail (if configured) |

**Health score:** TRD exists 30%, Lint pass 35%, No critical TODOs 35%

### 🧪 Tests (TSD Status)

Tracks test coverage and quality:

| Metric | Source | Calculation |
|--------|--------|-------------|
| TSD | `sdlc-studio/tsd.md` | Exists |
| Backend coverage | `.coverage` or TSD | Actual % vs 90% target |
| Frontend coverage | `coverage/lcov.info` or TSD | Actual % vs 90% target |
| E2E features | `e2e/*.spec.ts` | Spec files vs features |

**Health score:** TSD 10%, Backend coverage 30%, Frontend coverage 30%, E2E coverage 30%

### 🔍 Reviews

Tracks review currency and findings:

| Metric | Source | Calculation |
|--------|--------|-------------|
| PRD reviewed | `.local/review-state.json` | Has review, not modified since |
| TRD reviewed | `.local/review-state.json` | Has review, not modified since |
| TSD reviewed | `.local/review-state.json` | Has review, not modified since |
| Epics current | `.local/review-state.json` | % of epics reviewed after last modification |
| Stories current | `.local/review-state.json` | % of stories reviewed after last modification |
| Open findings | `sdlc-studio/reviews/` | Unaddressed critical/important issues |

**Health score calculation:**

```text
Review Health % =
  PRD reviewed (10%)
  + TRD reviewed (10%)
  + TSD reviewed (10%)
  + Epics with current reviews (40%)
  + Stories with current reviews (30%)
  × Stale penalty (0.9 if anything needs re-review)
```

**Stale detection:**

An artifact needs re-review when:
- Artifact file modified since last review
- Code files modified since last review (stories)
- No review exists

**Findings indicators:**

| Indicator | Meaning |
|-----------|---------|
| ✅ Reviewed (date) | Reviewed and current |
| ⚠️ N stories changed | Stories modified since epic review |
| ⚠️ N critical findings | Unaddressed critical issues |
| ❌ Never reviewed | No review record exists |

## Status Indicators

| Indicator | Meaning |
|-----------|---------|
| ✅ | Complete / Passing / On target |
| ⚠️ | Partial / Warning / Below target |
| ❌ | Missing / Failing / Critical gap |

## Progress Bars

Progress bars use 10 characters, right-aligned with percentage:

```
▓▓▓▓▓▓▓▓▓▓ 100%
▓▓▓▓▓▓▓▓▓░ 90%
▓▓▓▓▓▓▓▓░░ 80%
▓▓▓▓▓░░░░░ 50%
░░░░░░░░░░ 0%
```

## Next Steps Prioritisation

Next steps are prioritised by impact:

1. **Missing foundations** - PRD, TRD, TSD not created
2. **Blocking items** - Epics blocking stories, failing tests
3. **Below-target coverage** - Coverage under 90%
4. **Quality issues** - Lint failures, TODOs
5. **Automation gaps** - Test specs without automation

## Suggested Command

The dashboard includes a suggested `/sdlc-studio` command based on the highest-priority next step:

| Next Step Type | Suggested Command |
|----------------|-------------------|
| Missing PRD | `/sdlc-studio prd create` or `prd generate` |
| Missing TRD | `/sdlc-studio trd create` or `trd generate` |
| Missing TSD | `/sdlc-studio tsd create` |
| Epic incomplete | `/sdlc-studio epic review --epic {id}` |
| Stories ready | `/sdlc-studio story implement --story {id}` |
| Lint failures | `/sdlc-studio code review` |
| Test failures | `/sdlc-studio test-spec review` |
| Coverage gaps | `/sdlc-studio test-automation generate` |

The command maps directly to the first item in NEXT STEPS. For detailed guidance, use `/sdlc-studio hint`.

## Workflow Status

With `--workflows` flag, shows active and paused workflows:

```
Workflows:
  Active      1 story workflow (US0024 - phase 5/8)
  Paused      0
  Completed   7 story workflows, 1 epic workflow

Resume:
  /sdlc-studio story implement --story US0024 --from-phase 5
```

## Brief Mode

With `--brief` flag, shows single-line summary:

```
SDLC: 📋 85% | 💻 90% | 🧪 94% | 🔍 80% | ▶️ /sdlc-studio epic review --epic EP0001
```

## Data Sources

| Data | Primary Source | Fallback |
|------|----------------|----------|
| Coverage % | `.coverage`, `coverage/lcov.info` | Parse from TSD |
| Lint status | Run lint command | Skip if no config |
| TODO count | Grep source dirs | Show "unknown" |
| Feature count | Parse PRD headings | Count "##" sections |

**Note:** Coverage data may be stale if tests haven't run recently. The dashboard will indicate when coverage data is older than source file changes.

## When to Use

- **Session start** - See what needs attention
- **After changes** - Verify progress
- **Before commit** - Check all pillars healthy
- **Onboarding** - Understand project state

## Caching

For large projects, status uses cached results by default:

| Mode | Behaviour |
|------|-----------|
| Default (quick) | Uses cached results if available, shows timestamp |
| `--full` | Runs fresh analysis, updates cache |

Cache location: `sdlc-studio/.local/status-cache.json`

**When to use `--full`:**
- After running tests or lint
- After significant code changes
- When cache is stale (more than a few hours old)

**Quick mode still updates:**
- PRD/TRD/TSD existence checks (fast)
- Epic/Story status markers (fast file reads)

**Quick mode caches:**
- Lint results (slow command execution)
- TODO counts (slow grep across codebase)
- Coverage percentages (slow parsing)
- Test counts (slow parsing)

## See Also

- `/sdlc-studio hint` - Single actionable next step
- `/sdlc-studio help` - Full command reference
- `reference-tsd.md` - Detailed status workflow
