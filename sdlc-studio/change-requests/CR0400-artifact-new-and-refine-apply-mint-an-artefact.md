# CR-0400: artifact new and refine apply mint an artefact with an unresolvable Affects without a word, while file_finding refuses the same path

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py,.claude/skills/sdlc-studio/scripts/refine.py,.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The check already exists and is on the wrong door. `file_finding.py file` REFUSES a finding whose declared Affects resolves to nothing, allocating no id and writing nothing, which is correct and caught several bad paths during RUN-01KY3MFX. `artifact.py new` and `refine.py apply` perform no such validation: refine handles no Affects field at all and artifact does not resolve the value it stores. Measured on that sprint: of 23 stories minted through `refine apply`, FIVE carried a wrong or incomplete Affects, and the author typed the same wrong prefix (a reference doc under `scripts/`) six separate times across the session, twice inside artefacts filed about that very defect and once minutes after ruling on it in a decision of record. Each one was caught later and by something else - a grooming agent reading the file, a reviewer, or the author re-reading - never at the moment it was written. Every occurrence entered the tree through the two commands that do not check. This is not a knowledge problem: the author knew the rule and had written it down. It is a typing-shaped hazard on a field three separate consumers depend on, and the one command that guards it proves the guard is cheap.

## Impact

Every consuming project, on the two commands artefacts are actually created with - `refine` is the mandated route from a request into delivery units, so a whole batch of stories inherits whatever the caller typed. The failure is silent and fails open in three directions at once: the plan's collision analysis clusters parallel work by Affects and so mis-groups lanes; the engagement floor takes its declared file-count signal from Affects and so under-reads a unit's footprint; and `gate`'s changed-surface reporting reads it too. A wrong path in that field therefore degrades parallel-safety, the planning-pass gate and the evidence report simultaneously, while every command exits 0.

## Acceptance Criteria

- [ ] `artifact new` and `refine apply` validate a declared Affects with the SAME predicate `file_finding` uses, refusing before any id is allocated so a bad path mints nothing.
- [ ] The refusal names the closest unique basename match where one exists (CR0399), so the caller is told the answer the tool can already see rather than being sent to look for it.
- [ ] A path to a file the unit will CREATE is still legitimate: the check refuses only when NO declared path resolves, matching the rule the grooming gate already applies, so the ordinary case of naming a not-yet-existing file is unaffected.
- [ ] One shared helper serves all three writers, so a future writer cannot be added without the check and the three cannot drift on what 'resolvable' means.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
