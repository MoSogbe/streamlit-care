import os
from datetime import datetime

from flask import request, send_from_directory, url_for
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from db import db
from helper.utils import get_filtered_query
from models.care_giver import CareGiverModel
from schemas import StaffSchema

blp = Blueprint("StaffProfile", "care_givers", description="Operations on Staff Profile")

UPLOAD_FOLDER = os.path.join('uploads', 'staff_photos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@blp.route("/staff-profile/<string:staff_id>")
class StaffType(MethodView):
    @jwt_required()
    @blp.response(200, StaffSchema)
    def get(self, staff_id):
        care_giver = CareGiverModel.query.get_or_404(staff_id)
        return care_giver

    @jwt_required()
    def delete(self, staff_id):
        try:
            staff = CareGiverModel.query.get_or_404(staff_id)
            if staff.profile_image:
                file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(staff.profile_image))
                if os.path.exists(file_path):
                    os.remove(file_path)
            db.session.delete(staff)
            db.session.commit()
            return {"message": "Staff profile deleted successfully."}, 204
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the staff profile. {e}")

    @jwt_required()
    @blp.arguments(StaffSchema, location="form")
    @blp.response(200, StaffSchema)
    def put(self, staff_data, staff_id):
        staff = CareGiverModel.query.get(staff_id)
        if not staff:
            abort(404, message="Staff not found.")

        photo = request.files.get('profile_image')
        if photo:
            filename = secure_filename(photo.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(file_path)
            staff.profile_image = url_for('StaffProfile.uploaded_file', filename=filename, _external=True)

        for key, value in staff_data.items():
            if key != 'profile_image':
                setattr(staff, key, value)

        try:
            db.session.commit()
            return staff
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the staff profile. {e}")


@blp.route("/staff-profile")
class StaffList(MethodView):
    @jwt_required()
    @blp.response(200, StaffSchema(many=True))
    def get(self):
        return CareGiverModel.query.all()

    @jwt_required()
    @blp.arguments(StaffSchema, location="form")
    @blp.response(201, StaffSchema)
    def post(self, staff_data):
        if CareGiverModel.query.filter(or_(CareGiverModel.name == staff_data["name"])).first():
            abort(409, message="A staff with that name already exists.")

        photo = request.files.get('profile_image')
        profile_image_url = None

        if photo:
            filename = secure_filename(photo.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            photo.save(file_path)
            profile_image_url = url_for('StaffProfile.uploaded_file', filename=filename, _external=True)

        staff = CareGiverModel(
            **staff_data,
            profile_image=profile_image_url,
            user_id=get_jwt_identity(),
        )

        try:
            db.session.add(staff)
            db.session.commit()
            return staff
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the staff. {e}")


@blp.route("/uploads/staff_photos/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


def save_documentation(doc_data, user_id, file, model_class, upload_folder, blueprint_name, **extra_fields):
    """
    Generalized function to save a documentation entry.

    :param doc_data: The data of the documentation.
    :param user_id: The ID of the user creating the entry.
    :param file: The file to be saved.
    :param model_class: The model class to use for saving the documentation.
    :param upload_folder: The folder to save the file in.
    :param blueprint_name: The blueprint name for generating the URL.
    :param extra_fields: Additional fields to be added to the model.
    :return: The saved documentation model instance.
    """
    if not file:
        abort(400, message="File is required.")

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    file_url = url_for(f'{blueprint_name}.uploaded_file', filename=filename, _external=True)

    documentation = model_class(
        **doc_data,
        created_by=user_id,
        file_path=file_url,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        **extra_fields
    )
    try:
        db.session.add(documentation)
        db.session.commit()
        return documentation
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message=f"An error occurred while saving the documentation: {str(e)}")


@blp.route("/staff-profile/report")
class StaffProfileReport(MethodView):
    @jwt_required()
    @blp.response(200, StaffSchema(many=True))
    def get(self, **kwargs):
        """
        Get a list of staff profiles based on the query parameters.

        Query Parameters:
        - date_from: The start date for the search.
        - date_to: The end date for the search.
        """
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        query = get_filtered_query(CareGiverModel, date_from=date_from, date_to=date_to)
        return query.all()
