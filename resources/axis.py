# resources/axis.py
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required
from db import db
from models.axis import AxisModel
from schema.axis import AxisSchema

blp = Blueprint("Axis", "axis", description="Operations on Axis")

@blp.route("/axes")
class AxisList(MethodView):
    @jwt_required()
    @blp.response(200, AxisSchema(many=True))
    def get(self):
        axis = AxisModel.query.all()
        return axis

@blp.route("/axis/<int:axis_id>")
class Axis(MethodView):
    @jwt_required()
    @blp.response(200, AxisSchema)
    def get(self, axis_id):
        axis = AxisModel.query.get_or_404(axis_id)
        return axis
