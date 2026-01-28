<!--
Load: On /sdlc-studio test-env or /sdlc-studio test-env help
Dependencies: SKILL.md (always loaded first)
Related: reference-test-automation.md (test workflows), templates/docker-compose.test.template
-->

# /sdlc-studio test-env - Test Environment Setup

Generate and manage containerised test environments for integration and E2E testing.

## Quick Reference

```bash
/sdlc-studio test-env setup             # Generate docker-compose.test.yml
/sdlc-studio test-env up                # Start test environment
/sdlc-studio test-env down              # Stop test environment
/sdlc-studio test-env status            # Check environment health
```

## Purpose

Containerised test environments provide:

- **Consistent testing** - Same environment for all developers
- **Isolated services** - Database, cache, queues without local installation
- **Repeatable tests** - Fresh state for each test run
- **CI/CD ready** - Same compose file works in pipelines

## Actions

### setup

Generate docker-compose.test.yml from TRD.

**Prerequisites:** TRD must exist with Technology Stack section

**What happens:**

1. Reads TRD Technology Stack section
2. Identifies services needing containers (database, cache, etc.)
3. Generates docker-compose.test.yml with:
   - Database service with health checks
   - Cache service if applicable
   - Application service (test target)
   - Test runner service
4. Creates `.env.test` template

**Generated services:**

| Service | Purpose | Health Check |
|---------|---------|--------------|
| db | Integration test database | pg_isready / mysqladmin ping |
| redis | Cache for integration tests | redis-cli ping |
| app | Application under test | HTTP health endpoint |
| test-runner | Executes test suite | N/A |

### up

Start the test environment.

**What happens:**

1. Validates docker-compose.test.yml exists
2. Runs `docker compose -f docker-compose.test.yml up -d`
3. Waits for health checks to pass
4. Reports service status

### down

Stop the test environment.

**What happens:**

1. Runs `docker compose -f docker-compose.test.yml down -v`
2. Removes containers and volumes
3. Reports cleanup status

### status

Check test environment health.

**What happens:**

1. Checks each service status
2. Reports health check results
3. Shows container logs if unhealthy

## Output

**Files:**

- `docker-compose.test.yml` - Test environment definition
- `.env.test` - Environment variables template

**Example docker-compose.test.yml:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: test_db
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test_user -d test_db"]
      interval: 5s
      timeout: 3s
      retries: 5
    ports:
      - "5433:5432"

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    ports:
      - "6380:6379"

  app:
    build:
      context: .
      target: development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://test_user:test_pass@db:5432/test_db
      REDIS_URL: redis://redis:6379
    ports:
      - "8001:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  test-runner:
    build:
      context: .
      target: test
    depends_on:
      app:
        condition: service_healthy
    environment:
      APP_URL: http://app:8000
      DATABASE_URL: postgresql://test_user:test_pass@db:5432/test_db
    command: pytest tests/ -v
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--force` | Overwrite existing files | false |
| `--services` | Specific services to include | auto-detect from TRD |

## Integration with Code Commands

### Running Tests Against Containers

```bash
# Start environment
/sdlc-studio test-env up

# Run tests against containerised services
/sdlc-studio code test --env docker

# Stop environment
/sdlc-studio test-env down
```

### CI/CD Usage

```yaml
# GitHub Actions example
jobs:
  test:
    steps:
      - uses: actions/checkout@v4
      - name: Start test environment
        run: docker compose -f docker-compose.test.yml up -d --wait
      - name: Run tests
        run: docker compose -f docker-compose.test.yml run test-runner
      - name: Stop environment
        run: docker compose -f docker-compose.test.yml down -v
```

## Examples

```bash
# Generate test environment from TRD
/sdlc-studio test-env setup

# Start environment
/sdlc-studio test-env up

# Check status
/sdlc-studio test-env status

# Run integration tests
/sdlc-studio code test --type integration --env docker

# Stop and cleanup
/sdlc-studio test-env down
```

## Service Detection

Services are detected from TRD Technology Stack:

| TRD Entry | Generated Service |
|-----------|-------------------|
| PostgreSQL | postgres:16-alpine |
| MySQL | mysql:8 |
| Redis | redis:7-alpine |
| MongoDB | mongo:7 |
| RabbitMQ | rabbitmq:3-management-alpine |
| Elasticsearch | elasticsearch:8 |

## Next Steps

After setup:

```bash
/sdlc-studio test-env up              # Start environment
/sdlc-studio code test --env docker   # Run tests
```

## See Also

- `reference-test-automation.md` - Test workflows including containerised testing
- `/sdlc-studio trd help` - TRD with container design
- `/sdlc-studio code test help` - Running tests
