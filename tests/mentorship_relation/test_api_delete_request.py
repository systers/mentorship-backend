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


class TestDeleteMentorshipRequestApi(MentorshipRelationBaseTestCase):

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
            state=MentorshipRelationState.PENDING,
            notes=self.notes_example,
            tasks_list=TasksListModel(),
        )

        db.session.add(self.mentorship_relation)
        db.session.commit()

    def test_sender_delete_mentorship_request(self):
        request_id = self.mentorship_relation.id

        self.assertEqual(
            MentorshipRelationState.PENDING, self.mentorship_relation.state
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(id=request_id).first()
        )

        with self.client:
            response = self.client.delete(
                f"/mentorship_relation/{request_id}",
                headers=get_test_request_header(self.first_user.id),
            )
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertDictEqual(
            messages.MENTORSHIP_RELATION_WAS_DELETED_SUCCESSFULLY,
            json.loads(response.data),
        )
        self.assertIsNone(
            MentorshipRelationModel.query.filter_by(id=request_id).first()
        )

    def test_receiver_delete_mentorship_request(self):
        request_id = self.mentorship_relation.id

        self.assertEqual(
            MentorshipRelationState.PENDING, self.mentorship_relation.state
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(id=request_id).first()
        )

        with self.client:
            response = self.client.delete(
                f"/mentorship_relation/{request_id}",
                headers=get_test_request_header(self.second_user.id),
            )
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)
        self.assertDictEqual(
            messages.CANT_DELETE_REQUEST_YOU_DIDNT_CREATE, json.loads(response.data)
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(id=request_id).first()
        )


if __name__ == "__main__":
    unittest.main()
