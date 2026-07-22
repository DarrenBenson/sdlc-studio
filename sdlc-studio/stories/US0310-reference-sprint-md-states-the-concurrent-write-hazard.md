# US0310: reference-sprint.md states the concurrent-write hazard where it states the single-writer rule

> **Status:** Review
> **Delivers:** CR0388
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md,.claude/skills/sdlc-studio/reference-review.md
> **Epic:** EP0105
> **Points:** 2

## User Story

**As an** agent about to commit while an independent reviewer is working in the same tree
**I want** the concurrent-write hazard written down beside the single-writer rule I already read
**So that** the rule covers review time as well as build time, instead of leaving the more
dangerous of the two windows undocumented

## Context

CR0388's remaining criterion, unallocated by the first decomposition of that request and added
once the grooming pass found it.

The single-writer rule is already written down, and only for a `mutation.py` run during a build.
The hazard at REVIEW time is not covered anywhere, and review is precisely when an author is
making ceremony commits (retro, review anchor, findings) that touch nothing the reviewer is
working on and therefore feel safe.

State the corrected mechanism, not the one CR0388 originally filed. The staged file did not
carry a hand-applied mutant: a helper directory of symlinks turned a shell redirect into a write
through the symlink into the live tree. Documentation that describes only the mutant case would
leave a reader confident about the wrong hazard, which is worse than silence. See also
[[LL0039]].

US0307 and US0308 build the guard. This story is the written rule the guard enforces, and it
carries no code.

## Acceptance Criteria

### AC1: The single-writer rule covers review time, not only a build-time mutation run

- **Given** reference-sprint.md, which today states the single-writer rule for a `mutation.py`
  run during a build
- **When** the rule is read
- **Then** it also states that an independent review is a concurrent-writer window, and names
  the ceremony commits an author typically makes during one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py -k "test_the_rule_covers_review_time_and_names_the_ceremony_commits or test_ac1_rejects_a_denial_of_the_review_window or test_a_ceremony_list_stripped_from_the_rule_is_caught or test_the_contradiction_is_caught_on_every_criterion_it_denies"
- **Verified:** yes (2026-07-22)

### AC2: The documented mechanism is the corrected one

- **Given** CR0388's correction, that the observed incident was a redirect writing through a
  symlink rather than a hand-applied mutant going stale
- **When** the hazard is described in either reference file
- **Then** the description names the redirect-through-a-symlink mechanism, and does not claim
  a staged mutant was the cause
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py -k "test_the_mechanism_documented_is_the_redirect_through_a_symlink or test_ac2_rejects_blaming_a_staged_mutant"
- **Verified:** yes (2026-07-22)

### AC3: The rule states why a green suite is not evidence the tree is clean

- **Given** that the observed incident was caught only because the staged file broke the suite,
  and that a surviving mutant by definition leaves the suite green
- **When** the rule is read
- **Then** it states that a passing gate does not establish that no concurrent write is staged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py -k "test_a_passing_gate_is_documented_as_no_evidence_of_a_clean_tree or test_ac3_rejects_a_green_gate_treated_as_proof_of_a_clean_tree or test_the_contradiction_is_caught_on_every_criterion_it_denies"
- **Verified:** yes (2026-07-22)

### AC4: Both reference files point at the guard rather than restating it

- **Given** US0307 and US0308 implement the declared-window guard
- **When** either reference file describes the rule
- **Then** it names the window commands as the enforcement path, so the prose and the mechanism
  cannot drift into describing different rules
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_docs_single_writer.py -k "test_both_files_cite_the_window_guard_as_the_tool_really_offers_it or test_ac4_rejects_prose_that_names_no_window_command or test_a_command_the_tool_does_not_have_is_caught or test_a_flag_the_tool_does_not_accept_is_caught or test_every_axis_catches_a_contradiction_of_its_own_property"
- **Verified:** yes (2026-07-22)

## Verification Note

