from db import db
from models.base_model import BaseModel


class BillingModel(BaseModel):
    __tablename__ = 'billing'

    amount = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    pre_billing_id = db.Column(db.Integer, db.ForeignKey('pre_billing.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('UserModel', backref='billing')
    service = db.relationship('ServiceModel', backref='billing')
    pre_billing = db.relationship('PreBillingModel', backref='billing')
    participant = db.relationship('ParticipantModel', backref='billing')
