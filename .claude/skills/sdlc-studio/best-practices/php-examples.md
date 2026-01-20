# PHP Examples

Code patterns and snippets for PHP.

---

## Strict Types

```php
<?php

declare(strict_types=1);

// Without strict_types: "123" silently becomes 123
// With strict_types: TypeError if types don't match

function add(int $a, int $b): int
{
    return $a + $b;
}

add(1, 2);      // OK: returns 3
add("1", "2");  // TypeError in strict mode
```

---

## Type Declarations

### Function Signatures

```php
<?php

declare(strict_types=1);

// Basic types
function process(string $name, int $count): bool
{
    // ...
    return true;
}

// Nullable types
function find(string $id): ?User
{
    // Returns User or null
}

// Union types (PHP 8.0+)
function parse(string|int $value): array
{
    // ...
}

// Mixed (any type)
function handle(mixed $data): void
{
    // ...
}
```

### Class Properties

```php
<?php

declare(strict_types=1);

class User
{
    // PHP 8.0+ constructor promotion
    public function __construct(
        public readonly string $id,
        public readonly string $name,
        public ?string $email = null,
    ) {}
}

// Usage
$user = new User('123', 'John', 'john@example.com');
```

---

## Database with PDO

### Connection

```php
<?php

declare(strict_types=1);

$dsn = 'mysql:host=localhost;dbname=myapp;charset=utf8mb4';
$options = [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES => false,
];

$pdo = new PDO($dsn, $username, $password, $options);
```

### Prepared Statements

```php
<?php

// GOOD: Prepared statement (safe)
$stmt = $pdo->prepare('SELECT * FROM users WHERE id = :id');
$stmt->execute(['id' => $userId]);
$user = $stmt->fetch();

// BAD: String concatenation (SQL injection risk)
$stmt = $pdo->query("SELECT * FROM users WHERE id = '$userId'");
```

### Transactions

```php
<?php

try {
    $pdo->beginTransaction();

    $stmt = $pdo->prepare('INSERT INTO orders (user_id, total) VALUES (?, ?)');
    $stmt->execute([$userId, $total]);

    $orderId = $pdo->lastInsertId();

    $stmt = $pdo->prepare('INSERT INTO order_items (order_id, product_id) VALUES (?, ?)');
    foreach ($items as $item) {
        $stmt->execute([$orderId, $item['product_id']]);
    }

    $pdo->commit();
} catch (Exception $e) {
    $pdo->rollBack();
    throw $e;
}
```

---

## Exception Handling

### Custom Exceptions

```php
<?php

declare(strict_types=1);

class DomainException extends Exception
{
    public function __construct(
        public readonly string $code,
        string $message,
        ?Throwable $previous = null
    ) {
        parent::__construct($message, 0, $previous);
    }
}

class NotFoundException extends DomainException
{
    public function __construct(string $entity, string $id)
    {
        parent::__construct('NOT_FOUND', "{$entity} with ID '{$id}' not found");
    }
}

class ValidationException extends DomainException
{
    public function __construct(
        string $message,
        public readonly array $errors = []
    ) {
        parent::__construct('VALIDATION_ERROR', $message);
    }
}
```

### Catching Exceptions

```php
<?php

try {
    $user = $userService->find($id);
} catch (NotFoundException $e) {
    http_response_code(404);
    echo json_encode(['error' => $e->getMessage()]);
} catch (ValidationException $e) {
    http_response_code(400);
    echo json_encode(['error' => $e->getMessage(), 'errors' => $e->errors]);
} catch (Exception $e) {
    error_log($e->getMessage());
    http_response_code(500);
    echo json_encode(['error' => 'Internal server error']);
}
```

---

## Security

### Output Escaping

```php
<?php

// GOOD: Escape HTML output
echo htmlspecialchars($userInput, ENT_QUOTES, 'UTF-8');

// Helper function
function e(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
}

// Usage in templates
<p>Welcome, <?= e($user->name) ?></p>

// BAD: Direct output (XSS risk)
echo $userInput;
```

