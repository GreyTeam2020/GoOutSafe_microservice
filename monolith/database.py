from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal as D
import sqlalchemy.types as types


db = SQLAlchemy()


class SqliteNumeric(types.TypeDecorator):
    """
    Pysql doesn't support the floating point and we need to support it
    to avoid the warning during the tests
    """

    impl = types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return D(value)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Unicode(128), nullable=False, unique=True)
    phone = db.Column(db.Unicode(16), nullable=False, unique=True)
    firstname = db.Column(db.Unicode(128))
    lastname = db.Column(db.Unicode(128))
    password = db.Column(db.Unicode(128))
    dateofbirth = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    # user role
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    restaurant = relationship("Role", foreign_keys="User.role_id")
    is_anonymous = False

    def __init__(self, *args, **kw):
        super(User, self).__init__(*args, **kw)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def set_role(self, role):
        self.role = role

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id


class Restaurant(db.Model):
    __tablename__ = "restaurant"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.Text(100))

    likes = db.Column(
        db.Integer
    )  # will store the number of likes, periodically updated in background

    lat = db.Column(db.Float)  # restaurant latitude
    lon = db.Column(db.Float)  # restaurant longitude

    # menu = db.Column(db.Text(255)) #we keep a text field? or we create a menu table?

    # resturant owner
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    owner = relationship("User", foreign_keys="Restaurant.owner_id")

    phone = db.Column(db.Integer)

    covid_measures = db.Column(db.Text(500))

    # THERE IS NO INTERVAL DATA TYPE IN SQL LITE
    # avg_time = db.Column(db.Interval())
    # I store the avg time in integer THAT REPRESENTS MINUTES
    avg_time = db.Column(db.Integer, default=30)

    rating = db.Column(db.Float, default=0.0)

    def __init__(self, *args, **kw):
        super(Restaurant, self).__init__(*args, **kw)


class Like(db.Model):
    __tablename__ = "like"

    liker_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    liker = relationship("User", foreign_keys="Like.liker_id")

    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), primary_key=True
    )
    restaurant = relationship("Restaurant", foreign_keys="Like.restaurant_id")

    marked = db.Column(
        db.Boolean, default=False
    )  # True iff it has been counted in Restaurant.likes


class RestaurantTable(db.Model):
    __tablename__ = "restaurant_table"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"))
    restaurant = relationship(
        "Restaurant", foreign_keys="RestaurantTable.restaurant_id"
    )

    name = db.Column(db.Text(100))  # table name

    max_seats = db.Column(db.Integer)  # max seats of the table

    available = db.Column(
        db.Boolean, default=False
    )  # I don't understand the purpose of this field..


class Role(db.Model):
    # this is the role of a user (like operator, customer....)
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.Text(100))
    label = db.Column(db.Text(100))


class Positive(db.Model):
    # all covid positives
    __tablename__ = "positive"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_date = db.Column(db.Date)
    marked = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = relationship("User", foreign_keys="Positive.user_id")


class Reservation(db.Model):
    # reservations
    __tablename__ = "reservation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservation_date = db.Column(db.DateTime)
    reservation_end = db.Column(db.DateTime)
    # customer that did the the reservation
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    custumer = relationship("User", foreign_keys="Reservation.customer_id")
    #
    # reserved table
    table_id = db.Column(db.Integer, db.ForeignKey("restaurant_table.id"))
    table = relationship("RestaurantTable", foreign_keys="Reservation.table_id")
    #
    people_number = db.Column(db.Integer)  # number of people in this reservation
    checkin = db.Column(db.Boolean, default=False)


class PhotoGallery(db.Model):
    __tablename__ = "photo_gallery"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.Text(255))
    caption = db.Column(db.Text(200))
    # restaurant
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"))
    restaurant = relationship("Restaurant", foreign_keys="PhotoGallery.restaurant_id")


class OpeningHours(db.Model):
    """
    opening hours
    """

    __tablename__ = "opening_hours"
    restaurant_id = db.Column(
        db.Integer, db.ForeignKey("restaurant.id"), primary_key=True
    )
    restaurant = relationship("Restaurant", foreign_keys="OpeningHours.restaurant_id")
    week_day = db.Column(db.Integer, primary_key=True)
    open_lunch = db.Column(db.Time, default=datetime.utcnow)
    close_lunch = db.Column(db.Time, default=datetime.utcnow)
    open_dinner = db.Column(db.Time, default=datetime.utcnow)
    close_dinner = db.Column(db.Time, default=datetime.utcnow)


class Menu(db.Model):
    # menu
    __tablename__ = "menu"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # restaurant
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"))
    restaurant = relationship("Restaurant", foreign_keys="Menu.restaurant_id")
    #
    cusine = db.Column(db.Text(100))
    description = db.Column(db.Text(255))


class MenuDish(db.Model):
    # menu dishes
    __tablename__ = "menu_dish"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # restaurant
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"))
    restaurant = relationship("Restaurant", foreign_keys="MenuDish.restaurant_id")
    #
    name = db.Column(db.Text(100))
    price = db.Column(db.Float())


class MenuPhotoGallery(db.Model):
    # menu photos
    __tablename__ = "menu_photo_gallery"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.Text(255))
    caption = db.Column(db.Text(200))
    # menu reference
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id"))
    menu = relationship("Menu", foreign_keys="MenuPhotoGallery.menu_id")


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # review, reletion with user table
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    reviewer = relationship("User", foreign_keys="Review.reviewer_id")
    # restaurant
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"))
    restaurant = relationship("Restaurant", foreign_keys="Review.restaurant_id")

    stars = db.Column(SqliteNumeric())
    review = db.Column(db.Text())
    data = db.Column(db.DateTime(), default=datetime.now())


class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # reservation
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservation.id"))
    reservation = relationship("Reservation", foreign_keys="Friend.reservation_id")
    # email
    email = db.Column(db.Text())
