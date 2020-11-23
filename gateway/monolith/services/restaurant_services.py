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
from monolith.model.table_model import TableModel
from monolith.model.dish_model import DishModel
from monolith.app_constant import RESTAURANTS_MICROSERVICE_URL
from monolith.utils.http_utils import HttpUtils

from monolith.model.review_model import ReviewModel

from monolith.app_constant import BOOKING_MICROSERVICE_URL


class RestaurantServices:
    """
    This services give the possibility to isolate all the operations
    about the restaurants with the database
    """

    @staticmethod
    def create_new_restaurant(
        form: RestaurantForm, user_id: int, max_sit: int, user_email: str = None
    ):
        """
        This method contains all logic save inside the a new restaurant
        :return:
        """
        json_body = {}
        # Menu on restaurants microservices is the cuisine type on the form
        # avg_time is the the how much time the people stay inside the restaurants
        name_rest = form.name.data
        current_app.logger.debug("New rest name is {}".format(name_rest))
        # I'm putting this tries because form.sumbitting in the endpoint does not work
        # so I'm checking here if the field are ok
        try:
            phone_rest = int(form.phone.data)
        except:
            return None
        current_app.logger.debug("Phone is: {}".format(phone_rest))
        covid_measures = form.covid_measures.data
        current_app.logger.debug("Covid Measures is: {}".format(covid_measures))
        if user_email is not None:
            owner_email = user_email
        else:
            owner_email = current_user.email
        current_app.logger.debug("owner_email is {}".format(owner_email))
        try:
            lat_rest = float(form.lat.data)
            lon_rest = float(form.lon.data)
        except Exception as e:
            current_app.logger.error("Wrong lat/ton format\n{}".format(e))
            return None
        current_app.logger.debug(
            "Restaurant position is lat={} lon={}".format(lat_rest, lon_rest)
        )
        restaurant_json = {
            "name": name_rest,
            "covid_measures": covid_measures,
            "owner_email": owner_email,
            "phone": phone_rest,
            "lat": lat_rest,
            "lon": lon_rest,
            "rating": 0,
            "avg_time": 30,
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
        restaurant, status_code = HttpUtils.make_post_request(url, json_body)
        restaurant_model = RestaurantModel()
        restaurant_model.fill_from_json(restaurant)
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
        restaurant_model.fill_from_json(restaurant)
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
        dishes = []
        json_dishes = response["dishes"]
        for json_dish in json_dishes:
            new_dish = DishModel()
            new_dish.fill_from_json(json_dish)
            dishes.append(new_dish)

        return dishes

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
        response = HttpUtils.make_get_request(url)
        if response is None:
            return None
        return response["openings"]

    @staticmethod
    def get_restaurant_tables(restaurant_id: int):
        """
        This method retrieves all tables of a restaurant
        :param restaurant_id: id of the restaurant
        """
        url = "{}/{}/tables".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        response = HttpUtils.make_get_request(url)
        # if no tables
        if response is None:
            return []

        # otherwise pick from json all tables
        # model them into TableModel
        # and return a list of them
        all_tables = []
        for json_table in response["tables"]:
            current_app.logger.debug(
                "table {}, seats {}".format(json_table["name"], json_table["max_seats"])
            )
            new_table = TableModel()
            new_table.fill_from_json(json_table)
            all_tables.append(new_table)
        return all_tables

    @staticmethod
    def add_table(table):
        """
        This method add a table to the restaurant
        :param table: TableModel to insert
        """
        url = "{}/{}/tables".format(RESTAURANTS_MICROSERVICE_URL, table.restaurant_id)
        response = HttpUtils.make_post_request(url, table.serialize())
        if response is None:
            return None
        return True

    @staticmethod
    def delete_table(table_id):
        """
        This method remove a table from the restaurant
        :param table: table id
        """
        url = "{}/table/{}".format(RESTAURANTS_MICROSERVICE_URL, table_id)
        response = HttpUtils.make_delete_request(url)
        if response is None:
            return None
        return True


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
        return response["photos"]

    @staticmethod
    def get_reservation_rest(restaurant_id, from_date, to_date, email):
        """
        This method contains the logic to find all reservation in the restaurant
        with the filter on the date
        """

        url = "{}/list/{}".format(BOOKING_MICROSERVICE_URL, restaurant_id)
        # add filters...
        if from_date:
            url = HttpUtils.append_query(url, "fromDate", from_date)
        if to_date:
            url = HttpUtils.append_query(url, "toDate", to_date)
        if email:
            url = HttpUtils.append_query(url, "email", email)

        response = HttpUtils.make_get_request(url)
        return response

    @staticmethod
    def review_restaurant(restaurant_id, reviewer_email, stars, review):
        """
        This method insert a review to the specified restaurant
        """
        if stars is None or review is None or review == "":
            return None
        if stars < 0 or stars > 5:
            return None

        json = {"stars": stars, "review": review, "reviewer_email": reviewer_email}
        url = "{}/{}/reviews".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        current_app.logger.debug("URL to microservices: {}".format(url))
        response, code = HttpUtils.make_post_request(url, json)

        if response is None:
            return None

        review = ReviewModel()
        json["id"] = response["id"]
        json["date"] = response["date"]
        json["restaurant_id"] = restaurant_id
        review.fill_from_json(json)
        return review

    @staticmethod
    def get_three_reviews(restaurant_id):
        """
        Given the restaurant_di return three random reviews
        """
        response = HttpUtils.make_get_request(
            "{}/{}/reviews/3".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        )

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
        response = HttpUtils.make_get_request(
            "{}/{}/name".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        )
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
        response = HttpUtils.make_get_request(
            "{}/search/{}".format(RESTAURANTS_MICROSERVICE_URL, name)
        )

        rest_list = []
        for json in response["restaurants"]:
            rest = RestaurantModel()
            rest.fill_from_json(json)
            rest_list.append(rest)

        return rest_list

    @staticmethod
    def get_restaurant_people(restaurant_id: int):
        """
        Given the id of the restaurant return the number of people at lunch and dinner
        """
        response = HttpUtils.make_get_request("{}/stats/{}".format(BOOKING_MICROSERVICE_URL, restaurant_id))
        if response is None:
            return [0, 0, 0]

        return [response["lunch"], response["dinner"], response["now"]]

    @staticmethod
    def checkin_reservations(reservation_id: int):
        HttpUtils.make_get_request(
            "{}/{}/checkin".format(BOOKING_MICROSERVICE_URL, reservation_id)
        )

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
        #it's already a model
        #model.bind_dish(dishes)

        q_hours = RestaurantServices.get_opening_hours_restaurant(restaurant_id)
        if q_hours is None:
            return None
        model.bind_hours(q_hours)

        return model

    @staticmethod
    def update_restaurant(restaurant_id, name, lat, lon, anticovid_measures):
        restaurant = RestaurantServices.get_rest_by_id(restaurant_id)
        if restaurant is None:
            return None
        restaurant.name = name
        restaurant.lat = lat
        restaurant.lon = lon
        restaurant.covid_measures = anticovid_measures
        url = "{}/update".format(RESTAURANTS_MICROSERVICE_URL)
        response, status_code = HttpUtils.make_put_request(url, restaurant.serialize())
        if status_code == 200:
            return True
        return None

    @staticmethod
    def insert_dish(dish):
        """
        This method insert the dish in the system
        :param dish: DishModel of the dish
        """
        url = "{}/{}/dishes".format(RESTAURANTS_MICROSERVICE_URL, dish.restaurant_id)
        response, code =  HttpUtils.make_post_request(url, dish.serialize())
        if response is None:
            return None
        else:
            return response
    @staticmethod
    def delete_restaurant(restaurant_id: int) -> bool:
        """
        This method perform the request to microservices to delete the restaurants
        :return true or false
        """
        url = "{}/delele/{}".format(RESTAURANTS_MICROSERVICE_URL, restaurant_id)
        current_app.logger.debug("URL to microservice is {}".format(url))
        response = HttpUtils.make_put_request(url, {})
        return response is not None

    @staticmethod
    def delete_dish(dish_id):
        """
        This method delete a dish
        :param dish_id: dish id
        """
        url = "{}/menu/{}".format(RESTAURANTS_MICROSERVICE_URL, dish_id)
        response = HttpUtils.make_delete_request(url)
        return response

    @staticmethod
    def force_reload_rating_all_restaurants():
        """
        This method call the restaurants api to force the microservice to recalculate
        the rating for each restaurants
        :return if the request is ok I rill return the request, otherwise None
        """
        user = "{}//restaurants/calculate_rating_for_all_restaurant".format(
            RESTAURANTS_MICROSERVICE_URL
        )
        return HttpUtils.make_get_request(user)
