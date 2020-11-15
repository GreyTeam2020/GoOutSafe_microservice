import json

from werkzeug.security import check_password_hash


class UserModel:
    def __init__(self):
        self.is_anonymous = False
        self._authenticated = False
        self.is_active = True
        self.is_admin = False

    @classmethod
    def fill_from_json(cls, json_obj):
        """
        This method bind the object json that contains the user information.
        """
        if "id" in json_obj:
            cls.id = json_obj["id"]
        cls.email = json_obj["email"]
        cls.phone = json_obj["phone"]
        cls.firstname = json_obj["firstname"]
        cls.lastname = json_obj["lastname"]
        cls.dateofbirth = json_obj["dateofbirth"]
        cls.role_id = json_obj["role_id"]

    @property
    def is_authenticated(self):
        return self._authenticated

    @classmethod
    def set_authenticated(cls, authenticated):
        cls._authenticated = authenticated

    def get_id(self):
        return self.id

    def serialize(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != "_"])

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
