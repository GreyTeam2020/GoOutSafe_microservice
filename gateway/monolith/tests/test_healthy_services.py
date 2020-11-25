from random import randrange

from monolith.services import HealthyServices
from monolith.tests.utils import (
    create_user_on_db,
    del_user_on_db,
    positive_with_user_id,
)


class Test_HealthyServices:
    """
    This test suite test the services about healthy autority use case.
    All the code tested inside this class is inside the services/test_healthy_services.py
    """

    def test_mark_positive_user_precondition(self):
        """
        It tests that a new user is not positive
        """
        # an operator
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3
        positive = positive_with_user_id(user.id, marked=True)
        assert positive is None
        del_user_on_db(user.id)

    def test_mark_positive_ok(self):
        """
        It tests that a user is correctly marked as covid-19 positive by
        health authority
        """
        # an operator
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3
        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive(user.email, user.phone)
        assert len(message) is 0
        del_user_on_db(user.id)

    def test_mark_positive_already_covid(self):
        """
        It tests that a customer can't be marked as covid-19 positive if
        he is already covid-19 positive
        """
        user = create_user_on_db(randrange(1, 7000))
        assert user is not None
        assert user.role_id is 3
        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive(user.email, user.phone)
        assert len(message) is 0
        message = HealthyServices.mark_positive(user.email, user.phone)
        assert len(message) != 0
        del_user_on_db(user.id)

    def test_mark_positive_user_not_exist(self):
        """
        It tests that health authority can't mark as covid-19 positive
        someone that is not registered as customer
        """
        message = HealthyServices.mark_positive(
            user_email="alibaba@alibaba.com", user_phone="1234555"
        )
        assert message == "An error occurs, please try again"

    def test_mark_positive_nan_proprieties(self):
        """
        It tests that health authority, to mark someone as covid-19
        positive, have to insert an email or a phone number
        """
        message = HealthyServices.mark_positive()
        assert message == "Insert an email or a phone number"

    def test_mark_positive_user_by_email(self):
        """
        It tests that health authority can mark a customer as covid-19
        positive using only the customer's email
        """
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3
        assert user is not None
        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive(user.email, "")
        assert len(message) is 0
        del_user_on_db(user.id)

    def test_mark_positive_user_by_phone(self):
        """
        It tests that health authority can mark a customer as covid-19
        positive using only the customer's phone number
        """
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive("", user.phone)
        assert len(message) is 0
        del_user_on_db(user.id)

    def test_unmark_positive_ok(self):
        """
        It tests that health authority can mark a customer as healed
        using customer's email and phone number
        """
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3
        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive(user.email, user.phone)
        assert len(message) is 0

        message = HealthyServices.unmark_positive(user.email, user.phone)
        assert len(message) is 0

        del_user_on_db(user.id)

    def test_unmark_user_not_positive(self):
        """
        It tests that health authority cannot mark a customer as healed
        if the customer is not covid-19 positive
        """
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3

        message = HealthyServices.unmark_positive(user.email, user.phone)
        assert len(message) != 0

        del_user_on_db(user.id)

    def test_unmark_positive_user_by_email(self):
        """
        It tests that health authority can mark a customer as healed
        using only customer's email
        """
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3
        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive(user.email, "")
        assert len(message) is 0

        message = HealthyServices.unmark_positive(user.email, "")
        assert len(message) is 0

        del_user_on_db(user.id)

    def test_mark_positive_user_by_phone(self):
        """
        It tests that health authority can mark a customer as healed
        using only customer's phone number
        """
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3
        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive("", user.phone)
        assert len(message) is 0

        message = HealthyServices.unmark_positive("", user.phone)
        assert len(message) is 0

        del_user_on_db(user.id)

    def test_search_contacts_user_with_no_booking(self):
        """
        Searching for list of contacts of a covid-19 positive
        customer with no bookings
        """
        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3
        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive("", user.phone)
        assert len(message) is 0

        contacts = HealthyServices.search_contacts(user.email, "")
        assert len(contacts) is 0

        message = HealthyServices.unmark_positive("", user.phone)
        assert len(message) is 0

        del_user_on_db(user.id)

    def test_search_contacts_user_with_booking_only_one_user(self):
        """
        Searching for list of contacts of a covid-19 positive
        customer with bookings
        """

        user = create_user_on_db(randrange(1, 50000000))
        assert user is not None
        assert user.role_id is 3

        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive("", user.phone)
        assert len(message) == 0

        contacts = HealthyServices.search_contacts(user.email, "")
        assert len(contacts) == 0

        message = HealthyServices.unmark_positive("", user.phone)
        assert len(message) == 0
