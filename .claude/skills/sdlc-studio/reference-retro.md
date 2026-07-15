# Retro Workflow Reference

<!-- Load when: writing or closing a retro, or wiring the close gate. Pairs with help/retro.md -->

Deep workflow for `/sdlc-studio retro`. Load with `help/retro.md`.

The retro is the **adapt** half of inspect-and-adapt. Inspecting is easy and teams do it
willingly; adapting is the half that gets skipped, because nothing forces a finding to
become anything. This is the machinery that forces it.

File: `sdlc-studio/retros/RETRO{NNNN}-{slug}.md` · Index: `sdlc-studio/retros/_index.md`
· Template: `templates/reviews/retro.md` · Script: `scripts/retro.py`

## The loop

```text
sprint closes
  -> retro created            artifact new --type retro
  -> findings dispositioned   filed as BG/CR, or declined with a reason
  -> lessons extracted        retro extract   -> project lessons log
  -> summary regenerated      lessons summary -> the digest
  -> close gate               retro validate  (blocking)
       |
next sprint plan prints the still-valid lessons, unasked, in the plan the agent reads
```

The last line is the whole point. A lesson that does not reach the next plan has not been
learned by anything except the person who wrote it, and they were not the one who needed it.

For an INTERACTIVE sprint (no runner, so no per-unit telemetry), supply the harness-tracked token
total: `retro.py accuracy --id RETROxxxx --tokens N --write`. That yields a real, descriptive sprint
tokens-per-point over the delivered points - the token count is deterministic, so report it as
not-yet-captured until you supply it, never as if it were unknowable. It stays descriptive,
never a target.

## What the close gate checks

`gate --require-retro RETROxxxx` delegates to `retro.py validate`, which reads the
**content**:

1. **Required sections present** - `Delivered`, `What went well`,
   `What was hard / what stalled`, `Lessons`, `Actions raised`. Each is a question the
   ceremony exists to ask; a retro that drops one did not hold the ceremony.
2. **At least one real lesson** - an unfilled `{{placeholder}}` is not a lesson. "This
   sprint taught us nothing" is a legitimate answer, but it must be *stated*, because it is
   a claim and not a default.
3. **Every finding dispositioned** - filed, or declined with a reason.

A gate that checks a file exists is satisfied by `touch`, and the one gate worth having is
the one an agent cannot satisfy without doing the work. Existence is not evidence.

## The disposition rule

A finding is dispositioned when it is **either**:

- **filed** as an artefact - the row carries a `BG` / `CR` / `US` / `RFC` id; or
- **declined with a reason** - `declined: already tracked upstream, not ours to fix`.

Both are green. This is deliberate and it is the load-bearing design decision:

> Declining must cost exactly what filing costs, or the gate teaches people to file rubbish
> to go green. If honesty is cheaper than noise, you get honesty. If it is dearer, you get
> noise, and a backlog nobody trusts.

What is refused is **silence** - a finding recorded and left undecided - and a bare
`declined` with no reason, which is silence wearing a decision's clothes.

### A caution on filing

A confident false finding is not free. Under a gate that turns findings into work, a wrong
one manufactures work for everyone downstream, and the cost of filing scales with how much
the process trusts you. Decline generously; file deliberately.

## The question, and why it is in the template

The template asks it outright:

> **Are there any CRs or Bugs you want to raise in this project to address any of the
> issues found?**

The template is what drives behaviour. The field evidence is unambiguous: in a consuming
project, 8 of 9 retros carry a `## Lessons` section - **because the template prompts for
one** - and those same 9 retros reference exactly *one* artefact id between them, because
nothing ever asked what to file. People answer the questions they are asked. Ask the
question, then enforce the answer. A gate on a question nobody was asked is just a wall.

## Extraction: a lesson must leave the retro

`retro.py extract --id RETROxxxx` lifts the `## Lessons` bullets into the project lessons
log. Without it, a lesson lives only in the retro file, and the retro file is read by nobody
after the sprint that wrote it.

Extraction is idempotent by content, so re-running converges rather than duplicating - a
retro can be extracted, edited, and extracted again.

Promote a lesson to the **skill tier** (`lessons add --global`) only once it clearly
generalises beyond this project. The project tier is where a lesson goes first.

## See also

- `help/retro.md` - the command surface
- `help/lessons.md` - the two tiers and the promotion rule
- `reference-sprint.md` - the sprint close that requires the retro
- `reference-agentic-lessons.md` - how lessons accumulate and expire
