# Audit Merge & Classify Prompt

Portable merge/classify step (RFC0002 / reference-audit.md#audit-taxonomy). Runs once
over all refute-panel survivors before filing.

---

You are triaging audit survivors for filing. You are given the findings that survived
the refute panel. Do two things:

1. **Merge.** Collapse near-duplicates (same file + same underlying claim) into one,
   keeping the clearest title and the union of evidence.

2. **Classify** each merged finding by the standard rule:
   - **bug** - something is broken/wrong now (false claim, dangling ref, a test that
     does not test). Must carry Steps to Reproduce + a Proposed Fix.
   - **cr** - a concrete, agreed improvement to a settled area. Must carry checkable
     acceptance criteria.
   - **rfc** - an unsettled design question with real options to weigh. Must carry the
     options + the open decision.

**Survivors:** {{survivors}}

For each merged finding, emit the exact fields the filer needs (so it can write a rich,
non-hollow artifact - hollow auto-files become findings themselves):

```json
{
  "type": "bug|cr|rfc",
  "title": "...",
  "summary": "...",
  "severity": "...",            // bug
  "steps": "...", "fix": "...", // bug
  "priority": "...", "ctype": "Improvement|Feature|Bug", "acs": ["..."],  // cr
  "options": ["..."], "recommendation": "..."                            // rfc
}
```

Then file each with `scripts/file_finding.py file --type <t> --title ... <fields>`
(triage-then-approve by default; auto-file only when explicitly enabled).
