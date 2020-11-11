from flask import Blueprint, render_template, redirect, session
from flask_login import login_user, logout_user

from monolith.database import db, User, Role, Restaurant
from monolith.forms import LoginForm

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None and user.authenticate(password):
            login_user(user)
            q = db.session.query(Role).filter(Role.id == user.role_id)
            role = q.first()
            if role is not None:
                session["ROLE"] = role.value
                # if is operator, load restaurant information and load in session
                if role.value == "OPERATOR":
                    q = db.session.query(Restaurant).filter(
                        Restaurant.owner_id == user.id
                    )
                    restaurant = q.first()
                    if restaurant is not None:
                        session["RESTAURANT_ID"] = restaurant.id
                        session["RESTAURANT_NAME"] = restaurant.name
            return redirect("/")
        else:
            return render_template(
                "login.html", form=form, _test="error_login", message="User not exist"
            )
    return render_template("login.html", _test="first_visit_login", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    session.clear()  # remove all session objects, like role
    return redirect("/")
