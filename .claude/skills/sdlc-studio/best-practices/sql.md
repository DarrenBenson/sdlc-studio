# SQL Best Practices

General SQL patterns applicable across database systems.

## Query Structure

### Readability

Format queries for clarity:

```sql
-- Good: One clause per line, aligned keywords
SELECT
    u.id,
    u.email,
    o.total
FROM users u
INNER JOIN orders o ON o.user_id = u.id
WHERE u.status = 'active'
    AND o.created_at > '2024-01-01'
ORDER BY o.total DESC
LIMIT 100;

-- Bad: Everything on one line
SELECT u.id, u.email, o.total FROM users u INNER JOIN orders o ON o.user_id = u.id WHERE u.status = 'active' AND o.created_at > '2024-01-01' ORDER BY o.total DESC LIMIT 100;
```

### Meaningful Aliases

```sql
-- Good: Short but meaningful
SELECT
    u.email,
    o.order_number,
    p.name AS product_name
FROM users u
INNER JOIN orders o ON o.user_id = u.id
INNER JOIN products p ON p.id = o.product_id;

-- Bad: Single letters without pattern
SELECT a.email, b.order_number, c.name
FROM users a, orders b, products c;
```

## CTEs vs Subqueries

| Use CTE When | Use Subquery When |
|--------------|-------------------|
| Query reused multiple times | One-time use |
| Complex logic needs naming | Simple, inline logic |
| Need to break down steps | Performance critical |
| Recursive queries | Correlated subqueries |

### CTE Example

```sql
-- CTE: Clear, named, reusable
WITH active_users AS (
    SELECT id, email
    FROM users
    WHERE status = 'active'
),
recent_orders AS (
    SELECT user_id, COUNT(*) as order_count
    FROM orders
    WHERE created_at > CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    u.email,
    COALESCE(o.order_count, 0) as recent_orders
FROM active_users u
LEFT JOIN recent_orders o ON o.user_id = u.id;
```

### Recursive CTE

```sql
-- Hierarchical data (e.g., org chart)
WITH RECURSIVE org_tree AS (
    -- Base case: top-level
    SELECT id, name, manager_id, 1 as depth
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: subordinates
    SELECT e.id, e.name, e.manager_id, t.depth + 1
    FROM employees e
    INNER JOIN org_tree t ON t.id = e.manager_id
)
SELECT * FROM org_tree ORDER BY depth, name;
```

## JOIN Optimisation

### Filter Early

```sql
-- Good: Filter before join
SELECT u.email, o.total
FROM users u
INNER JOIN (
    SELECT user_id, total
    FROM orders
    WHERE status = 'completed'
) o ON o.user_id = u.id;

-- Or with CTE
WITH completed_orders AS (
    SELECT user_id, total
    FROM orders
    WHERE status = 'completed'
)
SELECT u.email, o.total
FROM users u
INNER JOIN completed_orders o ON o.user_id = u.id;
```

### EXISTS vs IN

```sql
-- EXISTS: Better for large subquery results
SELECT u.email
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.status = 'completed'
);

-- IN: Better for small, static lists
SELECT * FROM users
WHERE status IN ('active', 'pending');
```

### JOIN Order

Most databases optimise join order, but hints can help:

```sql
-- Put smaller tables first in FROM clause (some DBs)
-- Use EXPLAIN to verify actual execution
SELECT /*+ LEADING(small_table) */ *
FROM small_table s
INNER JOIN large_table l ON l.small_id = s.id;
```

## NULL Handling

### COALESCE for Defaults

```sql
-- Provide defaults for NULL
SELECT
    name,
    COALESCE(nickname, name) as display_name,
    COALESCE(phone, 'Not provided') as contact
FROM users;
```

### NULL-Safe Comparisons

```sql
-- Remember: NULL = NULL returns NULL, not TRUE
-- Use IS NULL / IS NOT NULL
SELECT * FROM users WHERE deleted_at IS NULL;

-- Use COALESCE for NULL-safe equality
SELECT * FROM users
WHERE COALESCE(status, 'unknown') = COALESCE(@input, 'unknown');
```

### NULLIF

