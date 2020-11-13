import json

from werkzeug.security import check_password_hash


class UserModel:
    def __init__(
        self,
        id,
        email,
        phone,
        firstname,
        lastname,
        password,
        dateofbirth,
        role_id,
        is_active=True,
        is_admin=False,
        is_anonymous=False,
    ):
        self.id = id
        self.email = email
        self.phone = phone
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.dateofbirth = dateofbirth
        self.is_active = is_active
        self.is_admin = is_admin
        self.role_id = role_id
        self.is_anonymous = is_anonymous
        self._authenticated = False

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authenticated = checked
        return self._authenticated

    def get_id(self):
        return self.id

    def serialize(self):
        return dict([(k, v) for k, v in self.__dict__.items() if k[0] != "_"])

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
