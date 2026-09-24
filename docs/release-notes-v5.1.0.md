# SDLC Studio v5.1

**The release that closes the carried list: every Medium open at v5.0.1 is disposed of or
ruled, and the disclosure page states which bar it is held to.**

v5.0.0 is the substantive release and [its notes](release-notes-v5.0.0.md) remain the place to
read what the tool does. v5.0.1 was a patch for one High-severity defect found hours after the
tag. This release is about the list those two left behind.

## The bar

**Zero open High-severity bugs at the tag, and every Medium disposed of or ruled.** A finding
either reaches a terminal status with its own verifiers passing, or it stays open carrying a
dated ruling that says why it ships. The v5.0.0 bar - zero open High - is unchanged and still
holds; this adds the Medium half, because a list that only ever grows is a disclosure nobody
can act on.

**The bar is the RULING, not the count.** An earlier form of it named a number - fewer than
sixteen disclosed - and that number is the wrong instrument: a count falls by fixing findings
or by not looking for them, and the two are indistinguishable from the outside. RUN-01M20RWX
filed all seven disclosed here, every one from a review or a gate that was doing its job, and
holding a count would have made the run's own thoroughness the reason it could not ship.
What holds instead is that nothing Critical or High is open, and that every Medium on the
page carries a dated ruling naming why it ships rather than blocks (D0186, which
supersedes D0185's count promise; the other two promises D0185 made still bind).

## What you will notice first

Two things that grated on a real backlog are gone.

**`status` was taking about a minute.** Measured on the same machine, over 822 stories and
667 bugs:

| | 5.0.1 | 5.1 |
| --- | ---: | ---: |
| `status` | 59.6s | **0.9s** |
| `status hint` | 59.5s | **0.8s** |

**Fixing one bug no longer invalidates other people's evidence.** A mutation-ledger row was tied
to a whole file, so an edit anywhere in a file another unit had touched staled that unit's rows
as well - on this project, one line moving in a shared file forced seven units' evidence to be
re-measured by hand before a commit could land. A row is now tied to the exact text its mutant
replaced, so an edit elsewhere in the same file leaves it alone.

**The other direction, stated plainly:** the checks that run on a commit take LONGER, not less.
There are 536 more tests than 5.0.1 and the full suite moved from 286s to 331s on the same
machine - about 7% more per test. That is the trade this release makes: more is checked, so more
is caught. What got fast is what you run interactively.

## Upgrading: one breaking change

**`mutation.py register` now requires `--anchor`.** If your project calls it from a script or a
mutation runner, every one of those calls exits 2 until you pass the flag. Give it the exact text
the mutant REPLACED, quoted with enough context to occur exactly once in the target:

```bash
mutation.py register --unit <id> --criterion ACn --target <file> --line <n> \
    --mutant '<the edit>' --anchor '<the text it replaced>' \
    --test '<the command>' --verdict killed
```

That is the whole migration. Rows already in your ledger are untouched and keep being judged by
the file's content hash exactly as before - there is no backfill and nothing to re-measure. A row
gains its anchor the next time somebody actually measures it, and from then on an edit elsewhere
in the same file stops staling it. On this project's own ledger that tax was seven units'
evidence re-measured by hand for one line moving in a shared file.

## Known issues

The open findings are on [the disclosure page](known-issues.md), which is generated from the
bug corpus rather than maintained by hand.

**v5.1.0 discloses 8 open defects: 8 Medium, 0 Low.** Zero Critical, zero High.

## What is in it

Composed at the tag from `changelog.d/` by `release_cut.py changelog-cut`. Until then the
fragments are the record, one per delivered unit.
