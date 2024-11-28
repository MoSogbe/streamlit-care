from marshmallow import Schema, fields

class MedActionStatusSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    status_name = fields.Str(required=True)
    description = fields.Str()
