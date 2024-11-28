from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.user_types import UserTypeModel
from schemas import UserSchema,UserTypeSchema,UserTypeUpdateSchema
from datetime import datetime

blp = Blueprint("User Types", "user_types", description="Operations on User Types")


@blp.route("/user-type/<string:user_type_id>")
class UserType(MethodView):
    @jwt_required()
    @blp.response(200, UserTypeSchema)
    def get(self, user_type_id):
        user_type = UserTypeModel.query.get_or_404(user_type_id)
        return user_type
    @jwt_required()
    def delete(self, user_type_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            user_type = UserTypeModel.query.get_or_404(user_type_id)
            db.session.delete(user_type)
            db.session.commit()
            return {"message": "User Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the user types. {e}")
    @jwt_required()
    @blp.arguments(UserTypeUpdateSchema)
    @blp.response(200, UserTypeSchema)
    def put(self, user_type_data, user_type_id):
        user_type = UserTypeModel.query.get(user_type_id)

        if user_type:
            user_type.type_name = user_type_data["type_name"]
        else:
            user_type = UserTypeModel(id=user_type_id, **user_type_data)

        db.session.add(user_type)
        db.session.commit()

        return user_type


@blp.route("/user-type")
class UserTypeList(MethodView):
    @jwt_required()
    @blp.response(200, UserTypeSchema(many=True))
    def get(self):
        return UserTypeModel.query.all()
    @jwt_required()
    @blp.arguments(UserTypeSchema)
    @blp.response(201, UserTypeSchema)
    def post(self, user_type_data):
        if UserTypeModel.query.filter(
            or_
            (
             UserTypeModel.type_name==user_type_data["type_name"],
           
             )).first():
            abort(409, message="A User Type with that name already exist")
        user_type = UserTypeModel(
            type_name = user_type_data["type_name"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(user_type)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the user type.")

        return user_type
