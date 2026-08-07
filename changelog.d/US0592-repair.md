<!-- section: Fixed -->
- **A preview plan can no longer bank a permanent waiver.** `--goal-review-waived` recorded its
  decision-log row whether or not `--write` was given, and a waiver is read by SUBJECT rather
  than by run - so a preview silenced the compulsory `goal-seat-reviewed` item for a later,
  unrelated close. It is refused without `--write` now, refused beside a stated goal (where the
  gate is armed and the escape is not the answer, rather than being silently ignored), and not
  banked under the no-seats carve-out where no refusal could ever have fired.
