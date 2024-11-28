# resources/life_story.py
from flask import request,send_from_directory
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required
from db import db
from models.life_story import LifeStoryModel
from schema.life_story import LifeStorySchema
from werkzeug.utils import secure_filename
from datetime import datetime
import os

blp = Blueprint("LifeStories", "life_stories", description="Operations on Life Stories")
UPLOAD_FOLDER = "uploads/life_stories"

@blp.route("/life_story/<int:participant_id>")
class LifeStoryUpload(MethodView):
    @jwt_required()
    @blp.response(201, LifeStorySchema)
    def post(self, participant_id):
        user_id = get_jwt_identity()

        # Handle file upload
        file = request.files.get('file_path')
        if not file:
            abort(400, message="File is required.")

        filename = secure_filename(file.filename)
        file_path = os.path.join("uploads/life_stories", filename)
        file.save(file_path)

        life_story = LifeStoryModel(
            participant_id=participant_id,
            created_by=user_id,
            file_path=file_path,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        try:
            db.session.add(life_story)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while saving the life story: {str(e)}")

        return life_story

    @jwt_required()
    @blp.response(200, LifeStorySchema(many=True))
    def get(self, participant_id):
        life_stories = LifeStoryModel.query.filter_by(participant_id=participant_id).all()
        if not life_stories:
            abort(404, message="No life stories found for the specified participant.")
        return life_stories

@blp.route("/life_stories")
class AllLifeStories(MethodView):
    @jwt_required()
    @blp.response(200, LifeStorySchema(many=True))
    def get(self):
        life_stories = LifeStoryModel.query.all()
        return life_stories


@blp.route("/life_story/file/<int:life_story_id>")
class LifeStoryFile(MethodView):
    #@jwt_required()
    def get(self, life_story_id):
        life_story = LifeStoryModel.query.get_or_404(life_story_id)
        directory = os.path.dirname(life_story.file_path)
        filename = os.path.basename(life_story.file_path)
        return send_from_directory(directory, filename)
