from marshmallow import Schema, fields, validate


class BehavioralIssuesSchema(Schema):

    class Meta:
        unknown = 'exclude'

    details = fields.String(required=True)


class BehavioralIssuesReportSchema(Schema):

    class Meta:
        unknown = 'exclude'

    month = fields.Integer(required=False, validate=validate.Range(min=1, max=12))
    year = fields.Integer(required=False, validate=validate.Range(min=1900, max=2100))


class BehavioralIssuesResponseSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Integer(required=True)
    details = fields.String(required=True)
    participant_id = fields.Integer(required=True)
    created_by = fields.Integer(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
