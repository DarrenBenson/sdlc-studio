---

id: LL0024
title: A hazard found by calling a private helper directly may already be guarded at the only call site that matters
tags: [testing, false-positive, review, tooling, bug-class, humility]
added: 2026-07-14
origin: BG0124 - a High bug filed against a defence that already existed
---

**Lesson.** An agent reviewing the artefact tooling found that `_md_safe()` backtick-wraps
snake_case identifiers, reasoned that a Verify line run under `shell=True` would then suffer
command substitution, demonstrated exactly that by calling `_md_safe()` **directly** on a
verify-shaped string, and filed a High bug about false-green acceptance criteria.

The bug was not real. `artifact.py` routes `--verify` through a separate function that passes the
command through verbatim and never markdown-safes it - and that function's docstring already spelled
out both failure modes, concluding *"verbatim is the only form that is both correct and safe."* The
hazard was genuine. The exposure was zero. The defence was already there, deliberate, and
documented.

The reasoning was sound at every step and the conclusion was still false, because every step
happened on the wrong side of the boundary. Calling the private helper proved what the helper does.
It proved nothing about what the **pipeline** does, and the pipeline is the only thing that ships.

**The rules:**

1. **Reproduce through the public path, or you have not reproduced it.** Drive the actual command,
   the actual entry point, the artefact the user would really get. If the repro invokes a private
   function directly, it is a hypothesis, not a finding.

2. **Before filing, look for the guard.** Ask "would anyone sensible have defended this already?"
   and go and look. Read the call site, not just the helper. Here the answer was sitting in a
   docstring at the call site, which is exactly where a competent author would have put it.

3. **A false finding is not free.** This one cost a High bug, a severity correction, a lesson, and
   three commits - all of it noise in the ledger, all of it needing withdrawal. Under a disposition
   gate that turns findings into work, a confident false finding manufactures work for everyone
   downstream. The cost of filing scales with how much the process trusts you.

4. **Suspicion of your own certainty rises with the elegance of the theory.** The failure mode here
   was seductive precisely because it was a *good* piece of reasoning about a *real* hazard. The
   more satisfying the bug, the harder you should look for the reason it cannot happen.

This is [[LL0014]] and [[LL0017]] turned on the reviewer instead of the tested code: a boundary you
mock, or step around, tests the code on your side of it and nothing else. And it is the mirror of
[[LL0010]] - validate a defence against the bug it defends against - because the defence existed and
was never checked.

**Postscript.** The AC corruption that started the hunt was self-inflicted: a shell command had been
written into `--ac` prose, where commands do not belong, instead of into `--verify`. The tool then
correctly normalised the prose it was given. The tool was right and the caller was wrong, which is
the ordinary case and the one an agent is least inclined to consider.
