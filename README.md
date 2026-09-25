# StayLuxe -- Hotel Reservation System

StayLuxe is a web-based **Hotel Reservation and Management System**
developed using Python Flask, SQLAlchemy, MySQL, HTML, CSS, and Jinja2.

The system has two roles:

-   **Customer** -- browse hotels, check room availability, make
    reservations, view bookings and bills, and update payment status.
-   **Staff** -- manage rooms, view bookings and customers, and perform
    check-in/check-out operations for an assigned hotel.

> **Note:** The current project does not include an admin role or an
> external payment gateway. The Pay operation updates the bill payment
> status to `paid`.

## Features

### Customer

-   Customer registration
-   Common customer/staff login
-   Hotel browsing and location search
-   Hotel details
-   Date-based room availability
-   Room selection and reservation
-   Booking history
-   Bill generation
-   10% tax calculation
-   Payment status update
-   Customer-specific booking/bill access
-   Logout

### Staff

-   Staff account creation through `add_staff.py`
-   Common login
-   Staff dashboard
-   Assigned hotel information
-   Room management
-   Room price updates
-   Available/maintenance room status
-   Hotel booking management
-   Customer listing
-   Check-in and check-out

## Project Flow

### Customer Flow

``` text
Home
  ↓
Browse / Search Hotels
  ↓
Hotel Details
  ↓
Login / Register
  ↓
Check Room Availability
  ↓
Select Room
  ↓
Enter Booking Details
  ↓
Confirm Booking
  ↓
My Bookings
  ↓
View Bill
  ↓
Pay
  ↓
Payment Status = Paid
```

### Staff Flow

``` text
add_staff.py
  ↓
Common Login
  ↓
Staff Dashboard
  ↓
Assigned Hotel
  ├── Hotel Information
  ├── Rooms → Manage Room
  ├── Bookings → Check-in / Check-out
  └── Customers
```

## Technology Stack

  Technology         Purpose
  ------------------ --------------------------
  Python             Backend programming
  Flask              Web framework
  Flask-SQLAlchemy   SQLAlchemy integration
  SQLAlchemy         ORM/database interaction
  MySQL              Relational database
  Flask-Migrate      Database migrations
  Alembic            Migration engine
  PyMySQL            MySQL driver
  Jinja2             Dynamic HTML templates
  HTML5              Page structure
  CSS3               Styling
  python-dotenv      Environment variables
  Werkzeug           Password hashing
  Git/GitHub         Version control

## Architecture

``` text
Browser
   ↓
HTML / CSS / Jinja2
   ↓
Flask Routes
   ↓
SQLAlchemy ORM
   ↓
MySQL Database
```

### Main Files

  File              Purpose
  ----------------- ----------------------------------------------
  `app.py`          Creates and configures the Flask application
  `config.py`       Application/database configuration
  `extensions.py`   Initializes SQLAlchemy
  `models.py`       Database models and relationships
  `routes.py`       Customer and staff routes
  `seed.py`         Initial/sample database data
  `add_hotel.py`    Adds a hotel and four rooms
  `add_staff.py`    Creates a staff account
  `templates/`      Jinja2 HTML pages
  `static/`         CSS and images
  `migrations/`     Database migration files

## Project Structure

``` text
Hotel Reservation Dashboard/
├── app.py
├── config.py
├── extensions.py
├── models.py
├── routes.py
├── seed.py
├── add_hotel.py
├── add_staff.py
├── requirements.txt
├── .env
├── .gitignore
├── migrations/
├── templates/
│   ├── home.html
│   ├── hotel_details.html
│   ├── register.html
│   ├── login.html
│   ├── customer_dashboard.html
│   ├── rooms.html
│   ├── booking.html
│   ├── bookings.html
│   ├── bill.html
│   ├── staff_dashboard.html
│   ├── staff_hotel.html
│   ├── staff_customers.html
│   ├── staff_bookings.html
│   ├── staff_rooms.html
│   └── manage_room.html
└── static/
    ├── css/
    │   └── style.css
    └── images/
        ├── hotels/
        ├── rooms/
        └── hero/
```

## Database Design

The main entities are:

``` text
User
Hotel
RoomType
Room
Booking
Bill
```

### Relationships

``` text
Hotel
 ├── Staff Users
 └── Rooms
       └── Room Type

Customer
 └── Bookings
       ├── Room
       └── Bill
```

### Users

Stores customer and staff accounts:

`id`, `name`, `email`, `password_hash`, `role`, `hotel_id`, `created_at`

### Hotels

Stores hotel information:

`id`, `name`, `city`, `hotel_code`, `address`, `phone`, `staff_key`

### Room Types

Stores Standard, Deluxe, and Suite categories with capacity and
description.

### Rooms

Stores hotel, room type, room number, status, and price per night.

### Bookings

Stores customer, room, check-in, check-out, guests, status, and creation
time.

### Bills

Stores booking, subtotal, tax, total amount, payment status, and
generation time.

