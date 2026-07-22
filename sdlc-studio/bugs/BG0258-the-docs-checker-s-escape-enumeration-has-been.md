# BG0258: The docs-checker's escape enumeration has been wrong at three, four, five, six and seven, because each repair enumerates instead of deriving

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Five consecutive review rounds each found an escape the previous enumeration had denied. Round 3 found item 4 (an unrelated negation within `NEG_REACH` launders an assertion, which the comment explicitly said could not happen). Round 4 found item 5 (a sentence with every topic word but no enumerated ASSERTING word is never judged). Round 5 found item 6 (normalise strips asterisk emphasis but not underscore, so `_proves_` escapes where `*proves*` is caught). Round 6 found item 7: an axis fires only when EVERY topic group matches, and AC3's object group is a closed list, so any synonym for the staged tree escapes selection entirely - and items 1 and 5 positively DENY that case, so a maintainer reading the list concluded those sentences were judged. Each round's author believed they had understood the previous failure and wrote a corrected count; the count was wrong again every time. Round 7 found item 8, and it is the one item 2 explicitly EXCLUDED: a polarity cue outside the closed NEG_CUES vocabulary, so 'A review without a declared window is perfectly fine' is a direct denial that reads as an assertion. Round 9 then found the same class on the OVER-fire side, where a count had just been introduced while correcting one: the scan reads only backwards from the asserting word, so a postposed cue is invisible and a natural paraphrase of the guarded rule is flagged as its own opposite. The pattern is the same one CR0394 names for guard messages: an enumeration of a rule that lives elsewhere in code is a restatement, and a restatement is only correct until the rule moves. Here the rule is emergent from three enumerated lists interacting, which is precisely the shape a human cannot enumerate reliably.

## Steps to Reproduce

1. Read THE BOUND in `test_docs_single_writer.py`, which enumerates the escapes. 2. Construct a sentence that contradicts a guarded property while matching only SOME of an axis's topic groups, for example 'A green gate proves the working copy is uncontaminated'. 3. Append it to the shipped reference-sprint.md in memory and call `check_all.` Observed: it escapes cleanly, and no item in the enumeration covers it while items 1 and 5 deny it. Repeat historically: the same procedure found a new escape against the three-, four-, five-, six- and seven-item versions.

## Proposed Fix

Stop enumerating. Derive the disclosure from the mechanism: report, for a candidate sentence, WHICH axis selected it and WHY it was or was not judged, so a maintainer asking 'would this be caught' gets an answer from the code rather than from a list a human maintains. Failing that, generate the escape corpus rather than hand-writing it - the escapes found so far were each found by an adversary constructing a sentence, which is a search a fuzzer can do continuously. Whatever is chosen, the enumeration must stop being presented as a boundary; it has been a lower bound five times running.

## Acceptance Criteria

**What makes the fix complete.** A maintainer asking "would this sentence be caught" gets
the mechanism's own answer - which axis selected it, or that none did; whether it carried
an enumerated asserting word; which cue set its polarity - so the question THE BOUND has
answered wrongly at three, four, five, six and seven is no longer answered by prose a
human maintains. The enumeration stops being presented as a boundary, and the escape
corpus is generated from the axes rather than typed by whoever last got caught out.

**Not claimed**, stated so no later reader mistakes it: this does not make the scan
complete. It makes its incompleteness derived. A contradiction written in words no axis
selects is still not caught.

Each criterion below carries its own verifier, because `verify_ac` executes only the first
`Verify` line in an AC block and stacked ones are decorative.

### AC1: the module explains its own verdict for a candidate sentence

- **Given** a sentence handed to the module rather than to a maintainer
- **When** the explanation is asked for
- **Then** it names the axis that selected the sentence or reports that none did, whether
  an enumerated asserting word was present, and which cue set the polarity - so the answer
  comes from running the mechanism, not from reading a list beside it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::EscapeExplanationTests::test_explain_names_the_selecting_axis_and_why_a_sentence_was_not_judged

### AC2: an unselected sentence is reported as unselected, never as clean

- **Given** the Steps to Reproduce sentence, "A green gate proves the working copy is
  uncontaminated", which matches some of an axis's topic groups and not all
- **When** it is checked
- **Then** it is reported as UNSELECTED, naming the topic group that failed to match,
  instead of coming back indistinguishable from prose the scan judged and passed - today
  the two are the same empty result, which is how five rounds each read a lower bound as
  coverage
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::EscapeExplanationTests::test_a_partial_topic_sentence_is_reported_as_unselected_not_as_clean

### AC3: the escape corpus is generated, and every escape it finds is reported

- **Given** the axes, their topic groups, their asserting words and their cue vocabulary
- **When** the corpus is generated from them and run
- **Then** every escape it finds is reported, so a new escape appears without a reviewer
  having to invent the sentence - and the test fails if the corpus is a hand-written list,
  because a hand-written list is the defect this bug names
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py::GeneratedEscapeCorpusTests::test_the_corpus_is_generated_from_the_axes_and_every_escape_it_finds_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
