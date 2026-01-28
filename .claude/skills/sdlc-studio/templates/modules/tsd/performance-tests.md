<!--
Module: Performance Test Patterns
Extends: templates/core/tsd.md
Section: After Performance Testing attributes
Load: tsd create --with-perf or tsd create --full
-->

## Performance Test Implementation

### Load Testing

| Metric | Target | Tool |
|--------|--------|------|
| Response time (p50) | {{p50_target}} | {{load_tool}} |
| Response time (p95) | {{p95_target}} | {{load_tool}} |
| Throughput | {{throughput_target}} | {{load_tool}} |
| Error rate | < 1% | {{load_tool}} |

### Test Scenarios

| Scenario | Users | Duration | Ramp-up |
|----------|-------|----------|---------|
| Baseline | {{baseline_users}} | 5 min | 1 min |
| Normal load | {{normal_users}} | 15 min | 3 min |
| Peak load | {{peak_users}} | 10 min | 2 min |
| Stress test | {{stress_users}} | 5 min | 1 min |

### Tool Configuration

**k6 example:**
```javascript
export const options = {
  stages: [
    { duration: '1m', target: {{normal_users}} },
    { duration: '5m', target: {{normal_users}} },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<{{p95_target}}'],
    http_req_failed: ['rate<0.01'],
  },
};
```

### CI Integration

```yaml
performance:
  stage: test
  script:
    - k6 run --out json=results.json perf/load-test.js
  artifacts:
    paths:
      - results.json
  only:
    - main
    - /^release\/.*/
```
