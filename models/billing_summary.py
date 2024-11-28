from db import db
from models.base_model import BaseModel


class BillingReportModel(BaseModel):
    __tablename__ = 'billing_summary'

    total_cost = db.Column(db.Float, nullable=False)
    total_duration = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('UserModel', backref='billing_summary')
    service = db.relationship('ServiceModel', backref='billing_summary')
    participant = db.relationship('ParticipantModel', backref='billing_summary')
