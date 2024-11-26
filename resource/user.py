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
from schema import (AuthModelSchema, PlainUpdateWorkSpaceSchema,
                    PlainUserLoginSchema, PlainUserRegisterSchema,
                    PlainUserUpdateSchema, SuccessSchema)

blp = Blueprint("Users","user", description="CRUD operation with user" )

from block_list import BLOCKLIST


@blp.route("/register", strict_slashes=False)
class UserRegister(MethodView):
    @blp.arguments(PlainUserRegisterSchema, location="form")
    @blp.response(201, AuthModelSchema)
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
    @blp.arguments(PlainUserLoginSchema, location="form")
    @blp.response(200, AuthModelSchema, description="Response for admin")
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
    @blp.response(200, PlainUserRegisterSchema)
    def get(self):
        user_id = get_jwt_identity()
        user = UserModel.query.filter(UserModel.id == user_id).first()
        if user is not None:
            user.image = user.convert_image_to_link(route="/user/image/", image_id=user.id)
            return user
        else:
            abort(404, message="Invalid credentials.")

    @jwt_required()
    @blp.arguments(PlainUserUpdateSchema, location="form")
    @blp.response(200, PlainUserUpdateSchema)
    def put(self, user_data):
        user_id = get_jwt_identity()
        user = UserModel.query.filter(UserModel.id == user_id).first()
        if user is not None:
            if len(user_data) != 0:
                user_saved = user.update(**user_data)
                if user_saved:
                    return user
                abort(401, message="""an error accured while saving in db becuase of you want to save email or phone """)

            else:
                abort(401, message="Enter data to update ")
        else:
            abort(404, message="Invalid credentials.")
    
    @jwt_required(fresh=True)
    @blp.response(200, SuccessSchema)
    def delete(self):
        current_user_id = get_jwt_identity()
        user = UserModel.query.filter(UserModel.id ==current_user_id).first()
        if user is not None:
            user_deleted = user.delete()
            if user_deleted:
                
                return {
                    "code":200,
                    "message": "delete successfully",
                    "success": True}
            else:
                abort(500, message="error accured while deleteing user from db")       
        else:
            abort(404, message="user not found")       


    
    
@blp.route("/user/image/<string:user_id>")
class UserImage(MethodView):
    # @jwt_required()
    # def put(self):
    #     user_id = get_jwt_identity()
    #     user = UserModel.query.filter(UserModel.id == user_id).first()
    #     saved = user.save_image(request_data = request, folder_name="user_pics")
    #     if isinstance(saved, str):
    #         error_msg = saved
    #         abort(401, message = error_msg)
    #     user.save()
    #     return send_file(user.image,mimetype='image/jpeg' ,as_attachment=True)
    def get(self, user_id):
        # user_id = get_jwt_identity()
        print("hiii", user_id)
        user = UserModel.query.filter(UserModel.id == user_id).first()
        if user is not None:
            file = os.path.join(os.getcwd(),f"{user.image}")
            return send_file(file, mimetype='image/jpeg' )
        else:
            abort(404, message="image is not found")
            
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id, fresh=False)
   

        return jsonify(
            {
                "access_token":new_token,
            }
        ),201



@blp.route("/logout")
class Logout(MethodView):
    @jwt_required()
    @blp.response(200, SuccessSchema)
    def post(self):
        current_user_id = get_jwt_identity()
        refresh_token = create_refresh_token(current_user_id)
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {
            "code":200,
            "message": "logout successfully",
            "success": True}



