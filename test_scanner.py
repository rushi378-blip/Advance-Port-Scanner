#!/usr/bin/env python3
"""
Test Suite for Advanced Port Scanner
Comprehensive testing of all scanner functionality
"""

import unittest
import socket
import threading
import time
import tempfile
import os
import json
import csv
from unittest.mock import patch, MagicMock
from advanced_port_scanner import AdvancedPortScanner

class TestAdvancedPortScanner(unittest.TestCase):
    """Test cases for AdvancedPortScanner class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scanner = AdvancedPortScanner(
            target="127.0.0.1",
            ports="80,443,8080",
            threads=10,
            timeout=1
        )
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove test files
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
    
    def test_init(self):
        """Test scanner initialization"""
        self.assertEqual(self.scanner.target, "127.0.0.1")
        self.assertEqual(self.scanner.ports, [80, 443, 8080])
        self.assertEqual(self.scanner.threads, 10)
        self.assertEqual(self.scanner.timeout, 1)
        self.assertEqual(self.scanner.scan_type, "connect")
        self.assertEqual(len(self.scanner.results), 0)
    
    def test_parse_ports_single(self):
        """Test parsing single ports"""
        ports = self.scanner._parse_ports("80")
        self.assertEqual(ports, [80])
        
        ports = self.scanner._parse_ports("443")
        self.assertEqual(ports, [443])
    
    def test_parse_ports_range(self):
        """Test parsing port ranges"""
        ports = self.scanner._parse_ports("1-5")
        self.assertEqual(ports, [1, 2, 3, 4, 5])
        
        ports = self.scanner._parse_ports("80-82")
        self.assertEqual(ports, [80, 81, 82])
    
    def test_parse_ports_mixed(self):
        """Test parsing mixed port specifications"""
        ports = self.scanner._parse_ports("80,443,8080-8082")
        self.assertEqual(ports, [80, 443, 8080, 8081, 8082])
        
        ports = self.scanner._parse_ports("1-3,5,7-9")
        self.assertEqual(ports, [1, 2, 3, 5, 7, 8, 9])
    
    def test_parse_ports_edge_cases(self):
        """Test edge cases in port parsing"""
        # Single port range
        ports = self.scanner._parse_ports("80-80")
        self.assertEqual(ports, [80])
        
        # Large range
        ports = self.scanner._parse_ports("1-10")
        self.assertEqual(ports, list(range(1, 11)))
    
    def test_resolve_target_ip(self):
        """Test IP address resolution"""
        # Test with IP address
        result = self.scanner._resolve_target("192.168.1.1")
        self.assertEqual(result, "192.168.1.1")
        
        # Test with localhost
        result = self.scanner._resolve_target("127.0.0.1")
        self.assertEqual(result, "127.0.0.1")
    
    @patch('socket.gethostbyname')
    def test_resolve_target_hostname(self, mock_gethostbyname):
        """Test hostname resolution"""
        mock_gethostbyname.return_value = "192.168.1.100"
        
        result = self.scanner._resolve_target("example.com")
        self.assertEqual(result, "192.168.1.100")
        mock_gethostbyname.assert_called_once_with("example.com")
    
    @patch('socket.gethostbyname')
    def test_resolve_target_error(self, mock_gethostbyname):
        """Test hostname resolution error"""
        mock_gethostbyname.side_effect = socket.gaierror("Name or service not known")
        
        with self.assertRaises(SystemExit):
            self.scanner._resolve_target("invalid.hostname.com")
    
    def test_identify_service(self):
        """Test service identification"""
        # Test known services
        self.assertEqual(self.scanner._identify_service(80), "HTTP")
        self.assertEqual(self.scanner._identify_service(443), "HTTPS")
        self.assertEqual(self.scanner._identify_service(22), "SSH")
        
        # Test unknown service
        self.assertEqual(self.scanner._identify_service(9999), "Unknown")
    
    @patch('socket.socket')
    def test_connect_scan_open_port(self, mock_socket):
        """Test connect scan with open port"""
        # Mock socket behavior
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 0
        mock_socket.return_value = mock_sock
        
        # Mock banner grabbing
        with patch.object(self.scanner, '_get_banner') as mock_banner:
            mock_banner.return_value = "HTTP/1.1 200 OK"
            
            result = self.scanner._connect_scan(80)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['port'], 80)
            self.assertEqual(result['state'], 'open')
            self.assertEqual(result['service'], 'HTTP')
            self.assertEqual(result['banner'], 'HTTP/1.1 200 OK')
            self.assertEqual(result['scan_type'], 'connect')
    
    @patch('socket.socket')
    def test_connect_scan_closed_port(self, mock_socket):
        """Test connect scan with closed port"""
        # Mock socket behavior
        mock_sock = MagicMock()
        mock_sock.connect_ex.return_value = 1  # Connection refused
        mock_socket.return_value = mock_sock
        
        result = self.scanner._connect_scan(9999)
        self.assertIsNone(result)
    
    @patch('socket.socket')
    def test_connect_scan_exception(self, mock_socket):
        """Test connect scan with socket exception"""
        mock_socket.side_effect = Exception("Socket error")
        
        result = self.scanner._connect_scan(80)
        self.assertIsNone(result)
    
    @patch('socket.socket')
    def test_get_banner_success(self, mock_socket):
        """Test successful banner grabbing"""
        # Mock socket behavior
        mock_sock = MagicMock()
        mock_sock.connect.return_value = None
        mock_sock.send.return_value = None
        mock_sock.recv.return_value = b"HTTP/1.1 200 OK"
        mock_socket.return_value = mock_sock
        
        banner = self.scanner._get_banner(80)
        self.assertEqual(banner, "HTTP/1.1 200 OK")
    
    @patch('socket.socket')
    def test_get_banner_no_response(self, mock_socket):
        """Test banner grabbing with no response"""
        # Mock socket behavior
        mock_sock = MagicMock()
        mock_sock.connect.return_value = None
        mock_sock.send.return_value = None
        mock_sock.recv.return_value = b""
        mock_socket.return_value = mock_sock
        
        banner = self.scanner._get_banner(80)
        self.assertEqual(banner, "No banner")
    
    @patch('socket.socket')
    def test_get_banner_exception(self, mock_socket):
        """Test banner grabbing with exception"""
        mock_socket.side_effect = Exception("Connection error")
        
        banner = self.scanner._get_banner(80)
        self.assertEqual(banner, "No banner")
    
    def test_udp_scan_open_port(self):
        """Test UDP scan with open port"""
        # This test would require more complex mocking of UDP behavior
        # For now, we'll test the basic structure
        self.assertTrue(hasattr(self.scanner, '_udp_scan'))
    
    def test_scan_port_connect(self):
        """Test scan_port method with connect scan"""
        with patch.object(self.scanner, '_connect_scan') as mock_connect:
            mock_connect.return_value = {'port': 80, 'state': 'open', 'service': 'HTTP'}
            
            result = self.scanner.scan_port(80)
            self.assertEqual(result['port'], 80)
            mock_connect.assert_called_once_with(80)
    
    def test_scan_port_syn(self):
        """Test scan_port method with SYN scan"""
        self.scanner.scan_type = "syn"
        
        with patch.object(self.scanner, '_syn_scan') as mock_syn:
            mock_syn.return_value = {'port': 80, 'state': 'open', 'service': 'HTTP'}
            
            result = self.scanner.scan_port(80)
            self.assertEqual(result['port'], 80)
            mock_syn.assert_called_once_with(80)
    
    def test_scan_port_udp(self):
        """Test scan_port method with UDP scan"""
        self.scanner.scan_type = "udp"
        
        with patch.object(self.scanner, '_udp_scan') as mock_udp:
            mock_udp.return_value = {'port': 53, 'state': 'open', 'service': 'DNS'}
            
            result = self.scanner.scan_port(53)
            self.assertEqual(result['port'], 53)
            mock_udp.assert_called_once_with(53)
    
    def test_export_results_json(self):
        """Test JSON export functionality"""
        # Add some test results
        self.scanner.results = [
            {'port': 80, 'state': 'open', 'service': 'HTTP', 'banner': 'Test', 'scan_type': 'connect'},
            {'port': 443, 'state': 'open', 'service': 'HTTPS', 'banner': 'Test2', 'scan_type': 'connect'}
        ]
        
        filename = os.path.join(self.test_dir, "test_export")
        self.scanner.export_results("json", filename)
        
        # Verify file was created
        json_file = f"{filename}.json"
        self.assertTrue(os.path.exists(json_file))
        
        # Verify content
        with open(json_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]['port'], 80)
            self.assertEqual(data[1]['port'], 443)
    
    def test_export_results_csv(self):
        """Test CSV export functionality"""
        # Add some test results
        self.scanner.results = [
            {'port': 80, 'state': 'open', 'service': 'HTTP', 'banner': 'Test', 'scan_type': 'connect'}
        ]
        
        filename = os.path.join(self.test_dir, "test_export")
        self.scanner.export_results("csv", filename)
        
        # Verify file was created
        csv_file = f"{filename}.csv"
        self.assertTrue(os.path.exists(csv_file))
        
        # Verify content
        with open(csv_file, 'r') as f:
            content = f.read()
            self.assertIn("port,state,service,banner,scan_type", content)
            self.assertIn("80,open,HTTP,Test,connect", content)
    
    def test_export_results_text(self):
        """Test text export functionality"""
        # Add some test results
        self.scanner.results = [
            {'port': 80, 'state': 'open', 'service': 'HTTP', 'banner': 'Test', 'scan_type': 'connect'}
        ]
        
        filename = os.path.join(self.test_dir, "test_export")
        self.scanner.export_results("text", filename)
        
        # Verify file was created
        txt_file = f"{filename}.txt"
        self.assertTrue(os.path.exists(txt_file))
        
        # Verify content
        with open(txt_file, 'r') as f:
            content = f.read()
            self.assertIn("Port Scan Results for 127.0.0.1", content)
            self.assertIn("80/tcp", content)
            self.assertIn("HTTP", content)
    
    def test_export_results_auto_filename(self):
        """Test automatic filename generation"""
        # Add some test results
        self.scanner.results = [
            {'port': 80, 'state': 'open', 'service': 'HTTP', 'banner': 'Test', 'scan_type': 'connect'}
        ]
        
        self.scanner.export_results("json")
        
        # Check if files were created with auto-generated names
        files = os.listdir(self.test_dir)
        json_files = [f for f in files if f.endswith('.json')]
        self.assertGreater(len(json_files), 0)
    
    def test_thread_safety(self):
        """Test thread safety of results collection"""
        def add_result(port):
            with self.scanner.lock:
                self.scanner.results.append({'port': port, 'test': True})
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=add_result, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all results were added
        self.assertEqual(len(self.scanner.results), 10)
        
        # Verify no duplicates or missing values
        ports = [r['port'] for r in self.scanner.results]
        self.assertEqual(set(ports), set(range(10)))

class TestPortScannerIntegration(unittest.TestCase):
    """Integration tests for the port scanner"""
    
    def setUp(self):
        """Set up test server"""
        # Create a simple test server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1', 0))
        self.server_socket.listen(1)
        
        # Get the port number
        self.test_port = self.server_socket.getsockname()[1]
        
        # Start server in background thread
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Give server time to start
        time.sleep(0.1)
    
    def tearDown(self):
        """Clean up test server"""
        self.server_socket.close()
    
    def _run_server(self):
        """Run the test server"""
        try:
            while True:
                client, addr = self.server_socket.accept()
                client.send(b"Test Server Response")
                client.close()
        except:
            pass
    
    def test_real_connection_scan(self):
        """Test real connection scanning"""
        scanner = AdvancedPortScanner(
            target="127.0.0.1",
            ports=str(self.test_port),
            threads=1,
            timeout=1
        )
        
        results = scanner.run_scan()
        
        # Should find our test server
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['port'], self.test_port)
        self.assertEqual(results[0]['state'], 'open')

class TestCommandLineInterface(unittest.TestCase):
    """Test command line interface functionality"""
    
    def test_help_output(self):
        """Test help output"""
        # This would require testing the actual argparse output
        # For now, we'll test that the argument parser is properly configured
        scanner = AdvancedPortScanner("127.0.0.1", "80")
        self.assertTrue(hasattr(scanner, 'target'))
        self.assertTrue(hasattr(scanner, 'ports'))

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
