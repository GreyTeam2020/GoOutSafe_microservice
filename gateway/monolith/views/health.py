from flask import Blueprint, redirect, render_template, request

from monolith.auth import roles_allowed
from monolith.services import UserService
from monolith.forms import SearchUserForm

from monolith.services import HealthyServices

health = Blueprint("health", __name__)


@health.route("/health/report_positive")
def report_positive():
    users = HealthyServices.report_positive()
    n = list(range(len(users)))
    return render_template("report_positive.html", n=n, users=users)


@health.route("/mark_positive", methods=["POST", "GET"])
@roles_allowed(roles=["HEALTH"])
def mark_positive():
    form = SearchUserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            phone = form.phone.data
            if len(email) == 0 and len(phone) == 0:
                return render_template(
                    "mark_positive.html",
                    _test="search_contacts_no_data",
                    form=form,
                    message="Insert an email or a phone number",
                )
            message = HealthyServices.mark_positive(email, phone)
            if len(message) == 0:
                return redirect("/")
            return render_template(
                "mark_positive.html",
                _test="mark_positive_page_error_test",
                form=form,
                message=message,
            )

    return render_template("mark_positive.html", form=form)


@health.route("/search_contacts", methods=["POST", "GET"])
@roles_allowed(roles=["HEALTH"])
def search_contacts():
    form = SearchUserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            phone = form.phone.data
            if len(email) == 0 and len(phone) == 0:
                return render_template(
                    "search_contacts.html",
                    _test="search_contacts_no_data",
                    form=form,
                    message="Insert an email or a phone number",
                )

            user_email = UserService.user_is_present(email)
            user_phone = UserService.user_is_present(phone)
            if user_email is None and user_phone is None:
                return render_template("/search_contacts.html", form=form, message="User not exist inside the sistem",
                                       _test="search_contact_not_registered")
            contacts = HealthyServices.search_contacts(email, phone)
            if isinstance(contacts, list):
                return render_template(
                    "list_contacts.html", _test="list_page", contacts=contacts
                )
            elif isinstance(contacts, str):
                return render_template(
                    "search_contacts.html",
                    _test="search_contacts_no_positive",
                    form=form,
                    message=contacts,
                )
            else:
                return render_template(
                    "search_contacts.html",
                    _test="search_contacts_no_positive",
                    form=form,
                    message="Error",
                )

    return render_template("/search_contacts.html", form=form)


@health.route("/unmark_positive", methods=["POST", "GET"])
@roles_allowed(roles=["HEALTH"])
def unmark_positive():
    form = SearchUserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email = form.email.data
            phone = form.phone.data
            message = HealthyServices.unmark_positive(email, phone)
            if message == "":
                return redirect("/")
            return render_template(
                "unmark_positive.html",
                _test="unmark_positive_page",
                form=form,
                message=message,
            )
    return render_template("unmark_positive.html", form=form)
