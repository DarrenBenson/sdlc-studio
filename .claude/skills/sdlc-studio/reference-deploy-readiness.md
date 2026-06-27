# Deploy Readiness Reference

<!-- Load when: writing or reviewing a deploy script, debugging a deploy that fails post-rollout, planning a release-gate checklist that includes a smoke pass, or designing a healthcheck contract for a new service -->

Patterns for making post-deploy verification reliable. Every pattern below is generic – it applies regardless of language, platform, or whether the project uses Docker, systemd, Kubernetes, or bare process management. The only assumption is that the project has *something* the deploy script calls "smoke" – a post-rollout functional verification.

The patterns are written down because they are the failures that occur **silently** if you don't think about them in advance. By the time the operator notices, the deploy has half-rolled-out, smoke is timing out, and the rollback path is being exercised under pressure rather than in calm.

Companion files:

- `reference-test-best-practices.md#verification-depth-tiers` – the depth vocabulary the smoke pass produces evidence at
- `templates/workflows/release-gate.md` – the checklist that operationalises this file
- `reference-operator-heuristics.md` – incident-response patterns for when smoke fails post-deploy

---

## Cold-Spawn Pre-Warm {#cold-spawn-pre-warm}

**Pattern:** When the slowest path's cold-start time approaches the smoke budget, the smoke pass becomes a lottery. The fix is to **pre-warm** the cold path before triggering smoke – either via the deploy script or as an explicit pre-deploy step.

**Class of incident:** A multi-service deploy contains a heterogeneous mix of workloads. Most services warm in 1–5 seconds. One service (a CLI-spawning agent, a JIT-compiled language runtime, a model-loading inference path) takes 60–90 seconds cold. The smoke budget is set to 90 seconds because that's "enough for normal traffic". Every deploy then gets unlucky – the cold path lands within milliseconds of the timeout. Smoke fails, auto-rollback fires, the deploy reverts. The next deploy attempt fares the same way. The operator concludes "the deploy is broken" when the actual problem is a smoke budget that doesn't account for cold-spawn variance.

**Detection rubric:**

For each smoke target, watch the rolling timing:

- If `last-deploy-time(target) > 0.6 × smoke_budget` → mark target as **cold-spawn-sensitive**.
- If `last-deploy-time(target) > 0.85 × smoke_budget` → cold-spawn-sensitive AND the smoke pass is one bad hand away from failure.

The threshold is 60% because variance compounds: a target that runs at 60% of budget on average will exceed budget regularly under load.

**How to apply:**

1. Identify cold-spawn-sensitive targets via the rubric above. Maintain the list in deploy-script config or in `sdlc-studio/.local/deploy-targets.json`.
2. **Pre-warm before deploy.** Before pulling the new image / rolling the systemd unit / restarting the process, send the cold-spawn-sensitive target a benign request that exercises its slow path. The next request – the smoke ping post-deploy – hits a warm runtime.
3. **Or auto-pre-warm in the deploy script.** Detect the target on the rolling-timing list and emit a pre-warm request as the first step of the rollout, *not* the smoke pass.
4. **Or extend the smoke budget for that one target.** Per-target budgets beat single-budget-for-all. This is the simplest mitigation when pre-warm isn't feasible (e.g. the cold-spawn IS the path being smoke-tested).

**Anti-pattern:** "Just retry smoke once on failure." Retries paper over the symptom while leaving the variance unaddressed. The next deploy still has the same lottery. Pre-warm fixes the cause; retry buries it.

---

## Smoke Budget Sizing {#smoke-budget-sizing}

**Pattern:** Smoke budget = (slowest-path observed worst-case) × 1.5. Not the average. Not the median. The worst-case.

**Class of incident:** Smoke budget is set as the average of all targets' last-known timings. The math looks reasonable: 8 targets × ~10s each → 80s total budget. But the SLOWEST target on its WORST day takes 80s by itself; on a deploy where it lands worst-case, it consumes the entire budget and the seven faster targets never get to run. Smoke times out. Auto-rollback fires. The deploy reverts.

**How to apply:**

1. **Per-target budgets, not single shared budget.** Each smoke target has its own deadline based on its own observed worst-case. Sum them for the total budget; don't compute the total first.
2. **Multiplier of 1.5 above worst-case.** The 0.5× headroom is for the variance that happens between the last measurement and the next deploy. If you observe 60s worst-case, set the budget at 90s. If you observe 4s worst-case, set it at 6s.
3. **Refresh worst-case after every deploy.** A target whose worst-case grew last deploy needs its budget grown next deploy. Treat "smoke budget never changes" as drift – refresh the rolling-worst-case on every successful deploy.

