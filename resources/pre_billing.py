from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from helper.utils import get_participant_or_404, calculate_billing_amount, get_status
from models import LogEntryModel, PreBillingModel, BillingModel
from models.participant import ParticipantModel
from models.service import ServiceModel
from schema.pre_billing import LogIdSchema, PreBillingSchema,PreBillingUpdateSchema, PreBillingViewSchema

blp = Blueprint("Pre Billing", "pre-billing", description="Operations for billing")

@blp.route("/pre-billing/<int:log_id>")
class AddPreBilling(MethodView):
    @jwt_required()
    @blp.arguments(PreBillingSchema, location="json")
    def post(self, pre_billing_data, log_id):
        log_entry_id = pre_billing_data.get('log_id')

        # Step 1: Check if log_entry_id exists in LogEntryModel
        log_entry = LogEntryModel.query.get(log_entry_id)
        if not log_entry:
            abort(404, message=f"Log entry with ID {id} not found.")

        # Step 2: Check if the log_entry_id already exists in PreBillingModel
        existing_prebilling = PreBillingModel.query.filter_by(log_id=log_entry_id).first()
        if existing_prebilling:
            abort(400, message=f"Log entry with ID {log_entry_id} already exists in pre-billing.")

        # Step 3: Insert a new record into PreBillingModel
        new_prebilling = PreBillingModel(
            log_id=log_entry_id,
            service_id=pre_billing_data.get('service_id'),
            participant_id=pre_billing_data.get('participant_id'),
            check_in_time=pre_billing_data.get('check_in_time'),
            check_out_time=pre_billing_data.get('check_out_time'),
            created_by=get_jwt_identity(),
            duration=pre_billing_data.get('duration', 0),  # Default duration to 0 if not provided
            billing_status=0  # Assuming initial billing status is 0 (not billed)
        )

        try:
            # Add the new pre-billing record and commit the transaction
            db.session.add(new_prebilling)
            # Step 4: Update the pre_billing_status of the log entry to 1
            log_entry.pre_billing_status = 1
            db.session.commit()

            return jsonify({"message": "New pre-billing record added successfully."}), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while inserting the new pre-billing record: {e}")

@blp.route("/pre-billing-update/<int:pre_billing_id>")
class PreBillingUpdateSchema(MethodView):
    @jwt_required()
    @blp.arguments(PreBillingUpdateSchema, location="json")
    def put(self, pre_billing_data, pre_billing_id):
        # Step 1: Fetch the existing pre-billing record
        pre_billing = PreBillingModel.query.get(pre_billing_id)

        if not pre_billing:
            abort(404, message=f"Pre billing record with ID {pre_billing_id} not found.")

        # Step 2: Update the pre-billing record fields if they are provided
        pre_billing.duration = pre_billing_data.get('duration', pre_billing.duration)
        pre_billing.check_in_time = pre_billing_data.get('check_in_time', pre_billing.check_in_time)
        pre_billing.check_out_time = pre_billing_data.get('check_out_time', pre_billing.check_out_time)
        pre_billing.service_id = pre_billing_data.get('service_id', pre_billing.service_id)
        pre_billing.created_by = pre_billing_data.get('created_by', pre_billing.created_by)

        # Step 3: Commit the updated pre-billing record
        try:
            db.session.commit()
            return jsonify({"message": "Pre billing record updated successfully."}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the pre-billing record: {e}")


@blp.route("/pre-billing/all")
class GetAllPreBillingRecords(MethodView):

    @jwt_required()
    @blp.response(200, PreBillingViewSchema(many=True))
    def get(self):
        """
        Retrieve all pre-billing records with participant names.
        """
        try:
            # Join PreBillingModel with ParticipantModel
            pre_billing_records = db.session.query(
                PreBillingModel.id,
                PreBillingModel.duration,
                PreBillingModel.participant_id,
                PreBillingModel.check_in_time,
                PreBillingModel.check_out_time,
                PreBillingModel.billing_status,
                PreBillingModel.service_id,
                ServiceModel.service_name.label('service_name'),
                ParticipantModel.name.label('participant_name')
            ).join(ServiceModel, PreBillingModel.service_id == ServiceModel.id) \
            .join(ParticipantModel, PreBillingModel.participant_id == ParticipantModel.id).all()

            if not pre_billing_records:
                abort(404, message="No pre-billing records found.")

            # Serialize the result for the response
            result = [
                {
                    'id': record.id,
                    'duration': record.duration,
                    'check_in_time': record.check_in_time,
                    'check_out_time': record.check_out_time,
                    'billing_status': record.billing_status,
                    'service_id': record.service_id,
                    'service_name': record.service_name,
                    'participant_name': record.participant_name,
                    'participant_id': record.participant_id
                }
                for record in pre_billing_records
            ]

            return result, 200

        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving the pre-billing records: {str(e)}")


@blp.route("/pre-billing/participant/<int:participant_id>")
class GetPreBillingRecordsByParticipant(MethodView):

    @jwt_required()
    @blp.response(200, PreBillingSchema(many=True))
    def get(self, participant_id):
        """
        Retrieve all pre-billing records for a specific participant.
        """
        get_participant_or_404(participant_id)
        try:
            pre_billing_records = PreBillingModel.query.filter_by(participant_id=participant_id).all()
            if not pre_billing_records:
                abort(404, message="No pre-billing records found for this participant.")
            return pre_billing_records
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving the pre-billing records: {str(e)}")


@blp.route("/pre-billing/item/<int:pre_billing_id>")
class GetPreBillingRecordById(MethodView):

    @jwt_required()
    @blp.response(200, PreBillingSchema)
    def get(self, pre_billing_id):
        """
        Retrieve a specific pre-billing record by its ID.
        """
        try:
            pre_billing_record = PreBillingModel.query.get_or_404(pre_billing_id)
            return pre_billing_record
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving the pre-billing record: {str(e)}")


@blp.route("/pre-billing/status")
class PreBillingStatus(MethodView):
    @jwt_required()
    def get(self):
        """
        Get the pre-billing status.

        Query Parameters:
        - pre_billed: 0 or 1
        """
        pre_billed = request.args.get('pre_billed', type=int)
        return get_status(PreBillingModel, 'billing_status', pre_billed)


@blp.route("/pre-billing/unprebilled/<int:participant_id>")
class UnprebilledPreBillingByParticipant(MethodView):
    @jwt_required()
    @blp.response(200, PreBillingSchema(many=True))
    def get(self, participant_id):
        """
        Get all unbilled pre-billing records for a participant with the specified participant_id.

        Query Parameters:
        - billed: 0 or 1
        """
        billed = request.args.get('billed', type=int)
        try:
            pre_billing_records = PreBillingModel.query.filter_by(
                participant_id=participant_id,
                billing_status=billed
            ).all()
            if not pre_billing_records:
                abort(404, message="No pre-billing records found for the specified participant.")
            return pre_billing_records
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving pre-billing records: {str(e)}")