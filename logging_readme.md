# 📊 SmartTV Backend Logging System

A comprehensive logging solution with file storage, IP tracking, and Discord webhook integration for real-time monitoring and alerting.

## 🌟 Features

### 📁 **File-Based Logging**
- **Rotating logs** with automatic file management
- **Separate error logs** for quick issue identification
- **Structured JSON data** with timestamps and metadata
- **Configurable log levels** and retention policies

### 🌐 **IP Address Tracking**
- **ProxyFix integration** for accurate client IP detection
- **IPv4/IPv6 support** with automatic classification
- **Proxy header support** (X-Forwarded-For, X-Real-IP, CF-Connecting-IP, etc.)
- **IP geolocation hints** (public, private, loopback classification)

### 📱 **Discord Integration**
- **Real-time alerts** sent to Discord channels
- **Professional embeds** with color-coded severity levels
- **Smart filtering** (warnings/errors auto-sent, info optional)
- **Organized field grouping** for better readability

### 🔍 **Request Monitoring**
- **Automatic API logging** for all HTTP requests
- **Performance metrics** (response times, status codes)
- **Error tracking** with detailed context
- **Security monitoring** (failed authentication, suspicious IPs)

## 📋 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Configuration](#configuration)
3. [Usage Examples](#usage-examples)
4. [Log Types](#log-types)
5. [Discord Alerts](#discord-alerts)
6. [File Structure](#file-structure)
7. [API Reference](#api-reference)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

## 🚀 Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
# Application Settings
APP_NAME=SmartTV Backend
ENVIRONMENT=development

# Discord Webhook (Optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN

# ProxyFix Configuration (for production behind load balancers)
PROXY_FIX_X_FOR=1
PROXY_FIX_X_PROTO=1
```

### 3. Discord Webhook Setup (Optional)
1. Open Discord server settings
2. Go to **Integrations** → **Webhooks**
3. Create a new webhook
4. Copy the webhook URL to your `.env` file

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name for logs | `SmartTV Backend` | No |
| `ENVIRONMENT` | Environment (dev/staging/prod) | `development` | No |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL | None | No |
| `PROXY_FIX_X_FOR` | Number of X-Forwarded-For proxies | `1` | No |
| `PROXY_FIX_X_PROTO` | Number of X-Forwarded-Proto proxies | `1` | No |

### Log File Configuration

```python
# Log files are automatically created in logs/ directory
logs/
├── app.log      # All application logs (10MB max, 5 backups)
└── errors.log   # Errors only (5MB max, 3 backups)
```

## 💡 Usage Examples

### Basic Logging
```python
from services.logger_service import app_logger

# Simple logging
app_logger.info("User logged in successfully")
app_logger.warning("High memory usage detected")
app_logger.error("Database connection failed")

# With extra data
app_logger.info("API request processed", extra_data={
    "endpoint": "/api/users",
    "response_time": 45.2,
    "status_code": 200
})

# Send to Discord
app_logger.error("Critical system error", 
                extra_data={"error_code": "DB_001"},
                send_to_discord=True)
```

### User Action Logging
```python
# Track user activities
app_logger.log_user_action(
    user_id="ABC123",
    action="device_registration",
    details={
        "device_type": "smarttv",
        "model": "Samsung QN85A",
        "ip_address": "192.168.1.100"
    },
    client_ip="192.168.1.100"
)
```

### API Call Logging
```python
# Log API requests (automatic via middleware)
app_logger.log_api_call(
    endpoint="/api/users/register",
    method="POST",
    status_code=200,
    user_id="ABC123",
    response_time=45.2,
    client_ip="192.168.1.100"
)
```

### Twilio Event Logging
```python
# Track Twilio webhook events
app_logger.log_twilio_event(
    event_type="call_completed",
    call_sid="CA1234567890abcdef",
    status="completed"
)

# Log Twilio errors
app_logger.log_twilio_event(
    event_type="call_failed",
    call_sid="CA1234567890abcdef",
    status="failed",
    error="Invalid phone number"
)
```

### System Event Logging
```python
# Track system events
app_logger.log_system_event(
    event="service_started",
    details={"version": "2.1.0", "port": 3001},
    send_to_discord=True
)

app_logger.log_system_event(
    event="database_connection_lost",
    level="critical",
    send_to_discord=True
)
```

## 📝 Log Types

### 1. **Application Logs** (`logs/app.log`)
All application events with full context:
```
2025-09-07 00:28:35 | INFO  | smarttv_app | User action: user_registration by user ABC123 from 192.168.1.100
2025-09-07 00:28:36 | ERROR | smarttv_app | API Error: POST /api/calls/start -> 500 (250.80ms) from 203.0.113.42
```

### 2. **Error Logs** (`logs/errors.log`)
Errors and critical events only:
```
2025-09-07 00:29:51 | ERROR    | smarttv_app | Authentication failed: Invalid API key provided
2025-09-07 00:29:54 | CRITICAL | smarttv_app | Database connection pool exhausted
```

### 3. **Automatic Request Logging**
Every API request is logged with:
- HTTP method and endpoint
- Response status code and time
- Client IP address and type
- User agent and referer
- Request body (sensitive data filtered)

## 🎨 Discord Alerts

### Alert Types

| Level | Color | Emoji | Auto-Send | Description |
|-------|-------|-------|-----------|-------------|
| **INFO** | 🔵 Blue | 🔵 | Optional | General information |
| **WARNING** | 🟠 Orange | 🟠 | Yes | Warning conditions |
| **ERROR** | 🔴 Red | 🔴 | Yes | Error conditions |
| **CRITICAL** | 🔥 Dark Red | 🔥 | Yes | Critical failures |

### Discord Embed Structure
```
🔴 Error Alert
Authentication failed: Invalid API key provided

👤 User Information
User ID: `ABC123`
Action: device_registration

🌐 Request Information  
Client IP: `203.0.113.45`
Endpoint: `/api/users/authenticate`
Method: `POST`
Status Code: `401`

❌ Error Information
Error Type: AuthenticationError  
Response Time: 127.3ms

SmartTV Backend • DEVELOPMENT
```

### Field Categories
- **👤 User fields**: user_id, action, device_type
- **🌐 Request fields**: client_ip, endpoint, method, status_code, response_time_ms
- **❌ Error fields**: exception_type, error_message, error_type
- **⚙️ System fields**: memory_usage, cpu_usage, etc.

## 📁 File Structure

```
backend/
├── logs/                           # Log files (auto-created)
│   ├── app.log                     # All application logs
│   └── errors.log                  # Errors and criticals only
├── services/
│   └── logger_service.py           # Main logging service
├── middleware/
│   └── logging_middleware.py       # Request/response logging
├── utils/
│   └── ip_utils.py                 # IP address utilities
├── test_logging.py                 # Basic logging tests
├── test_discord_embeds.py          # Discord formatting tests
└── logging_readme.md               # This documentation
```

## 📚 API Reference

### `app_logger` Methods

#### Core Logging
```python
app_logger.info(message, extra_data=None, send_to_discord=False)
app_logger.warning(message, extra_data=None, send_to_discord=True)
app_logger.error(message, extra_data=None, send_to_discord=True)
app_logger.critical(message, extra_data=None, send_to_discord=True)
```

#### Structured Logging
```python
app_logger.log_user_action(user_id, action, details=None, client_ip=None)
app_logger.log_api_call(endpoint, method, status_code, user_id=None, response_time=None, client_ip=None)
app_logger.log_twilio_event(event_type, call_sid=None, status=None, error=None)
app_logger.log_system_event(event, details=None, level='info', send_to_discord=False)
```

### IP Utilities
```python
from utils.ip_utils import get_client_ip, get_ip_info

# Get real client IP (handles proxies)
client_ip = get_client_ip()

# Get IP information
ip_info = get_ip_info("192.168.1.100")
# Returns: {'address': '192.168.1.100', 'type': 'private', 'version': 4}
```

## 🧪 Testing

### Run Basic Tests
```bash
python test_logging.py
```

### Test Discord Embeds
```bash
python test_discord_embeds.py
```

### Test Output
```
🚀 Starting logging system tests...

📁 Logs will be saved to: /path/to/backend/logs
🧪 Testing basic logging...
✅ Basic logging test completed.

🧪 Testing IP utility functions...
   IP: 192.168.1.100   -> Type: private  Version: 4
   IP: 203.0.113.42    -> Type: public   Version: 4
✅ IP utility test completed.

✅ Discord integration test completed. Check your Discord channel!
```

## 🔧 Troubleshooting

### Common Issues

#### Discord Webhooks Not Working
```bash
# Check webhook URL format
echo $DISCORD_WEBHOOK_URL

# Test webhook manually
curl -X POST "$DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}'
```

#### IP Detection Issues
```python
# Debug IP detection
from utils.ip_utils import get_client_ip, get_ip_info

# In a Flask route
@app.route('/debug-ip')
def debug_ip():
    ip = get_client_ip()
    info = get_ip_info(ip)
    return {"detected_ip": ip, "info": info, "headers": dict(request.headers)}
```

#### Log File Permissions
```bash
# Ensure logs directory is writable
chmod 755 logs/
chmod 644 logs/*.log
```

#### ProxyFix Configuration
For production deployments behind load balancers:

**Nginx**:
```bash
PROXY_FIX_X_FOR=1
PROXY_FIX_X_PROTO=1
```

**Cloudflare**:
```bash
PROXY_FIX_X_FOR=1
PROXY_FIX_X_PROTO=1
# Uses CF-Connecting-IP header automatically
```

**AWS Application Load Balancer**:
```bash
PROXY_FIX_X_FOR=1
PROXY_FIX_X_PROTO=1
```

### Debug Mode
Enable debug logging to troubleshoot issues:

```python
import logging
logging.getLogger('smarttv_app').setLevel(logging.DEBUG)
```

### Performance Considerations

- Log files rotate automatically to prevent disk space issues
- Discord webhooks have rate limiting (consider batching for high-volume apps)
- IP detection adds minimal overhead (~1ms per request)
- Sensitive data (passwords, tokens) is automatically filtered from logs

## 📊 Monitoring & Analytics

### Log Analysis
```bash
# View recent errors
tail -f logs/errors.log

# Count error types
grep "ERROR" logs/app.log | cut -d'|' -f4 | sort | uniq -c

# Find high-traffic IPs
grep "API Request" logs/app.log | grep -o "from [0-9.]*" | sort | uniq -c | sort -nr
```

### Discord Channel Organization
Consider creating separate Discord channels for:
- `#app-info` - Information and user actions
- `#app-warnings` - Performance and security warnings  
- `#app-errors` - Errors and critical alerts
- `#app-security` - Security-related events

## 🔒 Security Considerations

### Data Protection
- **Sensitive data filtering**: Passwords, tokens, API keys automatically removed
- **IP privacy**: Internal IPs logged but external IPs can be anonymized
- **User data**: Only necessary user identifiers logged

### Discord Security
- **Webhook URLs**: Keep webhook URLs secret (treat like passwords)
- **Channel permissions**: Restrict Discord channel access appropriately
- **Message retention**: Consider Discord's message retention policies

---

## 📞 Support

For questions or issues with the logging system:

1. Check this documentation
2. Review log files in `logs/` directory
3. Run test scripts to verify functionality
4. Check Discord channel for real-time alerts

**Happy logging! 🚀**