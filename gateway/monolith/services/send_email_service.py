import requests
from flask import current_app
from monolith.app_constant import EMAIL_MICROSERVICE_URL
from monolith.utils.http_utils import HttpUtils


class SendEmailService:
    """
    This method contains all the logic to
    send the email with send email microservices
    """

    @staticmethod
    def confirm_registration(email: str, name: str) -> bool:
        """
        :param email: Email of the new user
        :param name: Name of the new user
        """
        current_app.logger.debug("Email to send the email: {}".format(email))
        current_app.logger.debug("Name of the user {}".format(name))
        json = {"email": email, "name": name}
        current_app.logger.debug("JSON request {}".format(json))
        url = "{}/confirm_registration".format(EMAIL_MICROSERVICE_URL)
        current_app.logger.debug("URL to microservices sendemail {}".format(url))
        response = requests.post(url=url, json=json)
        json = response.json()
        if response.ok is False:
            current_app.logger.error(
                "Error during the request: {}".format(response.status_code)
            )
            current_app.logger.error("Error with message {}".format(json))
            return False
        return True

    @staticmethod
    def send_possible_contact(contacts: list) -> bool:
        """
        This method perform the request to send emails to possible contacts
        """
        url = EMAIL_MICROSERVICE_URL + "/send_contact"
        response = HttpUtils.make_post_request(url, contacts)
        return response is not None