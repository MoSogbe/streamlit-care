from db import db
from models.base_model import BaseModel


class MedicalConditionModel(BaseModel):
    __tablename__ = "medical_conditions"

    condition_name = db.Column(db.String(120), unique=True, nullable=False)
