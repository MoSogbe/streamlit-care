from datetime import datetime, date,time

from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from helper.utils import get_participant_or_404
from models import (
    AdministrationModel,
    MedActionModel,
    PrescriptionModel,
    StockTotalModel,
    DosageModel
)
from schema.give import GiveSchema
from schema.med_action import MedActionSchema
from schemas import (
    MarReportSchema,
    PrescriptionSchema,
    PrescriptionUpdateSchema,
)

blp = Blueprint("Participant Prescription", "prescriptions",
                description="Operations on Participant Prescription or MAR")


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def reset_todays_frequency():
    today = date.today()  # Get today's date
    prescriptions = PrescriptionModel.query.all()  # Query all prescriptions
    custom_datetime = datetime.combine(today, time(0, 0, 1))  # Today's date with time 00:00:01

    for prescription in prescriptions:
        # Convert prescription date_from and date_to to datetime objects
        date_from = datetime.strptime(prescription.date_from, '%Y-%m-%d %H:%M:%S')
        date_to = datetime.strptime(prescription.date_to, '%Y-%m-%d %H:%M:%S')

        # Check if today is within the date range and the time is exactly 00:00:01
        if date_from.date() <= today <= date_to.date() and datetime.now() == custom_datetime:
            prescription.todays_frequency = 0  # Reset today's frequency to 0

    # Commit the changes to the database
    db.session.commit()


@blp.route("/mar/<int:participant_id>")
class MarType(MethodView):
    @jwt_required()
    @blp.response(200, PrescriptionSchema(many=True))
    def get(self, participant_id):
        now = datetime.now()
        date_from = datetime(now.year, now.month, now.day, 0, 0, 1)
        date_to = datetime(now.year, now.month, now.day, 23, 59, 59)

        if not date_from or not date_to:
            abort(400, message="date_from and date_to query parameters are required.")

        try:
            reset_todays_frequency()  # Reset today's frequency at the start of each day

            query = PrescriptionModel.query.filter(
                PrescriptionModel.participant_id == participant_id,
                PrescriptionModel.date_from <= date_to,
                PrescriptionModel.date_to >= date_from
            )
            prescriptions = query.all()

            if not prescriptions:
                abort(404, message="No prescriptions found for the specified participant and date range.")

            return prescriptions
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving prescriptions: {str(e)}")


@blp.route("/mar/admin/<int:participant_id>")
class MarType(MethodView):
    @jwt_required()
    @blp.response(200, PrescriptionSchema(many=True))
    def get(self, participant_id):
        now = datetime.now()
        date_from = datetime(now.year, now.month, now.day, 0, 0, 1)
        date_to = datetime(now.year, now.month, now.day, 23, 59, 59)

        if not date_from or not date_to:
            abort(400, message="date_from and date_to query parameters are required.")

        try:
            reset_todays_frequency()  # Reset today's frequency at the start of each day

            query = PrescriptionModel.query.filter(
                PrescriptionModel.participant_id == participant_id,
                PrescriptionModel.date_to > now
            )
            prescriptions = query.all()

            if not prescriptions:
                abort(404, message="No prescriptions found for the specified participant and date range.")

            return prescriptions
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving prescriptions: {str(e)}")


@blp.route("/mar/<string:mar_id>")
class MarUpdate(MethodView):
    @jwt_required()
    def delete(self, mar_id):
        jwt = get_jwt()
        try:
            participant_mar = PrescriptionModel.query.get_or_404(mar_id)
            db.session.delete(participant_mar)
            db.session.commit()
            return {"message": "Participant Prescription deleted."}
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while deleting the Participant Prescription. {e}")

    @jwt_required()
    @blp.arguments(PrescriptionUpdateSchema)
    @blp.response(200, PrescriptionUpdateSchema)
    def put(self, participant_data, mar_id):
        mar = PrescriptionModel.query.get(mar_id)
        if mar is None:
            return {"error": "Prescription not found"}, 404

        for key, value in participant_data.items():
            setattr(mar, key, value)

        mar.updated_at = datetime.now()
        if 'created_at' in participant_data:
            mar.created_at = participant_data['created_at']

        db.session.commit()
        return mar


