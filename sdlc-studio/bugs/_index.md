# Bug Index

**Last Updated:** 2026-10-07

## Summary

| Status | Count |
| --- | --- |
| Open | 17 |
| In Progress | 0 |
| Fixed | 787 |
| Verified | 0 |
| Closed | 87 |
| Won't Fix | 40 |
| Superseded | 31 |
| **Total** | **962** |

## All Bugs

| ID | Title | Status | Severity | Created | Updated |
| --- | --- | --- | --- | --- | --- |
| [BG0944](BG0944-three-behaviours-bg0940-and-bg0943-shipped-have-no.md) | Three behaviours BG0940 and BG0943 shipped have no test that fails when they break | Open | Low | 2026-10-05 | 2026-10-05 |
| [BG0945](BG0945-bg0940-s-changelog-entry-says-a-page-with.md) | BG0940's changelog entry says a page with a late ruling is signed, though sign refuses until the run is re-closed | Open | Low | 2026-10-05 | 2026-10-05 |
| [BG0946](BG0946-reports-index-md-last-updated-is-not-restamped.md) | reports/_index.md Last Updated is not restamped when a report is filed | Open | Low | 2026-10-05 | 2026-10-05 |
| [BG0947](BG0947-reference-outputs-md-terminal-status-table-contradicts-sdlc.md) | reference-outputs.md terminal-status table contradicts sdlc_md.TERMINAL_STATUS | Open | Medium | 2026-10-05 | 2026-10-05 |
| [BG0948](BG0948-a-migrating-project-cannot-baseline-pre-existing-placeholder.md) | A migrating project cannot baseline pre-existing placeholder findings, and v3 ids can never be baselined | Open | Medium | 2026-10-05 | 2026-10-05 |
| [BG0949](BG0949-an-inline-ruled-or-decided-ruling-is-never.md) | An inline `ruled:` or `decided:` ruling is never recognised - `_RULING_RE` puts a word boundary after the colon | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0950](BG0950-a-verdict-that-follows-critic-py-brief-s.md) | A verdict that follows `critic.py brief`'s return contract to the letter is refused by `critic.py record --from-verdict` | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0951](BG0951-critic-tier-for-reads-the-raw-difficulty-band.md) | `critic.tier_for` reads the raw difficulty band and skips every critic-role policy `route.pick` applies, so code units get a light review the routing policy says should be medium | Won't Fix | High | 2026-10-06 | 2026-10-06 |
| [BG0952](BG0952-an-open-questions-item-declaring-none-after-a.md) | An Open Questions item declaring None after a dash is read as unanswered - `_DECLARES_NONE_RE` does not allow a leading dash | Open | Low | 2026-10-06 | 2026-10-06 |
| [BG0953](BG0953-full-template-story-and-tsd-ship-unrendered-config.md) | Full-template story and TSD ship unrendered {{config.story_quality.*}} placeholders | Open | Low | 2026-10-06 | 2026-10-06 |
| [BG0954](BG0954-a-draft-story-transitions-straight-to-done-the.md) | A Draft story transitions straight to Done - the Definition of Ready is never required | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0955](BG0955-test-lean-backlog-sweep-reads-only-the-live.md) | `test_lean_backlog_sweep` reads only the live `_index.md`, so the v6.1 row archive turned main red with 25 false disagreements | Fixed | Medium | 2026-10-06 | 2026-10-06 |
| [BG0956](BG0956-transition-set-reports-index-synced-but-leaves-archived.md) | transition set reports index synced but leaves archived index rows stale, and reconcile apply refuses them | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0957](BG0957-test-epic-index-derived-s-negative-control-needs.md) | `test_epic_index_derived`'s negative control needs a live epic row with a count, so an archive that empties the live epic index turns it red | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0958](BG0958-mutation-py-finds-no-changed-lines-when-git.md) | `mutation.py` finds no changed lines when git's `diff.mnemonicPrefix` is set, so a mutation probe scoped to a unit's changes has nothing to mutate | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0959](BG0959-the-engagement-floor-rejects-a-ulid-adopt-after.md) | The engagement floor rejects a ULID adopt_after cutoff and tells you to set a sequential one | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0960](BG0960-a-plan-refused-for-a-missing-verify-line.md) | A plan refused for a missing Verify line tells you to add Affects and Points | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0961](BG0961-a-verify-line-cannot-name-the-skill-skill.md) | A Verify line cannot name the skill: <skill> is a shell redirect, not a path | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0962](BG0962-closing-review-reads-a-unit-s-latest-verdict.md) | closing-review reads a unit's latest verdict only from the frozen sprint-review ledger, so a frozen batch REJECT outlives a later per-unit APPROVE and blocks the close as a hard correctness gate | Open | High | 2026-10-07 | 2026-10-07 |

## Archived Releases

- **v6.1** (BG0659-BG0943, 283 archived) -> sdlc-studio/bugs/archive/v6.1/bug.md
- **v5.1.0** (BG0350-BG0663, 181 archived) -> sdlc-studio/bugs/archive/v5.1.0/bug.md
- **v5.0.0** (BG0302-BG0498, 178 archived) -> sdlc-studio/bugs/archive/v5.0.0/bug.md
- **v3.4.0** (BG0001-BG0052, 52 archived) -> sdlc-studio/bugs/archive/v3.4.0/bug.md
