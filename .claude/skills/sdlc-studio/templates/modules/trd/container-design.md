<!--
Module: Container Design
Extends: templates/core/trd.md
Section: 9.6 (after Architecture Checklist reference)
Load: trd create --with-containers or trd create --full or trd containerize
-->

## Container Design

> Generated with `/sdlc-studio trd containerize`. This section captures containerisation decisions for development and testing.

### Application Container

| Decision | Value | Rationale |
|----------|-------|-----------|
| Base Image | {{container_base_image}} | {{container_base_rationale}} |
| Build Stages | {{container_build_stages}} | {{container_stages_rationale}} |
| Exposed Ports | {{container_ports}} | {{container_ports_usage}} |
| Health Check | {{container_health_endpoint}} | Readiness/liveness probe |

### Environment Variables

| Variable | Purpose | Default | Required |
|----------|---------|---------|----------|
| {{env_var_name}} | {{env_var_purpose}} | {{env_var_default}} | {{env_var_required}} |

### Build Stages

| Stage | Purpose | Output |
|-------|---------|--------|
| base | Shared dependencies | Base layer |
| builder | Compile and bundle | /app/dist |
| development | Dev with hot reload | Running app |
| test | Test dependencies | Test runner |
| production | Minimal runtime | Final container |

### Test Environment Containers

| Service | Image | Purpose | Health Check |
|---------|-------|---------|--------------|
| db | {{test_db_image}} | Integration test database | {{test_db_healthcheck}} |
| {{test_cache_service}} | {{test_cache_image}} | Cache for integration tests | {{test_cache_healthcheck}} |
| app | Built from Dockerfile | Application under test | HTTP /health |
| test-runner | Built from Dockerfile | Executes test suite | N/A |

### Container Networking

| Network | Purpose | Services |
|---------|---------|----------|
| default | Service communication | All services |
| {{custom_network}} | {{network_purpose}} | {{network_services}} |

### Volume Mounts

| Volume | Purpose | Mount Path |
|--------|---------|------------|
| db_data | Database persistence | /var/lib/postgresql/data |
| test_results | Test output collection | /app/test-results |
| {{custom_volume}} | {{volume_purpose}} | {{volume_path}} |
