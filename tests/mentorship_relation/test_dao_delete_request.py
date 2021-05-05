from datetime import datetime, timedelta
from http import HTTPStatus

from app import messages
from app.api.dao.mentorship_relation import MentorshipRelationDAO
from app.database.models.tasks_list import TasksListModel
from app.utils.enum_utils import MentorshipRelationState
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.models.user import UserModel
from app.database.sqlalchemy_extension import db
from tests.base_test_case import BaseTestCase
from tests.test_data import user1, user2


class TestMentorshipRelationDeleteDAO(BaseTestCase):

    # Setup consists of adding 2 users into the database
    # User 1 is the mentorship relation requester = action user
    # User 2 is the receiver
    def setUp(self):
        super().setUp()

        self.first_user = UserModel(
            name=user1["name"],
            email=user1["email"],
            username=user1["username"],
            password=user1["password"],
            terms_and_conditions_checked=user1["terms_and_conditions_checked"],
        )
        self.second_user = UserModel(
            name=user2["name"],
            email=user2["email"],
            username=user2["username"],
            password=user2["password"],
            terms_and_conditions_checked=user2["terms_and_conditions_checked"],
        )

        # making sure both are available to be mentor or mentee
        self.first_user.need_mentoring = True
        self.first_user.available_to_mentor = True
        self.first_user.is_email_verified = True
        self.second_user.need_mentoring = True
        self.second_user.available_to_mentor = True
        self.second_user.is_email_verified = True

        self.notes_example = "description of a good mentorship relation"

        self.now_datetime = datetime.utcnow()
        self.end_date_example = self.now_datetime + timedelta(weeks=5)

        db.session.add(self.first_user)
        db.session.add(self.second_user)
        db.session.commit()

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

    def test_dao_delete_non_existing_mentorship_request(self):

        result = MentorshipRelationDAO.delete_request(self.first_user.id, 123)

        self.assertEqual(
            (messages.MENTORSHIP_RELATION_REQUEST_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND),
            result,
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(
                id=self.mentorship_relation.id
            ).first()
        )

    def test_dao_sender_does_not_exist(self):

        result = MentorshipRelationDAO.delete_request(123, self.mentorship_relation.id)

        self.assertEqual((messages.USER_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND), result)
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(
                id=self.mentorship_relation.id
            ).first()
        )

    def test_dao_receiver_tries_to_delete_mentorship_request(self):

        result = MentorshipRelationDAO.delete_request(
            self.second_user.id, self.mentorship_relation.id
        )

        self.assertEqual(
            (messages.CANT_DELETE_REQUEST_YOU_DIDNT_CREATE, HTTPStatus.FORBIDDEN),
            result,
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(
                id=self.mentorship_relation.id
            ).first()
        )

    def test_dao_sender_delete_mentorship_request(self):
        relation_id = self.mentorship_relation.id

        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(id=relation_id).first()
        )

        result = MentorshipRelationDAO.delete_request(self.first_user.id, relation_id)
        self.assertEqual(
            (messages.MENTORSHIP_RELATION_WAS_DELETED_SUCCESSFULLY, HTTPStatus.OK),
            result,
        )

        self.assertIsNone(
            MentorshipRelationModel.query.filter_by(id=relation_id).first()
        )

    def test_dao_user_not_creator_tries_to_delete_mentorship_request(self):

        result = MentorshipRelationDAO.delete_request(
            self.admin_user.id, self.mentorship_relation.id
        )

        self.assertEqual(
            (messages.CANT_DELETE_REQUEST_YOU_DIDNT_CREATE, HTTPStatus.FORBIDDEN),
            result,
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(
                id=self.mentorship_relation.id
            ).first()
        )

    def test_dao_delete_mentorship_request_user_not_creator_and_request_not_in_pending_state(
        self,
    ):
        relation_id = self.mentorship_relation.id
        relation_states = [
            relation_state
            for relation_state in MentorshipRelationState
            if relation_state != MentorshipRelationState.PENDING
        ]

        for relation_state in relation_states:
            # persist the mentorship_relation
            self.mentorship_relation.state = relation_state
            db.session.add(self.mentorship_relation)
            db.session.commit()

            result = MentorshipRelationDAO.delete_request(
                self.second_user.id, self.mentorship_relation.id
            )
            self.assertEqual(
                (messages.CANT_DELETE_REQUEST_YOU_DIDNT_CREATE, HTTPStatus.FORBIDDEN),
                result,
            )
            self.assertIsNotNone(
                MentorshipRelationModel.query.filter_by(id=relation_id).first()
            )

    def test_dao_mentorship_delete_request_not_in_pending_state(self):
        relation_id = self.mentorship_relation.id

        self.mentorship_relation.state = MentorshipRelationState.ACCEPTED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        result = MentorshipRelationDAO.delete_request(
            self.first_user.id, self.mentorship_relation.id
        )
        self.assertEqual(
            (messages.NOT_PENDING_STATE_RELATION, HTTPStatus.FORBIDDEN), result
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(id=relation_id).first()
        )

        self.mentorship_relation.state = MentorshipRelationState.COMPLETED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        result = MentorshipRelationDAO.delete_request(
            self.first_user.id, self.mentorship_relation.id
        )
        self.assertEqual(
            (messages.NOT_PENDING_STATE_RELATION, HTTPStatus.FORBIDDEN), result
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(id=relation_id).first()
        )

        self.mentorship_relation.state = MentorshipRelationState.CANCELLED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        result = MentorshipRelationDAO.delete_request(
            self.first_user.id, self.mentorship_relation.id
        )
        self.assertEqual(
            (messages.NOT_PENDING_STATE_RELATION, HTTPStatus.FORBIDDEN), result
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(id=relation_id).first()
        )

        self.mentorship_relation.state = MentorshipRelationState.REJECTED
        db.session.add(self.mentorship_relation)
        db.session.commit()

        result = MentorshipRelationDAO.delete_request(
            self.first_user.id, self.mentorship_relation.id
        )
        self.assertEqual(
            (messages.NOT_PENDING_STATE_RELATION, HTTPStatus.FORBIDDEN), result
        )
        self.assertIsNotNone(
            MentorshipRelationModel.query.filter_by(id=relation_id).first()
        )
