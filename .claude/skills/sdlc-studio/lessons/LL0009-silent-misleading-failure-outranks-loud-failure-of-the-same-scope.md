---
id: LL0009
title: Silent misleading failure outranks loud failure of the same scope
tags: [severity, triage, silent-failure, review, bug-class]
added: 2026-06-27
origin: a consuming repo BG0026/BG0028/BG0029
---

**Lesson.** **Lesson.** A failure that misleads the caller into believing it succeeded ranks categorically above a loud failure of the same functional scope; default it to P0/P1. The triage question is "what does the user believe happened?" - if the belief is wrong, escalate.

**Why / what it cost.** a consuming repo BG0026 was Critical because session state recorded delivery as successful after the channel callback dropped, so the agent gave confident "scroll up, it's there" replies. A loud variant (error thrown, user sees "something failed") would have ranked P2. Same scope, two severities. BG0028/0029 were the same shape: server log success, counter success, session delivered, user sees nothing.

**How to apply.** Grade silent-misleading failures up by default. After any change to a delivery/result path, grep every early `return` in the call chain and prove it fires the result callback, or log why it does not - make it a reviewer checklist item. This is the runtime sibling of [[LL0008]] (a tool must fail loud): there it is the tool lying about its own success, here it is the system lying to its user.

**Generalises to.** Any path that reports/records success independently of the side effect actually landing: message delivery, writes, notifications, payments, job completion.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
