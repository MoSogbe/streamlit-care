from datetime import datetime

from marshmallow import Schema, fields, validates_schema, ValidationError

from helper.utils import validate_email

class UserTypeSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    type_name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserTypeUpdateSchema(Schema):
    class Meta:
        unknown = 'exclude'

    type_name = fields.Str(required=True)


class UserSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class FetchUserSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    fullname = fields.Str(required=True)
    user_type = fields.Nested(UserTypeSchema)
    username = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserListSchema(Schema):
    class Meta:
        unknown = 'exclude'

    users = fields.Nested(FetchUserSchema, many=True)

class UserRegistersSchema(Schema):
    class Meta:
        unknown = 'exclude'

    fullname = fields.Str(required=True)
    email = fields.Str(required=True, validate=validate_email)
    username = fields.Str(required=True)
    user_type = fields.Str(required=True)
    password = fields.Str(required=True)



class ServiceCategorySchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    category_name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ServiceCategoryUpdateSchema(ServiceCategorySchema):
    class Meta:
        unknown = 'exclude'

    category_name = fields.Str(required=True)


class ServiceSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    service_name = fields.Str(required=True)
    service_price = fields.Str(required=True)
    service_charge_duration = fields.Str(required=True)
    service_charge_frequency = fields.Str(required=True)
    service_category = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ServiceUpdateSchema(Schema):
    class Meta:
        unknown = 'exclude'

    service_name = fields.Str(required=True)
    service_price = fields.Str(required=True)
    service_charge_duration = fields.Str(required=True)
    service_charge_frequency = fields.Str(required=True)
    service_category = fields.Str(required=True)


class UoMSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    unit_name = fields.Str(required=True)
    symbol = fields.Str(required=True)


class BStatusSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    status = fields.Str(required=True)


class MedicalConditionSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    condition_name = fields.Str(required=True)


class GenderSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class BioTitleSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    bio_name = fields.Str(required=True)


class StaffSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True, validate=validate_email)
    phone = fields.Str(required=True)
    address = fields.Str(required=True)
    address_2 = fields.Str(missing=None)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    zip_code = fields.Str(required=True)
    gender_id = fields.Int(required=True)
    bio_title_id = fields.Int(required=True)
    user_id = fields.Str(dump_only=True)
    profile_image = fields.Str(required=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class LocationSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    location_name = fields.Str(required=True)


class LocationUpdateSchema(Schema):
    class Meta:
        unknown = 'exclude'

    location_name = fields.Str(required=True)


class SchedulePeriodSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)


class SchedulePeriodUpdateSchema(Schema):
    class Meta:
        unknown = 'exclude'

    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)


class SchedulingSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    location_id = fields.Str(required=True)
    shift_period_id = fields.Str(required=True)
    patient_id = fields.Str(required=True)
    caregiver_id = fields.Str(required=True)
    scheduled_by = fields.Str(required=True)
    day_of_week = fields.Str(required=True)
    month = fields.Str(required=True)
    year = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class SchedulingReport(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    start_date = fields.Str(required=True)
    end_date = fields.Str(required=True)
    report_type = fields.Str(required=True)


class ParticipantServiceProviderHistorySchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Str(required=True)
    service_type_id = fields.Int(required=True)
    provider_name = fields.Str(required=True)
    provider_address = fields.Str(required=True)
    provider_phone = fields.Str(required=True)


class DiagnosisSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    axis_id = fields.Int(required=True)
    medical_condition_id = fields.Int(required=True)


class DiagnosisViewSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    medical_condition_id = fields.Int(required=True)
    condition_name = fields.Str(required=True)
    axis_name = fields.Str(required=True)
    created_by = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class MITSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    mit_name = fields.Str(required=True)


class MISchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    mit_id = fields.Int(required=True)
    participant_id = fields.Int(required=True)
    created_by = fields.Int(dump_only=True)
    medical_condition_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class MIViewSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    mit_id = fields.Int(required=True)
    participant_id = fields.Int(required=True)
    created_by = fields.Int(dump_only=True)
    medical_condition_id = fields.Int(required=True)
    condition_name = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ECISchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    created_by = fields.Int(dump_only=True)
    gaurdian_name = fields.Str(required=True)
    gaurdian_phone = fields.Str(required=True)
    gaurdian_address = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class CaseManagerSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    created_by = fields.Int(dump_only=True)
    cm_name = fields.Str(required=True)
    cm_phone = fields.Str(required=True)
    cm_emergency_phone = fields.Str(required=True)
    cm_address = fields.Str(required=True)
    cm_fax = fields.Str(required=True)
    cm_email_address = fields.Str(required=True, validate=validate_email)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PreferredHospitalSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    created_by = fields.Int(dump_only=True)
    ph_name = fields.Str(required=True)
    ph_address = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ParticipantsPhysicianSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    created_by = fields.Int(dump_only=True)
    physician_name = fields.Str(required=True)
    physician_phone = fields.Str(required=True)
    physician_address = fields.Str(required=True)


class DrugCategorySchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    drug_category_name = fields.Str(required=True)


class DrugSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    drug_category_id = fields.Str(required=True)
    brand_name = fields.Str(required=True)
    drug_name = fields.Str(required=True)
    generic_name = fields.Str(required=True)
    uom_id = fields.Str(required=True)


class SupplierSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    supplier_name = fields.Str(required=True)
    supplier_phone = fields.Str(required=True)
    supplier_address = fields.Str(required=True)
    supplier_contact_person = fields.Str(required=True)
    supplier_balance = fields.Str(required=True)


class StockSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    transaction_code = fields.Str(required=True)
    batch_code = fields.Str(required=True)
    supplier_id = fields.Str(required=True)
    drug_id = fields.Str(required=True)
    quantity_received = fields.Str(required=True)
    expiry_date = fields.Str(required=True)


class StockListSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    transaction_code = fields.Str(required=True)
    batch_code = fields.Str(required=True)
    supplier_id = fields.Str(required=True)
    drug_id = fields.Str(required=True)
    drug_name = fields.Str(required=True)
    quantity_received = fields.Str(required=True)
    expiry_date = fields.Str(required=True)


class StockTotalSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    total_qty = fields.Str(required=True)
    drug_id = fields.Str(required=True)


class BatchNumSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    batch_num = fields.Str(required=True)
    drug_id = fields.Str(required=True)


class ReportRequestSchema(Schema):
    class Meta:
        unknown = 'exclude'

    category_id = fields.Integer()
    product_id = fields.Integer()


class ReportResponseSchema(Schema):
    class Meta:
        unknown = 'exclude'

    category_id = fields.Integer()
    category_name = fields.String()
    product_id = fields.Integer()
    product_name = fields.String()
    total_stock = fields.Integer()


class InvoiceSpecificRequestSchema(Schema):
    class Meta:
        unknown = 'exclude'

    transaction_code = fields.String()


class InvoiceSpecificResponseSchema(Schema):
    class Meta:
        unknown = 'exclude'

    transaction_code = fields.String()
    batch_code = fields.String()
    quantity_received = fields.String()
    expiry_date = fields.DateTime()
    drug_name = fields.String()
    supplier_name = fields.String()
    supplier_phone = fields.String()
    supplier_address = fields.String()
    supplier_contact_person = fields.String()

class DossageSchema(Schema):
    dosage = fields.String(required=True)
    time = fields.String(required=True)


class PrescriptionSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    drug_id = fields.Int(required=True)
    reason_for_medication = fields.Str(required=True)
    mar_date = fields.Str(required=True)
    mar_time = fields.Str(required=True)
    date_from = fields.Str(required=True)
    date_to = fields.Str(required=True)
    place_of_mar = fields.Str(required=True)
    frequency = fields.Int(required=True)
    qty = fields.Int(required=True)
    todays_frequency = fields.Int(required=True)
    comment = fields.Str(required=True)
    Dossage = fields.List(fields.Nested(DossageSchema), required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PrescriptionUpdateSchema(Schema):
    class Meta:
        unknown = 'exclude'

    id = fields.Int(dump_only=True)
    participant_id = fields.Int(required=True)
    drug_id = fields.Int(required=True)
    reason_for_medication = fields.Str(required=True)
    mar_date = fields.Str(required=True)
    mar_time = fields.Str(required=True)
    date_from = fields.Str(required=True)
    date_to = fields.Str(required=True)
    place_of_mar = fields.Str(required=True)
    dossage = fields.Str(required=False)
    frequency = fields.Int(required=True)
    qty = fields.Int(required=True)
    comment = fields.Str(required=True)


class DateRangeSchema(Schema):
    class Meta:
        unknown = 'exclude'

    date_from = fields.Str()
    date_to = fields.Str()

    @validates_schema
    def validate_dates(self, data, **kwargs):
        date_format = '%Y-%m-%d'
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        if date_from and date_to:
            try:
                datetime.strptime(date_from, date_format)
                datetime.strptime(date_to, date_format)
            except ValueError:
                raise ValidationError("Invalid date format. Expected format: YYYY-MM-DD")

            if date_from > date_to:
                raise ValidationError("'date_from' must be earlier than 'date_to'")


class ServiceReportSchema(DateRangeSchema):
    class Meta:
        unknown = 'exclude'

    service_category_id = fields.Int(required=False)
    participant_id = fields.Int(required=False)
    service_id = fields.Int(required=False)


class MarReportSchema(DateRangeSchema):
    class Meta:
        unknown = 'exclude'

    participant_id = fields.Int(required=False)
    administered_by = fields.Int(required=False)
    administered = fields.Bool(required=False)
