import json
import os
from database import get_db_connection


class User:
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', 
                          (user_id,)).fetchone()
        conn.close()
        return user

    @staticmethod
    def get_by_phone(phone_number):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE phone_number = ?', 
                          (phone_number,)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', 
                          (email,)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def create(phone_number, email):
        # Kiểm tra số điện thoại đã tồn tại chưa
        existing_user = User.get_by_phone(phone_number)
        if existing_user:
            return None
            
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (phone_number, email) VALUES (?, ?)',
                       (phone_number, email))
            conn.commit()
            user = User.get_by_phone(phone_number)
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            conn.close()

class HomestayJSONManager:
    JSON_FILE = 'data/homestays.json'
    
    @staticmethod
    def read_homestays():
        if not os.path.exists(HomestayJSONManager.JSON_FILE):
            return []
        
        with open(HomestayJSONManager.JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both formats - direct array or nested under 'homestays' key
            return data.get('homestays', data) if isinstance(data, dict) else data
    
    @staticmethod
    def write_homestays(homestays):
        os.makedirs(os.path.dirname(HomestayJSONManager.JSON_FILE), exist_ok=True)
        
        with open(HomestayJSONManager.JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump({'homestays': homestays}, f, ensure_ascii=False, indent=4)

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
            
        return normalized

    @staticmethod
    def get_all(order_by='priority'):
        homestays = HomestayJSONManager.read_homestays()
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
        
        homestays = HomestayJSONManager.read_homestays()
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
        homestays = HomestayJSONManager.read_homestays()
        # Convert id to integer if it's a string
        try:
            id_to_find = int(id)
        except (ValueError, TypeError):
            id_to_find = id
            
        for homestay in homestays:
            if str(homestay.get('id')) == str(id_to_find):
                return Homestay.normalize_homestay(homestay)
        return None

    @staticmethod
    def get_filter_options():
        homestays = HomestayJSONManager.read_homestays()
        
        cities = set()
        districts = set()
        wards = set()
        styles = set()
        
        for homestay in homestays:
            if 'locations' in homestay:
                for location in homestay['locations']:
                    # Kiểm tra sự tồn tại của trường trước khi truy cập
                    if 'city' in location:
                        cities.add(location['city'])
                    if 'district' in location:
                        districts.add(location['district'])
                    if 'ward' in location:
                        wards.add(location['ward'])
            
            # Xử lý style (chuỗi phân cách bởi dấu phẩy)
            if 'style' in homestay:
                style_list = [s.strip() for s in homestay['style'].split(',')]
                styles.update(style_list)
        
        # Chuyển đổi sang định dạng tương thích với template
        cities_list = [{'city': city} for city in cities]
        districts_list = [{'district': district} for district in districts]
        wards_list = [{'ward': ward} for ward in wards]
        
        return {
            'cities': cities_list,
            'districts': districts_list,
            'wards': wards_list,
            'styles': sorted(styles)
        }
    
    @staticmethod
    def add_homestay(homestay_data):
        homestays = HomestayJSONManager.read_homestays()
        
        # Tìm ID lớn nhất hiện tại
        max_id = 0
        for homestay in homestays:
            if homestay['id'] > max_id:
                max_id = homestay['id']
        
        # Tạo homestay mới với ID tăng dần
        new_homestay = homestay_data.copy()
        new_homestay['id'] = max_id + 1
        
        homestays.append(new_homestay)
        HomestayJSONManager.write_homestays(homestays)
        
        return new_homestay
    
    @staticmethod
    def update_homestay(id, homestay_data):
        homestays = HomestayJSONManager.read_homestays()
        
        for i, homestay in enumerate(homestays):
            if homestay['id'] == id:
                # Giữ nguyên ID, cập nhật các trường khác
                updated_homestay = homestay_data.copy()
                updated_homestay['id'] = id
                homestays[i] = updated_homestay
                
                HomestayJSONManager.write_homestays(homestays)
                return updated_homestay
        
        return None  # Không tìm thấy homestay
    
    @staticmethod
    def delete_homestay(id):
        homestays = HomestayJSONManager.read_homestays()
        
        for i, homestay in enumerate(homestays):
            if homestay['id'] == id:
                deleted_homestay = homestays.pop(i)
                HomestayJSONManager.write_homestays(homestays)
                return deleted_homestay
        
        return None  # Không tìm thấy homestay

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
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            conn.close()
            self.username = user['username'] if user else ""
        else:
            self.username = username if username else ""

    @staticmethod
    def create(user_id, homestay_id, rating, comment):
        from datetime import datetime
        import uuid
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
    def __init__(self, json_file='data/reviews.json'):
        self.json_file = json_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.json_file):
            os.makedirs(os.path.dirname(self.json_file), exist_ok=True)
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def read_reviews(self):
        with open(self.json_file, 'r', encoding='utf-8') as f:
            reviews_data = json.load(f)
        return [Review(**review) for review in reviews_data]

    def write_reviews(self, reviews):
        reviews_data = [vars(review) for review in reviews]
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(reviews_data, f, ensure_ascii=False, indent=4)

    def add_review(self, review):
        reviews = self.read_reviews()
        # Kiểm tra xem user đã review homestay này chưa (kiểm tra theo user_id nếu có)
        if review.user_id:
            existing_review = next((r for r in reviews if r.user_id == review.user_id and str(r.homestay_id) == str(review.homestay_id)), None)
            if existing_review:
                return False, "Bạn đã đánh giá homestay này rồi"
        
        reviews.append(review)
        self.write_reviews(reviews)
        return True, "Đánh giá của bạn đã được ghi nhận"

    def get_reviews_by_homestay(self, homestay_id):
        reviews = self.read_reviews()
        return [r for r in reviews if str(r.homestay_id) == str(homestay_id)]

    def get_average_rating(self, homestay_id):
        reviews = self.get_reviews_by_homestay(homestay_id)
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)