# US0362: a command-substitution fingerprint detector with a recorded miss rate

> **Status:** Draft
> **Delivers:** CR0351
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0125
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py

## Already delivered - this story is the residue

`file_finding.shell_hazards` / `report_shell_hazards` ship, are called by every adopting
writer, and flag three shapes: an unbalanced backtick, a surviving `$(`, and a trailing
backslash. That is the detector's first half and is not rebuilt here.

Every one of those three shapes is a metacharacter that SURVIVED. The corruptions that
prompted the request are the opposite case: the substitution completed, so the backticks and
everything between them are gone and the stored text carries no metacharacter at all. The
detector is silent on exactly the four real cases it was commissioned against, and nobody has
measured that. Two things are missing: the post-damage fingerprints, and a number.

## User Story

**As a** reader of a filed finding
**I want** the filer to flag text bearing the marks of a substitution that already completed, and to state how often it fails to
**So that** I know which fields to distrust, and do not read a silent detector as proof the text is intact

## Acceptance Criteria

### AC1: the four real corruptions are a recorded corpus, each with what was lost

- **Given** the four corruptions measured during RUN-01KXVYGR - the summary that reads
  `US0251 AC2 runs .`, the two reproduction commands deleted from a lessons filing, the
  `git commit -a` executed while a bug about destructive git calls was being filed, and the
  fourth whose backticked token opened a sentence
- **When** the corpus constant is loaded by the suite
- **Then** it holds four entries, each carrying the text as stored, the text as written, and
  the token the shell removed, so the evidence is in the repository rather than in a run log
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py::CorruptionCorpusTests::test_the_corpus_holds_the_four_real_corruptions_with_what_was_lost

### AC2: the catch rate is asserted as a count, and the miss is named

- **Given** the recorded corpus and the detector extended with the post-damage fingerprints -
  a collapsed double space, a space before punctuation, and a preposition immediately followed
  by punctuation
- **When** the detector runs over all four entries
- **Then** the test asserts the NUMBER caught, not a label or a status word, and the entry it
  cannot catch is named in the assertion message as undetectable in principle - a token lost
  from the start of a sentence leaves grammatical text behind
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py::MeasuredCatchRateTests::test_the_catch_count_over_the_corpus_is_asserted_as_a_number

### AC3: no legitimate artefact field is flagged

- **Given** a sample of prose fields taken from artefacts already in the repository, none of
  which crossed a shell
- **When** the extended detector runs over every field in the sample
- **Then** it reports nothing, so the new fingerprints buy their catch rate without a false
  positive that would train a reader to ignore the warning
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_shell_hazard_rate.py::MeasuredCatchRateTests::test_no_legitimate_artefact_field_is_flagged

## Notes

Report, never refuse. A field quietly repaired, or a filing refused outright, loses the
content the author has in hand; the author is the only one who can reconstruct what the shell
removed. The detector stays defence in depth - the fields-file path is the actual fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-24 | sdlc-studio | Groomed: real ACs + Affects authored |
| 2026-07-24 | claude | Built - three post-damage fingerprints, the four corruptions recorded as a self-checking corpus, and the catch rate MEASURED at 3 of 4 with the miss named. Zero false positives over 1,668 artefact prose fields (856,277 characters). 2 tests RED first, 8 hand-mutants all killed |
