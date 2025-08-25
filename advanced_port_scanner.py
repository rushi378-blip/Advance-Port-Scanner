#!/usr/bin/env python3
"""
Advanced Port Scanner with Advanced Features
Author: Rushi Patel
Description: A professional-grade port scanner for cybersecurity professionals
Features: Multi-threading, service fingerprinting, custom payloads, and advanced scanning techniques
"""

import socket
import threading
import time
import argparse
import sys
import json
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import ipaddress
import random
import struct

class AdvancedPortScanner:
    def __init__(self, target, ports, threads=100, timeout=3, scan_type="connect"):
        self.target = target
        self.ports = self._parse_ports(ports)
        self.threads = threads
        self.timeout = timeout
        self.scan_type = scan_type
        self.results = []
        self.lock = threading.Lock()
        
        # Service signatures for fingerprinting
        self.service_signatures = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            6379: "Redis",
            8080: "HTTP-Proxy",
            8443: "HTTPS-Alt"
        }
        
        # Custom payloads for different services
        self.custom_payloads = {
            80: b"GET / HTTP/1.1\r\nHost: {}\r\n\r\n",
            443: b"GET / HTTP/1.1\r\nHost: {}\r\n\r\n",
            22: b"SSH-2.0-OpenSSH_8.2p1\r\n",
            21: b"USER anonymous\r\n",
            25: b"EHLO {}\r\n",
            53: b"\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01"
        }

    def _parse_ports(self, ports_str):
        """Parse port ranges and individual ports"""
        ports = set()
        for port_range in ports_str.split(','):
            if '-' in port_range:
                start, end = map(int, port_range.split('-'))
                ports.update(range(start, end + 1))
            else:
                ports.add(int(port_range))
        return sorted(list(ports))

    def _resolve_target(self):
        """Resolve target to IP address"""
        try:
            if self.target.replace('.', '').isdigit():
                return self.target
            else:
                return socket.gethostbyname(self.target)
        except socket.gaierror:
            print(f"[!] Error: Cannot resolve hostname '{self.target}'")
            sys.exit(1)

    def _connect_scan(self, port):
        """Perform TCP connect scan"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, port))
            sock.close()
            
            if result == 0:
                service = self._identify_service(port)
                banner = self._get_banner(port)
                return {
                    'port': port,
                    'state': 'open',
                    'service': service,
                    'banner': banner,
                    'scan_type': 'connect'
                }
        except Exception as e:
            pass
        return None

    def _syn_scan(self, port):
        """Perform SYN scan (requires raw socket privileges)"""
        try:
            # Create raw socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            
            # Craft SYN packet
            source_port = random.randint(1024, 65535)
            seq_num = random.randint(1000000000, 2000000000)
            
            # TCP header
            tcp_header = struct.pack('!HHLLBBHHH',
                source_port, port, seq_num, 0, 5 << 4, 2, 8192, 0, 0)
            
            # IP header
            ip_header = struct.pack('!BBHHHBBH4s4s',
                69, 0, 40, 54321, 0, 255, 6, 0, socket.inet_aton('127.0.0.1'), 
                socket.inet_aton(self.target))
            
            packet = ip_header + tcp_header
            sock.sendto(packet, (self.target, 0))
            
            # Listen for response
            sock.settimeout(self.timeout)
            try:
                response = sock.recv(1024)
                if response:
                    # Parse response to check if port is open
                    tcp_header = response[20:40]
                    flags = struct.unpack('!BB', tcp_header[12:14])[1]
                    if flags & 0x12:  # SYN-ACK
                        service = self._identify_service(port)
                        return {
                            'port': port,
                            'state': 'open',
                            'service': service,
                            'banner': '',
                            'scan_type': 'syn'
                        }
            except socket.timeout:
                pass
            sock.close()
        except PermissionError:
            print(f"[!] SYN scan requires root/administrator privileges")
            return None
        except Exception as e:
            pass
        return None

    def _identify_service(self, port):
        """Identify service based on port number"""
        return self.service_signatures.get(port, "Unknown")

    def _get_banner(self, port):
        """Attempt to grab service banner"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.target, port))
            
            # Send custom payload if available
            if port in self.custom_payloads:
                payload = self.custom_payloads[port].format(self.target).encode()
                sock.send(payload)
            
            # Receive banner
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            return banner if banner else "No banner"
        except:
            return "No banner"

    def _udp_scan(self, port):
        """Perform UDP scan"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            # Send empty UDP packet
            sock.sendto(b"", (self.target, port))
            
            try:
                data, addr = sock.recvfrom(1024)
                sock.close()
                return {
                    'port': port,
                    'state': 'open',
                    'service': self._identify_service(port),
                    'banner': data.decode('utf-8', errors='ignore')[:100],
                    'scan_type': 'udp'
                }
            except socket.timeout:
                # Port might be open/filtered
                sock.close()
                return {
                    'port': port,
                    'state': 'open|filtered',
                    'service': self._identify_service(port),
                    'banner': 'No response',
                    'scan_type': 'udp'
                }
        except Exception as e:
            return None

    def scan_port(self, port):
        """Scan a single port based on scan type"""
        if self.scan_type == "connect":
            return self._connect_scan(port)
        elif self.scan_type == "syn":
            return self._syn_scan(port)
        elif self.scan_type == "udp":
            return self._udp_scan(port)
        return None

    def run_scan(self):
        """Execute the port scan"""
        print(f"[*] Starting {self.scan_type.upper()} scan of {self.target}")
        print(f"[*] Scanning {len(self.ports)} ports with {self.threads} threads")
        print(f"[*] Scan started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_port = {executor.submit(self.scan_port, port): port for port in self.ports}
            
            for future in as_completed(future_to_port):
                result = future.result()
                if result:
                    with self.lock:
                        self.results.append(result)
                        print(f"[+] {result['port']:5d}/tcp  {result['state']:12}  {result['service']:15}  {result['banner'][:30]}")
        
        end_time = time.time()
        scan_duration = end_time - start_time
        
        print("-" * 60)
        print(f"[*] Scan completed in {scan_duration:.2f} seconds")
        print(f"[*] Found {len(self.results)} open ports")
        
        return self.results

    def export_results(self, format_type="text", filename=None):
        """Export scan results in various formats"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"port_scan_{self.target}_{timestamp}"
        
        if format_type == "json":
            with open(f"{filename}.json", 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"[*] Results exported to {filename}.json")
        
        elif format_type == "csv":
            with open(f"{filename}.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['port', 'state', 'service', 'banner', 'scan_type'])
                writer.writeheader()
                writer.writerows(self.results)
            print(f"[*] Results exported to {filename}.csv")
        
        elif format_type == "text":
            with open(f"{filename}.txt", 'w') as f:
                f.write(f"Port Scan Results for {self.target}\n")
                f.write(f"Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("-" * 60 + "\n")
                for result in self.results:
                    f.write(f"{result['port']:5d}/tcp  {result['state']:12}  {result['service']:15}  {result['banner']}\n")
            print(f"[*] Results exported to {filename}.txt")

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Port Scanner with Advanced Features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python advanced_port_scanner.py 192.168.1.1 -p 1-1000
  python advanced_port_scanner.py example.com -p 80,443,8080 -t 200
  python advanced_port_scanner.py 10.0.0.1 -p 1-65535 -s syn --export json
        """
    )
    
    parser.add_argument("target", help="Target IP address or hostname")
    parser.add_argument("-p", "--ports", default="1-1000", help="Port range (e.g., 80,443,8080 or 1-1000)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Number of threads (default: 100)")
    parser.add_argument("--timeout", type=int, default=3, help="Connection timeout in seconds (default: 3)")
    parser.add_argument("-s", "--scan-type", choices=["connect", "syn", "udp"], default="connect", 
                       help="Scan type (default: connect)")
    parser.add_argument("--export", choices=["text", "json", "csv"], help="Export results to file")
    parser.add_argument("--output", help="Output filename (without extension)")
    
    args = parser.parse_args()
    
    try:
        # Validate target
        scanner = AdvancedPortScanner(
            target=args.target,
            ports=args.ports,
            threads=args.threads,
            timeout=args.timeout,
            scan_type=args.scan_type
        )
        
        # Resolve target
        scanner.target = scanner._resolve_target()
        
        # Run scan
        results = scanner.run_scan()
        
        # Export results if requested
        if args.export:
            scanner.export_results(args.export, args.output)
        
        # Summary
        if results:
            print(f"\n[*] Summary: {len(results)} open ports found on {scanner.target}")
            for result in results:
                print(f"    Port {result['port']}: {result['service']} ({result['state']})")
        else:
            print(f"\n[*] No open ports found on {scanner.target}")
            
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
