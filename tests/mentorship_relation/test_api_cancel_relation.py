import json
import unittest
from datetime import datetime, timedelta
from http import HTTPStatus

from app import messages
from app.database.models.tasks_list import TasksListModel
from app.database.sqlalchemy_extension import db
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.utils.enum_utils import MentorshipRelationState
from tests.mentorship_relation.relation_base_setup import MentorshipRelationBaseTestCase
from tests.test_utils import get_test_request_header
from datetime import timedelta


class TestCancelMentorshipRelationApi(MentorshipRelationBaseTestCase):

    # Setup consists of adding 2 users into the database
    # User 1 is the mentorship relation requester = action user
    # User 2 is the receiver
    def setUp(self):
        super().setUp()

        self.notes_example = "description of a good mentorship relation"

        self.now_datetime = datetime.utcnow()
        self.end_date_example = self.now_datetime + timedelta(weeks=5)

        # create new mentorship relation

        self.mentorship_relation = MentorshipRelationModel(
            action_user_id=self.first_user.id,
            mentor_user=self.first_user,
            mentee_user=self.second_user,
            creation_date=self.now_datetime.timestamp(),
            end_date=self.end_date_example.timestamp(),
            state=MentorshipRelationState.ACCEPTED,
            notes=self.notes_example,
            tasks_list=TasksListModel(),
        )

        db.session.add(self.mentorship_relation)
        db.session.commit()

    def test__mentor_cancel_mentorship_relation(self):
        self.assertEqual(
            MentorshipRelationState.ACCEPTED, self.mentorship_relation.state
        )
        with self.client:
            response = self.client.put(
                f"/mentorship_relation/{self.mentorship_relation.id}/cancel",
                headers=get_test_request_header(self.first_user.id),
            )

            self.assertEqual(HTTPStatus.OK, response.status_code)
            self.assertEqual(
                MentorshipRelationState.CANCELLED, self.mentorship_relation.state
            )
            self.assertDictEqual(
                messages.MENTORSHIP_RELATION_WAS_CANCELLED_SUCCESSFULLY,
                json.loads(response.data),
            )

    def test__mentee_cancel_mentorship_relation(self):
        self.assertEqual(
            MentorshipRelationState.ACCEPTED, self.mentorship_relation.state
        )
        with self.client:
            response = self.client.put(
                f"/mentorship_relation/{self.mentorship_relation.id}/cancel",
                headers=get_test_request_header(self.second_user.id),
            )

            self.assertEqual(HTTPStatus.OK, response.status_code)
            self.assertEqual(
                MentorshipRelationState.CANCELLED, self.mentorship_relation.state
            )
            self.assertDictEqual(
                messages.MENTORSHIP_RELATION_WAS_CANCELLED_SUCCESSFULLY,
                json.loads(response.data),
            )

    # Valid user tries to cancel valid task with authentication token missing (FAIL)
    # Response= 401, AUTHORISATION_TOKEN_IS_MISSING
    def test_cancel_mentorship_relation_noauth(self):
        self.assertEqual(
            MentorshipRelationState.ACCEPTED, self.mentorship_relation.state
        )
        with self.client:
            expected_response = messages.AUTHORISATION_TOKEN_IS_MISSING
            response = self.client.put(
                f"/mentorship_relation/{self.mentorship_relation.id}/cancel"
            )

            self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
            self.assertDictEqual(expected_response, json.loads(response.data))

    # Valid user tries to cancel valid task with authentication token expired (FAIL)
    # Response= 401, TOKEN_HAS_EXPIRED
    def test_cancel_mentorship_relation_expiredauth(self):
        self.assertEqual(
            MentorshipRelationState.ACCEPTED, self.mentorship_relation.state
        )
        with self.client:
            expected_response = messages.TOKEN_HAS_EXPIRED
            response = self.client.put(
                f"/mentorship_relation/{self.mentorship_relation.id}/cancel",
                headers=get_test_request_header(
                    self.second_user.id, token_expiration_delta=timedelta(minutes=-7)
                ),
            )

            self.assertEqual(HTTPStatus.UNAUTHORIZED, response.status_code)
            self.assertDictEqual(expected_response, json.loads(response.data))

    # User1 cancel a mentorship relation which the User1 is not involved with (FAIL)
    # Response= 400, CANT_CANCEL_UNINVOLVED_REQUEST
    def test_cancel_mentorship_relation_notinvolvedinrelation(self):
        self.assertEqual(
            MentorshipRelationState.ACCEPTED, self.mentorship_relation.state
        )
        with self.client:
            expected_response = messages.CANT_CANCEL_UNINVOLVED_REQUEST
            response = self.client.put(
                f"/mentorship_relation/{self.mentorship_relation.id}/cancel",
                headers=get_test_request_header(self.admin_user.id),
            )

            self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
            self.assertDictEqual(expected_response, json.loads(response.data))


if __name__ == "__main__":
    unittest.main()
