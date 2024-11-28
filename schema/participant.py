from marshmallow import Schema, fields


class ParticipantSchema(Schema):

    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    dob = fields.Str(required=True)
    ssn = fields.Str(required=True)
    maid_number = fields.Str(required=True)
    legal_status = fields.Str(required=True)
    address = fields.Str(required=True)
    address_2 = fields.Str(missing=None)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    zip_code = fields.Str(required=True)
    home_phone = fields.Str(required=True)
    gender_id = fields.Int(required=True)
    bio_title_id = fields.Int(required=True)
    profile_image = fields.Str(required=False)
