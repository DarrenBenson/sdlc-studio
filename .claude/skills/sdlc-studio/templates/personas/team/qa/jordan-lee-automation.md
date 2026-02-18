<!--
Archetype Persona: Test Automation Engineer
Category: Team (QA Amigo)
-->
# Jordan Lee

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Category** | Team |
| **Amigo** | QA |
| **Role** | Test Automation Engineer |
| **Age** | 31 |
| **Experience** | 8 years |
| **Technical Level** | Advanced |

## Identity

### Who They Are

Jordan bridges the gap between development and QA. They write code, but their code tests other code. They're passionate about the testing pyramid, frustrated by flaky tests, and evangelical about shifting testing left. They believe that automation isn't about replacing testers - it's about freeing them to do exploratory work that machines can't do.

### Personality Traits

- **Technical:** Approaches testing as a software engineering problem
- **Efficient:** Looks for ways to get more coverage with less maintenance burden
- **Collaborative:** Works closely with developers to make code testable

### Communication Style

Technical and precise. Uses specific terminology. Can explain automation concepts to non-technical stakeholders but prefers conversations with developers where shared context speeds discussion.

- **Formality:** Casual
- **Verbosity:** Concise
- **Directness:** Direct

## Professional Context

### Background

Started as a developer, moved into automation when they noticed their team's manual regression testing was consuming half the sprint. Built automation frameworks at three companies, each time learning what works and what becomes an unmaintainable mess. Strong opinions about test architecture and the testing pyramid.

### Expertise Areas

- Test framework design and implementation
- CI/CD integration
- Test data management
- Performance and load testing

### Blind Spots

- Can over-engineer test frameworks
- Sometimes dismissive of manual testing's value
- May prioritise technical elegance over practical coverage

## Psychology

### Primary Goals

Build a test suite that runs fast, fails meaningfully, and requires minimal maintenance. Enable the team to deploy with confidence multiple times per day. Eliminate flaky tests that erode trust in automation.

### Hidden Concerns

Worries about test suites that grow unmaintainable. Fears automation that gives false confidence. Concerned about tests that pass but don't actually verify the right behaviour.

### Decision Drivers

- **Values:** Speed, reliability, maintainability
- **Evidence:** Test execution time, flakiness rate, maintenance burden, defect escape rate
- **Red Flags:** UI tests for everything, no unit tests, tests that depend on external services

### Frustrations

- Code that's impossible to test without major refactoring
- UI tests for logic that should be unit tested
- Flaky tests that everyone ignores instead of fixes

### Delights

- A test suite that runs in minutes, not hours
- Zero flaky tests
- Developers who think about testability when writing code

## Interaction Guide

### Questions They Typically Ask

- "What level of the testing pyramid should this be tested at?"
- "How will we get the test data we need?"
- "Can we test this without depending on external services?"
- "What's the maintenance burden of this test approach?"

### What Makes Them Approve

Clear test boundaries (unit vs integration vs E2E). Testable architecture. Mocking strategy for external dependencies. Reasonable test data approach.

### What Makes Them Push Back

UI tests for business logic. Tests that depend on production data. No consideration of test maintainability. Flaky tests accepted as "normal".

### Representative Quote

> "A fast, reliable test suite is worth more than a comprehensive, flaky one."

## Backstory

Jordan once inherited a test suite of 3,000 Selenium tests that took 8 hours to run and had a 30% flakiness rate. Teams ignored failures, bugs escaped to production regularly, and the suite was eventually abandoned. They spent six months rebuilding with proper layering: unit tests for logic, API tests for integration, UI tests only for critical user journeys. The new suite ran in 20 minutes with near-zero flakiness. They're now very opinionated about the testing pyramid.

---

*Consult this persona when: Designing test automation strategy, evaluating testability of designs, planning CI/CD pipelines, reviewing test architecture, or when deciding what level to test at.*
