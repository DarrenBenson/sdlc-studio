---

id: LL0022
title: A guard that branches on invocation mode must be tested in every invocation mode
tags: [testing, false-green, shell, bug-class, silent-failure]
added: 2026-07-14
origin: BG0122 - install.sh no-op when piped to bash
---

**Lesson.** A source-vs-execute guard (`[[ "${BASH_SOURCE[0]}" == "${0}" ]]`) decides behaviour from HOW the script was invoked. It therefore has as many code paths as there are invocation modes - piped from stdin, executed as a file, sourced - and a suite that exercises one of them proves nothing about the others.

The installer's suite only ever SOURCED the script, which was the one mode that was never broken. Piped (`curl | bash`) bash reads from stdin, so ${BASH_SOURCE[0]} is unset while $0 is 'bash'; the guard failed, main never ran, and the script exited 0 having done nothing - the exact invocation the README advertised.

Two rules follow:

1. Enumerate the modes the guard discriminates and test EACH. If a conditional's whole job is to distinguish contexts, testing one context tests nothing.
2. Assert on OUTPUT, not the exit code, whenever the failure mode is 'did not run'. The broken installer exited 0. An exit-code assertion passes against the bug and gives false comfort. Probe with something only the guarded code path can produce, and check the observable effect.

A corollary for the probe itself: verify the probe FAILS against the pre-fix code before trusting it. A test that cannot detect the bug it was written for is worse than no test, because it looks like coverage.

Related: [[LL0008]] (fail loud, never report success not achieved), [[LL0009]] (silent misleading failure), [[LL0020]] (a fixture that supplies the thing under test proves nothing).

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
