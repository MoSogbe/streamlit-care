from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.mit import MITModel
from models.eci import ECIModel
from schemas import ECISchema
from datetime import datetime

blp = Blueprint("Emergency Contact Information", "eci", description="Operations on Emergency Contact Information Model")


@blp.route("/emergency-contact-information/<string:eci_id>")
class ECIType(MethodView):
    @jwt_required()
    @blp.response(200, ECISchema)
    def get(self, eci_id):
        eci = ECIModel.query.get_or_404(eci_id)
        return eci
    @jwt_required()
    def delete(self, eci_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            eci = ECIModel.query.get_or_404(eci_id)
            db.session.delete(eci)
            db.session.commit()
            return {"message": "ECI  Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the ECI. {e}")
    
    
       
    @jwt_required()
    @blp.arguments(ECISchema)
    @blp.response(200, ECISchema)
    def put(self, eci_data, eci_id):
        eci = ECIModel.query.get(eci_id)

        if eci:
            eci.gaurdian_name = eci_data["gaurdian_name"]
            eci.gaurdian_phone = eci_data["gaurdian_phone"]
            eci.gaurdian_address = eci_data["gaurdian_address"]
            eci.participant_id = eci_data["participant_id"]
           
        else:
            eci = ECIModel(id=eci_id, **eci_data)

        db.session.add(eci)
        db.session.commit()

        return eci


@blp.route("/emergency-contact-information/participant/<string:participant_id>")
class ECIList(MethodView):
    @jwt_required()
    @blp.response(200, ECISchema(many=True))
    def get(self,participant_id):
        return ECIModel.query.filter_by(participant_id=participant_id).all()
    
@blp.route("/emergency-contact-information")
class ECIPost(MethodView):
    @jwt_required()
    @blp.arguments(ECISchema)
    @blp.response(201, ECISchema)
    def post(self, eci_data):
        eci = ECIModel(
            gaurdian_name = eci_data["gaurdian_name"],
            gaurdian_phone = eci_data["gaurdian_phone"],
            gaurdian_address = eci_data["gaurdian_address"],
            participant_id = eci_data["participant_id"],
            created_by = get_jwt_identity(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(eci)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the ECI {e}.")

        return eci
