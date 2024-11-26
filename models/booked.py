from db import db
from models.base import BaseModel
from models.enum import StatusEnum


class BookModel(BaseModel):
    __tablename__ = "book"
    room_id = db.Column(db.String(120), db.ForeignKey("room.id"))  # Link booking to a room
    client_id = db.Column(db.String(120), db.ForeignKey("user.id"))
    price = db.Column(db.Float(precision=2), nullable=False)  
    status = db.Column(db.Enum(StatusEnum), default = StatusEnum.inProgress)
    #
    date =  db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    #
    client = db.relationship("UserModel", back_populates="booked")  # Back reference to Room
    room = db.relationship("RoomModel", back_populates="bookings")  # Back reference to Room
