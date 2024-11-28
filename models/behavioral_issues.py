from db import db
from models.base_model import BaseModel


class BIssuesModel(BaseModel):
    __tablename__ = "behavioral_issues"

    details = db.Column(db.String(255), unique=True, nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    participant = db.relationship('ParticipantModel', backref='behavioral_issues')
    user = db.relationship('UserModel', backref='behavioral_issues')

    def serialize(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'details': self.details,
            'created_by':self.created_by
        }
