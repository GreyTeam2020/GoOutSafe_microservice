from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    current_app,
    abort,
)
from monolith.database import (
    db,
    Restaurant,
    User,
    RestaurantTable,
    OpeningHours,
    Menu,
    PhotoGallery,
    MenuDish,
)
from monolith.forms import PhotoGalleryForm, ReviewForm, ReservationForm, DishForm
from monolith.services import RestaurantServices
from monolith.auth import roles_allowed
from flask_login import current_user, login_required
from monolith.forms import RestaurantForm, RestaurantTableForm
from monolith.utils.formatter import my_date_formatter_iso
from monolith.app_constant import CALCULATE_RATING_RESTAURANT
from monolith.services.user_service import UserService

restaurants = Blueprint("restaurants", __name__)

_max_seats = 6


@restaurants.route("/restaurant/<restaurant_id>")
def restaurant_sheet(restaurant_id):
    """
    Missing refactoring to services
    :param restaurant_id:
    """
    weekDaysLabel = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    # record = db.session.query(Restaurant).filter_by(id=int(restaurant_id)).all()
    # if record is not None:
    #    record = record[0]

    model = RestaurantServices.get_all_restaurants_info(restaurant_id)
    if model is None:
        ##TODO FIX THIS with a message in a view
        abort(501)

    # q_hours = db.session.query(OpeningHours).filter_by(restaurant_id=int(restaurant_id)).all()
    # q_cuisine = db.session.query(Menu).filter_by(restaurant_id=int(restaurant_id)).all()
    # photos = PhotoGallery.query.filter_by(restaurant_id=int(restaurant_id)).all()
    # dishes = db.session.query(MenuDish).filter_by(restaurant_id=restaurant_id).all()

    review_form = ReviewForm()
    book_form = ReservationForm()

    return render_template(
        "restaurantsheet.html",
        weekDaysLabel=weekDaysLabel,
        id=restaurant_id,
        name=model.name,
        lat=model.lat,
        lon=model.lon,
        phone=model.phone,
        covid_measures=model.covid_measures,
        hours=model.opening_hours,
        cuisine=model.cusine,
        photos=model.photos,
        dishes=model.dishes,
        review_form=review_form,
        book_form=book_form,
        reviews=RestaurantServices.get_three_reviews(restaurant_id),
        _test="visit_rest_test",
    )


