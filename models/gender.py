from db import db
from models.base_model import BaseModel


class GenderModel(BaseModel):
    __tablename__ = "genders"

    name = db.Column(db.String(12), unique=True, nullable=False)