```sql
-- Avoid division by zero
SELECT amount / NULLIF(quantity, 0) as unit_price
FROM line_items;
```

## Pagination Patterns

### Offset-Based (Simple)

```sql
-- Simple but slow at scale
SELECT * FROM items
ORDER BY id
LIMIT 20 OFFSET 100;
```

**Problems:**

- Scans all skipped rows
- Inconsistent if data changes
- O(n) performance

### Cursor-Based (Efficient)

```sql
-- Efficient for any page
SELECT * FROM items
WHERE id > :last_seen_id
ORDER BY id
LIMIT 20;
```

**Benefits:**

- Consistent O(1) performance
- Handles insertions/deletions
- Works with large datasets

### Keyset Pagination with Multiple Columns

```sql
-- For non-unique sort columns
SELECT * FROM items
WHERE (created_at, id) > (:last_date, :last_id)
ORDER BY created_at, id
LIMIT 20;
```

## Batch Operations

### Process in Chunks

```sql
-- Delete in batches to avoid lock contention
DELETE FROM old_logs
WHERE id IN (
    SELECT id FROM old_logs
    WHERE created_at < '2023-01-01'
    LIMIT 1000
);
-- Repeat until no rows affected
```

### Bulk Insert with Conflict Handling

```sql
-- Upsert pattern
INSERT INTO items (id, name, value)
VALUES
    (1, 'item1', 100),
    (2, 'item2', 200)
ON CONFLICT (id) DO UPDATE
SET name = EXCLUDED.name,
    value = EXCLUDED.value,
    updated_at = NOW();
```

## Aggregation

### Window Functions

```sql
-- Running totals
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM transactions;

-- Ranking
SELECT
    name,
    score,
    RANK() OVER (ORDER BY score DESC) as rank,
    DENSE_RANK() OVER (ORDER BY score DESC) as dense_rank
FROM players;

-- Partition by group
SELECT
    department,
    name,
    salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees;
```

### GROUP BY Best Practices

```sql
-- Include all non-aggregated columns
SELECT
    department,
    status,
    COUNT(*) as count,
    AVG(salary) as avg_salary
FROM employees
GROUP BY department, status;

-- Use HAVING for aggregate filters
SELECT department, COUNT(*) as count
FROM employees
GROUP BY department
HAVING COUNT(*) > 10;
```

## Date/Time

### Use UTC

```sql
-- Store in UTC, convert on display
INSERT INTO events (occurred_at)
VALUES (NOW() AT TIME ZONE 'UTC');

-- Convert for display
SELECT occurred_at AT TIME ZONE 'America/New_York' as local_time
FROM events;
```

### Date Ranges

```sql
-- Inclusive start, exclusive end
SELECT * FROM events
WHERE occurred_at >= '2024-01-01'
  AND occurred_at < '2024-02-01';

-- Or use date_trunc
SELECT * FROM events
WHERE date_trunc('month', occurred_at) = '2024-01-01';
```

## Security

### Parameterised Queries

```sql
-- ALWAYS use parameters, NEVER string concatenation
-- Bad (SQL injection vulnerability):
query = f"SELECT * FROM users WHERE email = '{email}'"

-- Good (parameterised):
query = "SELECT * FROM users WHERE email = $1"
execute(query, [email])
```

### Least Privilege

```sql
-- Create role with minimal permissions
CREATE ROLE app_reader;
GRANT SELECT ON users, orders TO app_reader;

-- Separate roles for different operations
CREATE ROLE app_writer;
GRANT INSERT, UPDATE ON users, orders TO app_writer;
```

## Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| `SELECT *` | Returns unnecessary data | List required columns |
| Implicit joins | Hard to read, error-prone | Use explicit JOIN |
| String concatenation | SQL injection | Use parameters |
| Cartesian products | Missing JOIN condition | Always specify ON clause |
| Correlated subqueries | N+1 execution | Use JOIN or CTE |
| Large IN lists | Performance, limits | Use temp table or JOIN |

## See Also

- `best-practices/postgresql.md` - PostgreSQL-specific patterns
- `reference-test-automation.md` - Database testing
- `reference-code.md` - Implementation workflow
