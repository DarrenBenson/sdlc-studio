# Operator Heuristics

Cross-cutting patterns for operators running a live service alongside their development work. Distinct from `reference-agentic-lessons.md` — which is narrowly about `epic implement --agentic` wave execution — this file covers the **operator-in-the-loop** patterns: incident response, memory hygiene, release discipline.

<!-- Load when: writing a runbook, authoring a release-gate checklist, debugging a live-service incident, or reviewing a memory note before citing it -->

Each pattern below is backed by observed production incidents. Keep the pattern generic — project-specific details (config keys, agent names, PR numbers, date-stamped incidents) belong in the per-project `sdlc-studio/.local/lessons.md`, not here. If a pattern loses its supporting evidence it should be pruned, not kept on faith.

---

## Hypothesis discipline {#hypothesis-discipline}

**Pattern:** When investigating a bug, a flake, or any unexpected behaviour, state the hypothesis explicitly *before* acting. Then name the cheap test that would falsify it. Then run that test. **Do not act on a hypothesis you have not falsified or confirmed with evidence.** Bumping a timeout, adding a sleep, disabling an assertion, or "just trying" a config change without a stated hypothesis is not engineering — it is superstition with a commit message.

**Class of incident:** A test fails on a CI runner. The investigator's first instinct ("slow disk I/O on this hosted runner") sounds plausible and gets the timeout bumped. The bump silences the symptom. Six months later the same test fails again under different load — the underlying performance regression that the timeout was masking turns out to have been there the whole time. The investigation that should have happened then now happens in a production incident, with worse evidence and more pressure.

The same anti-pattern shows up under many guises. *"It's probably a race condition"* — without a stated test that would prove it. *"Network glitch"* — without a network trace. *"Memory pressure"* — without a memory measurement. *"Cold start"* — without timing the cold start. Each one is a *guess that could have been a measurement* and was treated as a finding instead.

**How to apply:**

1. **State the hypothesis as a sentence.** Not in your head — in the bug record, the commit message, or the chat. "I think the test fails because the disk is slow on this CI runner." If you can't write it down, you don't have one.
2. **Name the cheap test that would falsify it.** "If the disk were slow, `dd if=/dev/zero of=/tmp/x bs=1M count=100` would show >50ms write latency. If it shows <5ms, my hypothesis is wrong."
3. **Run the test.** Read the output. Update the hypothesis based on what you see.
4. **If the hypothesis is confirmed, fix the root cause** — not the symptom. A real slow-disk problem is fixed by moving the test to RAM, batching writes, or relaxing the test's I/O assumption — not by giving the test more time to be slow.
5. **If the hypothesis is unfalsifiable** (no cheap test can disprove it), widen it until you have one. "The CI runner is flaky" is unfalsifiable. "The CI runner has >100ms p99 disk write latency" is falsifiable.
6. **A timeout bump, sleep, retry, or `.skip` is a workaround, not a fix.** If you ship one, it must carry a `// TODO(YYYY-MM-DD)` comment naming the unproven hypothesis it papers over and the date you'll come back. Workarounds without TODOs become permanent.

**Bug close-out gate:** A bug cannot be marked Fixed unless the bug record contains all three of: (a) the hypothesis that was confirmed, (b) the evidence that confirmed it, (c) the fix that addresses the confirmed root cause. "It seems to work now" is not evidence. See also `reference-bug.md#bug-close-workflow` and the depth-tier requirements in `reference-test-best-practices.md#verification-depth-tiers`.

**Anti-pattern:** Treating an investigator's first guess as a finding. The first guess is just the *most available* hypothesis — the one shaped by recent context, surface symptoms, or the bug's title (see `#bug-title-framing`). Falsify it before letting it steer the fix.

---

## Memory-entry drift {#memory-entry-drift}

**Pattern:** A memory note that names a specific config key, flag, topology element, or file path is a *snapshot of a regime* — not a timeless law. Before citing one, verify the regime hasn't shifted.

**Class of incident:** A project's operator kept a memory note that read "do not set field X on components of type Y". It was correct for the deployment topology of the day. After a later change to how component Y was proxied, the adapter's fallback logic for field X changed: unset X now produced a silent misroute. The memory note was still there. The operator still believed it. The resulting incident burned real detection time.

**How to apply:**

