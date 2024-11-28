from db import db
from models.base_model import BaseModel


class VitalsModel(BaseModel):
    __tablename__ = "vitals"

    blood_pressure = db.Column(db.String(24))
    systolic = db.Column(db.String(24))
    diastolic = db.Column(db.String(145))
    pulse = db.Column(db.String(24))
    glucose = db.Column(db.String(24))
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('ParticipantModel', backref='vitals')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel', backref='vitals')
    comment = db.Column(db.String(225))
