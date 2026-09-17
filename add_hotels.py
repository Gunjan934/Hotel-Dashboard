from app import app
from extensions import db
from models import Hotel, Room, RoomType


with app.app_context():

    print("ADD NEW HOTEL")

    name = input("Hotel name: ").strip()

    city = input("City: ").strip()

    hotel_code = input("Hotel code: ").strip()

    address = input("Address: ").strip()

    phone = input("Phone: ").strip()

    staff_key = input("Staff key: ").strip()

    existing_hotel = Hotel.query.filter_by(
        hotel_code=hotel_code
    ).first()

    if existing_hotel:

        print("\nHotel code already exists.")
        print("Please use a different hotel code.")

    else:

        hotel = Hotel(
            name=name,
            city=city,
            hotel_code=hotel_code,
            address=address,
            phone=phone,
            staff_key=staff_key
        )

        db.session.add(hotel)

        # Flush to get the new hotel ID
        db.session.flush()


        standard = RoomType.query.filter_by(
            name="Standard"
        ).first()

        deluxe = RoomType.query.filter_by(
            name="Deluxe"
        ).first()

        suite = RoomType.query.filter_by(
            name="Suite"
        ).first()


        if  not standard or not deluxe or not suite:

            print("\nRoom types are missing.")
            print("Please make sure Standard, Deluxe and Suite")
            print("exist in the database.")

            db.session.rollback()

        else:

            room_number_1 = input(
                "\nRoom 1 number: "
            ).strip()

            price_1 = float(
                input("Room 1 price per night: ")
            )


            room1 = Room(
                hotel_id=hotel.id,
                room_type_id=standard.id,
                room_number=room_number_1,
                status="available",
                price_per_night=price_1
            )

            db.session.add(room1)


            room_number_2 = input(
                "Room 2 number: "
            ).strip()

            price_2 = float(
                input("Room 2 price per night: ")
            )


            room2 = Room(
                hotel_id=hotel.id,
                room_type_id=standard.id,
                room_number=room_number_2,
                status="available",
                price_per_night=price_2
            )

            db.session.add(room2)

            room_number_3 = input(
                "Room 3 number: "
            ).strip()

            price_3 = float(
                input("Room 3 price per night: ")
            )


            room3 = Room(
                hotel_id=hotel.id,
                room_type_id=deluxe.id,
                room_number=room_number_3,
                status="available",
                price_per_night=price_3
            )

            db.session.add(room3)


            room_number_4 = input(
                "Room 4 number: "
            ).strip()

            price_4 = float(
                input("Room 4 price per night: ")
            )


            room4 = Room(
                hotel_id=hotel.id,
                room_type_id=suite.id,
                room_number=room_number_4,
                status="available",
                price_per_night=price_4
            )

            db.session.add(room4)


            db.session.commit()


            print("\n================================")
            print("Hotel added successfully!")
            print("================================")

            print(f"\nHotel: {hotel.name}")
            print(f"City: {hotel.city}")
            print(f"Hotel Code: {hotel.hotel_code}")
            print(f"Hotel ID: {hotel.id}")

            print("\n4 rooms added successfully.")

            print("\nExisting data was not deleted.")