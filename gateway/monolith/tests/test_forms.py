"""
This test case covered all simple action that we can do from the UI
"""
from monolith.database import Review
from monolith.tests.utils import *
from datetime import datetime, timedelta


class Test_GoOutSafeForm:
    """
    This test suite tested the application behavior about the flask client
    In this case we are testing the flask response and not the UI workflow.
    In other words, we are not testing the click on link that perform an action but we are
    testing the flask response with a correct url and correct app status.

    The response from flask is tested with an hidden tak returned from flask method.
    If possible see this hidden tak inside the method render_template with the name _tests.
    """

    def test_login_form_ok(self, client):
        """
        This test suit test the operation that we can do
        to login correctly an user
        """
        form = UserForm()
        form.firstname.data = "user_{}".format(randrange(10000))
        form.lastname.data = "user_{}".format(randrange(10000))
        form.password.data = "pass_{}".format(randrange(10000))
        form.phone.data = "12345{}".format(randrange(10000))
        form.dateofbirth.data = "1995-12-12"
        form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        result = UserService.create_user(form, 2)
        assert result is True
        assert result < 300

        response = login(client, form.email.data, form.password.data)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        user = UserService.user_is_present(form.email.data, form.phone.data)

        result_delete = UserService.delete_user(user.id)
        assert result_delete is True

    def test_login_form_ko(self, client):
        """
        This test suit test the operation that we can do
        to login correctly an user
        """
        email = "vincenzopalazzo@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "error_login" in response.data.decode("utf-8")

        user = UserService.user_is_present(email, "1234555")
        assert user is None

    def test_register_new_user_ok(self, client):
        """
        This use case try to login a new user with a correct execution

        The flow of this test is
        - Create user
        - Verify user on db
        - login user
        - verify the html returned from flask
        :param client: The flask app created inside the fixtures
        """
        user_form = UserForm()
        user_form.firstname.data = "user_{}".format(randrange(10000))
        user_form.lastname.data = "user_{}".format(randrange(10000))
        user_form.password.data = "pass_{}".format(randrange(10000))
        user_form.phone.data = "12345{}".format(randrange(10000))
        user_form.dateofbirth.data = "12/12/1995"
        user_form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        response = register_user(client, user_form)
        assert response.status_code == 200
        assert "first_visit_login" in response.data.decode("utf-8")

        ## Search inside the DB if this user exist
        user = UserService.user_is_present(user_form.email.data, user_form.phone.data)
        assert user is not None

        response = login(client, user_form.email.data, user_form.password.data)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = logout(client)
        assert response.status_code == 200
        assert "anonymous_test" not in response.data.decode("utf-8")

        result_delete = UserService.delete_user(user.id)
        assert result_delete is True

    def test_register_new_restaurant_ok(self, client):
        """
        This test test the use case to create a new restaurant
        and this test have the follow described below

        - Login like a operator (user the standard account)
        - Register a new restaurant
        - Look inside the db to see if the restaurant exist
        - Log out user
        - See if the restaurant is present on home screen.

        :param client:
        """

        form = UserForm()
        rand = randrange(100000)
        form.firstname.data = "User_{}".format(rand)
        form.lastname.data = "user_{}".format(rand)
        form.password.data = "Alibaba{}".format(rand)
        form.phone.data = "1234562344{}".format(rand)
        form.dateofbirth.data = "1985-12-12"
        form.email.data = "user{}@user.edu".format(str(rand))
        created = UserService.create_user(form, 2)
        assert created is True
        user = UserService.user_is_present(form.email.data, form.phone.data)
        assert user is not None

        response = login(client, user.email, form.password.data)
        assert response.status_code == 200

        restaurant_form = RestaurantForm()
        restaurant_form.name.data = "rest_rand_{}".format(randrange(10000))
        restaurant_form.phone.data = "096321343_{}".format(randrange(10000))
        restaurant_form.lat.data = 12
        restaurant_form.lon.data = 12
        restaurant_form.n_tables.data = 50
        restaurant_form.covid_measures.data = "Random comment_{}".format(
            randrange(10000)
        )
        restaurant_form.cuisine.data = ["Italian food"]
        restaurant_form.open_days.data = ["0"]
        restaurant_form.open_lunch.data = "12:00"
        restaurant_form.close_lunch.data = "15:00"
        restaurant_form.open_dinner.data = "18:00"
        restaurant_form.close_dinner.data = "00:00"
        response = register_restaurant(client, restaurant_form)
        assert response.status_code == 200  ## Regirect to /
        # assert restaurant_form.name in response.data.decode("utf-8")
        assert "logged_test" in response.data.decode("utf-8")
        # test if the db is clean
        list_rest = db.session.query(Restaurant).all()
        assert len(list_rest) == 1
        # assert response.status_code == 200
        # assert "create_rest_test" not in response.data.decode("utf-8")

        rest = RestaurantServices.get_restaurants_by_keyword(restaurant_form.name.data)
        assert rest is not None

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")

        response = client.get("/")  ## get index
        assert restaurant_form.name.data in response.data.decode("utf-8")

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")

        result = RestaurantServices.delete_restaurant(rest[0].id)
        assert result is True

    def test_register_new_restaurant_ko(self, client):
        """
        This test test the use case to create a new restaurant but the user
        and this test have the follow described below

        - Register a new user
        - Register a new restaurant
        - receive the 401 error because the user is not a customer
        - Delete the user

        :param client:
        """
        form = UserForm()
        rand = randrange(100000)
        form.firstname.data = "User_{}".format(rand)
        form.lastname.data = "user_{}".format(rand)
        form.password.data = "Alibaba{}".format(rand)
        form.phone.data = "1234562344{}".format(rand)
        form.dateofbirth.data = "1985-12-12"
        form.email.data = "user{}@user.edu".format(str(rand))
        created = UserService.create_user(form, 3)
        assert created is True
        user = UserService.user_is_present(form.email.data, form.phone.data)
        assert user is not None

        response = login(client, user.email, form.password.data)
        assert response.status_code == 200

        user = get_user_with_email(user.email)
        assert user is not None
        assert user.role_id == 3  ## Customer

        restaurant_form = RestaurantForm()
        restaurant_form.name.data = "rest_rand_{}".format(randrange(10000))
        restaurant_form.phone.data = "096321343_{}".format(randrange(10000))
        restaurant_form.lat.data = 12
        restaurant_form.lon.data = 12
        restaurant_form.n_tables.data = 50
        restaurant_form.covid_measures.data = "Random comment_{}".format(
            randrange(10000)
        )
        restaurant_form.cuisine.data = ["Italian food"]
        restaurant_form.open_days.data = ["0"]
        restaurant_form.open_lunch.data = "12:00"
        restaurant_form.close_lunch.data = "15:00"
        restaurant_form.open_dinner.data = "18:00"
        restaurant_form.close_dinner.data = "00:00"
        response = register_restaurant(client, restaurant_form)
        assert response.status_code == 401

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")

    def test_research_restaurant_by_name(self, client):
        """
        This method perform the flask request to search the restaurant by name
        or an key inside the name
        :param client:
        :return:
        """
        owner = create_user_on_db(randrange(100000))
        assert owner is not None

        restaurant = create_restaurants_on_db(
            name="First", user_id=owner.id, user_email=owner.email
        )
        assert restaurant is not None

        response = research_restaurant(client, restaurant.name)
        assert response.status_code is 200
        assert "rest_search_test" in response.data.decode("utf-8")

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")

        del_user_on_db(owner.id)
        result = RestaurantServices.delete_restaurant(restaurant.id)
        assert result is True

    def test_research_restaurant_by_name_ok_with_anonymus(self, client):
        """
        This method perform the flask request to search the restaurant by name
        or an key inside the name
        :param client:
        :return:
        """
        owner = create_user_on_db(randrange(100000))
        assert owner is not None

        restaurant = create_restaurants_on_db(
            name="First", user_id=owner.id, user_email=owner.email
        )
        assert restaurant is not None

        response = research_restaurant(client=client, name=restaurant.name)
        assert response.status_code is 200
        assert "rest_search_test" in response.data.decode("utf-8")

        del_user_on_db(owner.id)
        result = RestaurantServices.delete_restaurant(restaurant.id)
        assert result is True

    def test_open_photo_view_ok(self, client):
        """
        This test perform the use case described below
        - create a new user
        - create a new restaurant
        - open the single restaurant view
        - Go to photo gallery
        - check if the page is load correctly
        """
        user = create_user_on_db(randrange(100000), password="ciccio")

        response = login(client, user.email, "ciccio")
        assert response.status_code == 200

        owner = create_user_on_db(randrange(100000), role_id=2)
        assert owner is not None
        restaurant = create_restaurants_on_db(
            name="First", user_id=owner.id, user_email=owner.email
        )
        assert restaurant is not None

        response = visit_restaurant(client, restaurant.id)
        assert response.status_code == 200
        assert "visit_rest_test" in response.data.decode("utf-8")

        user_stored = get_user_with_email(user.email)
        response = visit_photo_gallery(client)
        ## the user is a customer and not a operator
        assert response.status_code == 401

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")

        del_user_on_db(id=owner.id)
        del_user_on_db(id=user_stored.id)

    def test_mark_positive_ko(self, client):
        """
        This test cases test the use case to mark a person as covid19
        positive, the work flow is the following:
        - Login as normal user (this is wrong, the test should be failed)
        - Create a new customer
        - mark this customer as positive
        - delete the customer
        :param client:
        """
        response = login(client, "john.doe@email.com", "customer")
        assert response.status_code == 200

        user = UserForm()
        user.email.data = "messi@gmail.com"
        user.firstname.data = "Messi"
        user.lastname.data = "Ronaldo"
        user.password.data = "messi434324"
        user.phone.data = "32343242455"
        user.dateofbirth.data = "12/12/1975"
        register_user(client, user)

        mark = SearchUserForm()
        mark.email.data = user.email.data
        mark.phone.data = user.phone.data
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 401

        user = UserService.user_is_present(user.email.data, user.phone.data)
        assert user.is_positive is False
        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")

        del_user_on_db(user.id)

    def test_mark_positive_ok(self, client):
        """
        This test cases test the use case to mark a person as covid19
        positive, the work flow is the following:
        - Login as normal user (this is wrong, the test should be failed)
        - Create a new customer
        - mark this customer as positive
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "cr7@gmail.com"
        user.firstname.data = "Cristiano"
        user.lastname.data = "Ronaldo"
        user.password.data = "Siiidasdasdasda"
        user.phone.data = "1234555"
        user.dateofbirth.data = "12/12/1975"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = user.email.data
        mark.phone.data = user.phone.data
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email.data)
        assert user.is_positive is True

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")

        del_user_on_db(user.id)

    def test_see_reservation_ok(self, client):
        """
        This test unit, tests the use case to perform the request to access from reservation
        as customer
        """
        form = UserForm()
        rand = randrange(100000)
        form.firstname.data = "User_{}".format(rand)
        form.lastname.data = "user_{}".format(rand)
        form.password.data = "Alibaba{}".format(rand)
        form.phone.data = "1234562344{}".format(rand)
        form.dateofbirth.data = "1985-12-12"
        form.email.data = "user{}@user.edu".format(str(rand))
        created = UserService.create_user(form, 3)
        assert created is True
        user = UserService.user_is_present(form.email.data, form.phone.data)
        assert user is not None

        response = login(client, user.email, form.password.data)
        assert response.status_code == 200

        response = visit_customer_reservation(
            client, from_date="2013-10-07T00:00:00Z", to_date="2014-10-07T00:00:00Z"
        )
        assert response.status_code == 200
        assert "customer_reservations_test" in response.data.decode("utf-8")

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")
        del_user_on_db(user.id)

    def test_make_review_ko(self, client):
        """
        This test unit, tests the use case to perform the request to make a new review
        with error as customer
        """
        email = "health_authority@gov.com"
        pazz = "nocovid"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        trial_rest = RestaurantServices.get_all_restaurants()[0]
        form = ReviewForm()
        form.stars.data = 3
        form.review.data = "Good food"
        response = make_revew(client, trial_rest["id"], form)
        assert response.status_code == 401

    def test_make_review_ko_operator(self, client):
        """
        operators can't do reviews
        """
        email = "ham.burger@email.com"
        pazz = "operator"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        trial_rest = RestaurantServices.get_all_restaurants()[0]
        form = ReviewForm()
        form.stars.data = 3
        form.review.data = "Good food"
        response = make_revew(client, trial_rest["id"], form)
        assert response.status_code == 401

    def test_make_review_ok(self, client):
        """
        operators can't do reviews
        """
        email = "john.doe@email.com"
        pazz = "customer"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        trial_rest = RestaurantServices.get_all_restaurants()[0]
        form = ReviewForm()
        form.stars.data = 3
        form.review.data = "Good food"
        response = make_revew(client, trial_rest["id"], form)
        assert response.status_code == 200
        assert "review_done_test" in response.data.decode("utf-8")

        response = logout(client)
        assert response.status_code == 200
        assert "not_logged_test" not in response.data.decode("utf-8")
        # TODO remove review
        # db.session.query(Review).filter_by(review=form.review).delete()
        # db.session.commit()

    def test_mark_positive_ok_email(self, client):
        """
        This test cases test the use case to mark a person as covid19
        positive using the email, the work flow is the following:
        - Create a new customer
        - health authority marks this customer as positive
        - check the customer is positive
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "cr7@gmail.com"
        user.firstname.data = "Cristiano"
        user.lastname.data = "Ronaldo"
        user.password.data = "Siiidasdasdasda"
        user.phone.data = "1234555"
        user.dateofbirth.data = "12/12/1975"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = user.email.data
        mark.phone.data = ""
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email.data, user.phone.data)
        assert user.is_positive is True

        del_user_on_db(user.id)

    def test_mark_positive_ok_phone(self, client):
        """
        This test cases test the use case to mark a person as covid19
        positive using the phone, the work flow is the following:
        - Create a new customer
        - health authority marks this customer as positive using the phone number
        - check the customer is positive
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "cr7@gmail.com"
        user.firstname.data = "Cristiano"
        user.lastname.data = "Ronaldo"
        user.password.data = "Siiidsadasdasdas"
        user.phone.data = "12345565"
        user.dateofbirth.data = "12/12/1975"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = ""
        mark.phone.data = user.phone.data
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email.data, user.phone.data)
        assert user.is_positive is True

        del_user_on_db(user.id)

    def test_mark_positive_ko_user_already_positive(self, client):
        """
        This test try to mark an user already positive.

        The work flow is reported below:
        - Create a new customer
        - health authority marks this customer as positive
        - check the customer is positive
        - health authority tries to mark the customer (already positive) as positive
        - delete the customer
        :param client:
        """
        user = create_user_on_db(randrange(1, 500000))

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = user.email
        mark.phone.data = user.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        user = UserService.user_is_present(user.email, user.phone)
        assert user.is_positive is True

        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200
        assert "mark_positive_page_error_test" in response.data.decode("utf-8")

        del_user_on_db(user.id)

    def test_mark_positive_ko_not_registered_user(self, client):
        """
        This test cases test the use case to mark a not registered
        person as covid19 positive. The work flow is the following:
        - health authority tries to mark a not registered customer as positive
        :param client:
        """
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = "joe@gmail.com"
        mark.phone.data = "324545"
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200
        assert "mark_positive_page" in response.data.decode("utf-8")

    def test_mark_positive_ko_empty_fields(self, client):
        """
        This test cases test the use case where the health authority
        tries o mark as a positive a customer indicating no data of user
        - health authority tries to mark a user as positive indicating no data
        :param client:
        """
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = ""
        mark.phone.data = ""
        response = unmark_people_for_covid19(client, mark)
        assert response.status_code == 200
        assert "mark_positive_page" in response.data.decode("utf-8")

    def test_unmark_positive_ko_unathorized(self, client):
        """
        This test cases test the use case where a customer tries to
        unmark as not positive himself. The work flow is the following:
        - register a new customer
        - this customer tries to mark himself as not positive person
        - delete the customer
        :param client:
        """
        response = login(client, "john.doe@email.com", "customer")
        assert response.status_code == 200

        user = UserForm()
        user.email.data = "joe@gmail.com"
        user.firstname.data = "joe"
        user.lastname.data = "joe"
        user.password.data = "joejoe"
        user.phone.data = "324545"
        user.dateofbirth.data = "24/10/1987"
        register_user(client, user)

        unmark = SearchUserForm()
        unmark.email.data = user.email.data
        unmark.phone.data = user.phone.data
        response = unmark_people_for_covid19(client, unmark)
        assert response.status_code == 401

        q_user = UserService.user_is_present(user.email.data, user.phone.data)
        del_user_on_db(q_user.id)

    def test_unmark_positive_ko_user_not_positive(self, client):
        """
        This test cases test the use case where the health authority
        try to mark as healed a not positive person. The work flow is the following:
        - register a new customer
        - the health authority tries to unmark a not positive person
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "joe@gmail.com"
        user.firstname.data = "joe"
        user.lastname.data = "joe"
        user.password.data = "joejoe"
        user.phone.data = "324545"
        user.dateofbirth.data = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        unmark = SearchUserForm()
        unmark.email.data = user.email
        unmark.phone.data = user.phone
        response = unmark_people_for_covid19(client, unmark)
        assert response.status_code == 200
        assert "unmark_positive_page" in response.data.decode("utf-8")

        user = UserService.user_is_present(user.email.data, user.phone.data)
        assert user.is_positive is False

        del_user_on_db(user.id)

    def test_unmark_positive_ko_user_not_registered(self, client):
        """
        This test cases test the use case where the health authority
        try to mark as healed a person who is not registered.
        The work flow is the following:
        - the health authority tries to unmark a person who isn't registered
        :param client:
        """
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        unmark = SearchUserForm()
        unmark.email.data = "joe@gmail.com"
        unmark.phone.data = "324545"
        response = unmark_people_for_covid19(client, unmark)
        assert response.status_code == 200
        assert "unmark_positive_page" in response.data.decode("utf-8")

    def test_unmark_positive_ko_empty_fields(self, client):
        """
        This test cases test the use case where the health authority
        try to mark a person inserting no data. The work flow is the following:
        - register a new customer
        - the health authority tries to unmark a person inserting no data
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "joe@gmail.com"
        user.firstname.data = "joe"
        user.lastname.data = "joe"
        user.password.data = "joejoe"
        user.phone.data = "324545"
        user.dateofbirth.data = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = user.email.data
        mark.phone.data = user.phone.data
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email.data, user.phone.data)
        assert user.is_positive is True

        unmark = SearchUserForm()
        unmark.email.data = ""
        unmark.phone.data = ""

        response = unmark_people_for_covid19(client, unmark)
        assert response.status_code == 200
        assert "unmark_positive_page" in response.data.decode("utf-8")

        user = UserService.user_is_present(user.email, user.phone)
        assert user.is_positive is True

        del_user_on_db(user.id)

    def test_unmark_positive_ok(self, client):
        """
        This test cases test the use case where the health authority
        try to mark as healed a positive person. The work flow is the following:
        - register a new customer
        - the health authority marks the customer as positive
        - the health authority unmarks te customer
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "joe@gmail.com"
        user.firstname.data = "joe"
        user.lastname.data = "joe"
        user.password.data = "joejoe"
        user.phone.data = "324545"
        user.dateofbirth.data = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = user.email.data
        mark.phone.data = user.phone.data
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email.data, user.phone.data)
        assert user.is_positive is True

        response = unmark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email, user.phone)
        assert user.is_positive is False

        del_user_on_db(user.id)

    def test_unmark_positive_email(self, client):
        """
        This test cases test the use case where the health authority
        try to mark as healed a positive person using the email.
        The work flow is the following:
        - register a new customer
        - the health authority marks the customer as positive
        - the health authority unmarks te customer using only the email
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "joe@gmail.com"
        user.firstname.data = "joe"
        user.lastname.data = "joe"
        user.password.data = "joejoe"
        user.phone.data = "324545"
        user.dateofbirth.data = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = user.email.data
        mark.phone.data = ""
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email.data, user.phone.data)
        assert user.is_positive is True

        response = unmark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email, user.phone)
        assert user.is_positive is False

        del_user_on_db(user.id)

    def test_unmark_positive_ok_phone(self, client):
        """
        This test cases test the use case where the health authority
        try to mark as healed a positive person using the phone number.
        The work flow is the following:
        - register a new customer
        - the health authority marks the customer as positive
        - the health authority unmarks te customer using only the phone number
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "joe@gmail.com"
        user.firstname.data = "joe"
        user.lastname.data = "joe"
        user.password.data = "joejoe"
        user.phone.data = "324545"
        user.dateofbirth.data = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = ""
        mark.phone.data = user.phone.data
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email.data, user.phone.data)
        assert user.is_positive is True

        response = unmark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(user.email, user.phone)
        assert user.is_positive is False

        del_user_on_db(user.id)

    def test_search_contacts_with_positive_ko(self, client):
        """
        This test cases test the use case where the health authority
        try to search contacts of a not positive person.
        The work flow is the following:
        - register a new customer
        - the health authority tries to search the contacts of this customer
        - delete the customer
        :param client:
        """
        user = UserForm()
        user.email.data = "joe@gmail.com"
        user.firstname.data = "joe"
        user.lastname.data = "joe"
        user.password.data = "joejoe"
        user.phone.data = "324545"
        user.dateofbirth.data = "24/10/1987"
        register_user(client, user)

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = user.email.data
        mark.phone.data = user.phone.data
        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200
        assert "search_contacts_no_positive" in response.data.decode("utf-8")

        q_user = UserService.user_is_present(user.email.data, user.phone.data)
        del_user_on_db(q_user.id)

    def test_search_contacts_with_user_not_registered(self, client):
        """
        This test cases test the use case where the health authority
        try to search contacts of a not registered person.
        The work flow is the following:
        - the health authority tries to search the contacts of a customer
          who is not registered
        :param client:
        """
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = "joe@gmail.com"
        mark.phone.data = "324545"
        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200
        assert "search_contact_not_registered" in response.data.decode("utf-8")

    def test_create_new_menu_restaurant_ok(self, client):
        """
        This test case perform the request with flask client to make
        the request to access at the db
        :param client:
        :return:
        """
        email = "ham.burger@email.com"
        pazz = "operator"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # GET
        response = client.get("/restaurant/menu")
        assert response.status_code is 200
        assert "menu_view_test" in response.data.decode("utf-8")

        rest = RestaurantServices.get_all_restaurants()[0]
        form = DishForm()
        form.name = "Pasta"
        form.price = 14

        with client.session_transaction() as session:
            session["RESTAURANT_ID"] = rest["id"]

        response = create_new_menu(client, form)
        assert response.status_code is 200
        assert "menu_view_test" in response.data.decode("utf-8")


        #delete th dish
        dish_id = None
        dishes = RestaurantServices.get_dishes_restaurant(rest["id"])
        for dish in dishes:
            if dish.name == "Pasta":
                print (dish.name)
                dish_id = dish.id
        if dish_id is not None:
            RestaurantServices.delete_dish(dish_id)

        logout(client)



    def test_create_new_menu_restaurant_ko(self, client):
        """
        This test case perform the request with flask client to make
        the request to access at the db
        :param client:
        :return:
        """
        rest = db.session.query(Restaurant).all()[0]
        form = DishForm()
        form.name = "Pasta"
        form.price = 14
        with client.session_transaction() as session:
            session["RESTAURANT_ID"] = rest.id
        response = create_new_menu(client, form)
        assert response.status_code is not 403

    def test_create_new_reservation_ok(self, client):
        """
        This test case perform the request in order to create
        a new reservation for user john doe
        :param client:
        :return:
        """

        email = "john.doe@email.com"
        pazz = "customer"
        response = login(client, email, pazz)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        restaurant = (
            db.session.query(Restaurant).filter_by(name="Trial Restaurant").first()
        )
        form = ReservationForm()
        form.restaurant_id = restaurant.id
        form.reservation_date = "25/11/2120 12:00"
        form.people_number = 2
        form.friends = "aa@aa.com"

        response = create_new_reservation(client, form)
        assert response.status_code == 200

        # delete data from db
        d1 = datetime(year=2120, month=11, day=25, hour=12)
        db.session.query(Reservation).filter_by(reservation_date=d1).delete()
        db.session.commit()

    def test_create_new_reservation_ko(self, client):
        """
        This test case perform the request in order to create
        a new reservation for user john doe THAT HAVE TO FAIL
        RESTAURANT IS CLOSED AT 10:00
        :param client:
        :return:
        """

        email = "john.doe@email.com"
        pazz = "customer"
        response = login(client, email, pazz)
        user = get_user_with_email(email)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        restaurant = create_restaurants_on_db(user_id=email)

        form = ReservationForm()
        form.restaurant_id = restaurant.id
        form.reservation_date = "23/11/2021 10:00"
        form.people_number = 2
        form.friends = "a@a.com"

        response = create_new_reservation(client, form)
        assert response.status_code == 200
        print(response.data.decode("utf-8"))
        assert "Cannot place your booking." in response.data.decode("utf-8")

        del_restaurant_on_db(restaurant.id)

    def test_create_new_reservation_unauthorized(self, client):
        """
        not logged client can not book.
        :param client:
        :return:
        """

        restaurant = (
            db.session.query(Restaurant).filter_by(name="Trial Restaurant").first()
        )
        form = ReservationForm()
        form.restaurant_id = restaurant.id
        form.reservation_date = "23/11/2020 12:00"
        form.people_number = 2
        form.friends = "aa@aa.com;bb@bb.com"

        response = create_new_reservation(client, form)
        assert response.status_code == 401

    def test_create_operator(self, client):
        """
        test to create an operator
        """
        # view page
        client.get("/create_operator")

        # POST
        user = UserForm()
        user.firstname.data = "Steve"
        user.lastname.data = "Jobs"
        user.email.data = "steve{}@apple.com".format(randrange(100000))
        response = create_new_user_with_form(client, user, "operator")

        assert response.status_code == 200
        print (response.data.decode("utf-8"))
        assert "logged_test" in response.data.decode("utf-8")
        user = UserService.user_is_present(user.email.data)
        del_user_on_db(user.id)

    def test_edit_user_data(self, client):
        """
        test edit of user info
        """
        form = UserForm()
        form.firstname.data = "user_{}".format(randrange(10000))
        form.lastname.data = "user_{}".format(randrange(10000))
        form.password.data = "pass_{}".format(randrange(10000))
        form.phone.data = "12345{}".format(randrange(10000))
        form.dateofbirth.data = "1995-12-12"
        form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        result = UserService.create_user(form, 2)
        assert result is True
        assert result < 300

        response = login(client, form.email.data, form.password.data)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # view page
        client.get("/user/data")

        # POST
        name = "Stefano"
        response = client.post(
            "/user/data",
            data=dict(
                email=form.email.data,
                firstname=name,
                lastname="Lavori",
                dateofbirth="22/03/1998",
                phone = "123434323432",
                headers={"Content-type": "application/x-www-form-urlencoded"},
            ),
            follow_redirects=True,
        )

        assert response.status_code == 200
        user = UserService.user_is_present(form.email.data)
        assert user.firstname == name

    def test_delete_user(self, client):
        """
        test delete user url
        """
        form = UserForm()
        form.firstname.data = "user_{}".format(randrange(10000))
        form.lastname.data = "user_{}".format(randrange(10000))
        form.password.data = "pass_{}".format(randrange(10000))
        form.phone.data = "12345{}".format(randrange(10000))
        form.dateofbirth.data = "1995-12-12"
        form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        result = UserService.create_user(form, 2)
        assert result is True
        assert result < 300

        response = login(client, form.email.data, form.password.data)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = client.get("/user/delete")
        assert response.status_code == 302

    def test_get_user_reservations(self, client):
        """
        test reservation page of customer
        """
        email = "john.doe@email.com"
        password = "customer"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = client.get("/customer/reservations")
        assert response.status_code == 200

    def test_create_restaurant_form(self, client):
        """
        test to create a restaurant
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # view page
        response = client.get("/restaurant/create")
        assert response.status_code == 200

        # POST
        restaurant = RestaurantForm()
        restaurant.name = "Krusty Krab"
        restaurant.phone = "0451245152"
        restaurant.lat = "1"
        restaurant.lon = "1"
        restaurant.n_tables = "1"
        restaurant.cuisine = "Italian food"
        restaurant.open_days = "0"
        restaurant.open_lunch = "11:00"
        restaurant.close_lunch = "12:00"
        restaurant.open_dinner = "20:00"
        restaurant.close_dinner = "21:00"
        restaurant.covid_measures = "masks"
        response = create_new_restaurant_with_form(client, restaurant)
        assert response.status_code == 200
        assert "Register your Restaurant" not in response.data.decode("utf-8")

    def test_create_restaurant_already_form(self, client):
        """
        test to create a restaurant already existent
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # POST
        restaurant = RestaurantForm()
        restaurant.name = "Krusty Krab"
        restaurant.phone = "0451245152"
        restaurant.lat = "1"
        restaurant.lon = "1"
        restaurant.n_tables = "1"
        restaurant.cuisine = "Italian food"
        restaurant.open_days = "0"
        restaurant.open_lunch = "11:00"
        restaurant.close_lunch = "12:00"
        restaurant.open_dinner = "20:00"
        restaurant.close_dinner = "21:00"
        restaurant.covid_measures = "masks"
        response = create_new_restaurant_with_form(client, restaurant)
        assert response.status_code == 200
        print (response.data.decode)
        assert "Register your Restaurant" in response.data.decode("utf-8")

        db.session.query(Restaurant).filter_by(name=restaurant.name).delete()
        db.session.query(OpeningHours).delete()
        db.session.commit()

    def test_edit_restaurant_data(self, client):
        """
        test edit of restaurant info
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # view page
        response = client.get("/restaurant/data")
        assert response.status_code == 200
        # TODO miss the code inside this methos

    def test_create_and_delete_table(self, client):
        """
        test to create a table and then destroy it
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        table = RestaurantTable()
        table.restaurant_id = "1"
        table.max_seats = "4"
        table.name = "TestTable123"
        response = create_new_table(client, table)
        assert response.status_code == 200
        assert table.name in response.data.decode("utf-8")

        table = db.session.query(RestaurantTable).filter_by(name="TestTable123").first()
        assert table is not None

        response = client.get("/restaurant/tables?id=" + str(table.id))
        assert response.status_code == 302

    def test_add_photo(self, client):
        """
        test to create a photo
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        photo = PhotoGalleryForm()
        photo.caption = "photo"
        photo.url = "https://www.google.com/pic.jpg"
        response = create_new_photo(client, photo)
        assert response.status_code == 200
        assert photo.caption in response.data.decode("utf-8")

    def test_delete_reservation(self, client):
        """
        test delete reservation by customer
        """
        email = "john.doe@email.com"
        password = "customer"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        reservation = db.session.query(Reservation).first()
        assert reservation is not None

        response = del_reservation_client(client, reservation.id)
        assert response.status_code == 200
        assert "del_rest_test" in response.data.decode("utf-8")

    def test_list_customer_reservations(self, client):
        """
        test list customer reservations
        """
        email = "john.doe@email.com"
        password = "customer"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        response = get_reservation(client)
        assert response.status_code == 200

    def test_operator_checkin(self, client):
        """
        test checkin
        """
        email = "ham.burger@email.com"
        password = "operator"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")
        reservation = db.session.query(Reservation).first()
        assert reservation is not None
        before_checkin = reservation.checkin
        assert before_checkin is False

        response = client.get("/restaurant/checkinreservations/" + str(reservation.id))
        assert response.status_code == 302

        reservation_after = (
            db.session.query(Reservation).filter_by(id=reservation.id).first()
        )
        assert reservation_after.checkin is True

    def test_update_booking(self, client):
        """
        not logged client can not book.
        :param client:
        :return:
        """
        email = "john.doe@email.com"
        password = "customer"
        response = login(client, email, password)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        reservation = db.session.query(Reservation).first()
        assert reservation is not None
        table = (
            db.session.query(RestaurantTable).filter_by(id=reservation.table_id).first()
        )
        assert table is not None

        form = ReservationForm()
        form.reservation_id = reservation.id
        form.restaurant_id = table.restaurant_id
        form.reservation_date = "29/11/2030 12:00"
        form.people_number = 4
        form.friends = "a@a.com;b@b.com;c@c.com"

        response = client.post(
            "/restaurant/book_update",
            data=dict(
                reservation_id=form.reservation_id,
                reservation_date=form.reservation_date,
                people_number=form.people_number,
                restaurant_id=form.restaurant_id,
                friends=form.friends,
                submit=True,
                headers={"Content-type": "application/x-www-form-urlencoded"},
            ),
            follow_redirects=True,
        )
        assert response.status_code == 200
        d1 = datetime(year=2030, month=11, day=29, hour=12)
        reservation_new = (
            db.session.query(Reservation).filter_by(reservation_date=d1).first()
        )
        assert reservation_new is not None

    def test_search_contacts_with_user_not_registered(self, client):
        """
        This test cases test the use case where the health authority
        try to search contacts of a not registered person.
        The work flow is the following:
        - the health authority tries to search the contacts of a customer
          who is not registered
        :param client:
        """
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = "joe@gmail.com"
        mark.phone.data = "324545"
        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200
        assert "search_contact_not_registered" in response.data.decode("utf-8")

    def test_search_contacts_with_no_data(self, client):
        """
        This test cases test the use case where the health authority
        try to search contacts using no data for the search.
        The work flow is the following:
        - the health authority tries to search the contacts of a customer
          using no data for the search
        :param client:
        """
        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        mark = SearchUserForm()
        mark.email.data = ""
        mark.phone.data = ""
        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200
        assert "search_contacts_no_data" in response.data.decode("utf-8")

    def test_search_contacts_ok(self, client):
        """
        This test cases make a check for the use case where the health authority
        try to search contacts of a positive person.

        The work flow is the following:
        - register a new owner of a restaurant
        - register a new restaurant
        - register a new customer (customer 1)
        - register a new booking for this customer at the restaurant
        - register a new customer (customer 2)
        - register a new booking for this customer at the restaurant
        - the health authority mark the customer 1 as positive
        - the health authority search the contacts of customer 1
        - delete new customers, owner, restaurant and bookings
        :param client:
        """
        # a new owner of a restaurant

        owner = create_user_on_db(randrange(1, 900000), role_id=2)
        assert owner is not None
        restaurant = create_restaurants_on_db(user_id=owner.id, user_email=owner.email)
        assert restaurant is not None

        customer1 = create_user_on_db(randrange(1, 900000))
        assert customer1 is not None

        date_booking_1 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books1 = create_random_booking(
            1, restaurant.id, customer1, date_booking_1, "a@aa.com"
        )
        assert books1 is not None

        # a new user that books in the same restaurant of the previous one
        customer2 = create_user_on_db(randrange(1, 900000))
        assert customer2 is not None

        date_booking_2 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books2 = create_random_booking(
            1, restaurant.id, customer2, date_booking_2, "b@b.com"
        )
        assert books2 is not None

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # an user become covid19 positive
        mark = SearchUserForm()
        mark.email.data = customer1.email
        mark.phone.data = customer1.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        user = UserService.user_is_present(customer1.email, customer1.phone)
        assert user.is_positive is True

        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200
        assert "list_page" in response.data.decode("utf-8")
        assert customer2.email in response.data.decode("utf-8")

        del_user_on_db(customer1.id)
        del_user_on_db(customer2.id)
        del_restaurant_on_db(restaurant.id)
        del_user_on_db(owner.id)

    def test_search_contacts_ok_email(self, client):
        """
        This test cases test the use case where the health authority
        try to search contacts of a positive person using email.
        The work flow is the following:
        - register a new owner of a restaurant
        - register a new restaurant
        - register a new customer (customer 1)
        - register a new booking for this customer at the restaurant
        - register a new customer (customer 2)
        - register a new booking for this customer at the restaurant
        - the health authority mark the customer 1 as positive
        - the health authority search the contacts of customer 1 using the email
        - delete new customers, owner, restaurant and bookings
        :param client:
        """
        # a new owner of a restaurant

        owner = create_user_on_db(randrange(1, 900000), role_id=2)
        assert owner is not None
        restaurant = create_restaurants_on_db(user_id=owner.id, user_email=owner.email)
        assert restaurant is not None

        customer1 = create_user_on_db(randrange(1, 5000000))
        assert customer1 is not None

        date_booking_1 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books1 = create_random_booking(
            1, restaurant.id, customer1, date_booking_1, "a@aa.com"
        )

        assert books1 is not None

        # a new user that books in the same restaurant of the previous one
        customer2 = create_user_on_db(randrange(1, 5000000))
        assert customer2 is not None

        date_booking_2 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books2 = create_random_booking(
            1, restaurant.id, customer2, date_booking_2, "b@b.com"
        )
        assert books2 is not None

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # an user become covid19 positive
        mark = SearchUserForm()
        mark.email.data = customer1.email
        mark.phone.data = ""
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        user = UserService.user_is_present(customer1.email, customer1.phone)
        assert user.is_positive is True

        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200
        assert "list_page" in response.data.decode("utf-8")
        assert customer2.email in response.data.decode("utf-8")

        del_user_on_db(customer1.id)
        del_user_on_db(customer2.id)
        del_restaurant_on_db(restaurant.id)
        del_user_on_db(owner.id)

    def test_search_contacts_ok_phone(self, client):
        """
        This test cases test the use case where the health authority
        try to search contacts of a positive person using phone number.
        The work flow is the following:
        - register a new owner of a restaurant
        - register a new restaurant
        - register a new customer (customer 1)
        - register a new booking for this customer at the restaurant
        - register a new customer (customer 2)
        - register a new booking for this customer at the restaurant
        - the health authority mark the customer 1 as positive
        - the health authority search the contacts of customer 1 using
          the phone number
        - delete new customers, owner, restaurant and bookings
        :param client:
        """
        # a new owner of a restaurant
        owner = create_user_on_db(randrange(1, 5000000), role_id=2)
        assert owner is not None
        restaurant = create_restaurants_on_db(user_id=owner.id, user_email=owner.email)
        assert restaurant is not None

        customer1 = create_user_on_db(randrange(1, 5000000))
        assert customer1 is not None

        date_booking_1 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books1 = create_random_booking(
            1, restaurant.id, customer1, date_booking_1, "a@aa.com"
        )

        assert books1 is not None

        # a new user that books in the same restaurant of the previous one
        customer2 = create_user_on_db(randrange(1, 5000000))
        assert customer2 is not None

        date_booking_2 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books2 = create_random_booking(
            1, restaurant.id, customer2, date_booking_2, "b@b.com"
        )
        assert books2 is not None

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        # an user become covid19 positive
        mark = SearchUserForm()
        mark.email.data = ""
        mark.phone.data = customer1.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200
        assert "logged_test" in response.data.decode("utf-8")

        user = UserService.user_is_present(customer1.email, customer1.phone)
        assert user.is_positive is True

        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200
        assert "list_page" in response.data.decode("utf-8")
        assert customer2.email in response.data.decode("utf-8")

        del_user_on_db(customer1.id)
        del_user_on_db(customer2.id)
        del_restaurant_on_db(restaurant.id)
        del_user_on_db(owner.id)

    def test_search_contacts_ok_no_contacts(self, client):
        """
        This test cases test the use case where the health authority
        try to search contacts of a positive person using phone number.
        The work flow is the following:
        - register a new owner of a restaurant
        - register a new restaurant
        - register a new customer
        - register a new booking for this customer at the restaurant
        - the health authority mark the customer as positive
        - the health authority search the contacts of the customer using
          the phone number
        - delete new customers, owner, restaurant and bookings
        :param client:
        """
        # a new owner of a restaurant
        owner = create_user_on_db(randrange(1, 900000), role_id=2)
        assert owner is not None
        restaurant = create_restaurants_on_db(user_id=owner.id, user_email=owner.email)
        assert restaurant is not None

        # a new client
        customer1 = create_user_on_db(randrange(1, 5000000))
        assert customer1 is not None

        # this user books in the restaurant
        date_booking_1 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books1 = create_random_booking(
            1, restaurant.id, customer1, date_booking_1, "b@b.com"
        )
        assert books1 is not None

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        # an user become covid19 positive
        mark = SearchUserForm()
        mark.email.data = None
        mark.phone.data = customer1.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(customer1.email, customer1.phone)
        assert user.is_positive is True

        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200
        assert "list_page" in response.data.decode("utf-8")

        del_user_on_db(customer1.id)
        del_restaurant_on_db(restaurant.id)
        del_user_on_db(owner.id)


    def test_search_contacts_ok_more_restaurants(self, client):
        """
        This test cases test the use case where the health authority
        try to search contacts of a positive person. There is a
        customer that was in the same restaurant at the same time
        of the positive person and there is a customer that was in another
        restaurant at the same of the previour two customer
        The work flow is the following:
        - register a new owner of a restaurant (owner 1)
        - register a new restaurant (restaurant 1)
        - register a new customer (customer 1)
        - register a new booking for this customer at the restaurant 1
        - register a new customer (customer 2)
        - register a new booking for this customer at the restaurant 1
        - register a new owner of a restaurant (owner 2)
        - register a new restaurant (restaurant 2)
        - register a new customer (customer 3)
        - register a new booking for this customer at restaurant 2
        - the health authority mark the customer 1 as positive
        - the health authority search the contacts of customer 1
        - customer 2 is in the list of contacts (customer 3 is not in the list)
        - delete new customers, owners, restaurants and bookings
        :param client:
        """
        # a new owner of a restaurant
        owner = create_user_on_db(randrange(1, 50000), role_id=2)
        assert owner is not None
        restaurant = create_restaurants_on_db(user_id=owner.id, user_email=owner.email)
        assert restaurant is not None

        # a new customer
        customer1 = create_user_on_db(randrange(1, 50000))
        assert customer1 is not None

        # this user books in the restaurant

        date_booking_1 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books1 = create_random_booking(
            1, restaurant.id, customer1, date_booking_1, "a@a.com"
        )
        assert books1 is not None
        # a new user that books in the same restaurant of the previous one

        customer2 = create_user_on_db(randrange(1, 50000))
        assert customer2 is not None

        date_booking_2 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books2 = create_random_booking(
            1, restaurant.id, customer2, date_booking_2, "b@b.com"
        )
        assert books2 is not None

        # a new owner of a restaurant
        owner2 = create_user_on_db(randrange(1, 50000), role_id=2)
        assert owner2 is not None
        restaurant2 = create_restaurants_on_db(user_id=owner2.id)
        assert restaurant2 is not None

        # a new user that books in this new restaurant
        customer3 = create_user_on_db(randrange(1, 50000), role_id=2)
        assert customer3 is not None

        date_booking_3 = datetime(year=datetime.now().year,
                                  month=datetime.now().month,
                                  day=datetime.now().day,
                                  hour=13) - timedelta(days=3)
        books3 = create_random_booking(
            1, restaurant2.id, customer3, date_booking_3, "c@c.com"
        )
        assert books3 is not None

        response = login(client, "health_authority@gov.com", "nocovid")
        assert response.status_code == 200

        # an user become covid19 positive
        mark = SearchUserForm()
        mark.email.data = None
        mark.phone.data = customer1.phone
        response = mark_people_for_covid19(client, mark)
        assert response.status_code == 200

        user = UserService.user_is_present(customer1.email, customer1.phone)
        assert user.is_positive is True

        response = search_contact_positive_covid19(client, mark)
        assert response.status_code == 200

        assert "list_page" in response.data.decode("utf-8")
        assert customer1.email not in response.data.decode("utf-8")
        assert customer2.email in response.data.decode("utf-8")
        assert customer3.email not in response.data.decode("utf-8")

        del_user_on_db(customer1.id)
        del_user_on_db(customer2.id)
        del_user_on_db(customer3.id)
        del_restaurant_on_db(restaurant.id)
        del_restaurant_on_db(restaurant2.id)
        del_user_on_db(owner.id)
        del_user_on_db(owner2.id)
