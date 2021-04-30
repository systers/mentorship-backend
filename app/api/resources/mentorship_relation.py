from flask import request
from flask_restx import Resource, Namespace, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus

from app import messages
from app.api.resources.common import auth_header_parser
from app.api.dao.mentorship_relation import MentorshipRelationDAO
from app.api.dao.user import UserDAO
from app.api.models.mentorship_relation import *
from app.database.models.mentorship_relation import MentorshipRelationModel
from app.api.email_utils import send_email_mentorship_relation_accepted
from app.api.email_utils import send_email_new_request

mentorship_relation_ns = Namespace(
    "Mentorship Relation",
    description="Operations related to " "mentorship relations " "between users",
)
add_models_to_namespace(mentorship_relation_ns)

DAO = MentorshipRelationDAO()
userDAO = UserDAO()


@mentorship_relation_ns.route("mentorship_relation/send_request")
class SendRequest(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("send_request")
    @mentorship_relation_ns.expect(auth_header_parser, send_mentorship_request_body)
    @mentorship_relation_ns.response(
        HTTPStatus.CREATED, f"{messages.MENTORSHIP_RELATION_WAS_SENT_SUCCESSFULLY}"
    )
    @mentorship_relation_ns.response(
        HTTPStatus.BAD_REQUEST,
        f"{messages.MATCH_EITHER_MENTOR_OR_MENTEE}\n"
        f"{messages.MENTOR_ID_SAME_AS_MENTEE_ID}\n"
        f"{messages.END_TIME_BEFORE_PRESENT}\n"
        f"{messages.MENTOR_TIME_GREATER_THAN_MAX_TIME}\n"
        f"{messages.MENTOR_TIME_LESS_THAN_MIN_TIME}\n"
        f"{messages.MENTOR_NOT_AVAILABLE_TO_MENTOR}\n"
        f"{messages.MENTEE_NOT_AVAIL_TO_BE_MENTORED}\n"
        f"{messages.MENTOR_ALREADY_IN_A_RELATION}\n"
        f"{messages.MENTEE_ALREADY_IN_A_RELATION}\n"
        f"{messages.MENTOR_ID_FIELD_IS_MISSING}\n"
        f"{messages.MENTEE_ID_FIELD_IS_MISSING}\n"
        f"{messages.NOTES_FIELD_IS_MISSING}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.NOT_FOUND,
        f"{messages.MENTOR_DOES_NOT_EXIST}\n" f"{messages.MENTEE_DOES_NOT_EXIST}",
    )
    def post(cls):
        """
        Creates a new mentorship relation request.

        Also, sends an email notification to the recipient about new relation request.

        Input:
        1. Header: valid access token
        2. Body: A dict containing
        - mentor_id, mentee_id: One of them must contain user ID
        - end_date: UNIX timestamp
        - notes: description of relation request

        Returns:
        Success or failure message. A mentorship request is send to the other
        person whose ID is mentioned. The relation appears at /pending endpoint.
        """

        data = request.json
        user_sender_id = get_jwt_identity()

        is_valid = SendRequest.is_valid_data(data)

        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST

        response = DAO.create_mentorship_relation(user_sender_id, data)

        # if the mentorship relation creation failed dont send email and return
        if response[1] != HTTPStatus.CREATED.value:
            return response

        if user_sender_id == data["mentee_id"]:
            sender_role = "mentee"
            user_recipient_id = data["mentor_id"]
        else:
            sender_role = "mentor"
            user_recipient_id = data["mentee_id"]

        user_sender = userDAO.get_user(user_sender_id)
        user_recipient = userDAO.get_user(user_recipient_id)
        notes = data["notes"]

        send_email_new_request(user_sender, user_recipient, notes, sender_role)

        return response

    @staticmethod
    def is_valid_data(data):

        # Verify if request body has required fields
        if "mentor_id" not in data:
            return messages.MENTOR_ID_FIELD_IS_MISSING
        if "mentee_id" not in data:
            return messages.MENTEE_ID_FIELD_IS_MISSING
        if "end_date" not in data:
            return messages.END_DATE_FIELD_IS_MISSING
        if "notes" not in data:
            return messages.NOTES_FIELD_IS_MISSING

        return {}


@mentorship_relation_ns.route("mentorship_relations")
class GetAllMyMentorshipRelation(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("get_all_user_mentorship_relations")
    @mentorship_relation_ns.expect(auth_header_parser)
    @mentorship_relation_ns.param(
        name="relation_state",
        description="Mentorship relation state filter.",
        _in="query",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.OK.value,
        "Return all user's mentorship relations, filtered by the relation state, was successfully.",
        model=mentorship_request_response_body,
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    @mentorship_relation_ns.marshal_list_with(
        mentorship_request_response_body,
        code=HTTPStatus.OK.value,
        description="Success",
    )
    def get(cls):
        """
        Lists all mentorship relations of current user.

        Input:
        1. Header: valid access token

        Returns:
        JSON array containing user's relations as objects.
        """

        user_id = get_jwt_identity()
        rel_state_param = request.args
        rel_state_filter = None

        if rel_state_param:
            rel_state_filter = rel_state_param["relation_state"].upper()

        response = DAO.list_mentorship_relations(
            user_id=user_id, state=rel_state_filter
        )

        return response


@mentorship_relation_ns.route("mentorship_relation/<int:request_id>/accept")
class AcceptMentorshipRelation(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("accept_mentorship_relation")
    @mentorship_relation_ns.expect(auth_header_parser)
    @mentorship_relation_ns.response(
        HTTPStatus.OK, f"{messages.MENTORSHIP_RELATION_WAS_ACCEPTED_SUCCESSFULLY}"
    )
    @mentorship_relation_ns.response(
        HTTPStatus.FORBIDDEN,
        f"{messages.NOT_PENDING_STATE_RELATION}\n"
        f"{messages.CANT_ACCEPT_MENTOR_REQ_SENT_BY_USER}\n"
        f"{messages.CANT_ACCEPT_UNINVOLVED_MENTOR_RELATION}\n"
        f"{messages.USER_IS_INVOLVED_IN_A_MENTORSHIP_RELATION}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.NOT_FOUND, f"{messages.MENTORSHIP_RELATION_REQUEST_DOES_NOT_EXIST}"
    )
    def put(cls, request_id):
        """
        Accept a mentorship relation.

        Input:
        1. Header: valid access token
        2. Path: ID of request which is to be accepted (request_id)

        Returns:
        Success or failure message.
        """

        # check if user id is well parsed
        # if it is an integer

        user_id = get_jwt_identity()
        response = DAO.accept_request(user_id=user_id, request_id=request_id)

        if response[1] == HTTPStatus.OK.value:
            send_email_mentorship_relation_accepted(request_id)

        return response


@mentorship_relation_ns.route("mentorship_relation/<int:request_id>/reject")
class RejectMentorshipRelation(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("reject_mentorship_relation")
    @mentorship_relation_ns.expect(auth_header_parser)
    @mentorship_relation_ns.response(
        HTTPStatus.OK, f"{messages.MENTORSHIP_RELATION_WAS_REJECTED_SUCCESSFULLY}"
    )
    @mentorship_relation_ns.response(
        HTTPStatus.FORBIDDEN,
        f"{messages.NOT_PENDING_STATE_RELATION}\n"
        f"{messages.USER_CANT_REJECT_REQUEST_SENT_BY_USER}\n"
        f"{messages.CANT_REJECT_UNINVOLVED_RELATION_REQUEST}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.NOT_FOUND, f"{messages.MENTORSHIP_RELATION_REQUEST_DOES_NOT_EXIST}"
    )
    def put(cls, request_id):
        """
        Reject a mentorship relation.

        Input:
        1. Header: valid access token
        2. Path: ID of request which is to be rejected (request_id)

        Returns:
        Success or failure message.
        """

        # TODO check if user id is well parsed, if it is an integer

        user_id = get_jwt_identity()
        response = DAO.reject_request(user_id=user_id, request_id=request_id)

        return response


@mentorship_relation_ns.route("mentorship_relation/<int:request_id>/cancel")
class CancelMentorshipRelation(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("cancel_mentorship_relation")
    @mentorship_relation_ns.expect(auth_header_parser)
    @mentorship_relation_ns.response(
        HTTPStatus.OK, f"{messages.MENTORSHIP_RELATION_WAS_CANCELLED_SUCCESSFULLY}"
    )
    @mentorship_relation_ns.response(
        HTTPStatus.BAD_REQUEST,
        f"{messages.UNACCEPTED_STATE_RELATION}\n"
        f"{messages.CANT_CANCEL_UNINVOLVED_REQUEST}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.NOT_FOUND, f"{messages.MENTORSHIP_RELATION_REQUEST_DOES_NOT_EXIST}"
    )
    def put(cls, request_id):
        """
        Cancel a mentorship relation.

        Input:
        1. Header: valid access token
        2. Path: ID of request which is to be cancelled (request_id)

        Returns:
        Success or failure message.
        """

        # TODO check if user id is well parsed, if it is an integer

        user_id = get_jwt_identity()
        response = DAO.cancel_relation(user_id=user_id, relation_id=request_id)

        return response


@mentorship_relation_ns.route("mentorship_relation/<int:request_id>")
class DeleteMentorshipRelation(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("delete_mentorship_relation")
    @mentorship_relation_ns.expect(auth_header_parser)
    @mentorship_relation_ns.response(
        HTTPStatus.OK, f"{messages.MENTORSHIP_RELATION_WAS_DELETED_SUCCESSFULLY}"
    )
    @mentorship_relation_ns.response(
        HTTPStatus.FORBIDDEN,
        f"{messages.NOT_PENDING_STATE_RELATION}\n"
        f"{messages.CANT_DELETE_UNINVOLVED_REQUEST}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.NOT_FOUND, f"{messages.MENTORSHIP_RELATION_REQUEST_DOES_NOT_EXIST}"
    )
    def delete(cls, request_id):
        """
        Delete a mentorship request.

        Input:
        1. Header: valid access token
        2. Path: ID of request which is to be deleted (request_id)

        Returns:
        Success or failure message.
        """

        # TODO check if user id is well parsed, if it is an integer

        user_id = get_jwt_identity()
        response = DAO.delete_request(user_id=user_id, request_id=request_id)

        return response


@mentorship_relation_ns.route("mentorship_relations/past")
class ListPastMentorshipRelations(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("get_past_mentorship_relations")
    @mentorship_relation_ns.expect(auth_header_parser)
    @mentorship_relation_ns.response(
        HTTPStatus.OK.value,
        "Returned past mentorship relations with success.",
        model=mentorship_request_response_body,
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    @mentorship_relation_ns.marshal_list_with(
        mentorship_request_response_body,
        code=HTTPStatus.OK.value,
        description="Success",
    )
    def get(cls):
        """
        Lists past mentorship relations of the current user.

        Input:
        1. Header: valid access token

        Returns:
        JSON array containing details of past mentorship relations as objects.
        """

        user_id = get_jwt_identity()
        response = DAO.list_past_mentorship_relations(user_id)

        return response


@mentorship_relation_ns.route("mentorship_relations/current")
class ListCurrentMentorshipRelation(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("get_current_mentorship_relation")
    @mentorship_relation_ns.expect(auth_header_parser)
    @mentorship_relation_ns.response(
        HTTPStatus.OK.value,
        "Returned current mentorship relation with success.",
        model=mentorship_request_response_body,
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    def get(cls):
        """
        Lists current mentorship relation of the current user.

        Input:
        1. Header: valid access token

        Returns:
        JSON array containing details of current mentorship relations as objects.
        """

        user_id = get_jwt_identity()
        response = DAO.list_current_mentorship_relation(user_id)

        if isinstance(response, MentorshipRelationModel):
            return (
                marshal(response, mentorship_request_response_body),
                HTTPStatus.OK,
            )

        return response


@mentorship_relation_ns.route("mentorship_relations/pending")
class ListPendingMentorshipRequests(Resource):
    @classmethod
    @jwt_required()
    @mentorship_relation_ns.doc("get_pending_mentorship_relations")
    @mentorship_relation_ns.expect(auth_header_parser)
    @mentorship_relation_ns.response(
        HTTPStatus.OK.value,
        "Returned pending mentorship relation with success.",
        model=mentorship_request_response_body,
    )
    @mentorship_relation_ns.marshal_list_with(
        mentorship_request_response_body,
        code=HTTPStatus.OK.value,
        description="Success",
    )
    @mentorship_relation_ns.response(
        HTTPStatus.UNAUTHORIZED,
        f"{messages.TOKEN_HAS_EXPIRED}\n"
        f"{messages.TOKEN_IS_INVALID}\n"
        f"{messages.AUTHORISATION_TOKEN_IS_MISSING}",
    )
    def get(cls):
        """
        Lists pending mentorship requests of the current user.

        Input:
        1. Header: valid access token

        Returns:
        JSON array containing details of pending mentorship relations as objects.
        """

        user_id = get_jwt_identity()
        response = DAO.list_pending_mentorship_relations(user_id)

        return response
