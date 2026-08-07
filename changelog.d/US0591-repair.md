<!-- section: Fixed -->
- **An expired checklist row is reported by the CLOSE, not only by the rendered page.** The
  close and its dry-run pre-flight both built their output from `outstanding` alone, so four
  rows that were NAMED at the base ref were named nowhere afterwards - the close's own report
  lost information to the change that was meant to improve it, which is the vanish-instead-of-
  report failure the criterion forbids. Both surfaces now name them with the command that should
  have enforced them, and the pre-flight marks them non-blocking so reported-not-held means the
  same thing everywhere rather than only where it was first implemented.
