---

id: LL0014
title: A mocked boundary tests the code on your side of it, and nothing else
tags: [testing, mocking, coverage, false-green]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** Every test of a new GitHub fetcher patched fetch_github_tree with an AsyncMock and hand-built its return value. So 148 lines that parse the API's real payload were never executed. An independent critic deleted the 'truncated' flag - the sole defence against mass deletion on a large repo - and the entire suite still passed.

Mocking a boundary is legitimate for testing YOUR side of it. It says nothing whatever about whether you read the OTHER side's payload correctly. Any module that parses an external response needs at least one test that drives a real payload through the real function.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
