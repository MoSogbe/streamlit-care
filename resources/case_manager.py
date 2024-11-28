from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.mit import MITModel
from models.case_manager import CaseManagerModel
from schemas import CaseManagerSchema
from datetime import datetime

blp = Blueprint("Case Manager", "case_manager", description="Operations on Case Manager Model")


@blp.route("/case-manager/<string:case_manager_id>")
class CaseManagerType(MethodView):
    @jwt_required()
    @blp.response(200, CaseManagerSchema)
    def get(self, case_manager_id):
        case_manager = CaseManagerModel.query.get_or_404(case_manager_id)
        return case_manager
    @jwt_required()
    def delete(self, case_manager_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            case_manager = CaseManagerModel.query.get_or_404(case_manager_id)
            db.session.delete(case_manager)
            db.session.commit()
            return {"message": "Case Manager  Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the Case Manager. {e}")
    
    
       
    @jwt_required()
    @blp.arguments(CaseManagerSchema)
    @blp.response(200, CaseManagerSchema)
    def put(self, case_manager_data, case_manager_id):
        case_manager = CaseManagerModel.query.get(case_manager_id)

        if case_manager:
            case_manager.cm_name = case_manager_data["cm_name"]
            case_manager.cm_phone = case_manager_data["cm_phone"]
            case_manager.cm_emergency_phone = case_manager_data["cm_emergency_phone"]
            case_manager.cm_address = case_manager_data["cm_address"]
            case_manager.cm_fax = case_manager_data["cm_fax"]
            case_manager.cm_email_address = case_manager_data["cm_email_address"]
            case_manager.participant_id = case_manager_data["participant_id"]
           
        else:
            case_manager = CaseManagerModel(id=case_manager_id, **case_manager_data)

        db.session.add(case_manager)
        db.session.commit()

        return case_manager


@blp.route("/case-manager/participant/<string:participant_id>")
class CaseManagerGet(MethodView):
    @jwt_required()
    @blp.response(200, CaseManagerSchema(many=True))
    def get(self,participant_id):
        return CaseManagerModel.query.filter_by(participant_id=participant_id).all()
    
@blp.route("/case-manager")
class CaseManagerList(MethodView):
    @jwt_required()
    @blp.arguments(CaseManagerSchema)
    @blp.response(201, CaseManagerSchema)
    def post(self, case_manager_data):
        case_manager = CaseManagerModel(
            cm_name = case_manager_data["cm_name"],
            cm_phone = case_manager_data["cm_phone"],
            cm_emergency_phone = case_manager_data["cm_emergency_phone"],
            cm_address = case_manager_data["cm_address"],
            cm_fax = case_manager_data["cm_fax"],
            cm_email_address = case_manager_data["cm_email_address"],
            participant_id = case_manager_data["participant_id"],
            created_by = get_jwt_identity(),
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(case_manager)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting Case Manager {e}.")

        return case_manager
