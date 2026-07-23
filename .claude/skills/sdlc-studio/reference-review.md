# SDLC Studio Unified Review Reference

<!-- Load when: running /sdlc-studio review or assessing document currency -->

## Contents

- [Overview](#overview)
- [When to Run a Unified Review](#when-to-run-a-unified-review)
- [/sdlc-studio review - Step by Step](#review-workflow)
- [The adversarial closing-review brief](#closing-review-brief)
- [Quick Mode](#quick-mode)
- [Focus Mode](#focus-mode)
- [TSD Review Workflow (Detailed)](#tsd-review-workflow)
- [Cross-Document Rules](#cross-document-rules)
- [Review Output Formats](#review-output-formats)
- [See Also](#see-also)

Workflows for the unified document review command that analyses PRD, TRD, TSD, and Persona together.

## Overview

The unified review command runs document reviews across all four specification layers (Product, Technical, Test, Persona) and checks cross-document consistency. Persona is reviewed for **drift** (have personas gone stale, do PRD references still resolve, are personas still consulted) – distinct from "Persona Consultation" (using personas to assess the other documents), which is documented at step 3a.

> **Deterministic helper (run first).** `python3 "$CLAUDE_SKILL_DIR/scripts/review_prep.py" prep --format json` gathers the mechanical inputs each leg needs: artifact staleness (changed since last review), persona definition-vs-PRD usage, and the count / AC-verification inputs. Start each leg from that JSON. The review verdict - and the CODE leg in particular - stays your judgement; it is never scripted.
>
> **Agent-instructions hygiene check.** Also run `python3 "$CLAUDE_SKILL_DIR/scripts/validate.py" instructions` - it verifies the project's `AGENTS.md` / `CLAUDE.md` are well-formed (AGENTS.md canonical, CLAUDE.md a `@AGENTS.md` pointer, the operating-doctrine + `LATEST.md` pointers present, the pre-release gate and the compaction re-read rule present, and no per-ship-narrative bloat). Fold any findings into the review (or fix them in the same pass) - a stale or bloated instructions file is drift like any other.

---

## When to Run a Unified Review

Run `/sdlc-studio review` on a deliberate cadence – it is the periodic synthesis point that keeps PRD/TRD/TSD honest. The agent-instructions file (`AGENTS.md` / `CLAUDE.md`) and commit messages are audit trails, not indexes; the review is what answers "is this project healthy?"

**Cadence (any of, whichever comes first):**

- Every 5 minor releases.
- Per-epic completion (after the closing reconcile, before the next epic starts).
- More than 4 weeks since the last unified review.
- About to tag a release (also see `templates/workflows/release-gate.md`).

**Symptom triggers (any of these mean a review is overdue):**

- The agent-instructions file or PRD §3 detail blocks have started accumulating per-ship narrative – the changelog is leaking into the index because no review has synthesised it.
- A canvas / persona consultation surfaced multiple cross-cutting concerns that no document has digested.
- The number of versions since the most recent `RV{NNNN}-unified-review-*.md` exceeds the cadence above.

The most recent unified review is always written to `sdlc-studio/reviews/LATEST.md` (see step 4 below) so it is one read away – use it as the orientation entry-point for fresh conversations rather than re-deriving project state from `git log`.

---

## /sdlc-studio review - Step by Step {#review-workflow}

### 1. Parse Arguments

| Flag | Effect | Default |
| --- | --- | --- |
| (none) | Run all document reviews (PVD if present + PRD + TRD + TSD + Persona) | - |
| `--quick` | Use cached data, skip codebase analysis | false |
| `--focus pvd` | Run only PVD review (multi-repo products) | all |
| `--focus prd` | Run only PRD review | all |
| `--focus trd` | Run only TRD review | all |
| `--focus tsd` | Run only TSD review | all |
| `--focus persona` | Run only Persona review | all |
| `--skip-personas` | Drop Persona Review from the default chain (PRD+TRD+TSD only) | false |

If `sdlc-studio/personas/` does not exist or contains no persona files, Persona Review is skipped automatically – no flag required. The four-doc default applies whenever personas exist.

**PVD review is conditional.** The PVD leg runs **only when `sdlc-studio/product/pvd.md` exists** (a multi-repo product). A single-repo project has no PVD - the leg, and the Product Manager sign-off it carries, do not apply; the PRD is the top document and the Product Owner signs it.

**The four required legs are not conditional.** PVD may read "not applicable" when its file is absent; PRD / TRD / TSD / Persona may not. When a required leg's artefact is missing, resolve it one of exactly two ways, never by narrative downgrade to "optional": **file a finding** (the default - a missing required artefact is a review finding to triage), or record an **explicit waiver** (`decisions.py waive --leg <leg> --rationale ...`) and report the leg as **"waived (see D00xx)"**. `review_prep.py`'s `required_legs` makes each leg's presence and waiver machine-visible, and `gate.py --release` fails on an absent-and-unwaived required leg - so a prose reclassification cannot reach a tag. CODE is out of scope (no single testable artefact).

**RFC review (if `sdlc-studio/rfcs/` exists).** As part of the unified pass, scan the RFCs: flag any **Draft / In Review** RFC stalled > ~14 days with no Revision-History movement; flag **Open Decisions** unresolved > 7 days (name the owner); and for **Accepted** RFCs verify each workstream has a spawned CR that exists and links back. This catches design exploration that has gone quiet before it silently blocks the dependent CRs. Report-only – RFC acceptance is always a judgement call.

### 2. Run Document Reviews

Execute reviews in sequence, collecting findings:

#### PVD Review (only if `sdlc-studio/product/pvd.md` exists)

Skip this leg entirely for a single-repo project (no PVD). When a PVD exists:

```text
1. Load sdlc-studio/product/pvd.md (+ product/manifest.yaml)
2. For each PVD product requirement / shared feature, locate the child repo(s) that own it
3. Coverage: every PVD requirement maps to a child PRD feature (flag any with no PRD home)
4. Satisfaction: each mapped requirement is met in the child repos (verified epics / shipped)
5. Identify cross-repo drift, stale coordination prose, and inter-repo API mismatches
```

> **Product Manager sign-off (the gate):** the PVD leg ends with an explicit verdict - **"PVD
> requirements satisfied: yes / no (gaps: …)"**. The Product Manager seat owns this; it is the
> review's answer to "are the product-level requirements actually met across the repos?"

See `reference-pvd.md` for the PVD layer.

#### PRD Review

```text
1. Load sdlc-studio/prd.md
2. Scan codebase for feature implementation
3. Compare features against code
4. Calculate status percentages
5. Identify gaps and stale content
```

> **Product Owner sign-off (the gate):** the PRD leg ends with an explicit verdict - **"PRD
> requirements satisfied: yes / no (gaps: …)"**. The Product Owner seat owns this; a review is not
> complete until the PRD requirements are confirmed met (or the gaps are named and tracked).

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

#### Persona Review

```text
1. Load sdlc-studio/personas/index.md (and per-persona files)
2. Build the staleness map: for each persona, last consult date + last referenced-in-CR/Story date
3. Cross-check: every persona referenced in PRD §1/§2 still exists in personas/
4. Cross-check: every persona consulted on a CR/Story in the last `personas.staleness_days`
                (default 90 days) is still present (catches stale references after rename)
5. Identify drift:
   - Personas not consulted within the staleness window → "stale" (suggest refresh / archive / consult)
   - Personas referenced in PRD but missing from personas/ → "broken reference"
   - Duplicate personas (same role + name) → "duplicate"
   - Personas with no CR/Story references at all → "unused" (suggest archive or first-consult)
```

If `sdlc-studio/personas/` does not exist or contains no persona files, Persona Review is skipped (no warning – the project has no persona artefacts to review). The other three reviews run as normal. See `reference-persona.md#persona-review-workflow` for details (when personas exist).

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

#### PRD → Persona Reference Resolution

```text
For each persona referenced in PRD §1 (Personas) or §2 (Goals/Users):
  - Check persona file exists in sdlc-studio/personas/
  - Flag broken references as critical (PRD names a persona that no longer exists)
  - Flag PRD references to archived personas as important
```

#### Persona → CR / Story Activity

```text
For each persona in sdlc-studio/personas/:
  - Find most recent consult or reference in CRs and Stories
  - If older than `personas.staleness_days` (default 90 days):
    - Active personas: flag as stale, suggest refresh
    - Archived personas: no flag (expected)
  - If never referenced: flag as unused, suggest archive or first-consult
```

#### Persona Self-Consistency

```text
Within sdlc-studio/personas/:
  - Detect duplicate personas (same role + name)
  - Detect personas with broken cross-references (consultation guide names that no longer exist)
  - Detect personas missing from personas/index.md
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

**Single-writer during a review.** A review rewrites files in the author's tree, and a green suite is NOT
evidence the tree is clean: at RUN-01KY321Q a shell redirect through a symlink farm reverted live source,
caught only because it broke the suite. Declare the window (`mutation.py window open|close`), stage named
paths, never `git add -A` - see [reference-sprint.md](reference-sprint.md#single-writer).

### 4. Close the Review (tool-carried)

**CRITICAL - and one command, not hand-steps:** the close is
`review_prep.py close --rv RV{NNNN} [--latest-body FILE|-]`. It stamps
`sdlc-studio/.local/review-state.json` for every present leg (last_reviewed,
last_modified from git, review_findings_ref, the reviews.{RV} entry) and, when the
anchor content is supplied, writes `sdlc-studio/reviews/LATEST.md` - **refusing both
when the dated RV record does not exist**, and refusing an anchor body that never
cites the RV id. A review may never live only in the overwritable anchor: mint the
dated record first (`artifact.py new --type review`), write its content, then close.

```text
1. Mint + write the dated RV{NNNN} record (the historical copy; artifact.py allocates it)
2. Compose the anchor from templates/reviews/unified-anchor.md, citing the RV id
3. review_prep.py close --rv RV{NNNN} --latest-body <anchor-file>
   (stamps review-state.json + derives LATEST.md from the record, atomically)
4. For each reviewed document that was modified (status updates, AC checkboxes,
   auto-fixes): update its `**Last Updated:**` date and add a revision-history row
   `| {date} | Claude | {type} review: {summary of changes} |`
```

LATEST.md is the canonical "most recent review" pointer for fresh-conversation
orientation; the dated `RV{NNNN}-unified-review-*.md` remains the record.

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

👥 PERSONA REVIEW                      ▓▓▓▓▓▓▓▓▓░ 95%
   Personas: 7 active | 0 archived
   Stale: 1 (>90d since last consult)
   Broken refs: 0
   ✅ Persona alignment current

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
   PRD → Persona: ✅ 4/4 PRD persona refs resolve
   Persona → CRs: ⚠️ 1 persona stale (no consult in 92 days)
   Persona → Persona: ✅ no duplicates / broken cross-refs

──────────────────────────────────────────────────────────
📌 PRIORITY ACTIONS

   1. ❌ Increase test coverage to 90% target
   2. ⚠️ Add contract tests for API endpoints
   3. ⚠️ Add performance quality gate to CI

▶️ NEXT: /sdlc-studio test-automation generate
══════════════════════════════════════════════════════════
```

---

## The adversarial closing-review brief {#closing-review-brief}

The unified review above keeps the four specification layers honest. The **closing review** of a
sprint is a different pass: a fresh reviewer, who did not write the diff, tries to break it. That
brief is assembled by `scripts/critic.py brief` so it never depends on whoever wrote it happening
to remember what works. Two things it carries are standing instructions, because both were
improvised mid-sprint - in RUN-01KY3MFX and the reviews before it - rather than drawn from
anything shipped.

### The claim inventory runs first

Before reading a line of logic, the reviewer inventories every **assertion the diff's prose
makes** and marks each one against the code. The pass covers all four prose surfaces -
**Resolutions, docstrings, comments and CHANGELOG entries** - because a pass that omits one
exempts it, and a Resolution is the one artefact no test can fail: it is written after the work,
by the author, to justify what they just did.

Each assertion is ruled **TRUE, FALSE or UNVERIFIABLE**. UNVERIFIABLE is its own category, never
folded into TRUE: a claim no command can settle is reported as resting on trust, so the reader
sees how much of the prose is unchecked. A round whose every ruling is UNVERIFIABLE is not a
clean round - nothing was checked, and it must not read the same as one that looked and found
nothing wrong. The claim pass runs **before** the logic review and its findings are reported
apart, so a round that found only prose defects is visibly a different kind of round from one
that found logic defects - convergence told from churn.

### Three standing review practices

Every closing brief carries these three, each paired with the reason it exists:

- **Per-item repair verdicts.** On a repair review, rule each previous finding **CLOSED,
  OVER-CLAIMED or MOVED** individually. A general "review the repair" answer blurs the three
  into one impression; and MOVED is not CLOSED - a defect that moved survived, and counting it
  closed is how a repair masks the defect beside it.
- **Mutate the author's TESTS, not only the code.** A test whose shape list was drawn from the
  families where two implementations agree by construction passes every mutant while proving
  nothing. No amount of reading the code finds that - only mutating the test does.
- **Isolation re-testing of a surviving mutant.** When a mutant survives, re-test its branch in
  **isolation** before drawing any conclusion from it. A sibling guard masked a survivor three
  separate times in one sprint, and each time the truth appeared only when the branch was
  exercised alone - a survivor is evidence about the harness, not about the test.

`critic.py` refuses to issue a brief missing any of the three practices, or a claim-inventory
pass that omits one of the four prose surfaces, so the discipline holds by construction rather
than by the author remembering it.

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

### PRD → Persona Mapping

Each persona named in PRD §1 (Personas) or §2 (Goals/Users) should:

- Have a corresponding file in `sdlc-studio/personas/`
- Be present in `sdlc-studio/personas/index.md`
- Have at least one consult / story / CR reference within `personas.staleness_days` (default 90)

A "broken reference" (PRD names a persona that no longer exists) is **critical**. A "stale persona" (no consult in 90+ days) is **important** unless the persona has been explicitly archived.

### Persona → Artefact Activity Mapping

For each active persona:

- Recent consult (`/sdlc-studio consult`) – counts as a touch
- Reference in a CR's "Stakeholders" or "Personas Consulted" section – counts as a touch
- Reference in a Story's `As a {persona}` line or persona-reference section – counts as a touch

Personas with zero touches across all artefacts within the staleness window are flagged as **unused** and should be archived or first-consulted.

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
    "tsd": { "health": 78, "findings": 3 },
    "persona": { "health": 95, "findings": 1, "personas_total": 7, "stale": 1, "broken_refs": 0 }
  },
  "cross_document": {
    "prd_trd": { "covered": 14, "total": 14 },
    "trd_tsd": { "issues": ["API tests but no contract tests"] },
    "prd_tsd": { "issues": ["NFR 'p95 < 200ms' not in quality gates"] },
    "prd_persona": { "resolved": 4, "total": 4, "broken": [] },
    "persona_artefacts": { "stale": ["Webapp Dev"], "unused": [] },
    "persona_consistency": { "duplicates": [], "broken_xrefs": [] }
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
- `reference-persona.md#persona-review-workflow` - Persona review details (the 4th review in the chain)
- `templates/reviews/unified-anchor.md` - The LATEST.md template written on every full review
