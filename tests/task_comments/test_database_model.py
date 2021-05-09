from app.database.models.task_comment import TaskCommentModel
from tests.base_test_case import BaseTestCase


class TestTaskCommentModel(BaseTestCase):
    def test_task_validations_comment(self):
        self.assertRaises(
            AssertionError,
            TaskCommentModel,
            user_id=1,
            task_id=1,
            relation_id=1,
            comment="",
        )

    def test_task_validations_comment_strip(self):
        comment = TaskCommentModel(
            user_id=1, task_id=1, relation_id=1, comment=" user "
        )
        self.assertEqual(comment.comment, "user")
