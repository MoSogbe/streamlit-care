from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models.bio_title import BTitleModel
from schemas import BioTitleSchema
from datetime import datetime

blp = Blueprint("Bio Titles", "bio_titles", description="Operations on Bio Titles")


@blp.route("/bio-titles/<string:btitle_id>")
class BioTitleType(MethodView):
    @jwt_required()
    @blp.response(200, BioTitleSchema)
    def get(self, bio_title_id):
        bio_title = BTitleModel.query.get_or_404(bio_title_id)
        return bio_title
    @jwt_required()
    def delete(self,bio_title_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            btitle = BTitleModel.query.get_or_404(bio_title_id)
            db.session.delete(btitle)
            db.session.commit()
            return {"message": "Bio Title Type deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the bio title. {e}")
    
   
    @jwt_required()
    @blp.arguments(BioTitleSchema)
    @blp.response(200, BioTitleSchema)
    def put(self, bio_title_data, btitle_id):
        bio_title = BTitleModel.query.get(btitle_id)

        if bio_title:
            bio_title.bio_name = bio_title_data["bio_name"]
        else:
            bio_title = BTitleModel(id=btitle_id, **bio_title_data)

        db.session.add(bio_title)
        db.session.commit()

        return bio_title


@blp.route("/bio-title")
class BioTitleList(MethodView):
    @jwt_required()
    @blp.response(200, BioTitleSchema(many=True))
    def get(self):
        return BTitleModel.query.all()
    @jwt_required()
    @blp.arguments(BioTitleSchema)
    @blp.response(201, BioTitleSchema)
    def post(self, bstatus_data):
        if BTitleModel.query.filter(
            or_
            (
             BTitleModel.bio_name==bstatus_data["bio_name"],
           
             )).first():
            abort(409, message="A bio title with that name already exist")
        bstatus = BTitleModel(
            bio_name = bstatus_data["bio_name"],
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        try:
            db.session.add(bstatus)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the bio title .{e}.")

        return bstatus
