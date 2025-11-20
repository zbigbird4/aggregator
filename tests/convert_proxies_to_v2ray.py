#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert test proxies JSON to V2Ray subscription format for testing.
"""

import json
import base64
from typing import List, Dict, Any


def vmess_to_link(proxy: Dict[str, Any]) -> str:
    """Convert a proxy dict to V2Ray vmess:// link."""
    
    # Create vmess config object
    config = {
        "v": "2",
        "ps": proxy.get('name', 'proxy'),
        "add": proxy.get('server', '127.0.0.1'),
        "port": str(proxy.get('port', 8080)),
        "id": f"{proxy.get('id', 'test-id')}-uuid-1234-5678-9abcdef",
        "aid": "0",
        "net": "tcp",
        "type": "none",
        "host": "",
        "path": "",
        "tls": "none"
    }
    
    json_str = json.dumps(config, separators=(',', ':'))
    encoded = base64.b64encode(json_str.encode()).decode()
    
    return f"vmess://{encoded}"


def ss_to_link(proxy: Dict[str, Any]) -> str:
    """Convert a proxy dict to Shadowsocks ss:// link."""
    
    method = proxy.get('method', 'aes-256-gcm')
    password = proxy.get('password', 'testpassword')
    server = proxy.get('server', '127.0.0.1')
    port = proxy.get('port', 8080)
    name = proxy.get('name', 'proxy')
    
    # Format: ss://method:password@server:port#remarks
    auth = base64.b64encode(f"{method}:{password}".encode()).decode()
    url = f"ss://{auth}@{server}:{port}#{name}"
    
    return url


def trojan_to_link(proxy: Dict[str, Any]) -> str:
    """Convert a proxy dict to Trojan trojan:// link."""
    
    password = proxy.get('password', 'testpassword')
    server = proxy.get('server', '127.0.0.1')
    port = proxy.get('port', 8080)
    name = proxy.get('name', 'proxy')
    
    # Format: trojan://password@server:port?allowInsecure=1#remarks
    url = f"trojan://{password}@{server}:{port}?allowInsecure=1#{name}"
    
    return url


def proxy_to_link(proxy: Dict[str, Any]) -> str:
    """Convert a proxy dict to appropriate subscription link format."""
    
    proxy_type = proxy.get('type', 'vmess').lower()
    
    if proxy_type in ['ss']:
        return ss_to_link(proxy)
    elif proxy_type in ['trojan']:
        return trojan_to_link(proxy)
    else:  # Default to vmess
        return vmess_to_link(proxy)


def convert_proxies(input_file: str, output_file: str) -> None:
    """Convert proxy JSON to V2Ray subscription format."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        proxies = json.load(f)
    
    # Generate proxy links
    links = []
    for proxy in proxies:
        try:
            link = proxy_to_link(proxy)
            links.append(link)
        except Exception as e:
            print(f"Error converting proxy {proxy.get('name', 'unknown')}: {e}")
    
    # Create subscription content
    content = '\n'.join(links)
    
    # Encode to base64 for standard subscription format
    encoded = base64.b64encode(content.encode()).decode()
    
    # Save both formats
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    subscription_file = output_file.replace('.txt', '_subscription.txt')
    with open(subscription_file, 'w', encoding='utf-8') as f:
        f.write(encoded)
    
    print(f"Converted {len(links)} proxies")
    print(f"Raw format saved to: {output_file}")
    print(f"Subscription format saved to: {subscription_file}")
    
    return links


if __name__ == '__main__':
    input_file = '/home/engine/project/tests/data/test_proxies_100.json'
    output_file = '/home/engine/project/tests/data/test_proxies_100.txt'
    
    links = convert_proxies(input_file, output_file)
    
    print(f"\n=== Conversion Summary ===")
    print(f"Total links generated: {len(links)}")
    if links:
        print(f"First link: {links[0][:80]}...")
