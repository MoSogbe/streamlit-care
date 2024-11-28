from db import db
from models.base_model import BaseModel


class MITModel(BaseModel):
    __tablename__ = "mit"

    mit_name = db.Column(db.String(25), nullable=False)
