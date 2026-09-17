from app import app
from extensions import db
from models import User, Hotel


with app.app_context():

    print("\n===== StayLuxe Staff Account Creation =====\n")



    name = input("Enter staff name: ").strip()

    email = input("Enter staff email: ").strip()

    password = input("Enter staff password: ").strip()

    hotel_code = input("Enter hotel code: ").strip()



    hotel = Hotel.query.filter_by(
        hotel_code=hotel_code
    ).first()


    if not hotel:
        print("\nHotel not found.")

    else:

    

        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            print("\nA user with this email already exists.")

        else:

            staff = User(
                name=name,
                email=email,
                role="staff",
                hotel_id=hotel.id
            )

            staff.set_password(password)

            db.session.add(staff)

            db.session.commit()


            print("\nStaff account created successfully!")

            print(f"Name: {staff.name}")
            print(f"Email: {staff.email}")
            print(f"Hotel: {hotel.name}")
            print(f"Hotel Code: {hotel.hotel_code}")