import os

from flask import jsonify, request
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
        if user_data.get("email_address") is not None:
            filtered_user = ClientModel.query.filter(ClientModel.email_address == user_data.get("email_address")).first()
            if filtered_user is not None:
                error_msg = "the email address is taken before"
                return jsonify({"message":error_msg}),401
            else:
                user.email_address =  user_data.get("email_address")

        if user_data.get("phone_number") is not None:
            phone_number = user_data.get("phone_number")
            if phone_number.isdigit():
                filtered_user = ClientModel.query.filter(ClientModel.phone_number == user_data.get("phone_number")).first()
                if filtered_user is not None:
                    error_msg = "the phone number is taken before type another one"
                    return jsonify({"message":error_msg}),401
                else:
                    user.phone_number = phone_number
            else:
                error_msg = "Invalid phone number"
                return jsonify({"message": error_msg})

        user.f_name = user_data.get("f_name")
        user.l_name = user_data.get("l_name")
        if error_msg is None and 'image' not in request.files:
            error_msg = "image missing"
        try:
            file = request.files["image"]
            if error_msg is None and file.filename == '':
                error_msg = "image not selected"
        except Exception as e:
            if error_msg is None:
                error_msg = "server error to upload"
        user.set_password(raw_password=user_data["password"])
        done = user.save()
        if error_msg is None:
            file_extenstion = file.filename.split(".")[-1]
            folder_path = f"{os.getcwd()}\\assets\\user\\user_pics\\"
            final_path = f"{os.getcwd()}\\assets\\user\\user_pics\\{user.id}.{file_extenstion}"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file.save(final_path)
        else: 
            return jsonify({"message": error_msg}),401
        
        if not done :
            return jsonify(
                {
                    "message": "an error accured while saving in database"
                },
                401
            )
        user.access_token = create_access_token(identity=user.id, fresh=True)
        user.refresh_token = create_refresh_token(user.id)

        return user








@blp.route("/login", strict_slashes=False)
class LoginUser(MethodView):
    @blp.arguments(PlainUserSchema, location="form")
    @blp.response(200, AdminSchema, description="Response for admin")
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