from db import db
from models.location_base_model import LocationBaseModel
from models.base_model import BaseModel


class LocationModel(BaseModel):
    __tablename__ = "locations"
    location_name = db.Column(db.String(125), unique=True, nullable=False)
