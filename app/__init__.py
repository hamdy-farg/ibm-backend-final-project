import os
from resource.user import blp as UserBluePrint

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from db import db
from models import AdminModel, ClientModel, RoleEnum, StatusEnum


class Config(object):
    PROPAGATE_EXCEPTION=True
    #flask smorest configuration
    API_TITLE = "UDEMY FLASK TEST"
    API_VERSION = "v1.0"
    OPENAPI_VERSION ='3.0.3'
    OPENAPI_URL_PREFIX =  "/"
    OPENAPI_SWAGGER_UI_PATH = '/swagger'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    #
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:0000@127.0.0.1:3306/bankdb1'
    SQLALCHEMY_TRACK_MODIFICATION = False
    #JWT config
    JWT_SECRET_KEY = "105119963872580105811750424767882539424"

def create_app():
    """" create app
        create all flask app config
    """
    app = Flask(__name__)
    #flask smores configuration
    app.config.from_object(Config)
    api = Api(app)

    app.has_initialized = False
    app.app_context().push()
    #
    api.register_blueprint(UserBluePrint)
    db.init_app(app)
    def create_tables():
        if not app.has_initialized:
            app.has_initialized = True 
            db.create_all()
    create_tables()
    return app
app = create_app()

jwt = JWTManager(app)

@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    client = ClientModel.query.filter(ClientModel.id == identity).first()
    if client is not None :
        if client.role == RoleEnum.client:
            return {"is_admin": False}
        else :
            return {"is_admin": True}
            
    admin = AdminModel.query.filter(AdminModel.id == identity).first()
    if client is not None :
        if admin.role == RoleEnum.admin:
            return {"is_admin": True}
        else :
            return {"is_admin":False}

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

...

