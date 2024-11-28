from db import db
from models.base_model import BaseModel


class StockTotalModel(BaseModel):
    __tablename__ = "stock_total"

    total_qty = db.Column(db.String(125), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    drug = db.relationship('DrugModel', backref='stock_total')

    def serialize(self):
        return {
            'id': self.id,
            'drug_id': self.drug_id,
            'total_qty': self.total_qty
        }
