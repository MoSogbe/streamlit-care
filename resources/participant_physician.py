from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.mit import MITModel
from models.participant_physician import PPModel
from schemas import ParticipantsPhysicianSchema
from datetime import datetime

blp = Blueprint("Participant Pysician", "participant_physician", description="Operations on Participant Pysician Model")


@blp.route("/participant-physician/<string:pp_id>")
class PHType(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantsPhysicianSchema)
    def get(self, pp_id):
        pp = PPModel.query.get_or_404(pp_id)
        return pp
    @jwt_required()
    def delete(self, pp_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            pp = PPModel.query.get_or_404(pp_id)
            db.session.delete(pp)
            db.session.commit()
            return {"message": "Preferred Pysician  Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the Participant Pysician. {e}")
    
    
       
    @jwt_required()
    @blp.arguments(ParticipantsPhysicianSchema)
    @blp.response(200, ParticipantsPhysicianSchema)
    def put(self, pp_data, pp_id):
        pp = PPModel.query.get(pp_id)

        if pp:
            pp.physician_name = pp_data["physician_name"]
            pp.physician_address = pp_data["physician_address"]
            pp.physician_phone = pp_data["physician"]
           
        else:
            pp = PPModel(id=pp_id, **pp_data)

        db.session.add(pp)
        db.session.commit()

        return pp


@blp.route("/participant-physician/participant/<string:participant_id>")
class PHList(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantsPhysicianSchema(many=True))
    def get(self, participant_id):
        return PPModel.query.filter_by(participant_id=participant_id).all()
    
@blp.route("/participant-physician")
class PHPost(MethodView):
    @jwt_required()
    @blp.arguments(ParticipantsPhysicianSchema)
    @blp.response(201, ParticipantsPhysicianSchema)
    def post(self, ph_data):
        pp = PPModel(
            physician_name = ph_data["physician_name"],
            physician_address = ph_data["physician_address"],
            physician_phone = ph_data["physician_phone"],
            participant_id = ph_data["participant_id"],
            created_by = get_jwt_identity(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(pp)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the Participant Pysician {e}.")

        return pp
