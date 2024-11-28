from db import db
from models.location_base_model import LocationBaseModel


class ParticipantModel(LocationBaseModel):
    __tablename__ = 'participants'

    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(120), nullable=False)
    ssn = db.Column(db.String(15), nullable=False)
    maid_number = db.Column(db.String(255), nullable=False)
    legal_status = db.Column(db.String(100))
    home_phone = db.Column(db.String(100))
    profile_image = db.Column(db.String(255), nullable=True)
    gender_id = db.Column(db.Integer, db.ForeignKey('genders.id'), nullable=False)
    bio_title_id = db.Column(db.Integer, db.ForeignKey('bio_titles.id'), nullable=False)

    gender = db.relationship('GenderModel', backref='participants', lazy=True, overlaps="gender,participants")
    bio_title = db.relationship('BTitleModel', backref='participants', lazy=True, overlaps="gender,participants")
    med_errors = db.relationship("MedErrorModel", back_populates="participant")
