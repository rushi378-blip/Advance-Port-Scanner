# 🔍 Advanced Port Scanner with Advanced Features

A professional-grade port scanner designed for cybersecurity professionals, penetration testers, and red team operators. This tool demonstrates advanced scanning techniques, service fingerprinting, and custom payload generation.

## ⭐ Features

### 🚀 **Advanced Scanning Techniques**
- **TCP Connect Scan**: Standard connection-based port scanning
- **SYN Scan**: Stealthy SYN packet scanning (requires elevated privileges)
- **UDP Scan**: UDP port enumeration with response analysis
- **Multi-threaded**: High-performance concurrent scanning

### 🔍 **Service Fingerprinting**
- Automatic service identification for common ports
- Custom payload generation for specific services
- Banner grabbing capabilities
- Service version detection

### 📊 **Output & Export**
- Multiple export formats (JSON, CSV, TXT)
- Real-time scan progress display
- Detailed scan reports with timestamps
- Customizable output filenames

### 🛡️ **Professional Features**
- Hostname resolution support
- Configurable timeout and thread settings
- Error handling and graceful degradation
- Professional logging and status updates

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.7+ required
python --version

# Install dependencies (if any)
pip install -r requirements.txt
```

### Basic Usage
```bash
# Scan common ports on a target
python advanced_port_scanner.py 192.168.1.1

# Scan specific port range
python advanced_port_scanner.py example.com -p 1-1000

# High-speed scan with custom threads
python advanced_port_scanner.py 10.0.0.1 -p 80,443,8080 -t 200

# SYN scan (requires admin/root privileges)
python advanced_port_scanner.py target.com -p 1-65535 -s syn

# Export results to JSON
python advanced_port_scanner.py target.com -p 1-1000 --export json
```

## 📖 Detailed Usage

### Command Line Arguments

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `target` | Target IP or hostname | Required | `192.168.1.1` |
| `-p, --ports` | Port range or list | `1-1000` | `80,443,8080` or `1-1000` |
| `-t, --threads` | Number of threads | `100` | `200` |
| `--timeout` | Connection timeout (seconds) | `3` | `5` |
| `-s, --scan-type` | Scan type | `connect` | `syn`, `udp` |
| `--export` | Export format | None | `json`, `csv`, `text` |
| `--output` | Custom output filename | Auto-generated | `my_scan_results` |

### Scan Types

#### 1. **Connect Scan** (Default)
```bash
python advanced_port_scanner.py target.com -p 1-1000
```
- Establishes full TCP connections
- Most reliable but easily detected
- No special privileges required

#### 2. **SYN Scan**
```bash
python advanced_port_scanner.py target.com -p 1-1000 -s syn
```
- Sends SYN packets without completing handshake
- Stealthier than connect scan
- Requires administrator/root privileges
- May bypass some firewalls

#### 3. **UDP Scan**
```bash
python advanced_port_scanner.py target.com -p 53,67,123 -s udp
```
- Scans UDP ports for open services
- Useful for DNS, DHCP, NTP services
- Slower due to timeout handling

### Advanced Examples

#### Network Discovery
```bash
# Scan entire subnet for common services
for ip in {1..254}; do
    python advanced_port_scanner.py 192.168.1.$ip -p 22,80,443,3389
done
```

#### Web Application Assessment
```bash
# Focus on web services with custom output
python advanced_port_scanner.py webapp.com -p 80,443,8080,8443 --export json --output web_scan
```

#### Stealth Operations
```bash
# Slow, stealthy scan to avoid detection
python advanced_port_scanner.py target.com -p 1-65535 -t 10 --timeout 5
```

## 🔧 Installation

### Method 1: Direct Download
```bash
git clone https://github.com/rushi378-blip/advanced-port-scanner.git
cd advanced-port-scanner
python advanced_port_scanner.py --help
```

### Method 2: Requirements File
```bash
# Create requirements.txt (if needed)
echo "socket" > requirements.txt
echo "threading" >> requirements.txt
echo "argparse" >> requirements.txt

