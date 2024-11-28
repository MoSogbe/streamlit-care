from marshmallow import Schema, fields


class MedActionSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    mar_id = fields.Int(required=True)
    status_id = fields.Int(required=True)
    status = fields.Str(dump_only=True)
    administered_by = fields.Int(dump_only=True)
    caregiver_name = fields.Str(dump_only=True, attribute="users.fullname")
    participant_name = fields.Str(dump_only=True, attribute="prescriptions.participant.name")
    created_at = fields.DateTime(dump_only=True)
