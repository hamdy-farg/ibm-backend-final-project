from db import db
from models.base import BaseModel

class RoomModel(BaseModel):
    __tablename__ = "room"
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable= False, primary_key= False)
    price_per_hour = db.Column(db.Float(precision=2), nullable=False)  
    capacity = db.Column(db.Integer(), nullable=False)  
    photos = db.Column(db.JSON, nullable=True)
    #
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    #
    work_space_id =db.Column(db.String(120), db.ForeignKey('workSpace.id'))
    #
    workSpace = db.relationship("WorkSpaceModel", back_populates="rooms")
    bookings = db.relationship("BookModel", back_populates="room", lazy="dynamic", cascade="all, delete")
