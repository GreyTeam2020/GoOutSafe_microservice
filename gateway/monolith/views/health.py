from flask import Blueprint, redirect, render_template, request

from monolith.auth import roles_allowed
from monolith.database import db, User, Positive
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

            if form.email.data == "" and form.phone.data == "":
                return render_template(
                    "search_contacts.html",
                    _test="search_contacts_no_data",
                    form=form,
                    message="Insert an email or a phone number"
                )

            contacts = HealthyServices.search_contacts(form.email.data, form.phone.data)

            if str(type(contacts)) == "<class 'list'>":

                return render_template(
                    "list_contacts.html", _test="list_page", contacts=contacts
                )

            elif str(type(contacts)) == "<class 'str'>":

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
                    message="Error"
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
