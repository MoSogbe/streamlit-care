from db import db
from models.location_base_model import LocationBaseModel


class CompanyModel(LocationBaseModel):
    __tablename__ = "companies"

    suite_unit = db.Column(db.String(100), nullable=True)
    name_of_company = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(45), unique=True, nullable=False)
    logo_path = db.Column(db.String(255), nullable=True)
