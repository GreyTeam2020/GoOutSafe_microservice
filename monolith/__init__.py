from .app import create_app
from .background import (
    send_email_to_confirm_registration,
    send_alert_new_covid19_about_previous_booking,
    send_positive_in_restaurant_celery,
    send_possible_positive_contact_to_friend_celery,
    send_possible_positive_contact_celery,
    send_booking_confirmation_to_friends_celery,
    calculate_rating_for_all_celery,
    calculate_rating_about_restaurant,
    celery_app as celery,
)
from .app_constant import *
