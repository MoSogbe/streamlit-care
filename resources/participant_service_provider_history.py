from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.participant_service_provider_history import ParticipantServiceProviderHistoryModel
from schemas import ParticipantServiceProviderHistorySchema
from datetime import datetime

blp = Blueprint("Participant Service Provider History Model", "participant_service_history", description="Operations on Participant Service Model")


@blp.route("/participant-service-provider-history/<string:psph_id>")
class PSHType(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantServiceProviderHistorySchema)
    def get(self, psph_id):
        psh = ParticipantServiceProviderHistoryModel.query.get_or_404(psph_id)
        return psh
    @jwt_required()
    def delete(self, psph_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            psh = ParticipantServiceProviderHistoryModel.query.get_or_404(psph_id)
            db.session.delete(psh)
            db.session.commit()
            return {"message": "Participant Service Provider History  Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the Participant Service Provider History. {e}")
    
    
       
    @jwt_required()
    @blp.arguments(ParticipantServiceProviderHistorySchema)
    @blp.response(200, ParticipantServiceProviderHistorySchema)
    def put(self, psh_data, psph_id):
        psh = ParticipantServiceProviderHistoryModel.query.get(psph_id)

        if psh:
            psh.service_type_id = psh_data["service_type_id"]
            psh.participant_id = psh_data["participant_id"]
            psh.provider_name = psh_data["provider_name"]
            psh.provider_address = psh_data["provider_address"]
            psh.provider_phone = psh_data["provider_phone"]
            psh.created_by = get_jwt_identity()
        else:
            psh = ParticipantServiceProviderHistoryModel(id=psph_id, **psh_data)

        db.session.add(psh)
        db.session.commit()

        return psh


@blp.route("/participant-service-provider-history/participant/<string:participant_id>")
class PSPHParticipant(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantServiceProviderHistorySchema(many=True))
    def get(self, participant_id):
        return ParticipantServiceProviderHistoryModel.query.filter_by(participant_id=participant_id).all()

@blp.route("/participant-service-provider-history")
class PSPHList(MethodView):
    @jwt_required()
    @blp.arguments(ParticipantServiceProviderHistorySchema)
    @blp.response(201, ParticipantServiceProviderHistorySchema)
    def post(self, psh_data):
        if ParticipantServiceProviderHistoryModel.query.filter(
            or_
            (
             ParticipantServiceProviderHistoryModel.provider_name==psh_data["provider_name"],
           
             )).first():
            abort(409, message="A Participant Service Provider with that name already exist")
        psh = ParticipantServiceProviderHistoryModel(
            service_type_id = psh_data["service_type_id"],
            participant_id = psh_data["participant_id"],
            provider_name = psh_data["provider_name"],
            provider_address = psh_data["provider_address"],
            provider_phone = psh_data["provider_phone"],
            created_by = get_jwt_identity(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(psh)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the Participant Service Provider {e}.")

        return psh
