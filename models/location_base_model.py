from models.base_model import BaseModel
from db import db


class LocationBaseModel(BaseModel):
    __abstract__ = True

    address = db.Column(db.String(255), nullable=True)
    address_2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    zip_code = db.Column(db.String(45), nullable=True)
