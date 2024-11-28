from flask import jsonify,request
from sqlalchemy import func
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from sqlalchemy import and_, extract
from helper.utils import get_participant_or_404
from helper.utils import model_to_dict, get_filtered_data
from models import LogEntryModel,PreBillingModel, UserModel, ParticipantModel, PrescriptionModel, DrugModel,DosageModel,MedActionModel
from datetime import datetime, timedelta
from app import db
from schema.report import ResidentialDailyReportSchema,ResidentialDailyRequestSchema,MedicationCurrentRequestSchema,DayTrainingRequestSchema,MedicalAdministrationRequestSchema, MedicalAdministrationResponseSchema

blp = Blueprint("Reports", "reports",
                description="Operations for major reports")

@blp.route("/report/residential-daily")
class ParticipantMonthlyResidentialReport(MethodView):
    @jwt_required()
    @blp.arguments(ResidentialDailyRequestSchema)
    @blp.response(200, ResidentialDailyReportSchema(many=True))
    def post(self,args):
        try:
            data = request.get_json()
            participant_id = data.get('participant_id')
            month = data.get('month')
            year = data.get('year')

            # Fetch participant details
            participant = ParticipantModel.query.get(participant_id)
            if not participant:
                return jsonify({"message":f"No participant found with ID {participant_id}"}), 404

            # Querying records where service_id is 2 and filtering by participant_id, month, and year
            records = PreBillingModel.query.filter_by(service_id=2, participant_id=participant_id).filter(
                extract('month', PreBillingModel.check_in_time) == month,
                extract('year', PreBillingModel.check_in_time) == year
            ).all()
            participant_info = {
                "participant_name":participant.name,
                "maid_number":participant.maid_number,
                "address":participant.address,
                "address_line_2":participant.address_2 if participant.address_2 else "N/A",
                "city":participant.city,
                "state":participant.state,
                "zip_code":participant.zip_code,
                "home_phone":participant.home_phone
            }

            if not records:
                return jsonify({"message":"No records found for the given parameters"}), 404

            # Preparing the report as a list of dictionaries
            report_data = []
            for record in records:
                user = UserModel.query.get(record.created_by)  # Assuming this fetches the user

                # Deriving the date, time in, and time out
                date_of_service = record.check_in_time.strftime("%Y-%m-%d")
                time_in = record.check_in_time.strftime("%H:%M")
                time_out = record.check_out_time.strftime("%H:%M") if record.check_out_time else "N/A"

                # Checking if participant was present
                is_present = "YES" if record.check_in_time and record.check_out_time else "NO"

                # Preparing each row of the report
                report_data.append({

                    "date_of_service":date_of_service,
                    "time_in":time_in,
                    "time_out":time_out,
                    "is_participant_present":is_present,
                    "name_of_person_verifying_attendance":user.username if user else "N/A",
                    "title":user.user_type_id if user else "N/A",
                    "signature_of_person_verifying_attendance":user.username if user else "N/A",  # Assuming name as signature
                    "signature_aate":record.updated_at.strftime("%Y-%m-%d") if record.updated_at else "N/A"
                })

                 # Structuring the participant information as a separate object in the response
             # Structuring the participant information as a separate object in the response

            return jsonify({
                "participant": participant_info,
                "report": report_data
            }), 200


        except SQLAlchemyError as err:
            return jsonify({"message":f"Validation error: {err.messages}"}), 400
        except SQLAlchemyError as e:
            return jsonify({"message":f"An error occurred while generating the report: {str(e)}"}), 500

@blp.route("/report/medication", methods=["POST"])
class MedicationReport(MethodView):
    @jwt_required()
    @blp.arguments(MedicationCurrentRequestSchema)  # The request schema will expect the params in the request body
    @blp.response(200)  # Adjust response schema if needed
    def post(self, args):
        try:
            # Extracting the parameters from the request data
            participant_id = args.get("participant_id")
            date_from = args.get("date_from")
            date_to = args.get("date_to")

            # Fetching the participant
            participant = ParticipantModel.query.get(participant_id)
            if not participant:
                return jsonify({"message":"Participant not found"}), 404


            # Fetching records based on participant_id and date range
            prescriptions = PrescriptionModel.query.filter(
                PrescriptionModel.participant_id == participant_id,
                PrescriptionModel.date_from >= date_from,
                PrescriptionModel.date_to <= date_to
            ).all()

            if not prescriptions:
                return jsonify({"message":"No prescription records found"}), 404

            report_data = []

            for prescription in prescriptions:
                # Gathering dosage times
                dosage_times = [dosage.time for dosage in prescription.dosages]

                # Preparing the report for each prescription
                report_data.append({
                    "prescription_medication":prescription.drug.drug_name,  # Assuming drug has a name attribute
                    "dosage":prescription.dosages[0].dosage if prescription.dosages else "N/A",  # First dosage amount
                    "no_of_pills_per_dose":prescription.qty,
                    "times_of_day":",".join(dosage_times),
                    "date_ordered":prescription.date_from,
                    "date_expires":prescription.date_to,
                    "refills":"N/A",  # Add logic for refills if available
                    "prescribed":prescription.user.username if prescription.user else "N/A",  # Assuming prescriber is the user
                    "description":prescription.reason_for_medication,
                })

                    # Adding participant data as a separate object in the response
                participant_data = {
                    "id":participant.id,
                    "name":participant.name,
                    "dob":participant.dob,
                    "maid_number":participant.maid_number,
                    "address":participant.address,
                    "address_2":participant.address_2,
                    "city":participant.city,
                    "state":participant.state,
                    "zip_code":participant.zip_code,
                    "home_phone":participant.home_phone
                }


            return jsonify({
                "participant":participant_data,
                "report":report_data
            }), 200

        except SQLAlchemyError as e:
            return jsonify({"message":f"An error occurred while generating the reports: {str(e)}"}), 500


