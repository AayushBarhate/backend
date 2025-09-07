import time
import json
from flask import request, g
from functools import wraps
from services.logger_service import app_logger
from utils.ip_utils import get_client_ip, get_ip_info

def log_api_requests(app):
    """Middleware to log all API requests and responses"""
    
    @app.before_request
    def before_request():
        """Log incoming requests"""
        g.start_time = time.time()
        
        # Get client IP and store it in g for use across the request
        g.client_ip = get_client_ip()
        g.ip_info = get_ip_info(g.client_ip)
        
        # Skip logging for health checks and static assets
        if request.endpoint in ['health', 'home'] or request.path.startswith('/static'):
            return
        
        # Log basic request info
        request_data = {
            'method': request.method,
            'endpoint': request.path,
            'client_ip': g.client_ip,
            'ip_type': g.ip_info.get('type', 'unknown'),
            'user_agent': request.headers.get('User-Agent', 'Unknown')[:200],  # Limit length
            'referer': request.headers.get('Referer', '')[:100] if request.headers.get('Referer') else None
        }
        
        # Add IP version info if available
        if 'version' in g.ip_info:
            request_data['ip_version'] = f"IPv{g.ip_info['version']}"
        
        # Add query parameters if present
        if request.args:
            request_data['query_params'] = dict(request.args)
        
        # Add JSON body for POST/PUT requests (but don't log sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
            try:
                body = request.get_json()
                if body:
                    # Filter out sensitive fields
                    filtered_body = {k: v for k, v in body.items() 
                                   if k.lower() not in ['password', 'token', 'secret', 'key', 'auth_token', 'api_key']}
                    if filtered_body:
                        request_data['body'] = filtered_body
            except Exception:
                pass
        
        app_logger.info(f"API Request: {request.method} {request.path} from {g.client_ip}", extra_data=request_data)
    
    @app.after_request
    def after_request(response):
        """Log outgoing responses"""
        
        # Skip logging for health checks and static assets
        if request.endpoint in ['health', 'home'] or request.path.startswith('/static'):
            return response
        
        # Calculate response time
        response_time = None
        if hasattr(g, 'start_time'):
            response_time = (time.time() - g.start_time) * 1000  # Convert to milliseconds
        
        # Get client IP from g (set in before_request)
        client_ip = getattr(g, 'client_ip', 'unknown')
        
        # Log the API call
        app_logger.log_api_call(
            endpoint=request.path,
            method=request.method,
            status_code=response.status_code,
            response_time=response_time,
            client_ip=client_ip
        )
        
        # Log errors with more detail
        if response.status_code >= 400:
            ip_info = getattr(g, 'ip_info', {})
            error_data = {
                'status_code': response.status_code,
                'method': request.method,
                'endpoint': request.path,
                'client_ip': client_ip,
                'ip_type': ip_info.get('type', 'unknown'),
                'response_time_ms': response_time
            }
            
            # Try to get error message from response
            try:
                if response.is_json:
                    response_data = response.get_json()
                    if response_data and 'error' in response_data:
                        error_data['error_message'] = response_data['error']
            except Exception:
                pass
            
            level = 'error' if response.status_code >= 500 else 'warning'
            app_logger.log_system_event(
                f"HTTP {response.status_code} error on {request.method} {request.path} from {client_ip}",
                details=error_data,
                level=level,
                send_to_discord=response.status_code >= 500  # Only send 5xx errors to Discord
            )
        
        return response

def log_exceptions(app):
    """Log unhandled exceptions"""
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Log unhandled exceptions"""
        client_ip = getattr(g, 'client_ip', get_client_ip())
        ip_info = getattr(g, 'ip_info', get_ip_info(client_ip))
        
        error_data = {
            'exception_type': type(e).__name__,
            'exception_message': str(e),
            'method': request.method,
            'endpoint': request.path,
            'client_ip': client_ip,
            'ip_type': ip_info.get('type', 'unknown')
        }
        
        app_logger.critical(
            f"Unhandled exception in {request.method} {request.path} from {client_ip}: {type(e).__name__}",
            extra_data=error_data,
            send_to_discord=True
        )
        
        # Re-raise the exception to let Flask handle it normally
        raise e

def setup_logging_middleware(app):
    """Set up all logging middleware"""
    log_api_requests(app)
    log_exceptions(app)