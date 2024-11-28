from db import db
from models.location_base_model import LocationBaseModel


class CareGiverModel(LocationBaseModel):
    __tablename__ = 'caregivers'

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    gender_id = db.Column(db.Integer, db.ForeignKey('genders.id'), nullable=False)
    bio_title_id = db.Column(db.Integer, db.ForeignKey('bio_titles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    gender = db.relationship('GenderModel', backref='caregivers', lazy=True, overlaps="gender,caregivers")
    bio_title = db.relationship('BTitleModel', backref='caregivers', lazy=True, overlaps="gender,caregivers")
    user = db.relationship('UserModel', backref='caregivers', lazy=True, overlaps="gender,caregivers")
