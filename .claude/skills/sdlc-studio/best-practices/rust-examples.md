# Rust Examples

Code patterns and snippets for Rust.

---

## Error Handling with Result

### Custom Error Types (thiserror)

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("not found: {0}")]
    NotFound(String),

    #[error("invalid input: {0}")]
    InvalidInput(String),

    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("parse error: {0}")]
    Parse(#[from] serde_json::Error),
}
```

### Error Propagation

```rust
fn read_config(path: &str) -> Result<Config, AppError> {
    let content = std::fs::read_to_string(path)?;  // ? propagates io::Error
    let config: Config = serde_json::from_str(&content)?;  // ? propagates parse error
    Ok(config)
}
```

### Handling Multiple Error Types

```rust
fn process(path: &str) -> Result<Output, AppError> {
    let file = std::fs::File::open(path)
        .map_err(|e| AppError::NotFound(format!("{}: {}", path, e)))?;

    // Continue processing...
    Ok(output)
}
```

---

## Option Patterns

### Common Methods

```rust
// Get with default
let name = user.nickname.unwrap_or("Anonymous".to_string());
let name = user.nickname.unwrap_or_default();  // Uses Default trait

// Transform if Some
let upper = name.map(|n| n.to_uppercase());

// Chain operations
let email = user
    .profile
    .as_ref()
    .and_then(|p| p.email.as_ref())
    .cloned();
```

### Converting Between Option and Result

```rust
// Option to Result
let user = users.get(&id).ok_or(AppError::NotFound(id.clone()))?;

// Result to Option (discards error)
let maybe_config = load_config().ok();
```

---

## Ownership and Borrowing

### Function Parameters

```rust
// GOOD - borrows, doesn't take ownership
fn process(data: &str) -> usize {
    data.len()
}

// GOOD - accepts String or &str
fn process(data: impl AsRef<str>) -> usize {
    data.as_ref().len()
}

// BAD - takes ownership unnecessarily
fn process(data: String) -> usize {
    data.len()
}
```

### Cow for Conditional Ownership

```rust
use std::borrow::Cow;

fn normalise(input: &str) -> Cow<str> {
    if input.contains(' ') {
        Cow::Owned(input.replace(' ', "_"))
    } else {
        Cow::Borrowed(input)  // No allocation
    }
}
```

---

## Struct Patterns

### Builder Pattern

```rust
#[derive(Default)]
pub struct RequestBuilder {
    url: String,
    headers: Vec<(String, String)>,
    timeout: Option<Duration>,
}

impl RequestBuilder {
    pub fn new(url: impl Into<String>) -> Self {
        Self {
            url: url.into(),
            ..Default::default()
        }
    }

    pub fn header(mut self, key: &str, value: &str) -> Self {
        self.headers.push((key.to_string(), value.to_string()));
        self
    }

    pub fn timeout(mut self, duration: Duration) -> Self {
        self.timeout = Some(duration);
        self
    }

    pub fn build(self) -> Request {
        Request {
            url: self.url,
            headers: self.headers,
            timeout: self.timeout.unwrap_or(Duration::from_secs(30)),
        }
    }
}

// Usage
let request = RequestBuilder::new("https://api.example.com")
    .header("Authorization", "Bearer token")
    .timeout(Duration::from_secs(10))
    .build();
```

### Newtype Pattern

```rust
// Type safety for IDs
pub struct UserId(String);
pub struct OrderId(String);

impl UserId {
    pub fn new(id: impl Into<String>) -> Self {
        Self(id.into())
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

// Can't accidentally pass OrderId where UserId expected
fn get_user(id: &UserId) -> Result<User, AppError> { ... }
```

---

## Iteration Patterns

### Iterator Adapters

```rust
let active_users: Vec<_> = users
    .iter()
    .filter(|u| u.is_active)
    .map(|u| &u.name)
    .collect();

// Find first match
let admin = users.iter().find(|u| u.role == Role::Admin);

// Check existence
let has_admin = users.iter().any(|u| u.role == Role::Admin);

// All match condition
let all_verified = users.iter().all(|u| u.verified);
```

### Collecting into Different Types

```rust
// Into HashMap
let user_map: HashMap<String, User> = users
    .into_iter()
    .map(|u| (u.id.clone(), u))
    .collect();

// With Result - fails on first error
let parsed: Result<Vec<i32>, _> = strings
    .iter()
    .map(|s| s.parse())
    .collect();
```

---

## Async Patterns

### Basic Async Function

```rust
async fn fetch_user(id: &str) -> Result<User, AppError> {
    let response = reqwest::get(&format!("https://api.example.com/users/{}", id))
        .await?
        .error_for_status()?;

    let user = response.json::<User>().await?;
    Ok(user)
}
```

### Concurrent Execution

```rust
use tokio::join;

async fn fetch_all(user_id: &str) -> Result<(User, Vec<Order>), AppError> {
    let (user, orders) = join!(
        fetch_user(user_id),
        fetch_orders(user_id)
    );

    Ok((user?, orders?))
}
```

### Timeout

```rust
use tokio::time::{timeout, Duration};

async fn fetch_with_timeout(url: &str) -> Result<String, AppError> {
    let result = timeout(
        Duration::from_secs(5),
        reqwest::get(url)
    ).await??;

    Ok(result.text().await?)
}
```

---

## Testing

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add_positive() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_parse_valid() {
        let result = parse_config("key=value");
        assert!(result.is_ok());
        assert_eq!(result.unwrap().key, "value");
    }

    #[test]
    fn test_parse_invalid() {
        let result = parse_config("invalid");
        assert!(matches!(result, Err(AppError::InvalidInput(_))));
    }

    #[test]
    #[should_panic(expected = "empty input")]
    fn test_panics_on_empty() {
        process_required("");
    }
}
```

### Test Fixtures

```rust
#[cfg(test)]
mod tests {
    use super::*;

    fn sample_user() -> User {
        User {
            id: "test-id".to_string(),
            name: "Test User".to_string(),
            email: "test@example.com".to_string(),
        }
    }

    #[test]
    fn test_user_display() {
        let user = sample_user();
        assert_eq!(user.display_name(), "Test User");
    }
}
```

---

## Documentation Comments

```rust
/// Processes the input and returns the result.
///
/// # Arguments
///
/// * `input` - The string to process
///
/// # Returns
///
/// The processed output, or an error if processing fails.
///
/// # Errors
///
/// Returns `AppError::InvalidInput` if the input is empty.
///
/// # Examples
///
/// ```
/// # use mylib::process;
/// let result = process("hello")?;
/// assert_eq!(result, "HELLO");
/// # Ok::<(), mylib::AppError>(())
/// ```
pub fn process(input: &str) -> Result<String, AppError> {
    if input.is_empty() {
        return Err(AppError::InvalidInput("empty input".to_string()));
    }
    Ok(input.to_uppercase())
}
```

---

## See Also

- `rust-rules.md` - Standards checklist
