from datetime import datetime

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from db import db
from helper.utils import get_participant_or_404
from models import BillingReportModel, PreBillingModel, ServiceModel
from schema.billing_summary import BillingReportSchema, BillingReportResponseSchema

blp = Blueprint("BillingReport", "billing_report", description="Operations on Billing Reports")


@blp.route("/billing-report/participant/<int:participant_id>")
class CreateBillingReport(MethodView):

    @jwt_required()
    @blp.arguments(BillingReportSchema, location="json")
    @blp.response(201, BillingReportResponseSchema(many=True))
    def post(self, date_range_data, participant_id):
        user_id = get_jwt_identity()
        get_participant_or_404(participant_id)

        from_date_str = date_range_data.get('from_date')
        to_date_str = date_range_data.get('to_date')

        if not from_date_str or not to_date_str:
            abort(400, message="Both 'from_date' and 'to_date' are required.")

        try:
            if isinstance(from_date_str, str):
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            else:
                from_date = from_date_str

            if isinstance(to_date_str, str):
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
            else:
                to_date = to_date_str
        except ValueError:
            abort(400, message="Dates must be in the format YYYY-MM-DD.")

        services = db.session.query(
            ServiceModel.id,
            ServiceModel.service_price,
            ServiceModel.service_charge_duration
        ).join(PreBillingModel, ServiceModel.id == PreBillingModel.service_id).filter(
            PreBillingModel.participant_id == participant_id,
            PreBillingModel.created_at >= from_date,
            PreBillingModel.created_at <= to_date
        ).distinct().all()

        if not services:
            abort(404, message="No services found for this participant in the specified time frame.")

        created_billing_reports = []

        try:
            for service in services:
                service_id = service.id
                service_price = float(service.service_price)
                service_charge_duration = int(service.service_charge_duration)

                total_duration = db.session.query(
                    func.sum(PreBillingModel.duration)
                ).filter(
                    PreBillingModel.participant_id == participant_id,
                    PreBillingModel.service_id == service_id,
                    PreBillingModel.created_at >= from_date,
                    PreBillingModel.created_at <= to_date
                ).scalar() or 0

                chargeable_units = float(total_duration) / service_charge_duration
                total_cost = service_price * chargeable_units

                existing_billing = BillingReportModel.query.filter_by(
                    participant_id=participant_id,
                    service_id=service_id,
                    created_by=user_id
                ).first()

                if existing_billing:
                    created_billing_reports.append(existing_billing)
                    continue

                billing = BillingReportModel(
                    total_cost=total_cost,
                    total_duration=total_duration,
                    service_id=service_id,
                    participant_id=participant_id,
                    created_by=user_id,
                )

                db.session.add(billing)
                created_billing_reports.append(billing)

            db.session.commit()

            return created_billing_reports, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating billing summary: {str(e)}")


@blp.route("/billing-report/all")
class GetAllBillingReports(MethodView):

    @jwt_required()
    @blp.arguments(BillingReportSchema, location="query")
    @blp.response(200, BillingReportResponseSchema(many=True))
    def get(self, date_range_data):
        from_date_str = date_range_data.get('from_date')
        to_date_str = date_range_data.get('to_date')
        participant_id = date_range_data.get('participant_id')

        if not from_date_str or not to_date_str:
            abort(400, message="Both 'from_date' and 'to_date' are required.")

        try:
            if isinstance(from_date_str, str):
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            else:
                from_date = from_date_str

            if isinstance(to_date_str, str):
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
            else:
                to_date = to_date_str
        except ValueError:
            abort(400, message="Dates must be in the format YYYY-MM-DD.")

        query = db.session.query(BillingReportModel)

        if participant_id:
            query = query.filter(BillingReportModel.participant_id == participant_id)

        query = query.filter(
            BillingReportModel.created_at >= from_date,
            BillingReportModel.created_at <= to_date
        )

        billing_reports = query.all()

        if not billing_reports:
            abort(404, message="No billing reports found for the specified time frame and participant(s).")

        return billing_reports
