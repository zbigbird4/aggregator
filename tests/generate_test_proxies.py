#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate 100 test proxy nodes for functional testing.
Includes mix of normal, varying quality, and occasional faulty nodes.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Proxy types
PROXY_TYPES = ['ss', 'ssr', 'vmess', 'trojan', 'vless', 'hysteria']

# Server locations
LOCATIONS = [
    {'country': 'US', 'region': 'New York', 'lat': 40.7128, 'lon': -74.0060},
    {'country': 'US', 'region': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437},
    {'country': 'US', 'region': 'Chicago', 'lat': 41.8781, 'lon': -87.6298},
    {'country': 'JP', 'region': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
    {'country': 'JP', 'region': 'Osaka', 'lat': 34.6937, 'lon': 135.5023},
    {'country': 'SG', 'region': 'Singapore', 'lat': 1.3521, 'lon': 103.8198},
    {'country': 'CN', 'region': 'Hong Kong', 'lat': 22.3193, 'lon': 114.1694},
    {'country': 'DE', 'region': 'Berlin', 'lat': 52.5200, 'lon': 13.4050},
    {'country': 'GB', 'region': 'London', 'lat': 51.5074, 'lon': -0.1278},
    {'country': 'FR', 'region': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
    {'country': 'CA', 'region': 'Toronto', 'lat': 43.6532, 'lon': -79.3832},
    {'country': 'AU', 'region': 'Sydney', 'lat': -33.8688, 'lon': 151.2093},
    {'country': 'KR', 'region': 'Seoul', 'lat': 37.5665, 'lon': 126.9780},
    {'country': 'IN', 'region': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
    {'country': 'BR', 'region': 'São Paulo', 'lat': -23.5505, 'lon': -46.6333},
]

# ISP patterns
ISPS = ['Digital Ocean', 'Linode', 'AWS', 'Vultr', 'DigitalOcean', 'Hetzner', 
        'OVH', 'Scaleway', 'CyberPanel', 'Azure', 'GCP', 'Alibaba Cloud']

# Base IP ranges for different quality tiers
BASE_IPS = {
    'good': ['45.142', '185.162', '89.163', '147.135', '188.166', '159.65', '104.248'],
    'medium': ['104.21', '172.67', '103.21', '203.0', '198.41', '54.230', '13.224'],
    'poor': ['192.168', '10.0', '172.16', '127.0', '169.254', '224.0', '192.0'],
}


def generate_test_proxy(index: int, quality_tier: str = 'good') -> Dict[str, Any]:
    """Generate a single test proxy node."""
    
    location = random.choice(LOCATIONS)
    proxy_type = random.choice(PROXY_TYPES)
    isp = random.choice(ISPS)
    
    # Generate realistic IP based on quality tier
    ip_base = random.choice(BASE_IPS[quality_tier])
    parts = ip_base.split('.')
    ip = f"{ip_base}.{random.randint(1, 254)}.{random.randint(1, 254)}"
    
    # Generate realistic latency distribution based on quality tier
    if quality_tier == 'good':
        latency = random.gauss(80, 20)  # Mean 80ms, std 20ms
        latency = max(10, min(150, latency))  # Clamp between 10-150ms
        packet_loss = random.choice([0, 0, 0, 0, 0, 0.5, 1])  # Mostly 0%, occasionally 0.5-1%
    elif quality_tier == 'medium':
        latency = random.gauss(200, 50)  # Mean 200ms, std 50ms
        latency = max(50, min(400, latency))  # Clamp between 50-400ms
        packet_loss = random.choice([0, 0.5, 1, 2, 5])  # Higher loss
    else:  # poor
        latency = random.gauss(500, 150)  # Mean 500ms, std 150ms
        latency = max(200, min(2000, latency))  # Clamp between 200-2000ms
        packet_loss = random.choice([5, 10, 20, 30, 50])  # Very high loss
    
    # Some nodes might be down (simulated by extremely high latency)
    if random.random() < 0.05:  # 5% chance of being down
        latency = 9999
        packet_loss = 100
    
    creation_date = datetime.now() - timedelta(days=random.randint(1, 90))
    
    return {
        'id': f'proxy_{index:03d}',
        'name': f'{proxy_type.upper()}-{location["country"]}-{location["region"]}-{index}',
        'type': proxy_type,
        'server': ip,
        'port': random.choice([80, 443, 8080, 8443, 1080, 3128]),
        'password': f'pass{index}' if proxy_type in ['ss', 'ssr'] else None,
        'method': 'aes-256-gcm' if proxy_type == 'ss' else None,
        'obfs': 'tls' if proxy_type == 'ssr' else None,
        'location': location,
        'isp': isp,
        'latency_ms': round(latency, 1),
        'packet_loss_percent': packet_loss,
        'bandwidth_mbps': random.randint(1, 1000) if random.random() < 0.9 else None,
        'uptime_percent': random.uniform(90, 100) if quality_tier != 'poor' else random.uniform(50, 95),
        'is_residential': random.choice([True, False]),
        'created_at': creation_date.isoformat(),
        'last_checked': datetime.now().isoformat(),
        'quality_tier': quality_tier,
    }


def generate_test_dataset(num_proxies: int = 100, output_file: str = None) -> List[Dict[str, Any]]:
    """Generate a test dataset with specified number of proxies."""
    
    proxies = []
    
    # Distribute quality tiers
    good_count = int(num_proxies * 0.5)  # 50%
    medium_count = int(num_proxies * 0.35)  # 35%
    poor_count = num_proxies - good_count - medium_count  # 15%
    
    # Generate good quality proxies
    for i in range(good_count):
        proxies.append(generate_test_proxy(i, 'good'))
    
    # Generate medium quality proxies
    for i in range(good_count, good_count + medium_count):
        proxies.append(generate_test_proxy(i, 'medium'))
    
    # Generate poor quality proxies
    for i in range(good_count + medium_count, num_proxies):
        proxies.append(generate_test_proxy(i, 'poor'))
    
    # Shuffle to mix quality tiers
    random.shuffle(proxies)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(proxies, f, indent=2, ensure_ascii=False)
        print(f"Generated {num_proxies} test proxies and saved to {output_file}")
    
    return proxies


if __name__ == '__main__':
    random.seed(42)  # For reproducibility
    
    output_file = '/home/engine/project/tests/data/test_proxies_100.json'
    proxies = generate_test_dataset(100, output_file)
    
    # Print statistics
    print(f"\n=== Test Proxy Dataset Statistics ===")
    print(f"Total proxies: {len(proxies)}")
    
    quality_tiers = {}
    for proxy in proxies:
        tier = proxy['quality_tier']
        quality_tiers[tier] = quality_tiers.get(tier, 0) + 1
    
    for tier, count in sorted(quality_tiers.items()):
        print(f"{tier.capitalize()}: {count} ({count/len(proxies)*100:.1f}%)")
    
    # Latency statistics
    latencies = [p['latency_ms'] for p in proxies if p['latency_ms'] < 9999]
    if latencies:
        print(f"\nLatency (valid proxies):")
        print(f"  Min: {min(latencies):.1f}ms")
        print(f"  Max: {max(latencies):.1f}ms")
        print(f"  Avg: {sum(latencies)/len(latencies):.1f}ms")
    
    down_count = sum(1 for p in proxies if p['latency_ms'] == 9999)
    print(f"\nDown/Unreachable: {down_count} ({down_count/len(proxies)*100:.1f}%)")
