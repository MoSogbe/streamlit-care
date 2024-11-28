from marshmallow import Schema, fields


class BillingSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True)
    duration = fields.Int(required=True)
    service_id = fields.Int(required=True)
    participant_id = fields.Int(required=True)
    pre_billing_id = fields.Int(required=True)
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CreateBillingSchema(Schema):
    class Meta:
        unknown = 'exclude'

    pre_billing_id = fields.Int(required=True)
