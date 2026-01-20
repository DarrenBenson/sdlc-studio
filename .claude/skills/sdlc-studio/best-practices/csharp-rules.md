# C# Rules

Standards checklist for C# code.

---

## Nullable Reference Types

- [ ] Enable `<Nullable>enable</Nullable>` in csproj
- [ ] Annotate nullable types with `?`
- [ ] No `null!` without documented reason
- [ ] Handle nullable returns explicitly
- [ ] Use null-conditional (`?.`) and null-coalescing (`??`)

## Async/Await

- [ ] Return `Task` or `Task<T>` from async methods
- [ ] Suffix async methods with `Async`
- [ ] Use `ConfigureAwait(false)` in library code
- [ ] Never use `async void` except for event handlers
- [ ] Handle cancellation with `CancellationToken`

## Error Handling

- [ ] Catch specific exceptions, not `Exception`
- [ ] Use custom exception types for domain errors
- [ ] Never swallow exceptions silently
- [ ] Include context in exception messages
- [ ] Use `ExceptionDispatchInfo` when rethrowing

## Resource Management

- [ ] Use `using` statements for `IDisposable`
- [ ] Implement `IAsyncDisposable` for async cleanup
- [ ] Use `await using` for async disposables
- [ ] Don't dispose objects you don't own

## LINQ

- [ ] Prefer method syntax for complex queries
- [ ] Use `Any()` instead of `Count() > 0`
- [ ] Be aware of deferred execution
- [ ] Materialise early if iterating multiple times
- [ ] Avoid LINQ in hot paths - profile first

## Collections

- [ ] Use `IReadOnlyList<T>` for read-only returns
- [ ] Use `IEnumerable<T>` for lazy enumeration
- [ ] Prefer `List<T>` over `ArrayList`
- [ ] Use `Dictionary<K,V>` for key lookups
- [ ] Consider `Span<T>` for high-performance scenarios

## Testing

- [ ] Use xUnit, NUnit, or MSTest
- [ ] One assertion per test (when practical)
- [ ] Use Theory/TestCase for parameterised tests
- [ ] Mock dependencies with Moq or NSubstitute
- [ ] Test edge cases and error paths

## Naming Conventions

- [ ] `PascalCase` for public members, types, namespaces
- [ ] `_camelCase` for private fields
- [ ] `camelCase` for parameters and locals
- [ ] Prefix interfaces with `I`
- [ ] Suffix async methods with `Async`

---

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `async void` | Unhandled exceptions | Return `Task` |
| `catch (Exception) { }` | Hides bugs | Catch specific or log |
| `.Result` or `.Wait()` | Deadlocks | Use `await` |
| `Count() > 0` | Iterates entire collection | Use `Any()` |
| `string + string` in loops | Allocations | Use `StringBuilder` |
| `null!` everywhere | Defeats null safety | Fix the nullability |
| No `using` for streams | Resource leak | Wrap in `using` |
| `public` fields | No encapsulation | Use properties |

---

## .csproj Best Practices

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
  </PropertyGroup>
</Project>
```

---

## Required Tools

| Tool | Purpose |
|------|---------|
| dotnet format | Code formatting |
| .NET Analyzers | Static analysis |
| StyleCop.Analyzers | Style enforcement |
| xUnit/NUnit | Testing |
| Moq/NSubstitute | Mocking |

---

## See Also

- `csharp-examples.md` - Code patterns and snippets
