function toggleReviewForm() {
    const container = document.getElementById('reviewFormContainer');
    const button = document.querySelector('.review-toggle-btn');
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        button.innerHTML = '<i class="fas fa-times"></i> Đóng';
    } else {
        container.style.display = 'none';
        button.innerHTML = '<i class="fas fa-pen"></i> Viết đánh giá mới';
    }
} 