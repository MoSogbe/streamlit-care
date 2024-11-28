from db import db
from models.base_model import BaseModel


class MedActionModel(BaseModel):
    __tablename__ = "med_actions"

    mar_id = db.Column(db.Integer, db.ForeignKey("prescriptions.id"), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("med_action_statuses.id"), nullable=False)
    administered_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    prescription = db.relationship("PrescriptionModel", back_populates="med_actions")
    user = db.relationship("UserModel", back_populates="med_actions")
    status = db.relationship("MedActionStatusModel", back_populates="med_actions")
