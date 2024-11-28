from db import db
from models.base_model import BaseModel


class UoMModel(BaseModel):
    __tablename__ = "unit_of_measurements"

    unit_name = db.Column(db.String(45), unique=True, nullable=False)
    symbol = db.Column(db.String(11), unique=True, nullable=False)
