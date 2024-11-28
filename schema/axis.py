# schemas/axis.py
from marshmallow import Schema, fields

class AxisSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    axis_type = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
