import functools

from flask_login import current_user, LoginManager
from flask import session
from src.model import UserModel

login_manager = LoginManager()


def roles_allowed(func=None, roles=None):
    """
    Check if the user has at least one required role
    :param func: the function to decorate
    :param roles: an array of allowed roles
    """
    if not func:
        return functools.partial(roles_allowed, roles=roles)

    @functools.wraps(func)
    def f(*args, **kwargs):
        role = session.get("ROLE")
        if not any(role in s for s in roles):
            return login_manager.unauthorized()
        return func(*args, **kwargs)

    return f


@login_manager.user_loader
def load_user(user_id):
    # user = User.query.get(user_id)
    if "current_user" in session:
        user = UserModel()
        user.fill_from_json(session["current_user"])
        user.set_authenticated(True)
        return user
    return None
