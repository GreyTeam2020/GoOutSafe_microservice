from monolith.database import Restaurant, Menu, PhotoGallery, MenuDish, OpeningHours


class RestaurantModel:
    """
    This object contains all information necessary to work with restaurant
    """

    def __init__(self) -> None:
        ## Array of cusine
        self.cusine = []
        # Array of PhotoGallery
        self.photos = []
        # Array of MenuDish
        self.dishes = []
        ## array of OpeningHours
        self.opening_hours = []

    def bind_restaurant(self, db_object: Restaurant):
        """
        This method contains the code to bind the db object with a model of application
        :param db_object: instance of Restaurant from database
        """
        self.name = db_object.name
        self.phone = db_object.phone
        self.lat = db_object.lat
        self.lon = db_object.lon
        self.covid_measures = db_object.covid_measures

    def bind_menu(self, db_object: Menu):
        """
        This method bind the object from the db to RestaurantModel
        :param db_object: instance of Menu object from database
        """
        self.cusine.append(db_object.cusine)

    def bind_photo(self, db_obj: PhotoGallery):
        """
        This method bind the object from the database to RestaurantModel
        :param db_obj: instance of Menu object from database
        """
        self.photos.append(db_obj)

    def bind_dish(self, db_obj: MenuDish):
        """
        This method bind the information inside the object
        :param db_obj: instance of MenuDish object from database
        """
        self.dishes.append(db_obj)

    def bind_hours(self, obj: OpeningHours):
        """
        This method bind the information inside the object
        :param obj: instance of OpeningHours object from database
        :return:
        """
        self.opening_hours.append(obj)
