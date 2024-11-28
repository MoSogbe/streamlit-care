from db import db
from models.base_model import BaseModel


class AppointmentModel(BaseModel):
    __tablename__ = "appointments"

    doctor = db.Column(db.String(50), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_reason = db.Column(db.String(255), nullable=False)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    follow_up_details = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)

    participant = db.relationship('ParticipantModel', backref='appointments')
    user = db.relationship('UserModel', backref='appointments')

    def serialize(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'doctor':self.doctor,
            'appointment_date': self.appointment_date,
            'appointment_reason': self.appointment_reason,
            'follow_up_date' : self.follow_up_date,
            'follow_up_details': self.follow_up_details,
            'created_by':self.created_by
        }
