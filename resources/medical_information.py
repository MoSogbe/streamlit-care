from datetime import datetime

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import MITModel, MedicalConditionModel
from models.medical_information import MedicalInformationModel
from schemas import MISchema, MITSchema, MIViewSchema

blp = Blueprint("Medical Information Model", "genders", description="Operations on Medical Information Model")


@blp.route("/medical-information-types")
class MIType(MethodView):
    @jwt_required()
    @blp.response(200, MITSchema(many=True))
    def get(self):
        return MITModel.query.all()


@blp.route("/medical-information/<string:mi_id>")
class MedicalInformationType(MethodView):
    @jwt_required()
    @blp.response(200, MISchema)
    def get(self, mi_id):
        medical_information = MedicalInformationModel.query.get_or_404(mi_id)
        return medical_information

    @jwt_required()
    def delete(self, mi_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            medical_information = MedicalInformationModel.query.get_or_404(mi_id)
            db.session.delete(medical_information)
            db.session.commit()
            return {"message": "Medical Condition  Type deleted."}
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while deleting the Medical Condition. {e}")

    @jwt_required()
    @blp.arguments(MISchema)
    @blp.response(200, MISchema)
    def put(self, mi_data, mi_id):
        medical_information = MITModel.query.get(mi_id)

        if medical_information:
            medical_information.medication_condition_id = mi_data["medication_condition_id"]
        else:
            medical_information = MedicalInformationModel(id=mi_id, **mi_data)

        db.session.add(medical_information)
        db.session.commit()

        return medical_information


@blp.route("/medical-information/participant/<string:participant_id>")
class MedicalInformationList(MethodView):
    @jwt_required()
    @blp.response(200, MIViewSchema(many=True))
    def get(self, participant_id):
        return MedicalInformationModel.query.join(MedicalConditionModel,
                                                  MedicalInformationModel.medical_condition_id == MedicalConditionModel.id) \
            .with_entities(MedicalInformationModel.id, MedicalInformationModel.medical_condition_id,
                           MedicalConditionModel.condition_name) \
            .filter_by(participant_id=participant_id) \
            .all()


@blp.route("/medical-information")
class MedicalInformationPost(MethodView):
    @jwt_required()
    @blp.arguments(MISchema)
    @blp.response(201, MISchema)
    def post(self, mi_data):
        medical_information = MedicalInformationModel(
            medical_condition_id=mi_data["medical_condition_id"],
            participant_id=mi_data["participant_id"],
            created_by=get_jwt_identity(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        try:
            db.session.add(medical_information)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the Medical Information {e}.")

        return medical_information
