import os
import uuid
from datetime import datetime

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from db import db


class BaseModel(db.Model):
    __abstract__= True

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
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Automatically update the `updated_at` field
        self.updated_at = func.now()

        # Commit changes to the database
        done =  self.save()
        return done
    
    def save_image(self, file):
        """ save_image funcaiton
            - arguments
                - file contains the image
                - user 
            - Return
                - user if successed
                - json object if {message: ""} error accured
        """
        try:
            file_extenstion = file.filename.split(".")[-1]
            folder_path = f"{os.getcwd()}\\assets\\user\\user_pics\\"
            final_path = f"{os.getcwd()}\\assets\\user\\user_pics\\{self.id}.{file_extenstion}"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file.save(final_path)
            self.update({
                "image": final_path
            })
        except:
            return jsonify ({"message":"error accured while saving image"}),401
        return self

    def validate_user_data(self, user_data, request):
        """ validate uesr data to save user_data into db
            - ARGUMENTS:
                - user 
                - user data
            - RETURN:
                - if fial : 401 json of error message
                - if success  image file
                    
        """
        error_msg = None
        if  error_msg is None and  user_data.get("email_address") is not None:
            print("enter", type(self), type(self.__class__))
            
            filtered_user = self.__class__.query.filter(self.__class__.email_address == user_data.get("email_address")).first()
            print(filtered_user)
            if filtered_user is not None:
                error_msg = "the email address is taken before"
            else:
                self.email_address =  user_data.get("email_address")
        print(error_msg)
        
        if  error_msg is None and user_data.get("phone_number") is not None:
            phone_number = user_data.get("phone_number")
            if phone_number.isdigit():
                filtered_user = self.__class__.query.filter(self.__class__.phone_number == user_data.get("phone_number")).first()
                if filtered_user is not None:
                    error_msg = "the phone number is taken before type another one"
                else:
                    self.phone_number = phone_number
                    self.f_name = user_data.get("f_name")
                    self.l_name = user_data.get("l_name")
            else:
                error_msg = "Invalid phone number"
       
        if error_msg is None  and 'image' not in request.files:
            error_msg = "image missing"
        
        try:
            file = request.files["image"]
            if  error_msg is None and file.filename == '':
                error_msg = "image not selected"
        except Exception as e:
            if error_msg is None:
                error_msg = "server error to upload"
        if error_msg is None:
            self.set_password(raw_password=user_data["password"])
            done = self.save()
            if  not done :
                error_msg = "error accured when saving on server"
            if error_msg is None :
                self.file = file
                return self
        return jsonify({"message": error_msg}),401

