# RV0003 - Adversarial Audit - v2.0.0 (project profile)

> **Review type:** Adversarial multi-agent audit (project profile: PRD / TRD / TSD / personas / stories / traceability / design / code-vs-AC)
> **Reviewer:** Project Audit workflow
> **Date:** 2026-06-20
> **Project version:** 2.0.0
> **Proves:** RFC0002 (second proving instance - the project profile)

## Run summary

Per-artifact-type finders over the `sdlc-studio/` workspace, looping until dry,
3-vote refute panel (survive on >=2/3), then merge/classify.

| Metric | Value |
| --- | --- |
| Candidates | 76 (2 rounds) |
| Survived | 40 |
| Refuted | 36 (~47%) |
| Filed (after merge) | 23 - 13 Bug, 8 CR, 2 RFC |
| Cost | 245 agents, ~6.3M tokens, ~25 min |
| Lens spread | PRD 5, TRD 4, TSD 5, traceability 3, stories 1, design 5 |

## Two-profile comparison (for RFC0002)

| | Skill profile (RV0002) | Project profile (RV0003) |
| --- | --- | --- |
| Candidates -> filed | 69 -> 18 | 76 -> 23 |
| Refute rate | ~59% | ~47% |
| Dominant output | CRs/RFCs (determinism) | **Bugs** (artifact contradictions) |
| Critical/High | 1 crit, 7 high | 0 crit, 8 high |

The project profile is **more bug-heavy**: it hunts self-contradictions in finished
artifacts, where the skill profile hunted design/efficiency. Both refute rates are
healthy (the panel did real work).

## Headline findings (it audited the artifacts I generated)

- **BG0006** - the PRD names its own metadata format two incompatible ways: §4 still
  says "YAML frontmatter" (prd.md:209) while §7 says blockquote headers. My earlier
  CR0001 fix corrected §7 but missed §4 - a genuine incomplete-fix catch.
- **BG0005** - the PRD Performance NFR claims "all scripts read-only over the workspace",
  contradicting its own reconcile/verify_ac auto-fix features.
- **BG0007** - the PRD Quality Assessment marks everything Complete while four Open bugs
  (incl. BG0003 critical) sit in the same workspace - the risk section conceals risk.
- **BG0012** - `lint:links` is skill-scoped, so the `sdlc-studio/` artifact corpus is
  never link-checked (the workspace's own links are unguarded).
- **BG0013** - persona section headings carry a `[HIGH]` suffix that breaks every anchor
  link into personas.md.
- **BG0014** - story `Verify:` lines do not test what their ACs assert (broken shell/regex).
- **BG0015** - epic ownership double-mapping: github_sync/review_prep/next_id are each
  claimed by more than one epic.

## The meta finding (the audit audited the first audit)

The **design lens turned on RV0002's own output** and was right:

- **RFC0010** - the audit-filed RFC0003-0008 carry boilerplate "act vs status quo"
  options that never weigh the real choices.
- **CR0016** - all eight audit-filed CRs carry an identical placeholder AC.

These are defects in the **deterministic filing step**, not the findings themselves -
the filer wrote valid-but-shallow artifacts. This is direct, valuable input to RFC0002.

## What this proves for RFC0002

1. The project profile produces **real, actionable findings** (artifact
   self-contradictions), not noise - the harness generalises beyond the skill profile.
2. The ~47% refute rate and the self-critique argue RFC0002 should:
   - default to **triage-then-file** (or stronger merging) for the project profile to
     avoid volume - 23 findings from one run is a lot;
   - make the **filer produce richer artifacts** (real options, real AC), since shallow
     auto-filed artifacts themselves become findings.

## Recommended quick wins (cheap fixes to the artifacts I generated)

- BG0006 (prd.md:209 frontmatter wording), BG0005 (read-only NFR), CR0010 (false perf
  citation), CR0011 (plan.py location), BG0013 (persona `[HIGH]` heading suffix) - all
  small, mechanical corrections to the brownfield docs.

## Relation to RV0002

Two proving instances now exist (skill + project). Together they give RFC0002 the
telemetry it needs: refute rates, token costs (~6M each), lens yields, and a concrete
list of harness improvements (triage default, richer filing).
