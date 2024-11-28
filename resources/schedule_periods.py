from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.schedule_period import SchedulePeriodModel
from schemas import SchedulePeriodSchema,SchedulePeriodUpdateSchema
from datetime import datetime

blp = Blueprint("Shift Period", "schedule_periods", description="Operations on Shift Period")


@blp.route("/shift-period/<string:sp_id>")
class Location(MethodView):
    @jwt_required()
    @blp.response(200, SchedulePeriodSchema)
    def get(self, sp_id):
        sp = SchedulePeriodModel.query.get_or_404(sp_id)
        return sp
    @jwt_required()
    def delete(self, sp_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            sp = SchedulePeriodModel.query.get_or_404(sp_id)
            db.session.delete(sp)
            db.session.commit()
            return {"message": "schedule period  deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the schedule period. {e}")
    @jwt_required()
    @blp.arguments(SchedulePeriodUpdateSchema)
    @blp.response(200, SchedulePeriodSchema)
    def put(self, sp_data, sp_id):
        sp = SchedulePeriodModel.query.get(sp_id)

        if sp:
            sp.start_time = sp_data["start_time"],
            sp.end_time = sp_data["end_time"]
        else:
            sp = SchedulePeriodModel(id=sp_id, **sp_data)

        db.session.add(sp)
        db.session.commit()

        return sp


@blp.route("/shift-period")
class UserTypeList(MethodView):
    @jwt_required()
    @blp.response(200, SchedulePeriodSchema(many=True))
    def get(self):
        return SchedulePeriodModel.query.all()
    @jwt_required()
    @blp.arguments(SchedulePeriodSchema)
    @blp.response(201, SchedulePeriodSchema)
    def post(self, location_data):
        
        sp = SchedulePeriodModel(
            start_time = location_data["start_time"],
            end_time = location_data["end_time"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(sp)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the Location.")

        return sp
