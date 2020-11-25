from flask import current_app
from monolith.utils.http_utils import HttpUtils
from datetime import datetime, timedelta
from monolith.services import UserService
from monolith.services.send_email_service import SendEmailService
from monolith.services.booking_services import BookingServices
from monolith.services.restaurant_services import RestaurantServices
from monolith.app_constant import *


class HealthyServices:
    """
    This class is a service that has inside it all the component
    to make all REST call with other services about healthy authority
    """

    @staticmethod
    def report_positive():
        """
        This method call the user service to get all the positive
        """
        return UserService.get_list_of_positive_user()

    @staticmethod
    def mark_positive(user_email: str = None, user_phone: str = None) -> str:
        if user_email is None and user_phone is None:
            return "Insert an email or a phone number"
        response = UserService.mark_positive(user_email, user_phone)
        if response is not None:
            contacts = HealthyServices.search_contacts_for_email(user_email, user_phone)
            SendEmailService.send_possible_contact(contacts)  ## We assume that is true
            return ""
        else:
            return "An error occurs, please try again"

    @staticmethod
    def unmark_positive(user_email: str = None, user_phone: str = None) -> str:
        """
        This method perform the request to unmark th user as positive.
        """
        response = UserService.unmark_positive(user_email, user_phone)
        if response[0] is None:
            return "An error occurs"
        if response[1] == 400:
            return "An error occurs, please try again"
        if response[1] == 404:
            # Logic error make the check of the user inside the UI
            # If the user don't exist we don't need to perform the request
            return "The customer not registered or not positive"

        if response[1] == 200:
            return ""
        return "Error on Server please try again."

    @staticmethod
    def search_contacts(user_email: str, user_phone: str):
        if user_email == "" and user_phone == "":
            return "Insert an email or a phone number"
        response = UserService.search_possible_contacts(user_email, user_phone)

        if response is None:
            return "The customer not registered or not positive"

        contact_users_GUI = []
        # now we have the information about the positivity of the user in response
        date_marking = response["from_date"]
        user_id = response["user_id"]

        # start to check contacts
        # API: get all reservation of the customer between date_marking and date_marking -14
        date_marking = datetime.strptime(date_marking, "%Y-%m-%d")
        to_date = date_marking - timedelta(days=14)
        reservations_customer = BookingServices.get_reservation_by_constraint(
            user_id, from_data=to_date, to_data=date_marking
        )

        i = 1
        if reservations_customer is not None:
            all_reservations = BookingServices.get_reservation_by_constraint(
                from_data=to_date, to_data=date_marking
            )
            if all_reservations is None:
                return None

            for reservation in reservations_customer:
                restaurant_id = reservation["table"]["restaurant"]["id"]

                start = datetime.strptime(
                    reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ"
                )
                end = datetime.strptime(
                    reservation["reservation_end"], "%Y-%m-%dT%H:%M:%SZ"
                )
                current_app.logger.debug(
                    "I'm working with reserv from {} to {}".format(start, end)
                )
                for one_reservation in all_reservations:
                    restaurant_id_contact = one_reservation["table"]["restaurant"]["id"]
                    if restaurant_id_contact != restaurant_id:
                        continue
                    start_contact = datetime.strptime(
                        one_reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    end_contact = datetime.strptime(
                        one_reservation["reservation_end"], "%Y-%m-%dT%H:%M:%SZ"
                    )

                    # if people are in the same restaurant in the same day
                    if start.date() == start_contact.date():
                        openings = RestaurantServices.get_opening_hours_restaurant(
                            restaurant_id
                        )

                        dayNumber = start.weekday()
                        restaurant_hours = []
                        current_app.logger.debug(
                            "I got openings. Start is {}".format(dayNumber)
                        )
                        for opening in openings:
                            if opening["week_day"] == dayNumber:
                                restaurant_hours.append(
                                    datetime.strptime(opening["open_lunch"], "%H:%M")
                                )
                                restaurant_hours.append(
                                    datetime.strptime(opening["close_lunch"], "%H:%M")
                                )
                                restaurant_hours.append(
                                    datetime.strptime(opening["open_dinner"], "%H:%M")
                                )
                                restaurant_hours.append(
                                    datetime.strptime(opening["close_dinner"], "%H:%M")
                                )

                        # if people are in the restaurant at lunch or dinner
                        if (
                            restaurant_hours[0].time() <= start.time()
                            and restaurant_hours[1].time() >= end.time()
                        ) or (
                            restaurant_hours[2].time() <= start.time()
                            and restaurant_hours[3].time() >= end.time()
                        ):
                            # people are in the same restaurant at lunch
                            # if they are in the same time
                            if (end_contact < start or start_contact > end) is False:
                                # they are contacts!
                                # API: get user email and name of the contact
                                user = UserService.get_user_by_id(
                                    one_reservation["customer_id"]
                                )
                                if user is not None:
                                    contact_users_GUI.append(
                                        [
                                            i,
                                            user.firstname + " " + user.lastname,
                                            user.dateofbirth,
                                            user.email,
                                            user.phone,
                                        ]
                                    )
                                    i += 1
        return contact_users_GUI

    @staticmethod
    def search_contacts_for_email(user_email: str, user_phone: str):

        if user_email == "" and user_phone == "":
            return "Insert an email or a phone number"

        friends = []
        contacts = []
        past_restaurants = []
        future_restaurants = []

        if user_email != "":
            URL = USER_MICROSERVICE_URL + "/positiveinfo/email/" + str(user_email)
        else:
            URL = USER_MICROSERVICE_URL + "/positiveinfo/phone/" + str(user_phone)

        # check if the user exists
        # check if the user is positive (get also date of marking) (API)
        response = HttpUtils.make_get_request(URL)
        if response is None:
            return "Error, please try again"

        # now we have the information about the positivity of the user in response
        date_marking = response["from_date"]
        user_id = response["user_id"]

        # start to check contacts
        # API: get all reservation of the customer between date_marking and date_marking -14
        date_marking = datetime.strptime(date_marking, "%Y-%m-%d")
        to_date = date_marking - timedelta(days=14)
        reservations_customer = BookingServices.get_reservation_by_constraint(
            user_id, from_data=to_date, to_data=date_marking
        )

        if reservations_customer is not None:

            # API: get all reservations between date_marking and date_m -14
            all_reservations = BookingServices.get_reservation_by_constraint(
                from_data=to_date, to_data=date_marking
            )
            for reservation in reservations_customer:
                restaurant_id = reservation["table"]["restaurant"]["id"]
                restaurant = RestaurantServices.get_rest_by_id(restaurant_id)
                if restaurant is None:
                    continue
                friends = friends + reservation["people"]
                start = datetime.strptime(
                    reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ"
                )
                end = datetime.strptime(
                    reservation["reservation_end"], "%Y-%m-%dT%H:%M:%SZ"
                )
                past_restaurants.append(
                    {
                        "email": restaurant.owner_email,
                        "name": restaurant.name,
                        "date": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                )
                for one_reservation in all_reservations:
                    restaurant_id_contact = one_reservation["table"]["restaurant"]["id"]
                    if restaurant_id_contact != restaurant_id:
                        continue

                    start_contact = datetime.strptime(
                        one_reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    end_contact = datetime.strptime(
                        one_reservation["reservation_end"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    # if people are in the same restaurant in the same day
                    if start.date() != start_contact.date():
                        continue
                    openings = RestaurantServices.get_opening_hours_restaurant(
                        restaurant_id
                    )

                    dayNumber = start.weekday()
                    restaurant_hours = []
                    for opening in openings:
                        if opening["week_day"] == dayNumber:
                            restaurant_hours.append(
                                datetime.strptime(opening["open_lunch"], "%H:%M")
                            )
                            restaurant_hours.append(
                                datetime.strptime(opening["close_lunch"], "%H:%M")
                            )
                            restaurant_hours.append(
                                datetime.strptime(opening["open_dinner"], "%H:%M")
                            )
                            restaurant_hours.append(
                                datetime.strptime(opening["close_dinner"], "%H:%M")
                            )

                    # if people are in the restaurant at lunch or dinner
                    if (
                        restaurant_hours[0].time() <= start.time()
                        and restaurant_hours[1].time() >= end.time()
                    ) or (
                        restaurant_hours[2].time() <= start.time()
                        and restaurant_hours[3].time() >= end.time()
                    ):
                        # people are in the same restaurant at lunch
                        # if they are in the same time
                        if not ((end_contact < start) or (start_contact > end)):
                            # they are contacts!
                            # API: get user email and name of the contact
                            user = UserService.get_user_by_id(
                                one_reservation["customer_id"]
                            )
                            if user is not None:
                                contacts.append(
                                    {
                                        "email": user.email,
                                        "name": user.firstname,
                                        "restaurant_name": restaurant.name,
                                        "date": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    }
                                )
                                friends = friends + one_reservation["people"]
        if user_email != "":
            customer_email = user_email
        else:
            URL = USER_MICROSERVICE_URL + "/" + str(user_id)
            user = HttpUtils.make_get_request(URL)
            customer_email = user["email"]

        # API booking: get all future booking of the customer
        future_reservations = BookingServices.get_reservation_by_constraint(
            user_id, from_data=to_date, to_data=date_marking
        )
        for future_reservation in future_reservations:
            date = datetime.strptime(
                reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ"
            )
            restaurant_id = future_reservation["table"]["restaurant"]["id"]
            restaurant = RestaurantServices.get_rest_by_id(restaurant_id)
            if restaurant is not None:
                future_restaurants.append(
                    {
                        "email": restaurant.owner_email,
                        "name": restaurant.name,
                        "date": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "customer_email": customer_email,
                    }
                )
        return {
            "friends": friends,
            "contacts": contacts,
            "past_restaurants": past_restaurants,
            "reservation_restaurants": future_restaurants,
        }
