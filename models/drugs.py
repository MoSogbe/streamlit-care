from db import db
from models.base_model import BaseModel


class DrugModel(BaseModel):
    __tablename__ = "drugs"

    drug_name = db.Column(db.String(125), unique=True, nullable=False)
    generic_name = db.Column(db.String(125), nullable=False)
    brand_name = db.Column(db.String(125), nullable=False)
    uom_id = db.Column(db.Integer, db.ForeignKey('unit_of_measurements.id'), nullable=False)
    drug_category_id = db.Column(db.Integer, db.ForeignKey('drug_category.id'), nullable=False)

    uom = db.relationship('UoMModel', backref='drugs')
    drug_category = db.relationship('DrugCategoryModel', backref='drugs')
    med_errors = db.relationship('MedErrorModel', back_populates='drug', overlaps="drug,med_errors")

    def serialize(self):
        return {
            'id': self.id,
            'drug_category_id': self.drug_category_id,
            'uom_id': self.uom_id,
            'drug_name': self.drug_name,
            'brand_name': self.brand_name,
            'generic_name': self.generic_name
        }
