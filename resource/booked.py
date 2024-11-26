from datetime import datetime

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import and_, or_

from models import BookModel, RoleEnum, RoomModel, UserModel
from schema import (DATEFORMAT, TIMEFORMAT, BookDeleteSchema, BookedSchema,
                    BookListSchema, BookUpdateSchema, PlainBookedSchema,
                    SuccessSchema)

blp = Blueprint("Book", "book", description="CRUD opration to make booking")
def get_avialable_time(room_id: str, date:str):
        """ get available time slots to know which time room is available at 
                
            - ARGUMENTS 
                - room_id as string 
                - date : as string
            - RETURN 
                - success: List of avialable room
                - fial: dict{
                    code: int,
                    message: str,
                    satus: bool}
        """
        room = RoomModel.query.filter(RoomModel.id == room_id).first()
        if room is None:
            return {
                "code": 404,
                "message":"room with this id not found",
                "status": False
            }

        try:
            date = datetime.strptime(date, DATEFORMAT).date()
        except Exception:
            return {
                "code": 401,
                "message":"invalid date formate",
                "status": False
            }
        if date < datetime.now().date():
            return  {
                "code": 401,
                "message":"you can not select date in the past",
                "status": False 
            }   
        if date > room.end_date or  date < room.start_date:
            return {
                "code": 401,
                "message":"invalid date select is out of range",
                "status": False
            }
        default_start_time = room.start_time
        default_end_time = room.end_time

        bookings = BookModel.query.filter(BookModel.room_id == room.id, BookModel.date == date).all()

        available_slots = [(default_start_time, default_end_time)]
        for booking in bookings:
            new_slots = []
            for start, end in available_slots:
                if booking.start_time >= end or booking.end_time  <= start:
                    new_slots.append((start, end))
                else:
                    if start < booking.start_time:
                        new_slots.append((start, booking.start_time))
                    if end > booking.end_time:
                        new_slots.append((booking.end_time, end)) 
            available_slots = new_slots
        return available_slots

@blp.route("/book")
class Book(MethodView):

    @blp.arguments(PlainBookedSchema, location="form")
    @blp.response(200, PlainBookedSchema)
    def post(self, book_data):
        client = UserModel.query.filter(UserModel.id == book_data.get("client_id"),
        UserModel.role == RoleEnum.client).first()
        #
        if client is None:
            abort(404, message='you client with this id not found')
        room = RoomModel.query.filter(RoomModel.id == book_data.get("room_id")).first()
        if room is None:
            abort(404, message='you room with this id not found')
        #

        start_time = book_data.get("start_time")
        end_time = book_data.get("end_time")
        date = book_data.get("date")


        if start_time is None or end_time is None or date is None:
            abort(401, "start , end time and date connot be None")
        #

        start_time = datetime.strptime(start_time, TIMEFORMAT).time()
        end_time = datetime.strptime(end_time, TIMEFORMAT).time()
        date = datetime.strptime(date, DATEFORMAT).date()
        #
        if room.start_time >  start_time or room.end_time < end_time:
            abort(401, message="start and end time must be included in room start and end") 
        if room.start_date > date and room.end_date < date:
            abort(401, message="date must be included in room start and end date") 

        bookings = BookModel.query.filter(
            BookModel.room_id == room.id,  # Ensure it's the same room
            BookModel.date == date,  # Optional: If bookings are date-specific
                     or_(
            and_(BookModel.start_time < end_time, BookModel.end_time > start_time)
        )).first()

        if bookings is not None:
            abort(401, message="you can not book the those hours agian")
        #
        price = float(book_data.get("price"))
        if price < room.price_per_hour:
            abort(401, message="price can not be less than room hour price") 

        book = BookModel(
            room = room,
            client = client,
            date = date,
            start_time = start_time,
            end_time =end_time,
            price= price)
        book_save = book.save()
        if book_save:
            return book
        abort(500 , "error accured while saving in db")

        
    @blp.arguments(BookedSchema,location="form")
    # @blp.response(200, BookedSchema)
    def get(self, book_data):
        date = book_data.get("date")
        room_id = book_data.get("room_id")
        available_slots = get_avialable_time(room_id=room_id, date=date)
        formated_slots = [{
            "start_time": slot[0].strftime(TIMEFORMAT),
            "end_time":slot[1].strftime(TIMEFORMAT)
        } for slot in available_slots]
        return formated_slots,200
    #
    @blp.arguments(BookUpdateSchema,location="form")
    @blp.response(200, PlainBookedSchema)
    def put(self, book_data):
        book = BookModel.query.filter(BookModel.id == book_data.get("book_id")).first()
        if book is None:
            abort(404, message= "your booked with your id is not found")
            
        start_time = book_data.get('start_time')
        end_time  = book_data.get('end_time')
        price = book_data.get("price")
        start_time =  datetime.strptime(start_time, TIMEFORMAT).time()
        end_time =  datetime.strptime(end_time, TIMEFORMAT).time()
        date = book_data.get("date")
        available_slots = get_avialable_time(room_id=book.room.id, date= date)
        for slot in available_slots:
            print(slot[0], slot[1])
            print(slot[0] <= start_time and slot[1] >= end_time)
            if not(slot[0] <= start_time and slot[1] >= end_time):
                abort(401, message="you can not choose this hours")
            else: 
                break
        book.update(
            date= datetime.strptime(date, DATEFORMAT),
            start_time = start_time,
            end_time= end_time
        )
        return book
    #
    @blp.arguments(BookDeleteSchema, location="form")
    @blp.response(200, SuccessSchema)
    def delete(self, book_data):
        book = BookModel.query.filter(BookModel.id == book_data.get("book_id")).first()
        if book is None:
            abort(404, message= "your booked with your id is not found")
        book.delete()
        return {
            "code": 200,
            "message": "the booked deleted successfully",
            "success": True 
        }
@blp.route("/client/book")
class GetAll(MethodView):
    @blp.arguments(BookListSchema, location="form")
    @blp.response(200, BookListSchema)
    def get(self, book_data):
        client_id = book_data.get("client_id")
        client = UserModel.query.filter(UserModel.id == client_id).first()
        if client is None:
            abort(404, message= "your client with your id is not found")
        return client