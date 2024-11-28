import os
from datetime import datetime

from flask import request, send_from_directory
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort

from db import db
from helper.utils import (
    update_documentation,
    toggle_review_status,
    get_participant_or_404,
    delete_document_and_file,
    save_documentation,
)
from models.document_type import DocumentTypeModel
from models.participant_documentation import ParticipantDocumentationModel
from models.users import UserModel
from schema.participant_documentation import ParticipantDocumentationSchema

blp = Blueprint("ParticipantDocumentations", "participant_documentations",
                description="Operations on Participant Documentations")

UPLOAD_FOLDER = os.path.join('uploads', 'participant_documentations')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@blp.route("/uploads/participant_documentations/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@blp.route("/participant_documentation/<int:participant_id>")
class ParticipantDocumentationUpload(MethodView):
    @jwt_required()
    @blp.arguments(ParticipantDocumentationSchema, location="form")
    @blp.response(201, ParticipantDocumentationSchema)
    def post(self, doc_data, participant_id):
        user_id = get_jwt_identity()
        get_participant_or_404(participant_id)
        file = request.files.get('file_path')

        documentation = save_documentation(
            doc_data,
            user_id,
            file,
            ParticipantDocumentationModel,
            UPLOAD_FOLDER,
            participant_id=participant_id,
            documentation='ParticipantDocumentations'
        )
        return documentation

    @jwt_required()
    @blp.response(200, ParticipantDocumentationSchema(many=True))
    def get(self, participant_id):
        get_participant_or_404(participant_id)
        documentations = db.session.query(
            ParticipantDocumentationModel.id,
            ParticipantDocumentationModel.participant_id,
            ParticipantDocumentationModel.document_type_id,
            DocumentTypeModel.document_type,
            ParticipantDocumentationModel.created_by,
            UserModel.fullname.label('created_by_full_name'),
            ParticipantDocumentationModel.file_path,
            ParticipantDocumentationModel.created_at,
            ParticipantDocumentationModel.updated_at,
        ).join(DocumentTypeModel, ParticipantDocumentationModel.document_type_id == DocumentTypeModel.id) \
        .join(UserModel, ParticipantDocumentationModel.created_by == UserModel.id) \
        .filter(ParticipantDocumentationModel.participant_id == participant_id) \
        .all()
        return documentations


@blp.route("/participant_documentations/report")
class AllParticipantDocumentationReportView(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantDocumentationSchema(many=True))
    def get(self):
        """
        Get all documentations for all participants.
        Report of all participant documentations

        Query Parameters:
        - participant_id: int
        - reviewed: bool
        - date_from: str (YYYY-MM-DD)
        - date_to: str (YYYY-MM-DD)
        """
        participant_id = request.args.get('participant_id')
        reviewed = request.args.get('reviewed')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        query = ParticipantDocumentationModel.query
        if participant_id:
            get_participant_or_404(participant_id)
            query = query.filter_by(participant_id=participant_id)
        if reviewed is not None:
            query = query.filter_by(review_status=(reviewed.lower() == 'true'))
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(ParticipantDocumentationModel.created_at >= date_from_obj)
            except ValueError:
                abort(400, message="Invalid date_from format. Use YYYY-MM-DD.")
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(ParticipantDocumentationModel.created_at <= date_to_obj)
            except ValueError:
                abort(400, message="Invalid date_to format. Use YYYY-MM-DD.")
        documentations = query.all()
        if not documentations:
            abort(404, message="No documentations found.")
        return documentations


@blp.route("/participant_documentations/<int:participant_id>/report")
class ParticipantDocumentationReportView(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantDocumentationSchema(many=True))
    def get(self, participant_id):
        """
        Get all documentations for a participant with the specified participant_id.
        Report of a participant documentation

        Query Parameters:
        - reviewed: bool
        - date_from: str (YYYY-MM-DD)
        - date_to: str (YYYY-MM-DD)
        """
        reviewed = request.args.get('reviewed')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        query = ParticipantDocumentationModel.query
        if participant_id is not None:
            query = query.filter_by(participant_id=participant_id)
        if reviewed is not None:
            query = query.filter_by(review_status=(reviewed.lower() == 'true'))
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(ParticipantDocumentationModel.created_at >= date_from_obj)
            except ValueError:
                abort(400, message="Invalid date_from format. Use YYYY-MM-DD.")
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(ParticipantDocumentationModel.created_at <= date_to_obj)
            except ValueError:
                abort(400, message="Invalid date_to format. Use YYYY-MM-DD.")
        documentations = query.all()
        if not documentations:
            abort(404, message="No documentations found.")
        return documentations


@blp.route("/participant_documentations")
class AllParticipantDocumentations(MethodView):
    @jwt_required()
    @blp.response(200, ParticipantDocumentationSchema(many=True))
    def get(self):
        documentations = db.session.query(
            ParticipantDocumentationModel.id,
            ParticipantDocumentationModel.participant_id,
            ParticipantDocumentationModel.document_type_id,
            DocumentTypeModel.document_type,
            ParticipantDocumentationModel.created_by,
            UserModel.fullname.label('created_by_full_name'),
            ParticipantDocumentationModel.file_path,
            ParticipantDocumentationModel.created_at,
            ParticipantDocumentationModel.updated_at,
        ).join(DocumentTypeModel, ParticipantDocumentationModel.document_type_id == DocumentTypeModel.id) \
            .join(UserModel, ParticipantDocumentationModel.created_by == UserModel.id) \
            .all()

        return documentations

        # return [
        #     {
        #         column: getattr(doc, column) for column in doc.keys()
        #     }
        #     for doc in documentations
        # ]


@blp.route("/participant_documentation/file/<int:documentation_id>")
class ParticipantDocumentationFile(MethodView):
    @jwt_required()
    def get(self, documentation_id):
        documentation = ParticipantDocumentationModel.query.get_or_404(documentation_id)
        directory = os.path.dirname(documentation.file_path)
        filename = os.path.basename(documentation.file_path)
        return send_from_directory(directory, filename)


@blp.route("/participant_documentation/review/<int:documentation_id>")
class ToggleParticipantReviewStatus(MethodView):
    @jwt_required()
    def put(self, documentation_id):
        documentation = ParticipantDocumentationModel.query.get_or_404(documentation_id)
        return toggle_review_status(documentation, db.session)


@blp.route("/participant_documentation/<int:participant_id>/<int:documentation_id>")
class DeleteParticipantDocumentation(MethodView):
    @jwt_required()
    def delete(self, participant_id, documentation_id):
        get_participant_or_404(participant_id)

        documentation = ParticipantDocumentationModel.query.filter_by(
            id=documentation_id, participant_id=participant_id
        ).first_or_404()
        return delete_document_and_file(documentation, db.session, documentation.file_path)


@blp.route("/participant_documentation/<int:documentation_id>")
class UpdateParticipantDocumentation(MethodView):
    @jwt_required()
    @blp.arguments(ParticipantDocumentationSchema, location="form")
    @blp.response(200, ParticipantDocumentationSchema)
    def put(self, documentation_data, documentation_id):
        documentation = ParticipantDocumentationModel.query.get_or_404(documentation_id)
        new_file = request.files.get('file_path') if request.files else None
        return update_documentation(
            documentation,
            documentation_data,
            new_file, UPLOAD_FOLDER,
            'ParticipantDocumentations',
        )



@blp.route("/participant_documentation/<int:documentation_id>/view", methods=['GET'])
def view_document(documentation_id):
    """Serve the document for viewing in the browser based on its documentation ID."""
    # Retrieve the document from the database
    documentation = ParticipantDocumentationModel.query.get(documentation_id)

    if not documentation:
        abort(404, message="Documentation not found.")

    # Get the file path from the model and split the file name from it
    file_path = documentation.file_path
    filename = os.path.basename(file_path)

    try:
        # Serve the file for viewing in the browser
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        abort(404, description="File not found.")

@blp.route("/participant_documentation/<int:documentation_id>/download", methods=['GET'])
def download_document(documentation_id):
    """Serve the document for downloading based on its documentation ID."""
    # Retrieve the document from the database
    documentation = ParticipantDocumentationModel.query.get(documentation_id)

    if not documentation:
        abort(404, message="Documentation not found.")

    # Get the file path from the model and split the file name from it
    file_path = documentation.file_path
    filename = os.path.basename(file_path)

    try:
        # Send the file as an attachment for downloading
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404, description="File not found.")