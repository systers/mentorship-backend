import unittest
from datetime import datetime, timedelta

from flask import json
from flask_restx import marshal

from app import messages
from app.api.models.user import public_user_api_model
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.models.tasks_list import TasksListModel
from app.database.models.user import UserModel
from app.database.sqlalchemy_extension import db
from app.utils.enum_utils import MentorshipRelationState
from tests.base_test_case import BaseTestCase
from tests.test_utils import get_test_request_header
from tests.test_data import user1, user2, user3, user5


class TestListUsersApi(BaseTestCase):
    def setUp(self):
        super(TestListUsersApi, self).setUp()

        self.verified_user = UserModel(
            name=user1["name"] + "    Example",
            email=user1["email"],
            username=user1["username"],
            password=user1["password"],
            terms_and_conditions_checked=user1["terms_and_conditions_checked"],
        )
        self.other_user = UserModel(
            name=user2["name"],
            email=user2["email"],
            username=user2["username"],
            password=user2["password"],
            terms_and_conditions_checked=user2["terms_and_conditions_checked"],
        )
        self.second_user = UserModel(
            name=user3["name"],
            email=user3["email"],
            username=user3["username"],
            password=user3["password"],
            terms_and_conditions_checked=user3["terms_and_conditions_checked"],
        )

        self.third_user = UserModel(
            name=user5["name"],
            email=user5["email"],
            username=user5["username"],
            password=user5["password"],
            terms_and_conditions_checked=user5["terms_and_conditions_checked"],
        )
        self.third_user.location = user5["location"]

        self.verified_user.is_email_verified = True
        self.verified_user.need_mentoring = True

        # all three users are not in a current relationship
        # verified_user needs mentoring -> is_available = True
        self.verified_user.is_available = True
        self.other_user.is_available = False
        self.second_user.is_available = False
        self.third_user.is_available = False

        db.session.add(self.verified_user)
        db.session.add(self.other_user)
        db.session.add(self.second_user)
        db.session.add(self.third_user)
        db.session.commit()

    def create_relationship(self):
        """Creates relationship between verified and other user."""
        relation = MentorshipRelationModel(
            self.other_user.id,
            self.other_user,
            self.verified_user,
            datetime.now().timestamp(),
            (datetime.now() + timedelta(weeks=5)).timestamp(),
            MentorshipRelationState.ACCEPTED,
            "notes",
            TasksListModel(),
        )
        db.session.add(relation)
        db.session.commit()

    def test_list_users_api_resource_non_auth(self):
        expected_response = messages.AUTHORISATION_TOKEN_IS_MISSING
        actual_response = self.client.get("/users", follow_redirects=True)

        self.assertEqual(401, actual_response.status_code)
        self.assertDictEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_without_search_query_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [
            marshal(self.verified_user, public_user_api_model),
            marshal(self.other_user, public_user_api_model),
            marshal(self.second_user, public_user_api_model),
            marshal(self.third_user, public_user_api_model),
        ]
        actual_response = self.client.get(
            "/users", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_search_query_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.other_user, public_user_api_model)]
        actual_response = self.client.get(
            "/users?search=b", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_search_query_all_caps_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.other_user, public_user_api_model)]
        actual_response = self.client.get(
            "/users?search=USERB", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_search_query_with_spaces_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.verified_user, public_user_api_model)]
        actual_response = self.client.get(
            f"/users?search={self.verified_user.name}",
            follow_redirects=True,
            headers=auth_header,
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_location_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.third_user, public_user_api_model)]
        actual_response = self.client.get(
            f"/users?location={self.third_user.location}",
            follow_redirects=True,
            headers=auth_header,
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_search_with_special_characters_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.second_user, public_user_api_model)]
        actual_response = self.client.get(
            f"/users?search=s_t-r%24a%2Fn'ge",
            follow_redirects=True,
            headers=auth_header,
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_page_query_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [
            marshal(self.verified_user, public_user_api_model),
            marshal(self.other_user, public_user_api_model),
            marshal(self.second_user, public_user_api_model),
            marshal(self.third_user, public_user_api_model)]
        actual_response = self.client.get(
            "/users?page=1", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_page_query_out_of_range_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = []
        actual_response = self.client.get(
            "/users?page=2", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_page_and_per_page_query_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.verified_user, public_user_api_model)]
        actual_response = self.client.get(
            "/users?page=1&per_page=1", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_partial_page_and_per_page_query_resource_auth(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.second_user, public_user_api_model),
        marshal(self.third_user, public_user_api_model)]
        actual_response = self.client.get(
            "/users?page=2&per_page=2", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_resource_verified_users(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.verified_user, public_user_api_model)]
        actual_response = self.client.get(
            "/users/verified", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_page_query_resource_verified_users(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.verified_user, public_user_api_model)]
        actual_response = self.client.get(
            "/users/verified?page=1", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_page_query_out_of_range_resource_verified_users(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = []
        actual_response = self.client.get(
            "/users/verified?page=2", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_page_and_per_page_query_resource_verified_users(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [marshal(self.verified_user, public_user_api_model)]
        actual_response = self.client.get(
            "/users/verified?page=1&per_page=1", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_with_a_page_and_empty_per_page_query_resource_verified_users(self):
        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = []
        actual_response = self.client.get(
            "/users/verified?page=1&per_page=0", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_list_users_api_relation(self):
        # Creates relationship between two users, which means that they are
        # not available
        self.create_relationship()
        self.verified_user.is_available = False
        self.other_user.is_available = False

        auth_header = get_test_request_header(self.admin_user.id)
        expected_response = [
            marshal(self.verified_user, public_user_api_model),
            marshal(self.other_user, public_user_api_model),
            marshal(self.second_user, public_user_api_model),
            marshal(self.third_user, public_user_api_model),
        ]
        actual_response = self.client.get(
            "/users", follow_redirects=True, headers=auth_header
        )

        self.assertEqual(200, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))


if __name__ == "__main__":
    unittest.main()
