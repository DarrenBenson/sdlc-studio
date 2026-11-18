# CR-0742: Harness-agnostic and enterprise-ready documentation

> **Status:** Complete
> **Decomposed-into:** EP0377
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** High
> **Type:** Improvement
> **Target:** 6.4, alongside the evidence and cost work (RFC0062). 6.4.0 was tagged on 2026-11-16, so this lands in the next release cut from main.
> **Requested-by:** the operator, 2026-11-18

## Summary

Update every public surface of SDLC Studio so it reads consistently as an open, harness-agnostic Agent Skill. It runs inside an organisation's approved harness and model contracts, and produces the governance evidence enterprise change processes ask for. No surface should suggest that Claude Code or an Anthropic subscription is required.

## Why

- An enterprise architecture review of SDLC Studio recently concluded that it runs on Claude Code with Anthropic subscriptions outside the organisation's contracts, and that moving it to GitHub Copilot would need Claude Code-specific changes. Neither is true: the adopting team runs it in GitHub Copilot under its organisation's contract.
- The repository invites that reading:
  - The GitHub About description reads "Claude Code skill for managing the full software development lifecycle".
  - The canonical skill lives under `.claude/skills/sdlc-studio/`, and `CLAUDE.md` sits at the repository root.
  - Some features are labelled for Claude Code (for example `epic implement --agentic`) with no stated equivalent or fallback elsewhere.
  - The Anthropic sponsorship line can read as a dependency to someone skimming.
- Enterprise reviewers decide in minutes from the About box, the README first screen and the website home page. They look for: which harnesses, which models and contracts, where data goes, how cost is controlled, how it fits existing change and audit controls, and how to adopt it without forking. Today those answers are scattered or missing.
- This supports the positioning decided on 2026-11-09: human in the lead, with the accountable engineering lead as the primary persona.

## Impact

Enterprise reviewers decide in minutes from the About box, the README first screen and the website home page. Today those surfaces invite the reading that SDLC Studio needs Claude Code and an Anthropic subscription outside the organisation's contracts, which is not true: adopting teams run it in GitHub Copilot under their own organisation's contract.

## Outcome

A reviewer who reads only the About box, the README first screen or the website home page comes away knowing that SDLC Studio:

1. works in GitHub Copilot, Claude Code, Cursor, OpenAI Codex, Gemini CLI and opencode, and is tied to none of them;
2. uses whichever models the organisation's harness provides under its own contracts, with no separate vendor subscription;
3. produces the evidence change boards and auditors ask for, with people owning intent and sign-off;
4. reports its own token use and cost, so teams can manage spend.

## Requested changes

1. **GitHub About description and topics.**
   - Proposed description: "Harness-agnostic Agent Skill for governed software delivery, human in the lead. Works in GitHub Copilot, Claude Code, Cursor, Codex, Gemini CLI and opencode."
   - Proposed topics: agent-skills, sdlc, software-delivery, ai-governance, github-copilot, claude-code, cursor, codex, gemini-cli, opencode.
   - These are repository settings, not files. If they cannot be changed (for example with `gh repo edit`), record the exact text in this CR for the owner to apply.
2. **README.**
   - Rewrite the opening and first screen to lead with harness-agnostic and human in the lead, name the six harnesses, and link to the new harness and enterprise pages.
   - Remove or qualify any generic use of "Claude Code skill" or Claude Code-first wording. Keep harness-specific instructions in the install section.
   - Present harnesses neutrally (one table, alphabetical), with GitHub Copilot as a first-class path: install location, invocation and verification command.
   - Do not lengthen the README; this should move it towards the planned target of about 1,500 words.
3. **New page: harness compatibility** (`docs/harnesses.md`, linked from README, `docs/INSTALL.md` and the website).
   - A matrix of capabilities by harness: install path, invocation, skill discovery, parallel or sub-agents, token and cost reporting, hooks and gates, live reload.
   - For every harness-specific feature, state the equivalent or the fallback in the other harnesses (for example, what `epic implement --agentic` does outside Claude Code).
   - Verify each cell against the code and installers. Mark anything not tested as "untested" rather than claiming support.
