# C# Best Practices

Standards and patterns for modern C# (.NET 8+).

---

## Nullable Reference Types

Enable project-wide in the `.csproj`:

```xml
<Nullable>enable</Nullable>
<TreatWarningsAsErrors>true</TreatWarningsAsErrors>
```

```csharp
// Bad - silences the compiler instead of handling absence
var name = user!.Name;

// Good - handle the null path explicitly
var name = user?.Name ?? "anonymous";
```

**Why:** With nullability enforced as errors, the compiler proves null
safety; every `!` is a suppressed warning that needs justifying.

---

## Records for Data

```csharp
// Good - immutable, value equality, with-expressions
public record Order(string Id, IReadOnlyList<Item> Items);

var updated = order with { Items = newItems };
```

Use `readonly record struct` for small, allocation-sensitive values.

**Why:** Records remove equality/copy boilerplate and make data flow
explicit through non-destructive mutation.

---

## Async Discipline

```csharp
// Bad - async void loses exceptions; only valid for event handlers
public async void SaveAsync() { ... }

// Bad - sync-over-async deadlocks under a synchronisation context
var result = client.GetAsync(url).Result;

// Good - async all the way, with cancellation
public async Task<Order> LoadAsync(string id, CancellationToken ct)
{
    var response = await client.GetAsync(Url(id), ct);
    return await Parse(response, ct);
}
```

- Accept a `CancellationToken` on every public async API and pass it down.
- Suffix async methods with `Async`.
- Library code: `ConfigureAwait(false)`; application code: omit it.

**Why:** `.Result`/`.Wait()` block threads and deadlock; tokens let
callers abandon work instead of waiting on it.

---

## Pattern Matching for State

```csharp
public abstract record JobState;
public sealed record Running(DateTimeOffset Since) : JobState;
public sealed record Succeeded(Output Output) : JobState;
public sealed record Failed(Exception Cause) : JobState;

var label = state switch
{
    Running r => $"running since {r.Since}",
    Succeeded => "done",
    Failed f => $"failed: {f.Cause.Message}",
    _ => throw new UnreachableException(),
};
```

**Why:** One variant per real state plus an exhaustive `switch`
expression keeps every state handled and visible.

---

## Exceptions

- Throw specific types; never `throw new Exception(...)`.
- Preserve the stack: `throw;` not `throw ex;` when rethrowing.
- Include context in messages: which entity, which operation.

```csharp
catch (HttpRequestException e)
{
    throw new SyncException($"sync failed for order {id}", e);
}
```

---

## Resources

```csharp
// Good - using declaration disposes at scope exit
await using var conn = await dataSource.OpenConnectionAsync(ct);
using var reader = new StreamReader(path);
```

Prefer `await using` for `IAsyncDisposable`. A type owning a disposable
field implements `IDisposable` itself.

---

## Dependency Injection

Constructor injection with `readonly` fields; register against
interfaces:

```csharp
public sealed class PaymentService(IPaymentGateway gateway)
{
    public Task ChargeAsync(Order order, CancellationToken ct)
        => gateway.ChargeAsync(order.Total, ct);
}
```

**Why:** Primary constructors keep the wiring terse while dependencies
stay explicit and mockable; service-locator calls (`GetService` inside
methods) hide them.

---

## LINQ Judiciously

```csharp
// Good - transform-filter-collect
var names = users.Where(u => u.Active).Select(u => u.Name).ToList();

// Bad - multiple enumeration of a lazy query
var active = users.Where(u => u.Active);
if (active.Any()) Process(active.First(), active.Count());
```

**Why:** Lazy queries re-execute per enumeration; materialise with
`ToList()` once when a result is used more than once. Use loops for
side effects and early exits.

---

## Testing (xUnit)

```csharp
[Theory]
[InlineData("", 1)]      // empty sku
[InlineData("SKU1", 0)]  // zero quantity
public void RejectsInvalidItems(string sku, int qty)
{
    var act = () => Item.Create(sku, qty);
    Assert.Throws<ArgumentException>(act);
}

[Fact]
public async Task LoadsOrderById()
{
    var order = await service.LoadAsync("ORD-1", TestContext.Current.CancellationToken);
    Assert.Equal("ORD-1", order.Id);
}
```

- One behaviour per test; name as `Behaviour`, not `TestMethod1`.
- `[Theory]`/`[InlineData]` for edge-case tables, mirroring the
  test-spec's AC table.
- Constructor for per-test setup, `IClassFixture<T>` for shared
  expensive state; xUnit creates a fresh class instance per test.
- No `[Fact(Skip = "...")]` without a ticket reference.
