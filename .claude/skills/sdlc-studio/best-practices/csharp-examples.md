# C# Examples

Code patterns and snippets for C#.

---

## Nullable Reference Types

### Declaring Nullable Types

```csharp
// Non-nullable (default with <Nullable>enable</Nullable>)
string name;           // Must not be null
User user;             // Must not be null

// Nullable
string? nickname;      // May be null
User? cachedUser;      // May be null
```

### Null Handling

```csharp
// Null-conditional and null-coalescing
string displayName = user?.Profile?.DisplayName ?? "Anonymous";
int itemCount = order?.Items?.Count ?? 0;

// Null-forgiving (only when you're certain)
string id = GetIdFromCache()!;  // Document why this is safe

// Pattern matching
if (user is { Profile: { Email: var email } })
{
    SendEmail(email);
}

// Null checks
if (user is not null)
{
    Process(user);
}
```

---

## Async/Await

### Basic Pattern

```csharp
public async Task<User> GetUserAsync(string id, CancellationToken ct = default)
{
    var response = await _httpClient.GetAsync($"/users/{id}", ct);
    response.EnsureSuccessStatusCode();

    return await response.Content.ReadFromJsonAsync<User>(ct)
        ?? throw new InvalidOperationException("Null response");
}
```

### Cancellation

```csharp
public async Task ProcessItemsAsync(
    IEnumerable<Item> items,
    CancellationToken ct)
{
    foreach (var item in items)
    {
        ct.ThrowIfCancellationRequested();
        await ProcessItemAsync(item, ct);
    }
}
```

### Parallel Execution

```csharp
public async Task<(User User, Order[] Orders)> GetUserDataAsync(
    string userId,
    CancellationToken ct)
{
    var userTask = GetUserAsync(userId, ct);
    var ordersTask = GetOrdersAsync(userId, ct);

    await Task.WhenAll(userTask, ordersTask);

    return (await userTask, await ordersTask);
}
```

### Library Code (ConfigureAwait)

```csharp
// In library code, use ConfigureAwait(false)
public async Task<string> FetchDataAsync(string url)
{
    var response = await _client.GetAsync(url).ConfigureAwait(false);
    return await response.Content.ReadAsStringAsync().ConfigureAwait(false);
}
```

---

## Exception Handling

### Custom Exceptions

```csharp
public class DomainException : Exception
{
    public string Code { get; }

    public DomainException(string code, string message)
        : base(message)
    {
        Code = code;
    }

    public DomainException(string code, string message, Exception inner)
        : base(message, inner)
    {
        Code = code;
    }
}

public class NotFoundException : DomainException
{
    public NotFoundException(string entityType, string id)
        : base("NOT_FOUND", $"{entityType} with ID '{id}' not found")
    { }
}
```

### Catching Specific Exceptions

```csharp
try
{
    await ProcessOrderAsync(order);
}
catch (NotFoundException ex)
{
    _logger.LogWarning("Order not found: {Message}", ex.Message);
    return NotFound(ex.Message);
}
catch (ValidationException ex)
{
    _logger.LogWarning("Validation failed: {Message}", ex.Message);
    return BadRequest(ex.Message);
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.ServiceUnavailable)
{
    _logger.LogError(ex, "Service unavailable, will retry");
    throw new RetryableException("Service temporarily unavailable", ex);
}
```

---

## Resource Management

### Using Statement

```csharp
// Modern using declaration
using var stream = File.OpenRead(path);
using var reader = new StreamReader(stream);
var content = await reader.ReadToEndAsync();

// Traditional using block (when scope needs limiting)
using (var connection = new SqlConnection(connectionString))
{
    await connection.OpenAsync();
    // Use connection
}  // Disposed here
```

### Async Disposal

```csharp
public class DataProcessor : IAsyncDisposable
{
    private readonly HttpClient _client = new();

    public async ValueTask DisposeAsync()
    {
        _client.Dispose();
        await Task.CompletedTask; // Or actual async cleanup
    }
}

// Usage
await using var processor = new DataProcessor();
await processor.ProcessAsync();
```

---

## LINQ Patterns

### Method Syntax

