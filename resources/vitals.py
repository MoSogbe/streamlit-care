from datetime import datetime

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models.vitals import VitalsModel
from schema.vitals import VitalsSchema

blp = Blueprint("Participant Vitals", "vitals", description="Operations on Participant Vitals")


@blp.route("/vitals/<string:participant_id>")
class VitalsGet(MethodView):
    @jwt_required()
    @blp.response(200, VitalsSchema(many=True))
    def get(self, participant_id):
        participant = VitalsModel.query.filter_by(participant_id=participant_id).all()
        return participant


@blp.route("/vitals/<string:vitals_id>")
class VitalsUpdate(MethodView):
    @jwt_required()
    def delete(self, vitals_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            participant_vitals = VitalsModel.query.get_or_404(vitals_id)
            db.session.delete(participant_vitals)
            db.session.commit()
            return {"message": "Participant vitals deleted."}
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while deleting the Participant vitals. {e}")

    @jwt_required()
    @blp.arguments(VitalsSchema)
    @blp.response(200, VitalsSchema)
    def put(self, vitals_data, vitals_id):
        vitals = VitalsModel.query.get(vitals_id)
        # Check if the instance exists
        if vitals is None:
            return {"error": "vitals not found"}, 404
        # Update the instance fields with participant_data
        for key, value in vitals_data.items():
            setattr(vitals, key, value)
        # Set the updated_at field to the current time
        vitals.updated_at = datetime.now()
        # Optionally update created_at if it's part of participant_data
        if 'created_at' in vitals_data:
            vitals.created_at = vitals_data['created_at']
        # Commit the changes to the database
        db.session.commit()
        return vitals


@blp.route("/vitals")
class VitalsPost(MethodView):
    @jwt_required()
    @blp.arguments(VitalsSchema)
    @blp.response(201, VitalsSchema)
    def post(self, vitals_data):

        # Create a PrescriptionModel instance
        vitals = VitalsModel(
            participant_id=vitals_data["participant_id"],
            blood_pressure=vitals_data["blood_pressure"],
            systolic=vitals_data["systolic"],
            diastolic=vitals_data["diastolic"],
            pulse=vitals_data["pulse"],
            glucose=vitals_data["glucose"],
            comment=vitals_data["comment"],
            created_by=get_jwt_identity(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        try:
            db.session.add(vitals)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the participant vitals .{e}.")
        return vitals
