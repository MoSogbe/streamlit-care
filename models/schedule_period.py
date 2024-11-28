from db import db
from models.base_model import BaseModel


class SchedulePeriodModel(BaseModel):
    __tablename__ = "schedule_periods"

    start_time = db.Column(db.String(12), unique=False, nullable=False)
    end_time = db.Column(db.String(12), unique=False, nullable=False)
