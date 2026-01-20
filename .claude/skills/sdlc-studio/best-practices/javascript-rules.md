# JavaScript Rules

Standards checklist for JavaScript code.

---

## Variables

- [ ] Use `const` by default
- [ ] Use `let` only when reassignment is needed
- [ ] Never use `var`
- [ ] Destructure objects and arrays when accessing multiple properties

## Async Operations

- [ ] All async operations have error handling
- [ ] Use `async/await` over promise chains
- [ ] Fetch requests have timeout/cancellation via AbortController
- [ ] Never leave unhandled promise rejections

## Security

- [ ] Never use `eval()` or `new Function()` with user data
- [ ] Escape user input before inserting into HTML
- [ ] Use `textContent` for plain text, not `innerHTML`
- [ ] Validate URL protocols before using user-provided URLs
- [ ] No inline event handlers (`onclick=`)

## DOM Manipulation

- [ ] Use `querySelector`/`querySelectorAll` for selections
- [ ] Use event delegation for dynamic content
- [ ] Clean up event listeners when removing elements
- [ ] Batch DOM reads before DOM writes (avoid layout thrashing)

## Error Handling

- [ ] Never use empty `catch (e) {}`
- [ ] Log or handle all caught errors
- [ ] Create custom error classes for domain-specific errors
- [ ] Re-throw unexpected errors

## Performance

- [ ] Debounce search/input handlers
- [ ] Throttle scroll/resize handlers
- [ ] Batch DOM operations
- [ ] Avoid synchronous layout queries in loops

## Style

- [ ] Use template literals for string interpolation
- [ ] Use array methods (`map`, `filter`, `find`) over loops
- [ ] Use object spread for immutable updates
- [ ] Keep functions under 50 lines
- [ ] Named functions for event handlers (for removal)

## Regular Expressions

- [ ] No unnecessary escapes in character classes (`[-*]` not `[\-\*]`)
- [ ] Use named capture groups for complex patterns
- [ ] Comment complex regex patterns

---

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `var x = 1` | Hoisting bugs | Use `const` or `let` |
| `innerHTML = userInput` | XSS vulnerability | Use `textContent` or escape |
| `eval(code)` | Code injection | Use safer alternatives |
| `[\-\*]` in regex | Unnecessary escapes | Use `[-*]` |
| Inline `onclick` handlers | Hard to maintain | Use `addEventListener` |
| `catch (e) {}` empty | Hides errors | Log or handle the error |
| Nested callbacks | Callback hell | Use async/await |
| `fetch(url)` no error check | Silent failures | Check `response.ok` |

---

## Required Patterns

| Situation | Pattern |
|-----------|---------|
| Multiple requests to same host | Use fetch with shared headers |
| Dynamic content events | Event delegation |
| Search input | Debounce handler |
| Scroll handlers | Throttle handler |
| User input in DOM | Escape or use `textContent` |

---

## See Also

- `javascript-examples.md` - Code patterns and snippets
- `typescript-rules.md` - TypeScript-specific rules
