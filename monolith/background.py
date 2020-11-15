from celery import Celery
from flask import Flask

from monolith.database import db
from monolith.utils.send_mail import (
    send_registration_confirm,
    send_possible_positive_contact_to_friend,
    send_possible_positive_contact,
    send_booking_confirmation_to_friends,
    send_positive_in_restaurant,
    send_positive_booking_in_restaurant,
)
from monolith.services import RestaurantServices

_CELERY = False

# BACKEND = "redis://{}:6379".format("rd01")
# BROKER = "redis://{}:6379/0".format("rd01")
# celery = Celery(__name__, backend=BACKEND, broker=BROKER)
def create_celery_app():
    """
    This application create the flask app for the worker
    Thanks https://github.com/nebularazer/flask-celery-example
    """
    ## redis inside the http is the name of network that is called like the containser
    ## a good reference is https://stackoverflow.com/a/55410571/7290562
    BACKEND = "redis://{}:6379".format("rd01")
    BROKER = "redis://{}:6379/0".format("rd01")
    if _CELERY is False:
        return Celery(__name__, backend=BACKEND, broker=BROKER)
    app = Flask(__name__)
    app.config["WTF_CSRF_SECRET_KEY"] = "A SECRET KEY"
    app.config["SECRET_KEY"] = "ANOTHER ONE"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/gooutsafe.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    db.create_all(app=app)

    celery_app = Celery(app.import_name, backend=BACKEND, broker=BROKER)

    # celery.conf.update(app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask

    return celery_app


celery_app = create_celery_app()


@celery_app.task()
def send_email_to_confirm_registration(to_email: str, to_name: str, with_toke: str):
    """
    Perform the celery task to send the email registration
    it take the following element
    :param to_email: Email to send the message
    :param to_name: The user name to send the message
    :param with_toke: The token of user on system
    """
    send_registration_confirm(to_email, to_name, with_toke)


@celery_app.task()
def send_alert_new_covid19_about_previous_booking(
    to_email: str, to_name: str, email_user: str, restaurant_name: str
):
    """
    Perform the send email with celery async task to send a email to all restaurants with a booking from the person
    positive to covid19.
    :param to_email:
    :param to_name:
    :param email_user:
    :param restaurant_name:
    :return:
    """
    send_positive_booking_in_restaurant(to_email, to_name, email_user, restaurant_name)


@celery_app.task()
def send_positive_in_restaurant_celery(
    to_email: str, to_name: str, date_possible_contact: str, restaurant_name: str
):
    """
    Perform the send email with celery async task to send an email to the restaurant where a new positive cases was
    """
    send_positive_in_restaurant(
        to_email, to_name, date_possible_contact, restaurant_name
    )


@celery_app.task()
def send_possible_positive_contact_to_friend_celery(
    to_email: str, date_possible_contact: str, restaurant_name: str
):
    """
    Perform the send email with celery async task to send an email to friends with a reservation
    :param to_email:
    :param date_possible_contact:
    :param restaurant_name:
    """
    send_possible_positive_contact_to_friend(
        to_email, date_possible_contact, restaurant_name
    )


@celery_app.task()
def send_possible_positive_contact_celery(
    to_email: str, to_name: str, date_possible_contact: str, restaurant_name: str
):
    """
    Perform the send email with celery async task to send an email to the customer in a restaurants where a new positive
    case was
    :param to_email:
    :param to_name:
    :param date_possible_contact:
    :param restaurant_name:
    """
    send_possible_positive_contact(
        to_email, to_name, date_possible_contact, restaurant_name
    )


@celery_app.task()
def send_booking_confirmation_to_friends_celery(
    to_email: str, to_name: str, to_restaurants: str, to_friend_list: [], date_time
):
    """

    :param to_email:
    :param to_name:
    :param to_restaurants:
    :param to_friend_list:
    :param date_time:
    :return:
    """
    send_booking_confirmation_to_friends(
        to_email, to_name, to_restaurants, to_friend_list, date_time
    )


@celery_app.task
def calculate_rating_about_restaurant(restaurants_id: int):
    """
    This celery task is called inside the monolith app after a new review
    this give the possibility to maintain the the rating update and run a big task
    only to balance one time of day the rating.
    e.g: the task that we can run one  time per day is calculate_rating_for_all_celery
    :param restaurants_id: the restaurants id were the new review was created
    :return: the rating, only to have some feedback
    """
    RestaurantServices.get_rating_restaurant(restaurants_id)


@celery_app.task
def calculate_rating_for_all_celery():
    """
    This method is called inside a periodic task initialized below.
    The work of this task if get all restaurants inside the database and
    calculate the rating for each restaurants.
    """
    RestaurantServices.calculate_rating_for_all()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    This task make a calculation of review rating inside each
    this task take the db code and call the RestaurantServices for each restaurants
    """
    # Calls RestaurantServices.calculate_rating_for_all() every 30 seconds
    sender.add_periodic_task(30.0, calculate_rating_for_all_celery.s(), name="Rating")
