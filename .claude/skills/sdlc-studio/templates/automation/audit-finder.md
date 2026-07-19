# Audit Finder Prompt (per-lens, loop-until-dry)

Portable finder for one audit lens (the adversarial audit, see reference-audit.md). Run one agent per
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

---

## Carry-over candidate pool (skip the find phase)

When the harness is given a carry-over file from an earlier capped run
(`--carryover .local/audit-carryover-<date>.json`), **run no finder lenses at all**. The
records in that file are already grounded in a file and a claim, so re-finding them would
spend finder agents re-deriving what is written down - and might derive it differently.

Load the file's records as the carry-over candidate pool verbatim and go straight to the refute panels,
one panel per record, exactly as if the finders had just returned them. The run's cost is
refute agents only. Anything the panels leave unverified because a cap bit again is written
back out as a fresh carry-over file, so the tail never shortens by being forgotten.
