# CR-0229: engagement floor: mandatory planning when the change is multi-file in a spec-bearing repo

> **Status:** Complete
> **Target:** v4.1
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file
> **Depends on:** BG0110

## Summary

The v4 benchmark rerun (docs/benchmarks/2026-07-10-v4-rerun.md, finding 3) showed the scale-to-size judgement failing model-dependently: every Sonnet and Opus pipeline-arm agent judged a multi-file, spec-interacting ticket too small for ceremony and shipped the hidden-requirement defect the ceremony catches, while frontier-model agents engaged unprompted. The engagement threshold must not be left to the weaker model's own judgement. Ship a deterministic engagement floor: when a change touches more than one source file in a repo carrying a numbered spec (or sdlc-studio workspace), the planning/AC pass is mandatory, not advisory - a small, checkable rule in the doctrine and agent-instructions template, with an explicit config opt-out for operators who accept the risk.

## Acceptance Criteria

- [ ] (moved to CR0232, shipping in v4) ~~The doctrine and the shipped agent-instructions template state the floor as a hard rule~~
- [x] The floor is mechanically checkable where an sdlc-studio workspace exists (gate or conformance refuses a Done multi-file unit with no plan/AC artefact), advisory prose elsewhere
- [ ] A future protocol revision measures the floor as its own benchmark arm (noted in protocol docs; not a blocking AC for this CR)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
| 2026-07-10 | Claude (sprint driver) | split per operator: the prose floor ships in v4 as CR0232; this CR keeps the mechanical gate + protocol arm for v4.1 |
| 2026-07-13 | Dani Okafor (Engineering) | AC2 delivered: `engagement_floor.py` + the blocking `engagement-floor` gate lane (Affects ∪ git-cross-check signal, `adopt_after` cutoff, judgement-mode opt-out, BG0110 waiver reuse). AC3 remains a future protocol arm (non-blocking) |
| 2026-07-13 | Sam (QA) | REJECTED first pass: the omission hole was open for stories (git leg only fires when a commit names the id, and story/bug templates had no `Affects` field), so a multi-file no-AC story reached Done with the floor silent - and the docs claimed "cannot be dodged by omission". Also: a forward `adopt_after` silently disarmed the project, and the git leg over-fired on batch commits |
| 2026-07-13 | Dani Okafor (Engineering) | Repaired. F1: a shipped unit now skips planning only by planning OR DECLARING a single-file `Affects` - a unit that does neither fails `undeclared`; `Affects` added to the story/bug/CR templates. F2: a cutoff above the highest existing id is refused (a forward disarm, not grandfathering) and exempt-would-violate units stay counted. F3: batch commits (naming several ids) feed no id's git leg, and the summary counts multi-file units separately |
| 2026-07-13 | Sam (QA) | REJECTED again: MD012 in the story template failed markdownlint; `_affects_declared` accepted prose (`n/a`, `various`) as a declaration; the "cannot be dodged by omission" claim overstated the guarantee (understatement in a shared commit is not caught) |
| 2026-07-13 | Dani Okafor (Engineering) | Repaired round 3. Fixed MD012 (confirmed via markdownlint). Hardened `_affects_declared` to require a real file-path token, so `n/a`/prose fail `undeclared`. Restated the guarantee honestly in the docstring, reference-scripts-verify, reference-config: catches pure omission + solo-id-commit understatement; shared-commit understatement is a known limit filed as **CR0239** (commit-id convention). Reconciled D0021 via **D0026** (supersedes it; the "both signals together close it" overclaim corrected, the required-Affects + cutoff parts stand). Added a boundary test pinning the R2 limit |
