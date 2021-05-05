from flask import request
from flask_restx import Resource, Namespace, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus

from app import messages
from app.api.dao.task import TaskDAO
from app.api.resources.common import auth_header_parser
from app.api.models.task import *


task_ns = Namespace(
    "Task",
    description="Operations related to tasks for the mentee/mentor",
)
add_models_to_namespace(task_ns)


@task_ns.route("mentorship_relation/<int:relation_id>/task")
class CreateTask(Resource):
    @classmethod
    @jwt_required
    @task_ns.doc("create_task_in_mentorship_relation")
    @task_ns.expect(auth_header_parser, create_task_request_body)
    @task_ns.response(HTTPStatus.CREATED, f"{messages.TASK_WAS_CREATED_SUCCESSFULLY}")
    @task_ns.response(HTTPStatus.FORBIDDEN, f"{messages.UNACCEPTED_STATE_RELATION}")
    @task_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    @task_ns.response(
        HTTPStatus.FORBIDDEN, f"{messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION}"
    )
    def post(cls, relation_id):
        """
        Create a task for a mentorship relation.

        Input:
        1. Header: valid access token
        2. Path: ID of request for which task is being created (relation_id)
        3. Body: JSON object containing description of task.

        Returns:
        Success or failure message. It gets added to GET /tasks endpoint and
        is visible to the other person in the mentorship relation.
        """

        # TODO check if user id is well parsed, if it is an integer

        user_id = get_jwt_identity()
        request_body = request.json

        is_valid = CreateTask.is_valid_data(request_body)

        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST

        response = TaskDAO.create_task(
            user_id=user_id, mentorship_relation_id=relation_id, data=request_body
        )

        return response

    @staticmethod
    def is_valid_data(data):

        if "description" not in data:
            return messages.DESCRIPTION_FIELD_IS_MISSING

        return {}


@task_ns.route("mentorship_relation/<int:relation_id>/task/<int:task_id>")
class DeleteTask(Resource):
    @classmethod
    @jwt_required
    @task_ns.doc("delete_task_in_mentorship_relation")
    @task_ns.expect(auth_header_parser)
    @task_ns.response(HTTPStatus.OK, f"{messages.TASK_WAS_DELETED_SUCCESSFULLY}")
    @task_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}\n"
        f"{messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION}",
    )
    @task_ns.response(
        HTTPStatus.NOT_FOUND,
        f"{messages.MENTORSHIP_RELATION_DOES_NOT_EXIST}\n"
        f"{messages.TASK_DOES_NOT_EXIST}",
    )
    def delete(cls, relation_id, task_id):
        """
        Delete a task.

        Input:
        1. Header: valid access token
        2. Path: ID of the task to be deleted (task_id) and it ID of the associated
        mentorship relation (relation_id).
        3. Body: JSON object containing description of task.

        Returns:
        Success or failure message. Task is deleted if request is successful.
        """

        # TODO check if user id is well parsed, if it is an integer

        user_id = get_jwt_identity()

        response = TaskDAO.delete_task(
            user_id=user_id, mentorship_relation_id=relation_id, task_id=task_id
        )

        return response


@task_ns.route("mentorship_relation/<int:relation_id>/tasks")
class ListTasks(Resource):
    @classmethod
    @jwt_required
    @task_ns.doc("list_tasks_in_mentorship_relation")
    @task_ns.expect(auth_header_parser)
    @task_ns.response(
        HTTPStatus.OK,
        "List tasks from a mentorship relation with success.",
        model=list_tasks_response_body,
    )
    @task_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}\n"
        f"{messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION}",
    )
    @task_ns.response(
        HTTPStatus.NOT_FOUND, f"{messages.MENTORSHIP_RELATION_DOES_NOT_EXIST}"
    )
    def get(cls, relation_id):
        """
        List all tasks from a mentorship relation.

        Input:
        1. Header: valid access token
        2. Path: ID of the mentorship relation for which tasks are to be
        displayed(relation_id). The user must be involved in this relation.

        Returns:
        JSON array containing task details as objects is displayed on success.
        """

        # TODO check if user id is well parsed, if it is an integer

        user_id = get_jwt_identity()

        response = TaskDAO.list_tasks(
            user_id=user_id, mentorship_relation_id=relation_id
        )

        if isinstance(response, tuple):
            return response

        return marshal(response, list_tasks_response_body), HTTPStatus.OK


@task_ns.route("mentorship_relation/<int:relation_id>/task/<int:task_id>/complete")
class UpdateTask(Resource):
    @classmethod
    @jwt_required
    @task_ns.doc("update_task_in_mentorship_relation")
    @task_ns.expect(auth_header_parser)
    @task_ns.response(HTTPStatus.OK, f"{messages.TASK_WAS_ACHIEVED_SUCCESSFULLY}")
    @task_ns.response(HTTPStatus.CONFLICT, f"{messages.TASK_WAS_ALREADY_ACHIEVED}")
    @task_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}\n"
        f"{messages.USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION}",
    )
    @task_ns.response(
        HTTPStatus.NOT_FOUND,
        f"{messages.MENTORSHIP_RELATION_DOES_NOT_EXIST}\n{messages.TASK_DOES_NOT_EXIST}",
    )
    def put(cls, relation_id, task_id):
        """
        Update a task to mark it as complate

        Input:
        1. Header: valid access token
        2. Path: ID of task (task_id) and ID of the associated mentorship
        relation (relation_id). The user must be involved in this relation.
        3. Body:

        Returns:
        Success or failure message. The task is marked as complete if succesful.
        """

        # TODO check if user id is well parsed, if it is an integer

        user_id = get_jwt_identity()

        response = TaskDAO.complete_task(
            user_id=user_id, mentorship_relation_id=relation_id, task_id=task_id
        )

        return response
