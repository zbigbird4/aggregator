#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example demonstrating how to integrate ConfigManager into existing code.

This file shows best practices for using the centralized configuration manager
in the subscribe module and its submodules.
"""

from config_manager import get_config_manager
from logger import logger


def example_using_scheduler_config():
    """Example: Use scheduler config to schedule tasks."""
    manager = get_config_manager()
    scheduler_config = manager.get_scheduler_config()
    
    if not scheduler_config.enabled:
        logger.info("Scheduler is disabled")
        return
    
    logger.info(f"Scheduler enabled with {len(scheduler_config.tasks)} tasks")
    
    for task in scheduler_config.tasks:
        if not task.enabled:
            logger.info(f"Task '{task.name}' is disabled, skipping")
            continue
        
        logger.info(f"Scheduling task: {task.name}")
        logger.info(f"  Cron: {task.cron}")
        logger.info(f"  Script: {task.script}")
        logger.info(f"  Params: {task.params}")


def example_using_latency_test_config():
    """Example: Use latency test config in proxy checking."""
    manager = get_config_manager()
    latency_config = manager.get_latency_test_config()
    
    if not latency_config.enabled:
        logger.info("Latency testing is disabled")
        return
    
    logger.info(f"Latency test config:")
    logger.info(f"  Timeout: {latency_config.timeout}ms")
    logger.info(f"  Concurrent tests: {latency_config.concurrent}")
    logger.info(f"  Retry attempts: {latency_config.retries}")
    logger.info(f"  Exclude patterns: {latency_config.exclude_patterns}")
    
    # Example: Use in proxy testing loop
    test_proxies = ["proxy1", "test-proxy2", "proxy3-expired"]
    
    for proxy in test_proxies:
        # Check against exclude patterns
        should_exclude = any(
            pattern in proxy 
            for pattern in latency_config.exclude_patterns
        )
        
        if should_exclude:
            logger.debug(f"Excluding proxy: {proxy}")
            continue
        
        logger.info(f"Testing proxy: {proxy}")


def example_using_ranker_config():
    """Example: Use ranker config for proxy sorting."""
    manager = get_config_manager()
    ranker_config = manager.get_ranker_config()
    
    if not ranker_config.enabled:
        logger.info("Ranker is disabled")
        return
    
    logger.info(f"Ranker configuration:")
    logger.info(f"  Algorithm: {ranker_config.algorithm}")
    logger.info(f"  Sort by: {ranker_config.sort_by}")
    logger.info(f"  Residential priority: {ranker_config.residential_priority}")
    
    # Example: Apply ranking logic
    proxies = [
        {"name": "proxy1", "latency": 100, "location": "US"},
        {"name": "proxy2", "latency": 50, "location": "UK"},
        {"name": "backup-proxy3", "latency": 200, "location": "CN"},
    ]
    
    # Filter by exclude patterns
    filtered = [
        p for p in proxies
        if not any(pat in p["name"] for pat in ranker_config.exclude_patterns)
    ]
    
    # Sort by configured fields
    if ranker_config.algorithm == "latency":
        sorted_proxies = sorted(filtered, key=lambda p: p["latency"])
    elif ranker_config.algorithm == "location":
        sorted_proxies = sorted(filtered, key=lambda p: p["location"])
    else:  # mixed
        sorted_proxies = sorted(
            filtered,
            key=lambda p: (p["latency"], p["location"])
        )
    
    logger.info(f"Ranked proxies: {[p['name'] for p in sorted_proxies]}")


def example_using_wecom_config():
    """Example: Use WeCom config for notifications."""
    manager = get_config_manager()
    wecom_config = manager.get_wecom_config()
    
    if not wecom_config.enabled:
        logger.info("WeCom notifications are disabled")
        return
    
    if not wecom_config.webhook_url:
        logger.warning("WeCom enabled but webhook URL not found")
        return
    
    logger.info(f"WeCom configuration:")
    logger.info(f"  Webhook URL: {wecom_config.webhook_url[:50]}...")
    logger.info(f"  Retry attempts: {wecom_config.retry_times}")
    logger.info(f"  Retry delay: {wecom_config.retry_delay}s")
    logger.info(f"  Send on error: {wecom_config.send_on_error}")
    logger.info(f"  Send on success: {wecom_config.send_on_success}")
    
    # Example: Send notification
    def send_notification(message: str, is_error: bool = False) -> bool:
        """Simulated notification sending."""
        if is_error and not wecom_config.send_on_error:
            return True
        if not is_error and not wecom_config.send_on_success:
            return True
        
        logger.info(f"Sending WeCom notification: {message}")
        return True
    
    send_notification("Task completed successfully")


def example_environment_override_workflow():
    """
    Example: Show how environment variables override config.
    
    Usage:
        export SCHEDULER__ENABLED=false
        export LATENCY_TEST__TIMEOUT=10000
        python config_usage_example.py
    """
    manager = get_config_manager()
    
    print("\n=== Environment Override Example ===")
    print("Configuration values (after env overrides):")
    print()
    
    # Display all configs
    configs = manager.to_dict()
    for config_name, config_data in configs.items():
        print(f"{config_name}:")
        
        if isinstance(config_data, dict):
            for key, value in config_data.items():
                if isinstance(value, (list, dict)):
                    print(f"  {key}: {str(value)[:60]}...")
                else:
                    print(f"  {key}: {value}")
        print()


if __name__ == "__main__":
    print("ConfigManager Integration Examples\n")
    print("=" * 50)
    
    example_using_scheduler_config()
    print()
    
    example_using_latency_test_config()
    print()
    
    example_using_ranker_config()
    print()
    
    example_using_wecom_config()
    print()
    
    example_environment_override_workflow()
    
    print("=" * 50)
    print("\nExamples completed!")
