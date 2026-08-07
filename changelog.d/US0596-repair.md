<!-- section: Fixed -->
- **Unifying the coverage reading had voided the guarantee it was meant to preserve.** Delegating
  the whole decision to `review_coverage` meant a recorded rejection stopped being terminal: its
  negative test reads only the per-unit verdict ledger, so an adversarial-evidence row, or a
  stale APPROVE under a later sprint-level REJECT, cleared the closing review and printed
  `N unit(s) approved` over a batch nobody had cleared. Two of the sibling unit's own mutants
  went from killed to surviving in the commit that was supposed to unify the readings. The
  shared reading is the authority on COVERAGE; a non-approving verdict is still terminal for the
  unit, and both now apply. The attribution row's new branch is removed: it appended to `covered`
  while the row's figures still came from a counter with no evidence lane, so the row printed
  `2 unreviewed` beside `US0001 by adversarial evidence` and contradicted itself in one line.
