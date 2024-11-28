from flask import jsonify, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from db import db
from sqlalchemy import or_
from models import SchedulingModel, UserModel
from models.care_giver import CareGiverModel
from models.locations import LocationModel 
from models.participant import ParticipantModel
from schemas import SchedulingSchema,SchedulingReport
from datetime import datetime, date,timedelta

blp = Blueprint("Scheduling", "scheduling", description="Operations on Scheduling & Assignmnets")

@blp.route("/scheduling/<string:scheduling_id>")
class ScheduleType(MethodView):
    @jwt_required()
    @blp.response(200, SchedulingSchema)
    def get(self, scheduling_id):
        scheduling = SchedulingModel.query.get_or_404(scheduling_id)
        return scheduling
    @jwt_required()
    def delete(self,scheduling_id):
        jwt = get_jwt()
        # if not jwt.get("is_admin"):
        #     abort(401, message="Admin privillege is required")
        try:
            scheduling = SchedulingModel.query.get_or_404(scheduling_id)
            db.session.delete(scheduling)
            db.session.commit()
            return {"message": "Schedule deleted."}
        except SQLAlchemyError as e:
                abort(500, message=f"An error occurred while deleting the Schedule. {e}")
    
   
    @jwt_required()
    @blp.arguments(SchedulingSchema)
    @blp.response(200, SchedulingSchema)
    def put(self, scheduling_data, scheduling_id):
        scheduling = SchedulingModel.query.get(scheduling_id)

        if scheduling:
            scheduling.name = scheduling_data["name"]
        else:
            scheduling = SchedulingModel(id=scheduling_id, **scheduling_data)

        db.session.add(scheduling)
        db.session.commit()

        return scheduling


