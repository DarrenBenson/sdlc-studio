# Delivery mode: sequential or parallel

When a sprint run begins, the batch is built one of two ways:

- **Sequential** - the units are built in order, in the working tree. Always available.
- **Parallel** - each file-disjoint group is built by its own agent in an isolated git
  worktree, then merged. Available **only** when the batch genuinely decomposes.

`sprint plan` computes which modes are on the table and states the reason, so the operator
picks from real options rather than a preference. The offer is deterministic: the same batch
and repo state always yield the same modes and the same groups.

## When parallel is offered

Parallel is offered when the batch partitions into **two or more file-disjoint groups**. Two
units couple - and so land in the same group, forcing sequence - when they share any file.
A group of two or more units that all touch a common file cannot be split; two agents editing
the same file in separate worktrees produce a merge conflict.

Parallel is **withheld**, and the batch is delivered sequentially, when:

- the batch holds a single unit (nothing to parallelise);
- every unit couples to another, so the whole batch is one group; or
- any unit declares no `Affects` - its blast radius is unknown, and delivering it beside
  other units in separate worktrees risks an undeclared overlap.

## Test files count as coupling

The files a unit touches are its declared `Affects` **and** the files its `Verify:` lines
name. A shared test module couples two units exactly as a shared source module does: a real
parallel build once collided over a test file neither unit had declared, because two stories
extended the same test battery. So the disjointness check reads both surfaces, and a
test-file-only overlap denies the parallel offer just as a source overlap does.

## What the plan states

For a parallelisable batch the plan names the mode is the operator's to pick and lists the
worktree groups a parallel build would fan out to. For a sequential-only batch it names the
sequential mode and why parallel was withheld. Either way the reason is on the plan, so the
choice - and the road not taken - is recorded.

## Building in parallel

A parallel build gives each group its own agent and worktree, so the groups never touch each
other's files. On merge, the groups are file-disjoint by construction, so the merges combine
cleanly. The merge step still counts test files as coupling: a group boundary drawn without
them would let two groups share a test module and conflict at merge, which is the failure the
coupling rule exists to prevent.

## Worktree isolation is not workspace isolation

A parallel build gives each agent its own git worktree, so the disjointness check above is about
files IN THE REPOSITORY. Two things sit outside that check and bite anyway.

**A shared temp directory.** Agents commonly write temporary files - a commit message, a
fields-file, a worklist - and if they share one scratchpad path, one agent's file is overwritten
by another between write and use. This has happened: a commit landed carrying a different agent's
subject, because both wrote the same message path. Namespace any temp path per agent or per run,
or keep it inside the agent's own worktree. A worktree isolates the tree; it does not isolate
`/tmp`.

**The build tooling itself.** A unit that changes the pre-commit hook, the gate, or a guard the
commit path runs is coupled to every other unit in the batch, whatever its `Affects` says - every
parallel agent commits through it. `Affects` answers "what does this edit", which is the right
question for merge conflicts and the wrong one for shared machinery. Deliver such a unit on its
own, or serially.

Neither failure produces a merge conflict, which is the only outcome the file-disjointness check
was built to predict. That is why they are stated here rather than left to it.

## See also

- [reference-sprint.md](reference-sprint.md) - the sprint engine and `sprint plan`
- [reference-outputs.md](reference-outputs.md) - the completion cascades a build closes
