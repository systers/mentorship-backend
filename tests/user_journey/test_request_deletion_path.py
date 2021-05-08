import unittest
from datetime import datetime, timedelta
from http import HTTPStatus

from flask import json
from flask_restx import marshal

from app import messages
from app.api.models.user import public_user_api_model
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.utils.enum_utils import MentorshipRelationState
from app.database.models.tasks_list import TasksListModel
from app.database.models.user import UserModel
from app.database.sqlalchemy_extension import db
from app.utils.enum_utils import MentorshipRelationState
from tests.base_test_case import BaseTestCase
from tests.test_utils import get_test_request_header
from tests.test_data import user1, user2
from app.api.models.mentorship_relation import mentorship_request_response_body


class TestRequestDeletionPath(BaseTestCase):
    """
    Scenario: User A (mentor) and User B (mentee). The mentee sends
    a mentorship request to the mentor and then deletes the request.
    - User B (mentee) sends a request to User A (mentor)
    - User B (mentee) deletes the request
    """

    def setUp(self):
        super().setUp()

        # Defining mentor for this test
        self.mentor = UserModel(
            name="Mentor A",
            email=user1["email"],
            username=user1["username"],
            password=user1["password"],
            terms_and_conditions_checked=user1["terms_and_conditions_checked"],
        )

        # Defining mentee for this test
        self.mentee = UserModel(
            name="Mentee B",
            email=user2["email"],
            username=user2["username"],
            password=user2["password"],
            terms_and_conditions_checked=user2["terms_and_conditions_checked"],
        )

        self.mentor.is_email_verified = True
        self.mentor.available_to_mentor = True
        self.mentee.is_email_verified = True
        self.mentee.need_mentoring = True

        db.session.add(self.mentor)
        db.session.add(self.mentee)
        db.session.commit()

        self.test_description = "A request for mentorship"

    def test_deletion_path(self):

        mentor_auth_header = get_test_request_header(self.mentor.id)
        mentee_auth_header = get_test_request_header(self.mentee.id)

        # The mentee sends a new mentorship request to the mentor
        request_body = {
            "mentor_id": self.mentor.id,
            "mentee_id": self.mentee.id,
            "end_date": int((datetime.now() + timedelta(weeks=5)).timestamp()),
            "notes": self.test_description,
        }
        send_request_response = self.client.post(
            "/mentorship_relation/send_request",
            headers=mentee_auth_header,
            content_type="application/json",
            data=json.dumps(request_body),
        )

        self.assertEqual(HTTPStatus.CREATED, send_request_response.status_code)

        # Receiving the mentorship request on the mentor's side
        received_requests_response = self.client.get(
            "/mentorship_relations",
            headers=mentor_auth_header,
            content_type="application/json",
        )
        requests = json.loads(received_requests_response.data)
        request_id = requests[0]["id"]

        self.assertIsNotNone(request_id)

        ## The mentor rejects the request
        deletion_response = self.client.delete(
            f"/mentorship_relation/{request_id}", headers=mentee_auth_header
        )
        deletion_request = json.loads(deletion_response.data)
        self.assertEqual(
            messages.MENTORSHIP_RELATION_WAS_DELETED_SUCCESSFULLY, deletion_request
        )
        self.assertEqual(HTTPStatus.OK, deletion_response.status_code)


if __name__ == "__main__":
    unittest.main()
