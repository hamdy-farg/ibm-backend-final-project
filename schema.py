import datetime
import os
import re

from marshmallow import Schema, ValidationError, fields, validates
from werkzeug.utils import secure_filename

from models.enum import RoleEnum


class PlainWorkSpaceSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    location = fields.Str(required=True)

    @validates("title")
    def validate_title(self, value):
        """Validate Title and last name."""
        if not value.isalpha():
            raise ValidationError("Title must contain only alphabetic characters.")
        if len(value) < 2 or len(value) > 50:
            raise ValidationError("Title must be between 2 and 50 characters long.")
    
    @validates("description")
    def validate_description(self, value):
        """Validate Title and last name."""
        if len(value) < 20 or len(value) > 500:
            raise ValidationError("Name must be between 20 and 500 characters long.")
        
    @validates("location")
    def validate_location(self, value):
        if len(value) < 20:
            raise ValidationError("this is not valid location")
        

class PlainRoomSchema(Schema):
    work_space_id = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    price_per_hour = fields.Float(required=True)
    capacity = fields.Int(required=True)
    start_date = fields.Str(required=True)
    end_date = fields.Str(required=True)
    start_time = fields.Str(required=True)
    start_end = fields.Str(required=True)

    @validates("title")
    def validate_title(self, value):
        """Validate Title and last name."""
        if not value.isalpha():
            raise ValidationError("Title must contain only alphabetic characters.")
        if len(value) < 2 or len(value) > 50:
            raise ValidationError("Title must be between 2 and 50 characters long.")
    
    @validates("description")
    def validate_description(self, value):
        """Validate Title and last name."""
        if len(value) < 20 or len(value) > 500:
            raise ValidationError("Name must be between 20 and 500 characters long.")
    
    @validates("start_date")
    def validate_description(self, value):
        """Validate Start Date and last name."""
        start_date = datetime.datetime.strptime(value, DATE_STAMP).date()
        print(start_date)
        if not start_date:
            raise ValidationError("you have to enter correct start date")
        
    @validates("end_date")
    def validate_description(self, value):
        """Validate end Date and last name."""
        end_date = datetime.datetime.strptime(value, DATE_STAMP).date()
        print(end_date)
        if not end_date:
            raise ValidationError("you have to enter correct end date")
        
    @validates("start_time")
    def validate_description(self, value):
        """Validate Start Date and last name."""
        start_date = datetime.datetime.strptime(value, TIME_STAMP).date()
        print(start_date)
        if not start_date:
            raise ValidationError("you have to enter correct start date")
        
    @validates("end_time")
    def validate_description(self, value):
        """Validate end Date and last name."""
        end_date = datetime.datetime.strptime(value, TIME_STAMP).time()
        print(end_date)
        if not end_date:
            raise ValidationError("you have to enter correct end date")

        
class PlainUserLoginSchema(Schema):
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
            raise ValidationError("Invalid email address format.")
    
    @validates("password")
    def validate_password(self, value):
        """Validate the password for strength."""
        if len(value) < 8 or len(value) > 32:
            raise ValidationError("Password must be between 8 and 32 characters long.")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in value):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not any(char in "!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~" for char in value):
            raise ValidationError("Password must contain at least one special character.")
class PlainUserRegisterSchema(PlainUserLoginSchema):
    id = fields.Str(dump_only=True)
    f_name = fields.Str(required=True)
    l_name = fields.Str(required=True)
    phone_number = fields.Str(required=True)
    
    @validates("f_name")
    @validates("l_name")
    def validate_name(self, value):
        """Validate first and last name."""
        if not value.isalpha():
            raise ValidationError("Name must contain only alphabetic characters.")
        if len(value) < 2 or len(value) > 50:
            raise ValidationError("Name must be between 2 and 50 characters long.")

class PlainUserUpdateSchema(Schema):
    f_name = fields.Str()
    l_name = fields.Str()
    email_address = fields.Str()
    phone_number = fields.Str()

    @validates("email_address")
    def validate_email(self, value):
        """Validate the email address format."""
        if len(value) != 0 and value != "":
            email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_regex, value):
                raise ValidationError("Invalid email address format.")

    @validates("f_name")
    @validates("l_name")
    def validate_name(self, value):
        """Validate first and last name."""

        if len(value) != 0  and value != "":
            if not value.isalpha():
                raise ValidationError("Name must contain only alphabetic characters.")
            if len(value) < 2 or len(value) > 50:
                raise ValidationError("Name must be between 2 and 50 characters long.")


class PlainWorkSpaceImagesSchema(Schema):
    photos = fields.Dict(dump_only=True)
class PlainBookedSchema(Schema):
    client_id = fields.Str(required=True)
    room_id = fields.Str(required=True)
    price = fields.Float(required=True)
    date_time_start = fields.Str(required=True)
    date_time_end = fields.Str(required=True)


class AdminSchema(PlainUserRegisterSchema):
    workSpaces = fields.List(fields.Nested(PlainWorkSpaceSchema),dump_only=True)



class ClientSchema(PlainUserRegisterSchema):

    booked = fields.List(fields.Nested(PlainBookedSchema),dump_only=True)

    