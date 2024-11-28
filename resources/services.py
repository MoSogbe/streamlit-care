from datetime import datetime

from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from db import db
from helper.utils import get_participant_or_404
from models import ServiceModel, LogEntryModel
from schemas import ServiceSchema, ServiceUpdateSchema, ServiceReportSchema

blp = Blueprint("Services", "user_types", description="Operations on services being rendered in the care home")


@blp.route("/services/<string:service_id>")
class UserType(MethodView):
    @jwt_required()
    @blp.response(200, ServiceSchema)
    def get(self, service_id):
        services = ServiceModel.query.get_or_404(service_id)
        return services

    @jwt_required()
    def delete(self, service_id):

        try:
            services = ServiceModel.query.get_or_404(service_id)
            db.session.delete(services)
            db.session.commit()
            return {"message": "Service Type deleted."}

        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while deleting the services. {e}")

    @jwt_required()
    @blp.arguments(ServiceUpdateSchema)
    @blp.response(200, ServiceSchema)
    def put(self, service_data, service_id):
        services = ServiceModel.query.get(service_id)
        if services:
            services.service_name = service_data["service_name"]
            services.service_price = service_data["service_price"],
            services.service_charge_duration = service_data["service_charge_duration"],
            services.service_charge_frequency = service_data["service_charge_frequency"],
            services.service_category = service_data["service_category"],
        else:
            services = ServiceModel(id=service_id, **service_data)

        db.session.add(services)
        db.session.commit()

        return services


@blp.route("/services")
class ServiceList(MethodView):
    @jwt_required()
    @blp.response(200, ServiceSchema(many=True))
    def get(self):
        return ServiceModel.query.all()

    @jwt_required()
    @blp.arguments(ServiceSchema)
    @blp.response(201, ServiceSchema)
    def post(self, service_data):
        if ServiceModel.query.filter(
                or_
                    (
                    ServiceModel.service_name == service_data["service_name"],
                )).first():
            abort(409, message="A service Type with that name already exist")
        services = ServiceModel(
            service_name=service_data["service_name"],
            service_price=service_data["service_price"],
            service_charge_duration=service_data["service_charge_duration"],
            service_charge_frequency=service_data["service_charge_frequency"],
            service_category=service_data["service_category"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        try:
            db.session.add(services)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the services. {e}")

        return services


@blp.route("/services/report")
class ServicesReport(MethodView):
    @jwt_required()
    @blp.arguments(ServiceReportSchema, location="query")
    @blp.response(200, ServiceSchema(many=True))
    def get(self, args):
        """
        Get a list of Services based on the query parameters.

        Query Parameters:
            - date_from: The start date for the search.
            - date_to: The end date for the search.
            - participant_id: The participant id to filter by.
            - service_id: The service id to filter by.
            - service_category_id: The service category id to filter by.
        """
        date_from = args.get('date_from')
        date_to = args.get('date_to')
        service_id = args.get('service_id')
        participant_id = args.get('participant_id')
        service_category_id = args.get('service_category_id')
        query = db.session.query(ServiceModel).join(LogEntryModel)

        if date_from:
            query = query.filter(LogEntryModel.created_at >= date_from)
        if date_to:
            if not date_from:
                abort(400, message="'date_from' is required if 'date_to' is provided.")
            query = query.filter(LogEntryModel.created_at <= date_to)
        if service_id:
            query = query.filter(ServiceModel.id == service_id)
        if participant_id:
            get_participant_or_404(participant_id)
            query = query.filter(LogEntryModel.participant_id == participant_id)
        if service_category_id:
            query = query.filter(ServiceModel.service_category == service_category_id)

        services = query.all()

        if not services:
            abort(404, message="No services found for the specified criteria.")

        return services
