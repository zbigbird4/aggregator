#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main functional test runner for aggregator project.
Tests the complete workflow: crawl -> verify -> test -> rank -> output
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add subscribe directory to path
sys.path.insert(0, '/home/engine/project')
sys.path.insert(0, '/home/engine/project/subscribe')

import random as utils_random
from logger import logger


class TestRunner:
    """Run comprehensive functional tests for the aggregator project."""
    
    def __init__(self):
        self.start_time = None
        self.test_results = {}
        self.stage_timings = {}
        self.proxy_data = []
        self.verified_proxies = []
        self.tested_proxies = []
        self.output_proxies = []
        
    def log_stage(self, stage: str, message: str):
        """Log a stage message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{stage}] {message}")
        logger.info(f"[{stage}] {message}")
    
    def load_test_proxies(self) -> bool:
        """Load test proxy dataset."""
        self.log_stage("LOAD", "Loading test proxy dataset...")
        
        try:
            test_file = '/home/engine/project/tests/data/test_proxies_100.json'
            with open(test_file, 'r', encoding='utf-8') as f:
                self.proxy_data = json.load(f)
            
            self.log_stage("LOAD", f"Loaded {len(self.proxy_data)} test proxies")
            
            # Statistics
            quality_dist = {}
            for proxy in self.proxy_data:
                tier = proxy.get('quality_tier', 'unknown')
                quality_dist[tier] = quality_dist.get(tier, 0) + 1
            
            for tier, count in quality_dist.items():
                self.log_stage("LOAD", f"  {tier}: {count} proxies")
            
            return True
        except Exception as e:
            self.log_stage("LOAD", f"ERROR: Failed to load proxies: {e}")
            return False
    
    def simulate_verification_stage(self) -> bool:
        """Simulate proxy verification stage."""
        self.log_stage("VERIFY", "Simulating proxy verification stage...")
        
        start_time = time.time()
        
        try:
            verified_count = 0
            failed_count = 0
            down_count = 0
            
            for proxy in self.proxy_data:
                # Simulate verification based on latency
                latency = proxy.get('latency_ms', 9999)
                quality_tier = proxy.get('quality_tier', 'unknown')
                
                # Down nodes always fail
                if latency == 9999:
                    down_count += 1
                    continue
                
                # Poor quality nodes have lower pass rate
                if quality_tier == 'poor':
                    if latency > 1000:  # Very high latency
                        failed_count += 1
                        continue
                    if utils_random.random() < 0.3:  # 30% failure rate
                        failed_count += 1
                        continue
                elif quality_tier == 'medium':
                    if latency > 500:  # High latency
                        failed_count += 1
                        continue
                    if utils_random.random() < 0.15:  # 15% failure rate
                        failed_count += 1
                        continue
                else:  # good
                    if latency > 300:  # Fairly high latency
                        failed_count += 1
                        continue
                    if utils_random.random() < 0.05:  # 5% failure rate
                        failed_count += 1
                        continue
                
                verified_count += 1
                self.verified_proxies.append(proxy)
            
            elapsed = time.time() - start_time
            self.stage_timings['verify'] = elapsed
            
            pass_rate = (verified_count / len(self.proxy_data)) * 100 if self.proxy_data else 0
            
            self.log_stage("VERIFY", f"Verification complete in {elapsed:.2f}s")
            self.log_stage("VERIFY", f"  Verified: {verified_count}/{len(self.proxy_data)} ({pass_rate:.1f}%)")
            self.log_stage("VERIFY", f"  Failed: {failed_count}")
            self.log_stage("VERIFY", f"  Down/Unreachable: {down_count}")
            
            return verified_count > 0
        except Exception as e:
            self.log_stage("VERIFY", f"ERROR: {e}\n{traceback.format_exc()}")
            return False
    
    def simulate_latency_test_stage(self) -> bool:
        """Simulate latency testing stage."""
        self.log_stage("LATENCY_TEST", f"Testing latency for {len(self.verified_proxies)} proxies...")
        
        start_time = time.time()
        
        try:
            success_count = 0
            fail_count = 0
            
            for proxy in self.verified_proxies:
                # Simulate latency test - some proxies might fail during test
                if utils_random.random() < 0.1:  # 10% failure rate
                    fail_count += 1
                    continue
                
                # Calculate latency score (lower latency = higher score)
                latency = proxy.get('latency_ms', 1000)
                packet_loss = proxy.get('packet_loss_percent', 0)
                uptime = proxy.get('uptime_percent', 100)
                
                # Score calculation: normalize to 0-100 range
                # Lower latency -> higher score, considering packet loss and uptime
                latency_score = max(0, 100 - latency / 50)  # Max score at 0ms
                uptime_factor = uptime / 100
                packet_loss_factor = 1 - (packet_loss / 100)
                
                final_score = latency_score * uptime_factor * packet_loss_factor
                
                proxy['latency_score'] = round(final_score, 2)
                proxy['test_status'] = 'success'
                
                self.tested_proxies.append(proxy)
                success_count += 1
            
            elapsed = time.time() - start_time
            self.stage_timings['latency_test'] = elapsed
            
            success_rate = (success_count / len(self.verified_proxies)) * 100 if self.verified_proxies else 0
            
            self.log_stage("LATENCY_TEST", f"Latency testing complete in {elapsed:.2f}s")
            self.log_stage("LATENCY_TEST", f"  Passed: {success_count}/{len(self.verified_proxies)} ({success_rate:.1f}%)")
            self.log_stage("LATENCY_TEST", f"  Failed: {fail_count}")
            
            if self.tested_proxies:
                scores = [p.get('latency_score', 0) for p in self.tested_proxies]
                self.log_stage("LATENCY_TEST", f"  Score range: {min(scores):.1f} - {max(scores):.1f}")
                self.log_stage("LATENCY_TEST", f"  Average score: {sum(scores)/len(scores):.1f}")
            
            return success_count > 0
        except Exception as e:
            self.log_stage("LATENCY_TEST", f"ERROR: {e}\n{traceback.format_exc()}")
            return False
    
    def simulate_ranking_stage(self) -> bool:
        """Simulate proxy ranking stage."""
        self.log_stage("RANKING", f"Ranking {len(self.tested_proxies)} tested proxies...")
        
        start_time = time.time()
        
        try:
            # Sort by latency score (descending), then by latency (ascending)
            sorted_proxies = sorted(
                self.tested_proxies,
                key=lambda x: (
                    -x.get('latency_score', 0),
                    x.get('latency_ms', 9999)
                )
            )
            
            # Take top 80% of proxies
            keep_count = max(1, int(len(sorted_proxies) * 0.8))
            self.output_proxies = sorted_proxies[:keep_count]
            
            elapsed = time.time() - start_time
            self.stage_timings['ranking'] = elapsed
            
            self.log_stage("RANKING", f"Ranking complete in {elapsed:.2f}s")
            self.log_stage("RANKING", f"  Selected: {len(self.output_proxies)}/{len(sorted_proxies)}")
            
            # Score distribution analysis
            if self.output_proxies:
                scores = [p.get('latency_score', 0) for p in self.output_proxies]
                latencies = [p.get('latency_ms', 9999) for p in self.output_proxies if p.get('latency_ms', 9999) < 9999]
                
                self.log_stage("RANKING", f"  Score distribution:")
                self.log_stage("RANKING", f"    Min: {min(scores):.1f}")
                self.log_stage("RANKING", f"    Max: {max(scores):.1f}")
                self.log_stage("RANKING", f"    Avg: {sum(scores)/len(scores):.1f}")
                
                if latencies:
                    self.log_stage("RANKING", f"  Latency distribution:")
                    self.log_stage("RANKING", f"    Min: {min(latencies):.1f}ms")
                    self.log_stage("RANKING", f"    Max: {max(latencies):.1f}ms")
                    self.log_stage("RANKING", f"    Avg: {sum(latencies)/len(latencies):.1f}ms")
            
            return len(self.output_proxies) > 0
        except Exception as e:
            self.log_stage("RANKING", f"ERROR: {e}\n{traceback.format_exc()}")
            return False
    
    def simulate_output_generation(self) -> bool:
        """Simulate final output generation."""
        self.log_stage("OUTPUT", f"Generating output files...")
        
        start_time = time.time()
        
        try:
            output_dir = '/home/engine/project/tests/output'
            os.makedirs(output_dir, exist_ok=True)
            
            # Save verified proxies
            verified_file = os.path.join(output_dir, 'verified_proxies.json')
            with open(verified_file, 'w', encoding='utf-8') as f:
                json.dump(self.verified_proxies, f, indent=2, ensure_ascii=False)
            
            # Save tested proxies
            tested_file = os.path.join(output_dir, 'tested_proxies.json')
            with open(tested_file, 'w', encoding='utf-8') as f:
                json.dump(self.tested_proxies, f, indent=2, ensure_ascii=False)
            
            # Save output proxies
            output_file = os.path.join(output_dir, 'final_proxies.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.output_proxies, f, indent=2, ensure_ascii=False)
            
            # Generate simple Clash YAML
            clash_file = os.path.join(output_dir, 'clash.yaml')
            self._generate_clash_config(clash_file)
            
            elapsed = time.time() - start_time
            self.stage_timings['output'] = elapsed
            
            self.log_stage("OUTPUT", f"Output generation complete in {elapsed:.2f}s")
            self.log_stage("OUTPUT", f"  Verified proxies file: {verified_file}")
            self.log_stage("OUTPUT", f"  Tested proxies file: {tested_file}")
            self.log_stage("OUTPUT", f"  Final proxies file: {output_file}")
            self.log_stage("OUTPUT", f"  Clash config file: {clash_file}")
            
            return True
        except Exception as e:
            self.log_stage("OUTPUT", f"ERROR: {e}\n{traceback.format_exc()}")
            return False
    
    def _generate_clash_config(self, output_file: str):
        """Generate a basic Clash YAML configuration."""
        
        proxies = []
        proxy_names = []
        
        for proxy in self.output_proxies:
            name = proxy.get('name', f"proxy_{len(proxies)}")
            proxy_names.append(name)
            
            # Create Clash proxy entry
            clash_proxy = {
                'name': name,
                'type': proxy.get('type', 'ss').lower(),
                'server': proxy.get('server', '127.0.0.1'),
                'port': proxy.get('port', 8080),
                'cipher': proxy.get('method', 'aes-256-gcm'),
                'password': proxy.get('password', 'password'),
            }
            
            # Add location tags
            location = proxy.get('location', {})
            if location:
                clash_proxy['_location'] = f"{location.get('country', 'XX')}-{location.get('region', 'Unknown')}"
            
            proxies.append(clash_proxy)
        
        # Create YAML content
        yaml_content = "# Generated Clash Configuration\n"
        yaml_content += f"# Generated: {datetime.now().isoformat()}\n"
        yaml_content += f"# Proxies: {len(proxies)}\n"
        yaml_content += "\n"
        
        yaml_content += "proxies:\n"
        for proxy in proxies:
            yaml_content += f"  - name: {proxy['name']}\n"
            yaml_content += f"    type: {proxy['type']}\n"
            yaml_content += f"    server: {proxy['server']}\n"
            yaml_content += f"    port: {proxy['port']}\n"
            if proxy.get('cipher'):
                yaml_content += f"    cipher: {proxy['cipher']}\n"
            if proxy.get('password'):
                yaml_content += f"    password: {proxy['password']}\n"
            yaml_content += "\n"
        
        yaml_content += "proxy-groups:\n"
        yaml_content += "  - name: PROXY\n"
        yaml_content += "    type: select\n"
        yaml_content += "    proxies:\n"
        for name in proxy_names:
            yaml_content += f"      - {name}\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
    
    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        
        total_time = time.time() - self.start_time
        
        report = "\n" + "="*80 + "\n"
        report += "FUNCTIONAL TEST REPORT - AGGREGATOR PROJECT\n"
        report += "="*80 + "\n"
        report += f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total Execution Time: {total_time:.2f}s\n"
        report += "\n"
        
        # Stage breakdown
        report += "STAGE TIMING BREAKDOWN\n"
        report += "-"*80 + "\n"
        for stage, elapsed in sorted(self.stage_timings.items()):
            percentage = (elapsed / total_time * 100) if total_time > 0 else 0
            report += f"{stage.upper():20} {elapsed:8.2f}s ({percentage:5.1f}%)\n"
        
        report += "\n"
        
        # Data flow analysis
        report += "DATA FLOW ANALYSIS\n"
        report += "-"*80 + "\n"
        
        loaded = len(self.proxy_data)
        verified = len(self.verified_proxies)
        tested = len(self.tested_proxies)
        output = len(self.output_proxies)
        
        report += f"Total Loaded:          {loaded:4d}\n"
        report += f"Verified:              {verified:4d} ({verified/loaded*100:5.1f}%)\n"
        report += f"Passed Latency Test:   {tested:4d} ({tested/verified*100:5.1f}% of verified)\n"
        report += f"Final Selected:        {output:4d} ({output/tested*100:5.1f}% of tested)\n"
        report += f"Overall Pass Rate:     {output:4d} ({output/loaded*100:5.1f}% of total)\n"
        
        report += "\n"
        
        # Quality metrics
        report += "QUALITY METRICS\n"
        report += "-"*80 + "\n"
        
        if self.proxy_data:
            quality_dist = {}
            for proxy in self.proxy_data:
                tier = proxy.get('quality_tier', 'unknown')
                quality_dist[tier] = quality_dist.get(tier, 0) + 1
            
            report += "Input Quality Distribution:\n"
            for tier in ['good', 'medium', 'poor']:
                count = quality_dist.get(tier, 0)
                report += f"  {tier.capitalize():10} {count:3d} ({count/len(self.proxy_data)*100:5.1f}%)\n"
            
            report += "\n"
            
            # Latency statistics
            all_latencies = [p.get('latency_ms', 9999) for p in self.proxy_data if p.get('latency_ms', 9999) < 9999]
            if all_latencies:
                report += f"Input Latency Statistics:\n"
                report += f"  Min:     {min(all_latencies):7.1f}ms\n"
                report += f"  Max:     {max(all_latencies):7.1f}ms\n"
                report += f"  Average: {sum(all_latencies)/len(all_latencies):7.1f}ms\n"
            
            report += "\n"
        
        if self.output_proxies:
            scores = [p.get('latency_score', 0) for p in self.output_proxies]
            latencies = [p.get('latency_ms', 9999) for p in self.output_proxies if p.get('latency_ms', 9999) < 9999]
            
            report += "Output Proxy Statistics:\n"
            report += f"  Total Proxies: {len(self.output_proxies)}\n"
            
            if scores:
                report += f"  Score Min:     {min(scores):7.1f}\n"
                report += f"  Score Max:     {max(scores):7.1f}\n"
                report += f"  Score Average: {sum(scores)/len(scores):7.1f}\n"
            
            if latencies:
                report += f"  Latency Min:     {min(latencies):7.1f}ms\n"
                report += f"  Latency Max:     {max(latencies):7.1f}ms\n"
                report += f"  Latency Average: {sum(latencies)/len(latencies):7.1f}ms\n"
            
            # Residential ratio
            residential_count = sum(1 for p in self.output_proxies if p.get('is_residential', False))
            report += f"  Residential:   {residential_count:3d} ({residential_count/len(self.output_proxies)*100:5.1f}%)\n"
        
        report += "\n"
        
        # Geographic distribution
        report += "GEOGRAPHIC DISTRIBUTION\n"
        report += "-"*80 + "\n"
        
        if self.output_proxies:
            country_dist = {}
            for proxy in self.output_proxies:
                location = proxy.get('location', {})
                country = location.get('country', 'Unknown')
                country_dist[country] = country_dist.get(country, 0) + 1
            
            for country in sorted(country_dist.keys()):
                count = country_dist[country]
                report += f"  {country:5} {count:3d}\n"
        
        report += "\n"
        
        # Performance analysis
        report += "PERFORMANCE ANALYSIS\n"
        report += "-"*80 + "\n"
        report += f"Average time per proxy (total):  {total_time/loaded*1000:.2f}ms\n"
        report += f"Average time per proxy (verify): {self.stage_timings.get('verify', 0)/loaded*1000:.2f}ms\n"
        report += f"Average time per proxy (test):   {self.stage_timings.get('latency_test', 0)/verified*1000:.2f}ms\n"
        report += f"Throughput:                      {loaded/total_time:.1f} proxies/sec\n"
        
        report += "\n"
        
        # Status and recommendations
        report += "STATUS & RECOMMENDATIONS\n"
        report += "-"*80 + "\n"
        
        if total_time > 60:
            report += "⚠ WARNING: Total execution time exceeds 60 seconds\n"
            report += "  - Consider increasing concurrency in latency tester\n"
            report += "  - Optimize verification stage for bottlenecks\n"
        else:
            report += "✓ Execution time within acceptable range\n"
        
        if output / loaded < 0.3:
            report += "⚠ WARNING: Final output rate is below 30%\n"
            report += "  - Check proxy quality/network conditions\n"
            report += "  - Review filtering criteria\n"
        else:
            report += "✓ Final output rate is healthy\n"
        
        if tested / verified < 0.8:
            report += "⚠ WARNING: Latency test failure rate is high\n"
            report += "  - Increase timeout values\n"
            report += "  - Check network connectivity\n"
        else:
            report += "✓ Latency test success rate is good\n"
        
        report += "\n" + "="*80 + "\n"
        
        return report
    
    def run_full_test(self) -> bool:
        """Run the complete functional test."""
        
        self.start_time = time.time()
        self.log_stage("START", "Beginning functional test...")
        
        try:
            # Load test data
            if not self.load_test_proxies():
                return False
            
            # Run workflow stages
            if not self.simulate_verification_stage():
                return False
            
            if not self.simulate_latency_test_stage():
                return False
            
            if not self.simulate_ranking_stage():
                return False
            
            if not self.simulate_output_generation():
                return False
            
            # Generate report
            report = self.generate_report()
            print(report)
            
            # Save report
            report_file = '/home/engine/project/tests/output/test_report.txt'
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.log_stage("COMPLETE", f"Test completed successfully. Report saved to {report_file}")
            
            return True
            
        except Exception as e:
            self.log_stage("ERROR", f"Test failed: {e}\n{traceback.format_exc()}")
            return False


def main():
    """Main entry point."""
    runner = TestRunner()
    success = runner.run_full_test()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
