from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.unit_of_measurement import UoMModel
from schemas import UoMSchema
from datetime import datetime

blp = Blueprint("Unit of Measurement", "unit_of_measurements", description="Operations on Unit of Measurement")


@blp.route("/uom/<string:uom_id>")
class UoMType(MethodView):
    @jwt_required()
    @blp.response(200, UoMSchema)
    def get(self, uom_id):
        uom = UoMModel.query.get_or_404(uom_id)
        return uom
    @jwt_required()
    def delete(self, uom_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            uom = UoMModel.query.get_or_404(uom_id)
            db.session.delete(uom)
            db.session.commit()
            return {"message": "UOM Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the uom. {e}")
                
    @jwt_required()
    @blp.arguments(UoMSchema)
    @blp.response(200, UoMSchema)
    def put(self, uom_data, uom_id):
        uom = UoMModel.query.get(uom_id)
        if uom:
            uom.unit_name = uom_data["unit_name"],
            uom.symbol = uom_data["symbol"]
        else:
            uom = UoMModel(id=uom_id, **uom_data)
        try:
            db.session.add(uom)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while updating the uom.{e}")
        return uom


@blp.route("/uom")
class UoMList(MethodView):
    @jwt_required()
    @blp.response(200, UoMSchema(many=True))
    def get(self):
        return UoMModel.query.all()
    @jwt_required()
    @blp.arguments(UoMSchema)
    @blp.response(201, UoMSchema)
    def post(self, uom_data):
        if UoMModel.query.filter(
            or_
            (
             UoMModel.unit_name==uom_data["unit_name"]
           
             )).first():
            abort(409, message="A unit name with that name already exist")
        uom = UoMModel(
            unit_name = uom_data["unit_name"],
            symbol = uom_data["symbol"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(uom)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the uom type.{e}")

        return uom