- Date every memory note when written. The skill's auto-memory template does this; reinforce it for hand-written notes.
- When a memory note names a config key or path, include a `grep` or inspection line so the next reader can verify the named thing still exists.
- When the note describes a regime (e.g. "pre-migration" vs "post-migration"), spell out BOTH regimes once either has been in play. Don't delete the historical one — it may still be load-bearing for someone reading an older branch or investigating an older incident.
- Before answering "should I do X?" from memory alone, re-read the code the note references. If the current code contradicts the note, trust the code and **update the note before continuing**.
- At release-gate time, re-read any memory note that references flags, topology, or behaviour the release changes. Stale memory is one of the highest-leverage incident vectors; don't ship a release whose first consequence is invalidating your own operator notes.

**Anti-pattern:** A memory note that just says "do X" or "don't do Y" with no named regime. It will outlive the regime it was written for, and you won't notice until an incident. If you catch one of these, rewrite it to name the regime even if you have to reverse-engineer the context.

---

## Silent CLI / proxy failure localisation {#silent-cli-localisation}

**Pattern:** When a chained adapter / proxy / gateway stack returns a 5xx with sparse logs, bisect the chain by calling each hop directly. The hop where the error text gains specificity is the hop with the bug.

**Class of incident:** A multi-hop proxy returns a generic outer error ("Bad Gateway", "502", "upstream error"). The instinct is to inspect routing at the outer layer. In practice the bug is almost always at an inner hop whose error was swallowed or normalised on the way up. Direct-curling each hop reveals the layer that produces a specific error ("invalid model name", "exited with code 1", "auth token rejected") — that hop is the one with the bug.

**How to apply:**

1. Start at the innermost hop you can reach and call the same request the outer layer would have constructed. Use the exact shape — same fields, same headers, same body — not a simplified test payload.
2. Read the stderr / response body character-for-character. The error wording changes as you move up the chain; treat that progression as evidence, not as three separate bugs.
3. The hop where the error *names the mis-routed field* is the hop with the bug. At that point the fix is usually a one-line config change, not a code change.
4. After fixing, add a functional post-deploy smoke that exercises THIS path — not just a liveness endpoint. Health signals can stay green while every downstream call fails.

**Anti-pattern:** Treating a generic error from the outermost hop as the bug's location. The outermost hop is almost always the messenger, not the cause.

---

## Bug-title framing lock-in {#bug-title-framing}

**Pattern:** A bug's original title is an initial *hypothesis* about the cause — not a statement of fact. The title was written before diagnosis, often by someone with partial visibility, and it anchors every subsequent investigator toward the named layer. Treat titles as inherited context to verify, not ground truth.

**Class of incident:** A bug is filed with a title naming a specific subsystem as the cause (e.g. "X component returns error Y"). The first investigator confirms the component exists and returns that error. Subsequent diagnostic rounds assume X is the faulty layer and search for causes within it. Multiple hypotheses *within X* are confirmed-wrong; each one eats an investigation round. The actual root cause lives in a completely different layer (a DNS record, an environment variable, a parent framework, a library dependency) but was never questioned because the title made it invisible.

**How to apply:**

- When picking up a bug that's older than 24 hours, state the title aloud *as a hypothesis:* "the bug currently thinks X is at fault." Then ask: *what single cheap test falsifies this hypothesis?* Run that test first, before running any "what specifically in X is broken" tests.
- If the cheap falsifier disproves the titled hypothesis, **update the title** or add a title-correction note at the top of the bug file. Don't silently re-diagnose — future investigators will re-anchor on the original title unless it's updated.
- Bug files should maintain an explicit "Hypotheses" section near the top. Each diagnostic round should confirm or refute a SPECIFIC hypothesis. If a round resolves none, the list is incomplete; the next step is to *widen* the list, not go deeper on an existing item.
- Keep retired hypotheses visible (strikethrough, or a "Disproven by step N" annotation) so later investigators see what's been eliminated rather than re-walking the same paths.

**Anti-pattern:** Taking the title as an article of faith and going straight to "what specifically in the titled component is broken?" You'll find SOMETHING that looks suspicious in almost any component on close inspection — and confirm a wrong hypothesis by picking the most convincing of several wrongs.

---

## External-layer-first diagnostic {#external-layer-first}

**Pattern:** Before diagnosing a bug as a code problem, verify it isn't an external-layer problem. *External* = anything outside the project's own source: DNS records, mail-provider policy, cloud-provider account config, certificate validity, network firewall rules, third-party API behaviour, upstream library breaking change, DNS-hosting provider for a domain the project depends on.

**Class of incident:** A production send / API call / connection fails with a terse server-side error. The title names the application's code layer. Investigation goes deep into the application's client / sender / caller implementation. Hours in, it turns out the failure was caused by a DNS record missing on the domain, a policy change at the provider, or an expired cert — none of which the application code touches or could have caused.

