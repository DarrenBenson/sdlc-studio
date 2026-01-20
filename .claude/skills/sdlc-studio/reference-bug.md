# SDLC Studio Reference - Bug

Detailed workflows for Bug tracking and management.

<!-- Load when: creating, managing, or fixing Bugs -->

---

# Bug Tracking Workflows

## /sdlc-studio bug create - Step by Step

1. **Check Prerequisites**
   - Create sdlc-studio/bugs/ if needed
   - Scan for existing bugs to determine next ID

2. **Gather Bug Details**
   Use AskUserQuestion to collect:
   - Title (short description)
   - Summary (detailed description of the issue)
   - Reproduction steps (numbered list)
   - Expected behaviour
   - Actual behaviour

3. **Determine Severity and Priority**
   Ask user or infer from description:
   - **Severity:** Critical, High, Medium, Low
   - **Priority:** P1, P2, P3, P4

4. **Link to Affected Areas**
   - Auto-detect affected stories/epics from description
   - Ask user to confirm or specify component

5. **Capture Environment**
   - Version, platform, browser if applicable
   - Any other relevant environment details

6. **Write Bug Report**
   - Use `templates/bug-template.md`
   - Assign ID: BG{NNNN}
   - Create slug (kebab-case, max 50 chars)
   - Write to `sdlc-studio/bugs/BG{NNNN}-{slug}.md`

7. **Update Index**
   - Create/update `sdlc-studio/bugs/_index.md`
   - Update counts by status and severity

8. **Update Linked Story (Optional)**
   - If linked to a story, add "Known Issues" section
   - Reference bug ID and summary

9. **Report**
   - Bug ID and file path
   - Linked stories/epics
   - Suggested next action

---

## /sdlc-studio bug list - Step by Step

1. **Parse Filters**
   - `--status`: open, in_progress, fixed, verified, closed, wont_fix
   - `--severity`: critical, high, medium, low
   - `--priority`: P1, P2, P3, P4
   - `--epic`: EP{NNNN}
   - `--story`: US{NNNN}
   - `--assignee`: name

2. **Read Bug Files**
   - Load all from sdlc-studio/bugs/
   - Parse metadata from each file

3. **Apply Filters**
   - Match against specified criteria
   - Default: show all open bugs

4. **Sort Results**
   - By severity (Critical first)
   - Then by priority (P1 first)
   - Then by age (oldest first)

5. **Display Output**
   ```
   ## Open Bugs (12)

   | ID | Title | Severity | Priority | Age |
   |----|-------|----------|----------|-----|
   | BG0003 | Player falls through floor | Critical | P1 | 2d |
   ```

---

## /sdlc-studio bug fix --bug BG{NNNN} - Step by Step

1. **Read Bug Details**
   - Load bug file
   - Extract reproduction steps, affected areas
   - Verify status is Open or In Progress

2. **Update Status**
   - Change status: Open → In Progress
   - Update "Updated" date
   - Add revision history entry

3. **Analyse Root Cause**
   Use Task tool with Explore agent:
   ```
   For bug [BG{NNNN}]: [Title]
   Reproduction: [steps]
   Affected: [component/story]

   1. Search for relevant code files
   2. Identify likely cause of behaviour
   3. Suggest fix approach
   4. Identify tests to add
   ```

4. **Present Fix Plan**
   - Root cause analysis
   - Files to modify
   - Suggested approach
   - Tests to add

5. **Prompt for Regression Test**
   - Suggest test case based on reproduction steps
   - Link to relevant test spec

6. **Mark Fix Complete (--complete)**
   When user runs with `--complete`:
   - Update status: In Progress → Fixed
   - Fill in "Root Cause Analysis" section
   - Fill in "Fix Description" section
   - Add files modified to table
   - Add tests added to table
   - Update linked story with fix reference
   - Update revision history

---

## /sdlc-studio bug verify --bug BG{NNNN} - Step by Step

Quick happy path: verify fix and close in one step.

1. **Check Prerequisites**
   - Verify bug status is "Fixed"
   - If not, report error and suggest `bug fix --complete`

2. **Read Bug and Fix Details**
   - Load fix description
   - Identify tests added
   - Identify reproduction steps

3. **Run Associated Tests**
   - Execute tests listed in "Tests Added" section
   - Report pass/fail status
   - If tests fail, abort and report

4. **Verification Checklist**
   Guide user through:
   - [ ] Fix verified in development
   - [ ] Regression tests pass
   - [ ] No side effects observed
   - [ ] Documentation updated (if applicable)

5. **Update Bug Report**
   - Check off verification items
   - Fill in verifier and verification date
   - Update status: Fixed → Closed (verified)
   - Record close reason as "Verified"
   - Add revision history entry

6. **Update Index**
   - Move from "Open Bugs" to closed section
   - Update counts

7. **Update Linked Story**
   - If bug was linked, update story's "Known Issues"
   - Mark as resolved with bug reference

8. **Report**
   - Verification status
   - Test results
   - Bug closed

---

## /sdlc-studio bug close --bug BG{NNNN} - Step by Step

Close a bug with reason selection.

1. **Check Prerequisites**
   - Verify bug status is "Fixed" or "Open"
   - If already closed, report error

