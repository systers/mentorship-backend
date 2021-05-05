from app import messages
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.database.models.task_comment import TaskCommentModel
from app.utils.decorator_utils import email_verification_required
from app.utils.enum_utils import MentorshipRelationState
from http import HTTPStatus


def validate_data_for_task_comment(user_id, task_id, relation_id):
    relation = MentorshipRelationModel.find_by_id(relation_id)
    if relation is None:
        return messages.MENTORSHIP_RELATION_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND

    if user_id != relation.mentor_id and user_id != relation.mentee_id:
        return (
            messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION,
            HTTPStatus.UNAUTHORIZED,
        )

    if relation.state != MentorshipRelationState.ACCEPTED:
        return messages.UNACCEPTED_STATE_RELATION, HTTPStatus.FORBIDDEN

    task = relation.tasks_list.find_task_by_id(task_id)
    if task is None:
        return messages.TASK_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND

    return {}


class TaskCommentDAO:
    """Data Access Object for task comment functionalities."""

    @staticmethod
    @email_verification_required
    def create_task_comment(user_id, task_id, relation_id, comment):
        """Creates a new task comment.

        Creates a new task comment with provided data.

        Arguments:
            user_id: The id of the user.
            task_id: The id of the task.
            relation_id: The id of the relation.
            comment: A string containing the comment.

        Returns:
            A tuple with two elements.
            The first element is a dictionary containing a key 'message'
            containing a string which indicates whether or not the task comment
            was created successfully.
            The second is the HTTP response code.
        """

        is_valid = validate_data_for_task_comment(user_id, task_id, relation_id)
        if is_valid != {}:
            return is_valid

        task_comment = TaskCommentModel(user_id, task_id, relation_id, comment)
        task_comment.save_to_db()

        return messages.TASK_COMMENT_WAS_CREATED_SUCCESSFULLY, HTTPStatus.CREATED

    @staticmethod
    @email_verification_required
    def get_task_comment(user_id, _id):
        """Returns the task comment suing specified id.

        Arguments:
            user_id: The id of the user.
            _id: The id of the task comment.

        Returns:
            A tuple with two elements.
            The task comment that has given id and the HTTP response code.
        """

        task_comment = TaskCommentModel.find_by_id(_id)

        if task_comment:
            return task_comment, HTTPStatus.OK

        return messages.TASK_COMMENT_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND

    @staticmethod
    @email_verification_required
    def get_all_task_comments_by_task_id(user_id, task_id, relation_id):
        """Returns all the task comments using specified task id.

        Arguments:
            user_id: The id of the user.
            task_id: The id of the task.
            relation_id: The id of the relation.

        Returns:
            A tuple with two elements.
            The list of task comments that have given task id
            and the HTTP response code.
        """

        is_valid = validate_data_for_task_comment(user_id, task_id, relation_id)
        if is_valid != {}:
            return is_valid

        comments_list = TaskCommentModel.find_all_by_task_id(task_id, relation_id)
        return [comment.json() for comment in comments_list]

    @staticmethod
    @email_verification_required
    def get_all_task_comments_by_user_id(user_id):
        """Returns all the task comments using specified user id.

        Arguments:
            user_id: The id of the user.

        Returns:
            A tuple with two elements.
            The list of task comments that have given user id
            and the HTTP response code.
        """

        return TaskCommentModel.find_all_by_user_id(user_id), HTTPStatus.OK

    @staticmethod
    @email_verification_required
    def modify_comment(user_id, _id, task_id, relation_id, comment):
        """Modifies comment to a new one.

        Arguments:
            user_id: The id of the user.
            _id: The id of the task comment.
            task_id: The id of the task.
            relation_id: The id of the relation.
            comment: New comment.

        Returns:
            A tuple with two elements.
            The first element is a dictionary containing a key 'message'
            containing a string which indicates whether or not the task comment
            was updated successfully.
            The second is the HTTP response code.
        """

        is_valid = validate_data_for_task_comment(user_id, task_id, relation_id)
        if is_valid != {}:
            return is_valid

        task_comment = TaskCommentModel.find_by_id(_id)

        if task_comment is None:
            return messages.TASK_COMMENT_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND

        if task_comment.user_id != user_id:
            return messages.TASK_COMMENT_WAS_NOT_CREATED_BY_YOU, HTTPStatus.FORBIDDEN

        if task_comment.task_id != task_id:
            return (
                messages.TASK_COMMENT_WITH_GIVEN_TASK_ID_DOES_NOT_EXIST,
                HTTPStatus.NOT_FOUND,
            )

        task_comment.modify_comment(comment)
        task_comment.save_to_db()

        return messages.TASK_COMMENT_WAS_UPDATED_SUCCESSFULLY, HTTPStatus.OK

    @staticmethod
    @email_verification_required
    def delete_comment(user_id, _id, task_id, relation_id):
        """Deletes comment specified by id.

        Arguments:
            user_id: The id of the user.
            _id: The id of the task comment.
            task_id: The id of the task.
            relation_id: The id of the relation.

        Returns:
            A tuple with two elements.
            The first element is a dictionary containing a key 'message'
            containing a string which indicates whether or not the task comment
            was deleted successfully.
            The second is the HTTP response code.
        """

        is_valid = validate_data_for_task_comment(user_id, task_id, relation_id)
        if is_valid != {}:
            return is_valid

        task_comment = TaskCommentModel.find_by_id(_id)

        if task_comment is None:
            return messages.TASK_COMMENT_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND

        if task_comment.user_id != user_id:
            return (
                messages.TASK_COMMENT_WAS_NOT_CREATED_BY_YOU_DELETE,
                HTTPStatus.FORBIDDEN,
            )

        if task_comment.task_id != task_id:
            return (
                messages.TASK_COMMENT_WITH_GIVEN_TASK_ID_DOES_NOT_EXIST,
                HTTPStatus.NOT_FOUND,
            )

        task_comment.delete_from_db()
        return messages.TASK_COMMENT_WAS_DELETED_SUCCESSFULLY, HTTPStatus.OK
