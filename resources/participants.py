import os

from flask import request, send_from_directory, url_for
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from db import db
from helper.utils import get_participant_or_404, get_filtered_query
from models import ParticipantModel
from schema.participant import ParticipantSchema
from schemas import DateRangeSchema

blp = Blueprint("Participants", "participants", description="Operations on Participants")

UPLOAD_FOLDER = os.path.join('uploads', 'participant_photos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@blp.route("/participants")
class AllParticipants(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantSchema(many=True))
    def get(self):
        return ParticipantModel.query.all()

    @jwt_required()
    @blp.arguments(ParticipantSchema, location="form")
    @blp.response(201, ParticipantSchema)
    def post(self, participant_data):
        name = participant_data.get('name')
        photo = request.files.get('profile_image')

        if not name:
            abort(400, message="Name is required.")

        if ParticipantModel.query.filter(or_(ParticipantModel.name == name)).first():
            abort(409, message="A Participant with that name already exists.")

        profile_image_url = None
        if photo:
            filename = secure_filename(photo.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(file_path)
            profile_image_url = url_for('Participants.uploaded_file', filename=filename, _external=True)

        participant = ParticipantModel(**participant_data, profile_image=profile_image_url)

        try:
            db.session.add(participant)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the participant: {e}.")

        return participant


@blp.route("/participants/<int:participant_id>")
class ParticipantResource(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantSchema)
    def get(self, participant_id):
        participant = get_participant_or_404(participant_id)
        return participant

    @jwt_required()
    @blp.arguments(ParticipantSchema, location="form")
    @blp.response(200, ParticipantSchema)
    def put(self, participant_data, participant_id):
        participant = get_participant_or_404(participant_id)

        photo = request.files.get('profile_image')
        if photo:
            filename = secure_filename(photo.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(file_path)
            participant.profile_image = url_for('Participants.uploaded_file', filename=filename, _external=True)

        for key, value in participant_data.items():
            setattr(participant, key, value)

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the participant: {e}.")

        return participant

    @jwt_required()
    @blp.response(204)
    def delete(self, participant_id):
        participant = get_participant_or_404(participant_id)

        if participant.profile_image:
            try:
                file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(participant.profile_image))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                abort(500, message=f"An error occurred while deleting the participant's image: {e}.")

        try:
            db.session.delete(participant)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the participant: {e}.")

        return '', 204


@blp.route("/uploads/participant_photos/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@blp.route("/participants/report")
class ParticipantsReport(MethodView):
    @jwt_required()
    @blp.arguments(DateRangeSchema, location="query")
    @blp.response(200, ParticipantSchema(many=True))
    def get(self,  args):
        """
        Get a list of staff profiles based on the query parameters.

        Query Parameters:
        - date_from: The start date for the search.
        - date_to: The end date for the search.
        """
        date_from = args.get('date_from')
        date_to = args.get('date_to')
        participants = get_filtered_query(ParticipantModel, date_from, date_to)
        return participants
