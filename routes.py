from flask import ( Blueprint,render_template,request,redirect,url_for,session)
from datetime import datetime
from extensions import db
from models import (
    User,
    Room,
    RoomType,
    Booking,
    Bill,
    Hotel
)

routes = Blueprint("routes", __name__)
@routes.route("/")
def home():

    hotels = Hotel.query.all()

    return render_template(
        "home.html",
        hotels=hotels
    )
@routes.route("/hotel/<int:hotel_id>")
def hotel_details(hotel_id):

    hotel = Hotel.query.get(hotel_id)

    if not hotel:
        return "Hotel not found"

    rooms = Room.query.filter_by(
        hotel_id=hotel.id
    ).all()

    return render_template(
        "hotel_details.html",
        hotel=hotel,
        rooms=rooms
    )
@routes.route("/register", methods=["GET", "POST"])
def register():

    role = request.args.get("role")

    if request.method == "POST":

        role = request.form["role"]

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "User already registered"

        # CUSTOMER
        if role == "customer":

            user = User(
                name=name,
                email=email,
                role="customer",
                hotel_id=None
            )

        # STAFF
        elif role == "staff":

            hotel_code = request.form["hotel_code"]
            staff_key = request.form["staff_key"]

            hotel = Hotel.query.filter_by(
                hotel_code=hotel_code
            ).first()

            if not hotel:
                return "Invalid hotel code"

            if hotel.staff_key != staff_key:
                return "Invalid staff registration key"

            user = User(
                name=name,
                email=email,
                role="staff",
                hotel_id=hotel.id
            )

        else:

            return "Invalid role"

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        if role == "staff":

            return redirect(
                url_for("routes.staff_login")
            )

        return redirect(
            url_for("routes.login")
        )

    return render_template(
        "register.html",
        role=role
    )


@routes.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            role="customer"
        ).first()

        if not user:
            return "Invalid email or password"

        if not user.check_password(password):
            return "Invalid email or password"

        session["user_id"] = user.id
        session["role"] = user.role

        return redirect(
            url_for("routes.customer_dashboard")
        )

    return render_template("login.html")
@routes.route("/customer/dashboard")
def customer_dashboard():

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":
        return "Access Denied"

    return render_template(
        "customer_dashboard.html"
    )


@routes.route("/hotel/<int:hotel_id>/rooms", methods=["GET", "POST"])
def rooms(hotel_id):

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":
        return "Access Denied"

    hotel = Hotel.query.get(hotel_id)

    if not hotel:
        return "Hotel not found"

    available_rooms = []

    if request.method == "POST":

        check_in = datetime.strptime(
            request.form["check_in"],
            "%Y-%m-%d"
        ).date()

        check_out = datetime.strptime(
            request.form["check_out"],
            "%Y-%m-%d"
        ).date()

        if check_in >= check_out:
            return "Check-out date must be after check-in date"

        booked_rooms = Booking.query.filter(
            Booking.check_in < check_out,
            Booking.check_out > check_in,
            Booking.status != "cancelled"
        ).all()

        booked_room_ids = [
            booking.room_id
            for booking in booked_rooms
        ]

        if booked_room_ids:

            available_rooms = Room.query.filter(
                Room.hotel_id == hotel.id,
                Room.status != "maintenance",
                ~Room.id.in_(booked_room_ids)
            ).all()

        else:

            available_rooms = Room.query.filter(
                Room.hotel_id == hotel.id,
                Room.status != "maintenance"
            ).all()

    else:

        available_rooms = Room.query.filter(
            Room.hotel_id == hotel.id,
            Room.status != "maintenance"
        ).all()

    return render_template(
        "rooms.html",
        rooms=available_rooms,
        hotel=hotel
    )
