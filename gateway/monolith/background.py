from celery import Celery
from flask import Flask

from monolith.database import db
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
