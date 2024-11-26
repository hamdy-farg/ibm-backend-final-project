import os
import uuid

from flask import jsonify, request, send_file
from flask.views import MethodView
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort

from models.user import UserModel
from models.work_space import WorkSpaceModel
from schema import PlainWorkSpaceImagesSchema, PlainWorkSpaceSchema

blp = Blueprint("workspace", "workspace", description="CRUD operation on workspace")

@blp.route("/workspace", strict_slashes=False)
class WorkSpcae(MethodView):
    @jwt_required()
    @blp.arguments(PlainWorkSpaceSchema, location="form")
    @blp.response(201, PlainWorkSpaceSchema)
    def post(self, work_space_data):
        print("ernter")
        jwt = get_jwt()
       
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilage required")
        owner_id = get_jwt_identity()
        owner = UserModel.query.filter(UserModel.id == owner_id).first()
        work_space = WorkSpaceModel(**work_space_data, owner = owner)
    
        work_space_image_saved = work_space.save_image(request_data=request, folder_name="work_space_pics")
        if  isinstance(work_space_image_saved, str):
            error_msg = work_space_image_saved
            abort(401 , message= error_msg)
        work_space_saved = work_space.save()
        if work_space_saved:
                return work_space
        else:
            return abort(401,message ="an error accured while saving user in db")

    
@blp.route("/workspace/image/<string:work_space_id>", strict_slashes=False)
class WorkSpaceImages(MethodView):
    # @jwt_required()
    # @blp.arguments(PlainWorkSpaceImagesSchema)
    def get(self, work_space_id):
        # owner_id = get_jwt_identity()
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id == work_space_id).first()

        if work_space is not None:
            imageName = os.path.join(os.getcwd(),work_space.image)
            return send_file(imageName, mimetype='image/jpeg')
        return jsonify({"": ""})
    