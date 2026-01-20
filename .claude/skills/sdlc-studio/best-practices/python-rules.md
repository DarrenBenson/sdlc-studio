# Python Rules

Standards checklist for Python code.

---

## Type Safety

- [ ] Type hints on all public function signatures
- [ ] `Optional[T]` or `T | None` for nullable types
- [ ] Use `pathlib.Path` for file paths, not strings
- [ ] Generic types for collections (`list[str]`, not `list`)

## Error Handling

- [ ] Catch specific exceptions, never bare `except:`
- [ ] Never silence exceptions with `except: pass`
- [ ] Log errors with context before re-raising
- [ ] Top-level entry points may catch `Exception` for clean exit

## Security

- [ ] YAML: Always use `yaml.safe_load()`, never `yaml.load()`
- [ ] API keys from environment or config, never hardcoded
- [ ] No `eval()` or `exec()` with user input
- [ ] Validate file paths to prevent traversal attacks

## HTTP Requests

- [ ] Always set explicit timeouts: `timeout=(connect, read)`
- [ ] Use sessions for multiple requests to same host
- [ ] Handle `Timeout`, `ConnectionError`, `HTTPError` separately
- [ ] Use `response.raise_for_status()` after requests

## File Operations

- [ ] Use `pathlib.Path` for path manipulation
- [ ] Context managers for file handles: `with open(...) as f:`
- [ ] Use `path.read_text()` / `path.write_text()` for simple I/O
- [ ] Specify encoding explicitly when needed

## Resource Management

- [ ] Context managers for resources (files, connections, locks)
- [ ] PIL/Pillow: `with Image.open(path) as im:`
- [ ] Database connections: `with connection:` or proper cleanup
- [ ] Close sockets, file handles, and streams

## Testing

- [ ] Use pytest fixtures, not `setUp`/`tearDown`
- [ ] Parametrise similar test cases with `@pytest.mark.parametrize`
- [ ] Mock external dependencies (HTTP, filesystem, time)
- [ ] Run with `-W error` to treat warnings as errors

## Logging

- [ ] Use `logging` module, not `print()` for debugging
- [ ] Create logger with `logger = logging.getLogger(__name__)`
- [ ] Use lazy formatting: `logger.info("count: %d", count)`
- [ ] Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)

## Style

- [ ] Follow PEP 8 naming: `snake_case` for functions/variables
- [ ] Classes use `PascalCase`
- [ ] Constants use `UPPER_SNAKE_CASE`
- [ ] Keep functions under 50 lines
- [ ] Maximum 4 levels of nesting

---

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `yaml.load(f)` | Remote code execution | `yaml.safe_load(f)` |
| `requests.post(url)` | No timeout, hangs forever | `timeout=(5, 120)` |
| `except Exception: pass` | Hides bugs | Catch specific exceptions |
| `open(path)` without `with` | Resource leak | `with open()` or pathlib |
| Hardcoded API keys | Security breach | Environment variables |
| `Image.open()` without `with` | File handle leak | Context manager |
| `except:` bare | Catches `KeyboardInterrupt` | `except Exception:` minimum |
| `print()` for debugging | No log levels, not configurable | Use `logging` module |

---

## Required Libraries

| Library | Usage |
|---------|-------|
| `pathlib` | File path handling |
| `logging` | Application logging |
| `typing` | Type hints |
| `pytest` | Testing |
| `ruff` | Linting and formatting |

---

## See Also

- `python-examples.md` - Code patterns and snippets
- `script.md` - Script structure (Python and Bash)
