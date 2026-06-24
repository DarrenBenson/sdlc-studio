# CR-0103: best-practices + code check omit SOTA linters (ShellCheck/shfmt, Ruff/mypy) and teach bare set -e

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

best-practices/script.md hand-maintains an anti-pattern table but never mentions ShellCheck/shfmt and teaches bare set -e (ignores unset vars + pipeline failures); best-practices/python.md has no Tooling section (no Ruff/Black/mypy) unlike typescript.md/rust.md; python.md also uses typing.Optional against the PEP 604 / 3.10+ floor; help/code.md code check dispatches Python/TS/Go/Rust linters but has no shell entry, so the bash the skill ships is never statically analysed.

## Acceptance Criteria

- [ ] script.md adds a Tooling section recommending ShellCheck + shfmt (framing the anti-pattern table as what ShellCheck enforces mechanically) and teaches set -euo pipefail with a one-line why
- [ ] python.md gains a Tooling section (Ruff + mypy/pyright, 3.10+ floor) parallel to typescript.md/rust.md, and its Type Hints example uses PEP 604 'tuple[Path, dict] | None' dropping typing.Optional
- [ ] help/code.md code check lists a shell linter (ShellCheck + shfmt) so every language the repo ships is covered
- [ ] CHANGELOG entry same commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
