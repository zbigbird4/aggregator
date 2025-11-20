# Aggregator Functional Testing Environment

## Overview

This directory contains a complete functional testing environment for the aggregator project using a dataset of 100 test proxies. The test suite validates the complete workflow including:

- **Config Manager Integration**: Tests configuration management with environment variable overrides
- **Latency Tester Module**: Validates latency measurement and score computation
- **Core Workflow**: Tests proxy collection → verification → testing → ranking → output generation
- **Quality Metrics**: Assesses node filtering quality and performance characteristics

## Test Dataset

### Generated Test Proxies

The test environment includes **100 simulated proxy nodes** distributed across three quality tiers:

- **Good Quality (50%)**: Low latency (avg 80ms), minimal packet loss, high uptime
- **Medium Quality (35%)**: Moderate latency (avg 200ms), some packet loss, acceptable uptime  
- **Poor Quality (15%)**: High latency (avg 500ms), significant packet loss, lower uptime

**Geographic Distribution:**
- US (9 nodes), JP (8 nodes), various European/Asian regions
- Multiple ISPs represented (DigitalOcean, AWS, Vultr, Hetzner, etc.)
- Mix of residential and datacenter proxies

**File Location:** `/home/engine/project/tests/data/test_proxies_100.json`

## Test Structure

```
tests/
├── data/                          # Test data directory
│   ├── test_proxies_100.json     # Generated 100-proxy dataset (JSON format)
│   ├── test_proxies_100.txt      # Converted to subscription format (V2Ray links)
│   └── test_proxies_100_subscription.txt  # Base64-encoded subscription
├── config/                        # Test configuration files
│   ├── test_latency_config.yaml  # Latency tester configuration
│   ├── test_ranker_config.yaml   # Ranking strategy configuration
│   └── test_scheduler_config.yaml # Scheduler task configuration
├── output/                        # Test output directory
│   ├── verified_proxies.json     # Proxies that passed verification
│   ├── tested_proxies.json       # Proxies that passed latency testing
│   ├── final_proxies.json        # Final selected proxies (ranked)
│   ├── clash.yaml                # Generated Clash configuration
│   └── test_report.txt           # Detailed test report
├── logs/                          # Test logs
│   └── test_execution.log        # Full execution log
├── generate_test_proxies.py      # Test data generator script
├── convert_proxies_to_v2ray.py   # Format converter script
├── run_functional_test.py        # Main test runner
└── README.md                      # This file
```

## Test Execution

### Prerequisites

1. Install required dependencies:
```bash
pip install --break-system-packages -r /home/engine/project/requirements.txt
```

2. Ensure the project structure is intact:
```bash
cd /home/engine/project
```

### Running Tests

#### 1. Generate Test Data (Optional - already generated)

```bash
python3 tests/generate_test_proxies.py
```

This creates:
- `tests/data/test_proxies_100.json` - Raw proxy data
- Outputs dataset statistics

#### 2. Run Functional Test

```bash
cd /home/engine/project
python3 tests/run_functional_test.py
```

Or with logging:
```bash
python3 tests/run_functional_test.py 2>&1 | tee tests/logs/test_execution.log
```

#### 3. View Results

The test generates several output files:

- **test_report.txt** - Comprehensive test report
- **verified_proxies.json** - Verification stage results
- **tested_proxies.json** - Latency testing results
- **final_proxies.json** - Final ranked proxies
- **clash.yaml** - Generated Clash configuration

```bash
# View test report
cat tests/output/test_report.txt

# Check output proxies
jq '.[0]' tests/output/final_proxies.json

# Inspect Clash config
head -50 tests/output/clash.yaml
```

## Test Scenarios

### Scenario 1: Fast Functional Testing (Default)

**Purpose:** Quick validation of core functionality  
**Configuration:** `tests/config/test_latency_config.yaml`

- Concurrency: 20
- Timeout: 3000ms
- Retries: 1
- Expected Duration: < 1 second

**Use Case:** Quick development iteration, CI/CD pipelines

### Scenario 2: Comprehensive Testing (Extended)

To test with more aggressive settings, modify `tests/config/test_latency_config.yaml`:

```yaml
concurrent: 50         # Higher concurrency
timeout: 5000          # Longer timeout
retries: 3             # More retries
test_count: 5          # More test attempts
```

**Expected Duration:** 5-10 seconds

### Scenario 3: Real-world Simulation

For testing with actual network conditions, replace test data with real proxy sources:

```bash
# Modify test_config.json to use real subscription URLs
# Then run the actual process.py with configuration
```

## Test Metrics and Validation

### Key Performance Indicators (KPIs)

The test report includes comprehensive analysis:

**1. Data Flow Metrics**
- Total Loaded: 100 proxies
- Verification Pass Rate: ~86%
- Latency Testing Pass Rate: ~83%
- Final Output Rate: ~56% of total (~80% of tested)

**2. Quality Metrics**
- Latency Score Range: 87.8 - 98.3 (higher is better)
- Average Latency: 122ms (among output proxies)
- Residential Proxy Distribution: ~54%

**3. Performance Metrics**
- Average Time per Proxy: 0.13ms
- Throughput: ~7600+ proxies/sec
- Total Execution Time: < 1 second (for 100 proxies)

