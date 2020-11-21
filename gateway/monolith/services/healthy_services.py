from flask import current_app
from monolith.utils.http_utils import HttpUtils
from monolith.app_constant import USER_MICROSERVICE_URL
from monolith.model import UserModel

from datetime import datetime, timedelta
from sqlalchemy import extract

from monolith.services import UserService
from monolith.tests.utils import get_user_with_id
from monolith.app_constant import *


class HealthyServices:
    """
    This class is a service that has inside it all the component
    to make all REST call with other services about healthy authority
    """

    @staticmethod
    def report_positive():
        # bind filter params...
        url = "{}/positive".format(USER_MICROSERVICE_URL)
        response = HttpUtils.make_get_request(url)
        users = response["result"]
        list_user = []
        for user in users:
            new_user = UserModel()
            new_user.fill_from_json(user)
            list_user.append(new_user)
        return list_user

    @staticmethod
    def mark_positive(user_email: str = "", user_phone: str = "") -> str:
        # bind filter params...
        if user_email is not None:
            key = "email"
            value = user_email
        elif user_phone is not None:
            key = "phone"
            value = user_phone
        else:
            return None
        url = "{}/mark/{}/{}".format(USER_MICROSERVICE_URL, key, value)
        response = HttpUtils.make_get_request(url)

        '''
        TODO: chiamata contact
        esempio risposta API contact
        {
           "friends":["aaa@aaa.it","bbbb@bbb.it","bbbb@bbb.it"],
           "contacts":["","",""],
           "past_restaurants":["","",""],
           "reservation_restaurants":["","",""]
        }
        la risposta viene mandata come request body al email_microservice per notificare i contatti 
        il servizio prende le 4 liste, per ognuna cicla ed invia una mail ad ogni indirizzo
        
        ELEIMINARE, SONO LE VECCHIE CHIAMATE PER INVIO EMAIL, VENGONO MESSE IN email_microservice
         DispatcherMessage.send_message(
                    NEW_COVID_TO_RESTAURANT_BOOKING,
                    [
                        q_owner.email,
                        q_owner.firstname,
                        q_user.email,
                        restaurant.name,
                    ],
                )
        

         DispatcherMessage.send_message(
            NEW_POSITIVE_WAS_IN_RESTAURANT,
            [
                owner.email,
                owner.firstname,
                str(reservation.reservation_date),
                restaurant.name,
            ],
        )


         DispatcherMessage.send_message(
            EMAIL_TO_FRIEND,
            [friend, str(reservation.reservation_date), restaurant.name],
        )

        DispatcherMessage.send_message(
            NEW_POSITIVE_CONTACT,
            [
                thisuser.email,
                thisuser.firstname,
                contact.reservation_date,
                restaurant.name,
            ],
        )


         DispatcherMessage.send_message(
            EMAIL_TO_FRIEND,
            [
                friend,
                str(contact.reservation_date),
                restaurant.name,
            ],
        )
        '''

        return response


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
            body = str({
                "key": "email",
                "value": user_email
            })
        else:
            body = str({
                "key": "phone",
                "value": user_phone
            })

        URL = USER_MICROSERVICE_URL + "/unmark"

        response = HttpUtils.make_put_request(URL, body)

        if response is None:
            return "An error occurs"

        if response[1] == 400:
            return "An error occurs, please try again"

        if response[1] == 200:
            return response[0]["result"]

        return "Error"
