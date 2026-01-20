# TypeScript Examples

Code patterns and snippets for TypeScript.

---

## Type Definitions

### Interface vs Type

```typescript
// Use interface for object shapes
interface User {
  id: string;
  name: string;
  email: string;
}

// Use type for unions, intersections, utilities
type Status = 'pending' | 'active' | 'completed';
type UserWithRole = User & { role: string };
type PartialUser = Partial<User>;
```

### Readonly Properties

```typescript
interface Config {
  readonly apiUrl: string;
  readonly maxRetries: number;
}

// Arrays
const items: readonly string[] = ['a', 'b', 'c'];
// or
const items: ReadonlyArray<string> = ['a', 'b', 'c'];
```

---

## Null Safety

### Optional Chaining and Nullish Coalescing

```typescript
// GOOD - safe access
const name = user?.profile?.name ?? 'Unknown';
const count = response.data?.items?.length ?? 0;

// BAD - crashes if undefined
const name = user.profile.name;
```

### Type Guards

```typescript
function isUser(obj: unknown): obj is User {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj
  );
}

// Usage
if (isUser(data)) {
  console.log(data.name); // TypeScript knows data is User
}
```

### Discriminated Unions

```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string };

function handleResult<T>(result: Result<T>) {
  if (result.success) {
    console.log(result.data); // TypeScript knows data exists
  } else {
    console.error(result.error); // TypeScript knows error exists
  }
}
```

---

## Async Operations

### Typed Async Functions

```typescript
interface ApiResponse<T> {
  data: T;
  status: number;
}

async function fetchUser(id: string): Promise<ApiResponse<User>> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}
```

### Cancellable Fetch

```typescript
async function fetchWithTimeout<T>(
  url: string,
  timeout = 5000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timed out');
    }
    throw error;
  }
}
```

---

## Error Handling

### Custom Error Classes

```typescript
class ValidationError extends Error {
  constructor(
    public readonly field: string,
    message: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

class ApiError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
```

### Typed Catch Blocks

```typescript
try {
  await submitForm(data);
} catch (error: unknown) {
  if (error instanceof ValidationError) {
    showFieldError(error.field, error.message);
  } else if (error instanceof ApiError) {
    showNotification(`API Error: ${error.statusCode}`);
  } else if (error instanceof Error) {
    showNotification(error.message);
  } else {
    showNotification('An unexpected error occurred');
  }
}
```

---

## API Types

### Response Types

```typescript
// Define what the API actually returns
interface ApiUser {
  id: number;
  username: string;
  created_at: string; // API returns string, not Date
}

// Transform to frontend types
interface User {
  id: number;
  username: string;
  createdAt: Date;
}

function transformUser(api: ApiUser): User {
  return {
    id: api.id,
    username: api.username,
    createdAt: new Date(api.created_at),
  };
}
```

### Derived Types

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  password: string;
  createdAt: Date;
}

// Pick specific fields
type PublicUser = Pick<User, 'id' | 'name'>;

// Omit sensitive fields
type SafeUser = Omit<User, 'password'>;

// Make all optional for updates
type UserUpdate = Partial<Omit<User, 'id' | 'createdAt'>>;
```

---

## Generic Patterns

### Generic Functions

```typescript
function getFirst<T>(items: T[]): T | undefined {
  return items[0];
}

function groupBy<T, K extends keyof T>(
  items: T[],
  key: K
): Map<T[K], T[]> {
  const map = new Map<T[K], T[]>();
  for (const item of items) {
    const keyValue = item[key];
    const group = map.get(keyValue) ?? [];
    group.push(item);
    map.set(keyValue, group);
  }
  return map;
}
```

### Generic Components (React)

```typescript
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map(item => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}
```

---

## Testing Patterns

### Typed Mocks

```typescript
import { vi, type MockedFunction } from 'vitest';

const mockFetch: MockedFunction<typeof fetch> = vi.fn();

mockFetch.mockResolvedValue({
  ok: true,
  json: () => Promise.resolve({ id: 1, name: 'Test' }),
} as Response);
```

### Type-Safe Test Fixtures

```typescript
function createUser(overrides: Partial<User> = {}): User {
  return {
    id: 'test-id',
    name: 'Test User',
    email: 'test@example.com',
    ...overrides,
  };
}

test('user display name', () => {
  const user = createUser({ name: 'Custom Name' });
  expect(getDisplayName(user)).toBe('Custom Name');
});
```

---

## Runtime Validation with Zod

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().int().positive().optional(),
});

type User = z.infer<typeof UserSchema>;

function parseUser(data: unknown): User {
  return UserSchema.parse(data);
}

function safeParseUser(data: unknown): Result<User> {
  const result = UserSchema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, error: result.error.message };
}
```

---

## Import Organisation

```typescript
// 1. External libraries
import { useState, useEffect } from 'react';
import { z } from 'zod';

// 2. Internal modules
import { api } from '@/lib/api';
import { formatDate } from '@/utils/date';

// 3. Types (using type-only imports)
import type { User, ApiResponse } from '@/types';
```

---

## See Also

- `typescript-rules.md` - Standards checklist
- `javascript-examples.md` - JS patterns (applies to TS)
