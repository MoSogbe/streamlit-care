from db import db
from models.base_model import BaseModel


class MedicalInformationModel(BaseModel):
    __tablename__ = "medical_information"

    medical_condition_id = db.Column(db.Integer, db.ForeignKey('medical_conditions.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('ParticipantModel', backref='medical_information')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel', backref='medical_information')
    medical_condition = db.relationship('MedicalConditionModel', backref='medical_information')

    def serialize(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'medical_condition_id': self.medical_condition_id,
            'mi_name': self.medical_condition.condition_name,
            'created_by': self.created_by
        }
