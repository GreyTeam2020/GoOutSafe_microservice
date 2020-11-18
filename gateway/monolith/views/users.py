from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    current_app,
    session,
    jsonify,
)
from monolith.forms import UserForm, UserEditForm
from monolith.forms import ReservationForm
from monolith.services import UserService, SendEmailService
from monolith.services.booking_services import BookingServices
from monolith.auth import roles_allowed
from monolith.utils.formatter import my_date_formatter
from monolith.model.user_model import UserModel
from flask_login import current_user, login_user, login_required
import requests

users = Blueprint("users", __name__)


def _create_generic_user(role_id: int = 3, name_on_page: str = "customer"):
    """
    This method contains the logic to create a new user with a different role
    :param role_id: role id on database this mean that is possible
    :param name_on_page: name to customize the page inside the template
    :return: response template
    """
    form = UserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            q_user_email = UserService.user_is_present(email=form.email.data)
            q_user_phone = UserService.user_is_present(phone=form.phone.data)
            current_app.logger.debug(
                "user with email is null? {}".format(q_user_email is None)
            )
            current_app.logger.debug(
                "user with phone is null? {}".format(q_user_phone is None)
            )
            if (q_user_email is not None) or (q_user_phone is not None):
                return render_template(
                    "create_user.html",
                    form=form,
                    message="Email {} and/or number {} already registered".format(
                        form.email.data, form.phone.data
                    ),
                    type=name_on_page,
                )
            user = UserService.create_user(form, role_id)
            if user is False:
                current_app.logger.error("An error occured while creating the user")
                return render_template(
                    "create_user.html",
                    form=form,
                    message="An error occured while creating the user",
                    type=name_on_page,
                )
            SendEmailService.confirm_registration(form.email.data, form.firstname.data)
            # if user is operator, do the login and redirect to the home
            # in this way the home will show create restaurant page
            if role_id == 2:
                # we need to take the user from email
                current_app.logger.debug(
                    "Requesting user with email {}".format(form.email.data)
                )
                user = UserService.get_user_by_email(form.email.data)
                # set the session
                session["current_user"] = user.serialize()
                login_user(user)
                session["ROLE"] = "OPERATOR"
                return redirect("/")
            else:
                return redirect("/login")

    return render_template("create_user.html", form=form, type=name_on_page)


@users.route("/user/create_operator", methods=["GET", "POST"])
def create_operator():
    return _create_generic_user(2, "operator")


@users.route("/user/create_user", methods=["GET", "POST"])
def create_user():
    return _create_generic_user(3, "customer")


@users.route("/user/data", methods=["GET", "POST"])
@login_required
def user_data():
    if request.method == "POST":
        form = UserEditForm()
        if form.validate_on_submit():
            user = UserService.modify_user(form)
            if user is not None:
                session["current_user"] = user.serialize()
                return render_template("user_data.html", form=form, message="Modified")
            else:
                return render_template(
                    "user_data.html", form=form, error="Error during the operation"
                )
        current_app.logger.debug(form.errors.items())
        return render_template("user_data.html", form=form, message="Error in the data")
    user = current_user
    if user is not None:
        form = UserEditForm(obj=user)
        return render_template("user_data.html", form=form)


@users.route("/user/delete")
@login_required
def user_delete():
    UserService.delete_user(current_user.id)
    return redirect("/logout")


@users.route("/customer/reservations", methods=["GET"])
@login_required
@roles_allowed(roles=["CUSTOMER"])
def myreservation():

    # filter params
    fromDate = request.args.get("fromDate", type=str)
    toDate = request.args.get("toDate", type=str)

    reservations_as_list = UserService.get_customer_reservation(
        fromDate, toDate, current_user.id
    )
    form = ReservationForm()
    return render_template(
        "user_reservations.html",
        reservations_as_list=reservations_as_list,
        my_date_formatter=my_date_formatter,
        form=form,
    )


@users.route("/customer/deletereservations/<reservation_id>", methods=["GET", "POST"])
@login_required
@roles_allowed(roles=["CUSTOMER"])
def delete_reservation(reservation_id):

    deleted = BookingServices.delete_book(reservation_id, current_user.id)

    reservations_as_list = UserService.get_customer_reservation(
        None, None, current_user.id
    )
    form = ReservationForm()
    return render_template(
        "user_reservations.html",
        reservations_as_list=reservations_as_list,
        my_date_formatter=my_date_formatter,
        deleted=deleted,
        _test="del_rest_test",
        form=form,
    )
