# PostgreSQL Best Practices

Guidelines for PostgreSQL implementation in SDLC Studio projects.

## Query Optimisation

### Use EXPLAIN ANALYSE

Always analyse query performance before deployment:

```sql
EXPLAIN ANALYSE SELECT * FROM users WHERE email = 'test@example.com';
```

**What to check:**

- Sequential scans on large tables (add index)
- Estimated vs actual row differences (stale statistics)
- Nested loops on large datasets (consider hash join)
- Index scans vs index-only scans

### Index Strategies

| Index Type | Use Case | Example |
|------------|----------|---------|
| B-tree (default) | Equality, range queries | `CREATE INDEX idx_user_email ON users(email)` |
| GIN | JSONB, arrays, full-text | `CREATE INDEX idx_data_gin ON items USING GIN(data)` |
| GiST | Geometric, full-text | `CREATE INDEX idx_location ON places USING GIST(location)` |
| Composite | Multi-column queries | `CREATE INDEX idx_user_status ON users(org_id, status)` |
| Partial | Filtered subsets | `CREATE INDEX idx_active ON users(email) WHERE active = true` |
| Expression | Computed values | `CREATE INDEX idx_lower_email ON users(LOWER(email))` |

**Index guidelines:**

- Index columns used in WHERE, JOIN, ORDER BY
- Put most selective column first in composite indexes
- Use partial indexes for filtered queries
- Avoid over-indexing (slows writes)

### JSONB Operations

```sql
-- Text extraction (returns text)
SELECT data->>'name' FROM items;

-- JSON extraction (returns jsonb)
SELECT data->'metadata' FROM items;

-- Containment query (uses GIN index)
SELECT * FROM items WHERE data @> '{"type": "active"}';

-- Path query (PostgreSQL 12+)
SELECT jsonb_path_query(data, '$.items[*].name') FROM orders;
```

**Index JSONB for performance:**

```sql
-- GIN index for containment queries
CREATE INDEX idx_data_gin ON items USING GIN(data);

-- Expression index for specific key
CREATE INDEX idx_data_type ON items ((data->>'type'));
```

## Connection Management

### Connection Pooling

Use connection pooling for all production deployments:

| Pooler | Use Case | Configuration |
|--------|----------|---------------|
| PgBouncer | Simple pooling | Transaction/session mode |
| pgpool-II | Load balancing + pooling | Complex setups |
| Application pool | Framework built-in | Depends on framework |

**Pool sizing formula:**

```text
connections = (core_count * 2) + effective_spindle_count
```

For most applications: 20-50 connections per pool.

### Timeouts

Set appropriate timeouts to prevent runaway queries:

```sql
-- Session-level
SET statement_timeout = '30s';
SET idle_in_transaction_session_timeout = '5min';

-- Connection string
postgresql://host/db?options=-c%20statement_timeout%3D30000
```

## Transaction Best Practices

### Keep Transactions Short

```sql
-- Bad: Long transaction blocks other operations
BEGIN;
SELECT * FROM large_table;  -- Long operation
-- ... minutes pass ...
UPDATE users SET status = 'active';
COMMIT;

-- Good: Separate transactions
SELECT * FROM large_table;  -- Read outside transaction

BEGIN;
UPDATE users SET status = 'active';
COMMIT;
```

### Isolation Levels

| Level | Use Case | Trade-off |
|-------|----------|-----------|
| Read Committed (default) | Most operations | Phantom reads possible |
| Repeatable Read | Reports, analytics | Higher lock contention |
| Serializable | Financial, critical | Highest contention, retries needed |

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- Operations here see consistent snapshot
COMMIT;
```

### Lock Management

```sql
-- Advisory locks for application-level locking
SELECT pg_advisory_lock(12345);
-- Critical section
SELECT pg_advisory_unlock(12345);

-- Try-lock with timeout
SELECT pg_try_advisory_lock(12345);
```

## Schema Design

### Table Design

```sql
-- Use UUIDs for distributed systems
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Use TIMESTAMPTZ, not TIMESTAMP
-- Use TEXT, not VARCHAR (no performance difference)
-- Always include created_at, updated_at
```

### Constraints

```sql
-- Check constraints for data validation
ALTER TABLE orders ADD CONSTRAINT positive_amount
    CHECK (amount > 0);

-- Foreign keys with appropriate actions
ALTER TABLE orders ADD CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE;

-- Exclusion constraints for ranges
ALTER TABLE bookings ADD CONSTRAINT no_overlap
    EXCLUDE USING GIST (room_id WITH =, during WITH &&);
```

## Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| `SELECT *` | Fetches unnecessary data | Specify needed columns |
| N+1 queries | Multiple roundtrips | Use JOIN or batch query |
| Missing FK indexes | Slow JOINs and CASCADE | Add indexes on FK columns |
| OFFSET pagination | Slow on large offsets | Cursor-based pagination |
| Implicit type casts | Index not used | Match types explicitly |
| Too many indexes | Slow writes | Index selectively |
| No connection pooling | Connection overhead | Use PgBouncer |

### OFFSET vs Cursor Pagination

```sql
-- Bad: OFFSET (slow on large tables)
SELECT * FROM items ORDER BY id LIMIT 20 OFFSET 10000;

-- Good: Cursor-based (consistent performance)
SELECT * FROM items WHERE id > 10000 ORDER BY id LIMIT 20;
```

## Bulk Operations

### Batch Inserts

```sql
-- Use UNNEST for bulk inserts
INSERT INTO items (name, value)
SELECT * FROM UNNEST(
    ARRAY['item1', 'item2', 'item3'],
    ARRAY[100, 200, 300]
);

-- Or COPY for large imports
COPY items (name, value) FROM '/path/to/file.csv' CSV HEADER;
```

### Bulk Updates

```sql
-- Update from values
UPDATE items AS i
SET value = v.new_value
FROM (VALUES
    (1, 100),
    (2, 200),
    (3, 300)
) AS v(id, new_value)
WHERE i.id = v.id;
```

## Monitoring

### Essential Queries

```sql
-- Active queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active';

-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Index usage
SELECT indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Unused indexes
SELECT indexrelname
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

## See Also

- `best-practices/sql.md` - General SQL patterns
- `reference-code.md` - Implementation workflow
- `reference-test-automation.md` - Database testing patterns
