from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.drug_category import DrugCategoryModel
from schemas import DrugCategorySchema
from datetime import datetime

blp = Blueprint("Drug Category", "drug_category", description="Operations on Drug Category")


@blp.route("/drug-category/<string:drug_category_id>")
class DrugsCategoryType(MethodView):
    @jwt_required()
    @blp.response(200, DrugCategorySchema)
    def get(self, drug_category_id):
        bio_title = DrugCategoryModel.query.get_or_404(drug_category_id)
        return bio_title
    @jwt_required()
    def delete(self,drug_category_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            drug_category = DrugCategoryModel.query.get_or_404(drug_category_id)
            db.session.delete(drug_category)
            db.session.commit()
            return {"message": "Drug Category Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the drug category. {e}")
    
   
    @jwt_required()
    @blp.arguments(DrugCategorySchema)
    @blp.response(200, DrugCategorySchema)
    def put(self, drug_category_data, drug_category_id):
        drug_category = DrugCategoryModel.query.get(drug_category_id)

        if drug_category:
            drug_category.drug_category_name = drug_category_data["drug_category_name"]
        else:
            drug_category = DrugCategoryModel(id=drug_category_id, **drug_category_data)

        db.session.add(drug_category)
        db.session.commit()

        return drug_category


@blp.route("/drug-category")
class DrugsCategoryList(MethodView):
    @jwt_required()
    @blp.response(200, DrugCategorySchema(many=True))
    def get(self):
        return DrugCategoryModel.query.all()
    @jwt_required()
    @blp.arguments(DrugCategorySchema)
    @blp.response(201, DrugCategorySchema)
    def post(self, drug_category_data):
        if DrugCategoryModel.query.filter(
            or_
            (
             DrugCategoryModel.drug_category_name==drug_category_data["drug_category_name"],
           
             )).first():
            abort(409, message="A drug category with that name already exist")
        drug_category = DrugCategoryModel(
            drug_category_name = drug_category_data["drug_category_name"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(drug_category)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the Drug Category .{e}.")

        return drug_category
