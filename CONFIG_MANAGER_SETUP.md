# Config Manager Setup - Implementation Summary

This document summarizes the implementation of the centralized configuration manager for the subscribe module.

## Deliverables

### 1. Core Module: `subscribe/config_manager.py`

A centralized configuration management system with:

- **Typed Configuration Classes:**
  - `SchedulerConfig` - Task scheduling configuration
  - `LatencyTestConfig` - Proxy testing parameters
  - `RankerConfig` - Proxy ranking/sorting settings
  - `WeComConfig` - WeCom notification settings

- **ConfigManager Class:**
  - Loads YAML files from `config/` directory
  - Exposes strongly-typed accessors for each config type
  - Implements environment variable overrides using `MODULE__KEY__SUBKEY` format
  - Provides graceful fallbacks to defaults for missing files/fields
  - Validates required fields and cron expressions
  - Singleton pattern for global access
  - Automatic type conversion for environment variables (bool, int, float, string)

- **Key Features:**
  - Logging for configuration loading and overrides
  - Cron expression validation (5-field format)
  - List/dictionary traversal for nested overrides
  - Reload capability for dynamic reloading
  - Dictionary export for serialization

### 2. Sample Configuration Files

Created in `subscribe/config/`:

#### `scheduler.yaml`
- Defines scheduled tasks with cron expressions
- Supports task-level enable/disable
- Includes sample tasks for:
  - Process subscriptions (03:05 UTC daily)
  - Refresh storage (11:05 UTC daily)
  - Collect gist (12-hour intervals, disabled by default)

#### `latency_test.yaml`
- Timeout: 5000ms (min: 1000ms)
- Concurrent tests: 10 (min: 1)
- Retries: 2 (min: 1)
- Include/exclude patterns for proxy filtering

#### `ranker.yaml`
- Algorithm: "latency" (supports: latency, location, mixed)
- Sort fields: latency, location
- Residential priority toggle
- Exclude patterns for backup proxies

#### `wecom.yaml`
- WeCom notifications support
- Webhook URL from environment variable
- Retry configuration (3 attempts, 5s delay)
- Error/success notification toggles

### 3. Comprehensive Testing

#### `subscribe/test_config_manager.py`
Test suite covering:
1. Basic configuration loading
2. Environment variable overrides
3. Type validation and defaults
4. Cron expression validation
5. Missing files handling
6. Dictionary conversion

**All tests pass successfully.**

### 4. Documentation

#### `subscribe/config/README.md`
Complete guide including:
- Configuration file specifications
- Python API usage examples
- Environment variable override examples
- Validation rules
- Error handling strategy
- Container deployment examples
- Testing instructions

### 5. Integration Example

#### `subscribe/config_usage_example.py`
Demonstrates practical usage patterns:
- Using scheduler configuration
- Integrating latency test settings
- Applying ranker logic
- Configuring notifications
- Environment override workflow

## Usage

### Basic Python Usage

```python
from config_manager import get_config_manager

manager = get_config_manager()
scheduler_config = manager.get_scheduler_config()
latency_config = manager.get_latency_test_config()
ranker_config = manager.get_ranker_config()
wecom_config = manager.get_wecom_config()
```

### Environment Variable Overrides

```bash
export SCHEDULER__ENABLED=false
export LATENCY_TEST__TIMEOUT=10000
export RANKER__ALGORITHM=location
export WECOM__ENABLED=true
export WECOM_WEBHOOK_URL=https://...
```

### Container Deployment

```dockerfile
ENV SCHEDULER__ENABLED=true
ENV LATENCY_TEST__TIMEOUT=5000
ENV RANKER__ALGORITHM=latency
ENV WECOM__ENABLED=true
ENV WECOM_WEBHOOK_URL=${WEBHOOK_URL}
```

## Validation & Error Handling

### Validation Rules

1. **Scheduler Tasks:**
   - Required: `name`, `cron`
   - Cron format: 5 space-separated fields

2. **Latency Test:**
   - Minimum timeout: 1000ms
   - Minimum concurrent: 1
   - Minimum retries: 1

3. **Ranker:**
   - Valid algorithms: "latency", "location", "mixed"

4. **WeCom:**
   - Warns if enabled but webhook URL missing

### Error Handling

- Missing files → Uses defaults
- Invalid YAML → Logs error, uses defaults
- Invalid env vars → Logs warning, skips override
- Missing required fields → Logs error, skips entry

## Integration Points

The config manager can be integrated into:

1. `subscribe/process.py` - Task orchestration
2. `subscribe/workflow.py` - Workflow execution
3. Proxy testing modules - Latency configuration
4. Storage/push modules - Notification configuration
5. Scheduled job runners - Task scheduling

## Files Created

- `/home/engine/project/subscribe/config_manager.py` - Core module
- `/home/engine/project/subscribe/config/scheduler.yaml` - Scheduler config
- `/home/engine/project/subscribe/config/latency_test.yaml` - Latency test config
- `/home/engine/project/subscribe/config/ranker.yaml` - Ranker config
- `/home/engine/project/subscribe/config/wecom.yaml` - WeCom config
- `/home/engine/project/subscribe/config/README.md` - Configuration documentation
- `/home/engine/project/subscribe/test_config_manager.py` - Comprehensive test suite
- `/home/engine/project/subscribe/config_usage_example.py` - Integration examples

## Testing Results

All tests pass:
- ✓ Basic Configuration Loading
- ✓ Environment Variable Overrides
- ✓ Type Validation and Defaults
- ✓ Cron Expression Validation
- ✓ Missing Files Handling
- ✓ Dictionary Conversion

## Next Steps

To integrate into the codebase:

1. Import `ConfigManager` in modules that need configuration
2. Use `get_config_manager()` to access configuration
3. Set environment variables for deployment-specific overrides
4. Update CI/CD workflows to pass environment variables
5. Update documentation for users

## Backward Compatibility

The existing `config.default.json` and process configuration remain unchanged. The new `ConfigManager` is additive and can be gradually adopted in the codebase.
