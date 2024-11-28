from marshmallow import Schema, fields


class AdministrativeDocumentationSchema(Schema):

    class Meta:
        unknown = 'exclude'

    document_type_id = fields.Int(required=True)
    document_type = fields.Str(dump_only=True)
    comment = fields.Str()
    file_path = fields.Str(required=False)


class AdministrativeDResponseDocumentationSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    document_type_id = fields.Int(required=True)
    document_type = fields.Str(dump_only=True)
    created_by = fields.Int(dump_only=True)
    created_by_full_name = fields.Str(dump_only=True)
    file_path = fields.Str(dump_only=True)
    review_status = fields.Bool(required=True)
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