@blp.route("/scheduling")
class SchedulingList(MethodView):
    @jwt_required()
    @blp.response(200, SchedulingSchema(many=True))
    def get(self):
        return SchedulingModel.query.all()
    @jwt_required()
    @blp.arguments(SchedulingSchema)
    @blp.response(201, SchedulingSchema)
    def post(self, scheduling_data):
        # Create a ParticipantModel instance
        scheduling = SchedulingModel(
            location_id=scheduling_data["location_id"],
            shift_period_id=scheduling_data["shift_period_id"],
            patient_id=scheduling_data["patient_id"],
            caregiver_id=scheduling_data["caregiver_id"],
            scheduled_by=scheduling_data["scheduled_by"],
            day_of_week=scheduling_data["day_of_week"],
            month=scheduling_data["month"],
            year=scheduling_data["year"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        try:
            db.session.add(scheduling)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while inserting the scheduling .{e}.")
        return scheduling
    
    
@blp.route("/scheduling-report-today")
class SchedulingReport(MethodView):
    @jwt_required()
    @blp.response(200, SchedulingSchema(many=True))
    def get(self):
        try:
            today = date.today()
            
            # response_data = SchedulingModel.query.filter(
            #     db.func.DATE(SchedulingModel.created_at) == today
            # ).all()
            # Process the result as needed
            # For simplicity, let's assume 'result' is a list of dictionaries
           
            result = db.session.query(
                SchedulingModel.id,
                CareGiverModel.name.label('caregiver_name'),
                ParticipantModel.name.label('patient_name'),
                LocationModel.location_name.label('location_name'),
                SchedulingModel.day_of_week,
                SchedulingModel.month,
                SchedulingModel.year,
                SchedulingModel.created_at,
                UserModel.fullname.label('fullname')
                
            ).join(CareGiverModel, SchedulingModel.caregiver_id == CareGiverModel.id).\
                join(ParticipantModel, SchedulingModel.patient_id == ParticipantModel.id).\
                join(LocationModel, SchedulingModel.location_id == LocationModel.id).\
                join(UserModel, SchedulingModel.scheduled_by == UserModel.id).\
                filter(db.func.DATE(SchedulingModel.created_at) == today).all()

            # Convert each element to a dictionary
            response_data = []
            for item in result:
               response_data.append({
                    'id': item[0],
                    'caregiver_name': item[1],
                    'patient_name': item[2],
                    'location_name': item[3],
                    'day_of_week': item[4],
                    'month': item[5],
                    'year': item[6],
                    'created_at': item[7],
                    'Created_By': item[8],
                    # Include other fields as needed
                })

            # Print the content of response_data for debugging
            print("Response Data:", response_data)

            # Return the response with the processed data
            return jsonify({'data': response_data}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
@blp.route("/scheduling-report-week")
class SchedulingReportWeek(MethodView):
    @jwt_required()
    def get(self):
        try:
           
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)

            result = db.session.query(
                SchedulingModel.id,
                CareGiverModel.name.label('caregiver_name'),
                ParticipantModel.name.label('patient_name'),
                LocationModel.location_name.label('location_name'),
                SchedulingModel.day_of_week,
                SchedulingModel.month,
                SchedulingModel.year,
                SchedulingModel.created_at,
                UserModel.fullname.label('fullname')
                
            ).join(CareGiverModel, SchedulingModel.caregiver_id == CareGiverModel.id).\
                join(ParticipantModel, SchedulingModel.patient_id == ParticipantModel.id).\
                join(LocationModel, SchedulingModel.location_id == LocationModel.id).\
                join(UserModel, SchedulingModel.scheduled_by == UserModel.id).\
                filter(db.func.DATE(SchedulingModel.created_at).between(start_of_week, end_of_week)).all()

            # Convert each element to a dictionary
            response_data = []
            for item in result:
                response_data.append({
                    'id': item[0],
                    'caregiver_name': item[1],
                    'patient_name': item[2],
                    'location_name': item[3],
                    'day_of_week': item[4],
                    'month': item[5],
                    'year': item[6],
                    'created_at': item[7],
                    'Created_By': item[8],
                    # Include other fields as needed
                })

            # Print the content of response_data for debugging
            print("Response Data:", response_data)

            # Return the response with the processed data
            return jsonify({'data': response_data}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
@blp.route("/scheduling-report-month")
class SchedulingReportMonth(MethodView):
    @jwt_required()
    @blp.response(200, SchedulingSchema(many=True))
    def get(self):
        try:
            today = date.today()
            start_of_month = date(today.year, today.month, 1)
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)

            # response_data = SchedulingModel.query.filter(
            #     db.func.DATE(SchedulingModel.created_at).between(start_of_month, end_of_month)
            # ).all()
            # Process the result as needed
            # For simplicity, let's assume 'result' is a list of dictionaries
            
            result = db.session.query(
                SchedulingModel.id,
                CareGiverModel.name.label('caregiver_name'),
                ParticipantModel.name.label('patient_name'),
                LocationModel.location_name.label('location_name'),
                SchedulingModel.day_of_week,
                SchedulingModel.month,
                SchedulingModel.year,
                SchedulingModel.created_at,
                UserModel.fullname.label('fullname')
                
            ).join(CareGiverModel, SchedulingModel.caregiver_id == CareGiverModel.id).\
                join(ParticipantModel, SchedulingModel.patient_id == ParticipantModel.id).\
                join(LocationModel, SchedulingModel.location_id == LocationModel.id).\
                join(UserModel, SchedulingModel.scheduled_by == UserModel.id).\
                filter(db.func.DATE(SchedulingModel.created_at).between(start_of_month, end_of_month)).all()

            # Convert each element to a dictionary
            response_data = []
            for item in result:
                response_data.append({
                    'id': item[0],
                    'caregiver_name': item[1],
                    'patient_name': item[2],
                    'location_name': item[3],
                    'day_of_week': item[4],
                    'month': item[5],
                    'year': item[6],
                    'created_at': item[7],
                    'Created_By': item[8],
                    # Include other fields as needed
                })

            # Print the content of response_data for debugging
            print("Response Data:", response_data)

            # Return the response with the processed data
            return jsonify({'data': response_data}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
           

            return response_data, 200
        except Exception as e:
            return {'error': str(e)}, 500