from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr

from db import db


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @declared_attr
    def created_at(self):
        return Column(DateTime, nullable=False, default=datetime.now(timezone.utc))

    @declared_attr
    def updated_at(self):
        return Column(DateTime, nullable=False, default=datetime.now(timezone.utc),
                      onupdate=lambda: datetime.now(timezone.utc))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
