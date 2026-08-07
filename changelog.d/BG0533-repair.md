<!-- section: Fixed -->
- **The test holding BG0533's shared-counting criterion could not fail, and the ledger said it
  had.** An independent delivery review executed the declared mutant in both directions - giving
  the enumerator its own loop, and giving `mutated_text` its own - and found the whole class
  green each time, while `mutation-runs.json` recorded that mutant as killed. A false KILLED on
  the mutation instrument is the defect class this bug exists to prevent, produced by its own
  repair. The criterion asks for a STRUCTURAL property (one routine, both readers resolving
  through it) and the test asserted a behavioural one (the two agree) - which is what two
  correct-today implementations produce by construction. It now patches `_occurrences` and
  requires both readers to move with it: the enumerator must return a sentinel it could not have
  computed, and `mutated_text` must REFUSE when fed a line the pattern does not sit on. Both
  directions of the mutant now die. The second copy of the exclusion spans that made the
  duplicate-loop edit a one-liner is gone, and the ledger record is re-taken.
