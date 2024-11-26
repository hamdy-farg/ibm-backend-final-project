from datetime import datetime

from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required
from flask_smorest import Blueprint

from models import RoomModel, WorkSpaceModel
from schema import DATEFORMAT, TIMEFORMAT, PlainRoomSchema, RoomSchema

blp = Blueprint("Room", "room", description='CRUD on rooms')

@blp.route("/room")
class Room(MethodView):
    @jwt_required()
    @blp.arguments(PlainRoomSchema, location="form")
    @blp.response(201, PlainRoomSchema)
    def post(self, room_data):
        print("hellose")
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilage required")
        work_space_id = room_data.get("work_space_id")
        print(work_space_id)
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id == work_space_id).first()
        if work_space is None:
            abort(401, "this work space not found")
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
            print("room")
            return room
        else:
            return abort(404,message ="an error accured while saving user in db")
    @blp.arguments(RoomSchema,location="form")
    @blp.response(200, RoomSchema)
    def get(self, room_data):
        room = RoomModel.query.filter_by(RoomModel.id == room_data.get("room_id")).first()
        if room is not null:
            return room
        else:
            abort(404, "your room is not found")



