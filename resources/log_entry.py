from flask import jsonify, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from helper.utils import get_status
from models import LogEntryModel
from schema.log_entry import LogEntrySchema, LogEntryUpdateSchema

log_entry_blp = Blueprint(
    'Log Entry', 'log_entry', url_prefix='/log-entries',
    description="Operations on Log Entries"
)


@log_entry_blp.route("")
class LogEntryList(MethodView):
    @jwt_required()
    @log_entry_blp.response(200, LogEntrySchema(many=True))
    def get(self):
        try:
            log_entries = LogEntryModel.query.all()
            if not log_entries:
                abort(404, message="No log entries found.")
            return log_entries
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving log entries: {str(e)}")

    @jwt_required()
    @log_entry_blp.arguments(LogEntrySchema)
    @log_entry_blp.response(201, LogEntrySchema)
    def post(self, log_entry_data):
        log_entry = LogEntryModel(
            participant_id=log_entry_data['participant_id'],
            check_in=log_entry_data['check_in'],
            check_out=log_entry_data.get('check_out'),
            notes=log_entry_data.get('notes'),
            location=log_entry_data.get('location'),
            service_id=log_entry_data.get('service_id'),
            user_id=log_entry_data.get('user_id')
        )

        try:
            db.session.add(log_entry)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while inserting the log entry: {e}")

        return jsonify(LogEntrySchema().dump(log_entry)), 201


@log_entry_blp.route("/<int:log_entry_id>")
class LogEntryDetail(MethodView):
    @jwt_required()
    @log_entry_blp.response(200, LogEntrySchema)
    def get(self, log_entry_id):
        log_entry = LogEntryModel.query.get_or_404(log_entry_id)
        return jsonify(LogEntrySchema().dump(log_entry))

    @jwt_required()
    @log_entry_blp.arguments(LogEntryUpdateSchema)
    @log_entry_blp.response(200, LogEntrySchema)
    def put(self, log_entry_data, log_entry_id):
        log_entry = LogEntryModel.query.get_or_404(log_entry_id)
        log_entry.check_out = log_entry_data.get('check_out', log_entry.check_out)
        log_entry.notes = log_entry_data.get('notes', log_entry.notes)
        log_entry.duration = log_entry_data.get('duration', log_entry.notes)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the log entry: {e}")

        return jsonify(LogEntrySchema().dump(log_entry))

    @jwt_required()
    @log_entry_blp.response(204)
    def delete(self, log_entry_id):
        log_entry = LogEntryModel.query.get_or_404(log_entry_id)

        try:
            db.session.delete(log_entry)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the log entry: {e}")

        return '', 204


@log_entry_blp.route("/participant/<int:participant_id>")
class LogEntriesByParticipant(MethodView):
    @jwt_required()
    @log_entry_blp.response(200, LogEntrySchema(many=True))
    def get(self, participant_id):
        try:
            log_entries = LogEntryModel.query.filter_by(participant_id=participant_id).all()
            if not log_entries:
                abort(404, message="No log entries found for the specified participant.")
            return log_entries
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving log entries: {str(e)}")


@log_entry_blp.route("/status")
class LogEntryStatus(MethodView):
    @jwt_required()
    def get(self):
        """
        Get the billing status.

        Query Parameters:
        - billed: 0 or 1
        """
        billed = request.args.get('pre_billed', type=int)

        return get_status(LogEntryModel, 'pre_billing_status', billed)


@log_entry_blp.route("/unprebilled/<int:participant_id>")
class UnprebilledLogEntriesByParticipant(MethodView):
    @jwt_required()
    @log_entry_blp.response(200, LogEntrySchema(many=True))
    def get(self, participant_id):
        """
        Get all unprebilled log entries for a participant with the specified participant_id.

        Query Parameters:
        - pre_billed: 0 or 1 (required)
        """
        pre_billed = request.args.get('pre_billed', type=int)
        if pre_billed is None:
            abort(400, message="`pre_billed` query parameter is required.")
        try:
            log_entries = LogEntryModel.query.filter_by(
                participant_id=participant_id,
                pre_billing_status=pre_billed
            ).filter(
                LogEntryModel.check_out.isnot(None),
                LogEntryModel.check_out != ''
            ).all()
            if not log_entries:
                abort(404, message="No unprebilled log entries found for the specified participant.")
            return log_entries
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving log entries: {str(e)}")
