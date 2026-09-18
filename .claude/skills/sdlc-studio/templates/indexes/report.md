<!--
Template: Report Index
File: sdlc-studio/reports/_index.md
Status values: N/A (derived records, outside the status machinery)
Related: help/sprint.md, reference-sprint.md
-->
# Report Index

**Last Updated:** {{last_updated}}

Sprint reports of record, one per run that reached a close. Each is a JSON record derived from
the run's own artefacts with a Markdown twin rendered from it, and a fingerprint over the
ordered figure set - so a reader can tell whether a signed page still describes the tree.
Filed by `sprint close` and sealed by `sprint sign`; never hand-authored, and re-derived rather
than edited when a figure moves.

| ID | Run | Generated | Fingerprint | Signed |
| --- | --- | --- | --- | --- |
| [RPT{{report_id}}](RPT{{report_id}}-{{report_slug}}.md) | {{run_id}} | {{generated_at}} | {{fingerprint}} | {{signed_by}} |
