from flask import Blueprint, render_template, session, abort
from flask_login import current_user
from monolith.database import (
    db,
    Restaurant,
    Positive,
)
from monolith.forms import ReservationForm
from monolith.services import (
    UserService,
    RestaurantServices,
)
from monolith.utils import DispatcherMessage
from monolith.app_constant import CALCULATE_RATING_RESTAURANTS

home = Blueprint("home", __name__)


@home.route("/")
def index():
    DispatcherMessage.send_message(CALCULATE_RATING_RESTAURANTS, [])
    restaurants = db.session.query(Restaurant).all()
    if current_user is None:
        _test = "anonymous_test"
    else:
        _test = "logged_test"
    if "ROLE" in session:
        if session["ROLE"] == "HEALTH":
            n_positive = db.session.query(Positive).filter_by(marked=True).count()
            n_healed = (
                db.session.query(Positive)
                .filter_by(marked=False)
                .distinct(Positive.user_id)
                .count()
            )
            return render_template(
                "index_health.html",
                _test=_test,
                n_positive=n_positive,
                n_healed=n_healed,
            )
        elif session["ROLE"] == "OPERATOR":
            if "RESTAURANT_ID" in session:
                restaurant_id = session["RESTAURANT_ID"]
                model = RestaurantServices.get_all_restaurants_info(restaurant_id)
                if model is None:
                    abort(501)
                weekDaysLabel = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                # record = (
                #    db.session.query(Restaurant)
                #    .filter_by(id=int(restaurant_id))
                #    .first()
                # )

                # q_hours = (
                #    db.session.query(OpeningHours)
                #    .filter_by(restaurant_id=int(restaurant_id))
                #    .all()
                # )
                # q_cuisine = (
                #    db.session.query(Menu)
                #    .filter_by(restaurant_id=int(restaurant_id))
                #    .all()
                # )
                # photos = PhotoGallery.query.filter_by(
                #    restaurant_id=int(restaurant_id)
                # ).all()
                # dishes = (
                #    db.session.query(MenuDish)
                #    .filter_by(restaurant_id=restaurant_id)
                #    .all()
                # )

                return render_template(
                    "restaurantsheet.html",
                    id=restaurant_id,
                    name=model.name,
                    lat=model.lat,
                    lon=model.lon,
                    phone=model.phone,
                    covid_measures=model.covid_measures,
                    hours=model.opening_hours,
                    cuisine=model.cusine,
                    weekDaysLabel=weekDaysLabel,
                    photos=model.photos,
                    reviews=RestaurantServices.get_three_reviews(restaurant_id),
                    dishes=model.dishes,
                    _test=_test,
                )
            else:
                return render_template("norestaurant.html", _test=_test)
        elif session["ROLE"] == "CUSTOMER":
            form = ReservationForm()
            is_positive = UserService.is_positive(current_user.id)
            return render_template(
                "index_customer.html",
                _test=_test,
                restaurants=restaurants,
                form=form,
                is_positive=is_positive,
            )

    return render_template("index.html", _test=_test, restaurants=restaurants)
