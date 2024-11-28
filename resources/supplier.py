from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.supplier import SupplierModel
from schemas import SupplierSchema
from datetime import datetime

blp = Blueprint("Supplier Model", "supplier", description="Operations on Supplier Model")


@blp.route("/supplier/<string:supplier_id>")
class SupplierType(MethodView):
    @jwt_required()
    @blp.response(200, SupplierSchema)
    def get(self, supplier_id):
        supplier = SupplierModel.query.get_or_404(supplier_id)
        return supplier
    @jwt_required()
    def delete(self, supplier_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            supplier = SupplierModel.query.get_or_404(supplier_id)
            db.session.delete(supplier)
            db.session.commit()
            return {"message": "Supplier  Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the supplier. {e}")
    
    
       
    @jwt_required()
    @blp.arguments(SupplierSchema)
    @blp.response(200, SupplierSchema)
    def put(self, supplier_data, supplier_id):
        supplier = SupplierModel.query.get(supplier_id)

        if supplier:
            supplier.supplier_name = supplier_data["supplier_name"]
            supplier.supplier_phone = supplier_data["supplier_phone"]
            supplier.supplier_address = supplier_data["supplier_address"]
            supplier.supplier_contact_person = supplier_data["supplier_contact_person"]
            supplier.supplier_balance = supplier_data["supplier_balance"]
        else:
            supplier = SupplierModel(id=supplier_id, **supplier_data)

        db.session.add(supplier)
        db.session.commit()

        return supplier


@blp.route("/supplier")
class SupplierList(MethodView):
    @jwt_required()
    @blp.response(200, SupplierSchema(many=True))
    def get(self):
        return SupplierModel.query.all()
    @jwt_required()
    @blp.arguments(SupplierSchema)
    @blp.response(201, SupplierSchema)
    def post(self, supplier_data):
        if SupplierModel.query.filter(
            or_
            (
             SupplierModel.supplier_name==supplier_data["supplier_name"],
           
             )).first():
            abort(409, message="A supplier with that name already exist")
        supplier = SupplierModel(
            supplier_name = supplier_data["supplier_name"],
            supplier_phone = supplier_data["supplier_phone"],
            supplier_address = supplier_data["supplier_address"],
            supplier_contact_person = supplier_data["supplier_contact_person"],
            supplier_balance = supplier_data["supplier_balance"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(supplier)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the supplier {e}.")

        return supplier
