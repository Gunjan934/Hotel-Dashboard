from app import app
from extensions import db
from models import Hotel, Room, RoomType


def seed_data():

    # =========================
    # ROOM TYPES
    # =========================

    standard = RoomType(
        name="Standard",
        description="Comfortable standard room",
        capacity=2
    )

    deluxe = RoomType(
        name="Deluxe",
        description="Spacious deluxe room",
        capacity=2
    )

    suite = RoomType(
        name="Suite",
        description="Luxury suite",
        capacity=4
    )

    db.session.add_all([
        standard,
        deluxe,
        suite
    ])

    db.session.flush()


    # =========================
    # HOTEL 1
    # =========================

    hotel1 = Hotel(
        hotel_code="HTL001",
        name="Grand Palace Hotel",
        city="Delhi",
        address="Connaught Place, New Delhi",
        phone="9876543210",
        staff_key="GP@123"
    )

    db.session.add(hotel1)
    db.session.flush()

    rooms1 = [

        Room(
            hotel_id=hotel1.id,
            room_type_id=standard.id,
            room_number="101",
            price_per_night=2000,
            status="available"
        ),

        Room(
            hotel_id=hotel1.id,
            room_type_id=standard.id,
            room_number="102",
            price_per_night=2200,
            status="available"
        ),

        Room(
            hotel_id=hotel1.id,
            room_type_id=deluxe.id,
            room_number="201",
            price_per_night=3000,
            status="available"
        ),

        Room(
            hotel_id=hotel1.id,
            room_type_id=deluxe.id,
            room_number="202",
            price_per_night=3200,
            status="available"
        ),

        Room(
            hotel_id=hotel1.id,
            room_type_id=suite.id,
            room_number="301",
            price_per_night=6000,
            status="available"
        )
    ]

    db.session.add_all(rooms1)


    # =========================
    # HOTEL 2
    # =========================

    hotel2 = Hotel(
        hotel_code="HTL002",
        name="Sea View Hotel",
        city="Mumbai",
        address="Marine Drive, Mumbai",
        phone="9876543211",
        staff_key="SV@456"
    )

    db.session.add(hotel2)
    db.session.flush()

    rooms2 = [

        Room(
            hotel_id=hotel2.id,
            room_type_id=standard.id,
            room_number="201",
            price_per_night=2500,
            status="available"
        ),

        Room(
            hotel_id=hotel2.id,
            room_type_id=standard.id,
            room_number="202",
            price_per_night=2700,
            status="available"
        ),

        Room(
            hotel_id=hotel2.id,
            room_type_id=deluxe.id,
            room_number="301",
            price_per_night=3500,
            status="available"
        ),

        Room(
            hotel_id=hotel2.id,
            room_type_id=deluxe.id,
            room_number="302",
            price_per_night=3700,
            status="available"
        ),

        Room(
            hotel_id=hotel2.id,
            room_type_id=suite.id,
            room_number="401",
            price_per_night=7000,
            status="available"
        )
    ]

    db.session.add_all(rooms2)


    # =========================
    # HOTEL 3
    # =========================

    hotel3 = Hotel(
        hotel_code="HTL003",
        name="Royal Comfort Hotel",
        city="Bangalore",
        address="MG Road, Bangalore",
        phone="9876543212",
        staff_key="RC@789"
        
    )

    db.session.add(hotel3)
    db.session.flush()

    rooms3 = [

        Room(
            hotel_id=hotel3.id,
            room_type_id=standard.id,
            room_number="301",
            price_per_night=1800,
            status="available"
        ),

        Room(
            hotel_id=hotel3.id,
            room_type_id=standard.id,
            room_number="302",
            price_per_night=2000,
            status="available"
        ),

        Room(
            hotel_id=hotel3.id,
            room_type_id=deluxe.id,
            room_number="401",
            price_per_night=2800,
            status="available"
        ),

        Room(
            hotel_id=hotel3.id,
            room_type_id=deluxe.id,
            room_number="402",
            price_per_night=3000,
            status="available"
        ),

        Room(
            hotel_id=hotel3.id,
            room_type_id=suite.id,
            room_number="501",
            price_per_night=5500,
            status="available"
        )
    ]

    db.session.add_all(rooms3)


    # =========================
    # HOTEL 4
    # =========================

    hotel4 = Hotel(
        hotel_code="HTL004",
        name="Pink City Hotel",
        city="Jaipur",
        address="MI Road, Jaipur",
        phone="9876543213",
        staff_key="PC@321"
    )

    db.session.add(hotel4)
    db.session.flush()

    rooms4 = [

        Room(
            hotel_id=hotel4.id,
            room_type_id=standard.id,
            room_number="401",
            price_per_night=1700,
            status="available"
        ),

        Room(
            hotel_id=hotel4.id,
            room_type_id=standard.id,
            room_number="402",
            price_per_night=1900,
            status="available"
        ),

        Room(
            hotel_id=hotel4.id,
            room_type_id=deluxe.id,
            room_number="501",
            price_per_night=2600,
            status="available"
        ),

        Room(
            hotel_id=hotel4.id,
            room_type_id=deluxe.id,
            room_number="502",
            price_per_night=2800,
            status="available"
        ),

        Room(
            hotel_id=hotel4.id,
            room_type_id=suite.id,
            room_number="601",
            price_per_night=5000,
            status="available"
        )
    ]

    db.session.add_all(rooms4)


    # =========================
    # HOTEL 5
    # =========================

    hotel5 = Hotel(
        hotel_code="HTL005",
        name="Beach Resort",
        city="Goa",
        address="Calangute, Goa",
        phone="9876543214",
        staff_key="BR@654"
    )

    db.session.add(hotel5)
    db.session.flush()

    rooms5 = [

        Room(
            hotel_id=hotel5.id,
            room_type_id=standard.id,
            room_number="501",
            price_per_night=3000,
            status="available"
        ),

        Room(
            hotel_id=hotel5.id,
            room_type_id=standard.id,
            room_number="502",
            price_per_night=3200,
            status="available"
        ),

        Room(
            hotel_id=hotel5.id,
            room_type_id=deluxe.id,
            room_number="601",
            price_per_night=4200,
            status="available"
        ),

        Room(
            hotel_id=hotel5.id,
            room_type_id=deluxe.id,
            room_number="602",
            price_per_night=4500,
            status="available"
        ),

        Room(
            hotel_id=hotel5.id,
            room_type_id=suite.id,
            room_number="701",
            price_per_night=8000,
            status="available"
        )
    ]

    db.session.add_all(rooms5)


    # =========================
    # SAVE
    # =========================

    db.session.commit()

    print("5 hotels and rooms created successfully!")


if __name__ == "__main__":

    with app.app_context():
        seed_data()