<!-- section: Fixed -->
- **Five of batch 2's nine repairs were defective, two of them stop-ships (independent review of BG0401-BG0414).** BG0404, BG0407 and BG0401's four named guards verified; the rest did not.

  **The sign-off gate was DEADLOCKED (BG0406).** The skip refused a sign-off for any unit at `Review` - which is exactly the state this repo's two-role rule holds a unit in UNTIL that sign-off lands. Only an already-terminal unit could be signed off, inverting the central gate into retrospective paperwork. The rule is now WITHDRAWN DELIVERY, not "not yet terminal": a retracted verification depth, or a status that is neither terminal nor awaiting sign-off. `Review` is explicitly eligible, because that is the whole point of the gate. And the summary line no longer claims work it did not do - a run whose units were all skipped exits non-zero instead of printing "N unit(s) written" with rc 0 over a record holding fewer.

  **The lane brief still tracebacked (BG0405).** The guard went into `lane_dispatch` while the identical unguarded read sat three statements later in `cmd_lane`, so the artefact's own reproduction produced `RunStateError` and issued no brief. The test written for it exercised the LIBRARY function, not the command it names - this project's own recorded scar. Both remaining reads in `cmd_lane` are guarded, and the test runs the command.

  **A wrong path became a DEAD path (BG0402).** `_recorded_clause_verdicts` was changed to require `seat["clauses"]` while `_seat_from_dict` whitelisted four fields and silently stripped it, so no writer in the shipped code could produce one: the goal panel reported UNANSWERED on every close, permanently, and all six new tests asserted over a fixture shape the product cannot write. The writer now carries per-clause answers through, proven end-to-end via the CLI.

  **BG0411's AC1 was false.** `_is_artefact_file` checked only the `.md` extension, so `BG288-repro.md` - the "scratch note" the bug report itself names as sufficient - restored the false green in full. A declared id now resolves against the ARTEFACT INDEX and must live under the declared directory, which is what the Proposed Fix asked for and what no filename can forge.

  **BG0414 blocked on precisely what its docstring promised it never would**: a retro naming no units has nothing to compare, and the close returns 1 at the first failing step, so every such close hard-stopped. A nil result is now reported, not failed.

  **BG0403's second half was untested** - deleting the done-gate blocker's `cause` key survived all 600 sprint tests and the one-CR-per-unit fan-out returned in full.

  Four of the replacement tests were themselves vacuous on first write and were rebuilt - the worst asserted "a unit at Review is eligible" using a BUG, which has no Review status, so it read as "cannot say" and passed however the rule behaved.
