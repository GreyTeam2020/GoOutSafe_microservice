
class MenuModel:

    def fill_from_json(self, json_obj):
        self.id = json_obj["id"]
        self.cuisine = json_obj["cuisine"]
        self.description = json_obj["description"]
        self.restaurant_id = json_obj["restaurant_id"]
        ## TODO ignoring the photos for the moment