import json
from datetime import datetime

from werkzeug.security import check_password_hash


class UserModel:
    def __init__(self):
        self.is_anonymous = False
        self._authenticated = False
        self.is_active = True
        self.is_admin = False

    def fill_from_json(self, json_obj):
        """
        This method bind the object json that contains the user information.
        """
        if "id" in json_obj:
            self.id = json_obj["id"]
        self.email = json_obj["email"]
        self.phone = json_obj["phone"]
        self.firstname = json_obj["firstname"]
        self.lastname = json_obj["lastname"]
        # TODO: sistemare questa brutta roba
        if isinstance(json_obj["dateofbirth"], str):
            self.dateofbirth = datetime.strptime(
                json_obj["dateofbirth"], "%Y-%m-%dT%H:%M:%SZ"
            )
        else:
            self.dateofbirth = json_obj["dateofbirth"]
        self.role_id = json_obj["role_id"]

    @property
    def is_authenticated(self):
        return self._authenticated

    def set_authenticated(self, authenticated):
        self._authenticated = authenticated

    def get_id(self):
        return self.id

    def serialize(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != "_"])

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
