# defines user class to manage user auth and session handling
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, username, access):
        self.id = user_id
        self.username = username
        self.access = access
