# -*- coding: utf-8 -*-

# @Author  : wzdnzd
# @Time    : 2024-01-01

import os
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from logger import logger


# Typed configuration dataclasses
@dataclass
class SchedulerTask:
    """Individual scheduler task configuration"""
    name: str
    cron: str
    enabled: bool = True
    script: str = ""
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchedulerConfig:
    """Scheduler configuration"""
    enabled: bool = True
    tasks: List[SchedulerTask] = field(default_factory=list)


@dataclass
class LatencyTestConfig:
    """Latency test configuration"""
    enabled: bool = True
    timeout: int = 5000
    concurrent: int = 10
    retries: int = 2
    exclude_patterns: List[str] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=list)


@dataclass
class RankerConfig:
    """Ranker configuration for proxy ranking"""
    enabled: bool = True
    algorithm: str = "latency"
    sort_by: List[str] = field(default_factory=lambda: ["latency", "location"])
    residential_priority: bool = False
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class WeComConfig:
    """WeCom (WeChat Work) notification configuration"""
    enabled: bool = False
    webhook_url_env: str = "WECOM_WEBHOOK_URL"
    webhook_url: Optional[str] = None
    retry_times: int = 3
    retry_delay: int = 5
    send_on_error: bool = True
    send_on_success: bool = False


class ConfigManager:
    """
    Centralized configuration manager that loads YAML configs from config/ directory.
    Supports environment variable overrides with format: MODULE__KEY__SUBKEY=value
    Falls back to defaults for missing fields.
    """

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the config manager.
        
        Args:
            config_dir: Directory containing YAML config files (relative to subscribe/ or absolute)
        """
        self.config_dir = self._resolve_config_dir(config_dir)
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._load_all_configs()

    def _resolve_config_dir(self, config_dir: str) -> Path:
        """Resolve the config directory path."""
        if os.path.isabs(config_dir):
            path = Path(config_dir)
        else:
            # Try relative to subscribe directory
            subscribe_dir = Path(__file__).parent
            path = subscribe_dir / config_dir
        
        if not path.exists():
            logger.warning(f"Config directory does not exist: {path}. Creating it.")
            path.mkdir(parents=True, exist_ok=True)
        
        return path

    def _load_all_configs(self) -> None:
        """Load all YAML config files from config directory."""
        config_files = [
            "scheduler.yaml",
            "latency_test.yaml",
            "ranker.yaml",
            "wecom.yaml"
        ]
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            config_name = config_file.replace(".yaml", "")
            
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = yaml.safe_load(f) or {}
                    self._configs[config_name] = config_data
                    logger.debug(f"Loaded config file: {config_file}")
                except Exception as e:
                    logger.error(f"Failed to load config file {config_file}: {e}")
                    self._configs[config_name] = {}
            else:
                logger.debug(f"Config file not found: {config_file}. Using defaults.")
                self._configs[config_name] = {}
        
        # Apply environment variable overrides
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configs."""
        pattern = re.compile(r"^([A-Z_]+)__(.+)$")
        
        for env_key, env_value in os.environ.items():
            match = pattern.match(env_key)
            if not match:
                continue
            
            module_name = env_key.split("__")[0].lower()
            if module_name not in self._configs:
                continue
            
            # Extract nested keys: SCHEDULER__TASKS__0__ENABLED -> ["TASKS", "0", "ENABLED"]
            keys = env_key.split("__")[1:]
            
            try:
                self._set_nested_value(self._configs[module_name], keys, env_value)
                logger.debug(f"Applied environment override: {env_key}={env_value}")
            except Exception as e:
                logger.warning(f"Failed to apply environment override {env_key}: {e}")

    def _set_nested_value(self, obj: Any, keys: List[str], value: str) -> None:
        """Set a nested value in a dictionary/list using a list of keys."""
        for key in keys[:-1]:
            # Try to convert to int for list indexing
            try:
                index = int(key)
                if not isinstance(obj, list):
                    obj = []
                while len(obj) <= index:
                    obj.append({})
                obj = obj[index]
            except ValueError:
                # It's a string key
                key_lower = key.lower()
                if key_lower not in obj:
                    obj[key_lower] = {}
                obj = obj[key_lower]
        
        # Set the final value
        final_key = keys[-1]
        try:
            final_index = int(final_key)
            if isinstance(obj, list):
                while len(obj) <= final_index:
                    obj.append(None)
                obj[final_index] = self._parse_value(value)
        except ValueError:
            # It's a string key
            final_key_lower = final_key.lower()
            obj[final_key_lower] = self._parse_value(value)

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Parse string environment variable value to appropriate type."""
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value

    def get_scheduler_config(self) -> SchedulerConfig:
        """Get typed scheduler configuration."""
        config_data = self._configs.get("scheduler", {})
        
        # Validate required fields
        tasks_data = config_data.get("tasks", [])
        tasks = []
        
        for i, task_data in enumerate(tasks_data):
            if not isinstance(task_data, dict):
                logger.warning(f"Scheduler task {i} is not a dict, skipping")
                continue
            
            # Validate required fields
            if "name" not in task_data:
                logger.error(f"Scheduler task {i} missing required field: name")
                continue
            if "cron" not in task_data:
                logger.error(f"Scheduler task {i} missing required field: cron")
                continue
            
            # Validate cron expression format
            if not self._is_valid_cron(task_data["cron"]):
                logger.error(f"Scheduler task {i} has invalid cron expression: {task_data['cron']}")
                continue
            
            tasks.append(SchedulerTask(
                name=task_data["name"],
                cron=task_data["cron"],
                enabled=task_data.get("enabled", True),
                script=task_data.get("script", ""),
                params=task_data.get("params", {})
            ))
        
        return SchedulerConfig(
            enabled=config_data.get("enabled", True),
            tasks=tasks
        )

    def get_latency_test_config(self) -> LatencyTestConfig:
        """Get typed latency test configuration."""
        config_data = self._configs.get("latency_test", {})
        
        return LatencyTestConfig(
            enabled=config_data.get("enabled", True),
            timeout=max(config_data.get("timeout", 5000), 1000),  # Min 1s
            concurrent=max(config_data.get("concurrent", 10), 1),  # Min 1
            retries=max(config_data.get("retries", 2), 1),  # Min 1
            exclude_patterns=config_data.get("exclude_patterns", []),
            include_patterns=config_data.get("include_patterns", [])
        )

    def get_ranker_config(self) -> RankerConfig:
        """Get typed ranker configuration."""
        config_data = self._configs.get("ranker", {})
        
        # Validate algorithm
        valid_algorithms = ["latency", "location", "mixed"]
        algorithm = config_data.get("algorithm", "latency")
        if algorithm not in valid_algorithms:
            logger.warning(f"Invalid ranker algorithm: {algorithm}. Using default: latency")
            algorithm = "latency"
        
        return RankerConfig(
            enabled=config_data.get("enabled", True),
            algorithm=algorithm,
            sort_by=config_data.get("sort_by", ["latency", "location"]),
            residential_priority=config_data.get("residential_priority", False),
            exclude_patterns=config_data.get("exclude_patterns", [])
        )

    def get_wecom_config(self) -> WeComConfig:
        """Get typed WeCom notification configuration."""
        config_data = self._configs.get("wecom", {})
        
        # Validate webhook_url_env
        webhook_url_env = config_data.get("webhook_url_env", "WECOM_WEBHOOK_URL")
        if not webhook_url_env:
            logger.warning("WeComConfig: webhook_url_env is empty, using default")
            webhook_url_env = "WECOM_WEBHOOK_URL"
        
        # Get webhook URL from environment if enabled
        webhook_url = None
        if config_data.get("enabled", False):
            webhook_url = os.getenv(webhook_url_env)
            if not webhook_url:
                logger.warning(f"WeComConfig enabled but {webhook_url_env} environment variable not found")
        
        return WeComConfig(
            enabled=config_data.get("enabled", False),
            webhook_url_env=webhook_url_env,
            webhook_url=webhook_url,
            retry_times=max(config_data.get("retry_times", 3), 1),
            retry_delay=max(config_data.get("retry_delay", 5), 1),
            send_on_error=config_data.get("send_on_error", True),
            send_on_success=config_data.get("send_on_success", False)
        )

    @staticmethod
    def _is_valid_cron(cron_expr: str) -> bool:
        """
        Basic validation of cron expression format.
        A valid cron expression has 5 fields (minute, hour, day, month, weekday).
        """
        if not isinstance(cron_expr, str):
            return False
        
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            return False
        
        # Very basic validation - just check that we have 5 fields
        # More strict validation could be done with a cron library
        return all(p for p in parts)

    def get_raw_config(self, config_name: str) -> Dict[str, Any]:
        """Get raw configuration dictionary by name."""
        return self._configs.get(config_name, {})

    def reload_configs(self) -> None:
        """Reload all configurations from disk."""
        self._configs.clear()
        self._load_all_configs()
        logger.info("Configuration reloaded")

    def to_dict(self) -> Dict[str, Any]:
        """Convert all configurations to dictionary."""
        return {
            "scheduler": asdict(self.get_scheduler_config()),
            "latency_test": asdict(self.get_latency_test_config()),
            "ranker": asdict(self.get_ranker_config()),
            "wecom": asdict(self.get_wecom_config())
        }


# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_dir: str = "config") -> ConfigManager:
    """Get or create the singleton ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_dir)
    return _config_manager


def reset_config_manager() -> None:
    """Reset the singleton instance (useful for testing)."""
    global _config_manager
    _config_manager = None
