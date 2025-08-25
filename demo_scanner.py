#!/usr/bin/env python3
"""
Demo Script for Advanced Port Scanner
This script demonstrates various scanning techniques and use cases
"""

import time
import json
from advanced_port_scanner import AdvancedPortScanner

def demo_basic_scan():
    """Demonstrate basic port scanning"""
    print("🔍 Demo 1: Basic Port Scan")
    print("=" * 50)
    
    # Create scanner instance
    scanner = AdvancedPortScanner(
        target="127.0.0.1",
        ports="80,443,8080,22,3306",
        threads=50,
        timeout=2
    )
    
    print(f"Target: {scanner.target}")
    print(f"Ports: {scanner.ports}")
    print(f"Threads: {scanner.threads}")
    print(f"Timeout: {scanner.timeout}s")
    print()
    
    # Run scan
    results = scanner.run_scan()
    
    # Export results
    if results:
        scanner.export_results("json", "demo_basic_scan")
        scanner.export_results("csv", "demo_basic_scan")
    
    print("\n" + "=" * 50)
    return results

def demo_port_range_scan():
    """Demonstrate scanning a port range"""
    print("🔍 Demo 2: Port Range Scan")
    print("=" * 50)
    
    scanner = AdvancedPortScanner(
        target="127.0.0.1",
        ports="1-100",
        threads=100,
        timeout=1
    )
    
    print(f"Scanning ports 1-100 on {scanner.target}")
    print("This will test common low-numbered ports...")
    print()
    
    # Run scan
    results = scanner.run_scan()
    
    if results:
        print(f"\nFound {len(results)} open ports in range 1-100")
        for result in results:
            print(f"  Port {result['port']}: {result['service']}")
    
    print("\n" + "=" * 50)
    return results

def demo_service_fingerprinting():
    """Demonstrate service fingerprinting capabilities"""
    print("🔍 Demo 3: Service Fingerprinting")
    print("=" * 50)
    
    # Common web service ports
    web_ports = "80,443,8080,8443,3000,5000,8000"
    
    scanner = AdvancedPortScanner(
        target="127.0.0.1",
        ports=web_ports,
        threads=20,
        timeout=3
    )
    
    print("Testing web service ports with banner grabbing...")
    print(f"Ports: {web_ports}")
    print()
    
    # Run scan
    results = scanner.run_scan()
    
    if results:
        print("\nService Details:")
        for result in results:
            print(f"  Port {result['port']}:")
            print(f"    Service: {result['service']}")
            print(f"    Banner: {result['banner'][:100]}...")
            print()
    
    print("=" * 50)
    return results

def demo_network_discovery():
    """Demonstrate network discovery capabilities"""
    print("🔍 Demo 4: Network Discovery Simulation")
    print("=" * 50)
    
    # Simulate scanning multiple hosts
    hosts = ["127.0.0.1", "localhost"]
    common_ports = "22,23,25,53,80,110,143,443,993,995,3306,3389,5432,5900,6379,8080"
    
    print("Simulating network discovery scan...")
    print(f"Hosts: {', '.join(hosts)}")
    print(f"Common ports: {common_ports}")
    print()
    
    all_results = {}
    
    for host in hosts:
        print(f"Scanning {host}...")
        scanner = AdvancedPortScanner(
            target=host,
            ports=common_ports,
            threads=30,
            timeout=2
        )
        
        results = scanner.run_scan()
        if results:
            all_results[host] = results
            print(f"  Found {len(results)} open ports on {host}")
        else:
            print(f"  No open ports found on {host}")
        print()
    
    # Summary
    if all_results:
        print("Network Discovery Summary:")
        for host, results in all_results.items():
            print(f"  {host}: {len(results)} open ports")
            for result in results:
                print(f"    {result['port']}: {result['service']}")
    
    print("=" * 50)
    return all_results

def demo_export_formats():
    """Demonstrate different export formats"""
    print("🔍 Demo 5: Export Format Demonstration")
    print("=" * 50)
    
    scanner = AdvancedPortScanner(
        target="127.0.0.1",
        ports="80,443,22",
        threads=10,
        timeout=2
    )
    
    print("Testing different export formats...")
    print()
    
    # Run scan
    results = scanner.run_scan()
    
    if results:
        # Export in all formats
        formats = ["text", "json", "csv"]
        for fmt in formats:
            filename = f"demo_export_{fmt}"
            scanner.export_results(fmt, filename)
            print(f"Exported to {filename}.{fmt}")
    
    print("=" * 50)
    return results

def demo_performance_comparison():
    """Demonstrate performance with different thread counts"""
    print("🔍 Demo 6: Performance Comparison")
    print("=" * 50)
    
    ports = "1-1000"
    thread_counts = [10, 50, 100, 200]
    
    print("Comparing scan performance with different thread counts...")
    print(f"Port range: {ports}")
    print()
    
    performance_results = {}
    
    for threads in thread_counts:
        print(f"Testing with {threads} threads...")
        
        start_time = time.time()
        
        scanner = AdvancedPortScanner(
            target="127.0.0.1",
            ports=ports,
            threads=threads,
            timeout=1
        )
        
        results = scanner.run_scan()
        
        end_time = time.time()
        duration = end_time - start_time
        
        performance_results[threads] = {
            'duration': duration,
            'ports_found': len(results) if results else 0
        }
        
        print(f"  Duration: {duration:.2f}s")
        print(f"  Open ports found: {len(results) if results else 0}")
        print()
    
    # Performance summary
    print("Performance Summary:")
    for threads, data in performance_results.items():
        print(f"  {threads:3d} threads: {data['duration']:6.2f}s ({data['ports_found']:2d} ports)")
    
    print("=" * 50)
    return performance_results

def main():
    """Run all demos"""
    print("🚀 Advanced Port Scanner - Demo Suite")
    print("=" * 60)
    print("This demo will showcase various scanning techniques and features.")
    print("Make sure you have permission to scan the target systems!")
    print("=" * 60)
    print()
    
    # Run demos
    demos = [
        demo_basic_scan,
        demo_port_range_scan,
        demo_service_fingerprinting,
        demo_network_discovery,
        demo_export_formats,
        demo_performance_comparison
    ]
    
    results = {}
    
    for i, demo in enumerate(demos, 1):
        try:
            print(f"\n🎯 Running Demo {i}/{len(demos)}")
            result = demo()
            results[f"demo_{i}"] = result
            time.sleep(1)  # Brief pause between demos
        except Exception as e:
            print(f"Error in demo {i}: {e}")
            continue
    
    # Final summary
    print("\n🎉 Demo Suite Complete!")
    print("=" * 60)
    print("All demonstrations have been completed.")
    print("Check the generated files for exported results.")
    print("\nGenerated files:")
    print("- demo_*.json: JSON format results")
    print("- demo_*.csv: CSV format results")
    print("- demo_*.txt: Text format results")
    print("\nRemember to use this tool responsibly and ethically!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Demo interrupted by user")
    except Exception as e:
        print(f"\n[!] Demo error: {e}")
