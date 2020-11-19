import json

import requests
from flask import (
    Blueprint,
    render_template,
    redirect,
    session,
    current_app,
    jsonify,
    request,
)
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
            url = "{}/login".format(USER_MICROSERVICE_URL)
            current_app.logger.debug("URL to user microservice: {}".format(url))
            # Look at https://urllib3.readthedocs.io/en/latest/user-guide.html#certificate-verification
            user, status_code = UserService.login_user(email, password)
            # TODO improve the error code inside the User API
            if user is None and status_code != 404:
                return render_template(
                    "login.html",
                    form=form,
                    _test="error_login",
                    message="Connection refused",
                )

            if user is None and status_code == 404:
                return render_template(
                    "login.html",
                    form=form,
                    _test="error_login",
                    message="User not exist",
                )

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
