from db import db
from models.base_model import BaseModel


class ServiceModel(BaseModel):
    __tablename__ = "services"

    service_category = db.Column(db.Integer, db.ForeignKey('service_categories.id'), nullable=False)
    service_name = db.Column(db.String(120), unique=True, nullable=False)
    service_price = db.Column(db.String(80), unique=False, nullable=False)
    service_charge_duration = db.Column(db.String(45), unique=False, nullable=False)
    service_charge_frequency = db.Column(db.String(45), unique=False, nullable=False)

    log_entries = db.relationship('LogEntryModel', back_populates='service')