4. **New page: adopting SDLC Studio in an enterprise** (`docs/enterprise.md`; this is also the planned page for engineering leaders).
   - Harness and models: runs inside your approved harness and uses the models it exposes under your contracts. No separate subscription or vendor relationship is needed, and model choice per phase or persona is yours.
   - Data: what SDLC Studio itself does and does not send anywhere. Check the installers and scripts for network calls, downloads and telemetry before stating it.
   - Adopting without forking: install a pinned release; keep organisation configuration (personas, TSD templates, standards) in your own repository; upgrade with the upgrade and migrate commands; show how a shared skills repository can reference released versions.
   - Fitting existing controls: the evidence each change carries (PRD, TRD, TSD, test plans and results, independent review, and sign-off by someone who neither wrote nor reviewed the unit), stored in the same pull request as the code. Add a generic mapping to common SDLC control gates: requirements approved, design reviewed, tests evidenced, independent review, approval before release. Describe the evidence only; claim no certification or compliance.
   - Cost: per-run token and cost reporting, forecast cost per point, how to set and watch budgets, and how this works with request-based billing such as GitHub Copilot premium requests, including the 6.4 token cost estimation.
   - Verification for less experienced engineers: independent review and human-owned test specifications.
5. **Website (sdlc-studio.com).** Mirror the README positioning on the home page, link the two new pages, and keep the "One install, every agent" list consistent with the matrix.
6. **Skill metadata.** Make the SKILL.md description harness-neutral, as harnesses show it when listing skills. Check `llms.txt`, `package.json` and any other metadata for the same issue.
7. **Sponsorship wording.** Keep the Anthropic sponsorship acknowledgement, move it to an Acknowledgements section in the README and the site footer, and add that SDLC Studio does not require Anthropic products.
8. **Repository-wide sweep.**
   - Search `README.md`, `docs/` (`INSTALL.md`, `why-sdlc-studio.md`, `whitepaper.md`, `existing-users.md`, `known-issues.md`, release notes), the skill's `help/` and reference files, `AGENTS.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md` and `llms.txt`.
   - Look for "Claude Code skill", generic uses of "Claude Code" or "Claude", "Anthropic" listed as a prerequisite, and Claude-only paths presented as the only option.
   - Make generic statements harness-neutral; leave harness-specific instructions where they belong.
9. **Evidence page.** When regenerating it from the run reports (it currently stops at RPT0011), show the harness and model for each run, so readers can see runs outside Claude Code. If the reports do not record the harness, raise a separate CR to add it.
10. **CHANGELOG.** Add a documentation entry for this change.

## Out of scope

Raise separately if needed:

- Moving the canonical skill source out of `.claude/skills/` to a neutral path. It may help perception, but it affects the installers and existing users, so assess it in an RFC.
- Feature work to close any harness gaps the matrix finds.

## Acceptance Criteria

- A search of public docs finds no "Claude Code skill" and no generic statement that Claude Code or Anthropic is required.
- The About description and topics are updated, or the exact text is recorded for the owner.
- The README first screen names all six harnesses and links to the harness and enterprise pages, and the README is no longer than before.
- `docs/harnesses.md` exists; every cell is verified or marked untested; every harness-specific feature has a stated fallback.
- `docs/enterprise.md` covers harness and models, data, adoption without forking, controls and evidence, and cost, with every factual claim checked against the code.
- The SKILL.md description, `llms.txt` and the website match the new positioning.
- `CHANGELOG.md` has an entry.

## Constraints

- Public documents must not name any organisation, person or internal review. Describe the trigger generically, as in "Why" above.
- Do not overstate: no certifications, no untested harness claims, and no performance figures beyond those in signed run reports.
- Keep wording consistent with human in the lead and the persona registry decisions of 2026-11-09.
- British English.

## Applied

Applied on 2026-11-18 with `gh repo edit`, after US1315's review: the GitHub About description
is the text under Requested changes item 1, and the topics are exactly its ten, replacing the
previous ones (including `claude-code-skill`). `package.json` carries the same description and
the ten topics as its keywords (US1315).

Requested change 5, the website, lives in the website's own repository, so EP0377 delivers the
other nine here and a change request filed in that repository carries change 5, run after this
one: the home page positioning, the agents list matching docs/harnesses.md, links to the two new
pages, the footer sponsorship line, and the site's evidence page.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Created via `new` (deterministic) |
