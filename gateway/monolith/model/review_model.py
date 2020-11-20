from datetime import datetime


class ReviewModel:
    def fill_from_json(self, json_obj):
        self.id = json_obj["id"]
        self.stars = json_obj["stars"]
        self.review = json_obj["review"]
        self.date = datetime.strptime(json_obj["data"], "%m/%d/%Y, %H:%M:%S")
        self.reviewer_email = json_obj["reviewer_email"]
        self.restaurant_id = json_obj["restaurant_id"]
