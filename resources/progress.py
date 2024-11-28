from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import and_, extract
from sqlalchemy.exc import SQLAlchemyError

from db import db
from helper.utils import get_participant_or_404
from models.progress import PProgressModel
from schema.progress import PProgressReportSchema, PProgressIssuesSchema, PProgressIssuesResponseSchema

blp = Blueprint("Participant progress", "progress", description="Operations on progress")


@blp.route("/progress/participant/<int:participant_id>")
class PProgressList(MethodView):
    @jwt_required()
    @blp.response(200, PProgressIssuesResponseSchema(many=True))
    def get(self, participant_id):
        """
        Get Participant progress for a specific participant.
        """

        get_participant_or_404(participant_id)

        progress = PProgressModel.query.filter_by(participant_id=participant_id).all()
        return progress

    @jwt_required()
    @blp.arguments(PProgressIssuesSchema)
    @blp.response(201, PProgressIssuesResponseSchema)
    def post(self, progress_data, participant_id):
        """
        Create a Participant progress for a specific participant
        """
        user_id = get_jwt_identity()

        get_participant_or_404(participant_id)

        progress_data['created_by'] = user_id
        progress_data['participant_id'] = participant_id
        progress = PProgressModel(**progress_data)
        try:
            db.session.add(progress)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the Participant progress. {e}")
        return progress


@blp.route("/progress/<int:issue_id>")
class BehavioralIssueResource(MethodView):
    @jwt_required()
    @blp.response(200, PProgressIssuesResponseSchema)
    def get(self, issue_id):
        """
        Get specific Participant progress by issue ID.
        """
        progress = PProgressModel.query.filter_by(id=issue_id).first_or_404()
        return progress

    @jwt_required()
    @blp.arguments(PProgressIssuesSchema)
    @blp.response(200, PProgressIssuesResponseSchema)
    def put(self, progress_data, issue_id):
        """
        Update specific Participant progress by issue ID.
        """
        progress = PProgressModel.query.filter_by(id=issue_id).first()

        if not progress:
            abort(404, message="Participant progress not found.")

        for key, value in progress_data.items():
            setattr(progress, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the Participant progress. {e}")

        return progress

    @jwt_required()
    def delete(self, issue_id):
        """
        Delete specific participant progress by issue ID.
        """
        progress = PProgressModel.query.filter_by(id=issue_id).first()

        if not progress:
            abort(404, message="Participant progress not found.")

        try:
            db.session.delete(progress)
            db.session.commit()
            return {"message": "Participant progress deleted."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the Participant progress. {e}")


@blp.route("/progress/participant/<int:participant_id>/report")
class PProgressByReport(MethodView):
    @jwt_required()
    @blp.arguments(PProgressReportSchema, location="json", as_kwargs=True)
    @blp.response(200, PProgressIssuesResponseSchema(many=True))
    def post(self, participant_id, **kwargs):
        """
        Get all Participant progress for a specific participant in the provided month and year.
        \n
        Defaults to the most recent month and year if none are provided.
        """
        get_participant_or_404(participant_id)

        month = kwargs.get('month')
        year = kwargs.get('year')

        if not month or not year:
            most_recent_progress = db.session.query(
                extract('month', PProgressModel.created_at).label('month'),
                extract('year', PProgressModel.created_at).label('year')
            ).filter_by(participant_id=participant_id).order_by(
                PProgressModel.created_at.desc()
            ).first()

            if most_recent_progress:
                month = int(most_recent_progress.month)
                year = int(most_recent_progress.year)
            else:
                abort(404, message="No progress data found for this participant.")

        progress = PProgressModel.query.filter(
            and_(
                PProgressModel.participant_id == participant_id,
                extract('month', PProgressModel.created_at) == month,
                extract('year', PProgressModel.created_at) == year
            )
        ).all()

        if not progress:
            abort(404, message="No progress data found for the specified month and year.")

        return progress
