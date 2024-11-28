from datetime import datetime

from marshmallow import Schema, fields, ValidationError, pre_load


class BillingReportSchema(Schema):
    class Meta:
        unknown = 'exclude'
        fields = ("from_date", "to_date")

    from_date = fields.Date(
        required=True,
        description="Start of the time frame (format: YYYY-MM-DD)",
        example="2024-07-01",
    )
    to_date = fields.Date(
        required=True,
        description="End of the time frame (format: YYYY-MM-DD)",
        example="2024-07-31",
    )

    @pre_load
    def validate_dates(self, data, **kwargs):
        from_date_str = data.get('from_date')
        to_date_str = data.get('to_date')

        if not from_date_str:
            raise ValidationError("Missing data for required field: 'from_date'.")
        if not to_date_str:
            raise ValidationError("Missing data for required field: 'to_date'.")

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError("Dates must be in the format YYYY-MM-DD.")

        if from_date > to_date:
            raise ValidationError("'from_date' must be before 'to_date'.")

        return data


class BillingReportResponseSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Integer(dump_only=True)
    total_cost = fields.Float(required=True)
    total_duration = fields.Integer(required=True)
    service_id = fields.Integer(required=True)
    participant_id = fields.Integer(required=True)
    created_by = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
