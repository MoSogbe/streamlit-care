from db import db
from models.base_model import BaseModel


class PreBillingModel(BaseModel):
    __tablename__ = 'pre_billing'

    duration = db.Column(db.Integer, nullable=False, default=0)
    billing_status = db.Column(db.Integer, default=0, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=True)
    log_id = db.Column(db.Integer, db.ForeignKey('log_entries.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    user = db.relationship('UserModel', backref='pre_billing')
    service = db.relationship('ServiceModel', backref='pre_billing')
    log = db.relationship('LogEntryModel', backref='pre_billing')
    participant = db.relationship('ParticipantModel', backref='pre_billing')
