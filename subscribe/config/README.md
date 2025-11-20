# Configuration Manager

This directory contains YAML configuration files for the centralized config manager.

## Overview

The `ConfigManager` class loads YAML configurations and exposes strongly-typed Python accessors. It supports:

- **Environment variable overrides** using nested naming convention (e.g., `SCHEDULER__TASKS__0__ENABLED=false`)
- **Graceful fallbacks** to defaults for missing files and fields
- **Validation** of required fields and cron expressions
- **Type conversion** for environment variables (bool, int, float, string)

## Configuration Files

### scheduler.yaml
Defines scheduled tasks to execute at specified cron intervals.

**Structure:**
```yaml
enabled: true                    # Enable/disable all scheduler tasks
tasks:
  - name: "task_name"           # Task identifier
    cron: "05 03 * * *"         # Cron expression (5 fields required)
    enabled: true               # Enable/disable individual task
    script: "module:function"   # Script entry point
    params: {}                  # Task-specific parameters
```

**Required fields:** `name`, `cron` (must be valid 5-field cron expression)

### latency_test.yaml
Settings for proxy connectivity and speed testing.

**Structure:**
```yaml
enabled: true                        # Enable latency testing
timeout: 5000                        # Connection timeout (ms), min 1000
concurrent: 10                       # Number of concurrent tests, min 1
retries: 2                          # Retry attempts on failure, min 1
exclude_patterns: ["pattern1"]      # Regex patterns to exclude
include_patterns: []                # Regex patterns to include (if empty, test all)
```

### ranker.yaml
Settings for proxy ranking and sorting.

**Structure:**
```yaml
enabled: true                       # Enable ranker
algorithm: "latency"               # "latency", "location", or "mixed"
sort_by: ["latency", "location"]   # Sort fields in priority order
residential_priority: false         # Prioritize residential proxies
exclude_patterns: []               # Patterns to exclude
```

### wecom.yaml
WeCom (WeChat Work) notification configuration.

**Structure:**
```yaml
enabled: false                              # Enable WeCom notifications
webhook_url_env: "WECOM_WEBHOOK_URL"       # Environment variable name for webhook URL
retry_times: 3                              # Retry attempts, min 1
retry_delay: 5                              # Delay between retries (seconds), min 1
send_on_error: true                        # Send notification on errors
send_on_success: false                     # Send notification on success
```

**Note:** Set `enabled: true` and provide `WECOM_WEBHOOK_URL` environment variable to use.

## Usage

### Python API

```python
from config_manager import get_config_manager

# Get the config manager (singleton)
manager = get_config_manager()

# Access typed configurations
scheduler_config = manager.get_scheduler_config()
latency_config = manager.get_latency_test_config()
ranker_config = manager.get_ranker_config()
wecom_config = manager.get_wecom_config()

# Access strongly-typed data
for task in scheduler_config.tasks:
    print(f"Task: {task.name}, Cron: {task.cron}, Enabled: {task.enabled}")

print(f"Latency timeout: {latency_config.timeout}ms")

# Get all configs as dictionary
all_configs = manager.to_dict()

# Reload configurations from disk
manager.reload_configs()
```

### Environment Variable Overrides

Use nested naming convention to override specific config values:

```bash
# Disable scheduler
export SCHEDULER__ENABLED=false

# Set latency test timeout to 10 seconds
export LATENCY_TEST__TIMEOUT=10000

# Set ranker algorithm
export RANKER__ALGORITHM=location

# Disable WeCom notifications
export WECOM__ENABLED=false

# Override task in list (0-indexed)
export SCHEDULER__TASKS__0__ENABLED=false

# Enable WeCom with webhook URL
export WECOM__ENABLED=true
export WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...
```

## Validation

The config manager performs several validations:

1. **Scheduler:**
   - Validates cron expressions (must have 5 fields)
   - Checks required fields: `name`, `cron`

2. **Latency Test:**
   - Enforces minimum timeout: 1000ms
   - Enforces minimum concurrent: 1
   - Enforces minimum retries: 1

3. **Ranker:**
   - Validates algorithm: must be "latency", "location", or "mixed"

4. **WeCom:**
   - Checks for webhook URL when enabled
   - Warns if webhook environment variable not set

## Error Handling

The config manager gracefully handles:

- Missing configuration files (uses defaults)
- Invalid YAML syntax (logs error, uses defaults)
- Invalid environment variable overrides (logs warning, skips)
- Missing required fields (logs error, skips malformed entries)

## Container Deployment

For container deployments, configure via environment variables:

```dockerfile
FROM python:3.11

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV SCHEDULER__ENABLED=true
ENV LATENCY_TEST__TIMEOUT=5000
ENV RANKER__ALGORITHM=latency
ENV WECOM__ENABLED=true
ENV WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...

ENTRYPOINT ["python", "subscribe/process.py"]
```

## Testing

Run the included test script to verify configuration loading:

```bash
python subscribe/test_config_manager.py
```

This tests:
- Basic configuration loading
- Environment variable overrides
- Type validation and defaults
- Cron expression validation
- Missing files handling
- Dictionary conversion
