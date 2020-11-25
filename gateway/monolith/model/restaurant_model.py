from monolith.model.menu_model import MenuModel
from monolith.model.dish_model import DishModel
from monolith.model.photo_model import PhotoModel
from monolith.model.opening_hours_model import OpeningHoursModel


class RestaurantModel:
    """
    This object contains all information necessary to work with restaurant
    """

    def __init__(self) -> None:
        self.photos = []
        self.dishes = []
        self.opening_hours = []
        self.cusine = []

    def bind_menu(self, db_object):
        """
        This method bind the object from the db to RestaurantModel
        :param db_object: instance of Menu object from database
        """
        for cuisine in db_object:
            model = MenuModel()
            model.fill_from_json(cuisine)
            self.cusine.append(model)

    def bind_photo(self, db_obj):
        """
        This method bind the object from the database to RestaurantModel
        :param db_obj: instance of Menu object from database
        """
        for photo in db_obj:
            model = PhotoModel()
            model.fill_from_json(photo)
            self.photos.append(model)

    def bind_dish(self, db_obj):
        """
        This method bind the information inside the object
        :param db_obj: instance of MenuDish object from database
        """
        for dish in db_obj:
            model = DishModel()
            model.fill_from_json(dish)
            self.dishes.append(model)

    def bind_hours(self, obj):
        """
        This method bind the information inside the object
        :param obj: instance of OpeningHours object from database
        :return:
        """
        for hour in obj:
            model = OpeningHoursModel()
            model.fill_from_json(hour)
            self.opening_hours.append(model)

    def fill_from_json(self, only_rest):
        """
        This method parser the json and make the model available
        this parser only the information related to restaurants
        """
        if "id" in only_rest:
            self.id = only_rest["id"]
        self.name = only_rest["name"]
        self.phone = only_rest["phone"]
        self.owner_email = only_rest["owner_email"]
        self.lon = only_rest["lon"]
        self.lat = only_rest["lat"]
        self.covid_measures = only_rest["covid_measures"]
        self.rating = only_rest["rating"]
        self.avg_time = only_rest["avg_time"]


    def serialize(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != "_"])
