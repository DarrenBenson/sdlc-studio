# Best Practices

Quality standards and code patterns for SDLC Studio.

---

## Language Guides

Each language has two files:
- `{language}-rules.md` - Concise checklist of standards (load first)
- `{language}-examples.md` - Code patterns and snippets (load when writing code)

| Language | Rules | Examples |
|----------|-------|----------|
| Python | `python-rules.md` | `python-examples.md` |
| TypeScript | `typescript-rules.md` | `typescript-examples.md` |
| JavaScript | `javascript-rules.md` | `javascript-examples.md` |
| Go | `go-rules.md` | `go-examples.md` |
| Rust | `rust-rules.md` | `rust-examples.md` |
| C# | `csharp-rules.md` | `csharp-examples.md` |
| PHP | `php-rules.md` | `php-examples.md` |

---

## How to Use

### During Code Planning

1. Load `{language}-rules.md` for the project's language
2. Use the checklist to validate your plan

### During Implementation

1. Load `{language}-rules.md` for standards
2. Load `{language}-examples.md` when writing code
3. Reference patterns for common tasks
4. Check anti-patterns before completing

### During Code Review

1. Verify checklist items in `{language}-rules.md`
2. Check for anti-patterns listed in each guide

---

## Technology Guides

| Guide | Purpose |
|-------|---------|
| `architecture.md` | SDLC-specific architecture patterns |
| `docker.md` | Container best practices |
| `openapi.md` | API design standards |
| `script.md` | Script structure (Bash/Python) |

---

## Universal Standards

Applied across all languages:

- British English (analyse, colour, behaviour)
- No em dashes - use en dash with spaces or restructure
- No corporate jargon (synergy, leverage, robust)
- Dense, economical writing
- Consistent Markdown formatting

---

## Quick Reference

### Security Essentials

| Risk | Mitigation |
|------|------------|
| SQL Injection | Parameterised queries |
| XSS | Output escaping |
| Code Injection | No `eval()` with user input |
| Credential Exposure | Environment variables |
| YAML Attacks | Safe loading only |

### Error Handling

| Language | Pattern |
|----------|---------|
| Python | Specific exceptions, logging |
| TypeScript | Custom errors, typed catch |
| JavaScript | try/catch, custom Error classes |
| Go | Wrap errors, `errors.Is/As` |
| Rust | `Result<T, E>`, `?` operator |
| C# | Specific exceptions, custom types |
| PHP | Typed exceptions, no `@` suppression |

### Testing

| Language | Framework | Key Pattern |
|----------|-----------|-------------|
| Python | pytest | Fixtures, parametrise |
| TypeScript | Vitest/Jest | Typed mocks |
| JavaScript | Vitest/Jest | Mocking, coverage |
| Go | testing | Table-driven tests |
| Rust | built-in | `#[test]`, proptest |
| C# | xUnit | Theory, Moq |
| PHP | PHPUnit | Data providers |

---

## See Also

- `../reference-code.md` - Code workflow reference
- `../reference-testing.md` - Test workflow reference
