import json
import os
from database import get_db
import ast
from datetime import datetime, timedelta
from functools import lru_cache
import uuid


class User:
    @staticmethod
    def get_by_id(user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None

    @staticmethod
    def get_by_phone(phone_number):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE phone_number = ?', (phone_number,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    @staticmethod
    def get_by_email(email):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    @staticmethod
    def create(phone_number, email):
        with get_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO users (phone_number, email) VALUES (?, ?)',
                    (phone_number, email)
                )
                conn.commit()
                return User.get_by_phone(phone_number)
            except Exception as e:
                print(f"Error creating user: {e}")
                return None

class HomestayJSONManager:
    JSON_FILE = 'data/homestays.json'
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = timedelta(minutes=5)
    
    def __init__(self):
        self.data_file = os.path.join('data', 'homestays.json')
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def read_homestays(self):
        now = datetime.now()
        if 'homestays' in HomestayJSONManager._cache:
            if now - HomestayJSONManager._cache_time['homestays'] < HomestayJSONManager.CACHE_DURATION:
                return HomestayJSONManager._cache['homestays']

        if not os.path.exists(self.data_file):
            return []
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            result = data.get('homestays', data) if isinstance(data, dict) else data
            HomestayJSONManager._cache['homestays'] = result
            HomestayJSONManager._cache_time['homestays'] = now
            return result
    
    def write_homestays(self, homestays):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump({'homestays': homestays}, f, ensure_ascii=False, indent=4)
        
        # Update cache
        HomestayJSONManager._cache['homestays'] = homestays
        HomestayJSONManager._cache_time['homestays'] = datetime.now()

    def get_filter_options(self):
        """Get unique filter options from all homestays"""
        homestays = self.read_homestays()
        cities = set()
        districts = set()
        styles = set()
        
        for homestay in homestays:
            if 'style' in homestay:
                styles.add(homestay['style'])
            if 'locations' in homestay:
                for location in homestay['locations']:
                    if 'city' in location:
                        cities.add(location['city'])
                    if 'district' in location:
                        districts.add(location['district'])
        
        return {
            'cities': sorted(list(cities)),
            'districts': sorted(list(districts)),
            'styles': sorted(list(styles))
        }

    def get_homestay_by_id(self, id):
        """Get a homestay by its ID"""
        homestays = self.read_homestays()
        for homestay in homestays:
            if str(homestay.get('id')) == str(id):
                return Homestay.normalize_homestay(homestay)
        return None