**How to apply:**

For authentication / send-path / network bugs, check in this order *before* touching code:

1. **DNS.** Does the relevant domain have the required records? SPF for outbound mail, DKIM, DMARC, CAA for certs, MX for inbound, A/AAAA/CNAME for the hostname being reached. `dig` is the canonical tool. Compare against a domain or tenant where the same flow works — diff reveals what's missing.
2. **Provider policy.** Has the upstream provider changed its policy recently? Pull the provider's own current docs. Don't rely on stale forum posts, inherited assumptions, or your memory of how it worked last year.
3. **Credentials / auth state.** Token expired? Password rotated? Account locked? OAuth scopes changed? Provider-side 2FA enforcement newly applied?
4. **Certificate.** Expired, mis-issued, wrong SAN, untrusted chain, CT-log rejected?
5. **Network / firewall.** Port reachable from the origin? Egress rules? VPN / tailscale up?
6. **Only after all the above:** the application's own code.

**Diagnostic rule of thumb:** terse server-side errors ("invalid return path", "certificate verify failed", "auth required", "unknown host", "relay denied") almost always point to external-layer problems. Rich application-level errors ("processing step 3 of 7 threw RangeError at line 92") point to code-layer problems. Let the error's *detail level* steer the first diagnostic pass.

**Anti-pattern:** Assuming the code is the cause because the bug lives in the code repository. The failure may be in a layer the code cannot see or control, and all the code-layer diagnosis you do will be a dead end. This compounds with the bug-title framing lock-in above: a title naming a code component will keep you in the code layer unless you consciously break out.

---

## Post-release briefing {#post-release-briefing}

**Pattern:** When a release changes an interface that other agents or operators consume, brief them explicitly — don't rely on them to notice.

**Class of incident:** A release adds new endpoints, flags, or metric families. Programmatic consumers (agents, dashboards, other services) have no mechanism to discover the change through their normal I/O. They continue using the old shape until an operator notices the disparity, often much later. A short structured briefing at release time removes this lag.

**How to apply:**

- After tagging a release that changes a programmatic interface, identify the agents / operators that consume it. Brief each one in the channel they actually read.
- The briefing should name: (a) what surface area changed, (b) what they can now do that they couldn't before, (c) what they should STOP doing because it's no longer needed (e.g. the workaround that the release fixed).
- If briefings happen often, consider filing a CR to expose the "what's new" via a programmatic endpoint. Scope creep out of the release, but a pattern worth capturing.

**Anti-pattern:** Shipping a release and assuming consumers will read the changelog. They won't unless it's delivered to them.

---

## Adversarial review as a release gate {#adversarial-review-gate}

**Pattern:** The skill's built-in reviews (`/sdlc-studio review`, `/sdlc-studio code review`, persona consultation) assess design, pattern quality, and spec consistency. They don't reliably catch line-level nits — hardcoded strings, missed regex characters, flag-guard edge cases, stale numeric claims in docs. For that you need an adversarial review pass (the `/ultrareview` skill is one example), explicitly at the release boundary.

**Class of finding** — adversarial review on an aggregated release diff routinely surfaces:

- Stale numeric claims in prose docs (test counts, version strings, file totals)
- Hardcoded magic values where a named constant was already declared one scope away
- Shell / regex metacharacter classes that omit one or two legitimate members
- Flag-parsing guards that admit flag-shaped inputs as the positional arg
- Rollback / failure paths that omit cleanup of staging state

None of these are critical. All of them are real. All are the kind of thing a design-focused review does not look at.

**How to apply:**

- Include adversarial review as an explicit step in the release-gate checklist (see `templates/workflows/release-gate.md`).
- Run it on the aggregated diff, not per-commit. Per-commit loses the forest for the trees.
- Triage every finding into `fix-now` / `follow-up-artifact` / `wontfix-with-reason` — never ignore.
- File any follow-up CRs with a link back to the review session id so someone reading the CR later can see the original finding context.

**Anti-pattern:** Running adversarial review only after an incident. By then the signal is lost in the incident noise.

---

## See Also

- `reference-agentic-lessons.md` — agentic wave execution lessons (narrower scope)
- `templates/workflows/release-gate.md` — the checklist that operationalises the patterns above
- `reference-reconcile.md#numeric-claim-drift` — the doc-count detection this file's #memory-entry-drift pattern informs
- `help/lessons.md` — per-project `.local/lessons.md` for project-specific pitfalls (complementary, not replaced). Named incidents, bug IDs, and dated evidence belong there, not here.
