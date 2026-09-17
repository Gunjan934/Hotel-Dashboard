from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from datetime import datetime
from decimal import Decimal

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

    location = request.args.get("location", "").strip()

    if location:
        hotels = Hotel.query.filter( Hotel.city.ilike(f"%{location}%") ).all()
    else:
        hotels = Hotel.query.all()

    return render_template( "home.html",hotels=hotels, location=location )

@routes.route("/hotel/<int:hotel_id>")
def hotel_details(hotel_id):

    hotel = Hotel.query.get(hotel_id)

    if not hotel:
        flash("Hotel not found.", "error")
        return redirect(url_for("routes.home"))

    rooms = Room.query.filter_by(hotel_id=hotel.id).all()

    return render_template( "hotel_details.html", hotel=hotel, rooms=rooms )


@routes.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")


        if not name:
            flash("Please enter your name.", "error")
            return render_template("register.html")

        if not email:
            flash("Please enter your email.", "error")
            return render_template("register.html")

        if not password:
            flash("Please enter a password.", "error")
            return render_template("register.html")

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return render_template("register.html")


        user = User(
            name=name,
            email=email,
            role="customer",
            hotel_id=None
        )

        user.set_password(password)

        db.session.add(user)

        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(url_for("routes.login"))

    return render_template("register.html")


@routes.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:

            flash(
                "Please enter your email and password.",
                "error"
            )

            return render_template("login.html")


        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template("login.html")

        if not user.check_password(password):

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template("login.html")

        session.clear()

        session["user_id"] = user.id
        session["role"] = user.role


        if user.role == "customer":

            return redirect(
                url_for("routes.customer_dashboard")
            )


        if user.role == "staff":

            if not user.hotel_id:

                session.clear()

                flash(
                    "Staff account is not linked to a hotel.",
                    "error"
                )

                return render_template("login.html")

            session["hotel_id"] = user.hotel_id

            return redirect(
                url_for("routes.staff_dashboard")
            )

        session.clear()

        flash(
            "Invalid account role.",
            "error"
        )

        return render_template("login.html")

    return render_template("login.html")


@routes.route("/customer/dashboard")
def customer_dashboard():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    if session.get("role") != "customer":
        return redirect(url_for("routes.login"))

    user = User.query.get(session["user_id"])

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("routes.login"))

    return render_template(
        "customer_dashboard.html",
        user=user
    )
