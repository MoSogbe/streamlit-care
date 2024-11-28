from db import db
from models.base_model import BaseModel


class LifeStoryModel(BaseModel):
    __tablename__ = "life_stories"

    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    participant = db.relationship('ParticipantModel', backref='life_stories')
    creator = db.relationship('UserModel', backref='life_stories')
