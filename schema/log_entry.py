from marshmallow import Schema, fields


class LogEntrySchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    pre_billing_status = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    check_in = fields.DateTime(required=True)
    check_out = fields.DateTime()
    notes = fields.Str()
    location = fields.Str(required=False)
    duration = fields.Int(dump_only=True)
    service_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class LogEntryUpdateSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    notes = fields.Str()
    duration = fields.Int(required=True)
    check_out = fields.DateTime(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class AllParticipantsLogEntriesSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    user_id = fields.Int(dump_only=True)
    check_in = fields.DateTime(required=True)
    check_out = fields.DateTime()
    notes = fields.Str()
    location = fields.Str()
    duration = fields.Int(dump_only=True)
    service_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    pre_billing_status = fields.Int(dump_only=True)
