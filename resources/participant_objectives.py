from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import and_, extract
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models.participant_objectives import ParticipantObjectivesModel
from schema.participant_objectives import (
    ParticipantObjectivesSchema,
    ParticipantObjectivesReportSchema,
    ParticipantObjectivesResponseSchema,
)
from helper.utils import get_participant_or_404

blp = Blueprint("Participant Objectives", "participant_objectives", description="Operations on participant objectives")


@blp.route("/objectives/participant/<int:participant_id>")
class ParticipantObjectivesList(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantObjectivesResponseSchema(many=True))
    def get(self, participant_id):
        """
        Get objectives for a specific participant.
        """
        user_id = get_jwt_identity()

        get_participant_or_404(participant_id)

        objectives = ParticipantObjectivesModel.query.filter_by(participant_id=participant_id, created_by=user_id).all()
        return objectives

    @jwt_required()
    @blp.arguments(ParticipantObjectivesSchema)
    @blp.response(201, ParticipantObjectivesResponseSchema)
    def post(self, objectives_data, participant_id):
        """
        Create an objective for a specific participant.
        """
        user_id = get_jwt_identity()

        get_participant_or_404(participant_id)

        objectives_data['created_by'] = user_id
        objectives_data['participant_id'] = participant_id
        objective = ParticipantObjectivesModel(**objectives_data)
        try:
            db.session.add(objective)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while creating the objective. {e}")
        return objective


@blp.route("/objectives/<int:objective_id>")
class ParticipantObjectiveResource(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantObjectivesResponseSchema)
    def get(self, objective_id):
        """
        Get a specific objective by objective ID.
        """
        user_id = get_jwt_identity()
        objective = ParticipantObjectivesModel.query.filter_by(id=objective_id, created_by=user_id).first_or_404()
        return objective

    @jwt_required()
    @blp.arguments(ParticipantObjectivesSchema)
    @blp.response(200, ParticipantObjectivesResponseSchema)
    def put(self, objectives_data, objective_id):
        """
        Update a specific objective by objective ID.
        """
        user_id = get_jwt_identity()
        objective = ParticipantObjectivesModel.query.filter_by(id=objective_id, created_by=user_id).first()

        if not objective:
            abort(404, message="Objective not found.")

        for key, value in objectives_data.items():
            setattr(objective, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the objective. {e}")

        return objective

    @jwt_required()
    def delete(self, objective_id):
        """Delete a specific objective by objective ID."""
        user_id = get_jwt_identity()
        objective = ParticipantObjectivesModel.query.filter_by(id=objective_id, created_by=user_id).first()

        if not objective:
            abort(404, message="Objective not found.")

        try:
            db.session.delete(objective)
            db.session.commit()
            return {"message": "Objective deleted."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the objective. {e}")


@blp.route("/objectives/participant/<int:participant_id>/report")
class ParticipantObjectivesByReport(MethodView):
    @jwt_required()
    @blp.arguments(ParticipantObjectivesReportSchema, location="json", as_kwargs=True)
    @blp.response(200, ParticipantObjectivesResponseSchema(many=True))
    def post(self, participant_id, **kwargs):
        """
        Get all objectives for a specific participant in the provided month and year.
        \n
        Defaults to the most recent month and year if none are provided.
        """
        get_participant_or_404(participant_id)

        month = kwargs.get('month')
        year = kwargs.get('year')

        if not month or not year:
            most_recent_objective = db.session.query(
                extract('month', ParticipantObjectivesModel.created_at).label('month'),
                extract('year', ParticipantObjectivesModel.created_at).label('year')
            ).filter_by(participant_id=participant_id).order_by(
                ParticipantObjectivesModel.created_at.desc()
            ).first()

            if most_recent_objective:
                month = int(most_recent_objective.month)
                year = int(most_recent_objective.year)
            else:
                abort(404, message="No objectives found for this participant.")

        objectives = ParticipantObjectivesModel.query.filter(
            and_(
                ParticipantObjectivesModel.participant_id == participant_id,
                extract('month', ParticipantObjectivesModel.created_at) == month,
                extract('year', ParticipantObjectivesModel.created_at) == year
            )
        ).all()

        if not objectives:
            abort(404, message="No objectives found for the specified month and year.")

        return objectives
