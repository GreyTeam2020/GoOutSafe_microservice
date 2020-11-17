import requests
from flask import current_app

class HttpUtils:
    """
    This class contains all the function to make the HTTP request

    @author Vincenzo Palazzo v.palazzo1@studenti.unipi.it
    """

    @staticmethod
    def make_get_request(to_url: str):
        """
        This method contains the code to make the request
        to a url.
        :param to_url: The URL of the endpoint
        :return the json response or None if there is some error
        """
        try:
            current_app.logger.debug("Url is: {}".format(to_url))
            response = requests.get(to_url)
            current_app.logger.debug("Header Request: {}".format(response.request.headers))
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return None

        if response.ok is False:
            current_app.logger.error("Error from microservice")
            current_app.logger.error("Error received {}".format(response.reason))
            return None
        json = response.json()
        current_app.logger.debug("Response is: {}".format(json))
        return json

    @staticmethod
    def make_post_request(to_url: str, args):
        """
        This method contains the code to make the request
        to a url.
        :param to_url: The URL of the endpoint
        :param args: Python object, this object help to fill the body request
        :return the json response or None if there is some error
        """
        try:
            current_app.logger.debug("Url is: {}".format(to_url))
            current_app.logger.debug("Body request is: {}".format(args))
            response = requests.post(url=to_url, json=args)
            current_app.logger.debug("Header Request: {}".format(response.request.headers))
            current_app.logger.debug("Body Request: {}".format(response.request.body))
        except requests.exceptions.ConnectionError as ex:
            current_app.logger.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return None

        if not response.ok:
            current_app.logger.error("Error from microservice")
            current_app.logger.error("Error received {}".format(response.reason))
            return None
        json = response.json()
        current_app.logger.debug("Response is: ".format(json))
        return json