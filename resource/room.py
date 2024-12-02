import os
from datetime import datetime

from flask import request, send_file
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint, abort

from models import BookModel, RoomModel, WorkSpaceModel
from schema import (DATEFORMAT, TIMEFORMAT, PlainRoomSchema, RoomSchema,
                    RoomsSchema, RoomUpdateSchema, SuccessSchema)

blp = Blueprint("Room", "room", description='CRUD on rooms')

@blp.route("/room")
class Room(MethodView):
    @jwt_required()
    @blp.arguments(PlainRoomSchema, location="form")
    @blp.response(201, PlainRoomSchema)
    def post(self, room_data):
        room_exists = RoomModel.query.filter(RoomModel.title == room_data.get("title")).first()
        print(room_exists)
        if room_exists is not None:
            abort(400, message='this title is exists before choose another one')
        print("hellose")
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilage required")
        work_space_id = room_data.get("work_space_id")
        print(work_space_id)
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id == work_space_id).first()
        if work_space is None:
            abort(401,message= "this work space not found")
        start_date = room_data.get("start_date")
        end_date = room_data.get("end_date")
        start_time = room_data.get("start_time")
        end_time = room_data.get("end_time")     
        title =  room_data.get("title")   
        description = room_data.get("description")
        price_per_hour =  room_data.get("price_per_hour")
        capacity = room_data.get("capacity")

        #
        if (start_date is not None
        and end_date is not None 
        and start_date is not None
        and end_date is not None) :
            try:
                start_date = datetime.strptime(start_date, DATEFORMAT)
                end_date  = datetime.strptime(end_date, DATEFORMAT)
                start_time = datetime.strptime(start_time, TIMEFORMAT)
                end_time  = datetime.strptime(end_time, TIMEFORMAT)
            except Exception as e:
                abort(401, message="you have to send good formate date and time ")
        
        #
        room = RoomModel(
            workSpace = work_space,
            description = description,
            start_date = start_date.date(),
            end_date = end_date.date(),
            start_time = start_time.time(),
            end_time = end_time.time(),
            title = title,
            capacity = capacity,
            price_per_hour = price_per_hour
        )      
        #
        room_image_saved = room.save_image(request_data=request, folder_name="room_pics")
        if  isinstance(room_image_saved, str):
            error_msg = room_image_saved
            abort(4014 , message= error_msg)
        room_is_save = room.save()
        if room_is_save:
            room.image =room.convert_image_to_link(route="/room/image/", image_id=room.id)
            #f"{os.getenv("LOCALHOST","http://127.0.0.1:5000/")}"+ "room/image/"+f"{room.id}"
            return room
        else:
            return abort(404,message ="an error accured while saving user in db")
    
    @blp.arguments(RoomSchema, location="form")
    @blp.response(200, PlainRoomSchema)
    def get(self, room_data):

        room = RoomModel.query.filter(RoomModel.id == room_data.get("room_id")).first()
        if room is not None:
            room.image = room.convert_image_to_link(route="/room/image/", image_id=room.id)
            #f"{os.getenv("LOCALHOST","http://127.0.0.1:5000/")}"+ "room/image/"+f"{room.id}"
            return room
        else:
            abort(404, "your room is not found")


    @jwt_required()
    @blp.arguments(RoomUpdateSchema, location="form")
    @blp.response(200, PlainRoomSchema)
    def put(self, room_data):
        """ to update one room by id"""
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(400, message= "admin provilage are required")
        room = RoomModel.query.filter(RoomModel.id == room_data.get("room_id")).first()
        if room is None:
            abort(404, "your room is not found")
        saved = room.save_image(request_data = request, folder_name="room_pics")
        if isinstance(saved, str):
            error_msg = saved
            abort(401, message = error_msg)
        room.save()
        room.update(**room_data)
        if room is not None:
            room.image = room.convert_image_to_link(route="/room/image/",iamge_id = room.id)
            return room
       
    @blp.arguments(RoomSchema, location="form")
    @blp.response(200, SuccessSchema)
    def delete(self, room_data):
        """ delete specific work space"""
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(400, message= "admin provilage are required")
        room = RoomModel.query.filter(RoomModel.id == room_data.get("room_id")).first()
        if room is not None:
            room_deleted = room.delete()
            if  room_deleted:
                return {
                    "code": 200,
                    "message": "deleted",
                    "success" : True
                }
            else :
                return abort(200, message = "problem accured in server while deleteing")
        else:
            abort(404, message = "your room is not found")
 


@blp.route('/workspace/rooms')
class GetAllWorkSpaceRoom(MethodView):
    @blp.arguments(RoomsSchema, location="form")
    @blp.response(200, RoomsSchema)
    def post(self, room_data):
            """ to get work space rooms"""
            workSpace   = WorkSpaceModel.query.filter(WorkSpaceModel.id == room_data.get("work_space_id")).first()
            RoomsList = []
            if workSpace is not None:
                workSpaceRoomsList =  workSpace.rooms
                print(workSpaceRoomsList)
                for workSpaceRoom in workSpaceRoomsList:
                    workSpaceRoom.image =workSpaceRoom.convert_image_to_link(route="/room/image/", image_id=workSpaceRoom.id)
                    #f"{os.getenv("LOCALHOST","http://127.0.0.1:5000/")}"+ "room/image/"+f"{workSpaceRoom.id}"
                    RoomsList.append(workSpaceRoom)
                return {"work_space_id":workSpace.id,"rooms":RoomsList}
            abort(404,message =  "your work space is not found")


       
@blp.route("/room/image/<string:room_id>")
class RoomImage(MethodView):
    """ to provide image end point to display image"""
    def get(self, room_id):
        room = RoomModel.query.filter(RoomModel.id == room_id).first()
        image = os.path.join(os.getcwd(),"assets", "user","room_pics", room.image)
        return send_file(image, mimetype='image/jpeg')