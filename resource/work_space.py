import uuid

from flask import jsonify, request
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
    
        work_space_photos = {}
        photos = request.files.getlist("image")
        if photos is not None:

            for i in range(len(photos)):
                checked = work_space.check_image(file=photos[i])
                if isinstance(checked, str):
                    error_msg = checked
                    abort (401, message=error_msg) 

            for i in range(len(photos)):
                work_space_image_saved = work_space.save_image(file=photos[i], folder_name="work_space_pics")
                if  isinstance(work_space_image_saved, str):
                    error_msg = work_space_image_saved
                    abort(401 , message= error_msg)
                else:
                    print(type(work_space.photos))
                    image_id = uuid.uuid4().hex
                    work_space_photos[image_id] = {
                        f"image": 
                        work_space_image_saved.image,
                       } 

            work_space.photos = work_space_photos

        work_space.save()
        return work_space
@blp.route("/workspace/images", strict_slashes=False)
class WorkSpaceImages(MethodView):
    @jwt_required()
    # @blp.arguments(PlainWorkSpaceImagesSchema)
    def get(self):
        owner_id = get_jwt_identity()
        print(owner_id)
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.owner_id == owner_id).first()

        if work_space is not None:
            return jsonify({"phots":work_space.photos})
        return jsonify({"": ""})
    