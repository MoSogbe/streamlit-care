from db import db
from models.base_model import BaseModel

class MedErrorReasonModel(BaseModel):
    __tablename__ = "med_error_reasons"

    reason = db.Column(db.String(80), nullable=False)

    med_errors = db.relationship("MedErrorModel", back_populates="error_reason")
