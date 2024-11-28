from db import db
from models.base_model import BaseModel


class UserTypeModel(BaseModel):
    __tablename__ = "user_types"

    type_name = db.Column(db.String(20), unique=True, nullable=False)