# Install dependencies
pip install -r requirements.txt
```

## 📊 Output Examples

### Console Output
```
[*] Starting CONNECT scan of 192.168.1.1
[*] Scanning 1000 ports with 100 threads
[*] Scan started at 2024-01-15 14:30:25
------------------------------------------------------------
[+]    22/tcp  open          SSH            SSH-2.0-OpenSSH_8.2p1
[+]    80/tcp  open          HTTP           HTTP/1.1 200 OK
[+]   443/tcp  open          HTTPS          HTTP/1.1 200 OK
[+]  3306/tcp  open          MySQL          MySQL
------------------------------------------------------------
[*] Scan completed in 12.45 seconds
[*] Found 3 open ports
```

### JSON Export
```json
[
  {
    "port": 22,
    "state": "open",
    "service": "SSH",
    "banner": "SSH-2.0-OpenSSH_8.2p1",
    "scan_type": "connect"
  },
  {
    "port": 80,
    "state": "open",
    "service": "HTTP",
    "banner": "HTTP/1.1 200 OK",
    "scan_type": "connect"
  }
]
```

## 🛡️ Security Considerations

### Legal and Ethical Use
- **Only scan systems you own or have explicit permission to test**
- **Respect rate limits and network policies**
- **Use responsibly in authorized penetration testing engagements**
- **Comply with local laws and regulations**

### Detection Avoidance
- Use appropriate scan timing to avoid triggering IDS/IPS
- Consider using SYN scans for stealth operations
- Implement random delays between scans
- Use legitimate-looking source addresses when possible

### Best Practices
- Document all scanning activities
- Use in controlled testing environments
- Respect network infrastructure and bandwidth
- Follow responsible disclosure practices

## 🧪 Testing and Validation

### Test Environment Setup
```bash
# Set up test target (example)
# Run web server on localhost
python -m http.server 8080

# Test scanner on localhost
python advanced_port_scanner.py localhost -p 8080
```

### Validation Commands
```bash
# Verify port states with netstat
netstat -an | grep :8080

# Check with nmap for comparison
nmap -p 8080 localhost
```

## 🔍 Troubleshooting

### Common Issues

#### Permission Denied (SYN Scan)
```bash
# Error: SYN scan requires root/administrator privileges
# Solution: Run with elevated privileges
sudo python advanced_port_scanner.py target.com -s syn
```

#### Slow Scan Performance
```bash
# Increase thread count
python advanced_port_scanner.py target.com -t 500

# Reduce timeout for faster results
python advanced_port_scanner.py target.com --timeout 1
```

#### Hostname Resolution Issues
```bash
# Verify DNS resolution
nslookup target.com

# Use IP address directly if needed
python advanced_port_scanner.py 192.168.1.1
```

## 📈 Performance Optimization

### Threading Guidelines
- **Low bandwidth**: 50-100 threads
- **High bandwidth**: 200-500 threads
- **Local network**: 500-1000 threads
- **Internet targets**: 100-200 threads

### Timeout Settings
- **Fast LAN**: 1-2 seconds
- **Slow WAN**: 3-5 seconds
- **High-latency**: 5-10 seconds

## 🤝 Contributing

We welcome contributions from the cybersecurity community!

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Areas for Improvement
- Additional scan types (FIN, XMAS, NULL)
- More service signatures
- Custom payload templates
- Integration with other security tools
- Performance optimizations

## 📚 Learning Resources

### Port Scanning Fundamentals
- [Nmap Documentation](https://nmap.org/docs.html)
- [TCP/IP Protocol Suite](https://tools.ietf.org/html/rfc793)
- [Network Security Testing](https://owasp.org/www-project-web-security-testing-guide/)

### Advanced Techniques
- [Stealth Scanning Methods](https://nmap.org/book/scan-methods.html)
- [Service Fingerprinting](https://nmap.org/book/osdetect.html)
- [Evasion Techniques](https://nmap.org/book/evasion.html)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is provided for educational and authorized security testing purposes only. Users are responsible for ensuring they have proper authorization before scanning any systems. The authors are not responsible for any misuse of this tool.

## 🙏 Acknowledgments

- Inspired by professional security tools like Nmap
- Built with Python's powerful networking libraries
- Community feedback and testing contributions
- Open source security community

---

**🔒 Remember: Always scan responsibly and ethically!**

*For questions, issues, or contributions, please open an issue or pull request on GitHub.*
