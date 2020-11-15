"""
TODO
"""
import pytest

from monolith.app import create_app


@pytest.fixture(autouse=True)
def client():
    app = create_app(tests=True)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["DEBUG"] = True
    ctx = app.app_context()
    ctx.push()

    with app.test_client() as client:
        yield client
