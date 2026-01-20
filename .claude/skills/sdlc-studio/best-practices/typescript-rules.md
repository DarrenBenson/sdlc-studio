# TypeScript Rules

Standards checklist for TypeScript code.

---

## Type Safety

- [ ] Enable `strict: true` in tsconfig.json
- [ ] No `any` type without explicit justification
- [ ] Use `unknown` instead of `any` for truly unknown types
- [ ] Explicit return types on public functions
- [ ] Use `readonly` for immutable properties
- [ ] Prefer `type` for unions/intersections, `interface` for objects

## Null Safety

- [ ] Enable `strictNullChecks`
- [ ] Use optional chaining (`?.`) and nullish coalescing (`??`)
- [ ] Narrow types with type guards before use
- [ ] No non-null assertions (`!`) without documented reason
- [ ] Handle all nullable cases explicitly

## Async Operations

- [ ] Always return `Promise<T>` with explicit type
- [ ] Handle errors in try/catch or .catch()
- [ ] Use AbortController for cancellable operations
- [ ] Type async function return values

## Error Handling

- [ ] Use custom error classes extending Error
- [ ] Type catch blocks properly (error is `unknown` in TS 4.4+)
- [ ] Never use empty catch blocks
- [ ] Use discriminated unions for error results

## API Types

- [ ] Define response types matching actual API responses
- [ ] Use `Pick`, `Omit`, `Partial` for derived types
- [ ] Keep types in sync with backend schemas
- [ ] Use Zod or similar for runtime validation

## Imports/Exports

- [ ] Use named exports over default exports
- [ ] Group imports: external, internal, types
- [ ] Use type-only imports: `import type { X }`
- [ ] No circular dependencies

## Testing

- [ ] Type test utilities and fixtures
- [ ] Use `jest.MockedFunction<T>` for typed mocks
- [ ] Test type guards with edge cases
- [ ] Configure Jest/Vitest with TypeScript

## Style

- [ ] Enable ESLint with `@typescript-eslint`
- [ ] Use Prettier for formatting
- [ ] PascalCase for types/interfaces/classes
- [ ] camelCase for variables/functions
- [ ] UPPER_SNAKE_CASE for constants

---

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `any` type | Loses type safety | Use `unknown` or proper type |
| `as` casts | Bypasses type checking | Use type guards |
| `!` non-null assertion | Hides null bugs | Handle null case |
| `// @ts-ignore` | Suppresses all errors | Fix the type issue |
| Default exports | Refactoring breaks | Use named exports |
| `object` type | Too broad | Use specific interface |
| Nested ternaries | Hard to read | Use if/else or switch |
| `Function` type | No parameter types | Use specific signature |

---

## tsconfig.json Essentials

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true
  }
}
```

---

## Required Tools

| Tool | Purpose |
|------|---------|
| TypeScript | Type checking |
| ESLint + @typescript-eslint | Linting |
| Prettier | Formatting |
| ts-node or tsx | Execution |
| Vitest or Jest | Testing |

---

## See Also

- `typescript-examples.md` - Code patterns and snippets
- `javascript-rules.md` - JavaScript patterns (applies to TS)
