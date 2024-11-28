from db import db
from models.base_model import BaseModel


class BatchNumModel(BaseModel):
    __tablename__ = "batch_num_records"

    batch_num = db.Column(db.String(125), nullable=False)
    drug_id = db.Column(db.Integer, db.ForeignKey('drugs.id'), nullable=False)
    drug = db.relationship('DrugModel', backref='batch_num_records')

    def serialize(self):
        return {
            'id': self.id,
            'drug_id': self.drug_id,
            'batch_num': self.batch_num
        }
