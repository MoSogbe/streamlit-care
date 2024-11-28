from db import db
from models.base_model import BaseModel


class ParticipantServiceProviderHistoryModel(BaseModel):
    __tablename__ = "participant_service_provider_history"

    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    participant = db.relationship('ParticipantModel', backref='participant_service_provider_history')
    service_type_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    provider_name = db.Column(db.String(55), nullable=False)
    provider_address = db.Column(db.String(155), nullable=False)
    provider_phone = db.Column(db.String(155), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_type = db.relationship('ServiceModel', backref='participant_service_provider_history')
    user = db.relationship('UserModel', backref='participant_service_provider_history')

    def serialize(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'service_type_id': self.service_type_id,
            'provider_name': self.provider_name,
            'provider_address': self.provider_address,
            'provider_phone': self.provider_phone,
            'created_by': self.created_by
        }
