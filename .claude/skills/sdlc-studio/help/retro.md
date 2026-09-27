# `/sdlc-studio retro`

The retrospective: what the sprint taught, and what you are going to **do** about it. It is the
[learn step](../reference-sprint.md#the-loop) of the sprint loop.

A retro that nobody reads is a diary. The point of the ceremony is the second half -
turning what you learned into a lesson the next sprint actually sees.

## Commands

| Command | Does |
| --- | --- |
| `/sdlc-studio retro create` | Write the retro for the batch just closed (`artifact new --type retro`); `sprint close` with no `--retro` scaffolds it for you |
| `/sdlc-studio retro validate` | Content check: the three lines, the Try limit, no placeholder left, every class tag known |
| `/sdlc-studio retro extract` | Turn each Try item into a lesson (the close runs this) |
| `/sdlc-studio retro dispose` | An older retro's findings: filed, fixed, declined, or still undecided |

## The shape: Keep, Stop, Try

Three lines, written at the close. The estimates, delivery against plan and known issues are on
the sprint report, so the retro does not repeat them.

```markdown
## Keep

- One reviewer per unit caught every regression this run; keep briefing with `critic.py brief`.

## Stop

- Planning units with no `Affects:` cost two re-plans; stop admitting them.

## Try

- [LC-003] US0142 shipped a criterion its own test could not fail; name the mutant first.
- [new: stale fixture] A fixture copied from another unit hides a changed schema. Rebuild it from the template.
```

- **Keep** - what worked and should carry on.
- **Stop** - what cost more than it returned.
- **Try** - at most 3 items: the changes for the next run. A list that can grow is one nobody
  acts on, so `retro validate` refuses one more; keep the ones that matter most.

Every line must be this run's own: an empty section or a `{{placeholder}}` left from the template
is refused.

## A Try item becomes a lesson

`retro extract`, run by the close, lifts each Try item into the lessons stores. Tag it with its
failure class and a repeat is counted rather than written again:

| Tag | Does |
| --- | --- |
| `[LC-003] what happened this time` | adds a hit to class LC-003 in `sdlc-studio/lessons.jsonl` |
| `[new: <class name>] Rule. What to do differently.` | records a new class, injected at plan, build and review |
| `[new: <class name> \| build, review] ...` | a new class injected only at the named phases |

`lessons.py classes` lists every code, its name, state and hit count. A class that keeps
recurring files a CR to fix its failing path or retire it; a quiet one retires. An untagged item
goes to the project lessons log. An item that looks like a tag but does not parse (`(LC-003)`,
`[LC 3]`) is refused, never filed as prose: its author meant it to count.

## Retros written before Keep, Stop and Try

An older retro is still validated against the shape it was written in: Delivered, What went
well, What was hard / what stalled, Lessons and Actions raised, with every finding in Actions
raised dispositioned - filed (`BG0125`), fixed in-sprint (`fixed-in: <sha or unit>`) or
`declined: <reason>`. `retro dispose` lists those findings. A bare `declined` with no reason is
refused.

## See also

- `reference-retro.md` - the full workflow
- `help/lessons.md` - the lesson tiers and the failure classes
- [`reference-sprint.md#the-loop`](../reference-sprint.md#the-loop) - where the retro sits in the sprint
