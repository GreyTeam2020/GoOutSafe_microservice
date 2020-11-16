from .app import create_app
from .background import (
    calculate_rating_for_all_celery,
    calculate_rating_about_restaurant,
    celery_app as celery,
)
from .app_constant import *
