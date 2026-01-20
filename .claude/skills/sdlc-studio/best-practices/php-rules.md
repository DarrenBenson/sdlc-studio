# PHP Rules

Standards checklist for PHP code.

---

## Type Safety

- [ ] Declare `strict_types=1` in all files
- [ ] Type hints on all function parameters
- [ ] Return type declarations on all functions
- [ ] Use union types (`string|int`) for multiple types
- [ ] Use `?Type` or `Type|null` for nullable

## PSR Standards

- [ ] Follow PSR-12 coding style
- [ ] Use PSR-4 autoloading
- [ ] Follow PSR-3 for logging
- [ ] Follow PSR-7/PSR-15 for HTTP

## Error Handling

- [ ] Use exceptions, not error codes
- [ ] Catch specific exception types
- [ ] Create custom exception classes
- [ ] Never use `@` error suppression
- [ ] Set `error_reporting(E_ALL)`

## Security

- [ ] Use prepared statements for SQL (PDO/mysqli)
- [ ] Escape output with `htmlspecialchars()`
- [ ] Validate and sanitise all input
- [ ] Use `password_hash()` and `password_verify()`
- [ ] No `eval()`, `exec()`, or `shell_exec()` with user input

## Database

- [ ] Use PDO with prepared statements
- [ ] Set `PDO::ATTR_ERRMODE` to `EXCEPTION`
- [ ] Use transactions for multi-statement operations
- [ ] Close connections when done

## Testing

- [ ] Use PHPUnit for unit tests
- [ ] Test one thing per test method
- [ ] Use data providers for parameterised tests
- [ ] Mock external dependencies
- [ ] Aim for high coverage on business logic

## Namespaces and Autoloading

- [ ] One class per file
- [ ] Namespace matches directory structure
- [ ] Use Composer for autoloading
- [ ] Avoid `require`/`include` for classes

## Modern PHP

- [ ] Use PHP 8.0+ features where available
- [ ] Use named arguments for clarity
- [ ] Use match expressions over switch
- [ ] Use constructor property promotion
- [ ] Use attributes for metadata

---

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| No `strict_types` | Implicit coercion bugs | Add `declare(strict_types=1)` |
| `mysql_*` functions | Deprecated, insecure | Use PDO |
| String concatenation in SQL | SQL injection | Use prepared statements |
| `echo $userInput` | XSS vulnerability | Use `htmlspecialchars()` |
| `@function()` | Hides errors | Handle errors properly |
| `global $var` | Hidden dependencies | Use dependency injection |
| `eval($code)` | Code injection | Never eval user input |
| No type hints | Runtime type errors | Add type declarations |

---

## Required Configuration

```php
<?php
// At top of every file
declare(strict_types=1);

// php.ini recommendations
error_reporting = E_ALL
display_errors = Off  // In production
log_errors = On
```

---

## composer.json Best Practices

```json
{
    "require": {
        "php": "^8.1"
    },
    "autoload": {
        "psr-4": {
            "App\\": "src/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Tests\\": "tests/"
        }
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0",
        "phpstan/phpstan": "^1.0"
    }
}
```

---

## Required Tools

| Tool | Purpose | Command |
|------|---------|---------|
| PHP CS Fixer | Formatting | `php-cs-fixer fix` |
| PHPStan | Static analysis | `phpstan analyse` |
| Psalm | Type checking | `psalm` |
| PHPUnit | Testing | `phpunit` |

---

## See Also

- `php-examples.md` - Code patterns and snippets
