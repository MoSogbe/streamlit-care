from marshmallow import Schema,fields

from schema.behavioral_issues import BehavioralIssuesResponseSchema
from schema.progress import PProgressReportSchema, PProgressIssuesResponseSchema
from schema.progress_analysis import ProgressAnalysisResponseSchema


class ParticipantReportRequestSchema(PProgressReportSchema):

    class Meta:
        unknown = 'exclude'

    pass


class ParticipantReportResponseSchema(Schema):

    class Meta:
        unknown = 'exclude'

    analysis = ProgressAnalysisResponseSchema(many=True)
    progress = PProgressIssuesResponseSchema(many=True)
    issues = BehavioralIssuesResponseSchema(many=True)

class ResidentialDailyReportSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    service_id = fields.Int(required=True)  # Service ID
    participant_id = fields.Int(required=True)  # Participant ID
    user_id = fields.Int(required=True)  # Verifier's User ID
    date_of_service = fields.Date(required=True)  # Date of Service
    time_in = fields.Time(required=True)  # Time IN
    time_out = fields.Time(required=True)  # Time OUT
    is_present = fields.Str(required=True, validate=lambda x: x in ['YES', 'NO'])  # YES or NO
    location = fields.Str(required=False)  # Residential Service Location (if applicable)
    title = fields.Str(required=True)  # Title of the person verifying attendance
    created_at = fields.DateTime(dump_only=True)  # Automatically filled on creation
    updated_at = fields.DateTime(dump_only=True)  # Automatically filled on updates


class ResidentialDailyRequestSchema(Schema):
    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)  # Participant ID
    month = fields.Int(required=True, validate=lambda m: 1 <= m <= 12)  # Month as an integer (1-12)
    year = fields.Int(required=True, validate=lambda y: y > 0)  # Year as a positive integer


class MedicationCurrentRequestSchema(Schema):
    participant_id = fields.Int(required=True)
    date_from = fields.Date(required=True, format="%Y-%m-%d")
    date_to = fields.Date(required=True, format="%Y-%m-%d")

class DayTrainingRequestSchema(Schema):
    participant_id = fields.Int(required=True, description="ID of the participant", example=123)
    date_from = fields.Date(required=True, description="Start date for filtering logs (YYYY-MM-DD)", example="2024-10-01")
    date_to = fields.Date(required=True, description="End date for filtering logs (YYYY-MM-DD)", example="2024-10-31")

class MedicalAdministrationRequestSchema(Schema):
    participant_id = fields.Int(required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

class MedicalAdministrationResponseSchema(Schema):
    data = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()), required=True)

