import functools
from flask_login import current_user, LoginManager
from flask import session
from monolith.database import User

login_manager = LoginManager()


def roles_allowed(func=None, roles=None):
    """
    Check if the user has at least one required role
    Parameters:
        - func: the function to decorate
        - roles: an array of allowed roles
    :param func:
    :param roles:
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
    user = User.query.get(user_id)
    if user is not None:
        user._authenticated = True
    return user
