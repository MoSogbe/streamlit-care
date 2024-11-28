# resources/diagnosis.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required
from db import db
from models import DiagnosisModel, MedicalConditionModel, AxisModel
from schemas import DiagnosisSchema, DiagnosisViewSchema
from datetime import datetime

blp = Blueprint("Diagnosis Model", "diagnosis", description="Operations on Diagnosis Model")

@blp.route("/diagnosis/<string:diagnosis_id>")
class DiagnosisType(MethodView):
    @jwt_required()
    @blp.response(200, DiagnosisViewSchema)
    def get(self, diagnosis_id):
        diagnosis = db.session.query(
            DiagnosisModel.id,
            DiagnosisModel.participant_id,
            DiagnosisModel.medical_condition_id,
            MedicalConditionModel.condition_name,
            AxisModel.axis_type.label('axis_name')
        ).join(MedicalConditionModel, DiagnosisModel.medical_condition_id == MedicalConditionModel.id)\
         .join(AxisModel, DiagnosisModel.axis_id == AxisModel.id)\
         .filter(DiagnosisModel.id == diagnosis_id).first()

        if not diagnosis:
            abort(404, message="Diagnosis not found.")

        return diagnosis

    @jwt_required()
    def delete(self, diagnosis_id):
        try:
            diagnosis = DiagnosisModel.query.get_or_404(diagnosis_id)
            db.session.delete(diagnosis)
            db.session.commit()
            return {"message": "Diagnosis deleted."}
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while deleting the diagnosis: {e}")

    @jwt_required()
    @blp.arguments(DiagnosisSchema)
    @blp.response(200, DiagnosisSchema)
    def put(self, diagnosis_data, diagnosis_id):
        diagnosis = DiagnosisModel.query.get(diagnosis_id)

        if diagnosis:
            diagnosis.medical_condition_id = diagnosis_data["medical_condition_id"]
            diagnosis.axis_id = diagnosis_data["axis_id"]
        else:
            diagnosis = DiagnosisModel(id=diagnosis_id, **diagnosis_data)

        db.session.add(diagnosis)
        db.session.commit()

        return diagnosis

@blp.route("/diagnosis/participant/<string:participant_id>")
class DiagnosisGetUser(MethodView):
    @jwt_required()
    @blp.response(200, DiagnosisViewSchema(many=True))
    def get(self, participant_id):
        diagnoses = db.session.query(
            DiagnosisModel.id,
            DiagnosisModel.participant_id,
            DiagnosisModel.medical_condition_id,
            MedicalConditionModel.condition_name,
            AxisModel.axis_type.label('axis_name')
        ).join(MedicalConditionModel, DiagnosisModel.medical_condition_id == MedicalConditionModel.id)\
         .join(AxisModel, DiagnosisModel.axis_id == AxisModel.id)\
         .filter(DiagnosisModel.participant_id == participant_id).all()

        if not diagnoses:
            abort(404, message="No diagnoses found for the specified participant.")

        return diagnoses

@blp.route("/diagnosis")
class DiagnosisRoute(MethodView):
    @jwt_required()
    @blp.arguments(DiagnosisSchema)
    @blp.response(201, DiagnosisViewSchema)
    def post(self, diagnosis_data):
        diagnosis = DiagnosisModel(
            participant_id=diagnosis_data["participant_id"],
            medical_condition_id=diagnosis_data["medical_condition_id"],
            axis_id=diagnosis_data["axis_id"],
            created_by=get_jwt_identity(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        try:
            db.session.add(diagnosis)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the diagnosis: {e}")

        return diagnosis
