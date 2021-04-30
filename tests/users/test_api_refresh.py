import unittest
from datetime import timedelta
from http import HTTPStatus
from flask import json

from app import messages
from app.database.sqlalchemy_extension import db
from app.database.models.user import UserModel
from app.api.dao.user import UserDAO
from tests.base_test_case import BaseTestCase
from tests.test_data import user1
from tests.test_utils import get_test_request_header


class TestUserRefreshApi(BaseTestCase):

    # User 1 which has email verified
    def setUp(self):
        super().setUp()

        self.first_user = UserModel(
            name=user1["name"],
            email=user1["email"],
            username=user1["username"],
            password=user1["password"],
            terms_and_conditions_checked=user1["terms_and_conditions_checked"],
        )
        self.first_user.is_email_verified = True

        db.session.add(self.first_user)
        db.session.commit()

    def test_user_refresh(self):
        with self.client:
            refresh_header = get_test_request_header(
                UserDAO.get_user_by_username(user1["username"]).id, refresh=True
            )
            response = self.client.post(
                "/refresh",
                headers=refresh_header,
                follow_redirects=True,
                content_type="application/json",
            )
            self.assertIsNotNone(response.json.get("access_token"))
            self.assertEqual(1, len(response.json))
            self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_user_refresh_without_header(self):
        expected_response = messages.AUTHORISATION_TOKEN_IS_MISSING
        actual_response = self.client.post("/refresh", follow_redirects=True)

        self.assertEqual(HTTPStatus.UNAUTHORIZED, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_user_refresh_invalid_token(self):
        with self.client:
            refresh_token = "invalid_token"
            auth_header = {"Authorization": "Bearer {}".format(refresh_token)}
            expected_response = messages.TOKEN_IS_INVALID
            actual_response = self.client.post(
                "/refresh",
                headers=auth_header,
                follow_redirects=True,
                content_type="application/json",
            )

            self.assertEqual(HTTPStatus.UNAUTHORIZED, actual_response.status_code)
            self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_user_refresh_expired_token(self):
        auth_header = get_test_request_header(
            self.first_user.id,
            token_expiration_delta=timedelta(minutes=-5),
            refresh=True,
        )
        expected_response = messages.TOKEN_HAS_EXPIRED
        actual_response = self.client.post(
            "/refresh",
            follow_redirects=True,
            headers=auth_header,
            content_type="application/json",
        )

        self.assertEqual(HTTPStatus.UNAUTHORIZED, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_user_refresh_fails_change_password(self):
        auth_header = get_test_request_header(self.first_user.id, refresh=True)
        passDict = {
            "current_password": user1["password"],
            "new_password": "somepassword",
        }
        UserDAO.change_password(self.first_user.id, passDict)
        response = self.client.post(
            "/refresh",
            follow_redirects=True,
            headers=auth_header,
            content_type="application/json",
        )
        self.assertEqual(401, response.status_code)
        self.assertEqual(json.loads(response.data), messages.TOKEN_IS_INVALID)

    def test_user_refresh_change_password(self):
        passDict = {
            "current_password": user1["password"],
            "new_password": "setpassword",
        }
        UserDAO.change_password(self.first_user.id, passDict)
        auth_header = get_test_request_header(self.first_user.id, refresh=True)
        response = self.client.post(
            "/refresh",
            follow_redirects=True,
            headers=auth_header,
            content_type="application/json",
        )

        print(json.loads(response.data))
        self.assertEqual(200, response.status_code)


if __name__ == "__main__":
    unittest.main()
