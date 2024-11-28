from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.gender import GenderModel
from schemas import GenderSchema
from datetime import datetime

blp = Blueprint("Gender Model", "genders", description="Operations on Gender Model")


@blp.route("/gender/<string:gender_id>")
class GenderType(MethodView):
    @jwt_required()
    @blp.response(200, GenderSchema)
    def get(self, gender_id):
        gender = GenderModel.query.get_or_404(gender_id)
        return gender
    @jwt_required()
    def delete(self, gender_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            gender = GenderModel.query.get_or_404(gender_id)
            db.session.delete(gender)
            db.session.commit()
            return {"message": "Gender  Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the gender. {e}")
    
    
       
    @jwt_required()
    @blp.arguments(GenderSchema)
    @blp.response(200, GenderSchema)
    def put(self, gender_data, gender_id):
        gender = GenderModel.query.get(gender_id)

        if gender:
            gender.name = gender_data["name"]
        else:
            gender = GenderModel(id=gender_id, **gender_data)

        db.session.add(gender)
        db.session.commit()

        return gender


@blp.route("/gender")
class GenderList(MethodView):
    @jwt_required()
    @blp.response(200, GenderSchema(many=True))
    def get(self):
        return GenderModel.query.all()
    @jwt_required()
    @blp.arguments(GenderSchema)
    @blp.response(201, GenderSchema)
    def post(self, gender_data):
        if GenderModel.query.filter(
            or_
            (
             GenderModel.name==gender_data["name"],
           
             )).first():
            abort(409, message="A behavioral status with that name already exist")
        gender = GenderModel(
            name = gender_data["name"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(gender)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the gender {e}.")

        return gender
