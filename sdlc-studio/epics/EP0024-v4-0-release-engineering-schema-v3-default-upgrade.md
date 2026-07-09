# EP0024: v4.0 release engineering: schema-v3 default, upgrade walk, majors checklist

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new

## Summary

The v4.0 release-engineering unit (CR0198): make `schema_version: 3` the default for new
projects while leaving existing/unpinned projects on 2, present the v2 to v3 migration as a
directed, rehearsed upgrade walk, add a majors-only release-gate section, and home the version
strings and CHANGELOG at `4.0.0-rc.1` with the freeze banners removed. The actual rc-tag cut,
freeze lift, and push stay an explicit operator action gated on the US0109 checklist reading
green. Goal: the tree is rc-ready and the tag decision is a checklist read, not a judgement call.

## Story Breakdown

- [x] [US0105: init defaults schema_version 3 for new projects; code default stays 2 (existing projects untouched)](../stories/US0105-init-defaults-schema-version-3-for-new-projects.md)
- [x] [US0106: v3 to v4 upgrade walk rehearsed on two consuming projects with findings filed](../stories/US0106-v3-to-v4-upgrade-walk-rehearsed-on-two.md)
- [x] [US0107: Majors-only release-gate checklist section](../stories/US0107-majors-only-release-gate-checklist-section.md)
- [x] [US0108: Version and CHANGELOG conversion to 4.0.0-rc.1 and dormant-schema banner removal](../stories/US0108-version-and-changelog-conversion-to-4-0-0.md)
- [ ] [US0109: rc-tag readiness checklist enumerated so the tag decision is a checklist read](../stories/US0109-rc-tag-readiness-checklist-enumerated-so-the-tag.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