@blp.route("/mars")
class MarPost(MethodView):
    @jwt_required()
    @blp.arguments(PrescriptionSchema)
    @blp.response(201, PrescriptionSchema)
    def post(self, prescription_data):
        user_id = get_jwt_identity()
        prescription_data['created_by'] = user_id
        prescription_data['todays_frequency'] = prescription_data['frequency']

        # Extract the Dossage list from the prescription data
        dosage_list = prescription_data.pop('Dossage')

        # Create the Prescription entry
        prescription = PrescriptionModel(**prescription_data)

        try:
            db.session.add(prescription)
            db.session.flush()  # Get the prescription ID before committing

            # Loop through the dosage list and create DosageModel entries
            for dosage_item in dosage_list:
                dosage = dosage_item['dosage']
                time = dosage_item['time']

                dosage_entry = DosageModel(
                    prescription_id=prescription.id,
                    dosage=dosage,
                    time=time
                )
                db.session.add(dosage_entry)

            # Commit the Prescription and Dosage entries
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while saving the prescription: {e}.")

        return prescription


@blp.route("/mar/give/<int:mar_id>")
class MarGive(MethodView):
    @jwt_required()
    @blp.arguments(GiveSchema)
    def post(self, give_data, mar_id):
        if not request.is_json:
            abort(415, message="Content-Type must be application/json")

        status_id = give_data.get('status_id')
        if status_id is None:
            abort(400, message="status_id is required")

        try:
            prescription = PrescriptionModel.query.get_or_404(mar_id)
            today = date.today()

            date_from = parse_date(prescription.date_from)
            date_to = parse_date(prescription.date_to)

            if date_from.date() <= today <= date_to.date():
                if prescription.todays_frequency < prescription.frequency:
                    stock = StockTotalModel.query.filter_by(drug_id=prescription.drug_id).first()

                    if stock is None:
                        return {"message": "No stock found for this drug."}, 400

                    stock_qty = int(stock.total_qty)
                    if stock_qty < prescription.qty:
                        return {"message": "Not enough stock available for this drug."}, 400

                    if status_id != 1:
                        med_action = MedActionModel(
                            mar_id=prescription.id,
                            status_id=status_id,
                            administered_by=get_jwt_identity(),
                            created_at=datetime.now()
                        )
                        db.session.add(med_action)
                        db.session.commit()
                        return {"message": "Medication action recorded successfully."}, 200
                    else:
                        stock.total_qty = str(stock_qty - prescription.qty)
                        stock.updated_at = datetime.now()

                        administration = AdministrationModel(
                            mar_id=prescription.id,
                            administered_by=get_jwt_identity()
                        )
                        db.session.add(administration)
                        prescription.todays_frequency += 1
                        prescription.updated_at = datetime.now()

                        db.session.commit()
                        return {
                            "message": "Medication given successfully.",
                            "remaining_frequency": prescription.todays_frequency,
                            "remaining_stock": stock.total_qty
                        }, 200
                else:
                    return {"message": "No remaining frequency for this medication today."}, 400
            else:
                return {"message": "This prescription is not valid today."}, 400
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while updating the prescription: {str(e)}")


@blp.route("/med_actions")
class MedActionList(MethodView):
    @blp.response(200, MedActionSchema(many=True))
    def get(self):
        try:
            med_actions = MedActionModel.query.all()

            if not med_actions:
                abort(404, message="No medication actions found.")

            return med_actions
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving medication actions: {str(e)}")


@blp.route("/mar/report")
class MARReport(MethodView):
    @jwt_required()
    @blp.arguments(MarReportSchema, location="query")
    def get(self, args):
        """
        Get a list of MAR based on the query parameters.

        Query Parameters:
           - date_from: The start date for the search (YYYY-MM-DD).
           - date_to: The end date for the search (YYYY-MM-DD).
           - administered_by: The id of the user who administered the MAR.
           - administered: A boolean value to filter MARs that have been administered or not.
           - participant_id: The id of the participant.
        """
        date_from = args.get('date_from')
        date_to = args.get('date_to')
        administered_by = args.get('administered_by')
        administered = args.get('administered')
        participant_id = args.get('participant_id')

        query = PrescriptionModel.query

        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(PrescriptionModel.created_at >= date_from)
        if date_to:
            if not date_from:
                abort(400, message="'date_from' is required if 'date_to' is provided.")
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(PrescriptionModel.created_at <= date_to)
        if participant_id:
            get_participant_or_404(participant_id)
            query = query.filter(PrescriptionModel.participant_id == participant_id)
        if administered is not None:
            if administered:
                query = query.join(AdministrationModel).filter(
                    PrescriptionModel.id == AdministrationModel.mar_id
                )
            else:
                query = query.outerjoin(AdministrationModel).filter(
                    AdministrationModel.id.is_(None)
                )
        if administered_by is not None:
            query = query.join(
                AdministrationModel, PrescriptionModel.id == AdministrationModel.mar_id
            ).filter(AdministrationModel.administered_by == administered_by)

        results = query.all()

        if not results:
            abort(404, message="No MARs found for the specified query parameters.")

        return PrescriptionSchema(many=True).dump(results)
