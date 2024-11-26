from db import db
from models.base import BaseModel


class WorkSpaceModel(BaseModel):
    __tablename__ = "workSpace"

    title = db.Column(db.String(120), nullable= False, primary_key= False)
    description = db.Column(db.String(120), nullable= False, primary_key= False)
    location = db.Column(db.String(120), nullable= False,)
    image = db.Column(db.String(200), nullable=True)
    #
    owner_id = db.Column(db.String(120), db.ForeignKey("user.id"), nullable=False)
    rooms  = db.relationship("RoomModel", back_populates="workSpace", cascade="all, delete" )   
    owner = db.relationship("UserModel", back_populates="workSpaces")

