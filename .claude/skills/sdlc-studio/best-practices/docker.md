# Best Practices: Docker

Based on [Docker Hub CI/CD](https://www.docker.com/blog/best-practices-for-using-docker-hub-for-ci-cd/), [TestDriven.io](https://testdriven.io/blog/docker-best-practices/), [Thinksys](https://thinksys.com/devops/docker-best-practices/), and [Collabnix](https://collabnix.com/10-essential-docker-best-practices-for-python-developers-in-2025/).

## Architecture

### Image vs Data Separation

**Code belongs in the image; data belongs in volumes.**

```
# Server should contain only:
/path/to/project/
├── docker-compose.yml   # Pull config
├── .env                 # Server-specific secrets
└── data/                # Volume-mounted data
```

**Never deploy by copying source code to servers.** Instead:
1. Build image in CI/CD
2. Push to container registry (GHCR, Docker Hub)
3. Server pulls image and runs

### Deployment Flow

```
git push → CI builds image → Push to registry → Server pulls → docker compose up
```

## Dockerfile

### Base Image Selection

| Image | Size | Use When |
|-------|------|----------|
| `python:3.11-slim` | ~130MB | Default choice |
| `python:3.11-alpine` | ~52MB | Size critical, no C extensions |
| `python:3.11` | ~1GB | Need build tools at runtime |

**Prefer `-slim` over Alpine** - Alpine requires extra work for C extensions and can increase build times.

### Multi-Stage Builds

Separate build dependencies from runtime:

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "app.py"]
```

### Layer Caching

Order from least to most frequently changed:

```dockerfile
# Good: dependencies before code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# Bad: cache invalidated on every code change
COPY . .
RUN pip install -r requirements.txt
```

### Security

**Run as non-root user:**

```dockerfile
RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false \
    --disabled-password --uid 1001 --system --group app
USER app
```

**Never embed secrets in images.** Use:
- Environment variables via docker-compose
- Build-time arguments for non-sensitive config
- Secrets management (Docker secrets, Vault)

### Private Registry Authentication

For private registries (GHCR, ECR, etc.), store credentials in local environment:

```bash
# In ~/.bashrc or ~/.profile
export GHCR_PAT=ghp_xxxxx

# Setup script uses it to authenticate
echo "$GHCR_PAT" | docker login ghcr.io -u USERNAME --password-stdin
```

This keeps the PAT:
- Out of version control
- In one place (not scattered in Docker config)
- Easy to rotate across servers via setup scripts

### Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1
```

### Command Syntax

Use array syntax for proper signal handling:

```dockerfile
# Good: receives SIGTERM correctly
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]

# Bad: runs in shell, signals may not propagate
CMD uvicorn app:app --host 0.0.0.0
```

## Docker Compose

### Production vs Development

```yaml
# docker-compose.yml (production)
services:
  app:
    image: ghcr.io/org/app:latest  # Pull from registry
    restart: unless-stopped
    environment:
      - NODE_ENV=production

# docker-compose.override.yml (development, auto-loaded)
services:
  app:
    build: .                       # Build locally
    volumes:
      - .:/app                     # Hot reload
```

### Environment Variables

```yaml
services:
  app:
    environment:
      - API_KEY=${API_KEY}         # From .env or shell
    env_file:
      - .env                       # Load from file
```

## Container Registry

### GitHub Container Registry (GHCR)

```yaml
# .github/workflows/docker.yml
name: Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
```

### Image Tagging

| Tag | Purpose |
|-----|---------|
| `latest` | Current stable (mutable) |
| `v1.2.3` | Semantic version (immutable) |
| `sha-abc123` | Git commit (immutable, for rollback) |

**Always tag with git SHA** for rollback capability.

## Deployment

### Server Setup (One-Time)

```bash
# Create project directory
mkdir -p /path/to/project/data

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  app:
    image: ghcr.io/org/app:latest
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./data:/app/data
    env_file:
      - .env
EOF

# Create .env with secrets
echo "API_KEY=xxx" > .env
chmod 600 .env
```

### Deploy Commands

```bash
# Pull and restart
docker compose pull && docker compose up -d

# View logs
docker compose logs -f

# Rollback to specific version
docker compose pull ghcr.io/org/app:sha-abc123
docker compose up -d
```

### CI/CD Deployment

```yaml
# In GitHub Actions
- name: Deploy
  uses: appleboy/ssh-action@v1
  with:
    host: ${{ secrets.SERVER_IP }}
    username: ${{ secrets.SERVER_USER }}
    key: ${{ secrets.SSH_PRIVATE_KEY }}
    script: |
      cd /path/to/project
      docker compose pull
      docker compose up -d
      docker system prune -f
```

## .dockerignore

```
.git
.gitignore
.env
.env.*
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
node_modules
*.md
!README.md
Dockerfile
docker-compose*.yml
.github
.claude
tests
```

## Maintenance

```bash
# Remove unused images, containers, networks
docker system prune -f

# Remove all unused images (not just dangling)
docker system prune -a -f

# Check disk usage
docker system df
```

## Checklist

Before deploying:

- [ ] Using `-slim` base image (not full or Alpine unless necessary)
- [ ] Multi-stage build separates build/runtime dependencies
- [ ] Running as non-root user
- [ ] No secrets in Dockerfile or image
- [ ] HEALTHCHECK defined
- [ ] CMD uses array syntax
- [ ] .dockerignore excludes unnecessary files
- [ ] Image tagged with git SHA for rollback
- [ ] docker-compose.yml uses `image:` not `build:`
- [ ] Server only contains compose file, .env, and data volumes
