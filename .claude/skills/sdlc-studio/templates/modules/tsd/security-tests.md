<!--
Module: Security Test Patterns
Extends: templates/core/tsd.md
Section: After Security Testing attributes
Load: tsd create --with-security or tsd create --full
-->

## Security Test Implementation

### OWASP Top 10 Coverage

| Category | Test Approach | Automated |
|----------|--------------|-----------|
| Injection | Input validation tests, SQLi/XSS scanners | Yes |
| Broken Auth | Session tests, credential stuffing | Partial |
| Sensitive Data | Encryption verification, header checks | Yes |
| XXE | XML parser configuration tests | Yes |
| Broken Access | Role-based access control tests | Yes |
| Misconfig | Security header scans, default creds | Yes |
| XSS | Output encoding tests, CSP validation | Yes |
| Deserialisation | Input validation, type checking | Yes |
| Components | Dependency scanning (npm audit, pip-audit) | Yes |
| Logging | Audit log verification, PII filtering | Partial |

### Security Scanning Pipeline

```yaml
security:
  stage: test
  script:
    - npm audit --audit-level=high || true
    - pip-audit --strict || true
    - trivy image --exit-code 1 --severity HIGH,CRITICAL app:latest
```

### Authentication Tests

| Test | Description | Expected |
|------|-------------|----------|
| Invalid credentials | Wrong password | 401 Unauthorized |
| Missing token | No auth header | 401 Unauthorized |
| Expired token | Token past expiry | 401 Unauthorized |
| Insufficient scope | Valid token, wrong role | 403 Forbidden |
| Rate limiting | 100 requests/min | 429 Too Many Requests |

### Authorisation Tests

| Resource | Role | Expected |
|----------|------|----------|
| /admin/* | admin | 200 OK |
| /admin/* | user | 403 Forbidden |
| /users/{id} | owner | 200 OK |
| /users/{id} | other | 403 Forbidden |
