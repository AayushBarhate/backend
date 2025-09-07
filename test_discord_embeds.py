#!/usr/bin/env python3
"""
Test script specifically for Discord embed formatting
Run this to see various types of Discord notifications
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

def test_user_registration_alert():
    """Test user registration notification"""
    print("📝 Sending user registration alert...")
    
    app_logger.log_user_action(
        user_id="ABC123",
        action="user_registration",
        details={
            "device_type": "smarttv",
            "display_name": "Living Room TV",
            "metadata": {
                "device_model": "Samsung QN85A 65-inch",
                "app_version": "2.1.4",
                "firmware": "Tizen 6.5"
            }
        },
        client_ip="192.168.1.105"
    )
    
    # Send to Discord
    app_logger.info("New SmartTV device registered successfully", 
                   extra_data={
                       "user_id": "ABC123",
                       "device_type": "smarttv",
                       "client_ip": "192.168.1.105",
                       "ip_type": "private",
                       "display_name": "Living Room TV",
                       "device_model": "Samsung QN85A 65-inch"
                   },
                   send_to_discord=True)
    time.sleep(2)

def test_api_error_alert():
    """Test API error notification"""
    print("🚨 Sending API error alert...")
    
    app_logger.error("Authentication failed: Invalid API key provided",
                    extra_data={
                        "endpoint": "/api/users/authenticate",
                        "method": "POST",
                        "status_code": 401,
                        "client_ip": "203.0.113.45",
                        "ip_type": "public",
                        "user_agent": "SmartTV-App/2.1.4",
                        "error_type": "AuthenticationError",
                        "response_time_ms": 127.3
                    },
                    send_to_discord=True)
    time.sleep(2)

def test_system_critical_alert():
    """Test critical system error notification"""
    print("🔥 Sending critical system alert...")
    
    app_logger.critical("Database connection pool exhausted",
                       extra_data={
                           "active_connections": 50,
                           "max_connections": 50,
                           "queue_length": 25,
                           "error_type": "ConnectionPoolExhaustedError",
                           "affected_services": ["user_service", "call_service", "twilio_service"],
                           "memory_usage": "89%",
                           "cpu_usage": "94%"
                       },
                       send_to_discord=True)
    time.sleep(2)

def test_twilio_webhook_alert():
    """Test Twilio webhook notification"""
    print("📞 Sending Twilio webhook alert...")
    
    app_logger.log_twilio_event(
        event_type="call_failed",
        call_sid="CA1234567890abcdef1234567890abcdef",
        status="failed",
        error="Destination number is not reachable"
    )
    
    # Send to Discord
    app_logger.warning("Twilio call failed - unreachable number",
                      extra_data={
                          "event_type": "call_failed",
                          "call_sid": "CA1234567890abcdef1234567890abcdef",
                          "status": "failed",
                          "error_message": "Destination number is not reachable",
                          "caller_id": "+1-555-0123",
                          "recipient": "+1-555-9999",
                          "duration": "0 seconds"
                      },
                      send_to_discord=True)
    time.sleep(2)

def test_security_alert():
    """Test security-related notification"""
    print("🛡️ Sending security alert...")
    
    app_logger.warning("Multiple failed login attempts detected",
                      extra_data={
                          "client_ip": "198.51.100.42",
                          "ip_type": "public",
                          "user_id": "XYZ789",
                          "failed_attempts": 5,
                          "time_window": "2 minutes",
                          "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                          "last_attempt": "2025-09-07 00:30:45 UTC",
                          "action_taken": "Account temporarily locked"
                      },
                      send_to_discord=True)
    time.sleep(2)

def test_performance_alert():
    """Test performance monitoring notification"""
    print("⚡ Sending performance alert...")
    
    app_logger.warning("High response times detected on API endpoints",
                      extra_data={
                          "endpoint": "/api/calls/start",
                          "avg_response_time": "2,347ms",
                          "p95_response_time": "4,891ms",
                          "error_rate": "12.3%",
                          "requests_per_minute": 47,
                          "affected_users": 23,
                          "time_period": "Last 5 minutes"
                      },
                      send_to_discord=True)

def main():
    """Run Discord embed tests"""
    print("🚀 Testing Discord embed formatting...\n")
    
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL not set in .env file")
        return
    
    print(f"📡 Using Discord webhook: ...{webhook_url[-20:]}")
    print("📋 Sending test notifications to Discord channel...\n")
    
    try:
        test_user_registration_alert()
        test_api_error_alert() 
        test_system_critical_alert()
        test_twilio_webhook_alert()
        test_security_alert()
        test_performance_alert()
        
        print("\n✅ All Discord embed tests completed!")
        print("📱 Check your Discord channel to see the formatted messages")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    main()