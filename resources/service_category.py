from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.service_category import ServiceCategoryModel
from schemas import ServiceCategorySchema,ServiceCategoryUpdateSchema
from datetime import datetime

blp = Blueprint("Service Category ", "service_categories", description="Setting Up service categories for service to consume")


@blp.route("/service-category/<string:service_category_id>")
class ServiceCategory(MethodView):
    @jwt_required()
    @blp.response(200, ServiceCategorySchema)
    def get(self, service_category_id):
        service_category = ServiceCategoryModel.query.get_or_404(service_category_id)
        return service_category
    @jwt_required()
    def delete(self, service_category_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            service_category = ServiceCategoryModel.query.get_or_404(service_category_id)
            db.session.delete(service_category)
            db.session.commit()
            return {"message": "Service Category  deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the service category. {e}")
                
    @jwt_required()
    @blp.arguments(ServiceCategoryUpdateSchema)
    @blp.response(200, ServiceCategorySchema)
    def put(self, service_category_data, service_category_id):
       
        service_category = ServiceCategoryModel.query.get(service_category_id)
        
        if service_category:
            service_category.category_name = service_category_data["category_name"]
        else:
            service_category = ServiceCategoryModel(id=service_category_id, **service_category_data)

        db.session.add(service_category)
        db.session.commit()

        return service_category


@blp.route("/service-category")
class ServiceCategoryList(MethodView):
    @jwt_required()
    @blp.response(200, ServiceCategorySchema(many=True))
    def get(self):
        return ServiceCategoryModel.query.all()
    @jwt_required()
    @blp.arguments(ServiceCategorySchema)
    @blp.response(201, ServiceCategorySchema)
    def post(self, service_category_data):
        if ServiceCategoryModel.query.filter(
            or_
            (
             ServiceCategoryModel.category_name==service_category_data["category_name"],
           
             )).first():
            abort(409, message="A Service Category with that name already exist")
        service_category = ServiceCategoryModel(
            category_name =service_category_data["category_name"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(service_category)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the Service Category. {e}.")

        return service_category
