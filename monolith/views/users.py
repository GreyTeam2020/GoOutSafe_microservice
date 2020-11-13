from flask import Blueprint, redirect, render_template, request, current_app, session
from monolith.database import db, User, Like, Role
from monolith.forms import UserForm, UserEditForm
from monolith.forms import ReservationForm
from monolith.utils.dispaccer_events import DispatcherMessage
from monolith.app_constant import REGISTRATION_EMAIL, USER_MICROSERVICE_URL
from monolith.services.user_service import UserService
from monolith.services.booking_services import BookingServices
from monolith.auth import roles_allowed
from monolith.utils.formatter import my_date_formatter
from monolith.model.User import UserModel
from flask_login import current_user, login_user, login_required
import requests, json

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
            current_app.logger.error(
                "user with email is null? {}".format(q_user_email is None)
            )
            current_app.logger.error(
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
            user = User()
            form.populate_obj(user)
            user = UserService.create_user(user, form.password.data, role_id)
            if user is not None and user.authenticate(form.password.data):
                login_user(user)
            DispatcherMessage.send_message(
                REGISTRATION_EMAIL,
                [user.email, user.lastname, "112344"],
            )
            new_role = UserService.get_user_role(role_id)
            if new_role is not None:
                session["ROLE"] = new_role.value
            return redirect("/")
    return render_template("create_user.html", form=form, type=name_on_page)


@users.route("/user/create_operator", methods=["GET", "POST"])
def create_operator():
    return _create_generic_user(2, "operator")


@users.route("/user/create_user", methods=["GET", "POST"])
def create_user():
    form = UserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            form.email = request.form.get("email")
            form.phone = request.form.get("phone")
            form.password = request.form.get("password")
            form.dateofbirth = request.form.get("dateofbirth")
            form.firstname = request.form.get("firstname")
            form.lastname = request.form.get("lastname")

            response = requests.post(
                USER_MICROSERVICE_URL + "/user/create_user",
                data=json.dumps(
                    {
                        "email": form.email,
                        "phone": form.phone,
                        "password": form.password,
                        "dateofbirth": form.dateofbirth,
                        "firstname": form.firstname,
                        "lastname": form.lastname,
                    }
                ),
                headers={"Content-type": "application/json"},
            )
            if not response.ok:
                current_app.logger.error("Error from USER microservice")
                return render_template(
                    "create_user.html",
                    form=form,
                    message="An error occured while creating the user",
                    type="customer",
                )

            return redirect("/")

    return render_template("create_user.html", form=form, type="customer")

    # return _create_generic_user(3, "customer")


@users.route("/user/data", methods=["GET", "POST"])
@login_required
def user_data():
    message = None
    if request.method == "POST":
        form = UserEditForm()
        if form.validate_on_submit():
            UserService.modify_user(form)
            return render_template("user_data.html", form=form)
        print(form.errors.items())
        return render_template("user_data.html", form=form, error="Error in the data")
    else:
        q = User.query.filter_by(id=current_user.id).first()
        if q is not None:
            form = UserForm(obj=q)
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
