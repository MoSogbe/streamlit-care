from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required
from db import db
from models.document_type import DocumentTypeModel
from schema.document_type import DocumentTypeSchema
from datetime import datetime, timezone

blp = Blueprint("DocumentTypes", "document_types", description="Operations on document types")

@blp.route("/document_type")
class DocumentTypeList(MethodView):
    @jwt_required()
    @blp.arguments(DocumentTypeSchema)
    @blp.response(201, DocumentTypeSchema)
    def post(self, document_type_data):
        document_type = DocumentTypeModel(**document_type_data)
        try:
            db.session.add(document_type)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the document type: {str(e)}")

        return document_type

    @jwt_required()
    @blp.response(200, DocumentTypeSchema(many=True))
    def get(self):
        document_types = DocumentTypeModel.query.all()
        return document_types

@blp.route("/document_type/<int:document_type_id>")
class DocumentType(MethodView):
    @jwt_required()
    @blp.response(200, DocumentTypeSchema)
    def get(self, document_type_id):
        document_type = DocumentTypeModel.query.get_or_404(document_type_id)
        return document_type

    @jwt_required()
    @blp.arguments(DocumentTypeSchema)
    @blp.response(200, DocumentTypeSchema)
    def put(self, document_type_data, document_type_id):
        document_type = DocumentTypeModel.query.get_or_404(document_type_id)
        document_type.document_type = document_type_data["document_type"]

        try:
            db.session.add(document_type)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while updating the document type: {str(e)}")

        return document_type

    @jwt_required()
    def delete(self, document_type_id):
        document_type = DocumentTypeModel.query.get_or_404(document_type_id)

        try:
            db.session.delete(document_type)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while deleting the document type: {str(e)}")

        return {"message": "Document type deleted."}
