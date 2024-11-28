from db import db
from models.base_model import BaseModel


class BTitleModel(BaseModel):
    __tablename__ = "bio_titles"

    bio_name = db.Column(db.String(12), unique=True, nullable=False)
