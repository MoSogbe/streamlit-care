from db import db
from models.base_model import BaseModel


class ServiceCategoryModel(BaseModel):
    __tablename__ = "service_categories"

    category_name = db.Column(db.String(45), unique=True, nullable=False)
    service = db.relationship('ServiceModel', backref='service_categories', lazy=True)
