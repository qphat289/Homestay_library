from flask import Flask
import os
from utils import format_price
import json
from PIL import Image
from database import init_db, add_sample_user
from models import HomestayJSONManager, User
from flask_login import LoginManager
from auth import UserLogin
import base64
from routes import register_routes

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-generated-key')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user_data = User.get_by_phone(user_id)
    if user_data:
        return UserLogin(user_data)
    return None

# Add custom filters to Jinja
app.jinja_env.filters['format_price'] = format_price
app.jinja_env.filters['b64encode'] = lambda data: base64.b64encode(data).decode('utf-8')

# Create necessary directories
os.makedirs('static/images', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Function to initialize JSON data for homestays
def init_homestay_data():
    # Create a default image if it doesn't exist
    default_img_path = os.path.join('static', 'images', 'default.jpg')
    if not os.path.exists(default_img_path):
        # Create a simple colored image as default
        img = Image.new('RGB', (800, 600), color = (76, 175, 80)) 
        img.save(default_img_path)
    
    # Create hero background if it doesn't exist
    hero_bg_path = os.path.join('static', 'images', 'new_bg.jpg')
    if not os.path.exists(hero_bg_path):
        # Create a simple colored image for hero background
        hero_img = Image.new('RGB', (1920, 1080), color = (76, 175, 80))  
        hero_img.save(hero_bg_path)

# Initialize database for users
init_db()
add_sample_user()

# Initialize JSON data for homestays
init_homestay_data()

# Import and register routes after app is created
from routes import register_routes
register_routes(app)

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
