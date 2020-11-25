import logging

from flask import Flask
from src.views import blueprints
from src.auth import login_manager

logging.getLogger("urllib3").setLevel(logging.WARNING)


def create_app(tests=False):
    app = Flask(__name__)
    app.config["WTF_CSRF_SECRET_KEY"] = "A SECRET KEY"
    app.config["SECRET_KEY"] = "ANOTHER ONE"
    if tests is False:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/gooutsafe.db"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tests/gooutsafe.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    login_manager.init_app(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", debug=True)
