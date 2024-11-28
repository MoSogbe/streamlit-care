# resources/med_action_status.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from models.med_action_status import MedActionStatusModel
from schema.med_action_status import MedActionStatusSchema
from db import db

blp = Blueprint("MedActionStatuses", "med_action_statuses", description="Operations on Medication Action Statuses")

@blp.route("/med-action-statuses")
class MedActionStatusList(MethodView):
    @blp.response(200, MedActionStatusSchema(many=True))
    def get(self):
        try:
            statuses = MedActionStatusModel.query.all()
            return statuses
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving medication action statuses: {str(e)}")
