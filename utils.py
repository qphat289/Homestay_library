import os
from PIL import Image
from io import BytesIO

def format_price(price):
    """Format price with thousand separators"""
    return "{:,.0f}".format(price)

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


def resize_image(input_path, size=(800, 600)):
    """Resize an image to the specified size and return it as a BytesIO object."""
    try:
        with Image.open(input_path) as img:
            # Preserve aspect ratio
            img.thumbnail(size, Image.LANCZOS)
            img_byte_arr = BytesIO()
            # Convert RGBA to RGB if needed
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            return img_byte_arr
    except Exception as e:
        print(f"Error resizing image {input_path}: {e}")
        # Create a fallback image
        fallback = Image.new('RGB', size, color=(200, 200, 200))
        fallback_byte_arr = BytesIO()
        fallback.save(fallback_byte_arr, format='JPEG')
        fallback_byte_arr.seek(0)
        return fallback_byte_arr



