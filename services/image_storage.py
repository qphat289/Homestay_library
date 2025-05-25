import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, List
import os

class ImageStorageService:
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )

    def upload_image(self, file_path: str, folder: str = 'homestay') -> Optional[str]:
        """
        Upload an image to Cloudinary
        Returns the URL of the uploaded image
        """
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                resource_type="image"
            )
            return result.get('secure_url')
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None

    def delete_image(self, public_id: str) -> bool:
        """
        Delete an image from Cloudinary
        Returns True if successful
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False

    def get_image_url(self, public_id: str) -> Optional[str]:
        """
        Get the URL of an image from its public_id
        """
        try:
            result = cloudinary.api.resource(public_id)
            return result.get('secure_url')
        except Exception as e:
            print(f"Error getting image URL: {e}")
            return None 