# `/sdlc-studio retro`

The retrospective: what the sprint taught, and what you are going to **do** about it.

A retro that nobody reads is a diary. The point of the ceremony is the second half -
turning what you learned into work, and into a lesson the next sprint actually sees.

## Commands

| Command | Does |
| --- | --- |
| `/sdlc-studio retro create` | Write the retro for the batch just closed (`artifact new --type retro`) |
| `/sdlc-studio retro validate` | Content check: sections, a real lesson, every finding dispositioned |
| `/sdlc-studio retro dispose` | List each finding: filed, declined, or still undecided |
| `/sdlc-studio retro extract` | Lift the retro's lessons into the project lessons log |

## What a retro must carry

The close gate reads the content, not the filename. All of these must be there:

- **Delivered** / **Blocked or deferred** - what shipped, what did not.
- **What went well** / **What was hard or what stalled** - the honest account.
- **Lessons** - at least one, in your own words. A `{{placeholder}}` is the template
  talking, not you. If the sprint genuinely taught nothing, say *that*, in a bullet - it
  is a claim worth making explicitly, and it is not the default.
- **Actions raised** - the question that turns the retro into work.

## The question

> **Are there any CRs or Bugs you want to raise in this project to address any of the
> issues found?**

Every finding takes a disposition. There are exactly two green answers:

| Disposition | Means |
| --- | --- |
| `BG0125` / `CR0456` | **Filed.** It became work. |
| `declined: <reason>` | **Declined**, and here is why. |

Both pass. Declining is a first-class answer, not a workaround - so honesty costs exactly
what noise costs, and there is nothing to game by filing rubbish to go green.

What does **not** pass is silence: a finding written down and left to rot. A bare
`declined` with no reason is silence wearing a decision's clothes, and it is refused.

To say "nothing worth raising", say so in a row and give the reason. An empty table is not
an answer to a question.

## Why the gate reads the content

Because a gate that checks a file *exists* is satisfied by `touch`, and the one ceremony
worth enforcing is the one an agent would otherwise skip. Existence is not evidence.

## See also

- `reference-retro.md` - the full workflow and the disposition rules
- `help/lessons.md` - the two lesson tiers, and when to promote one
- `reference-sprint.md` - where the retro sits in the sprint close
