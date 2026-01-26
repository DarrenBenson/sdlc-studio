<!--
Load: On /sdlc-studio status or /sdlc-studio status help
Dependencies: SKILL.md (always loaded first)
Related: reference-testing.md (status workflow details)
-->

# /sdlc-studio status

Shows a visual dashboard of project health across three pillars: Requirements, Code, and Tests.

## Usage

```bash
/sdlc-studio status              # Full visual dashboard
/sdlc-studio status --testing    # Testing pillar only
/sdlc-studio status --workflows  # Workflow state only
/sdlc-studio status --brief      # One-line summary
```

## Visual Dashboard

The status command displays an at-a-glance dashboard:

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

──────────────────────────────────────────────────────────
📌 NEXT STEPS
   1. ⚠️ Complete Epic EP0003 → unblocks 4 stories
   2. ⚠️ Clear 5 TODOs in backend/
   3. ❌ Add CI/CD pipeline (gap identified in TSD)
══════════════════════════════════════════════════════════
```

## Three Pillars

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
SDLC: 📋 85% | 💻 90% | 🧪 94% | Next: Complete EP0003
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

## See Also

- `/sdlc-studio hint` - Single actionable next step
- `/sdlc-studio help` - Full command reference
- `reference-testing.md` - Detailed status workflow