```csharp
var activeUsers = users
    .Where(u => u.IsActive)
    .OrderBy(u => u.Name)
    .Select(u => new UserDto(u.Id, u.Name))
    .ToList();

// Check existence (prefer Any over Count)
bool hasAdmins = users.Any(u => u.Role == Role.Admin);

// Find single item
var admin = users.FirstOrDefault(u => u.Role == Role.Admin);
```

### Deferred Execution

```csharp
// CAREFUL: query executes on each iteration
var query = users.Where(u => u.IsActive);
foreach (var user in query) { }  // Executes here
foreach (var user in query) { }  // Executes AGAIN

// BETTER: materialise if iterating multiple times
var activeUsers = users.Where(u => u.IsActive).ToList();
foreach (var user in activeUsers) { }
foreach (var user in activeUsers) { }
```

### GroupBy

```csharp
var usersByRole = users
    .GroupBy(u => u.Role)
    .ToDictionary(
        g => g.Key,
        g => g.ToList()
    );
```

---

## Record Types

### Immutable Data

```csharp
// Positional record
public record User(string Id, string Name, string Email);

// Record with body
public record Order
{
    public required string Id { get; init; }
    public required string CustomerId { get; init; }
    public required IReadOnlyList<OrderItem> Items { get; init; }
    public decimal Total => Items.Sum(i => i.Price * i.Quantity);
}

// With-expression for copies
var updated = user with { Name = "New Name" };
```

---

## Dependency Injection

### Service Registration

```csharp
// In Program.cs or Startup.cs
services.AddScoped<IUserService, UserService>();
services.AddSingleton<ICache, MemoryCache>();
services.AddTransient<IEmailSender, SmtpEmailSender>();

services.AddHttpClient<IApiClient, ApiClient>(client =>
{
    client.BaseAddress = new Uri("https://api.example.com");
    client.Timeout = TimeSpan.FromSeconds(30);
});
```

### Constructor Injection

```csharp
public class OrderService
{
    private readonly IUserService _userService;
    private readonly IOrderRepository _repository;
    private readonly ILogger<OrderService> _logger;

    public OrderService(
        IUserService userService,
        IOrderRepository repository,
        ILogger<OrderService> logger)
    {
        _userService = userService;
        _repository = repository;
        _logger = logger;
    }
}
```

---

## Testing with xUnit

### Basic Test

```csharp
public class CalculatorTests
{
    [Fact]
    public void Add_PositiveNumbers_ReturnsSum()
    {
        var calculator = new Calculator();

        var result = calculator.Add(2, 3);

        Assert.Equal(5, result);
    }
}
```

### Parameterised Tests

```csharp
public class ValidatorTests
{
    [Theory]
    [InlineData("", false)]
    [InlineData("a", false)]
    [InlineData("valid@email.com", true)]
    [InlineData("also.valid@sub.domain.com", true)]
    public void IsValidEmail_ReturnsExpected(string email, bool expected)
    {
        var result = Validator.IsValidEmail(email);
        Assert.Equal(expected, result);
    }
}
```

### Mocking with Moq

```csharp
public class UserServiceTests
{
    [Fact]
    public async Task GetUser_ReturnsUser_WhenFound()
    {
        var mockRepo = new Mock<IUserRepository>();
        mockRepo
            .Setup(r => r.GetByIdAsync("123"))
            .ReturnsAsync(new User { Id = "123", Name = "Test" });

        var service = new UserService(mockRepo.Object);

        var user = await service.GetUserAsync("123");

        Assert.NotNull(user);
        Assert.Equal("Test", user.Name);
    }
}
```

---

## File Structure

```
src/
├── MyApp.Api/
│   ├── Controllers/
│   ├── Program.cs
│   └── MyApp.Api.csproj
├── MyApp.Core/
│   ├── Services/
│   ├── Models/
│   └── MyApp.Core.csproj
└── MyApp.Infrastructure/
    ├── Repositories/
    └── MyApp.Infrastructure.csproj

tests/
├── MyApp.Core.Tests/
│   └── MyApp.Core.Tests.csproj
└── MyApp.Api.Tests/
    └── MyApp.Api.Tests.csproj
```

---

## See Also

- `csharp-rules.md` - Standards checklist
