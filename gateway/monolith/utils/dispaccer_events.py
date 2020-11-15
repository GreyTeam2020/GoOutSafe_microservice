from monolith.background import (
    send_email_to_confirm_registration,
    send_alert_new_covid19_about_previous_booking,
    send_possible_positive_contact_to_friend,
    send_possible_positive_contact_celery,
    send_booking_confirmation_to_friends_celery,
    send_positive_in_restaurant,
    calculate_rating_about_restaurant,
)
from monolith.app_constant import *
from monolith.services.restaurant_services import RestaurantServices

_CELERY = False


class DispatcherMessage:
    """
    This class using a mediator patter to decide if the status of app admit
    the celery message.
    The celery message are available for the moment only in release and in some debug cases
    otherwise it is disabled.

    For instance, for the testing it is disabled.

    @author Vincenzo Palazzo v.palazzo1@studenti.unipi.it
    """

    @staticmethod
    def send_message(type_message: str, params):
        """
        This static method take and string that usually is defined inside the
        file app_constant.py and check if there is condition to dispatc the test
        :return: nothings
        """
        if _CELERY is False:
            if type_message == CALCULATE_RATING_RESTAURANTS:
                RestaurantServices.calculate_rating_for_all()
            elif type_message == CALCULATE_RATING_RESTAURANT:
                RestaurantServices.get_rating_restaurant(params[0])
            return
        if type_message == REGISTRATION_EMAIL:
            send_email_to_confirm_registration.apply_async(args=params)
        elif type_message == NEW_COVID_TO_RESTAURANT_BOOKING:
            send_alert_new_covid19_about_previous_booking.apply_async(args=params)
        elif type_message == NEW_POSITIVE_WAS_IN_RESTAURANT:
            send_positive_in_restaurant.apply_async(args=params)
        elif type_message == EMAIL_TO_FRIEND:
            send_possible_positive_contact_to_friend.apply_async(args=params)
        elif type_message == NEW_POSITIVE_CONTACT:
            send_possible_positive_contact_celery.apply_async(args=params)
        elif type_message == CONFIRMATION_BOOKING:
            send_booking_confirmation_to_friends_celery.apply_async(args=params)
        elif type_message == CALCULATE_RATING_RESTAURANT:
            calculate_rating_about_restaurant.apply_async(args=params)
