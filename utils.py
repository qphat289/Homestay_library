import os
from PIL import Image
from io import BytesIO
import io
from functools import lru_cache

# Define image sizes
IMAGE_SIZES = {
    'thumbnail': (300, 200),
    'medium': (800, 600),
    'large': (1200, 800),
    'full': None
}

def format_price(price):
    """Format price with thousand separators"""
    return price

def get_image_url(image_path):
    """Return image URL, or default if image doesn't exist"""
    if image_path and os.path.exists(os.path.join('static', image_path.lstrip('/'))):
        return image_path
    else:
        return '/static/images/default.jpg'

# Function to disable login (for reference)
def disable_login_instructions():
    """
    To disable login requirement:
    
    1. Open routes.py
    2. Find the index route function
    3. Remove or comment out the session check lines:
       # if 'phone_number' not in session:
       #     return redirect(url_for('login'))
    """
    pass

@lru_cache(maxsize=100)
def resize_image(image_data, size='medium', quality=85):
    """
    Resize image with caching for better performance
    """
    if not image_data:
        return None
        
    try:
        # Convert bytes to image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # Get target size
        target_size = IMAGE_SIZES.get(size)
        if not target_size:
            return image_data
            
        # Calculate new size maintaining aspect ratio
        width, height = img.size
        target_width, target_height = target_size
        
        # Calculate aspect ratios
        img_ratio = width / height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # Image is wider than target
            new_width = target_width
            new_height = int(target_width / img_ratio)
        else:
            # Image is taller than target
            new_height = target_height
            new_width = int(target_height * img_ratio)
            
        # Resize image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Save to bytes with optimization
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image_data

def optimize_image(image_path, quality=85):
    """
    Optimize an image file for web use
    """
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # Save with optimization
        img.save(image_path, format='JPEG', quality=quality, optimize=True)
        
    except Exception as e:
        print(f"Error optimizing image {image_path}: {e}")

def convert_to_webp(image_data, quality=85):
    """
    Convert image to WebP format for better performance
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # Save as WebP
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=quality)
        return output.getvalue()
        
    except Exception as e:
        print(f"Error converting to WebP: {e}")
        return image_data

def get_image_size(image_data):
    """
    Get image dimensions without loading the entire image
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        return img.size
    except Exception as e:
        print(f"Error getting image size: {e}")
        return None