@routes.route("/booking/<int:room_id>", methods=["GET", "POST"])
def booking(room_id):

    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    if session.get("role") != "customer":
        return "Access Denied"

    room = Room.query.get(room_id)

    if not room:
        return "Room not found"

    if room.status == "maintenance":
        return "Room is under maintenance"

    if request.method == "POST":

        check_in = datetime.strptime(
            request.form["check_in"],
            "%Y-%m-%d"
        ).date()

        check_out = datetime.strptime(
            request.form["check_out"],
            "%Y-%m-%d"
        ).date()

        guests = int(
            request.form["guests"]
        )

        if check_in >= check_out:
            return "Check-out date must be after check-in date"

        if guests <= 0:
            return "Number of guests must be greater than 0"

        if guests > room.room_type.capacity:
            return "Number of guests exceeds room capacity"

        existing_booking = Booking.query.filter(
            Booking.room_id == room.id,
            Booking.check_in < check_out,
            Booking.check_out > check_in,
            Booking.status != "cancelled"
        ).first()

        if existing_booking:
            return "Room is already booked for these dates"

        new_booking = Booking(
            user_id=session["user_id"],
            room_id=room.id,
            check_in=check_in,
            check_out=check_out,
            guests=guests,
            status="confirmed"
        )

        db.session.add(new_booking)

        db.session.commit()

        return redirect(
            url_for("routes.bookings")
        )

    return render_template(
        "booking.html",
        room=room
    )
@routes.route("/bookings")
def bookings():

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":
        return "Access Denied"

    user_bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "bookings.html",
        bookings=user_bookings
    )

@routes.route("/bill/<int:booking_id>")
def bill(booking_id):

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":
        return "Access Denied"

    booking = Booking.query.get(
        booking_id
    )

    if not booking:
        return "Booking not found"

    if booking.user_id != session["user_id"]:
        return "Access Denied"

    bill = Bill.query.filter_by(
        booking_id=booking.id
    ).first()

    if not bill:

        nights = (
            booking.check_out -
            booking.check_in
        ).days

        # PRICE IS NOW STORED IN ROOM
        price = booking.room.price_per_night

        subtotal = nights * price

        tax = subtotal * 10 / 100

        total_amount = subtotal + tax

        bill = Bill(
            booking_id=booking.id,
            subtotal=subtotal,
            tax=tax,
            total_amount=total_amount,
            payment_status="unpaid"
        )

        db.session.add(bill)
        db.session.commit()

    nights = (
        booking.check_out -
        booking.check_in
    ).days

    # PRICE IS NOW STORED IN ROOM
    price = booking.room.price_per_night

    return render_template(
        "bill.html",
        booking=booking,
        bill=bill,
        nights=nights,
        price=price
    )
@routes.route("/pay/<int:booking_id>")
def pay(booking_id):

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":
        return "Access Denied"

    booking = Booking.query.get(
        booking_id
    )

    if not booking:
        return "Booking not found"

    if booking.user_id != session["user_id"]:
        return "Access Denied"

    bill = Bill.query.filter_by(
        booking_id=booking.id
    ).first()

    if not bill:
        return "Bill not found"

    if bill.payment_status == "paid":
        return "Bill already paid"

    bill.payment_status = "paid"

    db.session.commit()

    return redirect(
        url_for(
            "routes.bill",
            booking_id=booking.id
        )
    )
@routes.route("/staff/login", methods=["GET", "POST"])
def staff_login():

    if request.method == "POST":

        hotel_code = request.form["hotel_code"]
        email = request.form["email"]
        password = request.form["password"]

        hotel = Hotel.query.filter_by(
            hotel_code=hotel_code
        ).first()

        if not hotel:
            return "Invalid hotel code"

        user = User.query.filter_by(
            email=email,
            role="staff",
            hotel_id=hotel.id
        ).first()

        if not user:
            return "Invalid staff details"

        if not user.check_password(password):
            return "Invalid password"

        session["user_id"] = user.id
        session["role"] = user.role
        session["hotel_id"] = hotel.id

        return redirect(
            url_for("routes.staff_dashboard")
        )

    return render_template("staff_login.html")
