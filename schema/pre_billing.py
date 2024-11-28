from datetime import datetime

from marshmallow import Schema, fields, ValidationError


def validate_date_range(value):
    if value < datetime(2021, 1, 1):
        raise ValidationError("Date must be on or after January 1, 2021.")


class DateRangeSchema(Schema):

    class Meta:
        unknown = 'exclude'

    from_date = fields.DateTime(required=True, validate=validate_date_range, format="%Y-%m-%d")
    to_date = fields.DateTime(required=True, validate=validate_date_range, format="%Y-%m-%d")


class PreBillingSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Integer(dump_only=True)
    billing_status = fields.Integer(dump_only=True)
    duration = fields.Integer(required=True)
    service_id = fields.Integer(required=True)
    participant_id = fields.Integer(required=True)
    log_id = fields.Integer(required=True)
    check_in_time = fields.DateTime()
    check_out_time = fields.DateTime()
    created_by = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class PreBillingViewSchema(Schema):

    id = fields.Integer(dump_only=True)
    billing_status = fields.Integer(dump_only=True)
    duration = fields.Integer(required=True)
    service_id = fields.Integer(required=True)
    participant_id = fields.Integer(required=True)
    log_id = fields.Integer(required=True)
    check_in_time = fields.DateTime()
    check_out_time = fields.DateTime()
    created_by = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    participant_name = fields.String(dump_only=True)
    service_name = fields.String(dump_only=True)


class PreBillingUpdateSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Integer(dump_only=True)
    billing_status = fields.Integer(dump_only=True)
    duration = fields.Integer(required=True)
    service_id = fields.Integer(required=True)
    participant_id = fields.Integer(required=True)
    log_id = fields.Integer(required=True)
    check_in_time = fields.DateTime()
    check_out_time = fields.DateTime()
    created_by = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class LogIdSchema(Schema):

    class Meta:
        unknown = 'exclude'

    duration = fields.Integer(required=True)
    log_id = fields.Int(required=True)
