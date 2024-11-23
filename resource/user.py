import os
from typing import TypeVar

from flask import Response, jsonify, request, send_file
from flask.views import MethodView
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256

from models.enum import RoleEnum
from models.user import UserModel
from schema import (AdminSchema, ClientSchema, PlainUserLoginSchema,
                    PlainUserRegisterSchema, PlainUserUpdateSchema)

blp = Blueprint("Users","user", description="CRUD operation with user" )

from block_list import BLOCKLIST


@blp.route("/register", strict_slashes=False)
class UserRegister(MethodView):
    @blp.arguments(PlainUserRegisterSchema, location="form")
    @blp.response(201, PlainUserRegisterSchema)
    def post(self, user_data):
        error_msg = None
        user = UserModel()
      
        validate = user.validate_user_data(user_data=user_data, request= request)
        if validate  is not None and isinstance(validate, str):
            error_msg = validate
            return abort(401, message = error_msg)

        user = validate
        # user = user.save_image(request_data= request)
        if  isinstance(user, str):
            error_msg = user
            return abort(401, message=error_msg)
        elif isinstance(user, UserModel):
            user.access_token = create_access_token(identity=user.id, fresh=True)
            user.refresh_token = create_refresh_token(user.id)
            user_saved = user.save()
            if user_saved:
                return user
            else:
                return abort(401,message ="an error accured while saving user in db")
            
        else:
            return user




@blp.route("/login", strict_slashes=False)
class LoginUser(MethodView):
<<<<<<< HEAD
    @blp.arguments(PlainUserLoginSchema, location="form")
    @blp.response(200, PlainUserLoginSchema, description="Response for admin")
=======
    @blp.arguments(PlainUserSchema, location="form")
    @blp.response(200, AdminSchema, description="Response for admin")
    # @blp.alt_response(201, ClientSchema, description="Response for client")
>>>>>>> development
    def post(self, user_data):

        user = UserModel.query.filter(
            UserModel.email_address == user_data["email_address"]
        ).first()

        # Verify user credentials
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # Create tokens
            user.access_token = create_access_token(identity=user.id, fresh=True)
            user.refresh_token = create_refresh_token(user.id)
            if user.role == RoleEnum.admin:
                return user # Serialize using AdminSchema
            else:
                return user # Serialize using ClientSchema
        abort(404, message="Invalid credentials.")

@blp.route("/user")
class User(MethodView):
    @jwt_required()
    # @blp.response(200, ClientSchema)
    def get(self):
        user_id = get_jwt_identity()

        user = UserModel.query.filter(UserModel.id == user_id).first()
        if user is not None:
            if user.role == RoleEnum.admin:
                return AdminSchema().dump(user)
            else:
                return ClientSchema().dump(user)
        else:
            abort(404, message="Invalid credentials.")

    @jwt_required()
    @blp.arguments(PlainUserUpdateSchema, location="form")
    @blp.response(200, PlainUserUpdateSchema)
    def put(self, user_data):
        user_id = get_jwt_identity()
        user = UserModel.query.filter(UserModel.id == user_id).first()
        print(user_data)
        if user is not None:
            if len(user_data) != 0:
                user.update(**user_data)
                return user
            else:
                abort(401, message="Enter data to update ")
        else:
            abort(404, message="Invalid credentials.")
    
@blp.route("/user/image")
class UserImage(MethodView):
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter(UserModel.id == user_id).first()
        saved = user.save_image(request_data = request, folder_name="user_pics")
        if isinstance(saved, str):
            error_msg = saved
            abort(401, message = error_msg)
        user.save()
        return send_file(user.image,mimetype='image/jpeg' ,as_attachment=True)
    
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter(UserModel.id == user_id).first()
        if user is not None:
            return send_file(user.image,mimetype='image/jpeg' ,as_attachment=True)
        else:
            abort(404, message="image is not found")
            
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id, fresh=False)
        refresh_token = create_refresh_token(current_user_id)
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)

        return jsonify(
            {
                "access_token":new_token,
                "refresh_token": refresh_token
            }
        ),201

    

