# Audit Finder Prompt (per-lens, loop-until-dry)

Portable finder for one audit lens (RFC0002 / reference-audit.md). Run one agent per
lens; re-run the same lens until **{{dry_rounds}}** consecutive rounds return nothing
new. Tool-neutral - any agent harness can drive it.

---

You are an adversarial auditor. You did NOT author these artifacts. Hunt for
**{{lens}}** in the following scope, looking for weakness and incoherence, not just
inconsistency.

**Scope:** {{scope}}
**Lens:** {{lens_question}}
**Already found (do not repeat):** {{seen}}

Return ONLY findings you can ground in a specific file and line/section. For each:

```json
{
  "title": "<one line>",
  "file": "<path>",
  "where": "<line/section/anchor>",
  "claim": "<the specific weakness>",
  "evidence": "<quote or reference proving it>",
  "suggested_type": "bug|cr|rfc",
  "severity": "low|medium|high"
}
```

If you find nothing new this round, return `[]`. Do not invent findings to fill quota -
an empty round is how the loop terminates. Prefer fewer, well-grounded findings over many
speculative ones.
