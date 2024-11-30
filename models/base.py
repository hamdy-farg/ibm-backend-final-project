import os
import uuid
from datetime import datetime

from flask import jsonify
from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from db import db

IMAGE_EXTENTIONS = ['jpg', "png", "jpeg"]

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(32), primary_key=True, nullable=False, default=lambda: uuid.uuid4().hex)
    created_at = db.Column(db.DateTime(timezone=True),default=func.now(),nullable=False )
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    def save(self):
        """save the object to the database."""  
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            print(e)
            return False

    def delete(self):
        """ delete the object from database"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            return False

    def update(self, **kwargs):
        """
        Update specific fields of an object.
        
        Example usage:
            user.update(email_address="new_email@example.com", phone_number="1234567890")
        """
        print("begen update")
        filtered_map = {key: value for key, value in kwargs.items() if value}
        for key, value in filtered_map.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Automatically update the `updated_at` field
        self.updated_at = func.now()

        # Commit changes to the database
        done =  self.save()
        return done

    def check_image(self, request_data= None, file=None):
        """ check image
                to check image is valid or not

            pre_condition  : Enter request_data contains file to check or file
            
            - ARGUMENTS
                - request_data  default None
                - file          default None

            - RETURN 
                - file if success
                - error message if fial
        """
        if file is None:
            if request_data is not None :
                if 'image' not in request_data.files:
                    return "image missing"
        if file is None:
            if request_data is not None:
                file = request_data.files['image']
        # print(file.read())
        if file is not None:
            if  file.filename == '':
                return "image not selected"
            file_extenstion = file.filename.split(".")[-1]
            if file_extenstion not in IMAGE_EXTENTIONS:
                print("extenstion error")
                return "this file extenstion is not allowed please send [jpg, jpeg, png]"
            return file
        else :
            return "you have to pass file or give request"
    def save_image(self, folder_name:str, request_data = None, file= None ):
        """ save_image funcaiton
            - arguments
                - folder name required
                - request data = None
                - file = None
            - Return
                - self if successed
                - if fial  error message
        """

        # print(request_data.files['image'].read())
        try:
            checked = self.check_image(request_data=request_data, file=file)
            if isinstance(checked, str):
                error_msg = checked
                return error_msg
            file = checked
            file_extenstion = file.filename.split(".")[-1]
            folder_path =  os.path.join(os.getcwd(),"assets","user",f"{folder_name}")
            self.save()
            final_path = os.path.join(os.getcwd(),"assets","user",f"{folder_name}", f"{self.id}.{file_extenstion}")
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            if os.path.exists(final_path):
                os.remove(final_path)
            file.save(final_path)
            saved_path =  f"{self.id}.{file_extenstion}"
            self.image = saved_path
        except Exception as e:
            print(e)
            return "error accured while saving image"
        return self

        
    def convert_image_to_link(self, route:str, image_id:str):
        """ convert any image id to link
            
            - ARGUMENTS
                - route as /room/image/
                - image_id 
            - RETURN
                - str image link
        """
        
        image_link =  f"{os.getenv("LOCALHOST","http://127.0.0.1:5000")}"+ f"{route}"+f"{image_id}"
        return image_link
    def validate_user_data(self, user_data, request):
        """ validate uesr data to save user_data into db
            - ARGUMENTS:
                - user 
                - user data
            - RETURN:
                - if fial : error message
                - if success  user with full data (email_address, phone, image, ......)
                    
        """
       
        error_msg = None
        if  error_msg is None and  user_data.get("email_address") is not None:
            
            filtered_user = self.__class__.query.filter(self.__class__.email_address == user_data.get("email_address")).first()
            if filtered_user is not None:
                error_msg = "the email address is taken before"
            else:
                self.email_address =  user_data.get("email_address")
        
        # print(error_msg)
        
        # if  error_msg is None and user_data.get("phone_number") is not None:
        #     phone_number = user_data.get("phone_number")
        # if phone_number.isdigit():
        #     filtered_user = self.__class__.query.filter(self.__class__.phone_number == user_data.get("phone_number")).first()
        #     if filtered_user is not None:
        #         error_msg = "the phone number is taken before type another one"
        #     else:
            # self.phone_number = phone_number
        self.f_name = user_data.get("f_name")
        self.l_name = user_data.get("l_name")
        # else:
        #     error_msg = "Invalid phone number"
        
           
        if error_msg is None:
            self.set_password(raw_password=user_data["password"])
            # if error_msg is None :
                # user = self.save_image(request_data=request, folder_name="user_pics")
                # if isinstance(user, str):
                #     error_msg = user
            if error_msg is None :
                return self
        return  error_msg

