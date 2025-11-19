# -*- coding: utf-8 -*-

# @Author  : wzdnzd
# @Time    : 2024-11-19

"""
Enhanced latency measurement module for proxy testing.

This module provides comprehensive latency and stability measurement capabilities:
- ICMP ping measurement with RTT per packet and packet loss tracking
- HTTP GET request latency measurement
- Concurrent testing with configurable concurrency limits
- Retry logic and outlier detection
- Latency score computation based on multiple metrics
- Structured result output for downstream ranking logic

Example usage:
    from latency_tester import measure
    
    proxies = [
        {"name": "proxy1", "server": "8.8.8.8", "port": 8080, "type": "http"},
        {"name": "proxy2", "server": "1.1.1.1", "port": 8080, "type": "socks5"},
    ]
    
    config = {
        "test_count": 3,
        "concurrent_limit": 5,
        "retry_times": 2,
        "max_latency": 3000,
        "ping_timeout": 5,
        "http_timeout": 10,
    }
    
    measurements, logs = measure(proxies, config)
    
    for proxy_id, metrics in measurements.items():
        print(f"{proxy_id}: ping={metrics['ping_ms']}ms, "
              f"http={metrics['http_ms']}ms, "
              f"score={metrics['latency_score']:.1f}")
"""

import json
import socket
import statistics
import subprocess
import sys
import time
import traceback
from concurrent import futures
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

import utils
from logger import logger


@dataclass
class MeasurementConfig:
    """Configuration for latency measurements"""

    # Number of test attempts per proxy
    test_count: int = 3

    # Maximum concurrent requests
    concurrent_limit: int = 10

    # Retry times per node
    retry_times: int = 3

    # Maximum acceptable latency in milliseconds
    max_latency: int = 5000

    # Ping timeout in seconds
    ping_timeout: int = 5

    # HTTP timeout in seconds (total)
    http_timeout: int = 10

    # HTTP connect timeout in seconds
    http_connect_timeout: int = 5

    # HTTP read timeout in seconds
    http_read_timeout: int = 5

    # Test URL for HTTP latency measurement
    test_url: str = "https://www.google.com"

    # Whether to discard outliers when computing averages
    discard_outliers: bool = True

    # Latency buckets for scoring (in milliseconds)
    latency_buckets: List[int] = field(default_factory=lambda: [50, 100, 200, 500, 1000])


@dataclass
class ProxyMeasurement:
    """Measurement result for a single proxy"""

    proxy_id: str
    ping_ms: Optional[float] = None
    http_ms: Optional[float] = None
    packet_loss: float = 0.0
    success_rate: float = 0.0
    latency_score: float = 0.0
    jitter: float = 0.0


def _parse_ping_output(output: str) -> Tuple[Optional[float], float]:
    """
    Parse ping command output to extract RTT and packet loss.

    Returns:
        Tuple of (rtt_ms, packet_loss_percent)
    """
    lines = output.strip().split("\n")
    rtt_ms = None
    packet_loss = 0.0

    for line in lines:
        # Match packet loss line: "X% packet loss"
        if "packet loss" in line:
            import re

            match = re.search(r"(\d+(?:\.\d+)?)\%", line)
            if match:
                packet_loss = float(match.group(1))

        # Match RTT line: "time=XXms" or "time=XX.XXms"
        if "time=" in line:
            import re

            match = re.search(r"time=(\d+(?:\.\d+)?)\s*ms", line)
            if match:
                rtt_ms = float(match.group(1))

    return rtt_ms, packet_loss


