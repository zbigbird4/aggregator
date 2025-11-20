#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple test script to validate config_manager functionality.
Demonstrates:
- Loading each config
- Environment variable overrides
- Accessing strongly-typed data
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import (
    get_config_manager,
    reset_config_manager,
    ConfigManager,
    SchedulerConfig,
    LatencyTestConfig,
    RankerConfig,
    WeComConfig
)
from logger import logger


def test_basic_loading():
    """Test basic configuration loading."""
    print("\n=== Test 1: Basic Configuration Loading ===")
    
    reset_config_manager()
    manager = get_config_manager()
    
    # Load each config
    scheduler_config = manager.get_scheduler_config()
    latency_config = manager.get_latency_test_config()
    ranker_config = manager.get_ranker_config()
    wecom_config = manager.get_wecom_config()
    
    print(f"✓ Scheduler config loaded: {len(scheduler_config.tasks)} tasks")
    print(f"  - Enabled: {scheduler_config.enabled}")
    for task in scheduler_config.tasks:
        print(f"    • {task.name}: {task.cron} (enabled={task.enabled})")
    
    print(f"✓ Latency test config loaded")
    print(f"  - Timeout: {latency_config.timeout}ms")
    print(f"  - Concurrent: {latency_config.concurrent}")
    print(f"  - Retries: {latency_config.retries}")
    
    print(f"✓ Ranker config loaded")
    print(f"  - Algorithm: {ranker_config.algorithm}")
    print(f"  - Sort by: {ranker_config.sort_by}")
    print(f"  - Residential priority: {ranker_config.residential_priority}")
    
    print(f"✓ WeCom config loaded")
    print(f"  - Enabled: {wecom_config.enabled}")
    print(f"  - Webhook env var: {wecom_config.webhook_url_env}")
    print(f"  - Retry times: {wecom_config.retry_times}")
    print(f"  - Send on error: {wecom_config.send_on_error}")


def test_env_overrides():
    """Test environment variable overrides."""
    print("\n=== Test 2: Environment Variable Overrides ===")
    
    # Set environment variables for overrides
    os.environ["SCHEDULER__ENABLED"] = "false"
    os.environ["LATENCY_TEST__TIMEOUT"] = "10000"
    os.environ["LATENCY_TEST__CONCURRENT"] = "20"
    os.environ["RANKER__ALGORITHM"] = "location"
    os.environ["WECOM__ENABLED"] = "true"
    os.environ["WECOM__RETRY_TIMES"] = "5"
    
    reset_config_manager()
    manager = get_config_manager()
    
    scheduler_config = manager.get_scheduler_config()
    latency_config = manager.get_latency_test_config()
    ranker_config = manager.get_ranker_config()
    wecom_config = manager.get_wecom_config()
    
    print(f"✓ Scheduler enabled (from env): {scheduler_config.enabled}")
    assert scheduler_config.enabled == False, "Scheduler should be disabled from env"
    
    print(f"✓ Latency timeout (from env): {latency_config.timeout}ms")
    assert latency_config.timeout == 10000, "Timeout should be 10000 from env"
    
    print(f"✓ Latency concurrent (from env): {latency_config.concurrent}")
    assert latency_config.concurrent == 20, "Concurrent should be 20 from env"
    
    print(f"✓ Ranker algorithm (from env): {ranker_config.algorithm}")
    assert ranker_config.algorithm == "location", "Algorithm should be location from env"
    
    print(f"✓ WeCom enabled (from env): {wecom_config.enabled}")
    assert wecom_config.enabled == True, "WeCom should be enabled from env"
    
    print(f"✓ WeCom retry times (from env): {wecom_config.retry_times}")
    assert wecom_config.retry_times == 5, "WeCom retry times should be 5 from env"
    
    # Clean up env vars
    for key in list(os.environ.keys()):
        if key.startswith(("SCHEDULER__", "LATENCY_TEST__", "RANKER__", "WECOM__")):
            del os.environ[key]


