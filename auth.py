from flask_login import UserMixin

class UserLogin(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['phone_number']
        self.phone_number = user_data['phone_number']
        self.email = user_data['email'] 
        