import unittest
from datetime import datetime

from app.database.models.tasks_list import TasksListModel
from app.utils.enum_utils import MentorshipRelationState
from tests.base_test_case import BaseTestCase
from app.database.models.user import UserModel
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.sqlalchemy_extension import db

from tests.test_data import user1, user2


# Testing Mentorship Relation database model
#
# Tests:
#     - Mentorship Relation creation
#     - Mentorship Relation setup in mentors and mentee
#     - Mentorship Relation json format
#     - Mentorship Relation update


class TestMentorshipRelationModel(BaseTestCase):

    # Setup consists of adding 2 users into the database
    def setUp(self):
        db.create_all()

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

        self.notes_example = "description of a good mentorship relation"

        now_datetime = datetime.utcnow()
        self.start_date_example = datetime(
            year=now_datetime.year + 1, month=3, day=1
        ).timestamp()
        self.end_date_example = datetime(
            year=now_datetime.year + 1, month=5, day=1
        ).timestamp()
        self.now_datetime = datetime.utcnow().timestamp()

        db.session.add(self.first_user)
        db.session.add(self.second_user)
        db.session.commit()

        self.mentorship_relation = MentorshipRelationModel(
            action_user_id=self.first_user.id,
            mentor_user=self.first_user,
            mentee_user=self.second_user,
            creation_date=self.now_datetime,
            end_date=self.end_date_example,
            state=MentorshipRelationState.PENDING,
            notes=self.notes_example,
            tasks_list=TasksListModel(),
        )
        db.session.add(self.mentorship_relation)
        db.session.commit()

    def test_mentorship_relation_creation(self):
        query_mentorship_relation = MentorshipRelationModel.query.first()

        self.assertTrue(query_mentorship_relation is not None)

        self.assertEqual(1, query_mentorship_relation.id)

        # asserting relation extra fields
        self.assertEqual(self.first_user.id, query_mentorship_relation.action_user_id)
        self.assertEqual(self.now_datetime, query_mentorship_relation.creation_date)
        self.assertIsNone(query_mentorship_relation.accept_date)
        self.assertIsNone(query_mentorship_relation.start_date)
        self.assertEqual(self.end_date_example, query_mentorship_relation.end_date)
        self.assertEqual(self.notes_example, query_mentorship_relation.notes)
        self.assertEqual(
            MentorshipRelationState.PENDING, query_mentorship_relation.state
        )

        # asserting mentor and mentees setup
        self.assertEqual(self.first_user.id, query_mentorship_relation.mentor_id)
        self.assertEqual(self.second_user.id, query_mentorship_relation.mentee_id)

        # assert mentors' mentor_relations and mentee_relations
        self.assertEqual(1, len(self.first_user.mentor_relations))
        self.assertEqual(query_mentorship_relation, self.first_user.mentor_relations[0])
        self.assertEqual([], self.first_user.mentee_relations)

        # assert mentees' mentor_relations and mentee_relations
        self.assertEqual(1, len(self.second_user.mentee_relations))
        self.assertEqual(
            query_mentorship_relation, self.second_user.mentee_relations[0]
        )
        self.assertEqual([], self.second_user.mentor_relations)

    def test_mentorship_relation_json_representation(self):
        expected_json = {
            "id": 1,
            "action_user_id": self.first_user.id,
            "mentor_id": self.first_user.id,
            "mentee_id": self.second_user.id,
            "creation_date": self.now_datetime,
            "accept_date": None,
            "start_date": None,
            "end_date": self.end_date_example,
            "state": MentorshipRelationState.PENDING,
            "notes": self.notes_example,
        }
        self.assertEqual(expected_json, self.mentorship_relation.json())

    def test_mentorship_relation_update(self):
        new_notes = "This contract notes are different..."
        self.mentorship_relation.notes = new_notes

        db.session.add(self.mentorship_relation)
        db.session.commit()

        self.assertEqual(self.mentorship_relation.notes, new_notes)

        # assert mentors' mentor_relations and mentee_relations
        self.assertEqual(1, len(self.first_user.mentor_relations))
        self.assertEqual(new_notes, self.first_user.mentor_relations[0].notes)
        self.assertEqual([], self.first_user.mentee_relations)

        # assert mentees' mentor_relations and mentee_relations
        self.assertEqual(1, len(self.second_user.mentee_relations))
        self.assertEqual(new_notes, self.second_user.mentee_relations[0].notes)
        self.assertEqual([], self.second_user.mentor_relations)

    def test_find_mentorship_relation_by_id(self):
        query_mentorship_relation = MentorshipRelationModel.query.first()
        find_by_id_result = MentorshipRelationModel.find_by_id(
            query_mentorship_relation.id
        )
        self.assertEqual(query_mentorship_relation, find_by_id_result)

    def test_empty_table(self):
        self.assertFalse(MentorshipRelationModel.is_empty())
        db.session.delete(self.mentorship_relation)
        db.session.commit()
        self.assertTrue(MentorshipRelationModel.is_empty())

    def test__validations_comment(self):
        self.assertRaises(
            AssertionError,
            MentorshipRelationModel,
            action_user_id=self.first_user.id,
            mentor_user=self.first_user,
            mentee_user=self.second_user,
            creation_date=self.now_datetime,
            end_date=self.end_date_example,
            state=MentorshipRelationState.PENDING,
            notes=" s ",
            tasks_list=TasksListModel(),
        )


if __name__ == "__main__":
    unittest.main()
