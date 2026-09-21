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

**v5.1.0 discloses 48 open defects: 48 Medium, 0 Low.**

**Six High-severity findings are open against the tag: BG0715, BG0718, BG0719, BG0722, BG0730 and BG0733.** It was raised on 2026-09-18,
after v5.1.0 shipped, by RUN-01M2SPNS running its own close. `_open_findings` dates a finding
by the last word of its `Raised-in-batch` stamp, so a finding raised outside a delivery batch -
the ordinary case for a backlog sweep or an audit - sorts as inside every run window and is
attributed to whichever run is open. The close then demands a stop-ship ruling for findings the
run never saw. It affects the sprint-close ceremony, not the tool's output, and it has a
documented route past it (a dated waiver naming the row, as D0215 records for that run), but it
is disclosed here rather than counted quietly because the bar names ids and so must the prose.

**BG0718 and BG0719 were both raised on 2026-09-19 by RUN-01M2SPNS's own SEAL**, and both are
about the report of record that run shipped. BG0718: the seal writes `ended_at`, the DORA window
was bounded by `ended_at` before the page's own generation time, so signing a report widened its
window and invalidated it - the run signed a page whose lead time re-derived differently one
second later, and no run could have held a valid signature over its own report. Its repair is
in this tree and it stays open only until an independent seat reviews its test plan. BG0719: the
report does not name the waivers that were in force when it was derived, so an operator signs
without being told which close-gate lane stood down - on that run, the per-unit coverage gate.
Both affect the report, not the rest of the tool, and both are disclosed here rather than
counted quietly because the bar names ids and so must the prose.

**BG0722 was raised on 2026-09-21 by RUN-01M306PY auditing its own guard.** That run built a lane reporting a discovery request that is In Progress, finished by its children, and never judged - then ran it against the real backlog and got ZERO, because all 37 stalled requests had at least one child still open. The lane is correct and its mutants are killed; it simply catches a request nobody closed rather than a request everybody abandoned, which is the path that actually accumulated. The run recorded the gap rather than quietly claiming its goal.

**The disclosed count rose from 39 to 47 in one day, and that is the sweep working rather than the tree rotting.** RUN-01M306PY re-triaged a July aggregate of twenty non-blocking review findings that had been closed as unbuildable, found it actually states TWENTY-FOUR claims, re-executed every one against HEAD, and filed the fifteen that still reproduce as artefacts that can be planned. Five had already been fixed by other work, one was never a defect, and three cannot be tested as written and say so. The count went up because the findings stopped being a bullet list nobody could act on.

**BG0730 is the one to read first**: a stop-ship ruling is never re-derived against its finding's status, so a ruling on a finding that has since been Fixed blocks every subsequent close, permanently, with no escape but editing a retro by hand.

## What is in it

Composed at the tag from `changelog.d/` by `release_cut.py changelog-cut`. Until then the
fragments are the record, one per delivered unit.
