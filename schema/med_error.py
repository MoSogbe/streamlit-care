from marshmallow import Schema, fields

class MedErrorReasonSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    reason = fields.Str(required=True)

class MedErrorSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    drug_id = fields.Int(required=True)
    mar_id = fields.Int()
    participant_id = fields.Int(required=True)
    error_reason_id = fields.Int(required=True)
    error_reason = fields.Nested(MedErrorReasonSchema, dump_only=True)
    qty = fields.Int(required=True)
    comment = fields.Str(required=False)
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
