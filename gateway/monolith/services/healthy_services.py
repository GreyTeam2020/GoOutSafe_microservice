from flask import current_app
from monolith.utils.http_utils import HttpUtils
from monolith.app_constant import USER_MICROSERVICE_URL

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
        return response

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
     
        TODO CHIAMATE PER INVIO EMAIL A email_microservice
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
