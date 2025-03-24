from models import User, Homestay, HomestayJSONManager, Review, ReviewJSONManager
from flask import Flask, render_template, request, redirect, session, send_file, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from io import BytesIO
import os
import json
from utils import resize_image
from datetime import datetime
import uuid
from auth import UserLogin
import re


def register_routes(app):
    @app.route('/')
    @login_required
    def index():
        # Get search query
        search_query = request.args.get('search', '').lower()
        
        # Get all homestays and filter options
        homestay_manager = HomestayJSONManager()
        homestays = homestay_manager.read_homestays()
        filter_options = Homestay.get_filter_options()
        
        # Chuẩn hóa priority và sắp xếp
        for homestay in homestays:
            # Đảm bảo priority chỉ nhận giá trị 1, 2, 3
            priority = homestay.get('priority', 3)
            if priority not in [1, 2, 3]:
                homestay['priority'] = 3
        
        # Sắp xếp theo priority (1 -> 2 -> 3)
        homestays = sorted(homestays, key=lambda x: x['priority'])
        
        # Filter homestays if search query exists
        if search_query:
            filtered_homestays = []
            for homestay in homestays:
                if (search_query in homestay['name'].lower() or
                    search_query in homestay['description'].lower() or
                    search_query in homestay['style'].lower() or
                    any(search_query in location['address'].lower() or
                        search_query in location['district'].lower() or
                        search_query in location['city'].lower()
                        for location in homestay['locations'])):
                    filtered_homestays.append(homestay)
            homestays = filtered_homestays
        
        return render_template('index.html', 
                            homestays=homestays,
                            cities=filter_options['cities'],
                            districts=filter_options['districts'],
                            styles=filter_options['styles'])

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            phone_number = request.form['phone_number']
            
            # Validate phone number
            if not phone_number.isdigit() or len(phone_number) != 10:
                flash('Số điện thoại không hợp lệ. Vui lòng nhập đúng 10 chữ số', 'error')
                return render_template('login.html')
            
            # Check if user exists by phone number
            user_data = User.get_by_phone(phone_number)
            
            # If user exists, log them in
            if user_data:
                user = UserLogin(user_data)
                login_user(user)
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('index'))
            
            # If user doesn't exist and email is provided, try to register them
            elif 'email' in request.form and request.form['email']:
                email = request.form['email']
                
                # Check if email already exists
                existing_user = User.get_by_email(email)
                if existing_user:
                    flash('Email này đã được đăng ký. Vui lòng sử dụng email khác.', 'error')
                    return render_template('login.html', phone_number=phone_number, need_email=True)
                
                # Create new user
                user_data = User.create(phone_number, email)
                if user_data:
                    user = UserLogin(user_data)
                    login_user(user)
                    flash('Đăng ký thành công!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Số điện thoại này đã được đăng ký. Vui lòng sử dụng số điện thoại khác.', 'error')
                    return render_template('login.html')
            
            # If user doesn't exist and no email provided, ask for email
            else:
                return render_template('login.html', phone_number=phone_number, need_email=True)
        
        return render_template('login.html', need_email=False)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Đã đăng xuất thành công!', 'success')
        return redirect(url_for('login'))

    @app.route('/search', methods=['GET'])
    def search():
        # Get filter parameters
        filters = {
            'city': request.args.get('city', ''),
            'district': request.args.get('district', ''),
            'style': request.args.get('style', '')
        }
        
        # Get search query
        search_query = request.args.get('search', '').lower()
        
        # Search homestays with filters
        homestays = Homestay.search(filters)
        
        # Chuẩn hóa priority và sắp xếp
        for homestay in homestays:
            # Đảm bảo priority chỉ nhận giá trị 1, 2, 3
            priority = homestay.get('priority', 3)
            if priority not in [1, 2, 3]:
                homestay['priority'] = 3
        
        # Sắp xếp theo priority (1 -> 2 -> 3)
        homestays = sorted(homestays, key=lambda x: x['priority'])
        
        # Filter homestays if search query exists
        if search_query:
            filtered_homestays = []
            for homestay in homestays:
                if (search_query in homestay['name'].lower() or
                    search_query in homestay['description'].lower() or
                    search_query in homestay['style'].lower() or
                    any(search_query in location['address'].lower() or
                        search_query in location['district'].lower() or
                        search_query in location['city'].lower()
                        for location in homestay['locations'])):
                    filtered_homestays.append(homestay)
            homestays = filtered_homestays
        
        # Get filter options for dropdowns
        filter_options = Homestay.get_filter_options()
        
        return render_template('index.html', 
                            homestays=homestays, 
                            cities=filter_options['cities'],
                            districts=filter_options['districts'],
                            styles=filter_options['styles'],
                            selected_city=filters['city'],
                            selected_district=filters['district'],
                            selected_style=filters['style'],
                            search_query=search_query)

    @app.route('/booking', methods=['POST'])
    def booking():
        if 'phone_number' not in session:
            return redirect(url_for('login'))
        
        homestay_id = request.form.get('homestay_id')
        location_index = int(request.form.get('location_index', 0))
        
        # TODO: Implement booking logic here
        flash('Chức năng đặt phòng đang được phát triển', 'info')
        return redirect(url_for('homestay_detail', id=homestay_id))

    @app.route('/homestay/<id>', methods=['GET'])
    @login_required
    def homestay_detail(id):
        homestay = Homestay.get_by_id(id)
        if not homestay:
            flash('Không tìm thấy homestay', 'error')
            return redirect(url_for('index'))

        review_manager = ReviewJSONManager()
        reviews = review_manager.get_reviews_by_homestay(id)
        
        # Tính điểm trung bình từ reviews
        average_rating = Review.calculate_average_rating(reviews)
        
        # Lấy thông tin user cho mỗi review
        for review in reviews:
            user = User.get_by_id(review.user_id)
            review.username = user['username'] if user else "Người dùng ẩn danh"
        
        # Sắp xếp reviews theo thời gian mới nhất
        reviews.sort(key=lambda x: x.created_at, reverse=True)
        
        return render_template('detail.html', 
                             homestay=homestay, 
                             reviews=reviews,
                             average_rating=average_rating,
                             review_count=len(reviews))

    @app.route('/homestay/<id>/review', methods=['POST'])
    @login_required
    def add_review(id):
        review_manager = ReviewJSONManager()
        
        # Kiểm tra xem người dùng đã review chưa
        existing_reviews = review_manager.get_reviews_by_homestay(id)
        for review in existing_reviews:
            if str(review.user_id) == str(current_user.id):
                flash('Bạn đã đánh giá homestay này rồi!', 'error')
                return redirect(url_for('homestay_detail', id=id))
        
        rating = request.form.get('rating', '0')  # Default to '0' if not provided
        comment = request.form.get('comment', '').strip()
        
        # Kiểm tra rating
        try:
            rating_value = int(rating)
            if rating_value == 0:
                flash('Vui lòng chọn số sao đánh giá', 'error')
                return redirect(url_for('homestay_detail', id=id))
        except ValueError:
            flash('Đánh giá không hợp lệ', 'error')
            return redirect(url_for('homestay_detail', id=id))
        
        # Kiểm tra comment
        if not comment:
            flash('Vui lòng nhập nhận xét của bạn', 'error')
            return redirect(url_for('homestay_detail', id=id))
        
        # Tạo review mới
        review = Review.create(
            user_id=current_user.id,
            homestay_id=id,
            rating=rating_value,
            comment=comment
        )
        
        # Thêm review mới
        review_manager.add_review(review)
        
        flash('Cảm ơn bạn đã đánh giá!', 'success')
        return redirect(url_for('homestay_detail', id=id))

    # Thêm route cho trang Giới thiệu
    @app.route('/about')
    @login_required
    def about():
        return render_template('about.html')
    
    # Thêm route cho trang Liên hệ
    @app.route('/contact')
    @login_required
    def contact():
        return render_template('contact.html')

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, message="Trang không tồn tại"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', error_code=500, message="Lỗi máy chủ"), 500


    @app.route('/serve_image/<int:homestay_id>/<int:image_index>/<string:size>')
    def serve_image(homestay_id, image_index, size='full'):
        homestay = Homestay.get_by_id(homestay_id)
        
        # Đường dẫn đến ảnh mặc định
        default_image_path = os.path.join(app.root_path, 'static', 'images', 'default.jpg')
        
        # Kiểm tra homestay và image_urls
        if not homestay or 'image_urls' not in homestay or not homestay['image_urls']:
            print(f"Using default image for homestay {homestay_id}")
            return send_file(default_image_path, mimetype='image/jpeg')

        # Kiểm tra và log index
        if image_index >= len(homestay['image_urls']) or image_index < 0:
            print(f"Image index {image_index} out of range for homestay {homestay_id}")
            image_index = 0

        image_url = homestay['image_urls'][image_index]
        
        # Kiểm tra URL có giá trị không
        if not image_url:
            print(f"Empty image URL at index {image_index} for homestay {homestay_id}")
            return send_file(default_image_path, mimetype='image/jpeg')
        
        # Xử lý đường dẫn ảnh - sử dụng app.root_path
        if image_url.startswith('./'):
            image_path = os.path.join(app.root_path, image_url[2:])
        elif image_url.startswith('/'):
            image_path = os.path.join(app.root_path, image_url[1:])
        else:
            image_path = os.path.join(app.root_path, image_url)
        
        print(f"Looking for image at: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return send_file(default_image_path, mimetype='image/jpeg')
        
        # Xử lý kích thước
        if size == 'thumbnail':
            img_byte_arr = resize_image(image_path, size=(200, 150))
            return send_file(img_byte_arr, mimetype='image/jpeg')
        
        # Trả về ảnh gốc
        return send_file(image_path, mimetype='image/jpeg')

    @app.route('/<name>', methods=['GET'])
    @login_required
    def homestay_by_name(name):
        # Skip for index route
        if name == '':
            return redirect(url_for('index'))
            
        # Get all homestays
        homestay_manager = HomestayJSONManager()
        homestays = homestay_manager.read_homestays()
        
        # Find homestay by slug
        for homestay in homestays:
            # Create slug from homestay name
            slug = re.sub(r'[^\w\s-]', '', homestay['name'].lower())
            slug = re.sub(r'[\s-]+', '-', slug)
            
            if slug == name:
                return redirect(url_for('homestay_detail', id=homestay['id']))
                
        # If not a homestay, check if it's a standard route
        if name in ['about', 'contact', 'login', 'logout', 'search', 'booking']:
            return redirect(url_for(name))
                
        flash('Không tìm thấy trang yêu cầu', 'error')
        return redirect(url_for('index'))