**Anti-pattern:** Sizing the budget to the *current target* of latency rather than *observed* latency. "It should be 5s, so let's give it 7." If it's actually 12s today, the deploy fails and the ambition was wrong. Size to reality, then improve reality separately.

---

## Auto-Rollback on Smoke Fail {#auto-rollback-on-smoke-fail}

**Pattern:** Smoke fail = automatic rollback. Non-negotiable. The deploy script's exit guarantee is that the system is in a known-good state when control returns to the operator.

**Class of incident:** A deploy script rolls out the new version, runs smoke, sees a failure, prints an error, and exits. The operator sees the error in their terminal but doesn't immediately roll back because they're investigating. Meanwhile the new (broken) version is serving production traffic. Real-user errors accumulate during the investigation window.

**How to apply:**

The deploy script must:

1. **Capture the pre-deploy state** before the rollout. For Docker: snapshot the previous image SHA. For systemd: capture the prior unit revision. For Kubernetes: track the prior `Deployment` revision. The capture is part of the deploy script's protocol.
2. **Roll out the new version**, then run smoke.
3. **On smoke fail, restore the captured state** automatically. Print the rollback summary. Exit with non-zero.
4. **On smoke pass, retain the captured state** (as the current rollback target until the next deploy supersedes it).

The deploy script's contract: when control returns to the operator, the system is either (a) running the new version with smoke green, or (b) running the previous version with smoke green. There is no third state where the system is running the new version with smoke red.

**Override:** `--skip-smoke` (or equivalent) for emergency-fix scenarios where the operator accepts the risk explicitly. The flag must be loud – log a warning, print a banner, write to incident log.

**Anti-pattern:** "We'll roll back manually if smoke fails." Manual rollback under incident pressure is slower, more error-prone, and may forget the pre-deploy state. Automate it.

---

## Readiness Wait Before Smoke {#readiness-wait}

**Pattern:** Smoke must not start until the deployed component reports both **version match** and **ready** state. Starting smoke earlier is racing the rollout.

**Class of incident:** A deploy rolls the container, then immediately fires smoke. The container is up but still loading config / connecting to dependencies / warming caches. Smoke fails because the component isn't ready yet, not because the deploy is broken. The script auto-rolls-back the perfectly-good deploy.

**How to apply:**

1. **Health endpoint contract.** The deployed component must expose a `/health` (or equivalent) endpoint that reports at least:
   - `version` – the version actually running, not the version intended.
   - `state` – one of `starting | ready | degraded | failed`.
   - `dependencies` – one row per upstream the component needs (DB, cache, downstream service), with state per row.
2. **Readiness wait protocol.** After rollout, poll the health endpoint at 1–2 second intervals. Wait until: (a) version equals the deployed version, AND (b) state is `ready`. If either is wrong after `readiness_timeout` (default 60s), abort and roll back.
3. **Only after readiness is confirmed**, fire smoke. The smoke budget starts now.

**Anti-pattern:** Polling for HTTP-200 from `/health` without checking the version field. The previous version's health endpoint also returns 200; this races the rollout silently.

---

## Smoke Targets and Coverage {#smoke-coverage}

**Pattern:** Smoke must exercise every functional path the deploy could affect – per-agent, per-channel, per-adapter. Not just liveness.

A health-endpoint 200 says only "the process started." It says nothing about whether traffic actually flows through any specific path. If the deploy broke the path that calls `/v1/foo` for agent X, but you only smoke `/health`, the deploy proceeds and the breakage hits real users.

**How to apply:**

1. **One smoke target per independently-failing path.** If your project has agents, channels, adapters, or per-tenant configurations, each gets its own smoke. The granularity is "if this path could break independently of the others, it gets a smoke target."
2. **Smoke = single round-trip = `functional` tier.** See `reference-test-best-practices.md#verification-depth-tiers`. Smoke is functional verification per target, not just smoke (compiles + handshake) verification.
3. **Smoke does not = `conversational` tier.** Multi-turn / multi-step verification is too slow to run on every deploy. Save it for stories whose AC requires it. But smoke must be at LEAST functional, not just liveness.

