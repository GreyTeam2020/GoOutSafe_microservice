from monolith.app_constant import *

_CELERY = False


class DispatcherMessage:
    """
    TODO REMOVE IT
    This class using a mediator patter to decide if the status of app admit
    the celery message.
    The celery message are available for the moment only in release and in some debug cases
    otherwise it is disabled.

    For instance, for the testing it is disabled.

    @author Vincenzo Palazzo v.palazzo1@studenti.unipi.it
    """

    @staticmethod
    def send_message(type_message: str, params):
        """
        This static method take and string that usually is defined inside the
        file app_constant.py and check if there is condition to dispatc the test
        :return: nothings
        """
        return