class Homestay:
    @staticmethod
    def normalize_homestay(homestay):
        """Normalize homestay data to handle both old and new formats"""
        normalized = homestay.copy()
        
        # Handle location/locations
        if 'location' in homestay and isinstance(homestay['location'], dict):
            normalized['locations'] = [homestay['location']]
        elif 'locations' not in homestay:
            normalized['locations'] = [{
                'city': '',
                'district': '',
                'address': ''
            }]
            
        # Handle images/image_urls
        if 'images' in homestay and isinstance(homestay['images'], list):
            normalized['image_urls'] = homestay['images']
        elif 'image_urls' not in homestay:
            normalized['image_urls'] = ['/static/images/default.jpg']
            
        # Handle style format (string or array)
        if 'style' in homestay and isinstance(homestay['style'], list):
            normalized['style'] = ', '.join(homestay['style'])
            
        # Ensure price is a dict if it looks like a dict in string form
        if 'price' in normalized and isinstance(normalized['price'], str):
            try:
                # Try to parse string dict to actual dict
                parsed = ast.literal_eval(normalized['price'])
                if isinstance(parsed, dict):
                    normalized['price'] = parsed
            except Exception:
                pass
        return normalized

    @staticmethod
    def get_all(order_by='priority'):
        homestays = HomestayJSONManager().read_homestays()
        normalized_homestays = [Homestay.normalize_homestay(h) for h in homestays]
        
        # Sắp xếp theo priority nếu có
        if order_by == 'priority ASC':
            normalized_homestays.sort(key=lambda x: x.get('priority', 999))
        elif order_by == 'priority DESC':
            normalized_homestays.sort(key=lambda x: x.get('priority', -1), reverse=True)
        
        return normalized_homestays
    
    @staticmethod
    def search(filters=None, order_by='priority'):
        if filters is None:
            filters = {}
        
        homestays = HomestayJSONManager().read_homestays()
        filtered_homestays = []
        
        for homestay in homestays:
            normalized = Homestay.normalize_homestay(homestay)
            match = True
            
            # Lọc theo thành phố
            if 'city' in filters and filters['city']:
                if not any(loc.get('city') == filters['city'] for loc in normalized['locations']):
                    match = False
            
            # Lọc theo quận/huyện
            if 'district' in filters and filters['district']:
                if not any(loc.get('district') == filters['district'] for loc in normalized['locations']):
                    match = False
            
            # Lọc theo phường/xã
            if 'ward' in filters and filters['ward']:
                if not any(loc.get('ward') == filters['ward'] for loc in normalized['locations']):
                    match = False
            
            # Lọc theo style
            if 'style' in filters and filters['style']:
                if filters['style'] not in normalized.get('style', ''):
                    match = False
            
            if match:
                filtered_homestays.append(normalized)
        
        # Sắp xếp theo priority
        if order_by == 'priority ASC':
            filtered_homestays.sort(key=lambda x: x.get('priority', 999))
        elif order_by == 'priority DESC':
            filtered_homestays.sort(key=lambda x: x.get('priority', -1), reverse=True)
        
        return filtered_homestays

    @staticmethod
    def get_by_id(id):
        homestay_manager = HomestayJSONManager()
        return homestay_manager.get_homestay_by_id(id)

    @staticmethod
    def get_filter_options():
        homestay_manager = HomestayJSONManager()
        return homestay_manager.get_filter_options()
    
    @staticmethod
    def add_homestay(homestay_data):
        homestays = HomestayJSONManager().read_homestays()
        
        # Tìm ID lớn nhất hiện tại
        max_id = 0
        for homestay in homestays:
            if homestay['id'] > max_id:
                max_id = homestay['id']
        
        # Tạo homestay mới với ID tăng dần
        new_homestay = homestay_data.copy()
        new_homestay['id'] = max_id + 1
        
        homestays.append(new_homestay)
        HomestayJSONManager().write_homestays(homestays)
        
        return new_homestay
    
    @staticmethod
    def update_homestay(id, homestay_data):
        homestays = HomestayJSONManager().read_homestays()
        
        for i, homestay in enumerate(homestays):
            if homestay['id'] == id:
                # Giữ nguyên ID, cập nhật các trường khác
                updated_homestay = homestay_data.copy()
                updated_homestay['id'] = id
                homestays[i] = updated_homestay
                
                HomestayJSONManager().write_homestays(homestays)
                return updated_homestay
        
        return None  # Không tìm thấy homestay
    
    @staticmethod
    def delete_homestay(id):
        homestays = HomestayJSONManager().read_homestays()
        
        for i, homestay in enumerate(homestays):
            if homestay['id'] == id:
                deleted_homestay = homestays.pop(i)
                HomestayJSONManager().write_homestays(homestays)
                return deleted_homestay
        
        return None  # Không tìm thấy homestay

    @staticmethod
    def add_image(homestay_id: int, image_url: str) -> bool:
        """Add an image URL to a homestay's image_urls list"""
        homestay_manager = HomestayJSONManager()
        return homestay_manager.add_image(homestay_id, image_url)

    @staticmethod
    def remove_image(homestay_id: int, image_url: str) -> bool:
        """Remove an image URL from a homestay's image_urls list"""
        homestay_manager = HomestayJSONManager()
        return homestay_manager.remove_image(homestay_id, image_url)

    @staticmethod
    def update_images(homestay_id: int, image_urls: list) -> bool:
        """Update all images for a homestay"""
        homestay_manager = HomestayJSONManager()
        return homestay_manager.update_images(homestay_id, image_urls)

class Review:
    def __init__(self, id, homestay_id, rating, comment, created_at, username=None, user_id=None):
        self.id = id
        self.homestay_id = homestay_id
        self.rating = rating
        self.comment = comment
        self.created_at = created_at
        self.user_id = user_id
        
        # Lấy username từ database nếu có user_id
        if user_id:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                conn.close()
                self.username = user['username'] if user else ""
        else:
            self.username = username if username else ""

    @staticmethod
    def create(user_id, homestay_id, rating, comment):
        return Review(
            id=str(uuid.uuid4()),
            user_id=user_id,
            homestay_id=homestay_id,
            rating=rating,
            comment=comment,
            created_at=datetime.now().isoformat()
        )

    @staticmethod
    def calculate_average_rating(reviews):
        if not reviews:
            return 0
        total_rating = sum(review.rating for review in reviews)
        return round(total_rating / len(reviews), 1)

class ReviewJSONManager:
    def __init__(self):
        self.data_file = os.path.join('data', 'reviews.json')
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def read_reviews(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading reviews: {e}")
            return []

    def write_reviews(self, reviews):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(reviews, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error writing reviews: {e}")
            return False

    def add_review(self, review):
        reviews = self.read_reviews()
        # Kiểm tra xem user đã review homestay này chưa (kiểm tra theo user_id nếu có)
        if review.user_id:
            existing_review = next((r for r in reviews if r['user_id'] == review.user_id and str(r['homestay_id']) == str(review.homestay_id)), None)
            if existing_review:
                return False, "Bạn đã đánh giá homestay này rồi"
        
        reviews.append(review.__dict__)
        return self.write_reviews(reviews)

    def get_reviews_by_homestay(self, homestay_id):
        reviews = self.read_reviews()
        return [Review(**review) for review in reviews if str(review['homestay_id']) == str(homestay_id)]

    def get_average_rating(self, homestay_id):
        reviews = self.get_reviews_by_homestay(homestay_id)
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)