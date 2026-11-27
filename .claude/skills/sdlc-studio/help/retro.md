# `/sdlc-studio retro`

The retrospective: what the sprint taught, and what you are going to **do** about it. It is the
[learn step](../reference-sprint.md#the-loop) of the sprint loop.

A retro that nobody reads is a diary. The point of the ceremony is the second half -
turning what you learned into a lesson the next sprint actually sees.

## Commands

| Command | Does |
| --- | --- |
| `/sdlc-studio retro create` | Write the retro for the batch just closed (`artifact new --type retro`); `sprint close` with no `--retro` scaffolds it for you |
| `/sdlc-studio retro validate` | Content check: the three lines, the Try limit, no placeholder left, every class tag known, and the Batch field omits no unit of the batch of the run its `Run` field names (read from the live run state, else the run archive) |
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

## What a second review seat caught

A high-class unit (its `Risk-class` tag, or a bug's Affects read through `risk.components`)
takes a second independent review seat, briefed with `critic.py brief`. The retro's accuracy
block reads the verdict ledger and names, per second seat, the units where it rejected or
raised issues after the first seat approved. It says in one line when a high-class unit had
no second-seat verdict, or when a seat caught nothing; a seat that keeps catching nothing is
yours to drop, and nothing drops it for you.

## Each seat's own record

`retro.py seats --id RETROxxxx [--format json]` scores each seat on the ledger rows that name it
as `<holder> (<role>)`: its APPROVE and REJECT counts and the rounds each unit took to
converge as a reviewer, and as the author the units it built, their rounds and each round's
blocking findings. A blocking finding citing a `file:line` no earlier round cited is charged
only to a seat whose earlier verdict on the unit approved, saying whether the file changed
between the two rows' dates or that it cannot be told. A superseded row is listed as recorded
in error with its reason, and the rows naming no seat are counted and named, never guessed.

It also charges each later bug to the approval that missed it. A bug counts in the retro whose
window holds its `Created` day. One carrying `Escaped-via` is charged to that unit; any other
only when it cites the unit, shares an `Affects` file with it and cites three ids or fewer. The
charge goes to every seat whose latest verdict on the unit approved, in any run, each miss with
its basis. See [seat evidence](../reference-retro.md#seat-evidence-each-seat-on-its-own-record).

It also states the release change failure rate, `escape.failure_rate`'s figure over the 90 days
ending on the retro's Date, or on today when the retro carries no Date it can read, which the line
says, with the 14-day settling period: the rate, the releases pending, each release counted with
the incident issues and escaped bugs that failed it, and the release record file it was read from.
`--format json` carries the function's figure as `release_cfr`, with `source` naming the record
file beside it. With no release recorded in the window, every one pending or no incident recorded
it reads not measured with the command's reason, and a record file the function cannot read reads
not measured naming the line, never a refusal.

## Persona learnings, listed at the close and struck at the signature

The close's `persona-memory` step writes a `## Persona learnings` block on the retro: every
approved learning not yet live, with its seat, its approver and the adverse items it addresses.
It names each seat whose record holds adverse evidence and no learning listed, and never blocks
the close ([what goes live when you sign](../reference-retro.md#persona-learnings-what-goes-live-when-you-sign)).
A listed learning reaches a brief only once the run is signed, and
`sprint.py sign --strike M-NNNN --strike-reason "..."` strikes one as it seals the run; a strike
with no reason, or naming a learning this run's close did not list, is refused before anything
is sealed ([listed and struck](../reference-persona-learning.md#listed-and-struck)).

## An escaped bug

`escape.py trace --bug BGxxxx` reads an escaped bug's `Shipped-in` release and proposes the
units that release shipped which share a file with the fix, each with its recorded verdict,
round and seat, and writes nothing. `--confirm <unit>` records one as the bug's `Escaped-via`,
and `retro.py seats` then charges the bug to that unit's approving seats.
`escape.py to-class --bug BGxxxx --class NAME --rule "..." --behaviour "..."` turns the
confirmed escape's written Root Cause into a failure class in `sdlc-studio/lessons.jsonl`,
carrying the bug's Affects paths, injected at build and review.
See [`escape.py`](../reference-scripts-review.md#escapepy) and `help/bug.md` for recording an
escaped bug.

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
