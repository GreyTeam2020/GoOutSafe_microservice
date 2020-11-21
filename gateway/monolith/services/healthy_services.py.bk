from flask import current_app
from monolith.utils.http_utils import HttpUtils
from monolith.app_constant import USER_MICROSERVICE_URL

#DA RIMUOVERE
from monolith.database import (
    db,
    Positive,
    User,
    OpeningHours,
    RestaurantTable,
    Reservation,
    Restaurant,
    Friend,
)
from datetime import datetime, timedelta
from sqlalchemy import extract

from monolith.services import UserService
from monolith.tests.utils import get_user_with_id
from monolith.app_constant import *


class HealthyServices:
    """
    This class is an service that have inside it all the component
    to make all operation with db about healthy authority
    """

    @staticmethod
    def mark_positive(user_email: str = "", user_phone: str = "") -> str:
        """
        This method mark the a people as positive on db
        :param user_email:
        :param user_phone:
        :return: return a message
        """
        f = open("logger2.txt", "w")
        if len(user_email) == 0 and len(user_phone) == 0:
            return "Insert an email or a phone number"

        if len(user_email) != 0:
            q_user = (
                db.session.query(User).filter_by(email=user_email, role_id=3).first()
            )
        else:
            q_user = (
                db.session.query(User).filter_by(phone=user_phone, role_id=3).first()
            )

        if q_user is None:
            return "The customer is not registered"

        q_already_positive = (
            db.session.query(Positive).filter_by(user_id=q_user.id, marked=True).first()
        )

        f.write(
            "User "
            + str(q_user.email)
            + " positive status:"
            + str(q_already_positive)
            + "\n"
        )
        if q_already_positive is None:
            new_positive = Positive()
            new_positive.from_date = datetime.now()
            new_positive.marked = True
            new_positive.user_id = q_user.id

            db.session.add(new_positive)
            db.session.commit()
            f.write("Now he is positive\n")
            # start notification zone

            # to notify restaurants with a future booking of the positive customer
            restaurant_notified = []
            all_reservations = (
                db.session.query(Reservation)
                .filter(
                    Reservation.reservation_date >= datetime.now(),
                    Reservation.customer_id == new_positive.user_id,
                )
                .all()
            )
            f.write(
                "Restaurant with future bookings: " + str(len(all_reservations)) + "\n"
            )
            # for each future booking
            for reservation in all_reservations:
                restaurant = (
                    db.session.query(Restaurant)
                    .filter(
                        reservation.table_id == RestaurantTable.id,
                        RestaurantTable.restaurant_id == Restaurant.id,
                    )
                    .first()
                )

                if restaurant.id not in restaurant_notified:
                    f.write(" - " + restaurant.name + "\n")
                    restaurant_notified.append(restaurant.id)

                    q_owner = (
                        db.session.query(User)
                        .filter(User.id == restaurant.owner_id)
                        .first()
                    )

                    # Send the email!
                    DispatcherMessage.send_message(
                        NEW_COVID_TO_RESTAURANT_BOOKING,
                        [
                            q_owner.email,
                            q_owner.firstname,
                            q_user.email,
                            restaurant.name,
                        ],
                    )
                    f.write("\t\tEmail sent to " + q_owner.email + "\n")

            # to notify the restaurants for a possible positive inside the restaurant
            restaurant_notified = []
            user_notified = []

            all_reservations = (
                db.session.query(Reservation)
                .filter(
                    Reservation.reservation_date
                    >= (datetime.today() - timedelta(days=14)),
                    Reservation.reservation_date < datetime.now(),
                    Reservation.customer_id == q_user.id,
                    # Reservation.checkin is True,
                )
                .all()
            )
            f.write("There are " + str(len(all_reservations)) + " past reservations\n")
            for reservation in all_reservations:
                f.write(" - " + str(reservation.reservation_date) + "\n")
                this_table = (
                    db.session.query(RestaurantTable)
                    .filter_by(id=reservation.table_id)
                    .first()
                )
                restaurant = (
                    db.session.query(Restaurant)
                    .filter_by(id=this_table.restaurant_id)
                    .first()
                )

                opening = (
                    db.session.query(OpeningHours)
                    .filter(
                        OpeningHours.restaurant_id == restaurant.id,
                        OpeningHours.week_day == reservation.reservation_date.weekday(),
                    )
                    .first()
                )
                period = (
                    [opening.open_dinner, opening.close_dinner]
                    if (opening.open_dinner <= reservation.reservation_date.time())
                    else [opening.open_lunch, opening.close_lunch]
                )

                # Notify Restaurant for a positive that was inside
                if restaurant.id not in restaurant_notified:
                    restaurant_notified.append(restaurant.id)
                    owner = (
                        db.session.query(User).filter_by(id=restaurant.owner_id).first()
                    )

                    if owner is not None:
                        f.write("\t\tSending mail to owner\n")
                        # Send the email!
                        DispatcherMessage.send_message(
                            NEW_POSITIVE_WAS_IN_RESTAURANT,
                            [
                                owner.email,
                                owner.firstname,
                                str(reservation.reservation_date),
                                restaurant.name,
                            ],
                        )
                    else:
                        current_app.logger.debug(
                            "owner for restaurant {} not present".format(
                                restaurant.owner_id
                            )
                        )

                # notify friends of the positive customer
                friends_email = (
                    db.session.query(Friend.email)
                    .filter_by(reservation_id=reservation.id)
                    .all()
                )
                f.write(
                    "\t\tI have to notify " + str(len(friends_email)) + " friends\n"
                )
                # Mail to friends of the positive person

                for friend in friends_email:
                    friend = friend[0]
                    f.write("\t\t > " + friend + "\n")
                    DispatcherMessage.send_message(
                        EMAIL_TO_FRIEND,
                        [friend, str(reservation.reservation_date), restaurant.name],
                    )

                # send mail to contact
                query = db.session.query(RestaurantTable.id).filter_by(
                    restaurant_id=this_table.restaurant_id
                )
                restaurant_tables = [r.id for r in query]

                all_contacts = (
                    db.session.query(Reservation)
                    .filter(
                        extract("day", Reservation.reservation_date)
                        == extract("day", reservation.reservation_date),
                        extract("month", Reservation.reservation_date)
                        == extract("month", reservation.reservation_date),
                        extract("year", Reservation.reservation_date)
                        == extract("year", reservation.reservation_date),
                        extract("hour", Reservation.reservation_date)
                        >= extract("hour", period[0]),
                        extract("hour", Reservation.reservation_date)
                        <= extract("hour", period[1]),
                        Reservation.table_id.in_(restaurant_tables),
                        Reservation.customer_id != q_user.id,
                    )
                    .all()
                )
                f.write(
                    "\t\tI have to notify " + str(len(all_contacts)) + " contacts\n"
                )
                for contact in all_contacts:
                    if contact.customer_id not in user_notified:
                        user_notified.append(contact.customer_id)
                        thisuser = (
                            db.session.query(User)
                            .filter_by(id=contact.customer_id)
                            .first()
                        )
                        if thisuser is not None:
                            f.write("\t\t > sending email to " + thisuser.email + "\n")
                            # Send the email to customer!
                            DispatcherMessage.send_message(
                                NEW_POSITIVE_CONTACT,
                                [
                                    thisuser.email,
                                    thisuser.firstname,
                                    contact.reservation_date,
                                    restaurant.name,
                                ],
                            )

                        friends_email = (
                            db.session.query(Friend.email)
                            .filter_by(reservation_id=contact.id)
                            .all()
                        )
                        f.write(
                            "\t\t\t this contact had "
                            + str(len(friends_email))
                            + " friends\n"
                        )
                        # Mail to friends of people with this reservation
                        for friend in friends_email:
                            friend = friend[0]
                            f.write("\t\t\t > " + friend + "\n")
                            DispatcherMessage.send_message(
                                EMAIL_TO_FRIEND,
                                [
                                    friend,
                                    str(contact.reservation_date),
                                    restaurant.name,
                                ],
                            )

            return ""
        else:
            return "User with email {} already Covid-19 positive".format(user_email)

    @staticmethod
    def search_contacts(id_user):
        result = []
        f = open("logger.txt", "w")
        f.write("Starting searching for user " + str(id_user) + "\n")
        all_reservations = (
            db.session.query(Reservation)
            .filter(
                Reservation.reservation_date >= (datetime.today() - timedelta(days=14)),
                Reservation.reservation_date < datetime.now(),
                Reservation.customer_id == id_user,
                # Reservation.checkin is True,
            )
            .all()
        )
        f.write("All user reservations: " + str(len(all_reservations)) + "\n\n")

        for reservation in all_reservations:
            f.write(
                "Reservation: "
                + str(reservation.id)
                + " at "
                + str(reservation.reservation_date)
                + " in table "
                + str(reservation.table_id)
                + "\n"
            )
            this_table = (
                db.session.query(RestaurantTable)
                .filter_by(id=reservation.table_id)
                .first()
            )
            restaurant = (
                db.session.query(Restaurant)
                .filter_by(id=this_table.restaurant_id)
                .first()
            )

            f.write(
                "The restaurant was "
                + restaurant.name
                + " with id:"
                + str(this_table.restaurant_id)
                + "\n"
            )
            opening = (
                db.session.query(OpeningHours)
                .filter(
                    OpeningHours.restaurant_id == restaurant.id,
                    OpeningHours.week_day == reservation.reservation_date.weekday(),
                )
                .first()
            )
            period = (
                [opening.open_dinner, opening.close_dinner]
                if (opening.open_dinner <= reservation.reservation_date.time())
                else [opening.open_lunch, opening.close_lunch]
            )
            f.write("The time slot was " + str(period) + "\n")

            query = db.session.query(RestaurantTable.id).filter_by(
                restaurant_id=this_table.restaurant_id
            )
            restaurant_tables = [r.id for r in query]
            print(restaurant_tables)

            all_contacts = (
                db.session.query(Reservation)
                .filter(
                    extract("day", Reservation.reservation_date)
                    == extract("day", reservation.reservation_date),
                    extract("month", Reservation.reservation_date)
                    == extract("month", reservation.reservation_date),
                    extract("year", Reservation.reservation_date)
                    == extract("year", reservation.reservation_date),
                    extract("hour", Reservation.reservation_date)
                    >= extract("hour", period[0]),
                    extract("hour", Reservation.reservation_date)
                    <= extract("hour", period[1]),
                    Reservation.table_id.in_(restaurant_tables),
                )
                .all()
            )

            f.write("Found " + str(len(all_contacts)) + " contacts:\n")
            for contact in all_contacts:
                f.write("- " + get_user_with_id(contact.customer_id).email + "\n")
                if contact.customer_id not in result:
                    result.append(contact.customer_id)

        contact_users = []
        for user_id in result:
            user = get_user_with_id(user_id)
            if not UserService.is_positive(user.id):
                contact_users.append(
                    [
                        user.id,
                        user.firstname + " " + user.lastname,
                        str(user.dateofbirth).split()[0],
                        user.email,
                        user.phone,
                    ]
                )

        return contact_users


    @staticmethod
    def unmark_positive(user_email: str, user_phone: str) -> str:
        """
        This method mark the a people as positive on db
        :param user_email:
        :param user_phone:
        :return: return a message
        """
        if user_email == "" and user_phone == "":
            return "Insert an email or a phone number"
        
        if user_email != "":
                body= str({
                    "key": "email",
                    "value": user_email
                })
        else:
            body= str({
                    "key": "phone",
                    "value": user_phone
                })
        
        URL = USER_MICROSERVICE_URL+"/unmark"
        
        response = HttpUtils.make_put_request(URL, body)
        
        if response is None:
            return "An error occurs"

        if response[1] == 400:
            return "An error occurs, please try again"

        if response[1] == 200:
            return response[0]["result"]

        return "Erorr"