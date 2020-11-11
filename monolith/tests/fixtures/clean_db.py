import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def del_db_before_run(request):
    # prepare something ahead of all tests
    request.addfinalizer(del_db)


def del_db():
    """
    Del db before run the tests
    :return:
    """
    try:
        my_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(my_path, "../")
        os.remove("{}/gooutsafe.db".format(path))
    except OSError:
        assert False
