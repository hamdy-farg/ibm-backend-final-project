import os
from resource.room import blp as RoomBluePrint
from resource.user import blp as UserBluePrint
from resource.work_space import blp as WorkSpaceBluePrint

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from block_list import BLOCKLIST
from db import db
from models import RoleEnum, StatusEnum, UserModel


class Config(object):
    PROPAGATE_EXCEPTION=True
    #flask smorest configuration
    API_TITLE = "UDEMY FLASK TEST"
    API_VERSION = "v1.0"
    OPENAPI_VERSION ='3.0.3'
    OPENAPI_URL_PREFIX =  "/"
    OPENAPI_SWAGGER_UI_PATH = '/swagger'
    OPENAPI_SWAGGER_UI_URL = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/' 
    #'mysql://avnadmin:AVNS_JwDR53p0C_FqW-lxnmo@mysql-9922e3a-farghamdy72-61e3.b.aivencloud.com:25133/defaultdb'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:0000@127.0.0.1:3306/bankdb1'
    SQLALCHEMY_TRACK_MODIFICATION = False
    #JWT config
    JWT_SECRET_KEY = "105119963872580105811750424767882539424"
    # SQLALCHEMY_ENGINE_OPTIONS = {
    #     'connect_args': {
    #         'ssl': {
    #             'ssl_ca': "C:\\Users\\spider\\Desktop\\IBM_BACKEND_PROJECT\\ca.pem"  
    #         }
    #     }
    # }

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
    api.register_blueprint(WorkSpaceBluePrint)
    api.register_blueprint(RoomBluePrint)


    
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
    user = UserModel.query.filter(UserModel.id == identity).first()
    if user is not None :
        if user.role == RoleEnum.client:
            return {"is_admin": False}
        else :
            return {"is_admin": True}
            
 

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

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "description": "The token is not fresh.",
                "error": "fresh_token_required",
            }
        ),
        401,
    )
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payloud):
    jti = jwt_payloud["jti"]
    print(BLOCKLIST)
    return jti in BLOCKLIST