class PhotoModel:
    def fill_from_json(self, json_obj):
        self.id = json_obj["id"]
        self.caption = json_obj["caption"]
        self.url = json_obj["url"]
        self.restaurant_id = json_obj["restaurant_id"]
