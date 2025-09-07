#!/usr/bin/env python3
"""
Test script for the logging system
Run this to test file logging and Discord webhook integration
"""
import os
import sys
import time
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from services.logger_service import app_logger
from utils.ip_utils import get_ip_info

def test_basic_logging():
    """Test basic logging functionality"""
    print("🧪 Testing basic logging...")
    
    # Test different log levels
    app_logger.info("Test info message", extra_data={"test": "info_test"})
    app_logger.warning("Test warning message", extra_data={"test": "warning_test"})
    app_logger.error("Test error message", extra_data={"test": "error_test"})
    
    print("✅ Basic logging test completed. Check logs/ directory for output files.")

def test_user_action_logging():
    """Test user action logging"""
    print("🧪 Testing user action logging...")
    
    app_logger.log_user_action(
        user_id="TEST1",
        action="test_login",
        details={
            "device_type": "smarttv",
            "user_agent": "TestAgent/1.0"
        },
        client_ip="192.168.1.100"
    )
    
    print("✅ User action logging test completed.")

def test_api_logging():
    """Test API call logging"""
    print("🧪 Testing API call logging...")
    
    # Simulate various API calls with IP addresses
    app_logger.log_api_call("/api/users/register", "POST", 200, "TEST1", 45.2, "192.168.1.100")
    app_logger.log_api_call("/api/users/profile", "GET", 404, "TEST2", 12.5, "10.0.0.5")
    app_logger.log_api_call("/api/calls/start", "POST", 500, "TEST3", 250.8, "203.0.113.42")
    
    print("✅ API call logging test completed.")

def test_twilio_logging():
    """Test Twilio event logging"""
    print("🧪 Testing Twilio event logging...")
    
    # Test successful Twilio event
    app_logger.log_twilio_event(
        event_type="call_initiated",
        call_sid="CA1234567890abcdef1234567890abcdef",
        status="ringing"
    )
    
    # Test Twilio error
    app_logger.log_twilio_event(
        event_type="call_failed",
        call_sid="CA9876543210fedcba9876543210fedcba",
        status="failed",
        error="Invalid phone number format"
    )
    
    print("✅ Twilio event logging test completed.")

def test_system_logging():
    """Test system event logging"""
    print("🧪 Testing system event logging...")
    
    # Test system events
    app_logger.log_system_event("test_service_started", details={"version": "1.0.0"})
    app_logger.log_system_event("test_critical_error", 
                               details={"memory_usage": "95%", "cpu_usage": "90%"}, 
                               level="critical")
    
    print("✅ System event logging test completed.")

def test_ip_utilities():
    """Test IP utility functions"""
    print("🧪 Testing IP utility functions...")
    
    # Test various IP types
    test_ips = [
        "192.168.1.100",    # Private IPv4
        "10.0.0.1",         # Private IPv4
        "127.0.0.1",        # Loopback IPv4
        "203.0.113.42",     # Public IPv4 (documentation range)
        "::1",              # Loopback IPv6
        "2001:db8::1",      # Documentation IPv6
        "invalid-ip",       # Invalid IP
    ]
    
    for ip in test_ips:
        info = get_ip_info(ip)
        print(f"   IP: {ip:15} -> Type: {info['type']:8} Version: {info.get('version', 'N/A')}")
    
    print("✅ IP utility test completed.")

def test_discord_integration():
    """Test Discord webhook integration"""
    print("🧪 Testing Discord integration...")
    
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    if not discord_webhook:
        print("⚠️  DISCORD_WEBHOOK_URL not set. Discord integration test skipped.")
        print("   To test Discord integration:")
        print("   1. Create a Discord webhook in your server")
        print("   2. Add DISCORD_WEBHOOK_URL to your .env file")
        print("   3. Run this test again")
        return
    
    # Test Discord notifications
    app_logger.info("Discord test: Info message", send_to_discord=True)
    time.sleep(1)  # Rate limit prevention
    
    app_logger.warning("Discord test: Warning message", 
                      extra_data={"test_type": "discord_warning"}, 
                      send_to_discord=True)
    time.sleep(1)
    
    app_logger.error("Discord test: Error message", 
                    extra_data={"test_type": "discord_error", "severity": "high"}, 
                    send_to_discord=True)
    
    print("✅ Discord integration test completed. Check your Discord channel!")

def main():
    """Run all logging tests"""
    print("🚀 Starting logging system tests...\n")
    
    # Check if logs directory will be created
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    print(f"📁 Logs will be saved to: {logs_dir}")
    
    # Run tests
    test_basic_logging()
    print()
    
    test_user_action_logging()
    print()
    
    test_api_logging()
    print()
    
    test_twilio_logging()
    print()
    
    test_system_logging()
    print()
    
    test_ip_utilities()
    print()
    
    test_discord_integration()
    print()
    
    print("🎉 All logging tests completed!")
    print(f"\n📋 Results:")
    print(f"   • Check {logs_dir}/app.log for general application logs")
    print(f"   • Check {logs_dir}/errors.log for error logs only")
    print(f"   • Check your Discord channel for webhook messages (if configured)")
    
    # Show log files if they exist
    if os.path.exists(logs_dir):
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        if log_files:
            print(f"\n📄 Generated log files:")
            for file in sorted(log_files):
                file_path = os.path.join(logs_dir, file)
                size = os.path.getsize(file_path)
                print(f"   • {file} ({size} bytes)")

if __name__ == "__main__":
    main()