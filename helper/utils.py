import os
import re
from datetime import datetime, timedelta

from flask import url_for, jsonify
from flask_smorest import abort
from marshmallow import ValidationError
from sqlalchemy import and_, extract
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from db import db
from models import ParticipantModel, ServiceModel, LogEntryModel, DocumentTypeModel

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


def validate_email(email):
    if not re.match(EMAIL_REGEX, email):
        raise ValidationError('Invalid email address.')


def save_documentation(doc_data, user_id, file, model_class, upload_folder, documentation, **kwargs):
    document_type_id = doc_data['document_type_id']
    document_type = DocumentTypeModel.query.get(document_type_id)
    if not document_type:
        abort(400, message=f"Document type with id {document_type_id} does not exist.")

    if not file:
        abort(400, message="File is required.")

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    file_url = f"/{upload_folder}/{filename}"

    documentation = model_class(
        document_type_id=document_type_id,
        created_by=user_id,
        file_path=file_url,
        review_status=doc_data['review_status'],
        comment=doc_data.get('comment'),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        **kwargs
    )

    try:
        db.session.add(documentation)
        db.session.commit()
    except SQLAlchemyError as e:
        abort(500, message=f"An error occurred while saving the documentation: {str(e)}")

    return documentation


def update_file(documentation, new_file, upload_folder, documentation_model):
    if new_file:
        old_file_path = documentation.file_path
        if old_file_path:
            old_file_path = os.path.join(upload_folder, os.path.basename(old_file_path))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        filename = secure_filename(new_file.filename)
        file_path = os.path.join(upload_folder, filename)
        new_file.save(file_path)

        file_url = url_for(f'{documentation_model}.uploaded_file', filename=filename, _external=True)

        return file_url

    return documentation.file_path


def toggle_review_status(documentation, db_session):
    """
    Helper function to toggle the review status of a documentation entry.

    Args:
    - documentation: The model instance of the documentation whose review status is to be toggled.
    - db_session: The database session to use for committing the status change.

    Returns:
    - A dictionary with a success message.
    """
    documentation.review_status = not documentation.review_status

    try:
        db_session.commit()
        return {
            "message": "Review status updated successfully.",
            "review_status": documentation.review_status
        }, 200
    except SQLAlchemyError as e:
        db_session.rollback()
        abort(500, message=f"An error occurred while updating the review status: {str(e)}")


def model_to_dict(model):
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}


def get_filtered_data(model, participant_id, month, year):
    if not month or not year:
        most_recent_data = db.session.query(
            extract('month', model.created_at).label('month'),
            extract('year', model.created_at).label('year')
        ).filter(
            model.participant_id == participant_id
        ).order_by(
            model.created_at.desc()
        ).first()
        if most_recent_data:
            month = most_recent_data.month
            year = most_recent_data.year
        else:
            return []

        if model == LogEntryModel:
            data = model.query.filter(
                and_(
                    extract('month', model.created_at) == month,
                    extract('year', model.created_at) == year,
                    model.participant_id == participant_id,
                    model.location.isnot(None),
                    model.location != ""
                )
            ).order_by(
                model.created_at.desc()
            ).all()
            return data

    data = model.query.filter(
        and_(
            extract('month', model.created_at) == month,
            extract('year', model.created_at) == year,
            model.participant_id == participant_id
        )
    ).all()
    return data


def get_participant_or_404(participant_id):
    """
    Helper function to check if the participant exists and belongs to the user.
    """
    participant = ParticipantModel.query.filter_by(id=participant_id).first()
    if not participant:
        abort(404, message="Participant not found.")
    return participant


def calculate_billing_amount(service_id, duration):
    service = ServiceModel.query.get(service_id)

    if not service:
        abort(404, message="Service not found.")

    try:
        service_price = float(service.service_price)
        amount = service_price * duration
        return amount
    except ValueError:
        abort(500, message="Service price is not a valid number.")


def delete_document_and_file(documentation, db_session, file_path):
    """
    Helper function to delete a file from the local storage and
    the corresponding documentation entry from the database.

    Args:
    - documentation: The model instance of the documentation to delete.
    - db_session: The database session to use for committing the deletion.
    - file_path: The path to the file that should be deleted.

    Returns:
    - A dictionary with a success message.
    """
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            abort(500, message=f"An error occurred while deleting the file: {str(e)}")

    try:
        db_session.delete(documentation)
        db_session.commit()
        return {"message": "Documentation and file deleted successfully."}, 200
    except SQLAlchemyError as e:
        db_session.rollback()
        abort(500, message=f"An error occurred while deleting the documentation: {str(e)}")


def update_documentation(documentation, documentation_data, new_file, upload_folder, documentation_model):
    if new_file:
        documentation.file_path = update_file(documentation, new_file, upload_folder, documentation_model)

    documentation.document_type_id = documentation_data.get('document_type_id', documentation.document_type_id)
    documentation.comment = documentation_data.get('comment', documentation.comment)
    documentation.review_status = documentation_data.get('review_status', documentation.review_status)

    try:
        db.session.commit()
        return documentation
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message=f"An error occurred while updating the documentation: {str(e)}")


def get_status(model, status_field, status_value):
    try:
        results = db.session.query(
            model.participant_id,
            db.func.count(model.id).label('count')
        ).filter_by(**{status_field: status_value}).group_by(model.participant_id).all()

        response = []
        for result in results:
            participant = db.session.query(ParticipantModel).get(result.participant_id)
            response.append({
                'participant_id': participant.id,
                'participant': participant.name,
                'count': result.count
            })

        return jsonify(response)
    except SQLAlchemyError as e:
        abort(500, message=f"An error occurred while retrieving the status: {str(e)}")


def get_filtered_query(
        model,
        date_from=None,
        date_to=None,
):
    query = model.query
    if date_from:
        query = query.filter(model.created_at >= date_from)
    if date_to:
        if not date_from:
            abort(400, message="'date_from' is required if 'date_to' is provided.")
        query = query.filter(model.created_at <= date_to)
    return query


def get_time_window(minutes):
    now = datetime.now()
    return now - timedelta(minutes=minutes), now
