from datetime import datetime, timedelta
from random import randrange

from monolith.database import db, Positive
from monolith.services import HealthyServices
from monolith.tests.utils import (
    create_user_on_db,
    del_user_on_db,
    positive_with_user_id,
    get_user_with_email,
    create_random_booking,
    create_restaurants_on_db,
    del_restaurant_on_db,
    get_today_midnight,
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
        assert message == "User with email {} already Covid-19 positive".format(
            user.email
        )
        del_user_on_db(user.id)

    def test_mark_positive_user_not_exist(self):
        """
        It tests that health authority can't mark as covid-19 positive
        someone that is not registered as customer
        """
        message = HealthyServices.mark_positive(
            user_email="alibaba@alibaba.com", user_phone="1234555"
        )
        assert message == "The customer is not registered"

    def test_mark_positive_nan_proprieties(self):
        """
        It tests that health authority, to mark someone as covid-19
        positive, have to insert an email or a phone number
        """
        message = HealthyServices.mark_positive("", "")
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
        assert message == "User with email {} is not Covid-19 positive".format(
            user.email
        )

        del_user_on_db(user.id)

    def test_unmark_user_not_in_app(self):
        """
        It tests that health authority cannot mark a customer as healed
        if the customer is not registered as customer
        """
        message = HealthyServices.unmark_positive("alibaba@alibaba.com", "")
        assert message == "The customer is not registered"

    def test_unmark_positive_nan_proprieties(self):
        """
        It tests that health authority cannot mark a customer as healed
        without insert neither customer's email nor customer's phone number
        """
        message = HealthyServices.mark_positive()
        assert message == "Insert an email or a phone number"

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

        contacts = HealthyServices.search_contacts(user.id)
        assert len(contacts) is 0

        message = HealthyServices.unmark_positive("", user.phone)
        assert len(message) is 0

        del_user_on_db(user.id)

    def test_search_contacts_user_with_booking_only_one_user(self):
        """
        Searching for list of contacts of a covid-19 positive
        customer with bookings
        """

        user = get_user_with_email("john.doe@email.com")

        positive = positive_with_user_id(user.id)
        assert positive is None
        message = HealthyServices.mark_positive("", user.phone)
        assert len(message) == 0

        contacts = HealthyServices.search_contacts(user.id)
        assert len(contacts) == 0

        message = HealthyServices.unmark_positive("", user.phone)
        assert len(message) == 0

    def test_search_contacts_user_with_booking(self):
        """
        Searching for list of contacts of a covid-19 positive
        customer with bookings
        """

        owner = create_user_on_db(787436)
        assert owner is not None
        restaurant = create_restaurants_on_db("Pepperwood", user_id=owner.id)
        assert restaurant is not None

        customer1 = create_user_on_db(787437)
        assert customer1 is not None

        date_booking_1 = (
            get_today_midnight()
            - timedelta(days=datetime.today().weekday())
            + timedelta(hours=13)
        )
        books1 = create_random_booking(
            1, restaurant.id, customer1, date_booking_1, "a@aa.com"
        )

        assert len(books1) == 1

        # a new user that books in the same restaurant of the previous one
        customer2 = create_user_on_db(787438)
        assert customer2 is not None

        date_booking_2 = (
            get_today_midnight()
            - timedelta(days=datetime.today().weekday())
            + timedelta(hours=13)
        )
        books2 = create_random_booking(
            1, restaurant.id, customer2, date_booking_2, "b@b.com"
        )
        assert len(books2) == 1

        # an user become covid19 positive
        positive = positive_with_user_id(customer1.id)
        assert positive is None
        message = HealthyServices.mark_positive(user_phone=customer1.phone)
        assert len(message) == 0

        q_already_positive = (
            db.session.query(Positive)
            .filter_by(user_id=customer1.id, marked=True)
            .first()
        )
        assert q_already_positive is not None

        contacts = HealthyServices.search_contacts(customer1.id)
        assert len(contacts) == 1

        message = HealthyServices.unmark_positive("", customer1.phone)
        assert len(message) == 0

        del_user_on_db(customer1.id)
        del_user_on_db(customer2.id)
        del_restaurant_on_db(restaurant.id)