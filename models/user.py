from passlib.hash import pbkdf2_sha256

from db import db
from models.base import BaseModel
from models.enum import RoleEnum, StatusEnum


class UserModel(BaseModel):
    __abstract__= True 
    __tablename__ = "user"
    email_address = db.Column(db.String(80), nullable=True, unique=True)
    phone_number = db.Column(db.String(80), nullable=True, unique=True)
    address = db.Column(db.Text, nullable=True)
    f_name = db.Column(db.String(80), nullable=True)
    l_name = db.Column(db.String(80), nullable=True)
    image = db.Column(db.String(80), nullable=True, default="defualt.png")
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, raw_password):
        """ save password as hash"""
        self.password = pbkdf2_sha256.hash(raw_password)

    def check_password(self, raw_password):
        """ check if the provided password is match the user password"""
        return pbkdf2_sha256.verify(raw_password, self.password)

class AdminModel(UserModel):
    """ Admin model class """
    __tablename__ = "admin"
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.admin)
    workSpaces = db.relationship("WorkSpaceModel", back_populates="owner", lazy="dynamic", cascade="all, delete")

class ClientModel(UserModel):
    __tablename__ = "client"
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.client)
    booked = db.relationship("BookModel", back_populates="client",lazy="dynamic" , cascade="all, delete")
    
