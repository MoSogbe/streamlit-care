from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.mit import MITModel
from models.preferred_hospital import PHModel
from schemas import PreferredHospitalSchema
from datetime import datetime

blp = Blueprint("Preferred Hospital", "preferred_hospital", description="Operations on Preferred Hospital Model")


@blp.route("/preferred-hospital/<string:ph_id>")
class PHType(MethodView):
    @jwt_required()
    @blp.response(200, PreferredHospitalSchema)
    def get(self, ph_id):
        ph = PHModel.query.get_or_404(ph_id)
        return ph
    @jwt_required()
    def delete(self, ph_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            ph = PHModel.query.get_or_404(ph_id)
            db.session.delete(ph)
            db.session.commit()
            return {"message": "Preferred Hospital  Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the Preferred Hospital. {e}")
    
    
       
    @jwt_required()
    @blp.arguments(PreferredHospitalSchema)
    @blp.response(200, PreferredHospitalSchema)
    def put(self, ph_data, ph_id):
        ph = PHModel.query.get(ph_id)

        if ph:
            ph.ph_name = ph_data["ph_name"]
            ph.ph_address = ph_data["ph_address"]
           
        else:
            ph = PHModel(id=ph_id, **ph_data)

        db.session.add(ph)
        db.session.commit()

        return ph


@blp.route("/preferred-hospital/participant/<string:participant_id>")
class PHList(MethodView):
    @jwt_required()
    @blp.response(200, PreferredHospitalSchema(many=True))
    def get(self, participant_id):
        return PHModel.query.filter_by(participant_id=participant_id).all()
    
@blp.route("/preferred-hospital")
class PHList(MethodView):
    @jwt_required()
    @blp.arguments(PreferredHospitalSchema)
    @blp.response(201, PreferredHospitalSchema)
    def post(self, ph_data):
        ph = PHModel(
            ph_name = ph_data["ph_name"],
            ph_address = ph_data["ph_address"],
            participant_id = ph_data["participant_id"],
            created_by = get_jwt_identity(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(ph)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the Preferred Hospital {e}.")

        return ph
