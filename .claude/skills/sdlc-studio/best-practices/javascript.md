# Best Practices: JavaScript

Guidelines for JavaScript code based on modern standards and common pitfalls.

## DOM Manipulation

### Use Modern Selectors

```javascript
// GOOD - clear and efficient
const element = document.getElementById('myId');
const items = document.querySelectorAll('.item');
const button = document.querySelector('button[data-action="save"]');

// BAD - older, less flexible
const element = document.getElementsByClassName('item')[0];
```

### Event Delegation

For dynamically generated content, use event delegation:

```javascript
// GOOD - handles dynamic content, single listener
container.addEventListener('click', (e) => {
    const button = e.target.closest('.action-btn');
    if (button) {
        handleAction(button.dataset.action);
    }
});

// BAD - breaks when content changes, many listeners
document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', () => handleAction(btn.dataset.action));
});
```

### Clean Up Event Listeners

```javascript
// GOOD - use AbortController for cleanup
const controller = new AbortController();

element.addEventListener('click', handler, { signal: controller.signal });
element.addEventListener('keydown', handler, { signal: controller.signal });

// Later, clean up all at once
controller.abort();

// Also GOOD - named functions for removal
function handleClick(e) { /* ... */ }
element.addEventListener('click', handleClick);
element.removeEventListener('click', handleClick);
```

## Async Operations

### Always Handle Errors

```javascript
// GOOD - explicit error handling
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch failed:', error);
        throw error; // Re-throw or handle appropriately
    }
}

// BAD - unhandled promise rejection
async function fetchData(url) {
    const response = await fetch(url);
    return response.json(); // What if it fails?
}
```

### Use AbortController for Cancellation

```javascript
// GOOD - cancellable fetch
async function fetchWithTimeout(url, timeout = 5000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('Request timed out');
        }
        throw error;
    }
}
```

## Variable Declarations

### Prefer const, Then let

```javascript
// GOOD - immutable by default
const config = loadConfig();
const items = [];
items.push(newItem); // Array mutation is fine with const

// Use let only when reassignment is needed
let count = 0;
count++;

// BAD - never use var (hoisting issues)
var name = 'value';
```

### Destructuring

```javascript
// GOOD - clear and concise
const { name, age, location = 'Unknown' } = user;
const [first, second, ...rest] = items;

// Function parameters
function processUser({ name, email, role = 'user' }) {
    // ...
}

// BAD - verbose
const name = user.name;
const age = user.age;
const location = user.location || 'Unknown';
```

## String Handling

### Template Literals

```javascript
// GOOD - readable, supports expressions
const message = `Hello ${name}, you have ${count} items`;
const html = `
    <div class="item">
        <span>${escapeHtml(title)}</span>
    </div>
`;

// BAD - concatenation is error-prone
const message = 'Hello ' + name + ', you have ' + count + ' items';
```

### HTML Escaping

Always escape user content when inserting into HTML:

```javascript
// GOOD - escape untrusted content
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

element.innerHTML = `<span>${escapeHtml(userInput)}</span>`;

// Also GOOD - use textContent for plain text
element.textContent = userInput;

// BAD - XSS vulnerability
element.innerHTML = `<span>${userInput}</span>`;
```

## Arrays and Objects

### Array Methods

```javascript
// GOOD - functional, chainable
const activeUsers = users
    .filter(u => u.active)
    .map(u => u.name)
    .sort();

// Check existence
const hasAdmin = users.some(u => u.role === 'admin');
const allVerified = users.every(u => u.verified);

// Find single item
const admin = users.find(u => u.role === 'admin');

// BAD - imperative, harder to read
const activeUsers = [];
for (let i = 0; i < users.length; i++) {
    if (users[i].active) {
        activeUsers.push(users[i].name);
    }
}
```

### Object Spread and Defaults

```javascript
// GOOD - immutable updates
const updated = { ...original, name: newName };
const withDefaults = { timeout: 5000, retries: 3, ...options };

// BAD - mutates original
original.name = newName;
```

## Regular Expressions

### Character Classes

```javascript
// GOOD - no unnecessary escapes
const pattern = /^[-*] (.+)$/gm;     // - at start/end doesn't need escape
const pattern = /[:_-](word)/;        // - at end of class

// BAD - unnecessary escapes (ESLint warning)
const pattern = /^[\-\*] (.+)$/gm;
const pattern = /[:\-_](word)/;
```

### Named Groups (Modern)

```javascript
// GOOD - self-documenting
const datePattern = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/;
const match = dateStr.match(datePattern);
if (match) {
    const { year, month, day } = match.groups;
}
```

## Error Handling

### Custom Errors

```javascript
// GOOD - specific error types
class ValidationError extends Error {
    constructor(field, message) {
        super(message);
        this.name = 'ValidationError';
        this.field = field;
    }
}

try {
    validateForm(data);
} catch (error) {
    if (error instanceof ValidationError) {
        showFieldError(error.field, error.message);
    } else {
        throw error; // Re-throw unexpected errors
    }
}
```

## Performance

### Debounce and Throttle

```javascript
// Debounce - wait until activity stops
function debounce(fn, delay) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

// Usage - search input
searchInput.addEventListener('input', debounce(handleSearch, 300));

// Throttle - limit rate of calls
function throttle(fn, limit) {
    let inThrottle;
    return (...args) => {
        if (!inThrottle) {
            fn(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Usage - scroll handler
window.addEventListener('scroll', throttle(handleScroll, 100));
```

### Avoid Layout Thrashing

```javascript
// GOOD - batch reads, then writes
const heights = items.map(el => el.offsetHeight); // All reads
items.forEach((el, i) => {
    el.style.top = `${heights[i]}px`; // All writes
});

// BAD - interleaved reads/writes force reflow
items.forEach(el => {
    const height = el.offsetHeight; // Read
    el.style.top = `${height}px`;   // Write - forces reflow
});
```

## Security

### Avoid eval and innerHTML with User Data

```javascript
// NEVER - code injection
eval(userInput);
new Function(userInput)();

// DANGEROUS - XSS if not escaped
element.innerHTML = userInput;

// SAFE alternatives
element.textContent = userInput;
element.innerHTML = escapeHtml(userInput);
```

### Validate URLs

```javascript
// GOOD - validate URL protocol
function isSafeUrl(url) {
    try {
        const parsed = new URL(url);
        return ['http:', 'https:'].includes(parsed.protocol);
    } catch {
        return false;
    }
}

// BAD - allows javascript: URLs
element.href = userProvidedUrl;
```

## Checklist

Before completing JavaScript code:

- [ ] Use `const` by default, `let` when needed, never `var`
- [ ] All async operations have error handling
- [ ] User input is escaped before inserting into HTML
- [ ] Event listeners are cleaned up when appropriate
- [ ] No unnecessary regex escapes in character classes
- [ ] No duplicate function declarations
- [ ] Fetch requests have timeout/cancellation
- [ ] No `eval()` or `new Function()` with user data

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `var x = 1` | Hoisting bugs | Use `const` or `let` |
| `innerHTML = userInput` | XSS vulnerability | Use `textContent` or escape |
| `eval(code)` | Code injection | Use safer alternatives |
| `[\-\*]` in regex | Unnecessary escapes | Use `[-*]` |
| Inline onclick handlers | Hard to maintain | Use `addEventListener` |
| `catch (e) {}` empty | Hides errors | Log or handle the error |
| Nested callbacks | Callback hell | Use async/await |