**The original evidence for all four criteria was vacuous, and the prose it claimed to
verify was never wrong.** Each AC shipped `Verified: yes` on a substring `grep`:
`grep "review is a concurrent-writer window"`, `grep "symlink"`, `grep "green"`,
`grep "window"`. An independent review built a temp root, replaced both reference files
with prose asserting the OPPOSITE of every criterion, and all four greps still passed:
`green`, `window` and `symlink` each survive inside their own denial, and a distinctive
phrase survives being quoted in order to be denied. Nothing in the toolchain objected -
`grep` is deliberately exempt from the vacuity gate (it could otherwise match a signature
inside the file it searches), and `verify-lint` reported 0 suspicious lines. The sprint's
published AC-verified count included these four, so the count was four higher than the
evidence supported.

The documentation was not touched. Rewriting correct prose to satisfy a verifier would be
the same defect in the other direction, and both reference files are within a line of
their CI ceilings anyway (`reference-sprint.md` 656 of 656, `reference-review.md` 600 of
600), so adding prose was not available either.

What changed is the evidence. All four criteria are now executable, against a new checker,
`scripts/tests/test_docs_single_writer.py`. None is manual: each of the four states
something a machine can be made to judge, and the one genuinely unjudgeable part (whether
the ceremony commits named are the ones an author *typically* makes) is a matter of
wording inside a list the checker requires to be present.

The checker has three parts, and each is worth exactly what it establishes:

- **Required.** A whole asserted sentence, normalised across line breaks (which a
  line-oriented grep cannot even match), plus the facts that must sit beside it: AC1 the
  four ceremony commits in the same paragraph; AC2 one sentence naming the redirect AND
  the symlink as a single mechanism, in *both* files; AC3 that every occurrence of
  "evidence the tree is clean" carries a negation; AC4 the literal
  `mutation.py window open|close --owner` commands, cross-checked against `mutation.py`'s
  own argparse so prose and mechanism cannot drift. This is a **presence** check and
  nothing more.
- **Polarity.** Every sentence about a guarded property is judged for polarity, wherever
  in the file it sits: what a green run shows, whether a review needs a declared window,
  what may be staged during one, and the force of the guard. This is the half that
  survives a contradiction written *beside* the required text.
- **Forbidden.** A curated family of contradicting phrasings: a sentence denying the
  window, one attributing the incident to a mutant, one saying a gate "does establish".
  A blocklist, not a semantic proof - a new phrasing has to be added to it.

**Correction (round 2).** The first version of this note claimed negated prose "fails on
the required half alone, structurally: it cannot contain the asserted sentence and assert
the opposite at the same time". That was FALSE. `_requires` searches the whole document,
so a contradiction added BESIDE the required sentence satisfies it too; the structural
argument holds only for whole-document REPLACEMENT, which was the only shape the suite
tried and is not how documentation rots. The review appended four contradicting sentences
to the shipped files - the guard "advisory only", `git add -A` "the normal way", a clean
gate run meaning a clean tree, nobody needing to declare a window - and all four criteria
stayed green. The polarity scan above is the answer to that, and the appended shape is now
permanent in the suite (`AppendedContradictionTests`).

**What the checker still cannot do.** A sentence is *selected* by topic vocabulary and
*judged* by negation cues, both enumerated in `POLARITY_AXES`. A contradiction phrased
without any of the topic words, or one carried by irony or by layout rather than by a cue,
or a negation sitting further from its verb than `NEG_REACH`, is not caught. It is a
polarity scan over named topics, not a proof that the documents mean the right thing.
**AC2 has no axis at all**: a contradiction of the mechanism is caught only by the
blocklist, so a fresh phrasing of "a stale mutant did it" still escapes. The appended
contradiction did not touch the mechanism, so this repair did not widen the scan to cover
a shape nothing has yet exercised.

The discrimination proof is built into the suite (`NegatedProseTests`,
`AppendedContradictionTests`) so it cannot rot: every AC RED on negated prose and on the
appended contradiction, every axis RED on a probe of its own property, and every AC GREEN
against the shipped files, while all four original greps still passed on the same text.
Fixtures live in memory or in a temp directory, never in this tree ([[LL0039]]).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Repair: four vacuous `grep` verifiers replaced by `test_docs_single_writer.py`; evidence re-derived |
| 2026-07-22 | claude | Repair round 2 - the checker's load-bearing claim was false: `_requires` searches the whole document, so a contradiction added BESIDE the required sentence passed every criterion. A per-sentence polarity scan over four named properties now judges the whole file, the reviewer's appended shape is a permanent test, and the claim is corrected to what the module provides |
