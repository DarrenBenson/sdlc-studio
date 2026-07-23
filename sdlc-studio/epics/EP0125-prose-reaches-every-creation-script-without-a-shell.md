# EP0125: Prose reaches every creation script without a shell

> **Status:** Draft
> **Derived Point Total:** 10
> **Parent:** CR0351
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0351. Delivers the work CR0351 requested.

## Story Breakdown

- [ ] [US0361: a shared fields-file and stdin helper in sdlc_md.py, adopted across the remaining prose scripts](../stories/US0361-a-shared-fields-file-and-stdin-helper-in.md)
- [ ] [US0362: a command-substitution fingerprint detector with a recorded miss rate](../stories/US0362-a-command-substitution-fingerprint-detector-with-a-recorded.md)
- [ ] [US0363: document the safe form in reference-scripts.md and agent-instructions.md](../stories/US0363-document-the-safe-form-in-reference-scripts-md.md)

## Acceptance Criteria (Epic Level)

- [ ] a shared helper in `lib/sdlc_md.py` gives every long field a form that does not transit
- [ ] all 13 scripts listed in Affects adopt that helper for their long fields; the existing
- [ ] a shared detector refuses text carrying the fingerprints of command substitution
- [ ] the detector's limit is recorded, not implied: measured against the four real
- [ ] `reference-scripts.md` documents the safe form as the default for prose, and

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
