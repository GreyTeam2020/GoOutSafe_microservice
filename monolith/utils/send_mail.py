from flask import Flask
from flask_mail import Mail, Message
import os

# Methods and configuration for send email
app = Flask(__name__)
app.config.from_pyfile(os.path.join("..", "config/app.config"), silent=False)

# EMAIL CONFIG
app.config["MAIL_SERVER"] = app.config.get("MAIL_SERVER")
app.config["MAIL_PORT"] = app.config.get("MAIL_PORT")
app.config["MAIL_USERNAME"] = app.config.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = app.config.get("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = app.config.get("MAIL_USE_TLS")
app.config["MAIL_USE_SSL"] = app.config.get("MAIL_USE_SSL")
mail = Mail(app)


def send_possible_positive_contact(
    to_email, to_name, date_possible_contact, restaurant_name
):
    """
    Compose positive COVID-19 contact notification email template and sends to customer
    """
    subject = "Possible COVID-19 contact"
    body = (
        "Hi {toName},<br>"
        'you had a possible COVID-19 contact at restaurant "{restaurantName}" in date {datePossibleContact}.<br> '
        "<br>Please contact authority at 911 and follow regulations at the following link:<br> "
        "http://www.salute.gov.it/portale/nuovocoronavirus/homeNuovoCoronavirus.jsp<br> "
    )
    body = body.replace("{toName}", to_name)
    body = body.replace("{restaurantName}", restaurant_name)
    body = body.replace("{datePossibleContact}", date_possible_contact)
    send_email(subject, body, to_email)


def send_reservation_confirm(
    to_email, to_name, date_reservation, restaurant_name, number_seat
):
    """
    Compose reservation confirm email template and sends to customer
    """
    subject = "Reservation confirmed"
    body = (
        "Hi {toName},<br>"
        "we are glad to confirm your table for {numberSeat} people "
        'at restaurant "{restaurantName}" in date {dateReservation}<br> '
        "<br>See you soon!<br> "
    )
    body = body.replace("{toName}", to_name)
    body = body.replace("{restaurantName}", restaurant_name)
    body = body.replace("{dateReservation}", date_reservation)
    body = body.replace("{numberSeat}", str(number_seat))
    send_email(subject, body, to_email)


def send_reservation_notification(
    to_email,
    to_name,
    restaurant_name,
    customer_name,
    date_reservation,
    table_number,
    number_seat,
):
    """
    Compose reservation notification email template and sends to operator
    """
    subject = "Reservation notification"
    body = (
        "Hi {toName} from {restaurantName},<br>"
        "you have a new reservation:<br>"
        "<ul>"
        "<li>customer name: {customerName}</li>"
        "<li>number of seats: {numberSeat}</li>"
        "<li>date: {dateReservation}</li>"
        "<li>table number: {tableNumber}</li>"
        "</ul>"
        "See you soon! "
    )
    body = body.replace("{toName}", to_name)
    body = body.replace("{restaurantName}", restaurant_name)
    body = body.replace("{customerName}", customer_name)
    # body = body.replace("{numberSeat}", str(numberSeat))
    body = body.replace("{dateReservation}", date_reservation)
    body = body.replace("{tableNumber}", str(table_number))
    send_email(subject, body, to_email)


def send_registration_confirm(to_email, to_name, token):
    """
    Compose registration confirm email template and sends to user
    """
    subject = "Confirm email"
    body = (
        "Hi {toName},<br>"
        "we are glad to have you in GoOutSafe but you must confirm your email"
        'by click on <a href="http://localhost:5000/confirme_mail?token={token}">this URL<a>.<br>'
        "<br>See you soon! "
    )
    body = body.replace("{toName}", to_name)
    body = body.replace("{token}", token)
    send_email(subject, body, to_email)


def send_email(subject, body, recipient):
    """
    Internal method for send email
    """
    subject = "[GoOutSafe] " + subject
    msg = Message(
        recipients=[recipient],
        sender="greyteam2020@gmail.com",
        html=body,
        subject=subject,
    )
    with app.app_context():
        mail.send(msg)


def send_positive_booking_in_restaurant(to_email, to_name, email_user, restaurant_name):
    """
    A positive COVID-19 booked in a restaurant
    """
    subject = "A COVID-19 positive person has a booking in your restaurant"
    body = """ 
        Hi {toName},<br>
        we inform you that the user with email {emalUser}, who is Covid19 positive, has a booking in your restaurant "{restaurantName}"<br>
        """
    body = body.replace("{toName}", to_name)
    body = body.replace("{restaurantName}", restaurant_name)
    body = body.replace("{emalUser}", email_user)
    send_email(subject, body, to_email)


def send_possible_positive_contact_to_friend(
    to_email, date_possible_contact, restaurant_name
):
    """
    Compose positive COVID-19 contact notification email template and sends to customer
    """
    subject = "Possible COVID-19 contact"
    body = (
        "Hi,<br>"
        'you had a possible COVID-19 contact at restaurant "{restaurantName}" in date {datePossibleContact}.<br> '
        "<br>Please contact authority at 911 and follow regulations at the following link:<br> "
        "http://www.salute.gov.it/portale/nuovocoronavirus/homeNuovoCoronavirus.jsp<br> "
    )
    body = body.replace("{restaurantName}", restaurant_name)
    body = body.replace("{datePossibleContact}", date_possible_contact)
    send_email(subject, body, to_email)


def send_positive_in_restaurant(
    to_email, to_name, date_possible_contact, restaurant_name
):
    """
    Compose positive COVID-19 contact notification email template and sends to customer
    """
    subject = "Possible COVID-19 in your restaurant"
    body = (
        "Hi {toName},<br>"
        'a COVID-19 person was in your restaurant "{restaurantName}" in date {datePossibleContact}.<br> '
        "<br>Please contact authority at 911.<br> "
    )
    body = body.replace("{toName}", to_name)
    body = body.replace("{restaurantName}", restaurant_name)
    body = body.replace("{datePossibleContact}", date_possible_contact)
    send_email(subject, body, to_email)


def _send_booking_confirmation_to_owner_table(
    to_email: str, to_name: str, to_restaurants: str, date_time
):
    """
    TODO add the position on the map
    This method send the confirmation email to the owner of reservation
    :param to_email: The owner email
    :param to_name: The name of owner
    :param to_restaurants: Tha name of restaurant
    :param date_time: The date of booking
    """
    subject = "New Reservation in {toRestaurants}"
    body = """ 
        Hi {toName},<br>
        Your Reservation in {toRestaurants} was accepted on {toDate}.
        <br>Regards.<br> 
        <br>GoOutSafe Team</br>
        """
    body = body.replace("{toRestaurants}", to_restaurants)
    body = body.replace("{toName}", to_name)
    body = body.replace("{toRestaurants}", to_restaurants)
    body = body.replace("{toDate}", str(date_time))
    send_email(subject, body, to_email)


def _send_booking_confirmation_to_friend(
    to_friend: str, to_name: str, to_restaurants: str, date_time
):
    """
    TODO add the position on the map
    This method send the confirmation email to a email friend with the name of the
    :param to_friend:
    :param to_name:
    :param date_time:
    :param to_restaurants: Tha name of restaurant
    :return:
    """
    subject = "New Reservation in {toRestaurants}"
    body = """ 
        Hi {toName},<br>
        You have a reservation in {toRestaurants} by {toName} in {toDate}.
        <br>Regards.<br> 
        <br>GoOutSafe Team</br>
        """
    body = body.replace("{toRestaurants}", to_restaurants)
    body = body.replace("{toName}", to_name)
    body = body.replace("{toRestaurants}", to_restaurants)
    body = body.replace("{toDate}", str(date_time))
    send_email(subject, body, to_friend)


def send_booking_confirmation_to_friends(
    to_email: str, to_name: str, to_restaurants: str, to_friend_list: [], date_time
):
    """
    This is the method to share the booking information with a email to all friends,
    that are inside the booking.
    :param to_email:
    :param to_name:
    :param to_friend_list:
    :param date_time:
    """
    _send_booking_confirmation_to_owner_table(
        to_email=to_email,
        to_name=to_name,
        to_restaurants=to_restaurants,
        date_time=date_time,
    )
    for friend in to_friend_list:
        _send_booking_confirmation_to_friend(
            to_name=to_name,
            to_friend=friend,
            to_restaurants=to_restaurants,
            date_time=date_time,
        )
