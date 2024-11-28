from db import db
from models.base_model import BaseModel


class SupplierModel(BaseModel):
    __tablename__ = "supplier"

    supplier_name = db.Column(db.String(12), unique=True, nullable=False)
    supplier_phone = db.Column(db.String(12), unique=True)
    supplier_address = db.Column(db.String(155))
    supplier_contact_person = db.Column(db.String(120))
    supplier_balance = db.Column(db.String(12), default=0)