2. **Prompt for Close Reason**
   Use AskUserQuestion:
   - **Verified** - Fix confirmed working (same as `bug verify`)
   - **Rejected** - Not a valid bug
   - **Won't Fix** - Valid bug but intentionally not addressing

3. **If Verified**
   - Run verification checklist (same as `bug verify`)
   - Only close if tests pass

4. **Update Bug Report**
   - Update status → Closed
   - Record close reason
   - Update "Updated" date
   - Add revision history entry

5. **Update Index**
   - Move from "Open Bugs" to appropriate closed section
   - Update counts

6. **Update Linked Story**
   - If bug was linked, update story's "Known Issues"
   - Mark as resolved with bug reference

7. **Report**
   - Bug closed with reason
   - Total time from report to close

**Tip:** Use `bug verify` for the common case of closing a verified fix.

---

## /sdlc-studio bug reopen --bug BG{NNNN} - Step by Step

1. **Check Prerequisites**
   - Verify bug status is "Closed" or "Won't Fix"
   - If not, report error

2. **Gather Reopen Reason**
   Use AskUserQuestion:
   - Why is this being reopened?
   - Is this a regression?
   - New reproduction steps?

3. **Update Bug Report**
   - Update status: Closed → Open
   - Add "Reopen Note" to Notes section
   - Link to related test failure if applicable
   - Add revision history entry

4. **Update Index**
   - Move back to "Open Bugs" section
   - Update counts

5. **Update Linked Story**
   - Re-add to story's "Known Issues"

6. **Report**
   - Bug reopened
   - Previous fix details for reference

---

# Bug Section Reference

Detailed guidance for completing each section of the Bug template.

---

## Summary and Metadata

### Status Values
- **Open**: Bug reported, awaiting fix
- **In Progress**: Fix being developed
- **Fixed**: Fix complete, awaiting verification
- **Closed**: Bug resolved (includes close reason: Verified, Rejected, Won't Fix)

### Severity Guide
| Severity | Description | Response Time |
|----------|-------------|---------------|
| Critical | System unusable, data loss, security issue | < 24 hours |
| High | Major feature broken, no workaround | < 3 days |
| Medium | Feature impaired, workaround exists | < 1 week |
| Low | Minor issue, cosmetic, edge case | Next release |

### Priority Guide
| Priority | Description |
|----------|-------------|
| P1 | Fix immediately, blocks release |
| P2 | Fix this sprint |
| P3 | Fix this release |
| P4 | Fix when possible |

---

## Affected Area

### Epic/Story Links
- Link to the affected Epic and Story
- Use relative paths: `../epics/EP0001-*.md`
- Multiple bugs can affect same story

### Component
- Module, service, or subsystem affected
- Helps with assignment and analysis

---

## Reproduction Steps

### Good Steps
- Numbered, precise actions
- Include specific data values
- State starting conditions
- One action per step

### Example
```
1. Navigate to /login
2. Enter email: test@example.com
3. Enter password: wrong-password
4. Click "Sign In"
5. Observe error message
```

---

## Expected vs Actual

### Expected Behaviour
- What SHOULD happen
- Reference acceptance criteria if applicable
- Be specific about the outcome

### Actual Behaviour
- What DOES happen
- Include error messages verbatim
- Screenshot references if visual

---

## Root Cause Analysis

### When to Fill
- During `bug fix` investigation
- Before implementing fix

### What to Include
- Code location(s) causing the issue
- Why the bug exists (not just what's wrong)
- Reference specific files and lines

---

## Fix Description

### What to Include
- Approach taken to fix
- Files modified (with change descriptions)
- Any architectural considerations
- Trade-offs made

### Files Modified Table
| File | Change |
|------|--------|
| src/services/auth.ts:45 | Added null check for user session |

---

## Tests Added

### Purpose
- Prevent regression
- Document expected behaviour

### Table Format
| Test ID | Description | File |
|---------|-------------|------|
| TC0042 | Verify login fails gracefully with wrong password | tests/auth.test.ts |

---

## Verification

### Checklist
- [ ] Fix verified in development
- [ ] Regression tests pass
- [ ] No side effects observed
- [ ] Documentation updated (if applicable)

### Who Verifies
- Preferably not the person who fixed it
- QA or another developer
- Record verifier and date

---

## Related Items

### What to Link
- Affected Story: The story this bug affects
- Related Bug: Duplicate or dependent bugs
- Related Test: Test that caught or should catch this

### Duplicate Handling
- If duplicate found, close as "Won't Fix"
- Link to original bug in notes
- Keep original open

---

## Notes

### What to Include
- Investigation findings
- Workarounds discovered
- Communication with stakeholders
- Reopen notes if reopened

---

## Revision History

### Required Entries
- Bug reported (initial creation)
- Status changes
- Fix complete
- Verification complete
- Closed/Reopened

### Format
| Date | Author | Change |
|------|--------|--------|
| 2026-01-17 | Reporter | Bug reported |
| 2026-01-18 | Developer | Status → In Progress |
| 2026-01-19 | Developer | Status → Fixed, added regression test |

---


# See Also

- `reference-epic.md` - Epic workflows
- `reference-story.md` - Story workflows
- `reference-decisions.md` - Ready criteria, decision guidance
- `reference-requirements.md` - PRD, TRD, Persona workflows
- `reference-code.md` - Code plan, implement, review workflows
- `reference-testing.md` - Test Strategy, Spec, Automation workflows
