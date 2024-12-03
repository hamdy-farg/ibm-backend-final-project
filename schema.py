import datetime
import os
import re

from flask_smorest import abort
from marshmallow import Schema, ValidationError, fields, validates
from werkzeug.utils import secure_filename

from models import WorkSpaceModel
from models.enum import RoleEnum, StatusEnum

TIMEFORMAT = "%H:%M:%S"
DATEFORMAT =  "%Y-%m-%d"
class PlainWorkSpaceSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    location = fields.Str(required=True)
    id = fields.Str(dump_only=True)
    image = fields.Str(dump_only=True)

    @validates("title")
    def validate_title(self, value):
        """Validate Title and last name."""
        
        if len(value) <= 2  or len(value) > 50:
            abort(400,message= "Title must be between 2 and 50 characters long.")
    
    @validates("description")
    def validate_description(self, value):
        """Validate Title and last name."""
        if len(value) < 20 or len(value) > 500:
            abort(400 ,message= "Name must be between 20 and 500 characters long.")
        
    @validates("location")
    def validate_location(self, value):
        if len(value) < 20:
            abort(400, message="this is not valid location")
        
class PlainGetWorkSpace(Schema):
    work_space_id = fields.Str(required=True)

    @validates("work_space_id")
    def validate_work_space_id(self, value):
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id == value).first()
        if work_space is None:
            abort(400, message="your workspace is not found")
        
class PlainUpdateWorkSpaceSchema(PlainWorkSpaceSchema):
    work_space_id = fields.Str(required=True)
    title = fields.Str()
    description = fields.Str()
    location = fields.Str()
    image = fields.Field()

    @validates("work_space_id")
    def validate_work_space_id(self, value):
        work_space = WorkSpaceModel.query.filter(WorkSpaceModel.id ==value).first()
        if work_space is None:
            abort(400, message="this id is not found")
        


class PlainRoomSchema(Schema):
    id = fields.Str(dump_only=True)
    work_space_id = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    price_per_hour = fields.Float(required=True)
    capacity = fields.Int(required=True)
    start_date = fields.Str(required=True)
    end_date = fields.Str(required=True)
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)
    image = fields.Str(dump_only=True)


    @validates("sart_date")
    @validates("end_date")
    def validate_date(self, value:str):
        """Validate Start Date and end Date"""
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
        except Exception as e:
            abort(400, message="you must send date with formate of year-month-day") 
    #
    @validates("start_time")
    @validates("end_time")
    def validate_date(self, value:str):
        """Validate Start Date and end Date"""
        try:
            datetime.datetime.strptime(value, "%H:%M:%S")
        except Exception as e:
             abort(400, message="you must send time with formate of hour:month:seconds") 
    @validates("title")
    def validate_title(self, value):
        """Validate Title and last name."""
       
        if len(value) <= 2 or len(value) > 50:
            abort(400, message="Title must be between 2 and 50 characters long.")
    
    @validates("description")
    def validate_description(self, value):
        """Validate Title and last name."""
        if len(value) < 20 or len(value) > 500:
            abort(400, message="Name must be between 20 and 500 characters long.")
    
    @validates("start_date")
    def validate_description(self, value):
        """Validate Start Date and last name."""
        start_date = datetime.datetime.strptime(value, DATE_STAMP).date()
        print(start_date)
        if not start_date:
            abort(400, message="you have to enter correct start date")
    @validates("capacity")
    def validate_description(self, value):
        """Validate capacity."""
        try:
            price = int(value)
        except Exception as e:
            abort(400, message="you must send capacity in integer formate")
   
        
class RoomSchema(Schema):
    room_id = fields.Str(required=True)
class RoomsSchema(Schema):
    work_space_id =fields.Str(required=True)
    rooms = fields.List(fields.Nested(PlainRoomSchema),dump_only=True)
class RoomUpdateSchema(PlainRoomSchema):
    room_id = fields.Str(required=True)
    work_space_id = fields.Str()
    title = fields.Str()
    description = fields.Str()
    price_per_hour = fields.Float()
    capacity = fields.Int()
    start_date = fields.Str()
    end_date = fields.Str()
    start_time = fields.Str()
    end_time = fields.Str()
   

class AuthModelSchema(Schema):
    access_token = fields.Str(dump_only=True)
    refresh_token = fields.Str(dump_only=True)
