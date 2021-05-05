from flask import request
from flask_restx import Resource, Namespace, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from app import messages
from app.api.resources.common import auth_header_parser

from app.api.validations.task_comment import validate_task_comment_request_data
from app.api.dao.task_comment import TaskCommentDAO
from app.api.models.task_comment import *

task_comment_ns = Namespace(
    "Task comment",
    description="Operations related to comments between user",
)
add_models_to_namespace(task_comment_ns)


@task_comment_ns.route(
    "mentorship_relation/<int:relation_id>/task/<int:task_id>/comment"
)
class CreateTaskComment(Resource):
    @classmethod
    @jwt_required
    @task_comment_ns.expect(auth_header_parser, task_comment_model)
    @task_comment_ns.doc(
        responses={
            HTTPStatus.CREATED: f"{messages.TASK_COMMENT_WAS_CREATED_SUCCESSFULLY}",
            HTTPStatus.BAD_REQUEST: f"{messages.COMMENT_FIELD_IS_MISSING}<br>"
            f"{messages.COMMENT_NOT_IN_STRING_FORMAT}<br>"
            f"{{'message': get_length_validation_error_message('comment', None, COMMENT_MAX_LENGTH)}}<br>"
            f"{messages.UNACCEPTED_STATE_RELATION}",
            HTTPStatus.UNAUTHORIZED: f"{messages.TOKEN_HAS_EXPIRED}<br>"
            f"{messages.TOKEN_IS_INVALID}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING}<br>"
            f"{messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION}",
            HTTPStatus.NOT_FOUND: f"{messages.USER_DOES_NOT_EXIST}<br>"
            f"{messages.MENTORSHIP_RELATION_DOES_NOT_EXIST}<br>"
            f"{messages.TASK_DOES_NOT_EXIST}",
        }
    )
    def post(cls, relation_id, task_id):
        """
        Creates a new task comment.
        """

        data = request.json

        is_valid = validate_task_comment_request_data(data)
        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST

        comment = data["comment"]
        return TaskCommentDAO.create_task_comment(
            get_jwt_identity(), task_id, relation_id, comment
        )


@task_comment_ns.route(
    "mentorship_relation/<int:relation_id>/task/<int:task_id>/comment/<int:comment_id>"
)
class TaskComment(Resource):
    @classmethod
    @jwt_required
    @task_comment_ns.expect(auth_header_parser, task_comment_model)
    @task_comment_ns.doc(
        responses={
            HTTPStatus.OK: f"{messages.TASK_COMMENT_WAS_UPDATED_SUCCESSFULLY}",
            HTTPStatus.BAD_REQUEST: f"{messages.COMMENT_FIELD_IS_MISSING}<br>"
            f"{messages.COMMENT_NOT_IN_STRING_FORMAT}<br>"
            f"{{'message': get_length_validation_error_message('comment', None, COMMENT_MAX_LENGTH)}}<br>"
            f"{messages.UNACCEPTED_STATE_RELATION}<br>"
            f"{messages.TASK_COMMENT_WAS_NOT_CREATED_BY_YOU}",
            HTTPStatus.UNAUTHORIZED: f"{messages.TOKEN_HAS_EXPIRED}<br>"
            f"{messages.TOKEN_IS_INVALID}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING}<br>"
            f"{messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION}",
            HTTPStatus.NOT_FOUND: f"{messages.USER_DOES_NOT_EXIST}<br>"
            f"{messages.MENTORSHIP_RELATION_DOES_NOT_EXIST}<br>"
            f"{messages.TASK_DOES_NOT_EXIST}<br>"
            f"{messages.TASK_COMMENT_DOES_NOT_EXIST}<br>"
            f"{messages.TASK_COMMENT_WITH_GIVEN_TASK_ID_DOES_NOT_EXIST}",
        }
    )
    def put(cls, relation_id, task_id, comment_id):
        """
        Modifies the task comment.
        """

        data = request.json

        is_valid = validate_task_comment_request_data(data)
        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST

        comment = data["comment"]
        return TaskCommentDAO.modify_comment(
            get_jwt_identity(), comment_id, task_id, relation_id, comment
        )

    @classmethod
    @jwt_required
    @task_comment_ns.expect(auth_header_parser)
    @task_comment_ns.doc(
        responses={
            HTTPStatus.OK: f"{messages.TASK_COMMENT_WAS_DELETED_SUCCESSFULLY}",
            HTTPStatus.BAD_REQUEST: f"{messages.UNACCEPTED_STATE_RELATION}",
            HTTPStatus.UNAUTHORIZED: f"{messages.TOKEN_HAS_EXPIRED}<br>"
            f"{messages.TOKEN_IS_INVALID}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING}<br>"
            f"{messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION}",
            HTTPStatus.FORBIDDEN: f"{messages.TASK_COMMENT_WAS_NOT_CREATED_BY_YOU_DELETE}",
            HTTPStatus.NOT_FOUND: f"{messages.USER_DOES_NOT_EXIST}<br>"
            f"{messages.MENTORSHIP_RELATION_DOES_NOT_EXIST}<br>"
            f"{messages.TASK_DOES_NOT_EXIST}<br>"
            f"{messages.TASK_COMMENT_DOES_NOT_EXIST}<br>"
            f"{messages.TASK_COMMENT_WITH_GIVEN_TASK_ID_DOES_NOT_EXIST}",
        }
    )
    def delete(cls, relation_id, task_id, comment_id):
        """
        Deletes the task comment.
        """

        return TaskCommentDAO.delete_comment(
            get_jwt_identity(), comment_id, task_id, relation_id
        )


@task_comment_ns.route(
    "mentorship_relation/<int:relation_id>/task/<int:task_id>/comments/"
)
class TaskComments(Resource):
    @classmethod
    @jwt_required
    @task_comment_ns.expect(auth_header_parser)
    @task_comment_ns.response(
        HTTPStatus.OK,
        f"{messages.LIST_TASK_COMMENTS_WITH_SUCCESS}",
        task_comments_model,
    )
    @task_comment_ns.doc(
        responses={
            HTTPStatus.FORBIDDEN: f"{messages.UNACCEPTED_STATE_RELATION}",
            HTTPStatus.UNAUTHORIZED: f"{messages.TOKEN_HAS_EXPIRED}<br>"
            f"{messages.TOKEN_IS_INVALID}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING}<br>"
            f"{messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION}",
            HTTPStatus.NOT_FOUND: f"{messages.USER_DOES_NOT_EXIST}<br>"
            f"{messages.MENTORSHIP_RELATION_DOES_NOT_EXIST}<br>"
            f"{messages.TASK_DOES_NOT_EXIST}",
        }
    )
    def get(cls, relation_id, task_id):
        """
        Lists the task comments.
        """

        response = TaskCommentDAO.get_all_task_comments_by_task_id(
            get_jwt_identity(), task_id, relation_id
        )

        if isinstance(response, tuple):
            return response
        else:
            return marshal(response, task_comments_model), HTTPStatus.OK
