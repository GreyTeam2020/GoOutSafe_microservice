import json

import requests
from flask import Blueprint, render_template, redirect, session, current_app, jsonify, request
from flask_login import login_user, logout_user

from monolith.forms import LoginForm
from monolith.model import UserModel
from monolith.services import UserService
from monolith.app_constant import USER_MICROSERVICE_URL

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            email, password = form.data["email"], form.data["password"]
            json_login = {"email": email, "password": password}
            url = "{}/login".format(USER_MICROSERVICE_URL)
            current_app.logger.debug("URL to user microservice: {}".format(url))
            # Look at https://github.com/psf/requests/issues/1198
            try:
                response = requests.post(url, data=json_login)
            except requests.exceptions.ConnectionError:
                return render_template(
                    "login.html", form=form, _test="error_login", message="Connection refused",
                    base_url="http://localhost/ui/login"
                )

            if not response.ok:
                current_app.logger.error(response.json())
                return render_template(
                    "login.html", form=form, _test="error_login", message="User not exist",
                    base_url="http://localhost/ui/login"
                )

            user = UserModel()
            user.fill_from_json(response.json())
            if UserService.log_in_user(user):
                return redirect("/ui")
            else:
                current_app.logger.error("log in failed")
                return render_template(
                    "login.html",
                    form=form,
                    _test="error_login",
                    message="An error occurred during log in. Please try later",
                    base_url="http://localhost/ui/login"
                )
    return render_template("login.html", _test="first_visit_login", form=form, base_url="http://localhost/ui/login")


@auth.route("/logout")
def logout():
    logout_user()
    session.clear()  # remove all session objects, like role
    return redirect("/")
