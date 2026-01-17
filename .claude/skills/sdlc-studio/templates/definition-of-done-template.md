# Definition of Done

This document defines the standard criteria that must be met before any user story can be considered complete. Individual stories may have additional criteria, but these are the baseline requirements.

## Code Quality

- [ ] Code is complete and implements all acceptance criteria
- [ ] Code follows project coding standards and conventions
- [ ] Code has been peer reviewed and approved
- [ ] No compiler warnings or linter errors
- [ ] No TODO/FIXME comments left in committed code (unless tracked as separate stories)

## Testing

- [ ] Unit tests written and passing
- [ ] Integration tests written and passing (where applicable)
- [ ] Manual testing completed by developer
- [ ] Edge cases and error conditions tested
- [ ] Test coverage meets project threshold

## Documentation

- [ ] Code is self-documenting with clear naming
- [ ] Complex logic has explanatory comments
- [ ] API documentation updated (if applicable)
- [ ] User-facing documentation updated (if applicable)

## Deployment

- [ ] Code merged to main branch
- [ ] CI/CD pipeline passes
- [ ] Feature deployable to staging environment
- [ ] No breaking changes to existing functionality

## Acceptance

- [ ] Acceptance criteria verified by developer
- [ ] Demo given to Product Owner (if required)
- [ ] Product Owner has accepted the story

---

## Notes

- Stories should not be marked "Done" until ALL applicable items are checked
- If an item is not applicable, add a note explaining why (e.g., "N/A - no API changes")
- Blocked stories should remain "In Progress" with blocker documented
- If DoD cannot be fully met, escalate to Product Owner for discussion
