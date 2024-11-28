from db import db
from models.base_model import BaseModel


class ParticipantDocumentationModel(BaseModel):
    __tablename__ = "participant_documentations"

    review_status = db.Column(db.Boolean, nullable=False, default=False)
    participant_id = db.Column(db.Integer, db.ForeignKey('participants.id'), nullable=False)
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_types.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.String(255), nullable=True)

    participant = db.relationship('ParticipantModel', backref='participant_documentations')
    document_type = db.relationship('DocumentTypeModel', backref='participant_documentations')
    user = db.relationship('UserModel', backref='participant_documentations')

    def serialize(self):
        return {
            'id': self.id,
            'participant_id': self.participant_id,
            'document_type_id': self.document_type_id,
            'document_type': self.document_type.document_type,
            'file_path': self.file_path,
            'comment': self.comment,
            'review_status': self.review_status,
        }
