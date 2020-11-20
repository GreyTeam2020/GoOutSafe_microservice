import os
from datetime import datetime
from random import randrange

import pytest
from monolith.database import db, User, Reservation
from monolith.forms import UserForm
from monolith.services.user_service import UserService
from monolith.tests.utils import get_user_with_email, login


class Test_UserServices:
    """
    This test suite test the services about user use case.
    All the code tested inside this class is inside the services/test_user_services.py
    """

    def test_create_get_and_delete_user(self):
        """
        test create user
        :return:
        """
        form = UserForm()
        form.firstname.data = "user_{}".format(randrange(100000))
        form.lastname.data = "user_{}".format(randrange(10000))
        form.password.data = "pass_{}".format(randrange(10000))
        form.phone.data = "12345{}".format(randrange(10000))
        form.dateofbirth.data = "1995-12-12"
        form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        result = UserService.create_user(form)
        assert result is True

        user_and_code = UserService.login_user(form.email.data, form.password.data)
        user = user_and_code[0]
        status_code = user_and_code[1]
        assert user.firstname == form.firstname.data
        assert user.id is not None
        assert status_code < 300

        result_delete = UserService.delete_user(user.id)
        assert result_delete is True

    def test_create_customer(self):
        """
        test create user
        :return:
        """
        form = UserForm()
        form.firstname.data = "user_{}".format(randrange(10000))
        form.lastname.data = "user_{}".format(randrange(10000))
        form.password.data = "pass_{}".format(randrange(10000))
        form.phone.data = "12345{}".format(randrange(10000))
        form.dateofbirth.data = "1995-12-12"
        form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        result = UserService.create_user(form, 2)
        assert result is True
        assert result < 300

        user_and_code = UserService.login_user(form.email.data, form.password.data)
        user = user_and_code[0]
        status_code = user_and_code[1]
        assert user.firstname == form.firstname.data
        assert user.id is not None
        assert status_code < 300

        result_delete = UserService.delete_user(user.id)
        assert result_delete is True

    def test_modify_user_role_id(self, client):
        """
        With this code is tested the services to perform the user modification
        with service and have the result on db

        Test flow
        - Create user
        - Modify user
        - check user
        - delete user to clean the database
        """
        form = UserForm()
        form.firstname.data = "user_{}".format(randrange(10000))
        form.lastname.data = "user_{}".format(randrange(10000))
        form.password.data = "pass_{}".format(randrange(10000))
        form.phone.data = "12345{}".format(randrange(10000))
        form.dateofbirth.data = "1995-12-12"
        form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        result = UserService.create_user(form, 2)
        assert result is True
        assert result < 300

        user_and_code = UserService.login_user(form.email.data, form.password.data)
        user = user_and_code[0]
        status_code = user_and_code[1]
        assert user.firstname == form.firstname.data
        assert user.id is not None
        assert status_code < 300

        form.firstname.data = "Alibaba"
        user_modified = UserService.modify_user(form, 3, user.id)
        assert user_modified is not None
        assert user_modified.role_id != 2

        result_delete = UserService.delete_user(user_modified.id)
        assert result_delete is True

    def test_delete_user_with_email(self):
        """
        This test cases test if the user service are able to
        remove correctly the user inside the DB
        Test flow
        - Create a new user with the service
        - delete a new user with service with user pass
        - check on db if this user is gone
        """

        form = UserForm()
        form.firstname.data = "user_{}".format(randrange(10000))
        form.lastname.data = "user_{}".format(randrange(10000))
        form.password.data = "pass_{}".format(randrange(10000))
        form.phone.data = "12345{}".format(randrange(10000))
        form.dateofbirth.data = "1995-12-12"
        form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        result = UserService.create_user(form, 2)
        assert result is True
        assert result < 300

        user_and_code = UserService.login_user(form.email.data, form.password.data)
        user = user_and_code[0]
        status_code = user_and_code[1]
        assert user.firstname == form.firstname.data
        assert user.id is not None
        assert status_code < 300

        result_delete = UserService.delete_user(email=user.email)
        assert result_delete is True

    def test_delete_user_with_id(self):
        """
        This test cases test if the user service are able to
        remove correctly the user inside the DB
        Test flow
        - Create a new user with the service
        - delete a new user with service with user id
        - check on db if this user is gone
        """

        form = UserForm()
        form.firstname.data = "user_{}".format(randrange(10000))
        form.lastname.data = "user_{}".format(randrange(10000))
        form.password.data = "pass_{}".format(randrange(10000))
        form.phone.data = "12345{}".format(randrange(10000))
        form.dateofbirth.data = "1995-12-12"
        form.email.data = "alibaba{}@alibaba.com".format(randrange(10000))
        result = UserService.create_user(form, 2)
        assert result is True
        assert result < 300

        user_and_code = UserService.login_user(form.email.data, form.password.data)
        user = user_and_code[0]
        status_code = user_and_code[1]
        assert user.firstname == form.firstname.data
        assert user.id is not None
        assert status_code < 300

        result_delete = UserService.delete_user(user.id)
        assert result_delete is True