def _measure_ping(host: str, config: MeasurementConfig) -> Tuple[List[float], float]:
    """
    Measure latency using ICMP ping.

    Returns:
        Tuple of (list of RTT values in ms, packet loss percentage)
    """
    rtts = []
    packet_loss = 0.0

    try:
        # Determine ping command based on platform
        if sys.platform == "win32":
            cmd = ["ping", "-n", str(config.test_count), "-w", str(config.ping_timeout * 1000), host]
        else:
            cmd = ["ping", "-c", str(config.test_count), "-W", str(config.ping_timeout * 1000), host]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=config.ping_timeout + 5,
        )

        output = result.stdout if result.returncode == 0 else result.stderr
        rtt_ms, packet_loss = _parse_ping_output(output)

        # Extract all RTT values from output
        import re

        for match in re.finditer(r"time=(\d+(?:\.\d+)?)\s*ms", output):
            rtts.append(float(match.group(1)))

        # If we got RTT samples, use them; otherwise use the parsed value
        if not rtts and rtt_ms is not None:
            rtts.append(rtt_ms)

    except subprocess.TimeoutExpired:
        packet_loss = 100.0
        logger.debug(f"Ping timeout for host {host}")
    except FileNotFoundError:
        logger.debug(f"Ping command not found on this system")
    except Exception as e:
        logger.debug(f"Ping failed for {host}: {str(e)}")

    return rtts, packet_loss


def _measure_http(url: str, config: MeasurementConfig, proxy: Optional[str] = None) -> Optional[float]:
    """
    Measure HTTP GET request latency.

    Args:
        url: URL to test
        config: Measurement configuration
        proxy: Optional proxy to use

    Returns:
        Latency in milliseconds or None if failed
    """
    try:
        import urllib.request
        import urllib.error
        import ssl

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        start_time = time.time()
        request = urllib.request.Request(url=url, headers=utils.DEFAULT_HTTP_HEADERS)

        if proxy and (proxy.startswith("https://") or proxy.startswith("http://")):
            host = proxy[8:] if proxy.startswith("https://") else proxy[7:]
            protocal = "https" if proxy.startswith("https://") else "http"
            request.set_proxy(host=host, type=protocal)

        response = urllib.request.urlopen(request, timeout=config.http_timeout, context=ctx)
        response.read(1024)  # Read a small amount to get real latency
        response.close()

        elapsed_ms = (time.time() - start_time) * 1000
        return elapsed_ms

    except (urllib.error.URLError, socket.timeout, Exception) as e:
        logger.debug(f"HTTP test failed for {url}: {str(e)}")
        return None


def _compute_score(
    ping_ms: Optional[float],
    http_ms: Optional[float],
    packet_loss: float,
    success_rate: float,
    jitter: float,
    config: MeasurementConfig,
) -> float:
    """
    Compute a latency/stability score based on measurements.

    Score is computed as:
    - Base score of 100
    - Deduction for latency (based on buckets)
    - Deduction for packet loss
    - Deduction for jitter
    - Bonus for high success rate

    Returns:
        Score between 0 and 100
    """
    score = 100.0

    # Consider ping latency with bucket-based deduction
    if ping_ms is not None:
        latency_deduction = 0.0
        for bucket in config.latency_buckets:
            if ping_ms <= bucket:
                latency_deduction = (ping_ms / bucket) * 20  # Max 20 points
                break
        else:
            latency_deduction = 20  # Max deduction if exceeds all buckets

        score -= latency_deduction

    # Consider HTTP latency as a bonus indicator
    if http_ms is not None and ping_ms is not None:
        http_ratio = http_ms / (ping_ms + 1)  # Avoid division by zero
        if http_ratio > 5:  # Significantly higher than ping
            score -= 5  # Slight deduction for potential congestion

    # Deduct for packet loss (max 30 points)
    score -= min(packet_loss * 0.3, 30)

    # Deduct for jitter (max 10 points)
    jitter_deduction = min(jitter / 50 * 10, 10)  # 50ms jitter = 10 point deduction
    score -= jitter_deduction

    # Add bonus for high success rate (max 20 points)
    if success_rate < 1.0:
        score -= (1.0 - success_rate) * 40  # Max 40 points deduction for low success rate

    # Clamp score to 0-100 range
    return max(0, min(100, score))


