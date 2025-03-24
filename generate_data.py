import random
import json
import datetime
import os
from uuid import uuid4


# Danh sách các tên phòng
room_name_prefixes = ["Cozy", "Modern", "Luxury", "Rustic", "Elegant", "Classic", "Charming", "Deluxe", "Peaceful", "Scenic"]
room_name_types = ["Villa", "Apartment", "Homestay", "Bungalow", "Suite", "House", "Condo", "Cabin", "Studio", "Cottage"]
room_name_locations = ["Riverside", "Garden", "Mountain View", "Beachfront", "Downtown", "Lakeside", "Forest", "City Center", "Sea View", "Hillside"]

# Danh sách các phong cách
styles = ["Hiện đại", "Cổ điển", "Tối giản", "Vintage", "Bohemian", "Scandinavian", "Tropical", "Industrial", "Rustic", "Contemporary"]

# Tiện ích phòng
room_amenities = [
    "Wi-Fi miễn phí", "TV màn hình phẳng", "Máy điều hòa", "Minibar", "Két an toàn", "Máy sấy tóc", 
    "Áo choàng tắm", "Dép đi trong phòng", "Máy pha cà phê", "Tủ lạnh mini", "Máy giặt", "Lò vi sóng",
    "Bàn làm việc", "Ghế nghỉ", "Ban công riêng", "Phòng tắm riêng", "Bồn tắm", "Vòi sen"
]

# Tiện ích xung quanh
surrounding_amenities = [
    "Nhà hàng", "Quán cà phê", "Siêu thị", "Chợ địa phương", "Bãi biển", "Công viên", 
    "Trung tâm mua sắm", "Bến xe buýt", "Trạm taxi", "Sân bay", "Bến tàu", "Trung tâm thành phố",
    "Bảo tàng", "Rạp chiếu phim", "Trung tâm thể thao", "Spa", "Gym", "Hồ bơi"
]

# Đặc điểm nổi bật
highlights = [
    "Không gian yên tĩnh", "View đẹp", "Nội thất sang trọng", "Đồ dùng cao cấp", 
    "Thiết kế độc đáo", "Khu vườn xinh xắn", "Sân thượng rộng rãi", "Bếp đầy đủ tiện nghi"
]

# Danh sách các quận và thành phố
districts_cities = [
    {"district": "Quận 1", "city": "Hồ Chí Minh"},
    {"district": "Quận 2", "city": "Hồ Chí Minh"},
    {"district": "Quận 3", "city": "Hồ Chí Minh"},
    {"district": "Hoàn Kiếm", "city": "Hà Nội"},
    {"district": "Ba Đình", "city": "Hà Nội"},
    {"district": "Hải Châu", "city": "Đà Nẵng"},
    {"district": "Sơn Trà", "city": "Đà Nẵng"}
]

# Danh sách họ và tên người Việt
first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Vũ", "Võ", "Phan", "Đặng"]
middle_names = ["Văn", "Thị", "Hữu", "Đức", "Công", "Quang", "Minh", "Hoàng"]
last_names = ["An", "Bình", "Cường", "Dũng", "Hùng", "Hương", "Lan", "Linh", "Mai"]

# Danh sách comment đánh giá
comments_positive = [
    "Phòng rất sạch sẽ và thoải mái, tôi rất hài lòng với dịch vụ.",
    "Vị trí tuyệt vời, gần các điểm tham quan và rất dễ tìm.",
    "Chủ nhà rất thân thiện và nhiệt tình giúp đỡ chúng tôi.",
    "Tôi rất thích thiết kế và cách bày trí của căn phòng.",
    "Giá cả hợp lý cho chất lượng dịch vụ được cung cấp.",
    "Chúng tôi sẽ quay lại đây vào lần sau!",
    "Một trong những trải nghiệm lưu trú tốt nhất của tôi."
]

comments_neutral = [
    "Phòng ở mức ổn, không quá xuất sắc nhưng cũng không tệ.",
    "Dịch vụ tạm được, còn một số điểm cần cải thiện.",
    "Vị trí không quá trung tâm nhưng cũng dễ di chuyển.",
    "Wi-Fi chập chờn nhưng vẫn sử dụng được.",
    "Tiện nghi cơ bản đầy đủ nhưng không có gì nổi bật.",
    "Chủ nhà đáp ứng yêu cầu nhưng không nhiệt tình lắm."
]

comments_negative = [
    "Phòng không được dọn dẹp sạch sẽ, tôi thấy rất thất vọng.",
    "Nhân viên phục vụ thiếu chuyên nghiệp.",
    "Tiếng ồn từ bên ngoài rất lớn, khó ngủ vào ban đêm.",
    "Vị trí xa trung tâm, không thuận tiện cho việc di chuyển.",
    "Chất lượng không xứng với giá tiền.",
    "Các tiện nghi trong phòng đã cũ và không hoạt động tốt."
]