**Anti-pattern:** Conflating smoke with health. Smoke is a per-path functional round-trip; health is a process-level liveness check. They are different gates with different signals.

---

## Pre-Deploy Gates {#pre-deploy-gates}

Before the deploy script even starts the rollout, verify:

| Gate | Why |
| --- | --- |
| **CI green for the target version** | The version was tested in CI; deploying without confirming this risks shipping a known-broken commit. Use `gh run list --commit <sha>` or equivalent. |
| **Tag / version resolves to a SHA** | "Deploy v1.2.3" is meaningful only if v1.2.3 maps to a unique commit. Resolve before rollout; abort on ambiguous tags. |
| **SSH / kubectl / API reachability** | If the rollout target is unreachable, fail fast. The error is much clearer at "step 1: connect" than at "step 5: roll" half-way through. |
| **Idempotency check** | If the target is already on the requested version, exit early with a no-op message. Don't pretend to do work. |
| **Backup of pre-deploy artefacts** | Snapshot prior compose / unit / config files. Required for the auto-rollback contract above. |

---

## Pre-Deploy Checklist {#pre-deploy-checklist}

Recurring deploy-time failure classes that pass every unit test yet break in production. Each is a mechanical check a release script should run (and abort on), not a manual reminder.

| Check | Failure it prevents | How |
| --- | --- | --- |
| **Env-key diff** | A changed default silently breaks the deploy. Replacing a hardcoded value with `${VAR:-default}` ships the default when prod's `.env` lacks `VAR`. | Diff `.env.example` against the target environment's `.env`; **refuse to deploy** if a required key is missing, rather than letting the fallback apply. |
| **Persistent-volume assertion** | A durability contract is betrayed by a non-persistent path. A feature "tested" against a tmpdir resolves, in the container, to a path that is not bind-mounted, so every restart wipes it. | Assert at startup that each durability target is on a persistent volume, or require an explicit operator-set path. Add to every such feature's AC: *restart the container; verify the data survives.* This is the deploy-side sibling of the deploy-meta-files gap class (LL0006). |
| **Remote-command heredoc discipline** | A remote command silently does not fail. `set -e` inside `bash -c '...'` over ssh does not propagate, and layered awk/sed quoting mangles. | Use `ssh ... bash -s <<'EOF'` heredoc form with explicit `$?` checks; never `bash -c "..."` for multi-command remote blocks. |
| **Crypto serialisation round-trip** | An ops helper that mirrors a crypto routine stores a value the canonical decryptor cannot read (e.g. base64 where hex is expected), breaking production at read time. | Any helper that touches encrypted state must round-trip against the **canonical** decryptor before it is trusted - mirror the serialisation format byte-for-byte, not just the algorithm and key. |

The env-key diff and the persistent-volume assertion are mechanical gates a project wires into its release script or container startup (abort on failure). The remote-heredoc and crypto-round-trip items are authoring disciplines a reviewer confirms.

---

## Soak Window Discipline {#soak-window}

**Pattern:** A feature is not Done until it has soaked under live traffic for the configured window (default 7 days). Smoke green is necessary but not sufficient.

This pairs with the verification-depth `soak` tier and the `staged-rollout` release strategy. Stories whose AC carries `Verification target: soak` cannot be marked Done immediately post-deploy; they remain In Progress / Verifying until the soak completes.

**Soak monitoring contract:**

- Define the metric(s) that would indicate degradation (error rate, latency p95, queue depth, etc.).
- Sample the metric at deploy time as the baseline.
- Re-sample at end-of-soak. If degraded beyond a configured tolerance, fail the soak and roll back.
- Document the soak result in the story's verification record (which AC, which window, what metrics, before/after sample).

**Anti-pattern:** Marking soak-target stories Done immediately after deploy on the basis of smoke green. The soak window exists *because* smoke is insufficient evidence for soak-target ACs.

---

## See Also

- `reference-test-best-practices.md#verification-depth-tiers` – the tier vocabulary; smoke is functional-tier evidence
- `reference-test-best-practices.md#test-timeout-tuning` – tuning timeouts for smoke targets uses the same measure-CI-variance discipline
- `reference-decisions.md#release-strategy-decision` – when to choose `staged-rollout` (which makes the soak window mandatory)
- `reference-operator-heuristics.md#silent-cli-localisation` – when smoke catches a path-level failure, this is the localisation pattern
- `templates/workflows/release-gate.md` – the release-gate checklist that aggregates these patterns
