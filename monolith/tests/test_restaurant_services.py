from random import random, randrange

from monolith.database import db, User, Restaurant, Review, MenuDish, Reservation
from monolith.forms import RestaurantForm
from monolith.services.restaurant_services import RestaurantServices
from datetime import datetime

from monolith.tests.utils import (
    get_user_with_email,
    create_restaurants_on_db,
    del_restaurant_on_db,
    del_user_on_db,
    create_user_on_db,
    login,
    create_random_booking,
    create_review_for_restaurants,
    get_rest_with_name,
    del_all_review_for_rest,
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
        form.name = "Gino Sorbillo"
        form.phone = "096321343"
        form.lat = 12
        form.lon = 12
        form.n_tables.data = 50
        form.covid_measures.data = "We can survive"
        form.cuisine.data = ["Italian food"]
        form.open_days.data = ["0"]
        form.open_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.close_lunch.data = datetime.time(datetime(2020, 7, 1, 12, 00))
        form.open_dinner.data = datetime.time(datetime(2020, 7, 1, 18, 00))
        form.close_dinner.data = datetime.time(datetime(2020, 6, 1, 22, 00))
        q_user = db.session.query(User).filter_by(email="ham.burger@email.com").first()
        assert q_user is not None
        restaurant = RestaurantServices.create_new_restaurant(form, q_user.id, 6)
        assert restaurant is not None

        del_restaurant_on_db(restaurant.id)

    def test_all_restaurant(self):
        """
        test about the services restaurant to test the result of all restaurants
        :return:
        """
        all_restauirants = RestaurantServices.get_all_restaurants()
        assert len(all_restauirants) == 1

    def test_reservation_local_ko_by_email(self):
        """
        This test cases, tru to test the logic inside the services to avoid
        stupid result

        http://localhost:5000/my_reservations?fromDate=2013-10-07&toDate=2014-10-07&email=john.doe@email.com
        :return:
        """
        email = "ham.burger@email.com"
        user = get_user_with_email(email)
        from_date = "2013-10-07"
        to_date = "2014-10-07"
        assert user is not None

        def_rest = db.session.query(Restaurant).all()[0]
        assert def_rest is not None
        all_reservation = RestaurantServices.get_reservation_rest(
            def_rest.owner_id, def_rest.id, from_date, to_date, email
        )
        assert len(all_reservation) == 0

    def test_reservation_local_ok_by_email(self):
        """
        This test cases, tru to test the logic inside the services to avoid
        stupid result

        http://localhost:5000/my_reservations?fromDate=2013-10-07&toDate=2014-10-07&email=john.doe@email.com
        :return:
        """
        owner = create_user_on_db(12345543234)
        assert owner is not None

        rest = create_restaurants_on_db(user_id=owner.id)
        assert rest is not None

        user = create_user_on_db(123455432332)
        assert user is not None

        date_time = datetime(2020, 10, 28, 21, 30)

        books = create_random_booking(1, rest.id, user, date_time, "a@a.com")
        assert len(books) == 1

        from_date = "2020-09-28"
        to_date = "2020-11-28"

        reservations = RestaurantServices.get_reservation_rest(
            rest.owner_id, rest.id, from_date, to_date, user.email
        )
        assert len(reservations) == 1

        del_user_on_db(user.id)
        del_restaurant_on_db(rest.id)

    def test_new_review(self):
        """
        test for the new review function
        """
        restaurant = (
            db.session.query(Restaurant.id)
            .filter(Restaurant.name == "Trial Restaurant")
            .first()
        )
        reviewer = (
            db.session.query(User.id).filter(User.email == "john.doe@email.com").first()
        )
        review = RestaurantServices.review_restaurant(
            restaurant.id, reviewer.id, 5, "test"
        )
        assert review is not None

        db.session.query(Review).filter_by(id=review.id).delete()
        db.session.commit()

    def test_restaurant_name(self):
        """
        check the function that return the restaurant name
        """
        restaurant = (
            db.session.query(Restaurant)
            .filter(Restaurant.name == "Trial Restaurant")
            .first()
        )
        name = RestaurantServices.get_restaurant_name(restaurant.id)
        assert restaurant.name == name

    def test_three_reviews(self):
        """
        check the three reviews fetcher
        """

        restaurant = (
            db.session.query(Restaurant.id)
            .filter(Restaurant.name == "Trial Restaurant")
            .first()
        )
        reviewer = (
            db.session.query(User.id).filter(User.email == "john.doe@email.com").first()
        )
        review1 = RestaurantServices.review_restaurant(
            restaurant.id, reviewer.id, 5, "test1"
        )
        review2 = RestaurantServices.review_restaurant(
            restaurant.id, reviewer.id, 4, "test2"
        )
        review3 = RestaurantServices.review_restaurant(
            restaurant.id, reviewer.id, 3, "test3"
        )

        three_reviews = RestaurantServices.get_three_reviews(restaurant.id)
        assert three_reviews is not None
        assert len(three_reviews) == 3

        db.session.query(Review).filter_by(id=review1.id).delete()
        db.session.query(Review).filter_by(id=review2.id).delete()
        db.session.query(Review).filter_by(id=review3.id).delete()

        db.session.commit()

    def test_search_restaurant_by_key_ok_complete_name(self):
        """
        This test unit test the service to perform the search by keyword of the restaurants
        on persistence
        """
        rest_by_name = RestaurantServices.get_restaurants_by_keyword(name="Trial")
        assert len(rest_by_name) is 1

    def test_search_restaurant_by_key_ok_partial_name(self):
        """
        This test unit test the service to perform the search by keyword of the restaurants
        on persistence
        """
        user = create_user_on_db()
        rest = create_restaurants_on_db("Gino Sorbillo", user.id)
        assert rest is not None
        rest_by_name = RestaurantServices.get_restaurants_by_keyword(name=rest.name)
        assert len(rest_by_name) is 1

        rest_by_name = RestaurantServices.get_restaurants_by_keyword(name="Gino")
        assert len(rest_by_name) is 1

        rest_by_name = RestaurantServices.get_restaurants_by_keyword(name="gino")
        assert len(rest_by_name) is 1

        rest_by_name = RestaurantServices.get_restaurants_by_keyword(name="Sorbillo")
        assert len(rest_by_name) is 1

        rest_by_name = RestaurantServices.get_restaurants_by_keyword(name="sorbillo")
        assert len(rest_by_name) is 1

        del_user_on_db(user.id)
        for rest in rest_by_name:
            del_restaurant_on_db(rest.id)

    def test_delete_dish_menu(self, client):
        """
        check if dish get deletedS
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        dish = MenuDish()
        dish.name = "Pearà"
        dish.price = 5.50
        dish.restaurant_id = 1
        db.session.add(dish)
        db.session.commit()
        assert dish is not None

        client.get("/restaurant/menu/delete/" + str(dish.id))

        dish = db.session.query(MenuDish).filter_by(name="Pearà").first()
        assert dish is None

    def test_checkin_reservation(self):
        """
        test mark checked in a reservation by operator
        """
        reservation = db.session.query(Reservation).first()
        reservation_query = db.session.query(Reservation).filter_by(id=reservation.id)
        reservation_query.update({Reservation.checkin: False})
        RestaurantServices.checkin_reservations(reservation.id)
        assert reservation.checkin is True
        reservation_query = db.session.query(Reservation).filter_by(id=reservation.id)
        reservation_query.update({Reservation.checkin: False})
        db.session.commit()
        db.session.flush()

    def test_rating_review_restaurants(self):
        """
        This method test the function called by celery to calculate the rating of all restaurants

        Test flow:
        - Create 2 owner
        - Create 2 restaurants and binding owner
        - Create a customer
        - Make a review for the restaurants
        - calculate the rating for all restaurants
        - check on db the new rating
        - erase all data create inside the test
        """
        owner_one = create_user_on_db(123444223)
        assert owner_one is not None
        owner_two = create_user_on_db(123444226)
        assert owner_two is not None

        restaurant_one = create_restaurants_on_db(name="First", user_id=owner_one.id)
        assert restaurant_one is not None
        restaurant_two = create_restaurants_on_db(name="Second", user_id=owner_two.id)
        assert restaurant_two is not None

        start_one = 3.0
        start_two = 5.0
        review = create_review_for_restaurants(
            starts=start_one, rest_id=restaurant_one.id
        )
        assert review is not None
        review = create_review_for_restaurants(
            starts=start_two, rest_id=restaurant_one.id
        )
        assert review is not None

        start_tree = 2.0
        review = create_review_for_restaurants(
            starts=start_tree, rest_id=restaurant_two.id
        )
        assert review is not None

        rating_rest_one = (start_one + start_two) / 2
        rating_rest_two = start_tree

        RestaurantServices.calculate_rating_for_all()

        rest = get_rest_with_name(restaurant_one.name)
        assert rest.rating == rating_rest_one
        rest = get_rest_with_name(restaurant_two.name)
        assert rest.rating == rating_rest_two

        del_all_review_for_rest(restaurant_one.id)
        del_all_review_for_rest(restaurant_two.id)
        del_restaurant_on_db(restaurant_one.id)
        del_restaurant_on_db(restaurant_two.id)
        del_user_on_db(owner_one.id)
        del_user_on_db(owner_two.id)

    def test_rating_single_restaurant(self):
        """
        This method test the method to calculate a rating inside a new restautants

        Test flow:
        - Create owner
        - Create restaurant1 and binding owner
        - Create a customer
        - Make a review for the restaurant
        - check the result of the function
        - check on bd the new rating
        - erase all data create inside the test
        """
        owner_one = create_user_on_db(randrange(100000))
        assert owner_one is not None

        restaurant_one = create_restaurants_on_db(name="First", user_id=owner_one.id)
        assert restaurant_one is not None

        start_one = 3.0
        start_two = 4.5
        review = create_review_for_restaurants(
            starts=start_one, rest_id=restaurant_one.id
        )
        assert review is not None
        review = create_review_for_restaurants(
            starts=start_two, rest_id=restaurant_one.id
        )
        assert review is not None

        rating_rest_one = (start_one + start_two) / 2.0

        rating = RestaurantServices.get_rating_restaurant(restaurant_one.id)
        assert rating == rating_rest_one

        rest = get_rest_with_name(restaurant_one.name)
        assert rest.rating == rating_rest_one

        del_all_review_for_rest(restaurant_one.id)
        del_restaurant_on_db(restaurant_one.id)
        del_user_on_db(owner_one.id)

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
        owner_one = create_user_on_db(randrange(100000))
        assert owner_one is not None

        restaurant_one = create_restaurants_on_db(name="First", user_id=owner_one.id)
        assert restaurant_one is not None

        all_people = RestaurantServices.get_restaurant_people(restaurant_one.id)
        assert all_people is not None
        assert len(all_people) == 3
        assert all_people[0] == 0
        assert all_people[1] == 0
        assert all_people[2] == 0
        del_restaurant_on_db(restaurant_one.id)
        del_user_on_db(owner_one.id)


"""
          The method test the function inside the RestaurantServices to search all the people
        inside the restaurants, the function return an array that looks like
        [people_to_lunch, people_to_dinner, people_checkin]
        Test flow
        - new restaurants
        - new booking
        - get all people
        - del restaurant
        """
""" 
    def test_get_restaurant_people(self):
        
        owner_one = create_user_on_db(randrange(100000))
        assert owner_one is not None

        restaurant_one = create_restaurants_on_db(name="First", user_id=owner_one.id)
        assert restaurant_one is not None
        
        customer_one = create_user_on_db(randrange(100000))
        customer_two = create_user_on_db(randrange(100000))
        # TODO I missing the logic, this is possible?

        # books_lunch = create_random_booking(1, rest_id=restaurant_one.id, customer_one, date_time=datetime(2020))

        all_people = RestaurantServices.get_restaurant_people(restaurant_one.id)
        assert all_people is not None
        assert len(all_people) == 3
        assert all_people[0] == 0
        assert all_people[1] == 0
        assert all_people[2] == 0
        del_restaurant_on_db(restaurant_one.id)
"""
