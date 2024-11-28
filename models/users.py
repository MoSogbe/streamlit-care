from db import db
from models.base_model import BaseModel


class UserModel(BaseModel):
    __tablename__ = "users"

    fullname = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_types.id'), nullable=False)
    user_type = db.relationship('UserTypeModel', backref='users')
    med_actions = db.relationship('MedActionModel', back_populates='user')