@blp.route("/report/day-training/logs", methods=["POST"])
class TrainingLogs(MethodView):
    @jwt_required()
    @blp.arguments(DayTrainingRequestSchema)
    def post(self, data):
        participant_id = data["participant_id"]
        date_from = data["date_from"]
        date_to = data["date_to"]

        # Fetching the participant
        participant = ParticipantModel.query.get(participant_id)
        if not participant:
            return jsonify({"message":"Participant not found"}), 404

        # Adding participant data as a separate object in the response
        participant_data = {
            "id":participant.id,
            "name":participant.name,
            "dob":participant.dob,
            "maid_number":participant.maid_number,
            "address":participant.address,
            "address_2":participant.address_2,
            "city":participant.city,
            "state":participant.state,
            "zip_code":participant.zip_code,
            "home_phone":participant.home_phone
        }


        try:
            # Filter log entries by participant, service_id 3, and date range based on created_at
            logs = (
                LogEntryModel.query
                .filter(
                    LogEntryModel.participant_id == participant_id,
                    LogEntryModel.service_id == 3,
                    func.date(LogEntryModel.created_at) >= date_from,
                    func.date(LogEntryModel.created_at) <= date_to
                )
                .order_by(LogEntryModel.id)
                .all()
            )

            if not logs:
                return jsonify({"message": "No log entries found for the specified participant and date range."}), 404

            # Grouping logs by day
            report_data = {}
            for log in logs:
                day = log.created_at.strftime("%Y-%m-%d")  # Group by day only
                check_in_out = f"{log.check_in.strftime('%H:%M')} - {log.check_out.strftime('%H:%M') if log.check_out else 'N/A'}"

                if day not in report_data:
                    report_data[day] = {
                        "date_of_service": day,
                        "Entries": []
                    }

                # Append time entries for each day
                report_data[day]["Entries"].append(check_in_out)



            # Final response structure
            response = {
                "participant_data": participant_data,
                "logs": list(report_data.values())
            }

            return jsonify(response), 200

        except SQLAlchemyError as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500


class MedicalAdministrationReport(MethodView):
    @blp.route("/report/medical-administrations", methods=["POST"])
    @blp.arguments(MedicalAdministrationRequestSchema)
    @blp.response(200, MedicalAdministrationResponseSchema)
    def post(self, data):
        # Extract participant ID and date range from request
        participant_id = data['participant_id']
        date_from = datetime.strptime(data['date_from'], "%Y-%m-%d")
        date_to = datetime.strptime(data['date_to'], "%Y-%m-%d")

        # Calculate total days in range and create a day range list
        total_days = (date_to - date_from).days + 1
        days_range = [date_from + timedelta(days=i) for i in range(total_days)]

        # Query `MedActionModel` filtering by `mar_id` with `PrescriptionModel.id` and `drug_id` in `PrescriptionModel` with `DrugModel.id`
        med_actions = (
            db.session.query(MedActionModel)
            .join(PrescriptionModel, MedActionModel.mar_id == PrescriptionModel.id)
            .join(DrugModel, PrescriptionModel.drug_id == DrugModel.id)
            .filter(
                PrescriptionModel.participant_id == participant_id,
                PrescriptionModel.created_at <= date_to,
                PrescriptionModel.created_at >= date_from
            )
            .all()
        )

        # Format response data based on prescriptions and dosages
        response_data = []
        for med_action in med_actions:
            prescription = med_action.prescription
            drug_name = prescription.drug.drug_name
            dosages_by_day = {f"day_{i + 1}": [] for i in range(total_days)}

            for dosage in prescription.dosages:
                dosage_time = datetime.strptime(dosage.time, "%Y-%m-%d %H:%M:%S")

                # Identify day index within range
                if date_from <= dosage_time.date() <= date_to:
                    day_index = (dosage_time.date() - date_from.date()).days
                    dosages_by_day[f"day_{day_index + 1}"].append(dosage.dosage)

            # Merge dosage entries by day for the response
            response_data.append({
                "Medicine name": drug_name,
                "Dosage": prescription.qty,
                **{day: ", ".join(dosages) or None for day, dosages in dosages_by_day.items()}
            })

        return jsonify({"data": response_data}), 200
