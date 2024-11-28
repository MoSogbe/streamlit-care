from marshmallow import Schema, fields
from helper.utils import validate_email
class CompanySchema(Schema):

    class Meta:
        unknown = 'exclude'
    
    id = fields.Int(dump_only=True)
    name_of_company = fields.Str(required=True)
    email = fields.Str(required=True,  validate=validate_email)
    phone_number = fields.Str(required=True)
    suite_unit = fields.Str(missing=None)
    logo_path = fields.Str(required=False)
    address = fields.Str(required=True)
    address_2 = fields.Str(missing=None)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    zip_code = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