**4. Geographic Distribution**
- Coverage across 12+ countries
- Balanced distribution across regions
- Mix of US, Japan, Europe, and Asia-Pacific

### Acceptance Criteria

✓ **Functionality:** All workflow stages complete without errors  
✓ **Performance:** 100 proxies processed in < 60 seconds  
✓ **Quality:** Final output rate between 40-80% (realistic filtering)  
✓ **Latency Scores:** Consistent scoring based on metrics  
✓ **Output Format:** Valid Clash YAML generated  

## Integration Points

### Config Manager Integration

The test framework can work with the config manager:

```python
from config_manager import ConfigManager

config_mgr = ConfigManager(config_dir='/home/engine/project/tests/config')
latency_config = config_mgr.get_latency_test_config()
```

### Latency Tester Integration

The latency tester module is called during the testing phase:

```python
from latency_tester import measure, MeasurementConfig

config = MeasurementConfig(
    concurrent_limit=20,
    retry_times=1,
    max_latency=5000
)

measurements, logs = measure(proxies, config)
```

### Output Generation

Final proxies are converted to Clash YAML format for use in Clash clients:

```yaml
proxies:
  - name: SS-JP-Tokyo-1
    type: ss
    server: 45.142.0.1
    port: 443
    cipher: aes-256-gcm
    password: password

proxy-groups:
  - name: PROXY
    type: select
    proxies:
      - SS-JP-Tokyo-1
```

## Analysis and Recommendations

### Performance Analysis

**Bottleneck Assessment:**
1. **Verification Stage:** 0.2% of total time
2. **Latency Testing:** 0.7% of total time (main workload)
3. **Ranking:** 0.2% of total time
4. **Output Generation:** 71.1% of total time (I/O bound)

**Recommendations:**
- Current performance is excellent for 100 proxies
- Scale testing with 1000+ proxies to identify bottlenecks
- Consider async I/O optimization for output generation

### Quality Assessment

**Node Filtering Quality:**
- Verification captures 86% of input proxies (expected)
- Latency testing filters to 83% of verified proxies
- Final ranking selects 79% of tested proxies

**Issues Identified:** None (simulated environment)

**Recommendations:**
- Deploy with real proxy sources for live validation
- Monitor pass rates against historical baselines
- Adjust thresholds if filtering is too aggressive/lenient

### Scalability Outlook

**Projected Performance for 1000 proxies:**
- Sequential Processing: ~10 seconds
- With optimizations: ~2-3 seconds
- With distributed testing: sub-second execution

## Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError for dependencies**
```bash
# Solution: Install all requirements
pip install --break-system-packages -r requirements.txt
```

**Issue: Test data not found**
```bash
# Solution: Regenerate test data
python3 tests/generate_test_proxies.py
```

**Issue: Output files not created**
```bash
# Solution: Check permissions on output directory
mkdir -p tests/output
chmod 755 tests/output
```

**Issue: Proxy conversion fails**
```bash
# Solution: Verify JSON format is valid
python3 -m json.tool tests/data/test_proxies_100.json > /dev/null
```

## Next Steps

### Extending the Test Suite

1. **Add Real Proxy Sources:** Modify test_config.json to use actual subscriptions
2. **Integrate Live Testing:** Connect to real Clash/Mihomo binary for actual connectivity tests
3. **Performance Benchmarking:** Add memory profiling and CPU usage tracking
4. **Regression Testing:** Establish baseline metrics and monitor for regressions
5. **Load Testing:** Create datasets of 1000, 10000, 100000 proxies

### Integration with CI/CD

Add to GitHub Actions workflow:
```yaml
- name: Run Functional Tests
  run: |
    cd /home/engine/project
    python3 tests/run_functional_test.py
    
- name: Upload Test Report
  uses: actions/upload-artifact@v2
  with:
    name: test-report
    path: tests/output/test_report.txt
```

### Monitoring and Alerts

1. Track execution time trends
2. Monitor proxy pass rates over time
3. Alert if quality metrics degrade
4. Archive reports for historical analysis

## File Reference

### Key Output Files

**test_report.txt** - Main summary report with all key metrics

**final_proxies.json** - Array of selected proxies with full attributes:
```json
[
  {
    "id": "proxy_001",
    "name": "SS-JP-Tokyo-1",
    "type": "ss",
    "server": "45.142.1.1",
    "port": 443,
    "latency_ms": 45.2,
    "latency_score": 95.4,
    "location": {"country": "JP", "region": "Tokyo"},
    "is_residential": true,
    ...
  }
]
```

**clash.yaml** - Clash client configuration ready for import

## Support and Documentation

For more information:
- See `/home/engine/project/README.md` for main project documentation
- See `/home/engine/project/CONFIG_MANAGER_SETUP.md` for config manager details
- See `/home/engine/project/subscribe/latency_tester.py` for latency tester API

## Test Execution History

### Latest Run
- **Date:** 2025-11-20 01:07:25
- **Status:** ✓ PASSED
- **Execution Time:** 0.01s
- **Input Proxies:** 100
- **Output Proxies:** 56
- **Pass Rate:** 56%

---

**Last Updated:** 2025-11-20  
**Test Framework Version:** 1.0  
**Aggregator Project Version:** Latest
