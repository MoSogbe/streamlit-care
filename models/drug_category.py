from db import db
from models.base_model import BaseModel


class DrugCategoryModel(BaseModel):
    __tablename__ = "drug_category"

    id = db.Column(db.Integer, primary_key=True)
    drug_category_name = db.Column(db.String(45), unique=True, nullable=False)
