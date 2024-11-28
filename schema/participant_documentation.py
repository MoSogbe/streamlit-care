from marshmallow import Schema, fields

class ParticipantDocumentationSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(dump_only=True)
    document_type_id = fields.Int(required=True)
    document_type = fields.Str(dump_only=True)
    created_by = fields.Int(dump_only=True)
    created_by_full_name = fields.Str(dump_only=True)
    file_path = fields.Str(required=False)
    review_status = fields.Bool(required=True)
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
