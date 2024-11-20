from db import db
from models.base import BaseModel


class WorkSpaceModel(BaseModel):
    __tablename__ = "workSpace"

    title = db.Column(db.String(120), nullable= False, primary_key= False)
    description = db.Column(db.String(120), nullable= False, primary_key= False)
    location = db.Column(db.String(120), nullable= False,)
    photos = db.Column(db.JSON, nullable=True)

    owner_id = db.Column(db.String(120), db.ForeignKey("admin.id"), nullable=False)
    rooms  = db.relationship("RoomModel", back_populates="workSpace", cascade="all, delete" )   
    owner = db.relationship("AdminModel", back_populates="workSpaces")

