import requests
from flask import session, current_app, redirect
from flask_login import current_user, login_user

from src.forms import UserForm, LoginForm
from src.app_constant import (
    USER_MICROSERVICE_URL,
    RESTAURANTS_MICROSERVICE_URL,
    BOOKING_MICROSERVICE_URL,
)
from src.utils.http_utils import HttpUtils
from src.services.restaurant_services import RestaurantServices
from src.model import RestaurantModel
from src.model import UserModel


class UserService:
    """
    This service is a wrapper of all operation with user
    - create a new user
    - deleter a user if exist
    """

    @staticmethod
    def login_user(email: str, password: str) -> (UserModel, int):
        """
        This method perform the http request to perform the login on user microservices
        :return It return the user if the login has success
        """
        current_app.logger.debug("Email user: {}".format(email))
        current_app.logger.debug("Password is {}".format(password))
        url = "{}/login".format(USER_MICROSERVICE_URL)
        current_app.logger.debug("URL to call microservices: {}".format(url))
        json = {"email": email, "password": password}
        response, status_code = HttpUtils.make_post_request(url, json)
        if response is None:
            return None, status_code
        user = UserModel()
        user.fill_from_json(response)
        return user, status_code

    @staticmethod
    def log_in_user(user: UserModel):
        session["current_user"] = user.serialize()
        login_user(user)
        try:
            url = "{}/role/{}".format(USER_MICROSERVICE_URL, str(user.role_id))
            current_app.logger.debug("Url is {}".format(url))
            response = requests.get(url=url)
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return False
        json_response = response.json()
        current_app.logger.debug("Response json content is: {}".format(json_response))
        if not response.ok:
            current_app.logger.error(json_response)
            return False

        role_value = json_response["value"]

        # set the role in the session
        session["ROLE"] = role_value

        if role_value == "OPERATOR":
            # TODO
            # get from restaurant microservice the restaurant of the user
            # and set the session
            try:
                url = "{}/id/{}".format(RESTAURANTS_MICROSERVICE_URL, str(user.email))
                current_app.logger.debug(
                    "Getting the restaurant of the user: Url is {}".format(url)
                )
                response = requests.get(url=url)
            except requests.exceptions.ConnectionError as ex:
                current_app.logger.error(
                    "Error during the microservice call {}".format(str(ex))
                )
                return False

            if response.ok:
                restaurant = RestaurantModel()
                current_app.logger.debug(
                    "Creating Restaurant model starting from: {}".format(
                        response.json()
                    )
                )
                restaurant.fill_from_json(response.json())

                session["RESTAURANT_ID"] = restaurant.id
                session["RESTAURANT_NAME"] = restaurant.name

        return True

    @staticmethod
    def get_user_role(role_id: int):
        """
        This method return the user role with id
        :param user_id:
        :return: role value of the user
        """
        try:
            url = "{}/role/{}/".format(USER_MICROSERVICE_URL, str(role_id))
            current_app.logger.debug("Url is {}".format(url))
            response = requests.get(url=url)
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return False
        json_response = response.json()
        current_app.logger.debug("Response json content is: {}".format(json_response))
        if not response.ok:
            current_app.logger.error(json_response)
            return None
        return json_response["value"]

    @staticmethod
    def user_is_present(email: str = None, phone: str = None):
        """
        This method contains the logic to search a user with the
        :param email: user email if it is present we use to filter user
        :param phone: phone number, if it is present we use to filter user
        :return: use user if exist otherwise, it is return None
        """
        try:
            url = USER_MICROSERVICE_URL
            json = {}
            if email is not None and len(email) != 0:
                url = "{}/user_by_email".format(url)
                json["email"] = email
            else:
                url = "{}/user_by_phone".format(url)
                json["phone"] = phone
            current_app.logger.debug("Url is {}".format(url))
            response = requests.post(url=url, json=json)
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return None
        current_app.logger.debug("Response is {}".format(response.text))
        json = response.json()
        if response.ok is False:
            current_app.logger.error("Request error: {}".format(json))
            return None
        current_app.logger.debug("User found is: {}".format(json))
        user = UserModel()
        user.fill_from_json(json)
        return user

    @staticmethod
    def create_user(user_form: UserForm, role_id: int = 3):
        """
        This method contains the logic to create a new user
        :return:
        """
        email = user_form.email.data
        current_app.logger.debug("New user email {}".format(email))
        phone = user_form.phone.data
        current_app.logger.debug("New user phone {}".format(phone))
        password = user_form.password.data
        current_app.logger.debug("New user password {}".format(password))
        date = user_form.dateofbirth.data
        current_app.logger.debug("New user date {}".format(date))
        firstname = user_form.firstname.data
        current_app.logger.debug("New user date {}".format(firstname))
        lastname = user_form.lastname.data
        current_app.logger.debug("New user date {}".format(lastname))
        json_request = {
            "email": email,
            "phone": phone,
            "password": password,
            "dateofbirth": str(date),
            "firstname": firstname,
            "lastname": lastname,
        }
        if role_id == 3:
            url = "{}/create_user".format(USER_MICROSERVICE_URL)
        else:
            url = "{}/create_operator".format(USER_MICROSERVICE_URL)
        response = HttpUtils.make_post_request(to_url=url, args=json_request)
        if response[0] is None:
            current_app.logger.debug("An error with code {} occurs".format(response[1]))
            return False
        current_app.logger.debug("User created and the response was {}".format(response[0]))
        return True

    @staticmethod
    def modify_user(user_form: UserForm, role_id: int = None, user_id: int = None):
        """
        This method take an user that is populate from te called (e.g: the flat form)
        and make the operation to store it as persistent (e.g database).
        We can assume that by default is not possible change the password
        :param form: the user form with new data
        :param user_id: it is used only for test because the session is not available
        :param role_id: by default is none but it is possible setup to change also the role id
        :return: the user with the change if is changed
        """
        if user_id is None:
            user_id = current_user.id
        if role_id is None:
            role_id = current_user.role_id

        email = user_form.email.data
        current_app.logger.debug("New user email {}".format(email))
        phone = user_form.phone.data
        current_app.logger.debug("New user phone {}".format(phone))
        date = user_form.dateofbirth.data
        current_app.logger.debug("New user birth {}".format(date))
        firstname = user_form.firstname.data
        current_app.logger.debug("New user firstname {}".format(firstname))
        lastname = user_form.lastname.data
        current_app.logger.debug("New user lastname {}".format(lastname))
        json_request = {
            "email": email,
            "phone": phone,
            "dateofbirth": str(date),
            "firstname": firstname,
            "lastname": lastname,
            "role": role_id,
            "id": user_id,
        }
        current_app.logger.debug("Request body \n{}".format(json_request))
        url = "{}/data/".format(USER_MICROSERVICE_URL)
        response = HttpUtils.make_put_request(to_url=url, args=json_request)
        if response[0] is None:
            current_app.logger.debug("An error with code occurs {}".format(response[1]))
            return None
        json = response[0]
        current_app.logger.debug("Response: ".format(json))
        user = UserModel()
        user.fill_from_json(json)
        return user

    @staticmethod
    def delete_user(user_id: int = None):
        user = UserService.get_user_by_id(user_id=user_id)
        if user is None:
            return False
        with current_app.test_request_context():
            if user.role_id == 2 and "RESTAURANT_ID" in session:
                restaurant_id = session["RESTAURANT_ID"]
                response = RestaurantServices.delete_restaurant(restaurant_id=restaurant_id)
                if response is False:
                    current_app.logger.debug("Impossible delete restaurant")
                    return False
        url = "{}/delete/{}".format(USER_MICROSERVICE_URL, str(user_id))
        response = HttpUtils.make_delete_request(url)
        if response is not None:
            return True
        else:
            return False

    @staticmethod
    def is_positive(user_id: int):
        """
        Given a userid i return if the user is currently positive
        :param user_id: user id of the user checked
        return: boolean if the user is positive
        """
        user = UserService.get_user_by_id(user_id=user_id)
        if user is not None:
            return user.is_positive
        return False

    @staticmethod
    def get_customer_reservation(fromDate: str, toDate: str, customer_id: str):
        current_app.logger.debug(
            "Filtering by: {}".format([fromDate, toDate, customer_id])
        )

        # bind filter params...
        url = "{}?user_id={}".format(BOOKING_MICROSERVICE_URL, customer_id)
        if fromDate:
            url = HttpUtils.append_query(url, "fromDate", fromDate)
        if toDate:
            url = HttpUtils.append_query(url, "toDate", toDate)

        response = HttpUtils.make_get_request(url)
        return response

    @staticmethod
    def user_login(form: LoginForm):
        """
        TODO implement it
        This method contains the logic to perform the request to microservices and
        receive the answer
        :return the object user or None
        """
        pass

    @staticmethod
    def get_user_by_email(email):
        try:
            url = "{}/email".format(USER_MICROSERVICE_URL, email)
            current_app.logger.debug("Url is: {}".format(url))
            response = requests.post(url, json={"email": email})
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return None
        if not response.ok:
            current_app.logger.error(
                "Microservice response is: {}".format(response.text)
            )
            return None
        user = UserModel()
        current_app.logger.debug("Microservice response is: {}".format(response.json()))
        user.fill_from_json(response.json())
        return user

    @staticmethod
    def mark_positive(email: str = None, phone: str = None):
        """
        This method perform the request to user microservices to make the user positive
        """
        current_app.logger.debug(
            "Asking to mark. Called with: {} , {}".format(email, phone)
        )
        if email is not None and len(email) != 0:
            current_app.logger.debug(
                "marking with email because email len: {}".format(len(email))
            )
            key = "email"
            value = email
        elif phone is not None and len(phone) != 0:
            current_app.logger.debug(
                "marking with phone because phone len: {}".format(len(phone))
            )
            key = "phone"
            value = phone
        else:
            return None
        url = "{}/mark/{}/{}".format(USER_MICROSERVICE_URL, key, value)
        return HttpUtils.make_get_request(url)

    @staticmethod
    def unmark_positive(email: str = None, phone: str = None):
        """
        This method perform the request to user microservices to make the user positive
        """
        if email is None and phone is None:
            return "Insert an email or a phone number"

        if email is not None and len(email) != 0:
            body = {"key": "email", "value": email}
        else:
            body = {"key": "phone", "value": phone}

        url = USER_MICROSERVICE_URL + "/unmark"
        response = HttpUtils.make_put_request(url, body)
        return response

    @staticmethod
    def get_list_of_positive_user():
        """
        This method perform the request to get all positive user inside the database
        """
        url = "{}/report_positive".format(USER_MICROSERVICE_URL)
        response = HttpUtils.make_get_request(url)
        if response is None or len(response) == 0:
            return []
        users = response["users"]
        list_user = []
        for user in users:
            new_user = UserModel()
            new_user.fill_from_json(user)
            list_user.append(new_user)
        return list_user

    @staticmethod
    def get_count_of_positive_user():
        """
        This method perform the request to get all positive user inside the database
        """
        url = "{}/report_positive".format(USER_MICROSERVICE_URL)
        response = HttpUtils.make_get_request(url)
        if response is None or len(response) == 0:
            return []
        users = response["users"]
        return len(users)

    @staticmethod
    def search_possible_contacts(email: str = None, phone: str = None):
        """
        Search all possible contact for the user with email of phone
        """
        if email is not None and len(email) != 0:
            url = USER_MICROSERVICE_URL + "/positiveinfo/email/" + str(email)
        elif phone is not None and len(phone) != 0:
            url = USER_MICROSERVICE_URL + "/positiveinfo/phone/" + str(phone)
        else:
            return None
        # check if the user exists (ON VIEW)
        # check if the user is positive (get also date of marking) (API) ????
        return HttpUtils.make_get_request(url)

    @staticmethod
    def get_user_by_id(user_id):
        """"""
        user = "{}/{}".format(USER_MICROSERVICE_URL, user_id)
        response = HttpUtils.make_get_request(user)
        if response is None:
            return None
        user_model = UserModel()
        user_model.fill_from_json(response)
        return user_model
