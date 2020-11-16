import requests
from flask import session, current_app
from flask_login import current_user, login_user

from monolith.database import db, Positive
from monolith.forms import UserForm, LoginForm
from monolith.app_constant import USER_MICROSERVICE_URL
from monolith.model import UserModel


class UserService:
    """
    This service is a wrapper of all operation with user
    - create a new user
    - deleter a user if exist
    """

    @staticmethod
    def log_in_user(user):
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
            # and set the session like
            """
            session["RESTAURANT_ID"] = restaurant.id
            session["RESTAURANT_NAME"] = restaurant.name
            """
            pass
        return True

    @staticmethod
    def get_user_role(role_id: int):
        """
        This method return the user role with id
        :param user_id:
        :return: role value of the user
        """
        try:
            url = "{}/role/{}".format(USER_MICROSERVICE_URL, str(role_id))
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
            url = "{}/user_by_email".format(USER_MICROSERVICE_URL)
            json = {}
            if email is not None:
                json["email"] = email
            else:
                json["phone"] = phone
            current_app.logger.debug("Url is {}".format(url))
            response = requests.post(url=url, json=json)
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return None
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
        try:
            if role_id == 3:
                url = "{}/create_user".format(USER_MICROSERVICE_URL)
            else:
                url = "{}/create_operator".format(USER_MICROSERVICE_URL)
            current_app.logger.debug("Url is: {}".format(url))
            response = requests.post(url, json=json_request)
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return False
        if not response.ok:
            json = response.json()
            current_app.logger.error("Error from USER microservice")
            current_app.logger.error("Error received {}".format(response.reason))
            current_app.logger.error("Error response received {}".format(json))
            return False
        return True

    @staticmethod
    def modify_user(user_form: UserForm, role_id: int = None):
        """
        This method take an user that is populate from te called (e.g: the flat form)
        and make the operation to store it as persistent (e.g database).
        We can assume that by default is not possible change the password
        :param form: the user form with new data
        :param role_id: by default is none but it is possible setup to change also the role id
        :return: the user with the change if is changed
        """
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
            "id": current_user.id,
        }
        current_app.logger.debug("Request body \n{}".format(json_request))
        try:
            url = "{}/data".format(USER_MICROSERVICE_URL)
            current_app.logger.debug("Url is: {}".format(url))
            response = requests.put(url, json=json_request)
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return False
        current_app.logger.debug(
            "Response: ".format(str(response.text))
        )
        json = response.json()
        if not response.ok:
            current_app.logger.error("Error from USER microservice")
            current_app.logger.error("Error received {}".format(response.reason))
            current_app.logger.error("Error response received {}".format(json))
            return None
        user = UserModel()
        user.fill_from_json(json)
        return user

    @staticmethod
    def delete_user(user_id: int = None, email: str = ""):
        try:
            url = "{}/delete/{}".format(USER_MICROSERVICE_URL, str(user_id))
            current_app.logger.debug("Url is: {}".format(url))
            response = requests.delete(url)
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return False
        json = response.json()
        if not response.ok:
            current_app.logger.error("Error from USER microservice")
            current_app.logger.error("Error received {}".format(response.reason))
            current_app.logger.error("Error response received {}".format(json))
            return None
        current_app.logger.debug("User deleted")
        current_app.logger.debug("Answer received: {}".format(current_app))

    @staticmethod
    def is_positive(user_id: int):
        """
        TODO implement it
        Given a userid i return if the user is currently positive
        :param user_id: user id of the user checked
        return: boolean if the user is positive
        """
        return False

    @staticmethod
    def get_customer_reservation(fromDate: str, toDate: str, customer_id: str):
        queryString = (
            "select reserv.id, reserv.reservation_date, reserv.people_number, tab.id as id_table, rest.name, rest.id as rest_id "
            "from reservation reserv "
            "join user cust on cust.id = reserv.customer_id "
            "join restaurant_table tab on reserv.table_id = tab.id "
            "join restaurant rest on rest.id = tab.restaurant_id "
            "where cust.id = :customer_id"
        )

        stmt = db.text(queryString)

        # bind filter params...
        params = {"customer_id": customer_id}
        if fromDate:
            params["fromDate"] = fromDate + " 00:00:00.000"
        if toDate:
            params["toDate"] = toDate + " 23:59:59.999"

        # execute and retrive results...
        result = db.engine.execute(stmt, params)
        reservations_as_list = result.fetchall()
        return reservations_as_list

    @staticmethod
    def user_login(form: LoginForm):
        """
        TODO implement it
        This method contains the logic to perform the request to microservices and
        receive the answer
        :return the object user or None
        """
        pass