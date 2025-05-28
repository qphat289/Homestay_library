from flask import Flask, send_from_directory
import os
from utils import format_price
import json
from PIL import Image
from database import init_db
from models import HomestayJSONManager, User
from auth import UserLogin
import base64
from datetime import timedelta
from extensions import init_extensions, login_manager
from config import config
import logging
from logging.handlers import RotatingFileHandler

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Configure logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/homestay.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Homestay startup')
    
    # Add cache headers to static files
    @app.after_request
    def add_header(response):
        if 'Cache-Control' not in response.headers:
            if response.mimetype in ['text/css', 'application/javascript']:
                response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            elif response.mimetype in ['image/jpeg', 'image/png', 'image/webp']:
                response.headers['Cache-Control'] = 'public, max-age=2592000'  # 30 days
            else:
                response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
        return response
    
    @login_manager.user_loader
    def load_user(user_id):
        user_data = User.get_by_phone(user_id)
        if user_data:
            return UserLogin(user_data)
        return None
    
    # Add custom filters to Jinja
    app.jinja_env.filters['format_price'] = format_price
    app.jinja_env.filters['b64encode'] = lambda data: base64.b64encode(data).decode('utf-8')
    
    # Initialize database
    init_db()
    
    # Initialize JSON data for homestays
    init_homestay_data()
    
    # Register routes
    from routes import register_routes
    register_routes(app)
    
    return app

def init_homestay_data():
    # Create a default image if it doesn't exist
    default_img_path = os.path.join('static', 'images', 'default.jpg')
    if not os.path.exists(default_img_path):
        # Create a simple colored image as default
        img = Image.new('RGB', (800, 600), color = (76, 175, 80)) 
        img.save(default_img_path, optimize=True, quality=85)
    
    # Create hero background if it doesn't exist
    hero_bg_path = os.path.join('static', 'images', 'new_bg.jpg')
    if not os.path.exists(hero_bg_path):
        # Create a simple colored image for hero background
        hero_img = Image.new('RGB', (1920, 1080), color = (76, 175, 80))  
        hero_img.save(hero_bg_path, optimize=True, quality=85)

# Create application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
