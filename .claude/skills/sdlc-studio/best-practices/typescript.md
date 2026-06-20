# TypeScript Best Practices

Standards and patterns for TypeScript code. For browser/DOM patterns shared
with plain JavaScript, see `javascript.md`.

---


## Quick conventions {#quick-conventions}

- Strict mode on; never `any` - use `unknown` and narrow.
- Validate external data at boundaries (e.g. zod) before trusting types.
- Discriminated unions over optional-field soup; `const` objects over enums.
- Let inference work; `import type` for type-only imports.
- Loaded alongside `javascript.md` for the shared JS/DOM conventions.

## Strict Mode

Always enable strict mode in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true
  }
}
```

**Why:** Catches whole bug classes (implicit any, null deref, unchecked
index access) at compile time. Retrofitting strict mode later is far more
expensive than starting with it.

---

## Prefer `unknown` to `any`

```typescript
// Bad - any disables checking everywhere it flows
function parse(input: string): any {
    return JSON.parse(input);
}

// Good - unknown forces narrowing before use
function parse(input: string): unknown {
    return JSON.parse(input);
}

const data = parse(raw);
if (isOrder(data)) {
    process(data.items);
}
```

**Why:** `any` silently infects downstream code; `unknown` keeps the
type-checker engaged and pushes validation to the boundary.

---

## Validate at Boundaries

Type assertions do not check anything at runtime. Validate external data
(API responses, file contents, env vars) with a schema library:

```typescript
// Bad - assertion, no runtime check
const order = (await res.json()) as Order;

// Good - parse, don't assert
const Order = z.object({
    id: z.string(),
    items: z.array(z.object({ sku: z.string(), qty: z.number().int() })),
});
type Order = z.infer<typeof Order>;

const order = Order.parse(await res.json());
```

**Why:** The compiler only sees compile time. Anything crossing a process
boundary must be checked where it enters.

---

## Discriminated Unions over Optional Fields

```typescript
// Bad - illegal states representable
interface FetchState {
    loading: boolean;
    data?: User;
    error?: Error;
}

// Good - each state is explicit, exhaustively checkable
type FetchState =
    | { status: "loading" }
    | { status: "success"; data: User }
    | { status: "error"; error: Error };
```

Use `never` for exhaustiveness:

```typescript
function render(state: FetchState) {
    switch (state.status) {
        case "loading": return spinner();
        case "success": return view(state.data);
        case "error": return alert(state.error);
        default: {
            const _exhaustive: never = state;
            return _exhaustive;
        }
    }
}
```

**Why:** Adding a new variant becomes a compile error at every switch
that misses it, instead of a silent fall-through.

---

## Const Objects over Enums

```typescript
// Avoid - enums generate runtime code and have surprising semantics
enum Role { Admin, User }

// Good - erased at compile time, plain values at runtime
const Role = {
    Admin: "admin",
    User: "user",
} as const;
type Role = (typeof Role)[keyof typeof Role];
```

**Why:** Const objects with `as const` give the same safety with no
runtime artefact, and the string values survive serialisation intact.

---

## Let Inference Work

```typescript
// Bad - noise, and the annotation can drift from the value
const names: string[] = users.map((u: User): string => u.name);

// Good - annotate parameters and public return types, infer the rest
const names = users.map((u) => u.name);
```

Annotate explicitly at module boundaries (exported function signatures),
where inference would widen unhelpfully, and for object literals you want
checked against a contract (`satisfies`):

```typescript
const config = {
    retries: 3,
    endpoint: "/api/v2",
} satisfies ClientConfig;
```

**Why:** `satisfies` checks the shape without losing the narrow literal
types that inference provides.

---

## Error Handling

```typescript
// Bad - caught value is unknown; don't assume Error
try {
    await sync();
} catch (err) {
    log(err.message);  // compile error under strict mode, and rightly so
}

// Good - narrow before use
try {
    await sync();
} catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    log(message);
}
```

For expected failures, return a result union instead of throwing:

```typescript
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };
```

**Why:** Thrown values are untyped; result unions make failure paths
visible in signatures and force callers to handle them.

---

## Modules and Imports

- Use ESM (`"type": "module"`); avoid CommonJS in new code.
- Use `import type { User } from "./user"` for type-only imports.
- No `namespace`; use modules.

**Why:** Type-only imports are erased cleanly by bundlers and avoid
accidental runtime cycles.

---

## Tooling

- **Lint/format:** ESLint (flat config) with `typescript-eslint`, plus
  Prettier. Run both in CI.
- **Tests:** Vitest or Jest; type-level assertions with `expectTypeOf`
  where the types are the contract.
- **Build:** `tsc --noEmit` as the type gate even when a bundler does
  the emitting.

**Why:** Bundlers skip type-checking for speed; without a `tsc` gate,
type errors ship.

---

## Testing Patterns

```typescript
describe("orderTotal", () => {
    it.each([
        ["empty order", [], 0],
        ["single item", [{ price: 10, qty: 2 }], 20],
        ["mixed items", [{ price: 10, qty: 1 }, { price: 5, qty: 4 }], 30],
    ])("%s", (_name, items, expected) => {
        expect(orderTotal(items)).toBe(expected);
    });
});
```

**Why:** Table-driven cases keep edge cases cheap to add, mirroring the
test-spec's AC table.
