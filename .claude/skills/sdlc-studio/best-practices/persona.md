# Persona Standard

The standard every design persona card (`sdlc-studio/personas/*.md`) and review seat card
(`sdlc-studio/personas/seats/*.md`) is held to. Read it before writing or reviewing a card, and
run the check before trusting one:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/persona_review.py" check [--card PATH] [--format json]
```

The check reports each card rule by rule and exits 1 when any finding blocks. Each heading
below names the rules that check it and the questions the reviewing seat answers that no rule
can. A rule's definition, what makes it fire, lives in
[reference-persona.md](../reference-persona.md#persona-rules); this page names it and says
whether it blocks.

## Blocks or reported

A rule **blocks** when it is card-level, deterministic, and its failure makes the card mislead
a brief: a seat whose role no resolver maps, a seat that cannot review, a card claiming a cast
the registry contradicts. Every other rule is **reported**: it names a defect to fix at the
card's next review, and no brief changes because of it. A roleless seat card is never resolved
and a duplicate role sits on the card the resolver does not pick, so neither can change what a
brief reads; a cast-level rule sits on no one card.

`validate.py seats` and `validate.py personas` print `blocks resolve` beside a blocking rule,
read from the same table `persona_review.py check` reads, and keep their own severity words
and exit codes. One table is the point: a second list of what blocks drifts from the first.

What the split is for: a consuming project's card argued for a Primary its registry had
demoted, and a seat card can name a persona no card declares. Each printed only a warning a
reviewer could read past; under this standard each blocks.

## Format

| Rule | Severity |
| --- | --- |
| `persona-cast-role` | reported |
| `persona-section` | reported |
| `seat-unreadable` | reported |
| `seat-no-role` | reported |
| `seat-unknown-role` | blocks |
| `seat-no-review-render` | blocks |

The reviewing seat asks: is every section filled with this person's specifics, or with
template prose renamed?

## Identity

| Rule | Severity |
| --- | --- |
| `seat-demographic-fluff` | blocks |

The reviewing seat asks: is this a specific person, not a demographic average? Does every
characteristic on the card influence a design or review decision? Strike any that influences
none; the denylist catches only the canonical demographics. An optional `## Goal Review
Questions` section, where a card carries one, asks what this person would ask of a goal; the
seat checks each question is one they would ask.

## Evidence

| Rule | Severity |
| --- | --- |
| `persona-evidence` | reported |

A card's `## Evidence` section cites the ids that ground it: an artefact on disk, a decisions
row, or a lesson in the project's or the skill's registry. The rule passes when at least one
cited id resolves; a heading alone, or ids that resolve to nothing, are reported. The rule is
the mechanical floor. Above it the reviewing seat checks each claim on the card against the
evidence cited, and strikes a claim nothing supports.

## Testable goals

| Rule | Severity |
| --- | --- |
| `persona-goal-verify` | reported |
| `persona-goal-scope` | reported |

The reviewing seat asks: would the End goal's Verify fail if the goal stopped being met, and do
its Applies-to patterns name the files that serve it?

## Consistency with the cast

| Rule | Severity |
| --- | --- |
| `persona-registry-role` | blocks |
| `seat-persona-unknown` | blocks |
| `seat-persona-role` | blocks |
| `persona-one-primary` | reported |
| `seat-duplicate-role` | reported |
| `seat-cast-size` | reported |
| `seat-core-missing` | reported |

`personas/index.md` is the registry of who is cast as what. A card whose Cast role disagrees
with it, or a seat card naming a persona the cast does not declare or in another role, blocks.
The reviewing seat asks: does this card argue for a different design target than the
registry names, in its goals or its scenario?

## Freshness

| Rule | Severity |
| --- | --- |
| `seat-malformed-stamp` | reported |
| `persona-review-owed` | reported |

The reviewing seat asks: does the card still describe the person the team designs for, and is
a generated card still labelled provisional until someone reviews it? A card is owed a review
when it has none, has changed since its PASS, or was last passed before the newest release tag;
`persona_review.py owed` lists them.

## Memory hygiene

No rule checks a persona's memory yet. The reviewing seat asks: is each learning in the
persona's memory file evidenced, still true of the card, and free of anything the card itself
contradicts?

## Anti-patterns

- Trusting a card because `validate.py` printed warnings and exited 0.
- Restating a rule's definition here instead of in the rule table.
- Reading a reported finding as permission: it is still a defect the next review owes.
