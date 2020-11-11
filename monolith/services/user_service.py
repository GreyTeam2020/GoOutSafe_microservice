from flask_login import current_user

from monolith.database import db, User, Positive, Reservation, Role
from monolith.forms import UserForm


class UserService:
    """
    This service is a wrapper of all operation with user
    - create a new user
    - deleter a user if exist
    """

    @staticmethod
    def get_user_role(user_id: int):
        """
        This method return the user role with id
        :param user_id:
        :return: role value of the user
        """
        return db.session.query(Role).filter_by(id=user_id).first()

    @staticmethod
    def user_is_present(email: str = None, phone: str = None):
        """
        This method contains the logic to search a user with the
        :param email: user email if it is present we use to filter user
        :param phone: phone number, if it is present we use to filter user
        :return: use user if exist otherwise, it is return None
        """
        if phone is not None:
            return db.session.query(User).filter_by(phone=phone).first()
        return db.session.query(User).filter_by(email=email).first()

    @staticmethod
    def create_user(new_user: User, password, role_id: int = 3):
        """

        :return:
        """
        ## By default I assume CUSTOMER
        new_user.role_id = role_id
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        q = db.session.query(User).filter(User.email == new_user.email)
        user = q.first()
        return user

    @staticmethod
    def modify_user(form: UserForm, role_id: int = None):
        """
        This method take an user that is populate from te called (e.g: the flat form)
        and make the operation to store it as persistent (e.g database).
        We can assume that by default is not possible change the password
        :param form: the user form with new data
        :param role_id: by default is none but it is possible setup to change also the role id
        :return: the user with the change if is changed
        """

        if role_id is None:
            role_id = current_user.role_id
        db.session.query(User).filter(User.email == current_user.email).update(
            {
                "email": form.email.data,
                "firstname": form.firstname.data,
                "lastname": form.lastname.data,
                "dateofbirth": form.dateofbirth.data,
                "role_id": role_id,
            }
        )
        db.session.commit()

        user = db.session.query(User).filter_by(email=form.email.data).first()
        return user

    @staticmethod
    def delete_user(user_id: int = None, email: str = ""):
        if user_id is not None:
            db.session.query(User).filter_by(id=user_id).delete()
        else:
            db.session.query(User).filter_by(email=email).delete()
        db.session.commit()

    @staticmethod
    def is_positive(user_id: int):
        """
        Given a userid i return if the user is currently positive
        :param user_id: user id of the user checked
        return: boolean if the user is positive
        """
        check = (
            db.session.query(Positive)
            .filter_by(user_id=user_id)
            .filter_by(marked=True)
            .first()
        )
        if check is None:
            return False
        return True

    @staticmethod
    def get_customer_reservation(fromDate: str, toDate: str, customer_id: str):
        queryString = (
            "select reserv.id, reserv.reservation_date, reserv.people_number, tab.id as id_table, rest.name, rest.id as rest_id "
            "from reservation reserv "
            "join user cust on cust.id = reserv.customer_id "
            "join restaurant_table tab on reserv.table_id = tab.id "
            "join restaurant rest on rest.id = tab.restaurant_id "
            "where cust.id = :customer_id"
        )

        stmt = db.text(queryString)

        # bind filter params...
        params = {"customer_id": customer_id}
        if fromDate:
            params["fromDate"] = fromDate + " 00:00:00.000"
        if toDate:
            params["toDate"] = toDate + " 23:59:59.999"

        # execute and retrive results...
        result = db.engine.execute(stmt, params)
        reservations_as_list = result.fetchall()
        return reservations_as_list
