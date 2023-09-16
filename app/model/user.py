from .db_setup import db
from flask_security import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.String(100), primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    
    def __init__(self, id, display_name, email):
        self.id = id
        self.display_name = display_name
        self.email = email
    
    def __repr__(self):
        return f'<User {self.display_name}>'
    
    def is_active(self):
        return True
    
    def get_id(self):   
        return self.id
    