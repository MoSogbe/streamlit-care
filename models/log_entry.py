from db import db
from models.base_model import BaseModel


class LogEntryModel(BaseModel):
    __tablename__ = "log_entries"

    check_in = db.Column(db.DateTime, nullable=False, default=db.func.now())
    check_out = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.String(255))
    location = db.Column(db.String(255),nullable=True)
    duration = db.Column(db.Integer, nullable=False, default=0)
    pre_billing_status = db.Column(db.Integer, default=0, nullable=False)

    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('UserModel', backref='log_entries')
    service = db.relationship('ServiceModel', back_populates='log_entries')
    participant = db.relationship('ParticipantModel', backref='log_entries')
