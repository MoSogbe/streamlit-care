from marshmallow import Schema, fields, post_load


class AppointmentSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    doctor = fields.Str(required=True)
    appointment_date = fields.DateTime(required=True)
    appointment_reason = fields.Str(required=True)
    follow_up_date = fields.DateTime(allow_none=True)
    created_by = fields.Int(dump_only=True)
    follow_up_details = fields.Str(allow_none=True)
    participant_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @post_load
    def process_follow_up(self, data, **kwargs):
        if 'follow_up_date' in data and data['follow_up_date'] == '':
            data['follow_up_date'] = None
        if 'follow_up_details' in data and data['follow_up_details'] == '':
            data['follow_up_details'] = None
        return data
