class TableModel:
    """
    This is the class model about the restaurant table db concept
    """

    def fill_from_json(self, json_obj):
        """
        This method fill the model with a json obj
        """
        self.id = json_obj["id"]
        self.name = json_obj["name"]
        self.max_seats = json_obj["max_seats"]
        self.restaurant_id = json_obj["restaurant_id"]
        self.available = json_obj["available"]

    def serialize(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != "_"])
