# models/category.py
from app import db

class Category(db.Model):
    __tablename__ = 'category'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    # relation vers Resource
    resources = db.relationship('Resource', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'
