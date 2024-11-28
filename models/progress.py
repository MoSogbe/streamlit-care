from db import db
from models.base_model import BaseModel


class PProgressModel(BaseModel):
    __tablename__ = "participant_progress"

    details = db.Column(db.String(255), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    participant = db.relationship('ParticipantModel', backref='progress')
    user = db.relationship('UserModel', backref='progress')

    def serialize(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'details': self.details,
            'created_by':self.created_by
        }
