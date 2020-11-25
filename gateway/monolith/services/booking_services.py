from monolith.app_constant import BOOKING_MICROSERVICE_URL
from monolith.utils import HttpUtils


class BookingServices:
    @staticmethod
    def book(
        restaurant_id,
        current_user,
        py_datetime,
        people_number,
        raw_friends,
        is_debug: bool = False,
    ):
        json = {
            "restaurant_id": int(restaurant_id),
            "user_id": int(current_user.id),
            "datetime": py_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "people_number": people_number,
            "raw_friends": raw_friends,
        }
        if is_debug is True:
            json["is_debug"] = True
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

    @staticmethod
    def get_reservation_by_constraint(
        user_id: int = None, from_data=None, to_data=None, restaurant_id: int = None
    ):
        """"""
        url = BOOKING_MICROSERVICE_URL
        # add filters...
        if from_data:
            url = HttpUtils.append_query(
                url, "fromDate", from_data.strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        if to_data:
            url = HttpUtils.append_query(
                url, "toDate", to_data.strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        if user_id:
            url = HttpUtils.append_query(url, "user_id", user_id)
        if restaurant_id:
            url = HttpUtils.append_query(url, "restaurant_id", restaurant_id)

        response = HttpUtils.make_get_request(url)
        return response
