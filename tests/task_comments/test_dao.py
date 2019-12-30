import json
import unittest

from app import messages
from app.api.dao.task_model import TaskCommentDAO
from tests.tasks.tasks_base_setup import TasksBaseTestCase


class TestTaskCommentDao(TasksBaseTestCase):

    def create_task_comment(self):
        dao = TaskCommentDAO()
        data = dict(
            user_id=1,
            task_id=1,
            comment='comment'
        )
        dao.create_task_comment(1, data)

    def test_dao_create_task_comment(self):
        self.create_task_comment()

        # Verify that task comment was inserted in database through DAO
        task_comment = TaskCommentDAO.get_task_comment(1, 1)[0]
        self.assertTrue(task_comment is not None)
        self.assertTrue(task_comment.id is not None)
        self.assertTrue(task_comment.task_id == 1)
        self.assertIsNotNone(task_comment.creation_date)
        self.assertEqual(task_comment.comment, 'comment')

    def test_dao_find_by_task_id(self):
        self.create_task_comment()

        # Verify that find_all_by_task_id() function is working properly
        task_comments = TaskCommentDAO.get_all_task_comments_by_task_id(
            1, 1)[0]
        task_comment = task_comments[0]
        self.assertEqual(len(task_comments), 1)
        self.assertTrue(task_comment is not None)
        self.assertTrue(task_comment.id is not None)
        self.assertTrue(task_comment.task_id == 1)
        self.assertIsNotNone(task_comment.creation_date)
        self.assertEqual(task_comment.comment, 'comment')

    def test_dao_find_by_user_id(self):
        self.create_task_comment()

        # Verify that find_all_by_user_id() function is working properly
        task_comments = TaskCommentDAO.get_all_task_comments_by_user_id(1)[0]
        task_comment = task_comments[0]
        self.assertEqual(len(task_comments), 1)
        self.assertTrue(task_comment is not None)
        self.assertTrue(task_comment.id is not None)
        self.assertTrue(task_comment.task_id == 1)
        self.assertIsNotNone(task_comment.creation_date)
        self.assertEqual(task_comment.comment, 'comment')

    def test_dao_modify_comment(self):
        self.create_task_comment()

        TaskCommentDAO.modify_comment(1, 1, 'modified comment')

        # Verify that task comment was modified
        task_comment = TaskCommentDAO.get_task_comment(1, 1)[0]
        self.assertTrue(task_comment is not None)
        self.assertTrue(task_comment.id is not None)
        self.assertTrue(task_comment.task_id == 1)
        self.assertIsNotNone(task_comment.creation_date)
        self.assertIsNotNone(task_comment.creation_date)
        self.assertEqual(task_comment.comment, 'modified comment')

    def test_dao_delete_comment(self):
        self.create_task_comment()

        TaskCommentDAO.delete_comment(1, 1)

        expected_response = messages.TASK_COMMENT_DOES_NOT_EXIST, 404
        actual_response = TaskCommentDAO.get_task_comment(1, 1)

        # Verify that task comment was deleted
        self.assertEqual(expected_response, actual_response)


if __name__ == '__main__':
    unittest.main()
