from db import db
from models.base_model import BaseModel


class StockModel(BaseModel):
    __tablename__ = "stock"

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    transaction_code = db.Column(db.String(125))
    batch_code = db.Column(db.String(125), nullable=False)
    quantity_received = db.Column(db.String(12), nullable=False)
    expiry_date = db.Column(db.DateTime(), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    drug = db.relationship('DrugModel', backref='stock')
    supplier = db.relationship('SupplierModel', backref='stock')

    def serialize(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'transaction_code': self.transaction_code,
            'batch_code': self.batch_code,
            'quantity_received': self.quantity_received,
            'expiry_date': self.expiry_date
        }
