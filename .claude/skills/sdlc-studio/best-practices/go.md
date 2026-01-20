# Go Best Practices

Standards and patterns for Go code.

---

## Table-Driven Tests

The idiomatic way to write tests in Go:

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name     string
        a, b     int
        expected int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -1, -1, -2},
        {"zeros", 0, 0, 0},
        {"mixed signs", -5, 10, 5},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.expected {
                t.Errorf("Add(%d, %d) = %d; want %d", tt.a, tt.b, got, tt.expected)
            }
        })
    }
}
```

**Why:** Easy to add cases, clear failure messages, subtests run in parallel.

---

## Error Handling

### Wrap errors with context

```go
// Bad - loses context
if err != nil {
    return err
}

// Good - adds context for debugging
if err != nil {
    return fmt.Errorf("failed to process item %s: %w", item.ID, err)
}
```

### Check specific errors

```go
if errors.Is(err, ErrNotFound) {
    // Handle not found case
}

var pathErr *os.PathError
if errors.As(err, &pathErr) {
    // Handle path-specific error
}
```

### Sentinel errors

```go
var (
    ErrNotFound      = errors.New("not found")
    ErrInvalidInput  = errors.New("invalid input")
    ErrUnauthorised  = errors.New("unauthorised")
)
```

---

## Interface Design

### Define interfaces at point of use

```go
// Bad - interface in implementation package
package storage

type UserStore interface {
    Get(id string) (*User, error)
    Save(user *User) error
}

// Good - interface where it's needed
package handler

// UserGetter is what this handler needs
type UserGetter interface {
    Get(id string) (*User, error)
}

func NewHandler(users UserGetter) *Handler {
    return &Handler{users: users}
}
```

### Keep interfaces small

```go
// Bad - too many methods
type Repository interface {
    Get(id string) (*Entity, error)
    GetAll() ([]*Entity, error)
    Create(e *Entity) error
    Update(e *Entity) error
    Delete(id string) error
    Search(query string) ([]*Entity, error)
    Count() (int, error)
}

// Good - single responsibility
type Getter interface {
    Get(id string) (*Entity, error)
}

type Saver interface {
    Save(e *Entity) error
}
```

---

## Context Usage

### Pass context as first parameter

```go
func ProcessOrder(ctx context.Context, orderID string) error {
    // Use ctx for cancellation and deadlines
}
```

### Respect cancellation

```go
func LongRunningTask(ctx context.Context) error {
    for _, item := range items {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            if err := process(ctx, item); err != nil {
                return err
            }
        }
    }
    return nil
}
```

### Set timeouts

```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()

result, err := slowOperation(ctx)
```

---

## Concurrency

### Use channels for communication

```go
// Worker pool pattern
func ProcessItems(items []Item, workers int) []Result {
    jobs := make(chan Item, len(items))
    results := make(chan Result, len(items))

    // Start workers
    for w := 0; w < workers; w++ {
        go func() {
            for item := range jobs {
                results <- process(item)
            }
        }()
    }

    // Send jobs
    for _, item := range items {
        jobs <- item
    }
    close(jobs)

    // Collect results
    output := make([]Result, len(items))
    for i := range items {
        output[i] = <-results
    }
    return output
}
```

### Use sync.WaitGroup for goroutine coordination

```go
var wg sync.WaitGroup
for _, url := range urls {
    wg.Add(1)
    go func(u string) {
        defer wg.Done()
        fetch(u)
    }(url)
}
wg.Wait()
```

### Protect shared state with mutex

```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}
```

---

## Struct Design

### Use constructor functions

```go
func NewServer(addr string, opts ...Option) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second, // Default
    }
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Functional options
type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.timeout = d
    }
}
```

### Embed for composition

```go
type Logger struct {
    prefix string
}

func (l *Logger) Log(msg string) {
    fmt.Printf("[%s] %s\n", l.prefix, msg)
}

type Service struct {
    *Logger  // Embed - Service gains Log method
    db *sql.DB
}
```

---

## Testing Patterns

### Test helpers

```go
func TestHandler(t *testing.T) {
    // Helper marks function as test helper (better stack traces)
    client := newTestClient(t)

    resp := client.Get("/users/1")
    assertStatus(t, resp, http.StatusOK)
}

func newTestClient(t *testing.T) *TestClient {
    t.Helper()
    // Setup code...
    return client
}

func assertStatus(t *testing.T, resp *http.Response, want int) {
    t.Helper()
    if resp.StatusCode != want {
        t.Errorf("status = %d; want %d", resp.StatusCode, want)
    }
}
```

### Time mocking with clockwork

```go
import "github.com/jonboulle/clockwork"

type Service struct {
    clock clockwork.Clock
}

func (s *Service) IsExpired(createdAt time.Time) bool {
    return s.clock.Now().Sub(createdAt) > 24*time.Hour
}

// In tests:
func TestIsExpired(t *testing.T) {
    fakeClock := clockwork.NewFakeClock()
    svc := &Service{clock: fakeClock}

    createdAt := fakeClock.Now()
    fakeClock.Advance(25 * time.Hour)

    if !svc.IsExpired(createdAt) {
        t.Error("expected expired")
    }
}
```

---

## Project Structure

```
project/
├── cmd/
│   └── myapp/
│       └── main.go       # Entry point
├── internal/
│   ├── handler/          # HTTP handlers
│   ├── service/          # Business logic
│   └── storage/          # Data access
├── pkg/                   # Public libraries
├── go.mod
└── go.sum
```

**Rules:**
- `internal/` - private to this module
- `pkg/` - importable by external projects
- `cmd/` - main packages only

---

## Common Mistakes

### Nil slice vs empty slice

```go
// Nil slice - JSON marshals to null
var s []string
json.Marshal(s) // "null"

// Empty slice - JSON marshals to []
s := []string{}
json.Marshal(s) // "[]"

// Or use make
s := make([]string, 0)
```

### Closing over loop variable

```go
// Bad - all goroutines share same i
for i := range items {
    go func() {
        process(items[i]) // Bug: i changes
    }()
}

// Good - capture value
for i := range items {
    go func(i int) {
        process(items[i])
    }(i)
}

// Go 1.22+ - loop variables are per-iteration
for i := range items {
    go func() {
        process(items[i]) // Safe in Go 1.22+
    }()
}
```

### Deferred function arguments

```go
// Argument evaluated immediately
for _, f := range files {
    defer f.Close() // Bug: all close same file
}

// Fix: use closure
for _, f := range files {
    defer func(file *os.File) {
        file.Close()
    }(f)
}
```
