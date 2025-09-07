import os
import json
import logging
import requests
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any

class DiscordLogger:
    """Enhanced logging service with file storage and Discord webhook integration"""
    
    def __init__(self):
        self.discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.app_name = os.getenv('APP_NAME', 'SmartTV Backend')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set up file logging
        self._setup_file_logging()
        
        # Create main logger
        self.logger = logging.getLogger('smarttv_app')
        self.logger.setLevel(logging.INFO)
        
        # Add file handler to main logger
        if not self.logger.handlers:
            self.logger.addHandler(self.file_handler)
            self.logger.addHandler(self.error_handler)
    
    def _setup_file_logging(self):
        """Set up rotating file handlers for different log levels"""
        
        # General application logs (all levels)
        log_file = os.path.join(self.logs_dir, 'app.log')
        self.file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB files, keep 5 backups
        )
        self.file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.file_handler.setFormatter(file_formatter)
        
        # Error logs (ERROR and CRITICAL only)
        error_log_file = os.path.join(self.logs_dir, 'errors.log')
        self.error_handler = RotatingFileHandler(
            error_log_file, maxBytes=5*1024*1024, backupCount=3  # 5MB files, keep 3 backups
        )
        self.error_handler.setLevel(logging.ERROR)
        self.error_handler.setFormatter(file_formatter)
    
    def _send_to_discord(self, level: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Send log message to Discord webhook with enhanced formatting"""
        if not self.discord_webhook_url:
            return
        
        # Define colors and emojis for different log levels
        level_config = {
            'INFO': {'color': 0x3498db, 'emoji': '🔵', 'name': 'Information'},      # Blue
            'WARNING': {'color': 0xf39c12, 'emoji': '🟠', 'name': 'Warning'},     # Orange  
            'ERROR': {'color': 0xe74c3c, 'emoji': '🔴', 'name': 'Error'},         # Red
            'CRITICAL': {'color': 0x8b0000, 'emoji': '🔥', 'name': 'Critical'}    # Dark Red
        }
        
        config = level_config.get(level, {'color': 0x95a5a6, 'emoji': '⚪', 'name': level})
        
        # Format the main message with better structure
        description = f"**{message}**"
        
        # Create embed with enhanced formatting
        embed = {
            "title": f"{config['emoji']} {config['name']} Alert",
            "description": description,
            "color": config['color'],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "footer": {
                "text": f"{self.app_name} • {self.environment.upper()}",
                "icon_url": "https://cdn.discordapp.com/emojis/1234567890123456789.png" if level == 'CRITICAL' else None
            },
            "fields": []
        }
        
        # Add structured fields based on data type
        if extra_data:
            # Group related fields
            system_fields = []
            request_fields = []
            error_fields = []
            user_fields = []
            
            for key, value in extra_data.items():
                if not value:  # Skip empty values
                    continue
                    
                field_name = key.replace('_', ' ').title()
                field_value = str(value)
                
                # Truncate long values but show truncation
                if len(field_value) > 1000:
                    field_value = field_value[:997] + "..."
                
                field = {
                    "name": field_name,
                    "value": f"`{field_value}`" if key in ['client_ip', 'user_id', 'endpoint', 'method', 'status_code'] else field_value,
                    "inline": True
                }
                
                # Categorize fields
                if key in ['client_ip', 'ip_type', 'ip_version', 'remote_addr']:
                    request_fields.append(field)
                elif key in ['user_id', 'action', 'device_type']:
                    user_fields.append(field)
                elif key in ['exception_type', 'exception_message', 'error_message', 'error_type']:
                    error_fields.append(field)
                elif key in ['endpoint', 'method', 'status_code', 'response_time_ms']:
                    request_fields.append(field)
                else:
                    system_fields.append(field)
            
            # Add fields in logical order with separators
            if user_fields:
                embed["fields"].extend(user_fields)
                if request_fields or error_fields or system_fields:
                    embed["fields"].append({"name": "\u200b", "value": "\u200b", "inline": False})  # Separator
            
            if request_fields:
                embed["fields"].extend(request_fields)
                if error_fields or system_fields:
                    embed["fields"].append({"name": "\u200b", "value": "\u200b", "inline": False})  # Separator
            
            if error_fields:
                embed["fields"].extend(error_fields)
                if system_fields:
                    embed["fields"].append({"name": "\u200b", "value": "\u200b", "inline": False})  # Separator
            
            if system_fields:
                embed["fields"].extend(system_fields)
        
        # Add environment as the last field if no other fields exist
        if not embed["fields"]:
            embed["fields"].append({
                "name": "Environment",
                "value": f"`{self.environment.upper()}`",
                "inline": True
            })
        
        # Enhanced payload with better bot appearance
        payload = {
            "embeds": [embed],
            "username": f"🤖 {self.app_name}",
            "avatar_url": "https://cdn.discordapp.com/emojis/1234567890123456789.png" if level == 'CRITICAL' else None
        }
        
        try:
            response = requests.post(
                self.discord_webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Don't log Discord webhook failures to avoid infinite loops
            print(f"Failed to send log to Discord: {e}")
    
    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None, send_to_discord: bool = False):
        """Log info message"""
        self.logger.info(message, extra=extra_data or {})
        if send_to_discord:
            self._send_to_discord('INFO', message, extra_data)
    
    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None, send_to_discord: bool = True):
        """Log warning message"""
        self.logger.warning(message, extra=extra_data or {})
        if send_to_discord:
            self._send_to_discord('WARNING', message, extra_data)
    
    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None, send_to_discord: bool = True):
        """Log error message"""
        self.logger.error(message, extra=extra_data or {})
        if send_to_discord:
            self._send_to_discord('ERROR', message, extra_data)
    
    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None, send_to_discord: bool = True):
        """Log critical message"""
        self.logger.critical(message, extra=extra_data or {})
        if send_to_discord:
            self._send_to_discord('CRITICAL', message, extra_data)
    
    def log_user_action(self, user_id: str, action: str, details: Optional[Dict[str, Any]] = None,
                       client_ip: Optional[str] = None):
        """Log user actions with structured data"""
        log_data = {
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'client_ip': client_ip,
            **(details or {})
        }
        message = f"User action: {action} by user {user_id}"
        if client_ip:
            message += f" from {client_ip}"
        self.info(message, extra_data=log_data)
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, 
                     user_id: Optional[str] = None, response_time: Optional[float] = None,
                     client_ip: Optional[str] = None):
        """Log API calls with performance metrics"""
        log_data = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'user_id': user_id,
            'response_time_ms': response_time,
            'client_ip': client_ip,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        message = f"{method} {endpoint} -> {status_code}"
        if response_time:
            message += f" ({response_time:.2f}ms)"
        if client_ip:
            message += f" from {client_ip}"
        
        if status_code >= 400:
            self.error(f"API Error: {message}", extra_data=log_data)
        else:
            self.info(f"API Call: {message}", extra_data=log_data)
    
    def log_twilio_event(self, event_type: str, call_sid: Optional[str] = None, 
                        status: Optional[str] = None, error: Optional[str] = None):
        """Log Twilio-related events"""
        log_data = {
            'event_type': event_type,
            'call_sid': call_sid,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if error:
            log_data['error'] = error
            self.error(f"Twilio Error: {event_type} - {error}", extra_data=log_data, send_to_discord=True)
        else:
            message = f"Twilio Event: {event_type}"
            if status:
                message += f" (Status: {status})"
            self.info(message, extra_data=log_data)
    
    def log_system_event(self, event: str, details: Optional[Dict[str, Any]] = None, 
                        level: str = 'info', send_to_discord: bool = False):
        """Log system events (startup, shutdown, etc.)"""
        log_data = {
            'event': event,
            'timestamp': datetime.utcnow().isoformat(),
            **(details or {})
        }
        
        message = f"System Event: {event}"
        
        if level.lower() == 'error':
            self.error(message, extra_data=log_data, send_to_discord=send_to_discord)
        elif level.lower() == 'warning':
            self.warning(message, extra_data=log_data, send_to_discord=send_to_discord)
        elif level.lower() == 'critical':
            self.critical(message, extra_data=log_data, send_to_discord=send_to_discord)
        else:
            self.info(message, extra_data=log_data, send_to_discord=send_to_discord)

# Global logger instance
app_logger = DiscordLogger()