def test_type_validation():
    """Test type validation and defaults."""
    print("\n=== Test 3: Type Validation and Defaults ===")
    
    reset_config_manager()
    manager = get_config_manager()
    
    # Test that latency config has proper type validation
    latency_config = manager.get_latency_test_config()
    
    # Should enforce minimum values
    assert latency_config.timeout >= 1000, "Timeout should have minimum"
    assert latency_config.concurrent >= 1, "Concurrent should have minimum"
    assert latency_config.retries >= 1, "Retries should have minimum"
    
    print(f"✓ Timeout minimum enforced: {latency_config.timeout}ms >= 1000ms")
    print(f"✓ Concurrent minimum enforced: {latency_config.concurrent} >= 1")
    print(f"✓ Retries minimum enforced: {latency_config.retries} >= 1")
    
    # Test ranker algorithm validation
    ranker_config = manager.get_ranker_config()
    assert ranker_config.algorithm in ["latency", "location", "mixed"], "Algorithm should be valid"
    print(f"✓ Ranker algorithm valid: {ranker_config.algorithm}")
    
    # Test default values
    assert isinstance(latency_config.exclude_patterns, list), "Patterns should be a list"
    print(f"✓ Exclude patterns is a list: {latency_config.exclude_patterns}")


def test_cron_validation():
    """Test cron expression validation."""
    print("\n=== Test 4: Cron Expression Validation ===")
    
    reset_config_manager()
    manager = get_config_manager()
    
    scheduler_config = manager.get_scheduler_config()
    
    for task in scheduler_config.tasks:
        print(f"✓ Valid cron expression: {task.name} -> {task.cron}")
        
        # Verify format: should be 5 space-separated fields
        parts = task.cron.split()
        assert len(parts) == 5, f"Cron should have 5 fields, got {len(parts)}"


def test_missing_files_handling():
    """Test graceful handling of missing configuration files."""
    print("\n=== Test 5: Missing Files Handling ===")
    
    # Create a temporary config directory with partial configs
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Only create scheduler.yaml
        scheduler_path = Path(tmpdir) / "scheduler.yaml"
        scheduler_path.write_text("enabled: true\ntasks: []")
        
        # Try to load from directory with missing files
        reset_config_manager()
        manager = ConfigManager(tmpdir)
        
        # Should not raise errors, should return defaults
        latency_config = manager.get_latency_test_config()
        ranker_config = manager.get_ranker_config()
        wecom_config = manager.get_wecom_config()
        
        print(f"✓ Missing latency_test.yaml handled gracefully")
        print(f"  - Loaded default latency timeout: {latency_config.timeout}ms")
        
        print(f"✓ Missing ranker.yaml handled gracefully")
        print(f"  - Loaded default algorithm: {ranker_config.algorithm}")
        
        print(f"✓ Missing wecom.yaml handled gracefully")
        print(f"  - Loaded default enabled: {wecom_config.enabled}")


def test_dict_conversion():
    """Test conversion to dictionary."""
    print("\n=== Test 6: Dictionary Conversion ===")
    
    reset_config_manager()
    manager = get_config_manager()
    
    all_configs = manager.to_dict()
    
    assert "scheduler" in all_configs, "Should have scheduler key"
    assert "latency_test" in all_configs, "Should have latency_test key"
    assert "ranker" in all_configs, "Should have ranker key"
    assert "wecom" in all_configs, "Should have wecom key"
    
    print(f"✓ Successfully converted to dictionary")
    print(f"  - Keys: {list(all_configs.keys())}")


if __name__ == "__main__":
    try:
        test_basic_loading()
        test_env_overrides()
        test_type_validation()
        test_cron_validation()
        test_missing_files_handling()
        test_dict_conversion()
        
        print("\n" + "="*50)
        print("✓ All tests passed!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
