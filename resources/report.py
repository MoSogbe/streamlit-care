from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint
from sqlalchemy import and_, extract
from helper.utils import get_participant_or_404
from helper.utils import model_to_dict, get_filtered_data
from models import (
    LogEntryModel,
    BIssuesModel,
    CompanyModel,
    PProgressModel,
    AppointmentModel,
    ParticipantModel,
    AProgressReportModel,
    ParticipantObjectivesModel,
)
from schema.report import ParticipantReportRequestSchema

blp = Blueprint("Get Participant Monthly Summary Report", "report",
                description="Operations for getting participant reports")


@blp.route("/report/monthly/participants/<int:participant_id>")
class ParticipantMonthlyReport(MethodView):

    @jwt_required()
    @blp.arguments(ParticipantReportRequestSchema, location="json", as_kwargs=True)
    def post(self, participant_id, **kwargs):
        """
        Get Participant report for a specific participant.
        """
        month = kwargs.get('month')
        year = kwargs.get('year')

        get_participant_or_404(participant_id)

        analysis = AProgressReportModel.query.filter(
            and_(
                extract('month', AProgressReportModel.created_at) == month,
                extract('year', AProgressReportModel.created_at) == year,
                AProgressReportModel.participant_id == participant_id
            )
        ).first()
        issues = get_filtered_data(BIssuesModel, participant_id, month, year)
        progress_data = get_filtered_data(PProgressModel, participant_id, month, year)
        appointment = get_filtered_data(AppointmentModel, participant_id, month, year)
        objectives = get_filtered_data(ParticipantObjectivesModel, participant_id, month, year)
        log_entries = get_filtered_data(LogEntryModel, participant_id, month, year)
        company_data = CompanyModel.query.first()
        participant = ParticipantModel.query.get(participant_id)

        response = {
            "analysis": model_to_dict(analysis) if analysis else {},
            "issues": [model_to_dict(item) for item in issues] if issues else [],
            "progress": [model_to_dict(item) for item in progress_data] if progress_data else [],
            "appointment": [model_to_dict(item) for item in appointment] if appointment else [],
            "objectives": [model_to_dict(item) for item in objectives] if objectives else [],
            "company": model_to_dict(company_data) if company_data else {},
            "participant": model_to_dict(participant) if participant else {},
            "log_entries": [model_to_dict(item) for item in log_entries] if log_entries else [],
        }

        return response
