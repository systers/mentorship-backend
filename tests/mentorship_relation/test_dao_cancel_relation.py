from datetime import datetime, timedelta
from http import HTTPStatus

from app import messages
from app.api.dao.mentorship_relation import MentorshipRelationDAO
from app.database.models.tasks_list import TasksListModel
from app.utils.enum_utils import MentorshipRelationState
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.sqlalchemy_extension import db
from tests.mentorship_relation.relation_base_setup import MentorshipRelationBaseTestCase


# TODO test when a user tries to cancel a relation where this user is not involved


class TestMentorshipRelationListingDAO(MentorshipRelationBaseTestCase):

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

    def test_dao_cancel_non_existing_mentorship_request(self):
        DAO = MentorshipRelationDAO()

        result = DAO.cancel_relation(self.first_user.id, 123)

        self.assertEqual(
            (messages.MENTORSHIP_RELATION_REQUEST_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND),
            result,
        )
        self.assertEqual(
            MentorshipRelationState.PENDING, self.mentorship_relation.state
        )

    def test_dao_sender_does_not_exist_mentorship_request(self):
        DAO = MentorshipRelationDAO()

        result = DAO.cancel_relation(123, self.mentorship_relation.id)

        self.assertEqual((messages.USER_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND), result)
        self.assertEqual(
            MentorshipRelationState.PENDING, self.mentorship_relation.state
        )

    def test_dao_receiver_cancel_mentorship_request(self):
        self.mentorship_relation.state = MentorshipRelationState.ACCEPTED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        DAO = MentorshipRelationDAO()
        result = DAO.cancel_relation(self.second_user.id, self.mentorship_relation.id)

        self.assertEqual(
            (messages.MENTORSHIP_RELATION_WAS_CANCELLED_SUCCESSFULLY, HTTPStatus.OK),
            result,
        )
        self.assertEqual(
            MentorshipRelationState.CANCELLED, self.mentorship_relation.state
        )

    def test_dao_sender_cancel_mentorship_request(self):
        self.mentorship_relation.state = MentorshipRelationState.ACCEPTED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        DAO = MentorshipRelationDAO()
        result = DAO.cancel_relation(self.first_user.id, self.mentorship_relation.id)

        self.assertEqual(
            (messages.MENTORSHIP_RELATION_WAS_CANCELLED_SUCCESSFULLY, HTTPStatus.OK),
            result,
        )
        self.assertEqual(
            MentorshipRelationState.CANCELLED, self.mentorship_relation.state
        )

    def test_dao_mentorship_cancel_relation_not_in_accepted_state(self):
        DAO = MentorshipRelationDAO()

        self.mentorship_relation.state = MentorshipRelationState.PENDING
        db.session.add(self.mentorship_relation)
        db.session.commit()

        result = DAO.cancel_relation(self.second_user.id, self.mentorship_relation.id)
        self.assertEqual(
            (messages.UNACCEPTED_STATE_RELATION, HTTPStatus.FORBIDDEN), result
        )

        self.mentorship_relation.state = MentorshipRelationState.COMPLETED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        result = DAO.cancel_relation(self.second_user.id, self.mentorship_relation.id)
        self.assertEqual(
            (messages.UNACCEPTED_STATE_RELATION, HTTPStatus.FORBIDDEN), result
        )

        self.mentorship_relation.state = MentorshipRelationState.CANCELLED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        result = DAO.cancel_relation(self.second_user.id, self.mentorship_relation.id)
        self.assertEqual(
            (messages.UNACCEPTED_STATE_RELATION, HTTPStatus.FORBIDDEN), result
        )

        self.mentorship_relation.state = MentorshipRelationState.REJECTED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        result = DAO.cancel_relation(self.second_user.id, self.mentorship_relation.id)
        self.assertEqual(
            (messages.UNACCEPTED_STATE_RELATION, HTTPStatus.FORBIDDEN), result
        )
