import os
import atexit
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from services.logger_service import app_logger

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configure ProxyFix to get real client IP addresses
    # Adjust x_for and x_proto values based on your proxy configuration
    # x_for=1: trust 1 proxy for X-Forwarded-For header
    # x_proto=1: trust 1 proxy for X-Forwarded-Proto header
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Enable CORS
    CORS(app)
    
    # Set up logging middleware
    from middleware.logging_middleware import setup_logging_middleware
    setup_logging_middleware(app)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    
    # Add basic routes
    @app.route('/')
    def home():
        return {'message': 'SmartTV Server is running', 'status': 'ok'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'server': 'SmartTV'}
    
    # Register blueprints
    from api.twilio_routes import twilio_bp
    from api.user_routes import user_bp
    from api.call_routes import call_bp
    from api.admin_routes import admin_bp
    from api.contact_routes import contact_bp
    from api.update_routes import update_bp
    from api.remote_routes import remote_bp, register_socketio_events
    
    app.register_blueprint(twilio_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(call_bp, url_prefix='/api/calls')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(contact_bp, url_prefix='/api/contacts')
    app.register_blueprint(update_bp, url_prefix='/api/updates')
    app.register_blueprint(remote_bp, url_prefix='/api/remote')
    
    # Register SocketIO events for mobile remote control
    register_socketio_events(socketio)
    
    # Start background service
    from services.background_service import background_service
    
    # Log application startup
    app_logger.log_system_event("Application starting up", 
                               details={"port": os.getenv('PORT', 3001)}, 
                               send_to_discord=True)
    
    # Start background tasks immediately when app is created
    try:
        background_service.start()
        app_logger.log_system_event("Background service started", send_to_discord=True)
    except Exception as e:
        app_logger.log_system_event("Background service startup failed", 
                                   details={"error": str(e)}, 
                                   level="error", send_to_discord=True)
    
    # Graceful shutdown
    def shutdown_background_service():
        """Stop background service on app shutdown"""
        try:
            background_service.stop()
            app_logger.log_system_event("Background service stopped gracefully")
        except Exception as e:
            app_logger.log_system_event("Error stopping background service", 
                                       details={"error": str(e)}, 
                                       level="error")
    
    atexit.register(shutdown_background_service)
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    port = int(os.getenv('PORT', 3001))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)