def _compute_statistics(values: List[float], discard_outliers: bool = True) -> Tuple[float, float]:
    """
    Compute average and jitter from a list of values.

    Returns:
        Tuple of (average, jitter)
    """
    if not values:
        return 0.0, 0.0

    if discard_outliers and len(values) > 2:
        # Remove outliers using modified Z-score method (Iglewicz and Hoaglin method)
        sorted_vals = sorted(values)
        median = sorted_vals[len(sorted_vals) // 2]

        # Calculate median absolute deviation
        deviations = [abs(v - median) for v in sorted_vals]
        mad = sorted(deviations)[len(deviations) // 2] if deviations else 0.0

        # Use modified Z-score threshold (3.5 is commonly used for outlier detection)
        filtered_values = []
        for v in values:
            if mad > 0:
                modified_z_score = 0.6745 * abs(v - median) / mad
                if modified_z_score <= 3.5:
                    filtered_values.append(v)
            elif v == median:
                # If MAD is 0 and value equals median, keep it
                filtered_values.append(v)
            elif abs(v - median) <= 0.01 * (median if median != 0 else 1):
                # If MAD is 0, keep values very close to median
                filtered_values.append(v)

        if filtered_values and len(filtered_values) > 0:
            values = filtered_values

    average = sum(values) / len(values)

    # Calculate jitter as standard deviation
    jitter = 0.0
    if len(values) > 1:
        jitter = statistics.stdev(values)

    return average, jitter


def _measure_proxy(
    proxy: dict,
    config: MeasurementConfig,
) -> Tuple[str, ProxyMeasurement]:
    """
    Measure a single proxy's latency metrics.

    Returns:
        Tuple of (proxy_id, ProxyMeasurement)
    """
    proxy_id = proxy.get("name", "unknown")
    measurement = ProxyMeasurement(proxy_id=proxy_id)

    # Measure ICMP ping if host is available
    host = proxy.get("server")
    if host:
        all_rtts = []
        all_packet_losses = []

        for attempt in range(config.retry_times):
            rtts, packet_loss = _measure_ping(host, config)
            if rtts:
                all_rtts.extend(rtts)
                all_packet_losses.append(packet_loss)

            if rtts and packet_loss == 0.0:
                break  # Success, no need to retry

        if all_rtts:
            avg_rtt, jitter = _compute_statistics(all_rtts, config.discard_outliers)
            measurement.ping_ms = avg_rtt
            measurement.jitter = jitter

            if all_packet_losses:
                measurement.packet_loss = sum(all_packet_losses) / len(all_packet_losses)

    # Measure HTTP latency
    all_http_latencies = []
    successful_http_tests = 0

    for attempt in range(config.test_count):
        http_latency = _measure_http(config.test_url, config)
        if http_latency is not None:
            all_http_latencies.append(http_latency)
            successful_http_tests += 1

    if all_http_latencies:
        avg_http, _ = _compute_statistics(all_http_latencies, config.discard_outliers)
        measurement.http_ms = avg_http

    # Compute success rate
    total_tests = config.test_count + config.retry_times
    total_successful = successful_http_tests + (1 if measurement.ping_ms is not None else 0)
    measurement.success_rate = total_successful / total_tests if total_tests > 0 else 0.0

    # Compute latency score
    measurement.latency_score = _compute_score(
        measurement.ping_ms,
        measurement.http_ms,
        measurement.packet_loss,
        measurement.success_rate,
        measurement.jitter,
        config,
    )

    return proxy_id, measurement


def _should_filter_proxy(proxy: dict, measurement: ProxyMeasurement, config: MeasurementConfig) -> bool:
    """
    Determine if a proxy should be filtered out based on measurements.

    Returns:
        True if proxy should be filtered out
    """
    # Filter if max latency exceeded
    if measurement.ping_ms is not None and measurement.ping_ms > config.max_latency:
        return True

    if measurement.http_ms is not None and measurement.http_ms > config.max_latency:
        return True

    # Filter if success rate is too low
    if measurement.success_rate < 0.3:  # Less than 30% success
        return True

    return False


def measure(
    proxies: List[dict],
    config: Optional[Dict] = None,
) -> Tuple[Dict[str, Dict], List[Dict]]:
    """
    Measure latency and stability for a list of proxies.

    Args:
        proxies: List of proxy dictionaries with at least 'name' and 'server' fields
        config: Configuration dictionary with optional keys:
            - test_count: Number of test attempts (default: 3)
            - concurrent_limit: Max concurrent requests (default: 10)
            - retry_times: Retry attempts per node (default: 3)
            - max_latency: Max acceptable latency in ms (default: 5000)
            - ping_timeout: Ping timeout in seconds (default: 5)
            - http_timeout: HTTP timeout in seconds (default: 10)
            - http_connect_timeout: HTTP connect timeout (default: 5)
            - http_read_timeout: HTTP read timeout (default: 5)
            - test_url: URL for HTTP tests (default: https://www.google.com)
            - discard_outliers: Whether to discard outliers (default: True)
            - latency_buckets: List of latency bucket thresholds

    Returns:
        Tuple of (measurements_dict, raw_logs)
        - measurements_dict: {proxy_id: {ping_ms, http_ms, packet_loss, success_rate, latency_score}}
        - raw_logs: List of log entries for auditing
    """
    if not proxies:
        return {}, []

    # Parse configuration
    if config is None:
        config = {}

    measurement_config = MeasurementConfig(
        test_count=max(1, config.get("test_count", 3)),
        concurrent_limit=max(1, config.get("concurrent_limit", 10)),
        retry_times=max(1, config.get("retry_times", 3)),
        max_latency=max(100, config.get("max_latency", 5000)),
        ping_timeout=max(1, config.get("ping_timeout", 5)),
        http_timeout=max(1, config.get("http_timeout", 10)),
        http_connect_timeout=max(1, config.get("http_connect_timeout", 5)),
        http_read_timeout=max(1, config.get("http_read_timeout", 5)),
        test_url=config.get("test_url", "https://www.google.com"),
        discard_outliers=config.get("discard_outliers", True),
        latency_buckets=config.get(
            "latency_buckets",
            [50, 100, 200, 500, 1000],
        ),
    )

    measurements = {}
    raw_logs = []
    filtered_proxies = []

    try:
        # Use ThreadPoolExecutor to measure proxies concurrently
        with futures.ThreadPoolExecutor(max_workers=measurement_config.concurrent_limit) as executor:
            # Submit all tasks
            future_to_proxy = {
                executor.submit(_measure_proxy, proxy, measurement_config): proxy
                for proxy in proxies
            }

            # Process completed tasks
            for future in futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    proxy_id, measurement = future.result()
                    measurements[proxy_id] = {
                        "ping_ms": measurement.ping_ms,
                        "http_ms": measurement.http_ms,
                        "packet_loss": measurement.packet_loss,
                        "success_rate": measurement.success_rate,
                        "latency_score": measurement.latency_score,
                        "jitter": measurement.jitter,
                    }

                    # Log the measurement
                    log_entry = {
                        "proxy_id": proxy_id,
                        "timestamp": time.time(),
                        "measurements": measurements[proxy_id],
                    }
                    raw_logs.append(log_entry)

                    # Check if proxy should be filtered
                    if not _should_filter_proxy(proxy, measurement, measurement_config):
                        filtered_proxies.append(proxy)

                    logger.debug(
                        f"Measured proxy {proxy_id}: "
                        f"ping={measurement.ping_ms}ms, "
                        f"http={measurement.http_ms}ms, "
                        f"loss={measurement.packet_loss}%, "
                        f"score={measurement.latency_score:.1f}"
                    )

                except Exception as e:
                    log_entry = {
                        "proxy_id": proxy.get("name", "unknown"),
                        "timestamp": time.time(),
                        "error": str(e),
                    }
                    raw_logs.append(log_entry)
                    logger.error(
                        f"Failed to measure proxy {proxy.get('name', 'unknown')}: {str(e)}\n{traceback.format_exc()}"
                    )

    except Exception as e:
        logger.error(f"Latency measurement failed: {str(e)}\n{traceback.format_exc()}")

    return measurements, raw_logs
