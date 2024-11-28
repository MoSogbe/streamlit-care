from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models import DrugModel,StockTotalModel
from schemas import DrugSchema, StockTotalSchema
from datetime import datetime

blp = Blueprint("Drugs", "drugs", description="Operations on Drugs")


@blp.route("/drug/<string:drug_id>")
class DrugsType(MethodView):
    @jwt_required()
    @blp.response(200, DrugSchema)
    def get(self, drug_id):
        drug = DrugModel.query.get_or_404(drug_id)
        return drug
    @jwt_required()
    def delete(self,drug_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            drug = DrugModel.query.get_or_404(drug_id)
            db.session.delete(drug)
            db.session.commit()
            return {"message": "Drug Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the drug. {e}")


    @jwt_required()
    @blp.arguments(DrugSchema)
    @blp.response(200, DrugSchema)
    def put(self, drug_data, drug_id):
        drug = DrugModel.query.get(drug_id)

        if drug:
            drug.drug_name = drug_data["drug_name"]
            drug.generic_name = drug_data["generic_name"]
            drug.brand_name = drug_data["brand_name"]
            drug.uom_id = drug_data["uom_id"]
            drug.drug_category_id = drug_data["drug_category_id"]
        else:
            drug = DrugModel(id=drug_id, **drug_data)

        db.session.add(drug)
        db.session.commit()

        return drug


@blp.route("/drug")
class DrugList(MethodView):
    @jwt_required()
    @blp.response(200, DrugSchema(many=True))
    def get(self):
        return DrugModel.query.all()
    @jwt_required()
    @blp.arguments(DrugSchema)
    @blp.response(201, DrugSchema)
    def post(self, drug_data):
        if DrugModel.query.filter(
            or_
            (
             DrugModel.drug_name==drug_data["drug_name"],

             )).first():
            abort(409, message="A drug with that name already exist")
        drug = DrugModel(
            drug_name = drug_data["drug_name"],
            generic_name = drug_data["generic_name"],
            brand_name = drug_data["brand_name"],
            uom_id = drug_data["uom_id"],
            drug_category_id = drug_data["drug_category_id"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(drug)
            db.session.commit()
            # If drug insert is successful, insert into StockTotal
            stock_total = StockTotalModel(
                total_qty="0",
                drug_id=drug.id,
                created_at = datetime.now(),
                updated_at = datetime.now()
            )
            db.session.add(stock_total)
            db.session.commit()  # Commit the stock total insert
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the Drug.{e}.")

        return drug
