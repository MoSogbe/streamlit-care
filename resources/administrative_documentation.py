import os
from datetime import datetime

from flask import request
from flask import send_from_directory
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort

from db import db
from helper.utils import (
    delete_document_and_file,
    toggle_review_status,
    update_documentation,
    save_documentation,
)
from models.administrative_documentation import AdministrativeDocumentationModel
from models.document_type import DocumentTypeModel
from models.users import UserModel
from schema.administrative_documentation import (
    AdministrativeDResponseDocumentationSchema,
    AdministrativeDocumentationSchema
)

blp = Blueprint(
    "AdministrativeDocumentations",
    "administrative_documentations",
    description="Operations on Administrative Documentations",
)
UPLOAD_FOLDER = os.path.join('uploads', 'administrative_documentations')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@blp.route("/uploads/administrative_documentations/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@blp.route("/administrative_documentations/report")
class AdministrativeDocumentationUpload(MethodView):
    @jwt_required()
    @blp.response(200, AdministrativeDResponseDocumentationSchema(many=True))
    def get(self):
        """
        Get administrative documents filtered by review status and optional date range.
        If no review status is provided, all documents are returned.

        Query Parameters:
        - reviewed: bool
        - date_from: str (YYYY-MM-DD)
        - date_to: str (YYYY-MM-DD)
        """
        reviewed = request.args.get('reviewed')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        query = AdministrativeDocumentationModel.query

        if reviewed is not None:
            query = query.filter_by(review_status=(reviewed.lower() == 'true'))

        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(AdministrativeDocumentationModel.created_at >= date_from_obj)
            except ValueError:
                abort(400, message="Invalid date_from format. Use YYYY-MM-DD.")

        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(AdministrativeDocumentationModel.created_at <= date_to_obj)
            except ValueError:
                abort(400, message="Invalid date_to format. Use YYYY-MM-DD.")

        documentations = query.all()

        if not documentations:
            abort(404, message="No administrative documentations found.")

        return documentations


@blp.route("/administrative_documentations")
class AllAdministrativeDocumentations(MethodView):

    @jwt_required()
    @blp.arguments(AdministrativeDResponseDocumentationSchema, location="form")
    @blp.response(201, AdministrativeDResponseDocumentationSchema)
    def post(self, doc_data):
        user_id = get_jwt_identity()
        file = request.files.get('file_path')

        documentation = save_documentation(
            doc_data,
            user_id,
            file,
            AdministrativeDocumentationModel,
            UPLOAD_FOLDER,
            'AdministrativeDocumentations'
        )

        return documentation

    @jwt_required()
    @blp.response(200, AdministrativeDResponseDocumentationSchema(many=True))
    def get(self):
        documentations = db.session.query(
            AdministrativeDocumentationModel.id,
            AdministrativeDocumentationModel.document_type_id,
            DocumentTypeModel.document_type,
            AdministrativeDocumentationModel.created_by,
            UserModel.fullname.label('created_by_full_name'),
            AdministrativeDocumentationModel.file_path,
            AdministrativeDocumentationModel.comment,
            AdministrativeDocumentationModel.created_at,
            AdministrativeDocumentationModel.updated_at,
        ).join(
            DocumentTypeModel,
            AdministrativeDocumentationModel.document_type_id == DocumentTypeModel.id
        ).join(
            UserModel,
            AdministrativeDocumentationModel.created_by == UserModel.id
        ).all()

        return [
            {
                'id': doc.id,
                'document_type_id': doc.document_type_id,
                'document_type': doc.document_type,
                'created_by': doc.created_by,
                'created_by_full_name': doc.created_by_full_name,
                'file_path': doc.file_path,
                'comment': doc.comment,
                'created_at': doc.created_at,
                'updated_at': doc.updated_at,
            }
            for doc in documentations
        ]


@blp.route("/administrative_documentation/file/<int:documentation_id>")
class AdministrativeDocumentationFile(MethodView):
    @jwt_required()
    def get(self, documentation_id):
        documentation = AdministrativeDocumentationModel.query.get_or_404(documentation_id)
        directory = os.path.dirname(documentation.file_path)
        filename = os.path.basename(documentation.file_path)
        return send_from_directory(directory, filename)


@blp.route("/administrative_documentation/review/<int:documentation_id>")
class ToggleAdministrativeReviewStatus(MethodView):
    @jwt_required()
    def put(self, documentation_id):
        documentation = AdministrativeDocumentationModel.query.get_or_404(documentation_id)
        return toggle_review_status(documentation, db.session)


@blp.route("/administrative_documentation/<int:documentation_id>")
class DeleteAdministrativeDocumentation(MethodView):
    @jwt_required()
    def delete(self, documentation_id):
        documentation = AdministrativeDocumentationModel.query.get_or_404(documentation_id)
        return delete_document_and_file(documentation, db.session, documentation.file_path)


@blp.route("/administrative_documentation/<int:documentation_id>")
class UpdateAdministrativeDocumentation(MethodView):
    @jwt_required()
    @blp.arguments(AdministrativeDocumentationSchema, location="form")
    @blp.response(200, AdministrativeDResponseDocumentationSchema)
    def put(self, documentation_data, documentation_id):
        documentation = AdministrativeDocumentationModel.query.get_or_404(documentation_id)
        new_file = request.files.get('file_path') if request.files else None
        return update_documentation(
            documentation,
            documentation_data,
            new_file, UPLOAD_FOLDER,
            'AdministrativeDocumentations',
        )


@blp.route("/administrative_documentation/<int:documentation_id>/view", methods=['GET'])
def view_document(documentation_id):
    """Serve the document for viewing in the browser based on its documentation ID."""
    # Retrieve the document from the database
    documentation = AdministrativeDocumentationModel.query.get(documentation_id)

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

@blp.route("/administrative_documentation/<int:documentation_id>/download", methods=['GET'])
def download_document(documentation_id):
    """Serve the document for downloading based on its documentation ID."""
    # Retrieve the document from the database
    documentation = AdministrativeDocumentationModel.query.get(documentation_id)

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
