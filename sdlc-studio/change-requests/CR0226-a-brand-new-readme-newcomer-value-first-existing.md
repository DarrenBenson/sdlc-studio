# CR-0226: a brand-new README: newcomer value first, existing users get their own page

> **Status:** In Progress
> **Depends on:** CR0222
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Operator-directed for the v4 GA. The README is rewritten from scratch for the NEWCOMER: what they get (a full high-performing squad grown from their project), why it is different (the mill, not the engine - the organisation around the code), and the fastest honest path to feeling it (quick start, ten-minute taster, the meet-your-team moment). Value before mechanism; plain language; every claim verifiable against shipped behaviour. Existing users move to their own page (docs/existing-users.md or similar): what v4 changes for a running project, the three-answer numbering question, the upgrade walk, breaking-change honesty, and the forward-port/testing flow. The current README's mixed audience (newcomer pitch + upgrade nuance + agent-evaluator notes interleaved) serves nobody first.

## Acceptance Criteria

- [ ] README rewritten newcomer-first: value proposition, the philosophy frame in one breath (cockpit/mill, human-in-the-lead), quick start that works verbatim, the meet-your-team moment shown, evidence-honest claims only, no competitor named
- [ ] docs/existing-users.md (linked prominently from the README) carries everything an existing project needs: what v4 changes, the explicit numbering question with its three answers, upgrade steps, and the dev/testing flow
- [ ] Lena (Product seat) reviews the new README claim-by-claim as the adopting reader before it merges; markdownlint + links + doc gates green

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
