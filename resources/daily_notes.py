from datetime import datetime

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased

from db import db
from models.daily_notes import DailyNotesModel
from models.participant import ParticipantModel
from models.users import UserModel
from schema.daily_notes import DailyNoteSchema, UpdateDailyNoteSchema

blp = Blueprint("Participant Daily Note", "daily_notes", description="Operations on Participant Daily Note")


@blp.route("/daily-note/<string:participant>")
class DailyNote(MethodView):
    @jwt_required()
    @blp.response(200, DailyNoteSchema(many=True))
    def get(self, participant):
        reviewer_alias = aliased(UserModel, name='reviewer')

        query = db.session.query(
            DailyNotesModel.id,
            DailyNotesModel.participant_id,
            DailyNotesModel.comment,
            ParticipantModel.name.label('participant_name'),
            UserModel.fullname.label('created_by_username'),
            reviewer_alias.fullname.label('reviewed_by_username')
        ).join(
            ParticipantModel, DailyNotesModel.participant_id == ParticipantModel.id
        ).join(
            UserModel, DailyNotesModel.created_by == UserModel.id
        ).outerjoin(
            reviewer_alias, DailyNotesModel.reviewed_by == reviewer_alias.id
        )

        if participant:
            query = query.filter(DailyNotesModel.participant_id == participant)

        results = query.all()

        daily_notes = [{
            'id': r.id,
            'participant_id': r.participant_id,
            'comment': r.comment,
            'participant_name': r.participant_name,
            'created_by_username': r.created_by_username,
            'reviewed_by_username': r.reviewed_by_username
        } for r in results]

        return daily_notes


@blp.route("/view/daily-note")
class ViewDailyNote(MethodView):
    @jwt_required()
    @blp.response(200, DailyNoteSchema(many=True))
    def get(self):
        reviewer_alias = aliased(UserModel, name='reviewer')

        results = db.session.query(
            DailyNotesModel.id,
            DailyNotesModel.participant_id,
            DailyNotesModel.comment,
            ParticipantModel.name.label('participant_name'),
            UserModel.fullname.label('created_by_username'),
            reviewer_alias.fullname.label('reviewed_by_username')
        ).join(
            ParticipantModel, DailyNotesModel.participant_id == ParticipantModel.id
        ).join(
            UserModel, DailyNotesModel.created_by == UserModel.id
        ).outerjoin(
            reviewer_alias, DailyNotesModel.reviewed_by == reviewer_alias.id
        ).all()

        daily_notes = [{
            'id': r.id,
            'participant_id': r.participant_id,
            'comment': r.comment,
            'participant_name': r.participant_name,
            'created_by_username': r.created_by_username,
            'reviewed_by_username': r.reviewed_by_username
        } for r in results]

        return daily_notes


@blp.route("/daily-note")
class DailyNotesPost(MethodView):
    @jwt_required()
    @blp.arguments(DailyNoteSchema)
    @blp.response(201, DailyNoteSchema)
    def post(self, vitals_data):

        vitals = DailyNotesModel(
            participant_id=vitals_data["participant_id"],
            comment=vitals_data["comment"],
            created_by=get_jwt_identity(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        try:
            db.session.add(vitals)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the participant vitals .{e}.")
        return vitals


@blp.route("/update/daily-note/<int:note_id>")
class UpdateDailyNote(MethodView):
    @jwt_required()
    @blp.arguments(UpdateDailyNoteSchema)
    @blp.response(200, DailyNoteSchema)
    def put(self, data, note_id):
        daily_note = DailyNotesModel.query.get_or_404(note_id)
        daily_note.comment = data['comment']
        daily_note.reviewed_by = get_jwt_identity(),
        db.session.commit()
        return daily_note
