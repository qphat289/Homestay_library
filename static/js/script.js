// Đặt ở đầu file, ngay sau dòng đầu tiên
document.addEventListener('DOMContentLoaded', function() {
    // Xử lý flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(100%)';
            flash.style.transition = 'all 0.5s ease-in-out';
            
            setTimeout(() => {
                flash.remove();
            }, 500);
        }, 3000);

        const closeButton = flash.querySelector('.btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                flash.style.opacity = '0';
                flash.style.transform = 'translateX(100%)';
                setTimeout(() => flash.remove(), 500);
            });
        }
    });
    
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Image Modal Functionality
    const createImageModal = () => {
        // Create modal container if it doesn't exist
        if (!document.getElementById('imageModal')) {
            const modal = document.createElement('div');
            modal.id = 'imageModal';
            modal.className = 'image-modal fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90 invisible opacity-0 transition-all duration-300';
            modal.innerHTML = `
                <button class="modal-nav-btn prev-btn absolute left-4 top-1/2 z-20" aria-label="Ảnh trước đó"></button>
                <div class="modal-content relative max-w-5xl mx-auto p-4">
                    <button class="close-modal absolute top-4 right-4 bg-white rounded-full p-2 text-gray-800 hover:bg-gray-200 transition-colors z-20" aria-label="Đóng">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                        </svg>
                    </button>
                    <img src="" alt="Ảnh phóng to" class="modal-image max-h-[90vh] max-w-full object-contain rounded shadow-lg">
                    <div class="image-counter absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/50 text-white px-4 py-2 rounded-full text-sm backdrop-blur-sm">
                        <span class="current-index">1</span>/<span class="total-count">1</span>
                    </div>
                </div>
                <button class="modal-nav-btn next-btn absolute right-4 top-1/2 z-20" aria-label="Ảnh tiếp theo"></button>
            `;
            document.body.appendChild(modal);
            
            // Mảng lưu trữ tất cả các ảnh có thể xem
            window.modalImages = [];
            window.currentImageIndex = 0;
            
            // Add event listeners for closing modal
            const closeBtn = modal.querySelector('.close-modal');
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeImageModal();
            });
            
            // Sự kiện cho nút điều hướng trước
            const prevBtn = modal.querySelector('.prev-btn');
            prevBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                navigateImage(-1);
            });
            
            // Sự kiện cho nút điều hướng tiếp
            const nextBtn = modal.querySelector('.next-btn');
            nextBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                navigateImage(1);
            });
            
            // Sự kiện phím mũi tên
            document.addEventListener('keydown', function(e) {
                if (modal.classList.contains('visible')) {
                    if (e.key === 'ArrowLeft') {
                        navigateImage(-1);
                    } else if (e.key === 'ArrowRight') {
                        navigateImage(1);
                    }
                }
            });
            
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    closeImageModal();
                }
            });
            
            // Close on Escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    const modal = document.getElementById('imageModal');
                    if (modal && modal.classList.contains('visible')) {
                        closeImageModal();
                    }
                }
            });
        }
    };
    
    // Hàm điều hướng ảnh
    const navigateImage = (direction) => {
        // Lấy danh sách ảnh hiện tại
        const images = window.modalImages;
        if (!images || images.length <= 1) return;
        
        // Tính toán index mới
        let newIndex = window.currentImageIndex + direction;
        
        // Xử lý trường hợp vượt quá giới hạn
        if (newIndex < 0) newIndex = images.length - 1;
        if (newIndex >= images.length) newIndex = 0;
        
        // Cập nhật ảnh hiện tại
        window.currentImageIndex = newIndex;
        
        const modal = document.getElementById('imageModal');
        if (!modal) return;
        
        // Cập nhật ảnh và thông tin
        const modalImage = modal.querySelector('.modal-image');
        const currentIndexElement = modal.querySelector('.current-index');
        
        if (modalImage && currentIndexElement) {
            const currentImage = images[newIndex];
            modalImage.src = currentImage.src;
            modalImage.alt = currentImage.alt || 'Ảnh phóng to';
            currentIndexElement.textContent = newIndex + 1;
            
            // Thêm hiệu ứng chuyển đổi
            modalImage.classList.add('image-transition');
            setTimeout(() => {
                modalImage.classList.remove('image-transition');
            }, 300);
        }
    };
    
    const openImageModal = (imageSrc, alt) => {
        console.log('Mở modal với ảnh:', imageSrc);
        
        // Tạo modal nếu chưa tồn tại
        createImageModal();
        
        const modal = document.getElementById('imageModal');
        if (!modal) {
            console.error('Không tìm thấy modal');
            return;
        }
        
        // Thu thập tất cả các ảnh tương tự để điều hướng
        collectImages(imageSrc);
        
        const modalImage = modal.querySelector('.modal-image');
        const currentIndexElement = modal.querySelector('.current-index');
        const totalCountElement = modal.querySelector('.total-count');
        
        if (!modalImage) {
            console.error('Không tìm thấy ảnh trong modal');
            return;
        }
        
        // Fix đường dẫn ảnh nếu cần
        if (imageSrc && !imageSrc.startsWith('http')) {
            if (!imageSrc.startsWith('/')) {
                imageSrc = '/' + imageSrc;
            }
        }
        
        modalImage.src = imageSrc;
        modalImage.alt = alt || 'Ảnh phóng to';
        
        // Cập nhật số lượng ảnh và vị trí hiện tại
        if (currentIndexElement && totalCountElement) {
            currentIndexElement.textContent = window.currentImageIndex + 1;
            totalCountElement.textContent = window.modalImages.length;
        }
        
        // Hiển thị/ẩn nút điều hướng dựa vào số lượng ảnh
        const navButtons = modal.querySelectorAll('.modal-nav-btn');
        navButtons.forEach(btn => {
            if (window.modalImages.length <= 1) {
                btn.classList.add('hidden');
            } else {
                btn.classList.remove('hidden');
            }
        });
        
        // Show modal with animation
        modal.classList.remove('invisible', 'opacity-0');
        modal.classList.add('visible', 'opacity-100');
        
        // Disable body scroll
        document.body.style.overflow = 'hidden';
    };
    
    // Thu thập tất cả các ảnh tương tự để điều hướng
    const collectImages = (currentImageSrc) => {
        // Reset mảng ảnh
        window.modalImages = [];
        
        // Tìm tất cả các ảnh trong cùng container
        let sourceImage = null;
        const allImages = document.querySelectorAll('img[data-modal-setup="true"]');
        
        // Tìm ảnh hiện tại
        allImages.forEach(img => {
            if (img.src === currentImageSrc || currentImageSrc.includes(img.src) || img.src.includes(currentImageSrc)) {
                sourceImage = img;
            }
            // Thêm tất cả ảnh vào mảng để điều hướng
            window.modalImages.push(img);
        });
        
        // Tìm index của ảnh hiện tại
        window.currentImageIndex = 0;
        if (sourceImage) {
            for (let i = 0; i < window.modalImages.length; i++) {
                if (window.modalImages[i] === sourceImage) {
                    window.currentImageIndex = i;
                    break;
                }
            }
        }
        
        console.log(`Đã tìm thấy ${window.modalImages.length} ảnh, đang hiển thị ảnh thứ ${window.currentImageIndex + 1}`);
    };
    
    const closeImageModal = () => {
        const modal = document.getElementById('imageModal');
        if (modal) {
            // Hide modal with animation
            modal.classList.remove('visible', 'opacity-100');
            modal.classList.add('invisible', 'opacity-0');
            
            // Re-enable body scroll
            document.body.style.overflow = '';
            
            // Clear image after animation completes
            setTimeout(() => {
                const modalImage = modal.querySelector('.modal-image');
                if (modalImage) {
                    modalImage.src = '';
                }
            }, 300);
        }
    };
    
    // Add click event to all images that should be expandable
    const setupImageClicks = () => {
        // Chọn tất cả các ảnh cần phóng to
        const imageElements = document.querySelectorAll('.card-image, .w-full.h-64.object-cover, img[src^="/images/homestay"], .carousel-item img');
        
        console.log('Số lượng ảnh tìm thấy:', imageElements.length);
        
        imageElements.forEach(image => {
            // Đảm bảo chỉ thêm sự kiện cho ảnh hợp lệ
            if (!image || image.hasAttribute('data-modal-setup')) {
                return;
            }
            
            // Đánh dấu ảnh đã được thiết lập
            image.setAttribute('data-modal-setup', 'true');
            
            // Add visual indication that image is clickable
            image.classList.add('cursor-pointer', 'hover:opacity-90', 'transition-opacity');
            
            // Add tabindex and aria attributes for accessibility
            image.setAttribute('tabindex', '0');
            image.setAttribute('aria-label', `${image.alt || 'Hình ảnh'} - Nhấn để xem phóng to`);
            
            // Handle click event
            image.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Đã click vào ảnh:', this.src);
                openImageModal(this.src, this.alt);
            });
            
            // Handle keyboard event for accessibility
            image.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    openImageModal(this.src, this.alt);
                }
            });
        });
    };
    
    // Run setup
    setupImageClicks();
    
    // Đăng ký lại setupImageClicks khi DOM có thể thay đổi
    document.addEventListener('DOMContentLoaded', setupImageClicks);
    
    // Chạy lại khi trang đã load hoàn chỉnh
    window.addEventListener('load', setupImageClicks);
    
    // Handle city selection to filter districts
    const citySelect = document.getElementById('city');
    const districtSelect = document.getElementById('district');
    
    if (citySelect && districtSelect) {
        citySelect.addEventListener('change', function() {
            // This is a placeholder - in a real app, you would fetch districts based on city
            districtSelect.value = '';
        });
    }
    
    // Form validation for login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const phoneInput = document.getElementById('phone_number');
            const emailInput = document.getElementById('email');
            
            if (phoneInput && !isValidPhone(phoneInput.value)) {
                event.preventDefault();
                return false;
            }
            
            if (emailInput && !isValidEmail(emailInput.value)) {
                event.preventDefault();
                showError(emailInput, 'Vui lòng nhập địa chỉ email hợp lệ');
                return false;
            }
        });
    }
    
    // Create a default hero background if it doesn't exist
    const heroSection = document.querySelector('.hero-section');
    if (heroSection && !heroSection.style.backgroundImage) {
        heroSection.style = defaultHeroStyle;
    }
    
    // Handle filter toggle
    const filterHeader = document.querySelector('.filter-header');
    const filterOptions = document.getElementById('filterOptions');
    
    if (filterHeader && filterOptions) {
        filterHeader.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
                if (filterOptions.classList.contains('show')) {
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                } else {
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-up');
                }
            }
        });
    }
    
    // Xử lý nút đặt phòng
    const bookButtons = document.querySelectorAll('.btn-book:not(.disabled)');
    bookButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Đặt phòng thành công! Chúng tôi sẽ liên hệ với bạn sớm nhất có thể.');
        });
    });
    
    // Xử lý form liên hệ
    const contactForm = document.querySelector('.contact-form form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const phone = document.getElementById('phone');
            const subject = document.getElementById('subject');
            const message = document.getElementById('message');
            
            // Reset previous errors
            resetErrors();
            
            // Validate fields
            let isValid = true;
            
            if (!name.value.trim()) {
                showError(name, 'Vui lòng nhập họ tên');
                isValid = false;
            }
            
            if (!isValidEmail(email.value)) {
                showError(email, 'Vui lòng nhập email hợp lệ');
                isValid = false;
            }
            
            if (!isValidPhone(phone.value)) {
                showError(phone, 'Vui lòng nhập số điện thoại hợp lệ');
                isValid = false;
            }
            
            if (subject.value === 'Chọn chủ đề liên hệ') {
                showError(subject, 'Vui lòng chọn chủ đề');
                isValid = false;
            }
            
            if (!message.value.trim()) {
                showError(message, 'Vui lòng nhập nội dung');
                isValid = false;
            }
            
            if (isValid) {
                // Show success message
                showSuccessMessage(contactForm);
                // Reset form
                contactForm.reset();
            }
        });
    }
    
    // Utility functions
    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
    
    function isValidPhone(phone) {
        return /^[0-9]{10}$/.test(phone.replace(/[^0-9]/g, ''));
    }
    
    function showError(input, message) {
        const formGroup = input.closest('.mb-3');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        input.classList.add('is-invalid');
        
        // Remove existing error message if any
        const existingError = formGroup.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        
        formGroup.appendChild(errorDiv);
    }
    
    function resetErrors() {
        document.querySelectorAll('.is-invalid').forEach(input => {
            input.classList.remove('is-invalid');
        });
        document.querySelectorAll('.invalid-feedback').forEach(error => {
            error.remove();
        });
    }
    
    function showSuccessMessage(form) {
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success mt-3';
        successDiv.textContent = 'Cảm ơn bạn đã liên hệ. Chúng tôi sẽ phản hồi trong thời gian sớm nhất!';
        
        // Remove existing success message if any
        const existingSuccess = form.querySelector('.alert-success');
        if (existingSuccess) {
            existingSuccess.remove();
        }
        
        form.appendChild(successDiv);
        
        // Remove success message after 5 seconds
        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }
});