# CR-0121: gate points at the conformance adopt_after remedy instead of burying it in a docstring

> **Status:** Proposed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

When `conformance` fails on a large count of Done units that lack per-unit Verified/critic
annotations, the gate prints "N non-conformant" and nothing else. The mechanism that legitimately
resolves it - the `conformance.adopt_after` cutoff (forward-only adoption), or a dedicated `verify_ac`
backfill tranche - is documented only in `conformance.py`'s source docstring. Nothing connects "gate
says 92 non-conformant" to "set this config key" or "run this backfill". You have to already know the
remedy exists. Two compounding readability problems the field surfaced:

- A failure of 92 reads as "the upgrade broke something" when it is actually **pre-existing accepted
  debt that merely grew** (later Done tranches shipped without the annotations). The gate does not
  distinguish "newly broken by this change" from "unadopted-discipline debt".
- The config comment hard-codes a count (`adopt_after: ... # 24`) that goes stale as the debt grows
  (the operator found it reading 24 while the real count was 92), so the annotation misleads.

## Acceptance Criteria

- [ ] on a conformance failure, the gate/conformance output names the remedies inline: the
      `conformance.adopt_after` cutoff (with the correct value format - see [[BG0039]]) and the
      `verify_ac` backfill path, not just a bare count
- [ ] the output distinguishes "unadopted-discipline debt (pre-existing, forward-only)" from
      "regressions introduced by the current change", so a grown-but-accepted count does not read as a
      new breakage
- [ ] guidance is not to hard-code a stale count in the `.config.yaml` comment; if a count is shown it
      is the live computed figure, or the comment is countless
- [ ] reference docs cross-link the remedy from the gate, not only the script docstring; unit test
      asserts the failure message includes the remedy pointer; CHANGELOG

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
