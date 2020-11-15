from flask import Flask
import decimal
from monolith.database import (
    db,
    User,
    Restaurant,
    Role,
    RestaurantTable,
    Reservation,
    OpeningHours,
    Review,
)
from monolith.views import blueprints
from monolith.auth import login_manager
import datetime


def create_app(tests=False):
    app = Flask(__name__)
    app.config["WTF_CSRF_SECRET_KEY"] = "A SECRET KEY"
    app.config["SECRET_KEY"] = "ANOTHER ONE"
    if tests is False:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/gooutsafe.db"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tests/gooutsafe.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    db.init_app(app)
    login_manager.init_app(app)
    db.create_all(app=app)

    # create a first admin user
    with app.app_context():

        # create the user roles
        q = db.session.query(Role).filter(Role.id == 1)
        role = q.first()
        if role is None:
            role = Role()
            role.value = "ADMIN"
            role.label = "Admin role"
            db.session.add(role)
            role = Role()
            role.value = "OPERATOR"
            role.label = "Operator role"
            db.session.add(role)
            role = Role()
            role.value = "CUSTOMER"
            role.label = "Customer role"
            db.session.add(role)
            role = Role()
            role.value = "HEALTH"
            role.label = "Health role"
            db.session.add(role)
            db.session.commit()

        # an Admin user
        q = db.session.query(User).filter(User.email == "admin@gooutsafe.com")
        user = q.first()
        if user is None:
            admin_user = User()
            admin_user.firstname = "Admin"
            admin_user.lastname = "Admin"
            admin_user.email = "admin@gooutsafe.com"
            admin_user.phone = "3334455678"
            admin_user.dateofbirth = datetime.datetime(2020, 10, 5)
            admin_user.is_admin = True
            admin_user.set_password("admin")
            admin_user.role_id = 1
            db.session.add(admin_user)
            db.session.commit()

        # an operator
        q = db.session.query(User).filter(User.email == "ham.burger@email.com")
        user = q.first()
        if user is None:
            first_operator = User()
            first_operator.firstname = "Ham"
            first_operator.lastname = "Burger"
            first_operator.email = "ham.burger@email.com"
            first_operator.phone = "222333567"
            first_operator.is_admin = False
            first_operator.set_password("operator")
            first_operator.role_id = 2
            db.session.add(first_operator)
            db.session.commit()

        # a customer
        q = db.session.query(User).filter(User.email == "john.doe@email.com")
        user = q.first()
        if user is None:
            first_customer = User()
            first_customer.firstname = "John"
            first_customer.lastname = "Doe"
            first_customer.email = "john.doe@email.com"
            first_customer.phone = "111234765"
            first_customer.is_admin = False
            first_customer.set_password("customer")
            first_customer.role_id = 3
            db.session.add(first_customer)
            db.session.commit()

        # health autority
        q = db.session.query(User).filter(User.email == "health_authority@gov.com")
        user = q.first()
        if user is None:
            health_authority = User()
            health_authority.firstname = "Health"
            health_authority.lastname = "Authority"
            health_authority.email = "health_authority@gov.com"
            health_authority.phone = "321456783"
            health_authority.is_admin = False
            health_authority.set_password("nocovid")
            health_authority.role_id = 4
            db.session.add(health_authority)
            db.session.commit()

        # a restaurant
        q = db.session.query(Restaurant).filter(Restaurant.id == 1)
        restaurant = q.first()
        if restaurant is None:
            # load the first operator
            q = db.session.query(User).filter(User.email == "ham.burger@email.com")
            user = q.first()
            first_restaurant = Restaurant()
            first_restaurant.name = "Trial Restaurant"
            first_restaurant.likes = 42
            first_restaurant.phone = 555123456
            first_restaurant.covid_measures = "Distance between tables 2mt; Menù touch; Alcohol Gel; Only Electronic Payment"
            first_restaurant.lat = 43.720586
            first_restaurant.lon = 10.408347
            first_restaurant.owner_id = user.id
            db.session.add(first_restaurant)
            db.session.commit()

        # a table
        q = db.session.query(RestaurantTable).filter(RestaurantTable.id == 1)
        table = q.first()
        if table is None:
            # insert the first table
            q = db.session.query(Restaurant).filter(
                Restaurant.name == "Trial Restaurant"
            )
            restaurant = q.first()
            first_table = RestaurantTable()
            first_table.restaurant_id = restaurant.id
            first_table.name = "Table 1"
            first_table.max_seats = 6
            first_table.available = True
            db.session.add(first_table)
            db.session.commit()

        # another table
        q = db.session.query(RestaurantTable).filter(RestaurantTable.id == 2)
        table = q.first()
        if table is None:
            # insert the first table
            q = db.session.query(Restaurant).filter(
                Restaurant.name == "Trial Restaurant"
            )
            restaurant = q.first()
            second_table = RestaurantTable()
            second_table.restaurant_id = restaurant.id
            second_table.name = "Table 2"
            second_table.max_seats = 4
            second_table.available = True
            db.session.add(second_table)
            db.session.commit()

        # insert some opening hours
        q = (
            db.session.query(OpeningHours)
            .filter(OpeningHours.restaurant_id == 1)
            .filter(OpeningHours.week_day == 0)
        )
        openinghour = q.first()
        if openinghour is None:
            q = db.session.query(Restaurant).filter(
                Restaurant.name == "Trial Restaurant"
            )
            restaurant = q.first()
            first_opening_hours = OpeningHours()
            first_opening_hours.restaurant_id = restaurant.id
            first_opening_hours.week_day = 0
            first_opening_hours.open_lunch = datetime.time(hour=12)
            first_opening_hours.close_lunch = datetime.time(hour=15)
            first_opening_hours.open_dinner = datetime.time(hour=20)
            first_opening_hours.close_dinner = datetime.time(hour=22)
            db.session.add(first_opening_hours)
            db.session.commit()

        # insert some opening hours
        q = (
            db.session.query(OpeningHours)
            .filter(OpeningHours.restaurant_id == 1)
            .filter(OpeningHours.week_day == 2)
        )
        openinghour = q.first()
        if openinghour is None:
            q = db.session.query(Restaurant).filter(
                Restaurant.name == "Trial Restaurant"
            )
            restaurant = q.first()
            second_opening_hours = OpeningHours()
            second_opening_hours.restaurant_id = restaurant.id
            second_opening_hours.week_day = 2
            second_opening_hours.open_lunch = datetime.time(hour=12)
            second_opening_hours.close_lunch = datetime.time(hour=15)
            second_opening_hours.open_dinner = datetime.time(hour=20)
            second_opening_hours.close_dinner = datetime.time(hour=22)
            db.session.add(second_opening_hours)
            db.session.commit()

        # insert some opening hours
        q = (
            db.session.query(OpeningHours)
            .filter(OpeningHours.restaurant_id == 1)
            .filter(OpeningHours.week_day == 4)
        )
        openinghour = q.first()
        if openinghour is None:
            q = db.session.query(Restaurant).filter(
                Restaurant.name == "Trial Restaurant"
            )
            restaurant = q.first()
            third_opening_hours = OpeningHours()
            third_opening_hours.restaurant_id = restaurant.id
            third_opening_hours.week_day = 4
            third_opening_hours.open_lunch = datetime.time(hour=12)
            third_opening_hours.close_lunch = datetime.time(hour=15)
            third_opening_hours.open_dinner = datetime.time(hour=20)
            third_opening_hours.close_dinner = datetime.time(hour=22)
            db.session.add(third_opening_hours)
            db.session.commit()

        # a reservation
        q = db.session.query(Reservation).filter(Reservation.id == 1)
        reservation = q.first()
        if reservation is None:
            # insert the first table
            q = db.session.query(User).filter(User.email == "john.doe@email.com")
            customer = q.first()
            q = db.session.query(RestaurantTable).filter(RestaurantTable.id == 1)
            table = q.first()
            q = db.session.query(Restaurant).filter(Restaurant.id == 1)
            restaurant = q.first()
            first_reservation = Reservation()
            first_reservation.reservation_date = datetime.datetime(
                2020, 10, 28, hour=12
            )
            first_reservation.reservation_end = (
                first_reservation.reservation_date
                + datetime.timedelta(minutes=restaurant.avg_time)
            )
            first_reservation.customer_id = customer.id
            first_reservation.table_id = table.id
            first_reservation.people_number = 2
            db.session.add(first_reservation)
            db.session.commit()

        # insert a review
        q = db.session.query(Review).filter_by(id=1).first()
        if q is None:
            review = Review()
            q = db.session.query(Restaurant).filter(
                Restaurant.name == "Trial Restaurant"
            )
            restaurant = q.first()

            q = db.session.query(User).filter(User.email == "john.doe@email.com")
            user = q.first()
            review.restaurant_id = restaurant.id
            review.reviewer_id = user.id
            review.review = "ciao"
            review.stars = decimal.Decimal(4.5)

            db.session.add(review)
            db.session.commit()
    # CALCULATE_RATING_RESTAURANTS
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", debug=True)
