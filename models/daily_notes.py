from db import db
from models.base_model import BaseModel


class DailyNotesModel(BaseModel):
    __tablename__ = "daily_notes"

    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('ParticipantModel', backref='daily_notes')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel', foreign_keys=[created_by], backref='created_notes')
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewer = db.relationship('UserModel', foreign_keys=[reviewed_by], backref='reviewed_notes')
    comment = db.Column(db.String(425), nullable=True)
