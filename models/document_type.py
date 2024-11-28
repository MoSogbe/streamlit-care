from db import db
from models.base_model import BaseModel

class DocumentTypeModel(BaseModel):
    __tablename__ = 'document_types'

    document_type = db.Column(db.String(100), nullable=False)
