import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_smorest import Api
from sqlalchemy import create_engine

from blocklist import BLOCKLIST
from db import db
from resources.administrative_documentation import blp as AdminDocumentationBluePrint
from resources.appointments import blp as AppointmentsBlueprint
from resources.axis import blp as AxisBlueprint
from resources.behavioral_issues import blp as BehavioralIssuesBlueprint
from resources.billing import blp as BillingBlueprint
from resources.billing_summary import blp as BillingSummaryBlueprint
from resources.bio_title import blp as BTitleBlueprint
from resources.care_givers import blp as StaffBlueprint
from resources.case_manager import blp as CaseManagerBlueprint
from resources.company import blp as CompanyBlueprint
from resources.daily_notes import blp as DailyNoteBluePrint
from resources.diagnosis import blp as DiagnosisBlueprint
from resources.document_type import blp as DocumentTypeBlueprint
from resources.drug_category import blp as DrugCategoryBlueprint
from resources.drugs import blp as DrugBlueprint
from resources.eci import blp as ECIBlueprint
from resources.gender import blp as GenderBlueprint
from resources.life_Story import blp as LifeStoryBluePrint
from resources.locations import blp as LocationBlueprint
from resources.log_entry import log_entry_blp as LogEntryBluePrint
from resources.mar_alerts import blp as MARAlertsBlueprint
from resources.med_action_status import blp as MedActionStatusBlueprint
from resources.med_error import blp as MedErrorBlueprint
from resources.medical_condition import blp as MedicalConditionBlueprint
from resources.medical_information import blp as MedicalInformationBlueprint
from resources.participant_documentation import blp as ParticipantDocumentation
from resources.participant_life_story import blp as ParticipantLifeStoryBluePrint
from resources.participant_objectives import blp as ParticipantObjectivesBlueprint
from resources.participant_physician import blp as PPBlueprint
from resources.participant_service_provider_history import blp as PSPHBlueprint
from resources.participants import blp as ParticipantBlueprint
from resources.pre_billing import blp as PreBillingBlueprint
from resources.preferred_hospital import blp as PHBlueprint
from resources.prescription import blp as PrescriptionBlueprint
from resources.progress import blp as ProgressBlueprint
from resources.progress_analysis import blp as ProgressAnalysisBlueprint
from resources.report import blp as ReportBlueprint
from resources.schedule_periods import blp as SPBlueprint
from resources.scheduling import blp as SchedulingBlueprint
from resources.service_category import blp as ServiceCategoryBlueprint
from resources.services import blp as ServicesBlueprint
from resources.stock_management import blp as StockMgmtBlueprint
from resources.supplier import blp as SupplierBlueprint
from resources.uom import blp as UOMBlueprint
from resources.user_types import blp as UserTypeBlueprint
from resources.users import blp as UserBlueprint
from resources.vitals import blp as VitalsBlueprint
from resources.main_reports import blp as ReportsBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()
    CORS(app)
    app.config["API_TITLE"] = "HomeCare API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.debug = True
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)
    app.config["JWT_SECRET_KEY"] = "brownfoxjumponthewall"
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 36000
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has beed revoked", "error": "token_revoked"}
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token is not fresh", "error": "fresh_tokn_required"}
            ),
            401,
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @app.route("/")
    def index():
        return jsonify({"message": "Welcome to HomeCare API"})

    api.register_blueprint(UserTypeBlueprint)
    api.register_blueprint(CompanyBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ServiceCategoryBlueprint)
    api.register_blueprint(ServicesBlueprint)
    api.register_blueprint(UOMBlueprint)
    api.register_blueprint(MedicalConditionBlueprint)
    api.register_blueprint(GenderBlueprint)
    api.register_blueprint(BTitleBlueprint)
    api.register_blueprint(LocationBlueprint)
    api.register_blueprint(SPBlueprint)
    api.register_blueprint(StaffBlueprint)
    api.register_blueprint(ParticipantBlueprint)
    api.register_blueprint(PSPHBlueprint)
    api.register_blueprint(DiagnosisBlueprint)
    api.register_blueprint(MedicalInformationBlueprint)
    api.register_blueprint(PPBlueprint)
    api.register_blueprint(PHBlueprint)
    api.register_blueprint(ECIBlueprint)
    api.register_blueprint(CaseManagerBlueprint)
    api.register_blueprint(LifeStoryBluePrint)
    api.register_blueprint(SchedulingBlueprint)
    api.register_blueprint(SupplierBlueprint)
    api.register_blueprint(DrugCategoryBlueprint)
    api.register_blueprint(DrugBlueprint)
    api.register_blueprint(StockMgmtBlueprint)
    api.register_blueprint(PrescriptionBlueprint)
    api.register_blueprint(VitalsBlueprint)
    api.register_blueprint(DailyNoteBluePrint)
    api.register_blueprint(LogEntryBluePrint)
    api.register_blueprint(ParticipantLifeStoryBluePrint)
    api.register_blueprint(AxisBlueprint)
    api.register_blueprint(DocumentTypeBlueprint)
    api.register_blueprint(ParticipantDocumentation)
    api.register_blueprint(AdminDocumentationBluePrint)
    api.register_blueprint(MedActionStatusBlueprint)
    api.register_blueprint(MedErrorBlueprint)
    api.register_blueprint(AppointmentsBlueprint)
    api.register_blueprint(BehavioralIssuesBlueprint)
    api.register_blueprint(ProgressBlueprint)
    api.register_blueprint(ProgressAnalysisBlueprint)
    api.register_blueprint(ReportBlueprint)
    api.register_blueprint(ParticipantObjectivesBlueprint)
    api.register_blueprint(PreBillingBlueprint)
    api.register_blueprint(BillingBlueprint)
    api.register_blueprint(BillingSummaryBlueprint)
    api.register_blueprint(MARAlertsBlueprint)
    api.register_blueprint(ReportsBlueprint)

    return app
