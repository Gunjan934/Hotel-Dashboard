from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):

    __tablename__ = "users"
    ROLE_CHOICES = ["customer", "staff"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    password_hash = db.Column(db.String(255),nullable=False)
    role = db.Column(db.String(20),nullable=False,default="customer")
    hotel_id = db.Column(db.Integer,db.ForeignKey("hotels.id"),nullable=True)
    created_at = db.Column(db.DateTime,server_default=db.func.now())
    hotel = db.relationship("Hotel",back_populates="staff")
    bookings = db.relationship("Booking", back_populates="user")
    def set_password(self, password):
     self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

class Hotel(db.Model):

    __tablename__ = "hotels"

    id = db.Column (db.Integer,primary_key=True)
    name = db.Column(db.String(150),nullable=False)
    city = db.Column(db.String(100),nullable=False)
    hotel_code = db.Column(db.String(20),unique=True,nullable=False)
    address = db.Column( db.String(255))
    phone = db.Column(db.String(20))
    rooms = db.relationship( "Room", back_populates="hotel",cascade="all, delete-orphan" )
    staff = db.relationship( "User", back_populates="hotel" )
    staff_key = db.Column(db.String(100),nullable=False)

class RoomType(db.Model):


    __tablename__ = "room_types"

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer,nullable=False)
    
    rooms = db.relationship("Room", back_populates="room_type")

class Room(db.Model):

    __tablename__ = "rooms"

    id = db.Column(db.Integer,primary_key=True )
    hotel_id = db.Column( db.Integer, db.ForeignKey("hotels.id"), nullable=False)
    room_type_id = db.Column(db.Integer,db.ForeignKey("room_types.id"),nullable=False)
    room_number = db.Column( db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False,default="available")
    price_per_night = db.Column(db.Numeric(10, 2),nullable=False)
    hotel = db.relationship( "Hotel", back_populates="rooms" )
    room_type = db.relationship("RoomType",back_populates="rooms")
    bookings = db.relationship("Booking",back_populates="room")

class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column( db.Integer, db.ForeignKey("users.id"), nullable=False)
    room_id = db.Column(db.Integer,db.ForeignKey("rooms.id"),nullable=False)
    check_in = db.Column(db.Date,nullable=False)
    check_out = db.Column(db.Date,nullable=False)
    guests = db.Column(db.Integer,nullable=False)
    status = db.Column(db.String(30),nullable=False,default="confirmed")
    created_at = db.Column( db.DateTime, server_default=db.func.now())
    user = db.relationship( "User", back_populates="bookings"  )
    room = db.relationship("Room",back_populates="bookings")
    bill = db.relationship("Bill",back_populates="booking",uselist=False,cascade="all, delete-orphan")

class Bill(db.Model):

    __tablename__ = "bills"

    id = db.Column(db.Integer,primary_key=True)
    booking_id = db.Column(db.Integer,db.ForeignKey("bookings.id"),unique=True,nullable=False)
    subtotal = db.Column(db.Numeric(10, 2),nullable=False)
    tax = db.Column(db.Numeric(10, 2),nullable=False)
    total_amount = db.Column(db.Numeric(10, 2),nullable=False)
    payment_status = db.Column(db.String(20),default="unpaid")
    generated_at = db.Column(db.DateTime,server_default=db.func.now() )
    booking = db.relationship("Booking",back_populates="bill")