@restaurants.route("/restaurant/create", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def create_restaurant():
    """
    This flask method give the possibility with a POST request to create a new
    restaurant inside the system
    """
    form = RestaurantForm()
    if request.method == "POST":
        # TODO check why it's not working this if statement below
        # if form.validate_on_submit():
        current_app.logger.debug(
            "Check if user {} si present".format(current_user.email)
        )
        user = UserService.user_is_present(current_user.email)
        if user is None:
            return render_template(
                "create_restaurant.html",
                _test="anonymus_user_test",
                form=form,
                message="User not logged",
            )

        # create the restaurant
        newrestaurant = RestaurantServices.create_new_restaurant(
            form, current_user.id, _max_seats
        )
        if newrestaurant is None:
            return render_template(
                "create_restaurant.html",
                _test="create_rest_failed",
                form=form,
                message="Error on create services",
            )
        session["RESTAURANT_ID"] = newrestaurant.id
        session["RESTAURANT_NAME"] = newrestaurant.name
        return redirect("/")
    return render_template(
        "create_restaurant.html", _test="create_rest_test", form=form
    )


@restaurants.route("/restaurant/reservations")
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_reservations():
    # http://localhost:5000/my_reservations?fromDate=2013-10-07&toDate=2014-10-07&email=john.doe@email.com

    # for security reason, that are retrive on server side, not passed by params
    owner_id = current_user.id
    restaurant_id = session["RESTAURANT_ID"]

    # filter params
    fromDate = request.args.get("fromDate", type=str)
    toDate = request.args.get("toDate", type=str)
    email = request.args.get("email", type=str)

    reservations_as_list = RestaurantServices.get_reservation_rest(
        owner_id, restaurant_id, fromDate, toDate, email
    )
    print(RestaurantServices.get_restaurant_people(restaurant_id))
    return render_template(
        "reservations.html",
        _test="restaurant_reservations_test",
        reservations_as_list=reservations_as_list,
        my_date_formatter_iso=my_date_formatter_iso,
        reservations_n=RestaurantServices.get_restaurant_people(restaurant_id),
    )


@restaurants.route("/restaurant/data", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_data():
    """
    TODO(vincenzopalazzo) add information
    This API call give the possibility to the user TODO
    """
    message = None
    if request.method == "POST":
        # update restaurant
        restaurant_modified = RestaurantServices.update_restaurant(
            session["RESTAURANT_ID"],
            request.form.get("name"),
            request.form.get("lat"),
            request.form.get("lon"),
            request.form.get("covid_measures"),
        )
        # if no resturant match the update query (session problem probably)
        if restaurant_modified:
            message = "Some errors occurs during modification. PLease try again later"
        else:
            message = "Restaurant data has been modified."

    # get the resturant info and fill the form
    # this part is both for POST and GET requests
    restaurant = RestaurantServices.get_rest_by_id(session["RESTAURANT_ID"])
    if restaurant is not None:
        form = RestaurantForm(obj=restaurant)
        form2 = RestaurantTableForm()
        # get all tables
        tables = RestaurantServices.get_restaurant_tables(session["RESTAURANT_ID"])
        return render_template(
            "restaurant_data.html",
            form=form,
            only=["name", "lat", "lon", "covid_measures"],
            tables=tables,
            form2=form2,
            message=message,
        )
    else:
        return redirect("/restaurant/create")


@restaurants.route("/restaurant/tables", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_tables():
    if request.method == "POST":
        # insert the table with data provided by the form
        table = RestaurantTable()
        table.restaurant_id = session["RESTAURANT_ID"]
        table.max_seats = request.form.get("capacity")
        table.name = request.form.get("name")
        db.session.add(table)
        db.session.commit()
        ##
        return redirect("/restaurant/data")

    elif request.method == "GET":
        # delete the table specified by the get request
        RestaurantTable.query.filter_by(id=request.args.get("id")).delete()
        db.session.commit()
        return redirect("/restaurant/data")


@restaurants.route("/restaurant/menu", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_menu():
    if "RESTAURANT_ID" in session:
        dishes = MenuDish.query.filter_by(restaurant_id=session["RESTAURANT_ID"]).all()
    else:
        dishes = []
    _test = "menu_view_test"
    if request.method == "POST":
        form = DishForm()
        # add dish to the db
        if form.validate_on_submit():
            dish = MenuDish()
            dish.name = form.data["name"]
            dish.price = form.data["price"]
            dish.restaurant_id = session["RESTAURANT_ID"]
            db.session.add(dish)
            db.session.commit()
            dishes.append(dish)
            _test = "menu_ok_test"
        else:
            _test = "menu_ko_form_test"
            print(form.errors)
            return render_template(
                "restaurant_menu.html",
                _test=_test,
                form=form,
                dishes=dishes,
                error=form.errors,
            )
    form = DishForm()
    return render_template(
        "restaurant_menu.html",
        _test=_test,
        form=form,
        dishes=dishes,
    )


@restaurants.route("/restaurant/menu/delete/<dish_id>")
@login_required
@roles_allowed(roles=["OPERATOR"])
def delete_dish(dish_id):
    db.session.query(MenuDish).filter_by(id=dish_id).delete()
    db.session.commit()
    return redirect("/restaurant/menu")


@restaurants.route("/restaurant/photogallery", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["OPERATOR"])
def my_photogallery():
    if request.method == "POST":
        form = PhotoGalleryForm()
        # add photo to the db
        if form.validate_on_submit():
            photo_gallery = PhotoGallery()
            photo_gallery.caption = form.data["caption"]
            photo_gallery.url = form.data["url"]
            photo_gallery.restaurant_id = session["RESTAURANT_ID"]
            db.session.add(photo_gallery)
            db.session.commit()

        return redirect("/restaurant/photogallery")
    else:
        photos = PhotoGallery.query.filter_by(
            restaurant_id=session["RESTAURANT_ID"]
        ).all()
        form = PhotoGalleryForm()
        return render_template("photogallery.html", form=form, photos=photos)


@restaurants.route("/restaurant/review/<restaurant_id>", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["CUSTOMER"])
def restaurant_review(restaurant_id):
    if request.method == "POST":
        form = ReviewForm()
        review = RestaurantServices.review_restaurant(
            restaurant_id, current_user.emai, form.data["stars"], form.data["review"]
        )
        if review is not None:
            current_app.logger.debug("Review inserted!")
            return render_template(
                "review.html",
                _test="review_done_test",
                restaurant_name=RestaurantServices.get_restaurant_name(restaurant_id),
                review=review,
            )
        DispatcherMessage.send_message(CALCULATE_RATING_RESTAURANT, [restaurant_id])
        current_app.logger.debug("New rating event ran")
    return render_template(
        "review.html",
        _test="review_done_test",
        error="An error occur inserting the review. Try again later.",
    )


@restaurants.route("/restaurant/search/<name_rest>", methods=["GET"])
def search_restaurant(name_rest):
    current_app.logger.debug(
        "An user want search a restaurant with name {}".format(name_rest)
    )

    file = "index.html"
    if "ROLE" in session and session["ROLE"] == "CUSTOMER":
        file = "index_customer.html"

    form = ReservationForm()
    filter_by_name = RestaurantServices.get_restaurants_by_keyword(name=name_rest)
    return render_template(
        file,
        _test="rest_search_test",
        restaurants=filter_by_name,
        search=name_rest,
        form=form,
    )


@restaurants.route("/restaurant/checkinreservations/<reservation_id>")
@login_required
@roles_allowed(roles=["OPERATOR"])
def checkin_reservations(reservation_id):
    RestaurantServices.checkin_reservations(reservation_id)
    return redirect("/restaurant/reservations")