class PlainUserLoginSchema(Schema):
    id = fields.Str(dump_only=True)
    email_address = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    access_token = fields.Str(dump_only=True)
    refresh_token = fields.Str(dump_only=True)
    role = fields.Enum(enum= RoleEnum, dump_only=True)


    @validates("email_address")
    def validate_email(self, value):
        """Validate the email address format."""
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            abort(400, message="Invalid email address format.")
    
    @validates("password")
    def validate_password(self, value):
        """Validate the password for strength."""
        if len(value) < 8 or len(value) > 32:
            abort(400, message="Password must be between 8 and 32 characters long.")
        if not any(char.isdigit() for char in value):
            abort(400, message="Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            abort(400, message="Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            abort(400, "Password must contain at least one lowercase letter.")
        if not any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in value):
            abort(400, message="Password must contain at least one special character.")
           
class PlainUserRegisterSchema(PlainUserLoginSchema):
    id = fields.Str(dump_only=True)
    f_name = fields.Str(required=True)
    l_name = fields.Str(required=True)
    phone_number = fields.Str(dump_only=True)
    secret = fields.Str()
    image = fields.Str(dump_only=True)
    
    @validates("f_name")
    @validates("l_name")
    def validate_name(self, value):
        """Validate first and last name."""
        if len(value) < 2 or len(value) > 50:
            abort(400, message="Name must be between 2 and 50 characters long.")

class SuccessSchema(Schema):
    code = fields.Str(required=True, description="Success code")
    message = fields.Str(required=True, description="Success message")
    success = fields.Bool(required=True, description="Indicates the success status")
class PlainUserUpdateSchema(Schema):
    f_name = fields.Str()
    l_name = fields.Str()
    email_address = fields.Str()
    phone_number = fields.Str()
    image = fields.Str()

    @validates("email_address")
    def validate_email(self, value):
        """Validate the email address format."""
        if len(value) != 0 and value != "":
            email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_regex, value):
                abort(400, message="Invalid email address format.")

    @validates("f_name")
    @validates("l_name")
    def validate_name(self, value):
        """Validate first and last name."""

        if len(value) != 0  and value != "":
            if len(value) < 2 or len(value) > 50:
                abort(400, message="Name must be between 2 and 50 characters long.")


class PlainBookedSchema(Schema):
    id = fields.Str(dump_only=True)
    client_id = fields.Str(required=True)
    room_id = fields.Str(required=True)
    price = fields.Float(required=True)
    date =  fields.Str(required=True)
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)
    status = fields.Enum(enum=StatusEnum)

   
    @validates("date")
    def validate_date(self, value:str):
        """Validate Start Date and end Date"""
        try:
            datetime.datetime.strptime(value, "%Y-%m-%d")
        except Exception as e:
            abort(400, message="you must send date with formate of year-month-day") 
    #
    @validates("start_time")
    @validates("end_time")
    def validate_date(self, value:str):
        """Validate Start Date and end Date"""
        try:
            datetime.datetime.strptime(value, "%H:%M:%S")
        except Exception as e:
            abort(400, message="you must send time with formate of hour:month:seconds") 
    
    @validates("price")
    def validate_description(self, value):
        """Validate price per hour."""
        try:
            price = float(value)
        except Exception as e:
            abort(400, message="you must send price in flaot formate")
class BookUpdateSchema(PlainBookedSchema):
    book_id = fields.Str(required=True)
    client_id = fields.Str(dump_only=True)#!
    room_id = fields.Str(dump_only=True)#!
class BookDeleteSchema(Schema):
    book_id = fields.Str(required=True)

class PlainBookingsSchema(Schema):
    id = fields.Str(dump_only=True)
    client_id = fields.Str(required=True)
    room_id = fields.Str(required=True)
    price = fields.Float(required=True)
    date =  fields.Str(required=True)
    start_time = fields.Str(required=True)
    end_time = fields.Str(required=True)
    status = fields.Enum(enum=StatusEnum)
    room_image = fields.Str(dump_only=True)
class BookListSchema(Schema):
    room_id = fields.Str(required=True)
    roomBookings = fields.List(fields.Nested(PlainBookingsSchema), dump_only=True)
    
class BookedSchema(Schema):
    date = fields.Str(required=True)
    room_id = fields.Str(required=True)
    booked = fields.List(fields.Nested(PlainBookedSchema), dump_only=True)
    

class WorkSpaceSchema(Schema):
    workSpaces = fields.List(fields.Nested(PlainWorkSpaceSchema), dump_only=True)

# class AdminSchema(PlainUserRegisterSchema):

    # workSpaces = fields.List(fields.Nested(PlainWorkSpaceSchema),dump_only=True)



# class ClientSchema(PlainUserRegisterSchema):

    # booked = fields.List(fields.Nested(PlainBookedSchema),dump_only=True)

    