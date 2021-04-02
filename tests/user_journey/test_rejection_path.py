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


class TestRejectionPath(BaseTestCase):
    """
    Scenario: User A (mentor) and User B (mentee). The mentee sends
    a mentorship request to the mentor and the mentor rejects the request.
    - User B (mentee) sends a request to User A (mentor)
    - User A (mentor) rejects request
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

    def test_rejection_path(self):

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
        print("The mentorship request has been sent")

        # Receiving the mentorship request on the mentor's side
        received_requests_response = self.client.get(
            "/mentorship_relations",
            headers=mentor_auth_header,
            content_type="application/json",
        )
        requests = json.loads(received_requests_response.data)

        latest_mentorship_request = requests[0]
        request_id = latest_mentorship_request["id"]
        request_state = latest_mentorship_request["state"]

        self.assertIsNotNone(request_id)
        self.assertEqual(MentorshipRelationState.PENDING, request_state)

        # The mentor rejects the request
        reject_response = self.client.put(
            f"/mentorship_relation/{request_id}/reject", headers=mentor_auth_header
        )
        self.assertEqual(HTTPStatus.OK, reject_response.status_code)

        received_requests_response = self.client.get(
            "/mentorship_relations",
            headers=mentor_auth_header,
            content_type="application/json",
        )
        requests = json.loads(received_requests_response.data)

        latest_mentorship_request = requests[0]
        request_id = latest_mentorship_request["id"]
        request_state = latest_mentorship_request["state"]

        self.assertEqual(MentorshipRelationState.REJECTED, request_state)
        print("The mentorship request has been rejected (PUT)")

        # Mentee discovers that the request has been rejected
        mentee_current_rejected_relation = self.client.get(
            f"/mentorship_relations/current", headers=mentee_auth_header
        )
        self.assertEqual(HTTPStatus.OK, mentee_current_rejected_relation.status_code)

        current_rejected_relation_data = json.loads(
            mentee_current_rejected_relation.data
        )
        self.assertEqual(
            messages.NOT_IN_MENTORED_RELATION_CURRENTLY["message"],
            current_rejected_relation_data["message"],
        )


if __name__ == "__main__":
    unittest.main()
