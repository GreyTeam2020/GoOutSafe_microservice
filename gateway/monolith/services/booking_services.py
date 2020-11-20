import datetime
from sqlalchemy import or_

from monolith.database import (
    db,
    RestaurantTable,
    Reservation,
    Restaurant,
    OpeningHours,
    Positive,
    Friend,
)
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
            "raw_friends": raw_friends
        }
        response, code = HttpUtils.make_post_request(BOOKING_MICROSERVICE_URL, json)
        return response

    @staticmethod
    def delete_book(reservation_id: str, customer_id: str):
        response, code = HttpUtils.make_delete_request("{}/{}?user_id={}".format(BOOKING_MICROSERVICE_URL, reservation_id, customer_id))

        return response

    @staticmethod
    def update_book(
        reservation_id, current_user, py_datetime, people_number, raw_friends
    ):

        reservation = (
            db.session.query(Reservation)
            .filter_by(id=reservation_id)
            .filter_by(customer_id=current_user.id)
            .first()
        )
        if reservation is None:
            print("Reservation not found")
            return False, "Reservation not found"

        table = (
            db.session.query(RestaurantTable).filter_by(id=reservation.table_id).first()
        )

        if table is None:
            print("Table not found")
            return False, "Table not found"

        book = BookingServices.book(
            table.restaurant_id, current_user, py_datetime, people_number, raw_friends
        )
        if book[0] is not None:
            BookingServices.delete_book(reservation_id, current_user.id)
        return book
