from datetime import datetime
from decimal import Decimal

from flask import current_app
from flask_login import current_user

from monolith.database import (
    Restaurant,
    OpeningHours,
    RestaurantTable,
    Review,
    Reservation,
)
from monolith.forms import RestaurantForm
from monolith.database import db
from sqlalchemy.sql.expression import func, extract
from monolith.model.restaurant_model import RestaurantModel
from monolith.app_constant import RESTAURANTS_MICROSERVICE_URL
from monolith.utils.http_utils import HttpUtils

from monolith.model.review_model import ReviewModel


class RestaurantServices:
    """
    This services give the possibility to isolate all the operations
    about the restaurants with the database
    """

    @staticmethod
    def create_new_restaurant(form: RestaurantForm, user_id: int, max_sit: int):
        """
        This method contains all logic save inside the a new restaurant
        :return:
        """
        json_body = {}
        # Menu on restaurants microservices is the cuisine type on the form
        # avg_time is the the how much time the people stay inside the restaurants
        name_rest = form.name.data
        current_app.logger.debug("New rest name is {}".format(name_rest))
        phone_rest = int(form.phone.data)
        current_app.logger.debug("Phone is: {}".format(phone_rest))
        covid_measures = form.covid_measures.data
        current_app.logger.debug("Covid Measures is: {}".format(covid_measures))
        owner_email = current_user.email
        current_app.logger.debug("owner_email is {}".format(owner_email))
        lat_rest = float(form.lat.data)
        lon_rest = float(form.lon.data)
        current_app.logger.debug("Restaurant position is lat={} lon={}".format(lat_rest, lon_rest))
        restaurant_json = {
            "name": name_rest,
            "covid_measures": covid_measures,
            "owner_email": current_user.email,
            "phone": phone_rest,
            "lat": lat_rest,
            "lon": lon_rest,
            "rating": 0,
            "avg_time": 0
        }
        current_app.logger.debug("Restaurants obj is {}".format(restaurant_json))
        json_body["restaurant"] = restaurant_json
        n_table_rest = int(form.n_tables.data)
        current_app.logger.debug("N tables is: {}".format(n_table_rest))
        json_body["restaurant_tables"] = n_table_rest
        opening_json = []

        days = form.open_days.data
        for i in range(len(days)):
            day_json = {}
            week_day = int(days[i])
            current_app.logger.debug("Week day is {}".format(week_day))
            close_dinner = str(form.close_dinner.data)
            current_app.logger.debug("Close dinner {}".format(close_dinner))
            close_lunch = str(form.close_lunch.data)
            current_app.logger.debug("Close lunch  {}".format(close_lunch))
            close_lunch = str(form.close_lunch.data)
            current_app.logger.debug("Close lunch  {}".format(close_lunch))
            open_dinner = str(form.open_dinner.data)
            current_app.logger.debug("Open dinner {}".format(open_dinner))
            open_lunch = str(form.open_lunch.data)
            current_app.logger.debug("Open lunch {}".format(open_lunch))
            day_json["close_dinner"] = close_dinner
            day_json["close_lunch"] = close_lunch
            day_json["open_dinner"] = open_dinner
            day_json["open_lunch"] = open_lunch
            day_json["week_day"] = week_day
            opening_json.append(day_json)
        current_app.logger.debug("Opening day list \n{}".format(opening_json))
        json_body["opening"] = opening_json

        cuisine_type = form.cuisine.data
        current_app.logger.debug("cuisine_type list is \n{}".format(cuisine_type))
        json_body["menu"] = cuisine_type

        url = "{}/create".format(RESTAURANTS_MICROSERVICE_URL)
        current_app.logger.debug("URL is: {}".format(url))
        current_app.logger.debug("Request body is: {}".format(json_body))
        restaurant = HttpUtils.make_post_request(url, json_body)
        restaurant_model = RestaurantModel()
        restaurant_model.from_simple_json(restaurant)
        return restaurant_model

    @staticmethod
    def get_all_restaurants():
        """
        Method to return a list of all restaurants inside the database
        """
        url = "{}".format(RESTAURANTS_MICROSERVICE_URL)
        current_app.logger.debug("URL microservices: {}".format(url))
        response = HttpUtils.make_get_request(url)
        if response is None:
            current_app.logger.error("Microservices error")
            return []
        all_restaurants = response["restaurants"]
        return all_restaurants

    @staticmethod
    def get_rest_by_id(id: int):
        """
        This method contains the logic to get an restaurants by id
        :param id: The restaurants id
        """
        url = "{}/{}".format(RESTAURANTS_MICROSERVICE_URL, id)
        current_app.logger.debug("URL to microservices is {}".format(url))
        restaurant = HttpUtils.make_get_request(url)
        if restaurant is None:
            return None
        current_app.logger.debug(restaurant)
        restaurant_model = RestaurantModel()
        restaurant_model.from_simple_json(restaurant)
        return restaurant_model

    @staticmethod
    def get_dishes_restaurant(restaurant_id: int):
        """
        This method return the restaurants dished
        """
        url = "{}/{}/dishes".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        current_app.logger.debug("URL to microservices is {}".format(url))
        response = HttpUtils.make_get_request(url)
        if response is None:
            return None
        return response["dishes"]

    @staticmethod
    def get_menu_restaurant(restaurant_id: int):
        """
        This method help to retrieve all information inside the
        """
        url = "{}/{}/menu".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        current_app.logger.debug("URL to microservices is {}".format(url))
        response = HttpUtils.make_get_request(url)
        if response is None:
            return None
        return response["menus"]

    @staticmethod
    def get_opening_hours_restaurant(restaurant_id: int):
        """
        This method help to retreival all information inside the
        """
        url = "{}/{}/openings".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        current_app.logger.debug("URL to microservices is {}".format(url))
        response = HttpUtils.make_get_request(url)
        if response is None:
            return None
        return response["opening hours"]

    @staticmethod
    def get_photos_restaurants(restaurant_id: int):
        """
        This method retrieval all information about the restaurants photos
        """
        url = "{}/{}/photos".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        current_app.logger.debug("URL to microservices is {}".format(url))
        response = HttpUtils.make_get_request(url)
        if response is None:
            return None
        return response["Photos"]

    @staticmethod
    def get_reservation_rest(owner_id, restaurant_id, from_date, to_date, email):
        """
        This method contains the logic to find all reservation in the restaurant
        with the filter on the date
        """

        queryString = (
            "select reserv.id, reserv.reservation_date, reserv.people_number, tab.id as id_table, cust.firstname, cust.lastname, cust.email, cust.phone, reserv.checkin from reservation reserv "
            "join user cust on cust.id = reserv.customer_id "
            "join restaurant_table tab on reserv.table_id = tab.id "
            "join restaurant rest on rest.id = tab.restaurant_id "
            "where rest.owner_id = :owner_id "
            "and rest.id = :restaurant_id "
        )

        # add filters...
        if from_date:
            queryString = queryString + " and  reserv.reservation_date > :fromDate"
        if to_date:
            queryString = queryString + " and  reserv.reservation_date < :toDate"
        if email:
            queryString = queryString + " and  cust.email = :email"
        queryString = queryString + " order by reserv.reservation_date desc"

        stmt = db.text(queryString)

        # bind filter params...
        params = {"owner_id": owner_id, "restaurant_id": restaurant_id}
        if from_date:
            params["fromDate"] = from_date + " 00:00:00.000"
        if to_date:
            params["toDate"] = to_date + " 23:59:59.999"
        if email:
            params["email"] = email

        # execute and retrive results...
        result = db.engine.execute(stmt, params)
        list_reservation = result.fetchall()
        return list_reservation

    @staticmethod
    def review_restaurant(restaurant_id, reviewer_id, stars, review):
        """
        This method insert a review to the specified restaurant
        """
        if stars is None or review is None or review == "":
            return None
        if stars < 0 or stars > 5:
            return None

        json = {"stars": stars, "review": review, "reviewer_email": current_user.email}
        response = HttpUtils.make_post_request("{}/{}/reviews".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id), json)

        if response is None:
            return None

        review = ReviewModel()
        # TODO: qui mi serve la nuova review nella response, perchè altrimenti non ho dati che mi servono,
        # TODO: per adesso li invento
        json["id"] = 1
        json["data"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        json["restaurant_id"] = restaurant_id
        # TODO: fine dati inventati
        review.fill_from_json(json)
        return review

    @staticmethod
    def get_three_reviews(restaurant_id):
        """
        Given the restaurant_di return three random reviews
        """
        response = HttpUtils.make_get_request("{}/{}/reviews/3".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id))

        if response is None:
            return []

        review_list = []
        for json in response["Reviews"]:
            review = ReviewModel()
            review.fill_from_json(json)
            review_list.append(review)
        return review_list

    @staticmethod
    def get_restaurant_name(restaurant_id):
        """
        Given the id return the name of the restaurant
        """
        response = HttpUtils.make_get_request("{}/{}/name".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id))
        if response is None:
            return ""

        return response["result"]

    @staticmethod
    def get_restaurants_by_keyword(name: str = None):
        """
        This method contains the logic to perform the search restaurant by keywords
        The keywords supported are:
        https://stackoverflow.com/questions/3325467/sqlalchemy-equivalent-to-sql-like-statement
        :param name: is the name of restaurants
        """
        if name is None:
            raise Exception("Name is required to make this type of research")
        response = HttpUtils.make_get_request("{}/search/{}".format(RESTAURANTS_MICROSERVICE_URL, name))

        rest_list = []
        for json in response["restaurants"]:
            rest = RestaurantModel()
            rest.from_simple_json(json)
            rest_list.append(rest)

        return rest_list

    @staticmethod
    def get_restaurant_people(restaurant_id: int):
        """
        Given the id of the restaurant return the number of people at lunch and dinner
        """
        openings = (
            db.session.query(OpeningHours)
            .filter(
                OpeningHours.week_day == datetime.today().weekday(),
                OpeningHours.restaurant_id == restaurant_id,
            )
            .first()
        )
        if openings is None:
            return [0, 0, 0]

        tables = (
            db.session.query(RestaurantTable)
            .filter_by(restaurant_id=restaurant_id)
            .all()
        )
        tables_id = []
        for table in tables:
            tables_id.append(table.id)

        reservations_l = (
            db.session.query(Reservation)
            .filter(
                Reservation.table_id.in_(tables_id),
                extract("day", Reservation.reservation_date)
                == extract("day", datetime.today()),
                extract("month", Reservation.reservation_date)
                == extract("month", datetime.today()),
                extract("year", Reservation.reservation_date)
                == extract("year", datetime.today()),
                extract("hour", Reservation.reservation_date)
                >= extract("hour", openings.open_lunch),
                extract("hour", Reservation.reservation_date)
                <= extract("hour", openings.close_lunch),
            )
            .all()
        )

        reservations_d = (
            db.session.query(Reservation)
            .filter(
                Reservation.table_id.in_(tables_id),
                extract("day", Reservation.reservation_date)
                == extract("day", datetime.today()),
                extract("month", Reservation.reservation_date)
                == extract("month", datetime.today()),
                extract("year", Reservation.reservation_date)
                == extract("year", datetime.today()),
                extract("hour", Reservation.reservation_date)
                >= extract("hour", openings.open_dinner),
                extract("hour", Reservation.reservation_date)
                <= extract("hour", openings.close_dinner),
            )
            .all()
        )

        reservations_now = (
            db.session.query(Reservation)
            .filter(
                Reservation.checkin is True,
                Reservation.reservation_date <= datetime.now(),
                Reservation.reservation_end >= datetime.now(),
            )
            .all()
        )

        return [len(reservations_l), len(reservations_d), len(reservations_now)]

    @staticmethod
    def checkin_reservations(reservation_id: int):
        reservation = db.session.query(Reservation).filter_by(id=reservation_id)
        if reservation:
            reservation.update({Reservation.checkin: True})
            db.session.commit()
            db.session.flush()

    @staticmethod
    def get_all_restaurants_info(restaurant_id: int):
        """
        This method contains the logic to get all informations about the restaurants.
        :return: RestaurantsModel
        """
        model = RestaurantServices.get_rest_by_id(restaurant_id)
        if model is None:
            return None

        cuisine = RestaurantServices.get_menu_restaurant(restaurant_id)
        if cuisine is None:
            return None
        model.bind_menu(cuisine)

        photos = RestaurantServices.get_photos_restaurants(restaurant_id)
        if photos is None:
            return None
        model.bind_photo(photos)

        dishes = RestaurantServices.get_dishes_restaurant(restaurant_id)
        if dishes is None:
            return None
        model.bind_dish(dishes)

        q_hours = RestaurantServices.get_opening_hours_restaurant(restaurant_id)
        if q_hours is None:
            return None
        model.bind_hours(q_hours)

        return model

    @staticmethod
    def get_rating_restaurant(restaurant_id: int) -> float:
        """
        TODO(vincenzopalazzo) this function need more testing.
        This method perform the request to calculate the rating of the restaurants
        with the review.
        :param restaurant_id: the restaurant id
        :return: the rating value, as 0.0 or 5.0
        """
        rating_value = 0.0
        restaurant = db.session.query(Restaurant).filter_by(id=restaurant_id).first()
        if restaurant is None:
            raise Exception(
                "Restaurant with id {} don't exist on database".format(restaurant_id)
            )
        reviews_list = (
            db.session.query(Review).filter_by(restaurant_id=restaurant_id).all()
        )
        if (reviews_list is None) or (len(reviews_list) == 0):
            return rating_value

        for review in reviews_list:
            rating_value = rating_value + float(review.stars)

        rating_value = rating_value / float(len(reviews_list))
        current_app.logger.debug(
            "Rating calculate for restaurant with name {} is {}".format(
                restaurant.name, rating_value
            )
        )
        restaurant.rating = Decimal(rating_value)
        db.session.commit()
        return rating_value

    @staticmethod
    def calculate_rating_for_all():
        """
        This method is used inside celery background task to calculate the rating for each restaurants
        """
        restaurants_list = db.session.query(Restaurant).all()
        for restaurant in restaurants_list:
            RestaurantServices.get_rating_restaurant(restaurant.id)
