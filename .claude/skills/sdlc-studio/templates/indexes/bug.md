<!--
Template: Bug Index (Streamlined)
File: sdlc-studio/bugs/_index.md
Status values: See reference-outputs.md
Related: help/bug.md, reference-bug.md
-->
# Bug Registry

**Last Updated:** {{last_updated}}

## Summary

| Status | Count |
|--------|-------|
| Open | {{open_count}} |
| In Progress | {{in_progress_count}} |
| Fixed | {{fixed_count}} |
| Verified | {{verified_count}} |
| Closed | {{closed_count}} |
| Won't Fix | {{wont_fix_count}} |
| **Total** | **{{total_count}}** |

## By Severity

| Severity | Open | In Progress | Fixed | Closed |
|----------|------|-------------|-------|--------|
| Critical | {{critical_open}} | {{critical_in_progress}} | {{critical_fixed}} | {{critical_closed}} |
| High | {{high_open}} | {{high_in_progress}} | {{high_fixed}} | {{high_closed}} |
| Medium | {{medium_open}} | {{medium_in_progress}} | {{medium_fixed}} | {{medium_closed}} |
| Low | {{low_open}} | {{low_in_progress}} | {{low_fixed}} | {{low_closed}} |

## All Bugs

| ID | Title | Severity | Priority | Status | Epic | Story | Created |
|----|-------|----------|----------|--------|------|-------|---------|
| [BG{{bug_id}}](BG{{bug_id}}-{{bug_slug}}.md) | {{title}} | {{severity}} | {{priority}} | {{status}} | EP{{epic_id}} | US{{story_id}} | {{created_date}} |

## Notes

- Bugs are numbered globally (BG0001, BG0002, etc.)
- Severity: Critical > High > Medium > Low
- Critical bugs should be fixed within 24 hours
