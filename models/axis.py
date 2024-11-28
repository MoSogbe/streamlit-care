# models/axis.py
from db import db
from models.base_model import BaseModel


class AxisModel(BaseModel):
    __tablename__ = "axis"

    axis_type = db.Column(db.String(80), nullable=False)
