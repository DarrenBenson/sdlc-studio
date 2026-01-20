# Go Rules

Standards checklist for Go code.

---

## Error Handling

- [ ] Wrap errors with context: `fmt.Errorf("failed to X: %w", err)`
- [ ] Check errors immediately after function calls
- [ ] Use `errors.Is()` and `errors.As()` for error checking
- [ ] Define sentinel errors for expected error conditions
- [ ] Never ignore errors with `_`

## Context Usage

- [ ] Pass `context.Context` as first parameter
- [ ] Check `ctx.Done()` in long-running operations
- [ ] Set timeouts on external calls
- [ ] Propagate context to child functions

## Interfaces

- [ ] Define interfaces at point of use, not implementation
- [ ] Keep interfaces small (1-3 methods)
- [ ] Use interface names ending in `-er` when possible
- [ ] Accept interfaces, return concrete types

## Concurrency

- [ ] Use channels for communication between goroutines
- [ ] Use `sync.WaitGroup` for goroutine coordination
- [ ] Protect shared state with `sync.Mutex`
- [ ] Always `defer cancel()` after `context.WithCancel/Timeout`
- [ ] Close channels from sender side only

## Testing

- [ ] Use table-driven tests for multiple cases
- [ ] Use `t.Helper()` in test helper functions
- [ ] Use `t.Run()` for subtests
- [ ] Mock time with clockwork or similar
- [ ] Run `go test -race` to detect race conditions

## Struct Design

- [ ] Use constructor functions (`NewX()`) for complex initialisation
- [ ] Use functional options for optional configuration
- [ ] Embed for composition, not inheritance
- [ ] Zero values should be useful

## Project Structure

- [ ] `cmd/` for main packages
- [ ] `internal/` for private packages
- [ ] `pkg/` for public libraries (if any)
- [ ] Keep main.go minimal

## Style

- [ ] Run `go fmt` before commit
- [ ] Run `go vet` for static analysis
- [ ] Use `golint` or `staticcheck`
- [ ] Names: `camelCase` for private, `PascalCase` for public
- [ ] Acronyms in caps: `HTTPClient`, `ID`

---

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `if err != nil { return err }` | Loses context | Wrap with `fmt.Errorf` |
| Interface in implementation pkg | Tight coupling | Define at point of use |
| `go func() { ... }()` without sync | Goroutine leak | Use WaitGroup or channel |
| Loop variable in goroutine | Shares variable | Capture as parameter |
| `defer f.Close()` in loop | Wrong file closed | Use closure or IIFE |
| Large interfaces | Hard to mock | Split into smaller interfaces |
| `err == ErrNotFound` | Doesn't handle wrapping | Use `errors.Is()` |
| Nil slice in JSON | Marshals to `null` | Use `[]T{}` for empty array |

---

## Required Tools

| Tool | Purpose | Command |
|------|---------|---------|
| go fmt | Formatting | `go fmt ./...` |
| go vet | Static analysis | `go vet ./...` |
| staticcheck | Extended checks | `staticcheck ./...` |
| golangci-lint | Meta-linter | `golangci-lint run` |

---

## See Also

- `go-examples.md` - Code patterns and snippets
