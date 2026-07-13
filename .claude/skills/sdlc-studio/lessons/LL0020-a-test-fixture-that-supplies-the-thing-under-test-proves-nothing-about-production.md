---

id: LL0020
title: A test fixture that supplies the thing under test proves nothing about production
tags: [testing, fixtures, observability, false-green, bug-class]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** An application never called logging.basicConfig. Uvicorn configures only its own loggers, so the root logger had no handler and EVERY application log line was silently discarded in production - from the first commit onwards.

824 tests passed while this was true. Every logging assertion in the suite used pytest's caplog, and caplog ATTACHES ITS OWN HANDLER. The fixture supplied the exact thing that was missing. The tests were testing the fixture.

The damage was not cosmetic: the component with the worst failure mode (an unattended background loop documented as 'it stops quietly') had its only observability routed into a void, and a security warning about unencrypted credentials at rest had never once been printed.

Ask of any fixture: does it PROVIDE something production must provide for itself? caplog provides a handler. A test client provides an app instance. An in-memory DB provides a schema. Wherever the answer is yes, at least one test must run WITHOUT the fixture and assert the real thing works - capture real stdout, boot the real app, run the real migration.

Corollary: this bug was found by opening 'docker logs' on the running container, not by any test. Deploy verification is not ceremony.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
