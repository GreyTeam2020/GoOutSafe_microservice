from flask import Blueprint, render_template, session, abort
from flask_login import current_user
from src.database import (
    db,
    Restaurant,
    Positive,
)
from src.forms import ReservationForm
from src.services import (
    UserService,
    RestaurantServices,
)

home = Blueprint("home", __name__)


@home.route("/")
def index():
    restaurants = RestaurantServices.get_all_restaurants()
    if current_user is None:
        _test = "anonymous_test"
    else:
        _test = "logged_test"
    if "ROLE" in session:
        if session["ROLE"] == "HEALTH":
            positives = UserService.get_count_of_positive_user()

            return render_template(
                "index_health.html",
                _test=_test,
                n_positive=positives
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
