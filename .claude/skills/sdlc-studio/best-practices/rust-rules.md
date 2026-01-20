# Rust Rules

Standards checklist for Rust code.

---

## Error Handling

- [ ] Use `Result<T, E>` for recoverable errors
- [ ] Use `Option<T>` for optional values
- [ ] Propagate errors with `?` operator
- [ ] Create custom error types with `thiserror`
- [ ] No `.unwrap()` in library code without comment
- [ ] Use `.expect("reason")` when panic is acceptable

## Ownership and Borrowing

- [ ] Prefer borrowing (`&T`) over ownership when possible
- [ ] Use `&mut T` only when mutation is required
- [ ] Avoid unnecessary cloning - benchmark first
- [ ] Use `Cow<str>` when ownership is conditional
- [ ] Understand lifetimes before using `'static`

## Memory Safety

- [ ] No `unsafe` without documented safety invariants
- [ ] Minimise `unsafe` block scope
- [ ] Use `#[deny(unsafe_code)]` in safe-only crates
- [ ] Audit unsafe dependencies

## Concurrency

- [ ] Use `Arc<T>` for shared ownership across threads
- [ ] Use `Mutex<T>` or `RwLock<T>` for shared mutable state
- [ ] Prefer channels over shared state when possible
- [ ] Use `tokio` or `async-std` for async operations
- [ ] Avoid blocking in async contexts

## Testing

- [ ] Unit tests in same file with `#[cfg(test)]` module
- [ ] Integration tests in `tests/` directory
- [ ] Use `#[should_panic]` for panic tests
- [ ] Test error conditions, not just happy path
- [ ] Use `proptest` for property-based testing

## Documentation

- [ ] Doc comments (`///`) on public items
- [ ] Examples in doc comments with `# ` hidden lines
- [ ] Module-level docs with `//!`
- [ ] Run `cargo doc --open` to verify

## Clippy and Formatting

- [ ] Run `cargo clippy` with no warnings
- [ ] Run `cargo fmt` before commit
- [ ] Enable `#![warn(clippy::all)]` in lib.rs
- [ ] Consider `#![warn(clippy::pedantic)]` for stricter checks

## Dependencies

- [ ] Audit dependencies with `cargo audit`
- [ ] Use specific versions, not wildcards
- [ ] Review `Cargo.lock` changes
- [ ] Prefer well-maintained crates

---

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `.unwrap()` everywhere | Panics in production | Use `?` or handle error |
| `clone()` to satisfy borrow checker | Performance | Restructure ownership |
| `String` parameters | Unnecessary allocation | Use `&str` or `impl AsRef<str>` |
| Large `unsafe` blocks | Hard to audit | Minimise unsafe scope |
| `'static` everywhere | Inflexible | Use proper lifetimes |
| Ignoring Clippy warnings | Missed optimisations | Fix all warnings |
| `panic!()` in library | Crashes callers | Return `Result` |
| `Box<dyn Error>` | Loses type info | Use custom error enum |

---

## Cargo.toml Best Practices

```toml
[package]
name = "myproject"
version = "0.1.0"
edition = "2021"
rust-version = "1.70"

[dependencies]
thiserror = "1.0"
anyhow = "1.0"

[dev-dependencies]
pretty_assertions = "1.4"

[lints.rust]
unsafe_code = "forbid"

[lints.clippy]
all = "warn"
pedantic = "warn"
```

---

## Required Tools

| Tool | Purpose | Command |
|------|---------|---------|
| rustfmt | Formatting | `cargo fmt` |
| Clippy | Linting | `cargo clippy` |
| cargo-audit | Security | `cargo audit` |
| cargo-deny | Dependency checks | `cargo deny check` |

---

## See Also

- `rust-examples.md` - Code patterns and snippets
