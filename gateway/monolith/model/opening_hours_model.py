
class OpeningHoursModel:

    def fill_from_json(self, json_obj):
        self.id = json_obj["id"]
        self.close_dinner = json_obj["close_dinner"]
        self.close_lunch = json_obj["close_lunch"]
        self.open_dinner = json_obj["open_dinner"]
        self.open_lunch = json_obj["open_lunch"]
        self.restaurant_id = json_obj["restaurant_id"]
        self.week_day = json_obj["week_day"]
