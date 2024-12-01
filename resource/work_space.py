import os
import uuid

from flask import jsonify, request, send_file
from flask.views import MethodView
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort

from models import RoleEnum, UserModel, WorkSpaceModel
from schema import (PlainGetWorkSpace, PlainUpdateWorkSpaceSchema,
                    PlainWorkSpaceSchema, SuccessSchema, WorkSpaceSchema)

blp = Blueprint("workspace", "workspace", description="CRUD operation on workspace")

@blp.route("/workspace", strict_slashes=False)
class WorkSpcae(MethodView):
    @jwt_required()
    @blp.arguments(PlainWorkSpaceSchema, location="form")
    @blp.response(201, PlainWorkSpaceSchema)
    def post(self, work_space_data):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilage required")
        owner_id = get_jwt_identity()
        workspaceTitle = WorkSpaceModel.query.filter(WorkSpaceModel.title == work_space_data.get("title")).first()
        if workspaceTitle is None:
            abort (400 , message="this work space title is taken before choose another one")

        owner = UserModel.query.filter(UserModel.id == owner_id).first()

        work_space = WorkSpaceModel(**work_space_data, owner = owner)

        work_space_image_saved = work_space.save_image(request_data=request, folder_name="work_space_pics")

        if  isinstance(work_space_image_saved, str):
            error_msg = work_space_image_saved
            abort(401 , message= error_msg)

        work_space_saved = work_space.save()            
        if work_space_saved:

                work_space.image = work_space.convert_image_to_link(route="/workspace/image/", image_id =work_space.id)
                return work_space
        else:
            return abort(401,message ="an error accured while saving user in db")

    
    @jwt_required()
    @blp.arguments(PlainUpdateWorkSpaceSchema, location="form")
    @blp.response(200, PlainUpdateWorkSpaceSchema)
    def put(self, work_space_data):
        user = get_jwt_identity()
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilage required")
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id == work_space_data.get("work_space_id")).first()
        if request.files["image"] is not None:
            work_space_saved = work_space.save_image(folder_name='user/work_space_pics', request_data = request)
            if isinstance(work_space_saved,str):
                error_message = work_space_saved 
                abort(500, message= error_message)
        work_space_saved = work_space.update(**work_space_data)
        if work_space_saved:
            work_space.image = work_space.convert_image_to_link(route='/workspace/image/', image_id =work_space.id)
            return work_space
        else:
            abort(500, message="error accured while updating in db")

    
    @jwt_required()
    @blp.arguments(PlainGetWorkSpace, location="form")
    @blp.response(200, PlainUpdateWorkSpaceSchema)
    def get(self, work_space_data):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilage required")
        work_space_id = work_space_data.get("work_space_id")
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id == work_space_id).first()
        work_space.image = work_space.convert_image_to_link(route = '/workspace/image/', image_id =work_space.id)
        return work_space


    @jwt_required()
    @blp.arguments(PlainGetWorkSpace, location="form")
    @blp.response(200, SuccessSchema)
    def delete(self, work_space_data):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilage required")
        work_space_id = work_space_data.get("work_space_id")
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id == work_space_id).first()
        work_space_deleted = work_space.delete()
        if work_space_deleted:
            return {
                "code":200,
                "message": "deleted successfully",
                "success":True
            }
        else:
            abort(500, messsage="error accured while saving in db")

    




@blp.route("/workspace/image/<string:work_space_id>", strict_slashes=False)
class WorkSpaceImages(MethodView):
    def get(self, work_space_id):
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id == work_space_id).first()
        if work_space is not None:
            print(work_space.image)
            imageName = os.path.join(os.getcwd(),"assets","user", "work_space_pics",work_space.image)
            return send_file(imageName, mimetype='image/jpeg')
        return jsonify({"": ""})





@blp.route("/client/workspaces", strict_slashes=False)
class UserWorkSpaces(MethodView):
    @blp.response(200, WorkSpaceSchema)
    def get(self):
        # user_id = get_jwt()
        # if jwt.get("is_admin"):
        #     abort(401, message="client privilage required")
        work_spaces = None
        try:
            work_spaces = WorkSpaceModel.query.all()
        except Exception as e:
            pass
        #
        workSpaceList = []
        if work_spaces is not None:
            for work_space in work_spaces:
                work_space.image = work_space.convert_image_to_link(route='/workspace/image/', image_id =work_space.id)
                workSpaceList.append(work_space)
            return {"workSpaces":workSpaceList, }
        return jsonify({"data": "there is not work space created until now"})
    
     

@blp.route("/admin/workspaces", strict_slashes=False)
class UserWorkSpaces(MethodView):
    @jwt_required()
    @blp.response(200, WorkSpaceSchema)
    def get(self):
        user_id = get_jwt_identity()
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilage required")
        admin = UserModel.query.filter(UserModel.id == user_id, UserModel.role == RoleEnum.admin).first()
        #
        work_spaces = None
        try:
            work_spaces = admin.workSpaces.all()
        except Exception as e:
            pass
        workSpaceList = []
        if work_spaces is not None:
            for work_space in work_spaces:
                work_space.image = work_space.convert_image_to_link(route='/workspace/image/', image_id =work_space.id)
                workSpaceList.append(work_space)
            return {"workSpaces":workSpaceList}
        return jsonify({"data": "there is not work space created until now"})
    
     