from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.locations import LocationModel
from schemas import LocationSchema,LocationUpdateSchema
from datetime import datetime

blp = Blueprint("Locations", "locations", description="Operations on Locations")


@blp.route("/locations/<string:location_id>")
class Location(MethodView):
    @jwt_required()
    @blp.response(200, LocationSchema)
    def get(self, location_id):
        location = LocationModel.query.get_or_404(location_id)
        return location
    @jwt_required()
    def delete(self, location_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            location = LocationModel.query.get_or_404(location_id)
            db.session.delete(location)
            db.session.commit()
            return {"message": "location  deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the location. {e}")
    @jwt_required()
    @blp.arguments(LocationUpdateSchema)
    @blp.response(200, LocationSchema)
    def put(self, location_data, location_id):
        location = LocationModel.query.get(location_id)

        if location:
            location.location_name = location_data["location_name"]
        else:
            location = LocationModel(id=location_id, **location_data)

        db.session.add(location)
        db.session.commit()

        return location


@blp.route("/location")
class UserTypeList(MethodView):
    @jwt_required()
    @blp.response(200, LocationSchema(many=True))
    def get(self):
        return LocationModel.query.all()
    @jwt_required()
    @blp.arguments(LocationSchema)
    @blp.response(201, LocationSchema)
    def post(self, location_data):
        if LocationModel.query.filter(
            or_
            (
             LocationModel.location_name==location_data["location_name"],
           
             )).first():
            abort(409, message="A Location with that name already exist")
        location = LocationModel(
            location_name = location_data["location_name"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(location)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the Location.")

        return location
