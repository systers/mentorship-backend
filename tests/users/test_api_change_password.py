import datetime
import json
import unittest
from http import HTTPStatus
from app.api.validations.user import PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH
from app.database.models.user import UserModel
from app.database.sqlalchemy_extension import db
from app.messages import (
    PASSWORD_SUCCESSFULLY_UPDATED,
    USER_INPUTS_SPACE_IN_PASSWORD,
    AUTHORISATION_TOKEN_IS_MISSING,
    TOKEN_HAS_EXPIRED,
)
from app.utils.validation_utils import get_length_validation_error_message
from tests.base_test_case import BaseTestCase

from tests.test_data import user1
from tests.test_utils import get_test_request_header


# Testing /PUT/ Change User's Password


class TestUserChangePasswordApi(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.first_user = UserModel(
            password=user1["password"],
            name="User",
            email="user1@email.com",
            username="user_not_admin",
            terms_and_conditions_checked=True,
        )
        self.first_user.is_email_verified = True

        db.session.add(self.first_user)
        db.session.commit()

        self.current_password = user1["password"]
        self.auth_header = get_test_request_header(self.first_user.id)

    def test_change_password_to_correct_new_one(self):
        with self.client:
            new_password = "123new_password"
            expected_response = PASSWORD_SUCCESSFULLY_UPDATED
            response = self.client.put(
                "/user/change_password",
                json={
                    "current_password": self.current_password,
                    "new_password": new_password,
                },
                follow_redirects=True,
                headers=self.auth_header,
            )
            self.assertEqual(HTTPStatus.CREATED, response.status_code)
            self.assertEqual(expected_response, json.loads(response.data))

    def test_change_password_with_authentication_token_missing(self):
        with self.client:
            new_password = "123new_password"
            expected_response = AUTHORISATION_TOKEN_IS_MISSING
            response = self.client.put(
                "/user/change_password",
                json={
                    "current_password": self.current_password,
                    "new_password": new_password,
                },
                follow_redirects=True,
            )
            self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
            self.assertEqual(expected_response, json.loads(response.data))

    def test_change_password_to_empty_one(self):
        with self.client:
            new_password = ""
            expected_response = {
                "message": get_length_validation_error_message(
                    "new_password", PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH
                )
            }
            response = self.client.put(
                "/user/change_password",
                json={
                    "current_password": self.current_password,
                    "new_password": new_password,
                },
                follow_redirects=True,
                headers=self.auth_header,
            )
            self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)
            self.assertEqual(expected_response, json.loads(response.data))

    def test_change_password_to_one_with_empty_spaces(self):
        with self.client:
            new_password = "password with spaces"
            expected_response = USER_INPUTS_SPACE_IN_PASSWORD
            response = self.client.put(
                "/user/change_password",
                json={
                    "current_password": self.current_password,
                    "new_password": new_password,
                },
                follow_redirects=True,
                headers=self.auth_header,
            )
            self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)
            self.assertEqual(expected_response, json.loads(response.data))

    def test_change_password_with_authentication_token_expired(self):
        with self.client:
            new_password = "123new_password"
            auth_header = get_test_request_header(
                self.first_user.id, datetime.timedelta(seconds=-1)
            )
            expected_response = TOKEN_HAS_EXPIRED
            response = self.client.put(
                "/user/change_password",
                json={
                    "current_password": self.current_password,
                    "new_password": new_password,
                },
                follow_redirects=True,
                headers=auth_header,
            )
            self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
            self.assertEqual(expected_response, json.loads(response.data))


if __name__ == "__main__":
    unittest.main()
