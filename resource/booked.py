from datetime import datetime

from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint, abort
from sqlalchemy import and_, or_

from models import BookModel, RoleEnum, RoomModel, UserModel
from schema import (DATEFORMAT, TIMEFORMAT, BookDeleteSchema, BookedSchema,
                    BookListSchema, BookUpdateSchema, PlainBookedSchema,
                    RoomsSchema, SuccessSchema, updateBookStatusSchema)

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
            abort(404,
                message="room with this id not found",)
            

        try:
            date = datetime.strptime(date, DATEFORMAT).date()
        except Exception:
            abort (401,message="invalid date formate")
        if date < datetime.now().date():
            abort  (
                 401,
                message ="you can not select date in the past",
                 
            )   
        if date > room.end_date or  date < room.start_date:
            abort(
               401,
                message="invalid date select is out of range",
              
            )
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
    @jwt_required()
    @blp.arguments(PlainBookedSchema, location="form")
    @blp.response(200, PlainBookedSchema)
    def post(self, book_data):
        client_id = get_jwt_identity()
        client = UserModel.query.filter(UserModel.id == client_id,
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
        if start_time >= end_time:
            abort(401, message="start can not be greater than or equal end time") 

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
        print("hiiiiiiiiii",available_slots)
        for slot in available_slots:

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
@blp.route("/room/book")
class GetAll(MethodView):
    @blp.arguments(BookListSchema, location="form")
    @blp.response(200, BookListSchema)
    def get(self, book_data):
        room = RoomModel.query.filter(RoomModel.id == book_data.get("room_id")).first()
        if room is not None:
            roomBookings = room.bookings.all()
            if roomBookings is not None:
                return  {
                    "room_id": room.id,
                    "roomBookings": roomBookings
                }
        else:
            abort(404, message="your room is not found")


from db import db
from models import WorkSpaceModel


@blp.route("/admin/books")
class GetAll(MethodView):
    @jwt_required()
    # @blp.arguments(BookListSchema, location="form")
    @blp.response(200, BookListSchema)
    def get(self):
        # Get the current admin's ID from the JWT token
        admin_id = get_jwt_identity()

        # Fetch all workspaces for this admin
        workspaces = WorkSpaceModel.query.filter_by(owner_id=admin_id).all()

        # Collect all room IDs from the admin's workspaces
        room_ids = []
        for workspace in workspaces:
            if workspace.rooms:  # Ensure the workspace has rooms
                for room in workspace.rooms:
                    room_ids.append(room.id)

        # Fetch all bookings associated with the collected room IDs
        books = []
        admin_books = BookModel.query.filter(BookModel.room_id.in_(room_ids)).all()
        for book in admin_books:
            room = RoomModel.query.filter(RoomModel.id == book.room_id).first()
            book.room_title = room.title
            book.work_space_title = room.workSpace.title
            book.room_image = room.convert_image_to_link(route="/room/image/", image_id= room.id)
            books.append(book)
        
        return {"roomBookings":books}

@blp.route("/book/status")    
class BookStatus (MethodView) :
    @blp.arguments(updateBookStatusSchema,location="form")
    @blp.response(200, PlainBookedSchema)
    def put(self, book_data):
        try:
            book = BookModel.query.filter(BookModel.id == book_data.get("booked_id")).first()
            book_data.pop("booked_id")
            if book == None:
                abor(404, message="your book not found")
            updated = book.update(**book_data)
            if updated:
                return book
            else:
                abort(500, message= "an error accred while saving in db" )
        except Exception as e:
            abort(500, message=f"{e}")


@blp.route("/book/available")
class AvialableTime(MethodView):
    @blp.arguments(BookedSchema,location="form")
    # @blp.response(200, BookedSchema)
    def post(self, book_data):
        date = book_data.get("date")
        room_id = book_data.get("room_id")
        available_slots = get_avialable_time(room_id=room_id, date=date)
        
        formated_slots = [{
            "start_time": slot[0].strftime(TIMEFORMAT),
            "end_time":slot[1].strftime(TIMEFORMAT)
        } for slot in available_slots]
        return formated_slots,200