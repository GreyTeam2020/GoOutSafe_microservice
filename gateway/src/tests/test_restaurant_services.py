from random import random, randrange

from src.forms import RestaurantForm
from src.services.restaurant_services import RestaurantServices
from datetime import datetime
from src.services.booking_services import BookingServices
from src.model.dish_model import DishModel
from src.model.table_model import TableModel

from src.tests.utils import (
    create_restaurants_on_db,
    del_restaurant_on_db,
    del_user_on_db,
    create_user_on_db,
    create_random_booking,
    del_booking,
)


class Test_RestaurantServices:
    """
    This test suite test the services about restaurant use case.
    All the code tested inside this class is inside the services/test_restaurant_services.py
    """

    def test_create_restaurant(self):
        """
        test create user
        :return:
        """
        form = RestaurantForm()
        form.name.data = "rest_mock_{}".format(randrange(10000))
        form.phone.data = "096321343{}".format(randrange(10000))
        form.lat.data = 12
        form.lon.data = 12
        form.n_tables.data = 50
        form.covid_measures.data = "Random comment {}".format(randrange(10000))
        form.cuisine.data = ["Italian food"]
        form.open_days.data = ["0"]
        form.open_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.close_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.open_dinner.data = datetime.time(datetime(2020, 7, 1, 18, 00))
        form.close_dinner.data = datetime.time(datetime(2020, 6, 1, 22, 00))

        user = create_user_on_db(randrange(1, 60000), role_id=2)
        assert user is not None
        assert user.role_id == 2

        restaurant = RestaurantServices.create_new_restaurant(
            form, user.id, 6, user.email
        )
        assert restaurant is not None

        ## This call should be delete also the restaurants
        del_user_on_db(user.id)
        RestaurantServices.delete_restaurant(restaurant.id)

    def test_all_restaurant(self):
        """
        test about the services restaurant to test the result of all restaurants
        :return:
        """
        all_restauirants = RestaurantServices.get_all_restaurants()
        assert len(all_restauirants) > 0

    def test_reservation_local_ko_by_email(self):
        """
        This test cases, tru to test the logic inside the services to avoid
        stupid result

        http://localhost:5000/my_reservations?fromDate=2013-10-07&toDate=2014-10-07&email=john.doe@email.com
        :return:
        """
        user = create_user_on_db(randrange(1, 500000), role_id=2)
        assert user is not None

        from_date = datetime(2013, 10, 7)
        to_date = datetime(2014, 10, 7)

        def_rest = RestaurantServices.get_all_restaurants()[0]
        assert def_rest is not None
        all_reservation = BookingServices.get_reservation_by_constraint(
            user.id,
            from_date,
            to_date,
            def_rest["id"],
        )
        assert len(all_reservation) == 0

    def test_reservation_local_ok_by_email(self):
        """
        This test cases, tru to test the logic inside the services to avoid
        stupid result

        http://localhost:5000/my_reservations?fromDate=2013-10-07&toDate=2014-10-07&email=john.doe@email.com
        :return:
        """
        owner = create_user_on_db(randrange(1, 500000), role_id=2)
        assert owner is not None

        rest = create_restaurants_on_db(user_id=owner.id, user_email=owner.email)
        assert rest is not None

        user = create_user_on_db(
            randrange(1, 500000),
        )
        assert user is not None

        date_time = datetime(2022, 10, 28, 21, 30)

        reservation = create_random_booking(1, rest.id, user, date_time, "a@a.com")
        assert reservation is not None

        from_date = datetime(2022, 9, 28)
        to_date = datetime(2022, 11, 28)

        print(BookingServices.get_all_booking())

        search_reservation = BookingServices.get_reservation_by_constraint(
            user.id, from_date, to_date, rest.id
        )
        print(search_reservation)
        assert len(search_reservation) != 0

        del_booking(reservation["id"], user.id)
        del_user_on_db(user.id)
        del_user_on_db(owner.id)
        del_restaurant_on_db(rest.id)

    def test_new_review(self):
        """
        test for the new review function
        """
        form = RestaurantForm()
        form.name.data = "rest_mock_{}".format(randrange(1, 10000))
        form.phone.data = "096321343{}".format(randrange(1, 10000))
        form.lat.data = 12
        form.lon.data = 12
        form.n_tables.data = 50
        form.covid_measures.data = "Random comment {}".format(randrange(1, 10000))
        form.cuisine.data = ["Italian food"]
        form.open_days.data = ["0"]
        form.open_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.close_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.open_dinner.data = datetime.time(datetime(2020, 7, 1, 18, 00))
        form.close_dinner.data = datetime.time(datetime(2020, 6, 1, 22, 00))

        user = create_user_on_db(randrange(10, 50000), role_id=2)
        assert user is not None
        assert user.role_id == 2

        restaurant = RestaurantServices.create_new_restaurant(
            form, user.id, 6, user.email
        )
        assert restaurant is not None

        reviewer = create_user_on_db(randrange(1, 3000000), role_id=3)
        review = RestaurantServices.review_restaurant(
            restaurant_id=restaurant.id,
            reviewer_email=reviewer.email,
            stars=5,
            review="test",
        )
        assert review is not None

        ## This call should be delete also the restaurants
        # At this point also the review should be killed with the restaurants
        del_user_on_db(user.id)
        del_user_on_db(reviewer.id)
        RestaurantServices.delete_restaurant(restaurant.id)

    def test_restaurant_name(self):
        """
        check the function that return the restaurant name
        """
        form = RestaurantForm()
        form.name.data = "rest_mock_{}".format(randrange(10000))
        form.phone.data = "096321343{}".format(randrange(10000))
        form.lat.data = 12
        form.lon.data = 12
        form.n_tables.data = 50
        form.covid_measures.data = "Random comment {}".format(randrange(10000))
        form.cuisine.data = ["Italian food"]
        form.open_days.data = ["0"]
        form.open_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.close_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.open_dinner.data = datetime.time(datetime(2020, 7, 1, 18, 00))
        form.close_dinner.data = datetime.time(datetime(2020, 6, 1, 22, 00))

        user = create_user_on_db(randrange(10, 50000), role_id=2)
        assert user is not None
        assert user.role_id == 2

        restaurant = RestaurantServices.create_new_restaurant(form, user, 6, user.email)
        assert restaurant is not None

        name = RestaurantServices.get_restaurant_name(restaurant.id)
        assert restaurant.name == name

        ## This call should be delete also the restaurants
        # At this point also the review should be killed with the restaurants
        del_user_on_db(user.id)
        RestaurantServices.delete_restaurant(restaurant.id)

    def test_three_reviews(self):
        """
        check the three reviews fetcher
        """
        form = RestaurantForm()
        form.name.data = "rest_mock_{}".format(randrange(10000))
        form.phone.data = "096321343{}".format(randrange(10000))
        form.lat.data = 12
        form.lon.data = 12
        form.n_tables.data = 50
        form.covid_measures.data = "Random comment {}".format(randrange(10000))
        form.cuisine.data = ["Italian food"]
        form.open_days.data = ["0"]
        form.open_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.close_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.open_dinner.data = datetime.time(datetime(2020, 7, 1, 18, 00))
        form.close_dinner.data = datetime.time(datetime(2020, 6, 1, 22, 00))

        user = create_user_on_db(randrange(10, 50000), role_id=2)
        assert user is not None
        assert user.role_id == 2

        restaurant = RestaurantServices.create_new_restaurant(
            form, user.id, 6, user.email
        )
        assert restaurant is not None

        reviewer = create_user_on_db(randrange(10, 50000), role_id=3)

        review1 = RestaurantServices.review_restaurant(
            restaurant.id, reviewer.email, 5, "test1"
        )
        assert review1 is not None
        review2 = RestaurantServices.review_restaurant(
            restaurant.id, reviewer.email, 4, "test2"
        )
        assert review2 is not None
        review3 = RestaurantServices.review_restaurant(
            restaurant.id, reviewer.email, 3, "test3"
        )
        assert review3 is not None

        three_reviews = RestaurantServices.get_three_reviews(restaurant.id)
        assert three_reviews is not None
        assert len(three_reviews) == 3

        ## This call should be delete also the restaurants
        # At this point also the review should be killed with the restaurants
        del_user_on_db(user.id)
        del_user_on_db(reviewer.id)
        RestaurantServices.delete_restaurant(restaurant.id)

    def test_search_restaurant_by_key_ok_complete_name(self):
        """
        This test unit test the service to perform the search by keyword of the restaurants
        on persistence
        """
        form = RestaurantForm()
        form.name.data = "rest_mock_{}".format(randrange(10000))
        form.phone.data = "096321343{}".format(randrange(10000))
        form.lat.data = 12
        form.lon.data = 12
        form.n_tables.data = 50
        form.covid_measures.data = "Random comment {}".format(randrange(10000))
        form.cuisine.data = ["Italian food"]
        form.open_days.data = ["0"]
        form.open_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.close_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.open_dinner.data = datetime.time(datetime(2020, 7, 1, 18, 00))
        form.close_dinner.data = datetime.time(datetime(2020, 6, 1, 22, 00))

        user = create_user_on_db(randrange(6000, 9000), role_id=2)
        assert user is not None
        assert user.role_id == 2

        restaurant = RestaurantServices.create_new_restaurant(
            form, user.id, 6, user.email
        )
        assert restaurant is not None
        rest_by_name = RestaurantServices.get_restaurants_by_keyword(
            name=restaurant.name
        )
        assert len(rest_by_name) is 1

        del_user_on_db(user.id)
        RestaurantServices.delete_restaurant(restaurant.id)

    def test_search_restaurant_by_key_ok_partial_name(self):
        """
        This test unit test the service to perform the search by keyword of the restaurants
        on persistence
        """
        form = RestaurantForm()
        form.name.data = "rest_mock_{}".format(randrange(10000))
        form.phone.data = "096321343{}".format(randrange(10000))
        form.lat.data = 12
        form.lon.data = 12
        form.n_tables.data = 50
        form.covid_measures.data = "Random comment {}".format(randrange(10000))
        form.cuisine.data = ["Italian food"]
        form.open_days.data = ["0"]
        form.open_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.close_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.open_dinner.data = datetime.time(datetime(2020, 7, 1, 18, 00))
        form.close_dinner.data = datetime.time(datetime(2020, 6, 1, 22, 00))

        user = create_user_on_db(randrange(6000, 9000), role_id=2)
        assert user is not None
        assert user.role_id == 2

        restaurant = RestaurantServices.create_new_restaurant(
            form, user.id, 6, user.email
        )
        assert restaurant is not None
        rest_by_name = RestaurantServices.get_restaurants_by_keyword(
            name=restaurant.name
        )
        assert len(rest_by_name) is 1

        del_user_on_db(user.id)
        RestaurantServices.delete_restaurant(restaurant.id)

    def test_delete_dish_menu(self, client):
        """
        check if dish get deletedS
        """

        user = create_user_on_db(randrange(10, 50000), role_id=2)
        assert user is not None

        dish = DishModel()
        dish.name = "Pearà"
        dish.price = 5.50
        dish.restaurant_id = 1
        dish = RestaurantServices.insert_dish(dish)
        assert dish is not None

        response = RestaurantServices.delete_dish(dish["id"])
        print(response)
        assert response is not None

    def test_checkin_reservation(self):
        """
        test mark checked in a reservation by operator
        """
        owner = create_user_on_db(randrange(1, 500000), role_id=2)
        assert owner is not None

        rest = create_restaurants_on_db(user_id=owner.id, user_email=owner.email)
        assert rest is not None

        user = create_user_on_db(randrange(1, 500000))
        assert user is not None

        date_time = datetime(2022, 10, 28, 21, 30)

        reservation = create_random_booking(1, rest.id, user, date_time, "a@a.com")

        assert reservation is not None

        response = RestaurantServices.checkin_reservations(reservation["id"])
        assert response is not None

        del_booking(reservation["id"], user.id)
        del_user_on_db(user.id)
        del_user_on_db(owner.id)
        del_restaurant_on_db(rest.id)

    def test_get_restaurant_people_none(self):
        """
        The method test the function inside the RestaurantServices to search all the people
        inside the restaurants, the function return an array that looks like
        [people_to_lunch, people_to_dinner, people_checkin]

        Test flow
        - new restaurants
        - get all people
        - del restaurant
        """
        owner_one = create_user_on_db(randrange(10, 50000), role_id=2)
        assert owner_one is not None

        restaurant_one = create_restaurants_on_db(
            name="First", user_id=owner_one.id, user_email=owner_one.email
        )
        assert restaurant_one is not None

        all_people = RestaurantServices.get_restaurant_people(restaurant_one.id)
        assert all_people is not None
        assert len(all_people) == 3
        assert all_people[0] == 0
        assert all_people[1] == 0
        assert all_people[2] == 0
        del_restaurant_on_db(restaurant_one.id)
        del_user_on_db(owner_one.id)

    def test_create_table_model(self):
        table = TableModel()
        json = {
            "id": 45,
            "name": "Table45",
            "max_seats": 6,
            "restaurant_id": 1,
            "available": True,
        }
        table.fill_from_json(json)

        assert json["name"] == (table.serialize())["name"]
