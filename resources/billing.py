from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint
from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from helper.utils import get_participant_or_404, calculate_billing_amount
from models import BillingModel, PreBillingModel, ServiceModel
from schema.billing import BillingSchema, CreateBillingSchema

blp = Blueprint("Billing", "billing", description="Operations for billing")


@blp.route("/billing/participant/<int:participant_id>")
class CreateBilling(MethodView):
    @jwt_required()
    @blp.arguments(CreateBillingSchema)
    def post(self, billing_data, participant_id):
        get_participant_or_404(participant_id)
        user_id = get_jwt_identity()
        pre_billing_id = billing_data.get('pre_billing_id')

        billing = BillingModel.query.filter_by(
            pre_billing_id=pre_billing_id,
            participant_id=participant_id
        ).first()

        if billing:
            billing.billing_status = 1
            db.session.add(billing)
            abort(400, message="Billing already exists for the given pre-billing ID.")

        pre_billing = PreBillingModel.query.get(pre_billing_id)
        if not pre_billing:
            abort(404, message="Pre billing item not found.")

        service = ServiceModel.query.get(pre_billing.service_id)
        if not service:
            abort(404, message="Service not found.")

        try:
            service_price = float(service.service_price)
            service_charge_duration = int(service.service_charge_duration)
            amount = service_price * (pre_billing.duration / service_charge_duration)
        except ValueError:
            abort(500, message="Service price or charge duration is not a valid number.")

        billing = BillingModel(
            amount=amount,
            duration=pre_billing.duration,
            service_id=pre_billing.service_id,
            participant_id=participant_id,
            pre_billing_id=pre_billing_id,
            created_by=user_id
        )
        pre_billing.billing_status = 1
        db.session.add(billing)
        db.session.add(pre_billing)
        db.session.commit()
        return {"message": "Billing created."}, 201


@blp.route("/billing/participant/<int:participant_id>/<int:billing_id>")
class BillingResource(MethodView):

    @jwt_required()
    @blp.response(200, BillingSchema)
    def get(self, participant_id, billing_id):
        get_participant_or_404(participant_id)
        billing_record = BillingModel.query.filter_by(
            id=billing_id,
            participant_id=participant_id
        ).first_or_404()
        return billing_record

    @jwt_required()
    def delete(self, participant_id, billing_id):
        billing_record = BillingModel.query.filter_by(
            id=billing_id,
            participant_id=participant_id
        ).first()

        if not billing_record:
            abort(404, message="Billing record not found.")

        try:
            db.session.delete(billing_record)
            db.session.commit()
            return {"message": "Billing record deleted."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the billing record. {e}")


@blp.route("/billing/participant/<int:participant_id>/<int:billing_id>")
class BillingResource(MethodView):

    @jwt_required()
    @blp.arguments(BillingSchema)
    @blp.response(200, BillingSchema)
    def put(self, billing_data, billing_id, participant_id):
        billing_record = BillingModel.query.filter_by(
            id=billing_id,
            participant_id=participant_id
        ).first()

        if not billing_record:
            abort(404, message="Billing record not found.")

        for key, value in billing_data.items():
            if key != 'created_by':
                setattr(billing_record, key, value)

        if 'service_id' in billing_data or 'duration' in billing_data:
            billing_record.amount = calculate_billing_amount(
                billing_record.service_id,
                billing_record.duration,
            )

        try:
            db.session.commit()
            return billing_record
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the billing record: {e}")


@blp.route("/billing")
class GetAllBillingRecords(MethodView):
    @jwt_required()
    @blp.response(200, BillingSchema(many=True))
    def get(self):
        """
        Retrieve all billing records for all participants.
        """
        try:
            billing_records = BillingModel.query.all()
            if not billing_records:
                abort(404, message="No billing records found.")
            return billing_records
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving the billing records. {e}")


@blp.route("/billing/participant/<int:participant_id>")
class GetParticipantBillingRecords(MethodView):
    @jwt_required()
    @blp.response(200, BillingSchema(many=True))
    def get(self, participant_id):
        """
        Retrieve all billing records for a specific participant.
        """
        try:
            billing_records = BillingModel.query.filter_by(participant_id=participant_id).all()
            if not billing_records:
                abort(404, message="No billing records found for the given participant.")
            return billing_records
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving the billing records. {e}")
