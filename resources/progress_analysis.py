from datetime import datetime

from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_smorest import Blueprint, abort
from sqlalchemy import and_, extract
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models.progress_analysis import AProgressReportModel
from schema.progress_analysis import (
    ProgressAnalysisSchema,
    ProgressAnalysisReportSchema,
    ProgressAnalysisResponseSchema,
)
from helper.utils import get_participant_or_404

blp = Blueprint("Participant Analysis Progress", "progress_analysis", description="Operations on progress analysis")


@blp.route("/progress-analysis/participant/<int:participant_id>")
class ProgressAnalysisList(MethodView):
    @jwt_required()
    @blp.response(200, ProgressAnalysisResponseSchema(many=True))
    def get(self, participant_id):
        """
        Get Participant analysis of progress
        """

        get_participant_or_404(participant_id)

        progress = AProgressReportModel.query.filter_by(participant_id=participant_id).all()
        return progress

    @jwt_required()
    @blp.arguments(ProgressAnalysisSchema)
    @blp.response(201, ProgressAnalysisResponseSchema)
    def post(self, progress_data, participant_id):
        """
        Create a Participant analysis of progress
        """
        user_id = get_jwt_identity()

        get_participant_or_404(participant_id)

        current_month = datetime.now().month
        current_year = datetime.now().year

        existing_entry = AProgressReportModel.query.filter(
            and_(
                AProgressReportModel.participant_id == participant_id,
                extract('month', AProgressReportModel.created_at) == current_month,
                extract('year', AProgressReportModel.created_at) == current_year
            )
        ).first()

        if existing_entry:
            abort(400, message="An entry for the current month already exists. Please update the existing entry.")

        progress_data['created_by'] = user_id
        progress_data['participant_id'] = participant_id
        progress = AProgressReportModel(**progress_data)
        try:
            db.session.add(progress)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the Participant analysis of progress. {e}")
        return progress


@blp.route("/progress-analysis/<int:issue_id>")
class ProgressAnalysisResource(MethodView):
    @jwt_required()
    @blp.response(200, ProgressAnalysisResponseSchema)
    def get(self, issue_id):
        """
        Get a specific Participant analysis of a progress report by issue ID.
        """
        progress = AProgressReportModel.query.filter_by(id=issue_id).first_or_404()
        return progress

    @jwt_required()
    @blp.arguments(ProgressAnalysisSchema)
    @blp.response(200, ProgressAnalysisResponseSchema)
    def put(self, progress_data, issue_id):
        """
        Update a specific Participant analysis of a progress report by issue ID.
        """
        progress = AProgressReportModel.query.filter_by(id=issue_id).first()

        if not progress:
            abort(404, message="Participant analysis of progress not found.")

        for key, value in progress_data.items():
            setattr(progress, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the Participant analysis of progress. {e}")

        return progress

    @jwt_required()
    def delete(self, issue_id):
        """
        Delete a specific participant analysis of progress by issue ID.
        """
        progress = AProgressReportModel.query.filter_by(id=issue_id).first()

        if not progress:
            abort(404, message="Participant analysis of progress not found.")

        try:
            db.session.delete(progress)
            db.session.commit()
            return {"message": "Participant analysis of progress deleted."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the Participant analysis of progress. {e}")


@blp.route("/progress-analysis/participant/<int:participant_id>/report")
class ProgressAnalysisReport(MethodView):

    @jwt_required()
    @blp.arguments(ProgressAnalysisReportSchema, location="json", as_kwargs=True)
    @blp.response(200, ProgressAnalysisResponseSchema(many=True))
    def post(self, participant_id, **kwargs):
        """
        Get all Participant analysis of progress for a specific participant in the provided month and year.
        \n
        Defaults to the most recent month and year if none are provided.
        """
        get_participant_or_404(participant_id)

        month = kwargs.get('month')
        year = kwargs.get('year')

        if not month or not year:
            most_recent_progress = db.session.query(
                extract('month', AProgressReportModel.created_at).label('month'),
                extract('year', AProgressReportModel.created_at).label('year')
            ).filter_by(participant_id=participant_id).order_by(
                AProgressReportModel.created_at.desc()
            ).first()

            if most_recent_progress:
                month = int(most_recent_progress.month)
                year = int(most_recent_progress.year)
            else:
                abort(404, message="No progress data found for this participant.")

        progress = AProgressReportModel.query.filter(
            and_(
                AProgressReportModel.participant_id == participant_id,
                extract('month', AProgressReportModel.created_at) == month,
                extract('year', AProgressReportModel.created_at) == year
            )
        ).all()

        if not progress:
            abort(404, message="No progress data found for the specified month and year.")

        return progress
