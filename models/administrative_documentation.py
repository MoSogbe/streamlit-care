from db import db
from models.base_model import BaseModel


class AdministrativeDocumentationModel(BaseModel):
    __tablename__ = 'administrative_documentations'

    review_status = db.Column(db.Boolean, nullable=False, default=False)
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_types.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.String(255), nullable=True)

    document_type = db.relationship('DocumentTypeModel', backref='administrative_documentations')
    created_by_user = db.relationship('UserModel', backref='administrative_documentations')
