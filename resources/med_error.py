# resources/med_error.py
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required
from db import db
from models.med_error_reason import MedErrorReasonModel
from models.med_error import MedErrorModel
from models.prescription import PrescriptionModel
from models.participant import ParticipantModel
from models.stock_total import StockTotalModel
from models.drugs import DrugModel
from schema .med_error import MedErrorReasonSchema, MedErrorSchema
from datetime import datetime

blp = Blueprint("MedErrors", "med_errors", description="Operations on Medication Errors")

@blp.route("/med_error_reasons")
class MedErrorReasonList(MethodView):
    @blp.response(200, MedErrorReasonSchema(many=True))
    def get(self):
        reasons = MedErrorReasonModel.query.all()
        return reasons

@blp.route("/med_errors")
class MedErrorList(MethodView):
    @jwt_required()
    @blp.arguments(MedErrorSchema)
    @blp.response(201, MedErrorSchema)
    def post(self, error_data):
        mar_id = error_data.get("mar_id")  # Use .get() to handle the case when mar_id is not provided
        error_reason_id = error_data["error_reason_id"]
        participant_id = error_data["participant_id"]
        drug_id = error_data["drug_id"]
        qty = error_data["qty"]
        comment = error_data.get("comment", "")
        user_id = get_jwt_identity()

        # Get the participant and stock
        participant = ParticipantModel.query.get_or_404(participant_id)
        stock = StockTotalModel.query.filter_by(drug_id=drug_id).first()

        if stock is None:
            abort(400, message="No stock found for this drug.")

        stock_qty = int(stock.total_qty)

        # Adjust stock based on error reason
        if error_reason_id in [2, 3]:  # Only handle stock adjustments for error reasons 2 and 3
            if error_reason_id == 2:  # Overdose
                stock_adjustment = -qty
            elif error_reason_id == 3:  # Underdose
                stock_adjustment = qty

            stock.total_qty = str(stock_qty + stock_adjustment)
            stock.updated_at = datetime.now()

        # Create the MedError record
        error = MedErrorModel(
            participant_id=participant_id,
            mar_id=mar_id if error_reason_id != 4 else None,  # Set mar_id to None for PRN
            drug_id=drug_id,
            error_reason_id=error_reason_id,
            qty=qty,
            comment=comment,
            created_by=user_id,
            created_at=datetime.now()
        )

        try:
            db.session.add(error)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while logging the medication error: {str(e)}")

        return error