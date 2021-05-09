from datetime import datetime, timedelta
from flask import json
from http import HTTPStatus
from app import messages
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.models.tasks_list import TasksListModel
from app.database.models.user import UserModel
from app.database.sqlalchemy_extension import db
from app.utils.enum_utils import MentorshipRelationState
from tests.base_test_case import BaseTestCase
from tests.test_utils import get_test_request_header


class TestHomeStatisticsApi(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user1 = UserModel("UserA", "user1", "__test__", "test@email.com", True)
        self.user2 = UserModel("UserB", "user2", "__test__", "test2@email.com", True)
        self.user1.available_to_mentor = True
        self.user1.is_email_verified = True
        self.user2.need_mentoring = True
        self.user2.is_email_verified = True

        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.commit()

    def test_relations_non_auth(self):
        expected_response = messages.AUTHORISATION_TOKEN_IS_MISSING
        actual_response = self.client.get("/home", follow_redirects=True)
        self.assertEqual(HTTPStatus.UNAUTHORIZED, actual_response.status_code)
        self.assertDictEqual(expected_response, json.loads(actual_response.data))

    def test_relations_invalid_id(self):
        auth_header = get_test_request_header(
            None
        )  # Supply invalid user ID for the test
        actual_response = self.client.get(
            "/home", follow_redirects=True, headers=auth_header
        )
        self.assertEqual(HTTPStatus.NOT_FOUND, actual_response.status_code)
        self.assertEqual(messages.USER_NOT_FOUND, json.loads(actual_response.data))

    def test_pending_requests_auth(self):
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(weeks=4)
        start_date = start_date.timestamp()
        end_date = end_date.timestamp()
        tasks_list = TasksListModel()

        mentorship_relation = MentorshipRelationModel(
            action_user_id=self.user2.id,
            mentor_user=self.user1,
            mentee_user=self.user2,
            creation_date=start_date,
            end_date=end_date,
            state=MentorshipRelationState.PENDING,
            notes=None,
            tasks_list=tasks_list,
        )

        db.session.add(mentorship_relation)
        db.session.commit()
        expected_response = {
            "name": "UserA",
            "pending_requests": 1,
            "accepted_requests": 0,
            "rejected_requests": 0,
            "completed_relations": 0,
            "cancelled_relations": 0,
            "achievements": [],
        }
        auth_header = get_test_request_header(self.user1.id)
        actual_response = self.client.get(
            "/home", follow_redirects=True, headers=auth_header
        )
        self.assertEqual(HTTPStatus.OK, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_accepted_requests_auth(self):
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(weeks=4)
        start_date = start_date.timestamp()
        end_date = end_date.timestamp()
        tasks_list = TasksListModel()

        mentorship_relation = MentorshipRelationModel(
            action_user_id=self.user2.id,
            mentor_user=self.user1,
            mentee_user=self.user2,
            creation_date=start_date,
            end_date=end_date,
            state=MentorshipRelationState.ACCEPTED,
            notes=None,
            tasks_list=tasks_list,
        )

        db.session.add(mentorship_relation)
        db.session.commit()
        expected_response = {
            "name": "UserA",
            "pending_requests": 0,
            "accepted_requests": 1,
            "rejected_requests": 0,
            "completed_relations": 0,
            "cancelled_relations": 0,
            "achievements": [],
        }
        auth_header = get_test_request_header(self.user1.id)
        actual_response = self.client.get(
            "/home", follow_redirects=True, headers=auth_header
        )
        self.assertEqual(HTTPStatus.OK, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_rejected_requests(self):
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(weeks=4)
        start_date = start_date.timestamp()
        end_date = end_date.timestamp()
        tasks_list = TasksListModel()

        mentorship_relation = MentorshipRelationModel(
            action_user_id=self.user2.id,
            mentor_user=self.user1,
            mentee_user=self.user2,
            creation_date=start_date,
            end_date=end_date,
            state=MentorshipRelationState.REJECTED,
            notes=None,
            tasks_list=tasks_list,
        )

        db.session.add(mentorship_relation)
        db.session.commit()
        expected_response = {
            "name": "UserA",
            "pending_requests": 0,
            "accepted_requests": 0,
            "rejected_requests": 1,
            "completed_relations": 0,
            "cancelled_relations": 0,
            "achievements": [],
        }
        auth_header = get_test_request_header(self.user1.id)
        actual_response = self.client.get(
            "/home", follow_redirects=True, headers=auth_header
        )
        self.assertEqual(HTTPStatus.OK, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_completed_relations(self):
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(weeks=4)
        start_date = start_date.timestamp()
        end_date = end_date.timestamp()
        tasks_list = TasksListModel()

        mentorship_relation = MentorshipRelationModel(
            action_user_id=self.user2.id,
            mentor_user=self.user1,
            mentee_user=self.user2,
            creation_date=start_date,
            end_date=end_date,
            state=MentorshipRelationState.COMPLETED,
            notes=None,
            tasks_list=tasks_list,
        )

        db.session.add(mentorship_relation)
        db.session.commit()
        expected_response = {
            "name": "UserA",
            "pending_requests": 0,
            "accepted_requests": 0,
            "rejected_requests": 0,
            "completed_relations": 1,
            "cancelled_relations": 0,
            "achievements": [],
        }
        auth_header = get_test_request_header(self.user1.id)
        actual_response = self.client.get(
            "/home", follow_redirects=True, headers=auth_header
        )
        self.assertEqual(HTTPStatus.OK, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_cancelled_relations(self):
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(weeks=4)
        start_date = start_date.timestamp()
        end_date = end_date.timestamp()
        tasks_list = TasksListModel()
        mentorship_relation = MentorshipRelationModel(
            action_user_id=self.user2.id,
            mentor_user=self.user1,
            mentee_user=self.user2,
            creation_date=start_date,
            end_date=end_date,
            state=MentorshipRelationState.CANCELLED,
            notes=None,
            tasks_list=tasks_list,
        )

        db.session.add(mentorship_relation)
        db.session.commit()
        expected_response = {
            "name": "UserA",
            "pending_requests": 0,
            "accepted_requests": 0,
            "rejected_requests": 0,
            "completed_relations": 0,
            "cancelled_relations": 1,
            "achievements": [],
        }
        auth_header = get_test_request_header(self.user1.id)
        actual_response = self.client.get(
            "/home", follow_redirects=True, headers=auth_header
        )
        self.assertEqual(HTTPStatus.OK, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))

    def test_achievements(self):
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(weeks=4)
        start_date = start_date.timestamp()
        end_date = end_date.timestamp()

        tasks_list = TasksListModel()
        task_created_time = datetime.utcnow().timestamp()
        task_completed_time = task_created_time + 100
        tasks_list.add_task(
            description="Test task",
            created_at=task_created_time,
            is_done=True,
            completed_at=task_completed_time,
        )
        tasks_list.add_task(
            description="Incomplete task: Should not appear in achievements",
            created_at=task_created_time,
            is_done=False,
            completed_at=task_completed_time,
        )

        db.session.add(tasks_list)
        db.session.commit()

        mentorship_relation = MentorshipRelationModel(
            action_user_id=self.user2.id,
            mentor_user=self.user1,
            mentee_user=self.user2,
            creation_date=start_date,
            end_date=end_date,
            state=MentorshipRelationState.ACCEPTED,
            notes=None,
            tasks_list=tasks_list,
        )

        db.session.add(mentorship_relation)
        db.session.commit()

        expected_response = {
            "name": "UserA",
            "pending_requests": 0,
            "accepted_requests": 1,
            "rejected_requests": 0,
            "completed_relations": 0,
            "cancelled_relations": 0,
            "achievements": [
                {
                    "completed_at": task_completed_time,
                    "created_at": task_created_time,
                    "description": "Test task",
                    "id": 1,  # This is the only task in the list
                    "is_done": True,
                }
            ],
        }
        auth_header = get_test_request_header(self.user1.id)
        actual_response = self.client.get(
            "/home", follow_redirects=True, headers=auth_header
        )
        self.assertEqual(HTTPStatus.OK, actual_response.status_code)
        self.assertEqual(expected_response, json.loads(actual_response.data))
