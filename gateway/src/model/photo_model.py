class PhotoModel:
    """
    This is the class model about the photo db concept
    """

    def fill_from_json(self, json_obj):
        self.id = json_obj["id"]
        self.caption = json_obj["caption"]
        self.url = json_obj["url"]
        self.restaurant_id = json_obj["restaurant_id"]

    def serialize(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != "_"])
