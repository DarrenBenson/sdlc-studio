# US0001: a visitor can sign up with an email address

> **Status:** Ready
> **Epic:** EP0001
> **Priority:** High
> **Affects:** src/auth/signup.py, tests/test_signup.py
> **Points:** 3

## Acceptance Criteria

### AC1: an account is created

- **Given** a valid email address
- **When** the signup form is submitted
- **Then** an account exists
- **Verify:** shell true
