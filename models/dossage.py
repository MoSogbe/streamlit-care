from db import db
from models.base_model import BaseModel

class DosageModel(BaseModel):
    __tablename__ = 'dosages'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    dosage = db.Column(db.String(125), nullable=False)
    time = db.Column(db.String(50), nullable=False)

