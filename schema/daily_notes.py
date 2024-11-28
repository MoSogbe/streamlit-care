from marshmallow import Schema, fields


class DailyNoteSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    comment = fields.Str(required=True)
    participant_name = fields.String()
    created_by_username = fields.String()
    reviewed_by_username = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UpdateDailyNoteSchema(Schema):

    class Meta:
        unknown = 'exclude'

    comment = fields.Str(required=True)
    reviewed_by = fields.Int(required=True)
