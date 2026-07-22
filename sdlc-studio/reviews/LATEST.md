# Reviews - LATEST (anchor)

> Derived from **RUN-01KY5EJX** (2026-07-22), the design rung over 40 units / 111 points.
> Closed `partial` with RETRO0067. Round 3 REJECTED and **its repair is UNREVIEWED** -
> `review.max_rounds` is 3 and the ceiling is spent. Sign-off is the operator's.

## Where the pipeline is (2026-07-22)

**The batch is groomed and ready to build.** EP0106-EP0115 plus eight bugs carry real
acceptance criteria; the DELIVERY run over the same units is the next step.

Goal: *every story's acceptance criteria would fail if the behaviour were absent, every bug
states what makes its fix complete and tested, and any declared dependency records a logical
constraint the file census cannot already derive.*

The batch attacks the loop that cost the previous sprint ten review rounds: plan a repair
before executing it (EP0106), derive a claim about a guard from the guard (EP0107), brief the
reviewer with the practices that found defects (EP0108), inventory claims first not last
(EP0109), validate `Affects` at mint (EP0110), stop a second sprint fusing into an open run
(EP0111), check the CHANGELOG's structure (EP0112), carry a REJECT forward as filed findings
(EP0113), price the sprint not the build (EP0114), hunt work done before its contract
(EP0115).

## Evidence

3,960 skill tests and 312 tool tests green. Drift 0, validate 0 errors, floor 0 violations,
no rewrite window open. **Red-now ledger: 94 criteria, pass=0, fail=91, manual=3** - nothing
vacuously green at a rung where the behaviour is absent, which is the only proof a
counterfactual bar admits. Two waves on five declared dependency edges, three of them between
units with disjoint file sets.

## What shipped as code

**BG0264** only, and it took four versions and three rejections. `verify_ac lint` refuses a
verifier whose every read is markdown. Each earlier version was defeated by an expression the
runner reads differently from the way the guard read it: the tokens as written, then an
invented flag-aware split, then "grep without `-r` never reads a directory" (true of grep,
false of this DSL), then an `rglob` walk that saw hidden and symlinked files `rg` will not
read. The parse now comes from `_build_command` and the walk from `rg --files`.

## The reviews

Three rounds, each finding something real, each finding the SAME CLASS: a rule restated
beside the thing it describes rather than derived from it. Round 1 also found that
normalising bug verifiers to a prose prefix had made all 21 unparseable while the commit
claimed they passed. Round 3 found an eighth escape and a mutant that survived because every
directory fixture was flat - fixtures agreeing by construction, unintentionally.

**Round 1's repair plan was attacked before execution and REFUTED in full** - it closed none
of the three escapes, and the attacker found two the review had missed. EP0106 is not built;
its discipline was dogfooded anyway, and it saved three rounds.

## Known holes, recorded not hidden

- **Round 3's repair is unreviewed.** Buying a fourth round or accepting it is the operator's
  decision.
- **D0056:** the goal sets dependency QUALITY, not coverage. Declaring nothing satisfies it,
  so the plan's shared-file warnings are expected.
- **BG0266:** `file <directory>` is an always-passing prose verifier the guard does not see.
- **BG0265:** a second `Verify:` line per AC block is silently dropped; six such verifiers
  have never run, all on Done stories, two inside a published claim of 84 criteria verified.
- **BG0256:** no routine sweep runs a bug's verifier at all - `walk_stories` yields only `US`
  records - so "story lint exit 0" says nothing about where these criteria were authored.
- The kill list carried by the grooming commit, including CR0403's "drawn from real failures",
  the batch's weakest leg with no criterion anywhere holding it.

## Next steps

- **Sign-off is owed and is the operator's.** `sprint close --retro RETRO0067 --apply-signoff`.
- Then the DELIVERY run over the same 40 units.
- **CR0319** is the 5.0.0 release cut, still outstanding.

## Lessons

Derive the whole behaviour, not the half you were looking at. A counterfactual bar needs a
ledger beside it. Plan the repair, attack the plan, then execute. Check whether the tool you
are about to build already exists.
