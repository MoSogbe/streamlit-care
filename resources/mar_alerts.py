from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError

from helper.utils import get_time_window
from models import PrescriptionModel, CareGiverModel
from schemas import PrescriptionSchema

blp = Blueprint("MARAlerts", "mar_alerts", description="Alerts on MAR Administration")


@blp.route("/mar/alerts/caregiver")
class CareGiverAlerts(MethodView):
    @jwt_required()
    @blp.response(200, PrescriptionSchema(many=True))
    def get(self):
        """
        Get MARs for the Care Giver that were created within the last X minutes.

        Query Parameters:
        - minutes: int (default: 30)
        """
        user_id = get_jwt_identity()
        minutes = int(request.args.get('minutes', 30))
        start_time, end_time = get_time_window(minutes)

        try:
            mar_records = PrescriptionModel.query.join(
                CareGiverModel,
                PrescriptionModel.created_by == CareGiverModel.user_id
            ).filter(CareGiverModel.user_id == user_id).filter(
                PrescriptionModel.created_at >= start_time,
                PrescriptionModel.created_at <= end_time,
            ).all()

            if not mar_records:
                abort(404, message=f"No MAR records found for the last {minutes} minutes.")

            return mar_records
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving MAR records: {str(e)}")


@blp.route("/mar/alerts/administer")
class AdministerAlerts(MethodView):
    @jwt_required()
    @blp.response(200, PrescriptionSchema(many=True))
    def get(self):
        """
        Get MARs that were created within the last X minutes and have not been administered yet.

        Query Parameters:
        - minutes: int (default: 15)
        """
        minutes = int(request.args.get('minutes', 15))
        start_time, end_time = get_time_window(minutes)

        try:
            mar_records = PrescriptionModel.query.filter(
                PrescriptionModel.created_at >= start_time,
                PrescriptionModel.created_at <= end_time,
                PrescriptionModel.mar_date.is_(None)
            ).all()

            if not mar_records:
                abort(404, message=f"No MAR records found for the last {minutes} minutes.")

            return mar_records
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving MAR records: {str(e)}")
