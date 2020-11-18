from datetime import datetime


class OpeningHoursModel:

    def fill_from_json(self, json_obj):
        if "id" in json_obj:
            self.id = json_obj["id"]
        self.close_dinner = datetime.strptime(json_obj["close_dinner"], "%H:%M")
        self.close_lunch = datetime.strptime(json_obj["close_lunch"], "%H:%M")
        self.open_dinner = datetime.strptime(json_obj["open_dinner"], "%H:%M")
        self.open_lunch = datetime.strptime(json_obj["open_lunch"], "%H:%M")
        self.restaurant_id = json_obj["restaurant_id"]
        self.week_day = json_obj["week_day"]
