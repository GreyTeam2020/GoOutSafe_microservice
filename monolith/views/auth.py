import json

import requests
from flask import Blueprint, render_template, redirect, session, current_app
from flask_login import login_user, logout_user

from monolith.database import db, User, Role, Restaurant
from monolith.forms import LoginForm
from monolith.app_constant import USER_MICROSERVICE_URL
from monolith.model import UserModel
from monolith.services import UserService

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]

        response = requests.post(
            USER_MICROSERVICE_URL + "/user/login",
            data=json.dumps(
                {
                    "email": email,
                    "password": password,
                }
            ),
            headers={"Content-type": "application/json"},
        )

        if not response.ok:
            current_app.logger.error(response.json())
            return render_template(
                "login.html", form=form, _test="error_login", message="User not exist"
            )

        user = UserModel()
        user.fill_from_json(response.json())
        if UserService.log_in_user(user):
            return redirect("/")
        else:
            current_app.logger.error("log in failed")
            return render_template(
                "login.html",
                form=form,
                _test="error_login",
                message="An error occurred during log in. Please try later",
            )

    return render_template("login.html", _test="first_visit_login", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    session.clear()  # remove all session objects, like role
    return redirect("/")
