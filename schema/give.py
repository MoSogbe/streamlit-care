from marshmallow import Schema, fields


class GiveSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    status_id = fields.Int(required=True)
