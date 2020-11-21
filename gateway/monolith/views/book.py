from flask import Blueprint, render_template, request
from monolith.forms import ReservationForm
from monolith.auth import current_user
from monolith.services.user_service import UserService
from monolith.utils.formatter import my_date_formatter_iso
import datetime

from flask_login import login_required

from monolith.auth import roles_allowed

from monolith.services import BookingServices

book = Blueprint("book", __name__)


@book.route("/restaurant/book", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["CUSTOMER"])
def index():
    if current_user is not None and hasattr(current_user, "id"):
        # check on the inputs
        if (
            request.form.get("reservation_date") is None
            or request.form.get("reservation_date") == ""
        ):
            return render_template(
                "booking.html",
                success=False,
                error="You have to specify a reservation date",
            )
        # the date and time come as string, so I have to parse them and transform them in python datetime
        #
        py_datetime = datetime.datetime.strptime(
            request.form.get("reservation_date"), "%d/%m/%Y %H:%M"
        )

        # check on people number
        if (
            request.form.get("people_number") is None
            or request.form.get("people_number") == ""
        ):
            return render_template(
                "booking.html", success=False, error="You have to specify people number"
            )
        people_number = int(request.form.get("people_number"))

        # check on restaurant_id (hidden field)
        if (
            request.form.get("restaurant_id") is None
            or request.form.get("restaurant_id") == ""
        ):
            return render_template(
                "booking.html",
                success=False,
                error="An error occured during the insertion your reservation. Please try later.",
            )

        # CALL TO BOOK SERVICE
        book = BookingServices.book(
            request.form.get("restaurant_id"),
            current_user,
            py_datetime,
            people_number,
            request.form.get("friends"),
        )

        if book is None:
            return render_template("booking.html", success=False, error="Please try again later") #TODO: display error message
        else:
            return render_template(
                "booking.html",
                success=True,
                restaurant_name=book["restaurant_name"],
                table_name=book["table_name"],
            )
    else:
        return render_template("booking.html", success=False, error="not logged in")


@book.route("/restaurant/book_update", methods=["GET", "POST"])
@login_required
def update_book():
    if current_user is not None and hasattr(current_user, "id"):
        # the date and time come as string, so I have to parse them and transform them in python datetime
        #
        reservation_date = request.form.get("reservation_date")
        py_datetime = datetime.datetime.strptime(reservation_date, "%d/%m/%Y %H:%M")
        #
        people_number = int(request.form.get("people_number"))
        #
        reservation_id = int(request.form.get("reservation_id"))

        new_book = BookingServices.update_book(
            reservation_id,
            current_user.id,
            py_datetime,
            people_number,
            request.form.get("friends"),
        )
        reservations_as_list = UserService.get_customer_reservation(
            None, None, current_user.id
        )

        form = ReservationForm()
        return render_template(
            "user_reservations.html",
            reservations_as_list=reservations_as_list,
            my_date_formatter_iso=my_date_formatter_iso,
            new_book=new_book,
            form=form,
        )