### Password Hashing

```php
<?php

// Hashing (when storing)
$hash = password_hash($password, PASSWORD_DEFAULT);

// Verifying (when authenticating)
if (password_verify($inputPassword, $storedHash)) {
    // Password correct
} else {
    // Password incorrect
}

// Check if rehash needed (algorithm updates)
if (password_needs_rehash($storedHash, PASSWORD_DEFAULT)) {
    $newHash = password_hash($inputPassword, PASSWORD_DEFAULT);
    // Update stored hash
}
```

### Input Validation

```php
<?php

declare(strict_types=1);

function validateEmail(string $email): string
{
    $filtered = filter_var($email, FILTER_VALIDATE_EMAIL);
    if ($filtered === false) {
        throw new ValidationException('Invalid email address');
    }
    return $filtered;
}

function validateInt(mixed $value, int $min = PHP_INT_MIN, int $max = PHP_INT_MAX): int
{
    $options = ['options' => ['min_range' => $min, 'max_range' => $max]];
    $filtered = filter_var($value, FILTER_VALIDATE_INT, $options);
    if ($filtered === false) {
        throw new ValidationException("Invalid integer (must be {$min}-{$max})");
    }
    return $filtered;
}
```

---

## Modern PHP Features

### Match Expression (PHP 8.0+)

```php
<?php

// Match is like switch but returns a value
$result = match ($status) {
    'pending' => 'Awaiting processing',
    'active' => 'Currently active',
    'completed' => 'Finished',
    default => 'Unknown status',
};
```

### Named Arguments (PHP 8.0+)

```php
<?php

function createUser(
    string $name,
    string $email,
    string $role = 'user',
    bool $active = true
): User {
    // ...
}

// Named arguments for clarity
$user = createUser(
    name: 'John',
    email: 'john@example.com',
    active: false,
);
```

### Attributes (PHP 8.0+)

```php
<?php

#[Attribute]
class Route
{
    public function __construct(
        public string $path,
        public string $method = 'GET'
    ) {}
}

class UserController
{
    #[Route('/users', 'GET')]
    public function index(): array
    {
        // ...
    }

    #[Route('/users/{id}', 'GET')]
    public function show(string $id): array
    {
        // ...
    }
}
```

---

## Testing with PHPUnit

### Basic Test

```php
<?php

declare(strict_types=1);

use PHPUnit\Framework\TestCase;

class CalculatorTest extends TestCase
{
    public function testAddPositiveNumbers(): void
    {
        $calculator = new Calculator();

        $result = $calculator->add(2, 3);

        $this->assertSame(5, $result);
    }
}
```

### Data Providers

```php
<?php

class ValidatorTest extends TestCase
{
    /**
     * @dataProvider emailProvider
     */
    public function testIsValidEmail(string $email, bool $expected): void
    {
        $result = Validator::isValidEmail($email);

        $this->assertSame($expected, $result);
    }

    public static function emailProvider(): array
    {
        return [
            ['', false],
            ['invalid', false],
            ['valid@example.com', true],
            ['also.valid@sub.domain.com', true],
        ];
    }
}
```

### Mocking

```php
<?php

class UserServiceTest extends TestCase
{
    public function testFindReturnsUser(): void
    {
        $mockRepo = $this->createMock(UserRepository::class);
        $mockRepo
            ->method('findById')
            ->with('123')
            ->willReturn(new User('123', 'Test'));

        $service = new UserService($mockRepo);

        $user = $service->find('123');

        $this->assertSame('Test', $user->name);
    }
}
```

---

## Directory Structure

```
project/
├── src/
│   ├── Controller/
│   ├── Service/
│   ├── Repository/
│   └── Entity/
├── tests/
│   ├── Unit/
│   └── Integration/
├── config/
├── public/
│   └── index.php
├── composer.json
└── phpunit.xml
```

---

## See Also

- `php-rules.md` - Standards checklist
