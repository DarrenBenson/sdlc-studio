# Go Examples

Code patterns and snippets for Go.

---

## Table-Driven Tests

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

---

## Error Handling

### Wrap Errors with Context

```go
// GOOD - adds context for debugging
if err != nil {
    return fmt.Errorf("failed to process item %s: %w", item.ID, err)
}

// BAD - loses context
if err != nil {
    return err
}
```

### Check Specific Errors

```go
if errors.Is(err, ErrNotFound) {
    // Handle not found case
}

var pathErr *os.PathError
if errors.As(err, &pathErr) {
    // Handle path-specific error
}
```

### Sentinel Errors

```go
var (
    ErrNotFound      = errors.New("not found")
    ErrInvalidInput  = errors.New("invalid input")
    ErrUnauthorised  = errors.New("unauthorised")
)
```

---

## Interface Design

### Define at Point of Use

```go
// BAD - interface in implementation package
package storage

type UserStore interface {
    Get(id string) (*User, error)
    Save(user *User) error
}

// GOOD - interface where it's needed
package handler

// UserGetter is what this handler needs
type UserGetter interface {
    Get(id string) (*User, error)
}

func NewHandler(users UserGetter) *Handler {
    return &Handler{users: users}
}
```

### Keep Interfaces Small

```go
// BAD - too many methods
type Repository interface {
    Get(id string) (*Entity, error)
    GetAll() ([]*Entity, error)
    Create(e *Entity) error
    Update(e *Entity) error
    Delete(id string) error
    Search(query string) ([]*Entity, error)
    Count() (int, error)
}

// GOOD - single responsibility
type Getter interface {
    Get(id string) (*Entity, error)
}

type Saver interface {
    Save(e *Entity) error
}
```

---

## Context Usage

### Pass as First Parameter

```go
func ProcessOrder(ctx context.Context, orderID string) error {
    // Use ctx for cancellation and deadlines
}
```

### Respect Cancellation

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

### Set Timeouts

```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()

result, err := slowOperation(ctx)
```

---

## Concurrency

### Worker Pool

```go
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

### WaitGroup

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

### Mutex for Shared State

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

### Constructor with Functional Options

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

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) {
        s.timeout = d
    }
}

// Usage
server := NewServer(":8080", WithTimeout(10*time.Second))
```

### Embedding for Composition

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

## Test Helpers

```go
func TestHandler(t *testing.T) {
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

---

## Time Mocking

```go
import "github.com/jonboulle/clockwork"

type Service struct {
    clock clockwork.Clock
}

func (s *Service) IsExpired(createdAt time.Time) bool {
    return s.clock.Now().Sub(createdAt) > 24*time.Hour
}

// In tests
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

## Common Mistakes

### Nil Slice vs Empty Slice

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

### Loop Variable in Goroutine

```go
// BAD - all goroutines share same i
for i := range items {
    go func() {
        process(items[i]) // Bug: i changes
    }()
}

// GOOD - capture value
for i := range items {
    go func(i int) {
        process(items[i])
    }(i)
}

// Go 1.22+ - loop variables are per-iteration (safe)
for i := range items {
    go func() {
        process(items[i]) // Safe in Go 1.22+
    }()
}
```

### Deferred Function Arguments

```go
// BAD - argument evaluated immediately
for _, f := range files {
    defer f.Close() // Bug: all close same file
}

// GOOD - use closure
for _, f := range files {
    defer func(file *os.File) {
        file.Close()
    }(f)
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

## See Also

- `go-rules.md` - Standards checklist
