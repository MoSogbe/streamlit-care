from marshmallow import Schema, fields


class VitalsSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    blood_pressure = fields.Int(required=True)
    systolic = fields.Str(required=True)
    diastolic = fields.Str(required=True)
    pulse = fields.Str(required=True)
    glucose = fields.Str(required=True)
    comment = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
