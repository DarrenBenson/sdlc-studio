<!-- section: Fixed -->
- **The premise re-check was run over the remaining backlog, and it corrected its own design
  (BG0577).** The bug proposed a repaired-but-open detector: for each open bug, run the criteria
  it already carries. Measured immediately after filing, **0 of 31 open bugs carry an executable
  `Verify:` line** - a verifier is authored when somebody TRANSITIONS a unit, which is exactly
  the step a repaired-but-open bug never reached. The check needed the artefact of the thing that
  did not happen, which is the same defect the bug is about, one level up.
  The half that does work is the COUNT re-check: four of the five fiction units stated a number,
  and every one was re-derivable. Ten of the 31 remaining bugs state one. Two were re-derived:
  BG0529's four lane-check units still print, so its premise holds; BG0555's grammar test passes,
  but only because the twelve scripts sit on a named `ROOT_GRAMMAR_DEBT` exemption whose comment
  points back at BG0555 - so that premise holds too, and a test passing was NOT evidence it did
  not. Both stay open on evidence rather than on assumption.
