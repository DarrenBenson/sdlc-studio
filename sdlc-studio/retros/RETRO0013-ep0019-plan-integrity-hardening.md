# RETRO-0013: EP0019 - plan-integrity hardening (the gate that catches a wrong plan)

> **Date:** 2026-07-09
> **Batch:** EP0019 / US0090-US0093 (closes CR0194 + CR0195 + CR0196; CR0197 deferred)
> **Goal:** `done` - make a mis-pinned or falsified plan un-shippable, schema-v3 dormant
> **Delivered:** 4 / 4   **Blocked:** 0

## Delivered

- **US0090** - the deterministic **plan-review gate** (`plan_review.py`): a story with
  spec-derived ACs cannot reach implementation (In Progress/Review/Done, wired into
  `transition.py`) without an independent plan-review verdict. The trigger fires by rule (a
  spec citation, an `affects_files` threshold, or a difficulty band) - no model judgement in
  fire/skip (ADR-006), so it is not skipped under effort pressure. `critic.py` gained a
  `--phase {delivery,plan-review}` split (own log, so a plan-review APPROVE never satisfies the
  delivery critique gate); `plan_review record` pins the verdict to the reviewed ACs by
  fingerprint, so a post-approval AC edit invalidates it. The only sanctioned skip is a recorded
  `> **Plan-Review-Override:**`.
- **US0091** - the **plan-reviewer charter** (the QA seat re-reads the cited spec section and
  flags an inverted AC as blocking, escalating to blind re-derivation for high-difficulty units),
  a story-template `> **Plan-Review:**` slot, and plan-review **telemetry** (its own summarise
  block: run count, verdict mix, independent-review rate).
- **US0092** - the **spec-edit guard** (`spec_guard.py`): a delivery diff that edits a
  requirements/spec document the story never references is `untraced` - the critic charter's
  blocking signal. Closes the N=5 case where a worker falsified the spec to match a wrong build.
- **US0093** - repo-only **bench-runner phase field**: calibration rows are excluded from the
  summary by the tool, not by hand (protocol v2's no-pooling rule made mechanical).

All era-gated behind `schema_version: 3`, dormant on v2 (the repo is v2; the release freeze holds).

## Critic loop, observed

Four independent per-unit critics (each a separate instance from the author, each framed to
refute) plus the closing full-diff pass. **Every per-unit critic found a real defect the
author's own tests passed over**, and two of the four required more than one round because the
first fix introduced or missed something.

| Unit | Verdict path | The escape the author's own tests missed |
| --- | --- | --- |
| US0093 | APPROVE (3 fixed) | `--include-phase` typo failed silently to measured-only; `record()` mutated the caller's dict; missing CHANGELOG |
| US0090 | REJECT -> fix -> APPROVE | the gate fired only on entry to In Progress, so a spec-derived story could be closed **straight Ready->Done unreviewed** - a complete bypass of the gate's purpose; plus a stale-approval TOCTOU (verdict bound to id, not AC content) and an extension-less spec-path under-fire |
| US0091 | REJECT -> fix -> APPROVE (3 rounds) | plan-review telemetry polluted the unit-close aggregate (phantom `unknown` type); then the fix for the independence-flag introduced a **regression** - `import critic` outside the try/except with no `sys.path.insert`, so it raised on a clean interpreter and the green was order-dependent |
| US0092 | REJECT -> fix -> APPROVE | story-wide traceability let an **untraced edit to spec B ride on a mention of spec A** (a `Verify: grep` line or `Affects:` header) - the exact under-flag CR0195 forbids; fixed to per-edited-file matching |
| Closing full-diff | APPROVE (1 LOW fixed) | the two spec-protection features drew the spec boundary differently - `plan_review.spec_globs` used `*.spec.md` while `spec_guard` used `*spec*.md`, so a root `SPEC.md` tripped one gate but not the other; a cross-unit inconsistency no per-unit review could see. Aligned both to `*spec*.md` at close |

Three per-unit REJECTs were genuine correctness bugs, each reproduced by the critic, fixed
test-first, and re-reproduced clean by the **same** critic before APPROVE.

## What went well

- **The independence gate is not ceremony - four for four again.** Every reviewer that did not
  write the code found a real defect. US0090's was a complete bypass of the feature's whole
  point (Ready->Done), invisible to every author test.
- **Re-run-your-own-repro caught a fix's own regression.** US0091's independence fix broke the
  best-effort no-raise contract; the same critic re-running its repro **in isolation** caught
  that the full-suite green was order-dependent (cross-test `sys.path` pollution). A fix can
  introduce its own escape; re-verification is where that dies.
- **Era-gating held end to end.** Every feature is dormant on v2; the closing pass exercised a
  full v2 repo and confirmed nothing changes v2 behaviour - the release-freeze contract intact.

## What was hard

- **Shared-file composition, again.** `critic.py`, `plan_review.py`, `config-defaults.yaml`, and
  `reference-agent-prompt-template.md` were each touched by two or three stories, so true parallel
  worktrees would have collided. Sequential-as-orchestrator (W1{US0090,US0093} -> W2{US0091,US0092})
  with a per-unit critic, then a closing full-diff pass, was the right call. US0093 (repo-only,
  no shared skill files) was the only genuinely parallel unit.
- **A deterministic proxy for a judgement.** Both gates (plan-review, spec-edit) had to be
  hard-to-dodge triggers with the *judgement* left to the critic. The under-flags both critics
  found were where the proxy quietly answered a judgement question ("was this spec edit
  requested?") too generously. The fix each time was to make the proxy narrower and surface the
  rest for the critic, never to silently clear it.
- **The catalogue at its ceiling, third sprint running.** `reference-scripts.md` needed two new
  entries; allowlisted at 643. The split is now overdue - filed as a follow-up, not smuggled in.

## Lessons

- **A gate must guard every path to the guarded state, not the tidy one.** US0090 fired on
  In Progress; the wrong plan walked in through Ready->Done. Enumerate every entry to the state
  the gate protects.
- **A fix is a change and earns its own adversarial pass.** US0091's regression was introduced
  by the fix for a LOW finding; only re-running the repro in isolation exposed it.
- **A deterministic "traced/safe" label is dangerous when it answers a judgement question.**
  Surface the fact (this spec file was edited / referenced) and leave "was it requested?" to the
  critic; never let the proxy stamp it cleared.
- **Deferred, on purpose:** CR0197 (upgrade re-baseline) depends on this gate existing and is the
  natural next sprint; the `reference-scripts.md` split; a path-aware tightening of the spec-guard
  basename match. All recorded in the ledger, none smuggled into this sprint.

## Metrics

- Delivered 4/4; 0 blocked. 5 adversarial reviews (4 per-unit + closing), 18 real findings
  (2 MAJOR gate-bypasses, the rest MEDIUM/LOW), 0 shipped unaddressed. Two per-unit reviews took
  3 rounds (US0091's fix introduced its own regression; US0090/US0092 REJECT then re-verified).
- 1366 script tests pass (was 1312 at EP0014 close; +new plan-review/spec-guard/telemetry/bench
  tests). Gate PASS; reconcile drift 0 throughout; per-unit conformance 7/7 on all four.
- Story index now 39 terminal rows (> 30 advisory) - archive deferred to the v4.0 cut (no release
  label to archive under mid-freeze).
