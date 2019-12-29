import unittest
from datetime import datetime, timedelta

from app import messages
from app.api.dao.mentorship_relation import MentorshipRelationDAO
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.models.tasks_list import TasksListModel
from app.utils.enum_utils import MentorshipRelationState
from tests.mentorship_relation.relation_base_setup import MentorshipRelationBaseTestCase
from app.database.sqlalchemy_extension import db


# TODO test combination of parameters while listing relations

class TestMentorshipRelationListingDAO(MentorshipRelationBaseTestCase):

    # Setup consists of adding 2 users into the database
    def setUp(self):
        super(TestMentorshipRelationListingDAO, self).setUp()

        self.notes_example = 'description of a good mentorship relation'
        self.now_datetime = datetime.now()
        self.end_date_example = self.now_datetime + timedelta(weeks=5)

        self.dao = MentorshipRelationDAO()

        # create new mentorship relation

        self.pending_mentorship_relation = MentorshipRelationModel(
            action_user_id=self.first_user.id,
            mentor_user=self.first_user,
            mentee_user=self.second_user,
            creation_date=self.now_datetime.timestamp(),
            end_date=self.end_date_example.timestamp(),
            state=MentorshipRelationState.PENDING,
            notes=self.notes_example,
            tasks_list=TasksListModel()
        )

        self.accepted_mentorship_relation = MentorshipRelationModel(
            action_user_id=self.first_user.id,
            mentor_user=self.first_user,
            mentee_user=self.second_user,
            creation_date=self.now_datetime.timestamp(),
            end_date=self.end_date_example.timestamp(),
            state=MentorshipRelationState.ACCEPTED,
            notes=self.notes_example,
            tasks_list=TasksListModel()
        )

        self.rejected_mentorship_relation = MentorshipRelationModel(
            action_user_id=self.first_user.id,
            mentor_user=self.first_user,
            mentee_user=self.second_user,
            creation_date=self.now_datetime.timestamp(),
            end_date=self.end_date_example.timestamp(),
            state=MentorshipRelationState.REJECTED,
            notes=self.notes_example,
            tasks_list=TasksListModel()
        )

        self.cancelled_mentorship_relation = MentorshipRelationModel(
            action_user_id=self.first_user.id,
            mentor_user=self.first_user,
            mentee_user=self.second_user,
            creation_date=self.now_datetime.timestamp(),
            end_date=self.end_date_example.timestamp(),
            state=MentorshipRelationState.CANCELLED,
            notes=self.notes_example,
            tasks_list=TasksListModel()
        )

        self.completed_mentorship_relation = MentorshipRelationModel(
            action_user_id=self.first_user.id,
            mentor_user=self.first_user,
            mentee_user=self.second_user,
            creation_date=self.now_datetime.timestamp(),
            end_date=self.end_date_example.timestamp(),
            state=MentorshipRelationState.COMPLETED,
            notes=self.notes_example,
            tasks_list=TasksListModel()
        )

        db.session.add(self.pending_mentorship_relation)
        db.session.add(self.accepted_mentorship_relation)
        db.session.add(self.rejected_mentorship_relation)
        db.session.add(self.cancelled_mentorship_relation)
        db.session.add(self.completed_mentorship_relation)

        db.session.commit()

    def test_dao_list_mentorship_relation_accepted(self):
        result = self.dao.list_mentorship_relations(user_id=self.first_user.id, rel_states=["accepted"])

        self.assertEqual(([self.accepted_mentorship_relation], 200), result)

    def test_dao_list_mentorship_relation_cancelled(self):
        result = self.dao.list_mentorship_relations(user_id=self.first_user.id, rel_states=["cancelled"])

        self.assertEqual(([self.cancelled_mentorship_relation], 200), result)

    def test_dao_list_mentorship_relation_rejected(self):
        result = self.dao.list_mentorship_relations(user_id=self.first_user.id, rel_states=["rejected"])

        self.assertEqual(([self.rejected_mentorship_relation], 200), result)

    def test_dao_list_mentorship_relation_completed(self):
        result = self.dao.list_mentorship_relations(user_id=self.first_user.id, rel_states=["completed"])

        self.assertEqual(([self.completed_mentorship_relation], 200), result)

    def test_dao_list_mentorship_relation_pending(self):
        result = self.dao.list_mentorship_relations(user_id=self.first_user.id, rel_states=["pending"])

        self.assertEqual(([self.pending_mentorship_relation], 200), result)

    def test_dao_list_mentorship_relation_all(self):
        result = self.dao.list_mentorship_relations(user_id=self.first_user.id)
        expected_response = [self.pending_mentorship_relation, self.accepted_mentorship_relation,
                             self.rejected_mentorship_relation, self.cancelled_mentorship_relation,
                             self.completed_mentorship_relation], 200

        self.assertIsNotNone(result)
        self.assertEqual(expected_response, result)

    def test_dao_list_mentorship_relation_all_pending_and_accepted(self):
        result = self.dao.list_mentorship_relations(user_id=self.first_user.id, rel_states=["pending", "accepted"])
        expected_response = [self.pending_mentorship_relation, self.accepted_mentorship_relation], 200

        self.assertIsNotNone(result)
        self.assertEqual(expected_response, result)


if __name__ == '__main__':
    unittest.main()
