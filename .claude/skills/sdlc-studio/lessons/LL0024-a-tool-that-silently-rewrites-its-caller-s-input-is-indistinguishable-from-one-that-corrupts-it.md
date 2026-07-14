---

id: LL0024
title: A tool that silently rewrites its caller's input is indistinguishable from one that corrupts it
tags: [tooling, silent-failure, false-green, bug-class, determinism, dx]
added: 2026-07-14
origin: BG0124 - the artefact filer backticked executable Verify lines
---

**Lesson.** The artefact filer ran a markdown-safety normaliser over every field it was given, including the AC's executable Verify command. It backtick-wrapped snake_case identifiers to dodge an emphasis-lint rule - correct for prose, catastrophic for a command, because the verifier runs Verify lines under a shell where backticks are command substitution. A path became a command; the command searched the wrong target; the AC returned 0. A false GREEN on the gate that decides Done.

The corruption was not the deepest problem. The SILENCE was. The caller passed one string and a different string was stored, and nothing in the output said so. It was invisible at the only moment anyone could have caught it, and it was found only because someone happened to read the stored file and notice a backtick they had not typed.

Three rules:

1. **Never normalise an executable.** If a field is going to be executed, evaluated or parsed by a machine downstream, it is not prose and no prettifier may touch it. Split the artefact at that boundary and pass the executable half through byte-for-byte.

2. **Announce every rewrite.** A tool that transforms caller input must report what it changed. 'normalised: 3 tokens backticked in Summary' costs one line and makes the transform reviewable. Silent normalisation and silent corruption are the same event from the caller's side.

3. **Document which tools mutate input.** A catalogue that says what a script DOES, but not that it rewrites what you hand it, is a trap for every agent after this one.

The tell: a helper named for a display concern (`_md_safe`, `prettify`, `sanitise`) applied to a
field that a machine will later execute. Look for the boundary; it is almost never where the
formatter thinks it is.

**Postscript, recorded because it is the best evidence in this file.** Writing this lesson, the
author passed the body to the tool inside a double-quoted shell string. The shell
command-substituted the three backticked tokens above, ran them, and stored their empty output -
so the sentence naming the tell arrived with the tell deleted from it. The bug bit the person
documenting the bug, in the act of documenting it, through the same mechanism. Backticks in a
string bound for a shell are not decoration, and knowing that does not save you - only not putting
them there does.

Related: [[LL0008]] (report no success you did not achieve), [[LL0009]] (silent misleading failure outranks loud), [[LL0016]] (two code paths building the same artefact must agree on what it MEANS).

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
