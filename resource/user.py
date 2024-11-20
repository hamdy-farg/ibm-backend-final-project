import os
from typing import TypeVar

from flask import Response, jsonify, request
from flask.views import MethodView
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256

from models.user import AdminModel, ClientModel
from schema import AdminSchema, ClientSchema, PlainUserSchema

blp = Blueprint("Users","user", description="CRUD operation with user" )



@blp.route("/register", strict_slashes=False)
class UserRegister(MethodView):
    @blp.arguments(ClientSchema, location="form")
    @blp.response(201, ClientSchema)
    def post(self, user_data):
        error_msg = None
        user = ClientModel()
        
        validate = user.validate_user_data(user_data=user_data, request= request)
        if isinstance(validate, Response):

            return validate
        file = validate
        user = user.save_image(file)
        if  isinstance(user, Response):
            return user
        elif isinstance(user, ClientModel):
            user.access_token = create_access_token(identity=user.id, fresh=True)
            user.refresh_token = create_refresh_token(user.id)
            return user
        else:
            return user




@blp.route("/login", strict_slashes=False)
class LoginUser(MethodView):
    @blp.arguments(PlainUserSchema, location="form")
    @blp.response(200, ClientSchema, description="Response for admin")
    # @blp.alt_response(201, ClientSchema, description="Response for client")
    def post(self, user_data):

        user = ClientModel.query.filter(
            ClientModel.email_address == user_data["email_address"]
        ).first()
        if not user :
            user = AdminModel.query.filter(
            ClientModel.email_address == user_data["email_address"]
            ).first()
        # Verify user credentials
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # Create tokens
            user.access_token = create_access_token(identity=user.id, fresh=True)
            user.refresh_token = create_refresh_token(user.id)
            
            # Serialize response based on role
            if user.role == "admin":
                return AdminSchema().dump(user)  # Serialize using AdminSchema
            else:
                return ClientSchema().dump(user)  # Serialize using ClientSchema

        # Abort with 401 if credentials are invalid
        abort(401, message="Invalid credentials.")