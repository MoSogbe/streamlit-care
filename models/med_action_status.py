from db import db
from models.base_model import BaseModel


class MedActionStatusModel(BaseModel):
    __tablename__ = "med_action_statuses"

    status_name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))
    med_actions = db.relationship("MedActionModel", back_populates="status")
