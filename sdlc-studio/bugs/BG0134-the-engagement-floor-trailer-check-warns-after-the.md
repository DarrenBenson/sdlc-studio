# BG0134: The engagement-floor trailer check warns after the commit has already landed, so it fails open

> **Status:** Fixed
> **Severity:** Medium
> **Effort:** S
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Affects:** .githooks/commit-msg
> **Verification depth:** functional - the hook was driven the way git drives it (message file as $1) across all four cases: a multi-id subject with no `Refs:` trailer exits 1 and prints pasteable trailer lines; the same subject with trailers exits 0; a single-id subject exits 0; and a `Revert` of a multi-id commit exits 0. 16 behavioural tests, and the load-bearing one fails against the old hook.
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The commit-msg hook prints "commit subject names more than one work-item id but none carry a Refs: trailer ... Without it the engagement floor cannot attribute this commit files per id (a shared commit is skipped), so an understated Affects would go uncaught." It then exits 0 and the commit lands anyway, without the trailer. The message is written as a failure and reads as one, but it is advisory: the very check it describes is skipped for the commit that just triggered it. A guard that names the hole it is leaving, and then leaves it, is worse than no guard - the operator reads the warning as having been enforced. Found by dogfooding: the CR0257/CR0258 commit landed with no trailers and had to be amended by hand.

## Steps to Reproduce

1. Stage a change touching files owned by two or more ids. 2. Commit with a subject naming both ids and no Refs: trailer, e.g. "feat(CR0257, CR0258): ...". 3. Observe the gate reports green, the engagement-floor warning is printed, and git log shows the commit landed with no Refs trailer. 4. The engagement floor has silently skipped it.

## Proposed Fix

Decide which it is and make the behaviour match the words. Either the trailer is required for a multi-id subject - in which case the commit-msg hook must exit non-zero and refuse the commit, as the wording already implies - or it is genuinely optional, in which case the message must not claim a check is being defeated. Preferred: refuse. The hook already knows the ids it wants and can print the exact trailer lines to paste, so the cost of enforcing is one retry, and the cost of not enforcing is an unattributable commit that the floor cannot check.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
