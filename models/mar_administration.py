from db import db
from models.base_model import BaseModel


class AdministrationModel(BaseModel):
    __tablename__ = "administrations"

    mar_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    administered_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    prescription = db.relationship("PrescriptionModel", back_populates="administrations", overlaps="prescriptions")
