from db import db
from models.base_model import BaseModel

class SchedulingModel(BaseModel):
    __tablename__ = "scheduling"

    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    shift_period_id = db.Column(db.Integer, db.ForeignKey('schedule_periods.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    caregiver_id = db.Column(db.Integer, db.ForeignKey('caregivers.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    scheduled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location = db.relationship('LocationModel', backref='scheduling')
    shift_period = db.relationship('SchedulePeriodModel', backref='scheduling')
    patient = db.relationship('ParticipantModel', backref='scheduling')
    caregiver = db.relationship('CareGiverModel', backref='scheduling')
    created_by = db.relationship('UserModel', backref='scheduling')
    