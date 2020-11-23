from monolith.app_constant import BOOKING_MICROSERVICE_URL
from monolith.utils import HttpUtils


class BookingServices:
    @staticmethod
    def book(restaurant_id, current_user, py_datetime, people_number, raw_friends):
        json = {
            "restaurant_id": int(restaurant_id),
            "user_id": int(current_user.id),
            "datetime": py_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "people_number": people_number,
            "raw_friends": raw_friends,
        }
        response, code = HttpUtils.make_post_request(BOOKING_MICROSERVICE_URL, json)
        return response

    @staticmethod
    def delete_book(reservation_id: str, customer_id: str):
        response = HttpUtils.make_delete_request(
            "{}/{}?user_id={}".format(
                BOOKING_MICROSERVICE_URL, reservation_id, customer_id
            )
        )
        return response

    @staticmethod
    def update_book(
        reservation_id: str,
        restaurant_id,
        user_id,
        py_datetime,
        people_number,
        raw_friends="",
    ):
        json = {
            "restaurant_id": restaurant_id,
            "user_id": user_id,
            "datetime": py_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "people_number": people_number,
            "raw_friends": raw_friends,
        }
        response, code = HttpUtils.make_put_request(
            "{}/{}".format(BOOKING_MICROSERVICE_URL, reservation_id), json
        )
        return response

    @staticmethod
    def get_single_booking(reservation_id):
        response = HttpUtils.make_get_request(
            "{}/{}".format(BOOKING_MICROSERVICE_URL, reservation_id)
        )

        return response

    @staticmethod
    def get_all_booking():
        response = HttpUtils.make_get_request(BOOKING_MICROSERVICE_URL)

        return response
