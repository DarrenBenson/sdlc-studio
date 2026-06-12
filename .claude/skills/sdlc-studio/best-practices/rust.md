# Rust Best Practices

Standards and patterns for Rust code.

---

## Error Handling

### No `unwrap()` or `expect()` on fallible paths

```rust
// Bad - panics in production on the first malformed line
let config: Config = toml::from_str(&text).unwrap();

// Good - propagate with context
let config: Config = toml::from_str(&text)
    .with_context(|| format!("failed to parse {}", path.display()))?;
```

`unwrap()` is acceptable in tests, examples, and where invariants make
failure impossible (document why with `expect("...invariant...")`).

### Pick the right error crate per crate type

- **Binaries:** `anyhow` - one opaque error type, easy context chaining.
- **Libraries:** `thiserror` - callers need to match on variants.

```rust
#[derive(Debug, thiserror::Error)]
pub enum StoreError {
    #[error("record {0} not found")]
    NotFound(String),
    #[error("storage unavailable")]
    Io(#[from] std::io::Error),
}
```

**Why:** Libraries that return `anyhow::Error` strip callers of the
ability to handle specific failures; binaries that define error enums
for every module add ceremony with no consumer.

---

## Ownership and Borrowing

### Accept the most general type

```rust
// Bad - forces callers to own and allocate
fn greet(name: String) { ... }

// Good - borrows, accepts &String, &str, and literals
fn greet(name: &str) { ... }
```

Likewise prefer `&[T]` to `&Vec<T>` and `impl AsRef<Path>` for paths.

### Clone deliberately, not reflexively

```rust
// Bad - clone to silence the borrow checker
let names: Vec<String> = users.clone().into_iter().map(|u| u.name).collect();

// Good - move or borrow what you need
let names: Vec<String> = users.into_iter().map(|u| u.name).collect();
```

**Why:** Scattered `.clone()` calls hide the real data flow and turn
the borrow checker's feedback off instead of acting on it.

---

## Type Design

### Newtypes for domain values

```rust
// Bad - any u64 passes
fn cancel(order_id: u64, user_id: u64) { ... }

// Good - the compiler keeps the IDs apart
struct OrderId(u64);
struct UserId(u64);
fn cancel(order_id: OrderId, user_id: UserId) { ... }
```

### Make illegal states unrepresentable

```rust
// Bad - four field combinations, two of them meaningless
struct Job { running: bool, result: Option<Output>, error: Option<Error> }

// Good - one variant per real state
enum Job {
    Running,
    Succeeded(Output),
    Failed(Error),
}
```

**Why:** Exhaustive `match` then proves every state is handled; adding
a variant becomes a compile error at every match site.

### Derive liberally

`#[derive(Debug, Clone, PartialEq)]` on data types as a baseline; add
`Eq`, `Hash`, `Default`, `serde::{Serialize, Deserialize}` as needed.

---

## Combinators over Manual Plumbing

```rust
// Bad
let port = match env::var("PORT") {
    Ok(v) => match v.parse::<u16>() {
        Ok(p) => p,
        Err(_) => 8080,
    },
    Err(_) => 8080,
};

// Good
let port = env::var("PORT")
    .ok()
    .and_then(|v| v.parse().ok())
    .unwrap_or(8080);
```

**Why:** `Option`/`Result` combinators state intent in one expression;
nested matches bury it. Stop chaining when a reader would have to
unpick it - a named helper beats a six-link chain.

---

## Tooling

- `cargo fmt` and `cargo clippy -- -D warnings` gate every commit.
- Fix clippy lints rather than `#[allow]`-ing them; an `allow` needs a
  comment saying why.
- `cargo test` includes doctests: code in `///` examples is compiled
  and run, so public API docs stay honest.

```rust
/// Returns the total in pence.
///
/// ```
/// let order = Order::new();
/// assert_eq!(order.total(), 0);
/// ```
pub fn total(&self) -> u64 { ... }
```

---

## Testing Patterns

Unit tests live beside the code; integration tests in `tests/`:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_empty_sku() {
        let err = Item::new("", 1).unwrap_err();
        assert!(matches!(err, ItemError::EmptySku));
    }
}
```

Table-style cases via a loop or the `rstest` crate:

```rust
#[rstest]
#[case("", 1, ItemError::EmptySku)]
#[case("SKU1", 0, ItemError::ZeroQty)]
fn rejects_invalid(#[case] sku: &str, #[case] qty: u32, #[case] want: ItemError) {
    assert_eq!(Item::new(sku, qty).unwrap_err(), want);
}
```

**Why:** `matches!` asserts on variants without brittle string
comparison; parameterised cases keep edge cases cheap to add.
