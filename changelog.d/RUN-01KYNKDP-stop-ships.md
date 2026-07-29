<!-- section: Fixed -->
- **Nine guards that failed silently, found by an independent review of RUN-01KYNKDP.** Every
  one answered a safety question in the unsafe direction and said nothing: `release_cut`'s
  close-owed check swallowed every error, so deleting one tracked file disarmed the only live
  release guard; a well-formed but WRONG declared gate id narrowed the tree to nothing, a false
  green from a typo; declaring a FILE walked past the content-read floor; `structural=None`, the
  documented "unanswered question runs the suites", answered `no`; `file_finding`'s
  `_land_unhomed` interpolated raw prose, so a finding's `steps` could forge a metadata line, and
  its heading test read the whole body so a finding merely MENTIONING a heading was refused;
  `critic record --units <ghost>` wrote verdicts for ids that do not exist at exit 0;
  `_killing_test` matched unittest's own `FAILED (failures=2)` footer, attributing every kill to
  a fabricated node; and the mutation run's pipe tied the read to EOF, so a suite backgrounding
  anything blocked the full timeout per mutant and `survived` flipped to `error`.

<!-- section: Removed -->
- **US0553 is REVERTED, not repaired.** It recorded a full-suite green on the premise that
  `sprint close` runs the suites at step 4 of seven. It does not - `gate.main` runs seventeen
  lanes and none runs a suite; the suites are run by the commit hook. So the close stamped a
  green over whatever sat in the working tree and the next commit skipped its tests: a false
  green written by the mechanism built to refuse false greens. A test now asserts the PREMISE, so
  if a gate lane ever genuinely runs the suites the decision can be revisited on evidence rather
  than on belief.
