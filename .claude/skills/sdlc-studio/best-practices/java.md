# Java Best Practices

Standards and patterns for modern Java (17+).

---

## Records for Data

```java
// Bad - 40 lines of boilerplate, mutable by default
public class Order {
    private String id;
    private List<Item> items;
    // getters, setters, equals, hashCode, toString...
}

// Good - immutable, value semantics for free
public record Order(String id, List<Item> items) {
    public Order {
        items = List.copyOf(items);
    }
}
```

**Why:** Records give immutability, `equals`/`hashCode`/`toString`, and a
compact constructor for validation. Defensive-copy collections in the
compact constructor to keep the record genuinely immutable.

---

## Sealed Interfaces for State

```java
public sealed interface JobState permits Running, Succeeded, Failed {}
public record Running(Instant since) implements JobState {}
public record Succeeded(Output output) implements JobState {}
public record Failed(Exception cause) implements JobState {}

// Exhaustive - adding a state breaks this switch at compile time
String label = switch (state) {
    case Running r -> "running since " + r.since();
    case Succeeded s -> "done";
    case Failed f -> "failed: " + f.cause().getMessage();
};
```

**Why:** Sealed types plus pattern-matching `switch` make illegal states
unrepresentable and missing cases a compile error.

---

## Optional Discipline

```java
// Bad - Optional as a field or parameter
void notify(Optional<String> email) { ... }

// Good - Optional only as a return type
Optional<User> findByEmail(String email);

// Good - consume with combinators, not isPresent/get
findByEmail(email)
    .map(User::displayName)
    .orElse("anonymous");
```

**Why:** `Optional` signals "may be absent" at API boundaries.
`isPresent()` followed by `get()` is a null check in disguise.

---

## Exceptions

- Throw unchecked exceptions for programming errors; reserve checked
  exceptions for recoverable conditions the caller can act on.
- Always include context: `throw new OrderNotFoundException("order %s".formatted(id), cause)`.
- Never swallow: an empty `catch` block needs a comment explaining why.

```java
// Bad - loses the original failure
catch (IOException e) {
    throw new RuntimeException("sync failed");
}

// Good - chain the cause
catch (IOException e) {
    throw new SyncException("sync failed for " + path, e);
}
```

---

## Resources

```java
// Good - try-with-resources, closes in reverse order even on failure
try (var in = Files.newInputStream(path);
     var reader = new BufferedReader(new InputStreamReader(in, UTF_8))) {
    return reader.lines().toList();
}
```

**Why:** Manual `finally` blocks leak on the unhappy path; any
`AutoCloseable` belongs in try-with-resources.

---

## Streams Judiciously

```java
// Good - linear pipeline, reads top to bottom
var names = users.stream()
    .filter(User::active)
    .map(User::name)
    .sorted()
    .toList();

// Bad - nested streams with side effects; write a loop instead
orders.forEach(o -> o.items().stream().forEach(i -> inventory.reserve(i)));
```

**Why:** Streams shine for transform-filter-collect; loops beat streams
for side effects, early exit, or anything a reader must single-step.

---

## Dependency Injection

Constructor injection only; fields `final`:

```java
// Bad - field injection hides dependencies and blocks testing
@Autowired private PaymentGateway gateway;

// Good - explicit, testable without the container
private final PaymentGateway gateway;

public PaymentService(PaymentGateway gateway) {
    this.gateway = gateway;
}
```

---

## Testing (JUnit 5)

```java
@ParameterizedTest(name = "{0}")
@CsvSource({
    "empty cart,        0,  0",
    "single item,       1, 10",
    "quantity discount, 5, 45",
})
void totals(String name, int qty, int expected) {
    assertEquals(expected, cart(qty).total());
}

@Test
void rejectsUnknownSku() {
    var ex = assertThrows(UnknownSkuException.class,
        () -> cart.add("NOPE", 1));
    assertTrue(ex.getMessage().contains("NOPE"));
}
```

- One behaviour per test; name tests after the behaviour, not the method.
- AssertJ (`assertThat(...).containsExactly(...)`) for collection-heavy
  assertions; built-in assertions otherwise.
- No `@Disabled` without a ticket reference.

**Why:** Parameterised tests keep edge cases cheap to add, mirroring the
test-spec's AC table; `assertThrows` pins both the type and the message.
