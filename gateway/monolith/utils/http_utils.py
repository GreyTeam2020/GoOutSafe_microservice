import logging
import requests


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
            logging.debug("Url is: {}".format(to_url))
            response = requests.get(to_url)
            logging.debug("Header Request: {}".format(response.request.headers))
            logging.debug("Body Request: {}".format(response.request.body))
        except requests.exceptions.ConnectionError as ex:
            logging.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return None

        if not response.ok:
            logging.error("Error from microservice")
            logging.error("Error received {}".format(response.reason))
            return None
        json = response.json()
        logging.debug("Response is: ".format(json))
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
            logging.debug("Url is: {}".format(to_url))
            logging.debug("Body request is: {}".format(args))
            response = requests.post(url=to_url, json=args)
            logging.debug("Header Request: {}".format(response.request.headers))
            logging.debug("Body Request: {}".format(response.request.body))
        except requests.exceptions.ConnectionError as ex:
            logging.error(
                "Error during the microservice call {}".format(str(ex))
            )
            return None

        if not response.ok:
            logging.error("Error from microservice")
            logging.error("Error received {}".format(response.reason))
            return None
        json = response.json()
        logging.debug("Response is: ".format(json))
        return json