@routes.route("/hotel/<int:hotel_id>/rooms", methods=["GET"])
def rooms(hotel_id):

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":
        flash(
            "Only customers can check room availability.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    hotel = Hotel.query.get(hotel_id)

    if not hotel:
        flash(
            "Hotel not found.",
            "error"
        )

        return redirect(
            url_for("routes.home")
        )

    # Get dates from GET request
    check_in_value = request.args.get(
        "check_in",
        ""
    )

    check_out_value = request.args.get(
        "check_out",
        ""
    )

    available_rooms = []

    # Check availability only when dates are selected
    if check_in_value and check_out_value:

        try:

            check_in = datetime.strptime(
                check_in_value,
                "%Y-%m-%d"
            ).date()

            check_out = datetime.strptime(
                check_out_value,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please enter valid check-in and check-out dates.",
                "error"
            )

            return render_template(
                "rooms.html",
                rooms=[],
                hotel=hotel,
                check_in=check_in_value,
                check_out=check_out_value
            )

        # Check date order
        if check_in >= check_out:

            flash(
                "Check-out date must be after check-in date.",
                "error"
            )

            return render_template(
                "rooms.html",
                rooms=[],
                hotel=hotel,
                check_in=check_in_value,
                check_out=check_out_value
            )

        # Find rooms already booked for these dates
        booked_rooms = Booking.query.filter(
            Booking.check_in < check_out,
            Booking.check_out > check_in,
            Booking.status != "cancelled"
        ).all()

        booked_room_ids = [
            booking.room_id
            for booking in booked_rooms
        ]

        # Get available rooms for this hotel
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

    return render_template(
        "rooms.html",
        rooms=available_rooms,
        hotel=hotel,
        check_in=check_in_value,
        check_out=check_out_value
    )
@routes.route(
    "/booking/<int:room_id>",
    methods=["GET", "POST"]
)
def booking(room_id):

    if "user_id" not in session:

        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":

        flash(
            "Only customers can book rooms.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    room = Room.query.get(room_id)

    if not room:

        flash(
            "Room not found.",
            "error"
        )

        return redirect(
            url_for("routes.home")
        )

    if room.status == "maintenance":

        flash(
            "This room is currently under maintenance.",
            "error"
        )

        return redirect(
            url_for(
                "routes.hotel_details",
                hotel_id=room.hotel_id
            )
        )

    if request.method == "POST":

        check_in_value = request.form.get(
            "check_in",
            ""
        )

        check_out_value = request.form.get(
            "check_out",
            ""
        )

        guests_value = request.form.get(
            "guests",
            ""
        )

        try:

            check_in = datetime.strptime(
                check_in_value,
                "%Y-%m-%d"
            ).date()

            check_out = datetime.strptime(
                check_out_value,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please enter valid booking dates.",
                "error"
            )

            return render_template(
                "booking.html",
                room=room,
                check_in=check_in_value,
                check_out=check_out_value,
                guests=guests_value
            )


        if check_in >= check_out:

            flash(
                "Check-out date must be after check-in date.",
                "error"
            )

            return render_template(
                "booking.html",
                room=room,
                check_in=check_in_value,
                check_out=check_out_value,
                guests=guests_value
            )



        try:

            guests = int(guests_value)

        except ValueError:

            flash(
                "Please enter a valid number of guests.",
                "error"
            )

            return render_template(
                "booking.html",
                room=room,
                check_in=check_in_value,
                check_out=check_out_value,
                guests=guests_value
            )

        if guests <= 0:

            flash(
                "Number of guests must be greater than 0.",
                "error"
            )

            return render_template(
                "booking.html",
                room=room,
                check_in=check_in_value,
                check_out=check_out_value,
                guests=guests_value
            )

        if guests > room.room_type.capacity:

            flash(
                f"This room allows a maximum of "
                f"{room.room_type.capacity} guests.",
                "error"
            )

            return render_template(
                "booking.html",
                room=room,
                check_in=check_in_value,
                check_out=check_out_value,
                guests=guests_value
            )

    
        existing_booking = Booking.query.filter(
            Booking.room_id == room.id,
            Booking.check_in < check_out,
            Booking.check_out > check_in,
            Booking.status != "cancelled"
        ).first()

        if existing_booking:

            flash(
                "This room is already booked for the selected dates.",
                "error"
            )

            return render_template(
                "booking.html",
                room=room,
                check_in=check_in_value,
                check_out=check_out_value,
                guests=guests_value
            )


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

        flash(
            "Room booked successfully.",
            "success"
        )

        return redirect(
            url_for("routes.bookings")
        )

    return render_template(
        "booking.html",
        room=room,
        check_in="",
        check_out="",
        guests=""
    )


@routes.route("/bookings")
def bookings():

    if "user_id" not in session:

        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    user_bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Booking.created_at.desc()
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

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    booking = Booking.query.get(booking_id)

    if not booking:

        flash(
            "Booking not found.",
            "error"
        )

        return redirect(
            url_for("routes.bookings")
        )

  

    if booking.user_id != session["user_id"]:

        flash(
            "You are not allowed to view this bill.",
            "error"
        )

        return redirect(
            url_for("routes.bookings")
        )


    nights = (
        booking.check_out - booking.check_in
    ).days

    subtotal = (
        booking.room.price_per_night * nights
    )

    tax = subtotal * Decimal("0.10")

    total_amount = subtotal + tax



    bill = Bill.query.filter_by(
        booking_id=booking.id
    ).first()

    if not bill:

        bill = Bill(
            booking_id=booking.id,
            subtotal=subtotal,
            tax=tax,
            total_amount=total_amount,
            payment_status="unpaid"
        )

        db.session.add(bill)
        db.session.commit()

    return render_template(
        "bill.html",
        booking=booking,
        bill=bill,
        nights=nights
    )


@routes.route(
    "/pay/<int:booking_id>",
    methods=["POST"]
)
def pay(booking_id):

    if "user_id" not in session:

        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "customer":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    booking = Booking.query.get(booking_id)

    if not booking:

        flash(
            "Booking not found.",
            "error"
        )

        return redirect(
            url_for("routes.bookings")
        )

    if booking.user_id != session["user_id"]:

        flash(
            "You are not allowed to make this payment.",
            "error"
        )

        return redirect(
            url_for("routes.bookings")
        )

    bill = Bill.query.filter_by(
        booking_id=booking.id
    ).first()

    if not bill:

        flash(
            "Bill not found.",
            "error"
        )

        return redirect(
            url_for(
                "routes.bill",
                booking_id=booking.id
            )
        )

    bill.payment_status = "paid"

    db.session.commit()

    flash(
        "Payment successful.",
        "success"
    )

    return redirect(
        url_for(
            "routes.bill",
            booking_id=booking.id
        )
    )

@routes.route("/staff/dashboard")
def staff_dashboard():

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "staff":
        return redirect(
            url_for("routes.login")
        )

    user = User.query.get(
        session["user_id"]
    )

    if not user:
        flash(
            "Staff user not found.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    if not user.hotel_id:
        flash(
            "Staff hotel information not found.",
            "error"
        )

        return redirect(
            url_for("routes.logout")
        )

    hotel = Hotel.query.get(
        user.hotel_id
    )

    if not hotel:
        flash(
            "Hotel not found.",
            "error"
        )

        return redirect(
            url_for("routes.logout")
        )

    return render_template(
        "staff_dashboard.html",
        user=user,
        hotel=hotel
    )

@routes.route("/staff/hotel")
def staff_hotel():

    if "user_id" not in session:

        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "staff":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    hotel_id = session.get("hotel_id")

    hotel = Hotel.query.get(hotel_id)

    if not hotel:

        flash(
            "Hotel not found.",
            "error"
        )

        return redirect(
            url_for("routes.staff_dashboard")
        )

    return render_template(
        "staff_hotel.html",
        hotel=hotel
    )
@routes.route("/staff/customers")
def staff_customers():

    if "user_id" not in session:
        return redirect(url_for("routes.login"))

    if session.get("role") != "staff":
        return redirect(url_for("routes.login"))

    hotel_id = session.get("hotel_id")

    hotel = Hotel.query.get(hotel_id)

    if not hotel:
        flash("Hotel not found.", "error")
        return redirect(url_for("routes.staff_dashboard"))

    customers = (
        db.session.query(
            User,
            db.func.count(Booking.id).label("booking_count")
        )
        .join(Booking, Booking.user_id == User.id)
        .join(Room, Booking.room_id == Room.id)
        .filter(
            User.role == "customer",
            Room.hotel_id == hotel_id
        )
        .group_by(User.id)
        .all()
    )

    customer_list = []

    for user, booking_count in customers:

        user.booking_count = booking_count

        customer_list.append(user)

    return render_template(
        "staff_customers.html",
        hotel=hotel,
        customers=customer_list
    )
@routes.route("/staff/bookings")
def staff_bookings():

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "staff":
        return redirect(
            url_for("routes.login")
        )

    hotel_id = session.get("hotel_id")

    if not hotel_id:
        flash(
            "Hotel information not found.",
            "error"
        )

        return redirect(
            url_for("routes.staff_dashboard")
        )

    hotel = Hotel.query.get(hotel_id)

    if not hotel:
        flash(
            "Hotel not found.",
            "error"
        )

        return redirect(
            url_for("routes.staff_dashboard")
        )

    bookings = (
        Booking.query
        .join(Room)
        .filter(Room.hotel_id == hotel_id)
        .order_by(Booking.check_in.desc())
        .all()
    )

    return render_template(
        "staff_bookings.html",
        hotel=hotel,
        bookings=bookings
    )

@routes.route("/staff/rooms")
def staff_rooms():

    if "user_id" not in session:
        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "staff":
        return redirect(
            url_for("routes.login")
        )

    hotel_id = session.get("hotel_id")

    if not hotel_id:
        flash(
            "Hotel information not found.",
            "error"
        )

        return redirect(
            url_for("routes.staff_dashboard")
        )

    hotel = Hotel.query.get(hotel_id)

    if not hotel:
        flash(
            "Hotel not found.",
            "error"
        )

        return redirect(
            url_for("routes.staff_dashboard")
        )

    rooms = Room.query.filter_by(
        hotel_id=hotel_id
    ).all()

    return render_template(
        "staff_rooms.html",
        hotel=hotel,
        rooms=rooms
    )


@routes.route(
    "/staff/room/<int:room_id>",
    methods=["GET", "POST"]
)
def manage_room(room_id):

    if "user_id" not in session:

        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "staff":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    hotel_id = session.get("hotel_id")

    room = Room.query.filter_by(
        id=room_id,
        hotel_id=hotel_id
    ).first()

    if not room:

        flash(
            "Room not found.",
            "error"
        )

        return redirect(
            url_for("routes.staff_rooms")
        )

    if request.method == "POST":

        status = request.form.get(
            "status",
            ""
        ).strip()

        price = request.form.get(
            "price_per_night",
            ""
        ).strip()

    

        allowed_statuses = [
            "available",
            "maintenance"
        ]

        if status not in allowed_statuses:

            flash(
                "Invalid room status.",
                "error"
            )

            return render_template(
                "manage_room.html",
                room=room
            )


        try:

            price = float(price)

        except ValueError:

            flash(
                "Please enter a valid room price.",
                "error"
            )

            return render_template(
                "manage_room.html",
                room=room
            )

        if price <= 0:

            flash(
                "Room price must be greater than 0.",
                "error"
            )

            return render_template(
                "manage_room.html",
                room=room
            )

        room.status = status
        room.price_per_night = price

        db.session.commit()

        flash(
            "Room updated successfully.",
            "success"
        )

        return redirect(
            url_for("routes.staff_rooms")
        )

    return render_template(
        "manage_room.html",
        room=room
    )



@routes.route(
    "/staff/checkin/<int:booking_id>",
    methods=["POST"]
)
def checkin(booking_id):

    if "user_id" not in session:

        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "staff":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    hotel_id = session.get("hotel_id")

    booking = Booking.query.join(
        Room,
        Booking.room_id == Room.id
    ).filter(
        Booking.id == booking_id,
        Room.hotel_id == hotel_id
    ).first()

    if not booking:

        flash(
            "Booking not found.",
            "error"
        )

        return redirect(
            url_for("routes.staff_bookings")
        )

    booking.status = "checked-in"

    db.session.commit()

    flash(
        "Guest checked in successfully.",
        "success"
    )

    return redirect(
        url_for("routes.staff_bookings")
    )

@routes.route(
    "/staff/checkout/<int:booking_id>",
    methods=["POST"]
)
def checkout(booking_id):

    if "user_id" not in session:

        return redirect(
            url_for("routes.login")
        )

    if session.get("role") != "staff":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("routes.login")
        )

    hotel_id = session.get("hotel_id")

    booking = Booking.query.join(
        Room,
        Booking.room_id == Room.id
    ).filter(
        Booking.id == booking_id,
        Room.hotel_id == hotel_id
    ).first()

    if not booking:

        flash(
            "Booking not found.",
            "error"
        )

        return redirect(
            url_for("routes.staff_bookings")
        )

    booking.status = "checked-out"

    db.session.commit()

    flash(
        "Guest checked out successfully.",
        "success"
    )

    return redirect(
        url_for("routes.staff_bookings")
    )


@routes.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("routes.home")
    )