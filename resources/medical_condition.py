from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.medical_conditions import MedicalConditionModel
from schemas import MedicalConditionSchema
from datetime import datetime

blp = Blueprint("Medical Condition", "medical_conditions", description="Operations on Medical Conditions")


@blp.route("/medical-condition/<string:md_id>")
class UserType(MethodView):
    @jwt_required()
    @blp.response(200, MedicalConditionSchema)
    def get(self, md_id):
        medical_condition = MedicalConditionModel.query.get_or_404(md_id)
        return medical_condition
    @jwt_required()
    def delete(self, md_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            medical_condition = MedicalConditionModel.query.get_or_404(md_id)
            db.session.delete(medical_condition)
            db.session.commit()
            return {"message": "User Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the medical condition. {e}")
                
    @jwt_required()
    @blp.arguments(MedicalConditionSchema)
    @blp.response(200, MedicalConditionSchema)
    def put(self, medical_condition_data, md_id):
        medical_condition = MedicalConditionModel.query.get(md_id)

        if medical_condition:
            medical_condition.condition_name = medical_condition_data["condition_name"]
        else:
            medical_condition = MedicalConditionModel(id=md_id, **medical_condition_data)

        db.session.add(medical_condition)
        db.session.commit()

        return medical_condition


@blp.route("/medical-condition")
class UserTypeList(MethodView):
    @jwt_required()
    @blp.response(200, MedicalConditionSchema(many=True))
    def get(self):
        return MedicalConditionModel.query.all()
    @jwt_required()
    @blp.arguments(MedicalConditionSchema)
    @blp.response(201, MedicalConditionSchema)
    def post(self, medical_condition_data):
        if MedicalConditionModel.query.filter(
            or_
            (
             MedicalConditionModel.condition_name==medical_condition_data["condition_name"],
           
             )).first():
            abort(409, message="A condition name with that name already exist")
        medical_condition = MedicalConditionModel(
            condition_name = medical_condition_data["condition_name"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(medical_condition)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the behavioral-status {e}.")

        return medical_condition
