import os
from flask import request, send_from_directory, url_for
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from db import db
from models.company import CompanyModel
from schema.company import CompanySchema

blp = Blueprint("Companies", "companies", description="Operations on Companies")

UPLOAD_FOLDER = os.path.join('uploads', 'company_logos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def truncate_table():
    try:
        db.session.execute(text('TRUNCATE TABLE companies'))
        db.session.commit()
    except SQLAlchemyError as e:
        abort(500, message=f"An error occurred while truncating the table: {e}")


@blp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@blp.route("/company")
class CreateCompany(MethodView):
    @jwt_required()
    @blp.arguments(CompanySchema, location="form")
    @blp.response(201, CompanySchema)
    def post(self, company_data):
        truncate_table()

        file = request.files.get('logo_path')
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            logo_path = url_for('Companies.uploaded_file', filename=filename, _external=True)
        else:
            logo_path = None

        company = CompanyModel(**company_data, logo_path=logo_path)
        try:
            db.session.add(company)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the company: {e}")

        return company

    @jwt_required()
    @blp.response(200, CompanySchema)
    def get(self):
        filters = request.args.to_dict()
        query = CompanyModel.query

        for key, value in filters.items():
            if hasattr(CompanyModel, key):
                query = query.filter(getattr(CompanyModel, key).like(f"%{value}%"))

        company = query.first()
        if not company:
            abort(404, message="No companies found with the given filters.")
        return company


@blp.route("/company/<int:company_id>")
class UpdateCompany(MethodView):
    @jwt_required()
    @blp.arguments(CompanySchema, location="form")
    @blp.response(200, CompanySchema)
    def put(self, company_data, company_id):
        company = CompanyModel.query.get_or_404(company_id)

        for key, value in company_data.items():
            setattr(company, key, value)

        file = request.files.get('logo_path')
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            # Generate URL for the uploaded file
            company.logo_path = url_for('Companies.uploaded_file', filename=filename, _external=True)

        try:
            db.session.commit()
            return company
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the company profile: {e}")


@blp.route("/company/<int:company_id>/logo")
class UpdateCompanyLogo(MethodView):
    @jwt_required()
    @blp.response(200, CompanySchema)
    def put(self, company_id):
        company = CompanyModel.query.get_or_404(company_id)

        file = request.files.get('logo_path')
        if not file:
            abort(400, message="Logo file is required.")

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        company.logo_path = url_for('Companies.uploaded_file', filename=filename, _external=True)

        try:
            db.session.commit()
            return company
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while updating the company logo: {e}")


@blp.route("/company/<int:company_id>")
class DeleteCompany(MethodView):
    @jwt_required()
    @blp.response(204)
    def delete(self, company_id):
        company = CompanyModel.query.get_or_404(company_id)
        try:
            db.session.delete(company)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while deleting the company: {e}")
        return '', 204