def random_date(start_date, end_date):
    """Tạo ngày ngẫu nhiên giữa start_date và end_date"""
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return (start_date + datetime.timedelta(days=random_number_of_days)).strftime("%Y-%m-%dT%H:%M:%S")

def generate_review(username, homestay_id, rating):
    """Tạo một đánh giá ngẫu nhiên"""
    # Chọn comment dựa trên rating
    if rating >= 4:
        comment = random.choice(comments_positive)
    elif rating >= 3:
        comment = random.choice(comments_neutral)
    else:
        comment = random.choice(comments_negative)
    
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date.today()
    
    return {
        "id": str(uuid4()),
        "username": username,
        "homestay_id": homestay_id,
        "rating": rating,
        "comment": comment,
        "created_at": random_date(start_date, end_date)
    }

def generate_homestay(id):
    """Tạo một homestay ngẫu nhiên"""
    prefix = random.choice(room_name_prefixes)
    type = random.choice(room_name_types)
    location = random.choice(room_name_locations)
    name = f"{prefix} {type} {location}"
    
    # Tạo 1-3 cơ sở cho mỗi homestay
    num_locations = random.randint(1, 3)
    locations = []
    for _ in range(num_locations):
        district_city = random.choice(districts_cities)
        address = f"Số {random.randint(1, 200)}, Đường {random.choice(['Lê Lợi', 'Nguyễn Huệ', 'Trần Hưng Đạo'])}"
        locations.append({
            "address": address,
            "district": district_city["district"],
            "city": district_city["city"]
        })
    
    # Tạo 3-5 links ảnh
    num_images = random.randint(3, 5)
    image_urls = [f"static/images/homestay{random.randint(1, 20)}.jpg" for _ in range(num_images)]
    
    # Chọn ngẫu nhiên các tiện ích, đặc điểm nổi bật
    selected_room_amenities = ", ".join(random.sample(room_amenities, random.randint(5, 10)))
    selected_surrounding_amenities = ", ".join(random.sample(surrounding_amenities, random.randint(5, 8)))
    selected_highlights = ", ".join(random.sample(highlights, random.randint(3, 5)))
    
    # Tạo giá ngẫu nhiên (500k - 5tr)
    price = random.randint(5, 50) * 100000
    
    # Chọn ngẫu nhiên 2-3 phong cách
    selected_styles = ", ".join(random.sample(styles, random.randint(2, 3)))
    
    # Tạo mô tả
    description = f"Chào mừng bạn đến với {name}! Đây là một không gian tuyệt vời tại {locations[0]['district']}, {locations[0]['city']}."
    
    return {
        "id": id,
        "name": name,
        "description": description,
        "price": price,
        "rating": 0,  # Sẽ được tính toán sau khi có đánh giá
        "image_urls": image_urls,
        "locations": locations,
        "style": selected_styles,
        "room_amenities": selected_room_amenities,
        "surrounding_amenities": selected_surrounding_amenities,
        "highlights": selected_highlights,
        "priority": random.choice([0, 1, 1, 1])  # 75% homestay khả dụng
    }

def generate_data():
    """Tạo dữ liệu cho 50 homestays và đánh giá"""
    homestays = []
    reviews = []
    
    for i in range(1, 51):
        # Tạo homestay
        homestay = generate_homestay(i)
        homestays.append(homestay)
        
        # Tạo 2-4 đánh giá cho mỗi homestay
        num_reviews = random.randint(2, 4)
        homestay_reviews = []
        
        for _ in range(num_reviews):
            # Tạo tên người dùng ngẫu nhiên
            username = f"{random.choice(first_names)} {random.choice(middle_names)} {random.choice(last_names)}"
            
            # Tạo đánh giá với rating ngẫu nhiên từ 1-5
            rating = random.randint(1, 5)
            review = generate_review(username, homestay["id"], rating)
            homestay_reviews.append(review)
            reviews.append(review)
        
        # Tính rating trung bình cho homestay
        avg_rating = sum(review["rating"] for review in homestay_reviews) / len(homestay_reviews)
        homestay["rating"] = round(avg_rating, 1)
    
    return homestays, reviews

def save_to_json():
    """Lưu dữ liệu vào file JSON"""
    homestays, reviews = generate_data()
    
    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Lưu homestays với encoding đúng
    with open("data/homestays.json", "w", encoding="utf-8") as f:
        json_str = json.dumps(homestays, ensure_ascii=False, indent=2)
        f.write(json_str)
    
    # Lưu reviews với encoding đúng
    with open("data/reviews.json", "w", encoding="utf-8") as f:
        json_str = json.dumps(reviews, ensure_ascii=False, indent=2)
        f.write(json_str)
    
    print(f"Đã tạo thành công {len(homestays)} homestays và {len(reviews)} đánh giá.")
    print(f"Dữ liệu đã được lưu vào thư mục 'data'.")

if __name__ == "__main__":
    save_to_json() 