@routes.route("/staff/dashboard")
def staff_dashboard():

    if "user_id" not in session:
        return redirect(
            url_for("routes.staff_login")
        )

    if session.get("role") != "staff":
        return "Access Denied"

    hotel = Hotel.query.get(
        session["hotel_id"]
    )

    if not hotel:
        return "Hotel not found"

    return render_template(
        "staff_dashboard.html",
        hotel=hotel
    )
@routes.route("/staff/hotel")
def staff_hotel():

    if "user_id" not in session:
        return redirect(
            url_for("routes.staff_login")
        )

    if session.get("role") != "staff":
        return "Access Denied"

    hotel = Hotel.query.get(
        session["hotel_id"]
    )

    if not hotel:
        return "Hotel not found"

    return render_template(
        "staff_hotel.html",
        hotel=hotel
    )
@routes.route("/staff/customers")
def staff_customers():

    if "user_id" not in session:
        return redirect(
            url_for("routes.staff_login")
        )

    if session.get("role") != "staff":
        return "Access Denied"

    customers = (
        User.query
        .join(Booking)
        .join(Room)
        .filter(
            User.role == "customer",
            Room.hotel_id == session["hotel_id"]
        )
        .distinct()
        .all()
    )

    return render_template(
        "staff_customers.html",
        customers=customers
    )
@routes.route("/staff/bookings")
def staff_bookings():

    if "user_id" not in session:
        return redirect(
            url_for("routes.staff_login")
        )

    if session.get("role") != "staff":
        return "Access Denied"

    bookings = (
        Booking.query
        .join(Room)
        .filter(
            Room.hotel_id == session["hotel_id"]
        )
        .all()
    )

    return render_template(
        "staff_bookings.html",
        bookings=bookings
    )

@routes.route("/staff/checkin/<int:booking_id>")
def checkin(booking_id):

    if "user_id" not in session:
        return redirect(
            url_for("routes.staff_login")
        )

    if session.get("role") != "staff":
        return "Access Denied"

    booking = Booking.query.get(booking_id)

    if not booking:
        return "Booking not found"

    if booking.room.hotel_id != session["hotel_id"]:
        return "Access Denied"

    if booking.status != "confirmed":
        return "Booking cannot be checked in"

    booking.status = "checked_in"

    db.session.commit()

    return redirect(
        url_for("routes.staff_bookings")
    )
@routes.route("/staff/checkout/<int:booking_id>")
def checkout(booking_id):

    if "user_id" not in session:
        return redirect(url_for("routes.staff_login"))

    if session.get("role") != "staff":
        return "Access Denied"

    booking = Booking.query.get(booking_id)

    if not booking:
        return "Booking not found"

    if booking.status != "checked_in":
        return "Booking cannot be checked out"

    booking.status = "checked_out"

    db.session.commit()

    return redirect(url_for("routes.staff_bookings"))


@routes.route("/staff/rooms")
def staff_rooms():

    if "user_id" not in session:
        return redirect(
            url_for("routes.staff_login")
        )

    if session.get("role") != "staff":
        return "Access Denied"

    rooms = Room.query.filter_by(
        hotel_id=session["hotel_id"]
    ).all()

    return render_template(
        "staff_rooms.html",
        rooms=rooms
    )
@routes.route(
    "/staff/room/<int:room_id>",
    methods=["GET", "POST"]
)
def manage_room(room_id):

    if "user_id" not in session:
        return redirect(
            url_for("routes.staff_login")
        )

    if session.get("role") != "staff":
        return "Access Denied"

    room = Room.query.get(room_id)

    if not room:
        return "Room not found"

    if room.hotel_id != session["hotel_id"]:
        return "Access Denied"

    if request.method == "POST":

        status = request.form["status"]

        if status not in [
            "available",
            "maintenance"
        ]:
            return "Invalid room status"

        room.status = status

        db.session.commit()

        return redirect(
            url_for("routes.staff_rooms")
        )

    return render_template(
        "manage_room.html",
        room=room
    )
@routes.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("routes.login"))