## Route Overview

  Route                            Method     Purpose
  -------------------------------- ---------- -----------------------
  `/`                              GET        Home/search
  `/hotel/<hotel_id>`              GET        Hotel details
  `/register`                      GET/POST   Customer registration
  `/login`                         GET/POST   Common login
  `/customer/dashboard`            GET        Customer dashboard
  `/hotel/<hotel_id>/rooms`        GET        Room availability
  `/booking/<room_id>`             GET/POST   Booking
  `/bookings`                      GET        Customer bookings
  `/bill/<booking_id>`             GET        Bill
  `/pay/<booking_id>`              POST       Payment status
  `/staff/dashboard`               GET        Staff dashboard
  `/staff/hotel`                   GET        Assigned hotel
  `/staff/rooms`                   GET        Staff rooms
  `/staff/room/<room_id>`          GET/POST   Manage room
  `/staff/bookings`                GET        Staff bookings
  `/staff/customers`               GET        Staff customers
  `/staff/checkin/<booking_id>`    POST       Check-in
  `/staff/checkout/<booking_id>`   POST       Check-out
  `/logout`                        GET        Logout

## Room Availability

``` text
Selected Hotel
      ↓
Selected Dates
      ↓
Find Overlapping Bookings
      ↓
Get Booked Room IDs
      ↓
Get Rooms of Selected Hotel
      ↓
Remove Booked Rooms
      ↓
Remove Maintenance Rooms
      ↓
Display Available Rooms
```

This prevents a room from being booked for overlapping dates.

## Booking Validation

Before creating a booking, the system checks:

-   User is logged in.
-   User has the customer role.
-   Hotel and room exist.
-   Room is not under maintenance.
-   Check-out is after check-in.
-   Guest count is valid.
-   Guest count does not exceed room capacity.
-   The room has no overlapping active booking.

## Staff Access Control

Each staff account is associated with one hotel using `hotel_id`.

``` text
Staff User
    ↓
hotel_id = 3
    ↓
Hotel 3
```

Staff operations are filtered by this hotel ID, so staff members work
only with their assigned hotel's rooms, bookings, and customers.

## Billing

``` text
Room Price × Number of Nights
             ↓
          Subtotal
             ↓
          10% Tax
             ↓
       Total Amount
```

Payment status:

``` text
unpaid → paid
```

The current implementation records payment status inside the
application; it does not process a real external financial transaction.

## Security

The project uses:

-   Flask sessions
-   Role-based authorization
-   Werkzeug password hashing
-   Customer-specific booking access
-   Staff hotel-level access control
-   `.env` for sensitive configuration
-   Foreign-key relationships
-   Input validation

Do not commit `.env` to GitHub.

Recommended `.gitignore` entries:

``` gitignore
.env
.env.*
venv/
.venv/
__pycache__/
*.py[cod]
instance/
.vscode/
.idea/
```

## Installation

### 1. Clone the repository

``` bash
git clone <your-repository-url>
cd "Hotel Reservation Dashboard"
```

### 2. Create virtual environment

``` bash
python -m venv venv
```

### 3. Activate it

Windows PowerShell:

``` powershell
.env\Scripts\Activate.ps1
```

Windows CMD:

``` cmd
venv\Scriptsctivate
```

### 4. Install dependencies

``` bash
pip install -r requirements.txt
```

Or:

``` bash
pip install flask flask-migrate flask-sqlalchemy pymysql python-dotenv
```

## Environment Configuration

Create `.env` in the project root:

``` env
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=hotel_reservation
SECRET_KEY=your_secret_key
```

## Database Setup

Create the MySQL database:

``` sql
CREATE DATABASE hotel_reservation;
```

Then configure `.env` and use the project's migration/setup process.

For initial/sample data:

``` bash
python seed.py
```

Avoid repeatedly running `seed.py` against an already-populated database
if its records have unique constraints.

## Add a New Hotel

``` bash
python add_hotel.py
```

The script collects hotel information and four room records and adds
them without resetting existing application data.

## Add Staff

``` bash
python add_staff.py
```

The script collects staff details and an existing hotel code, then
creates a staff account associated with that hotel.

## Run the Application

Activate the virtual environment and run:

``` bash
python app.py
```

Then open:

``` text
http://127.0.0.1:5000/
```

## Database Migrations

Create a migration after a model change:

``` bash
flask db migrate -m "Describe the change"
```

Apply migrations:

``` bash
flask db upgrade
```

Keep the `migrations/` directory in GitHub.

## Testing

Main testing areas include:

-   Customer registration
-   Customer/staff login
-   Invalid login
-   Hotel search
-   Hotel details
-   Room availability
-   Invalid dates
-   Overlapping bookings
-   Room capacity validation
-   Booking creation
-   Bill calculation
-   Payment status
-   Staff hotel isolation
-   Room management
-   Staff bookings
-   Check-in
-   Check-out
-   Logout

## Future Improvements

Possible future enhancements:

-   Real payment gateway
-   Email booking confirmation
-   SMS notifications
-   Booking cancellation/refund workflow
-   Advanced reporting
-   Automated unit/integration tests
-   Production deployment

These are future possibilities and are not part of the current
implementation scope.

## Academic Project

**Project:** StayLuxe -- Hotel Reservation System\
**Domain:** Web Development / Hotel Reservation and Management\
**Backend:** Python Flask\
**Database:** MySQL\
**ORM:** SQLAlchemy\
**Frontend:** HTML, CSS, Jinja2

Developed as an academic project for the **B.Tech Computer Science
Engineering** program.