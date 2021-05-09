import datetime
import unittest
from werkzeug.security import check_password_hash
from http import HTTPStatus
from app import messages
from app.api.email_utils import generate_confirmation_token
from app.api.dao.user import UserDAO
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.models.tasks_list import TasksListModel
from app.database.sqlalchemy_extension import db
from app.database.models.user import UserModel
from app.utils.enum_utils import MentorshipRelationState
from tests.base_test_case import BaseTestCase
from tests.test_data import user2


class TestUserDao(BaseTestCase):
    def test_dao_create_user(self):
        dao = UserDAO()
        data = dict(
            name="UserB",
            username="user2",
            email="user2@email.com",
            password="test_password",
            terms_and_conditions_checked=True,
        )
        dao.create_user(data)

        # Verify that user was inserted in database through DAO
        user = UserModel.query.filter_by(email="user2@email.com").first()
        self.assertTrue(user is not None)
        self.assertTrue(user.id is not None)
        self.assertTrue(user.name == "UserB")
        self.assertTrue(user.username == "user2")
        self.assertTrue(user.email == "user2@email.com")
        self.assertFalse(user.is_admin)
        self.assertFalse(user.password_hash == "test_password")
        self.assertTrue(check_password_hash(user.password_hash, "test_password"))
        self.assertTrue(user.terms_and_conditions_checked)
        self.assertIsInstance(user.registration_date, float)
        self.assertFalse(user.is_email_verified)

    def test_dao_confirm_registration_good_token(self):
        dao = UserDAO()

        user = UserModel(
            name=user2["name"],
            email=user2["email"],
            username=user2["username"],
            password=user2["password"],
            terms_and_conditions_checked=user2["terms_and_conditions_checked"],
        )
        db.session.add(user)
        db.session.commit()

        # Verify that user was inserted in database through DAO
        user = UserModel.query.filter_by(email=user2["email"]).first()
        self.assertIsNotNone(user)

        good_token = generate_confirmation_token(user2["email"])

        self.assertFalse(user.is_email_verified)

        actual_result = dao.confirm_registration(good_token)

        self.assertTrue(user.is_email_verified)
        self.assertIsNotNone(user.email_verification_date)
        self.assertEqual(
            (messages.ACCOUNT_ALREADY_CONFIRMED_AND_THANKS, HTTPStatus.OK),
            actual_result,
        )

    def test_dao_confirm_registration_bad_token(self):
        dao = UserDAO()

        user = UserModel(
            name=user2["name"],
            email=user2["email"],
            username=user2["username"],
            password=user2["password"],
            terms_and_conditions_checked=user2["terms_and_conditions_checked"],
        )
        db.session.add(user)
        db.session.commit()

        # Verify that user was inserted in database through DAO
        user = UserModel.query.filter_by(email=user2["email"]).first()
        self.assertIsNotNone(user)

        # bad token because it is incomplete
        bad_token = generate_confirmation_token(user2["email"])[:4]

        self.assertFalse(user.is_email_verified)

        actual_result = dao.confirm_registration(bad_token)

        self.assertFalse(user.is_email_verified)
        self.assertIsNone(user.email_verification_date)
        self.assertEqual(
            (messages.EMAIL_EXPIRED_OR_TOKEN_IS_INVALID, HTTPStatus.BAD_REQUEST),
            actual_result,
        )

    def test_dao_confirm_registration_of_already_verified_user(self):
        dao = UserDAO()

        user = UserModel(
            name=user2["name"],
            email=user2["email"],
            username=user2["username"],
            password=user2["password"],
            terms_and_conditions_checked=user2["terms_and_conditions_checked"],
        )
        db.session.add(user)
        db.session.commit()

        # Verify that user was inserted in database through DAO
        user = UserModel.query.filter_by(email=user2["email"]).first()
        self.assertIsNotNone(user)
        user.is_email_verified = True
        db.session.add(user)
        db.session.commit()

        self.assertTrue(user.is_email_verified)
        good_token = generate_confirmation_token(user2["email"])
        actual_result = dao.confirm_registration(good_token)

        self.assertTrue(user.is_email_verified)
        self.assertEqual(
            (messages.ACCOUNT_ALREADY_CONFIRMED, HTTPStatus.OK), actual_result
        )

    def test_dao_delete_only_user_admin(self):
        dao = UserDAO()

        before_delete_user = UserModel.query.filter_by(id=1).first()
        self.assertIsNotNone(before_delete_user)
        self.assertTrue(before_delete_user.is_admin)

        dao_result = dao.delete_user(1)

        # Verify that user was inserted in database through DAO
        after_delete_user = UserModel.query.filter_by(id=1).first()
        self.assertTrue(after_delete_user.is_admin)
        self.assertIsNotNone(after_delete_user)
        self.assertEqual(1, after_delete_user.id)
        self.assertEqual(
            (messages.USER_CANT_DELETE, HTTPStatus.BAD_REQUEST), dao_result
        )

    def test_get_achievements(self):
        dao = UserDAO()

        mentor = UserModel(
            "Test mentor", "test_mentor", "test_password", "mentor@email.com", True
        )

        mentee = UserModel(
            "Test mentee", "test_mentee", "test_password", "mentee@email.com", True
        )

        mentor.is_email_verified = True
        mentor.available_to_mentor = True
        mentee.is_email_verified = True
        mentee.need_mentoring = True

        db.session.add(mentor)
        db.session.add(mentee)
        db.session.commit()

        start_date = datetime.datetime.utcnow()
        end_date = start_date + datetime.timedelta(weeks=4)

        tasks_list = TasksListModel()
        tasks_list.add_task(
            description="Test Task",
            created_at=start_date.timestamp(),
            is_done=True,
            completed_at=end_date.timestamp(),
        )
        tasks_list.add_task(
            description="Test Task 2",
            created_at=start_date.timestamp(),
            is_done=True,
            completed_at=end_date.timestamp(),
        )

        relation = MentorshipRelationModel(
            action_user_id=mentee.id,
            mentor_user=mentor,
            mentee_user=mentee,
            creation_date=start_date.timestamp(),
            end_date=end_date.timestamp(),
            state=MentorshipRelationState.ACCEPTED,
            tasks_list=tasks_list,
            notes="Test Notes",
        )

        db.session.add(tasks_list)
        db.session.add(relation)
        db.session.commit()

        achievements = dao.get_achievements(mentee.id)

        self.assertEqual(2, len(achievements))

        for achievement in achievements:
            self.assertTrue(achievement.get("is_done"))

    def test_get_user_statistics(self):
        dao = UserDAO()

        mentor = UserModel(
            "Test mentor", "test_mentor", "__test__", "mentor@email.com", True
        )

        mentee = UserModel(
            "Test mentee", "test_mentee", "__test__", "mentee@email.com", True
        )

        mentor.is_email_verified = True
        mentor.available_to_mentor = True
        mentee.is_email_verified = True
        mentee.need_mentoring = True

        db.session.add(mentor)
        db.session.add(mentee)
        db.session.commit()

        start_date = datetime.datetime.utcnow()
        end_date = start_date + datetime.timedelta(weeks=4)

        tasks_list = TasksListModel()

        pending_relation = MentorshipRelationModel(
            action_user_id=mentee.id,
            mentor_user=mentor,
            mentee_user=mentee,
            creation_date=start_date.timestamp(),
            end_date=end_date.timestamp(),
            state=MentorshipRelationState.PENDING,
            tasks_list=tasks_list,
            notes="Test Notes",
        )

        db.session.add(tasks_list)
        db.session.add(pending_relation)
        db.session.commit()

        # We first test pending relations
        expected_response = {
            "name": mentor.name,
            "pending_requests": 1,
            "accepted_requests": 0,
            "rejected_requests": 0,
            "completed_relations": 0,
            "cancelled_relations": 0,
            "achievements": [],
        }

        actual_response = dao.get_user_statistics(mentor.id)
        self.assertEqual(expected_response, actual_response)

        # We now test accepted relations
        pending_relation.state = MentorshipRelationState.ACCEPTED
        expected_response["pending_requests"] = 0
        expected_response["accepted_requests"] = 1

        actual_response = dao.get_user_statistics(mentor.id)
        self.assertEqual(expected_response, actual_response)

        # We now test completed relations
        pending_relation.state = MentorshipRelationState.COMPLETED
        expected_response["accepted_requests"] = 0
        expected_response["completed_relations"] = 1

        actual_response = dao.get_user_statistics(mentor.id)
        self.assertEqual(expected_response, actual_response)

        # We now test rejected relations
        pending_relation.state = MentorshipRelationState.REJECTED
        expected_response["completed_relations"] = 0
        expected_response["rejected_requests"] = 1

        actual_response = dao.get_user_statistics(mentor.id)
        self.assertEqual(expected_response, actual_response)

        # We now test cancelled relations
        pending_relation.state = MentorshipRelationState.CANCELLED
        expected_response["rejected_requests"] = 0
        expected_response["cancelled_relations"] = 1

        actual_response = dao.get_user_statistics(mentor.id)
        self.assertEqual(expected_response, actual_response)

        # We now test achievements
        pending_relation.state = MentorshipRelationState.ACCEPTED
        tasks_list.add_task(
            description="Test Task",
            created_at=start_date.timestamp(),
            is_done=True,
            completed_at=end_date.timestamp(),
        )
        tasks_list.add_task(
            description="Test Task 2",
            created_at=start_date.timestamp(),
            is_done=True,
            completed_at=end_date.timestamp(),
        )

        expected_response["cancelled_relations"] = 0
        expected_response["accepted_requests"] = 1
        expected_response["achievements"] = [
            {
                "completed_at": end_date.timestamp(),
                "created_at": start_date.timestamp(),
                "description": "Test Task",
                "id": 1,  # This is the first task in the list
                "is_done": True,
            },
            {
                "completed_at": end_date.timestamp(),
                "created_at": start_date.timestamp(),
                "description": "Test Task 2",
                "id": 2,  # This is the second task in the list
                "is_done": True,
            },
        ]
        actual_response = dao.get_user_statistics(mentor.id)
        self.assertEqual(expected_response, actual_response)


if __name__ == "__main__":
    unittest.main()
