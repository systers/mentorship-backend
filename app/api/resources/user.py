from datetime import datetime
from http import HTTPStatus
from flask import request
from flask_jwt_extended import (
    jwt_required,
    jwt_refresh_token_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from flask_restx import Resource, marshal, Namespace

from app import messages
from app.api.validations.user import *
from app.api.email_utils import send_email_verification_message
from app.api.models.user import *
from app.api.dao.user import UserDAO
from app.api.resources.common import auth_header_parser, refresh_auth_header_parser

users_ns = Namespace("Users", description="Operations related to users")
add_models_to_namespace(users_ns)

DAO = UserDAO()  # User data access object


@users_ns.route("users")
@users_ns.response(
    HTTPStatus.UNAUTHORIZED.value,
    "%s\n%s\n%s"
    % (
        messages.TOKEN_HAS_EXPIRED,
        messages.TOKEN_IS_INVALID,
        messages.AUTHORISATION_TOKEN_IS_MISSING,
    ),
)
# TODO: @users_ns.response(404, 'User does not exist.')
class UserList(Resource):
    @classmethod
    @jwt_required
    @users_ns.doc(
        "list_users",
        params={
            "search": "Search query",
            "page": "specify page of users (default: 1)",
            "per_page": "specify number of users per page (default: 10)",
        },
    )
    @users_ns.response(
        HTTPStatus.OK.value,
        f"{messages.GENERAL_SUCCESS_MESSAGE}",
        public_user_api_model,
    )
    @users_ns.doc(
        responses={
            HTTPStatus.UNAUTHORIZED.value: f"{messages.TOKEN_HAS_EXPIRED}<br>"
            f"{messages.TOKEN_IS_INVALID}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING}"
        }
    )
    @users_ns.marshal_list_with(
        public_user_api_model, code=HTTPStatus.OK.value, description="Success"
    )
    @users_ns.expect(auth_header_parser)
    def get(cls):
        """
        Returns list of all the users whose names contain the given query.

        A user with valid access token can view the list of users. The endpoint
        doesn't take any other input. A JSON array having an object for each user is
        returned. The array contains id, username, name, slack_username, bio,
        location, occupation, current_organization, interests, skills, need_mentoring,
        available_to_mentor. The current user's details are not returned.
        """

        page = request.args.get("page", default=UserDAO.DEFAULT_PAGE, type=int)
        per_page = request.args.get(
            "per_page", default=UserDAO.DEFAULT_USERS_PER_PAGE, type=int
        )

        user_id = get_jwt_identity()
        return DAO.list_users(user_id, request.args.get("search", ""), page, per_page)


@users_ns.route("users/<int:user_id>")
@users_ns.param("user_id", "The user identifier")
class OtherUser(Resource):
    @classmethod
    @jwt_required
    @users_ns.doc("get_user")
    @users_ns.expect(auth_header_parser)
    @users_ns.response(
        HTTPStatus.OK.value,
        f"{messages.GENERAL_SUCCESS_MESSAGE}",
        public_user_api_model,
    )
    @users_ns.response(
        HTTPStatus.UNAUTHORIZED.value,
        "%s\n%s\n%s"
        % (
            messages.TOKEN_HAS_EXPIRED,
            messages.TOKEN_IS_INVALID,
            messages.AUTHORISATION_TOKEN_IS_MISSING,
        ),
    )
    @users_ns.response(HTTPStatus.NOT_FOUND.value, "%s" % messages.USER_DOES_NOT_EXIST)
    def get(cls, user_id):
        """
        Returns a user.

        A user with valid access token can view the details of another user. The endpoint
        takes "user_id" of such user has input.
        """
        requested_user = DAO.get_user(user_id)
        if isinstance(requested_user, tuple):
            return requested_user
        else:
            return marshal(requested_user, public_user_api_model), HTTPStatus.OK


@users_ns.route("user")
@users_ns.response(
    HTTPStatus.UNAUTHORIZED.value,
    "%s\n%s\n%s"
    % (
        messages.TOKEN_HAS_EXPIRED,
        messages.TOKEN_IS_INVALID,
        messages.AUTHORISATION_TOKEN_IS_MISSING,
    ),
)
@users_ns.response(HTTPStatus.NOT_FOUND.value, "%s" % messages.USER_DOES_NOT_EXIST)
class MyUserProfile(Resource):
    @classmethod
    @jwt_required
    @users_ns.doc("get_user")
    @users_ns.expect(auth_header_parser, validate=True)
    @users_ns.marshal_with(
        full_user_api_model, code=HTTPStatus.OK.value, description="Success"
    )  # , skip_none=True
    def get(cls):
        """
        Returns details of current user.

        A user with valid access token can use this endpoint to view his/her own
        user details. The endpoint doesn't take any other input.
        """
        user_id = get_jwt_identity()
        return DAO.get_user(user_id)

    @classmethod
    @jwt_required
    @users_ns.doc("update_user_profile")
    @users_ns.expect(auth_header_parser, update_user_request_body_model)
    @users_ns.response(HTTPStatus.OK.value, "%s" % messages.USER_SUCCESSFULLY_UPDATED)
    @users_ns.response(
        HTTPStatus.BAD_REQUEST.value,
        f"{messages.NO_DATA_FOR_UPDATING_PROFILE_WAS_SENT}\n"
        f"{messages.NEW_USERNAME_INPUT_BY_USER_IS_INVALID}\n"
        f"{messages.NAME_INPUT_BY_USER_IS_INVALID}\n"
        f"{messages.FIELD_NEED_MENTORING_IS_NOT_VALID}\n"
        f"{messages.FIELD_AVAILABLE_TO_MENTOR_IS_INVALID}\n"
        f"{messages.USER_DOES_NOT_EXIST}\n"
        f"{messages.USER_USES_A_USERNAME_THAT_ALREADY_EXISTS}",
    )
    def put(cls):
        """
        Updates user profile

        A user with valid access token can use this endpoint to edit his/her own
        user details. The endpoint takes any of the given parameters (name, username,
        bio, location, occupation, current_organization, slack_username, social_media_links,
        skills, interests, resume_url, photo_url, need_mentoring, available_to_mentor).
        The response contains a success message.
        """

        data = request.json

        is_valid = validate_update_profile_request_data(data)

        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST

        user_id = get_jwt_identity()
        return DAO.update_user_profile(user_id, data)

    @classmethod
    @jwt_required
    @users_ns.doc("delete_user")
    @users_ns.expect(auth_header_parser, validate=True)
    @users_ns.response(HTTPStatus.OK.value, "%s" % messages.USER_SUCCESSFULLY_DELETED)
    def delete(cls):
        """
        Deletes user.

        A user with valid access token can use this endpoint to delete his/her own
        user details. The endpoint doesn't take any other input. The response contains
        a success message.
        """
        user_id = get_jwt_identity()
        return DAO.delete_user(user_id)


@users_ns.response(
    HTTPStatus.CREATED.value, "%s" % messages.PASSWORD_SUCCESSFULLY_UPDATED
)
@users_ns.response(
    HTTPStatus.BAD_REQUEST.value,
    f"{messages.USER_ENTERED_INCORRECT_PASSWORD}\n{messages.USER_INPUTS_SPACE_IN_PASSWORD}",
)
@users_ns.response(
    HTTPStatus.UNAUTHORIZED.value,
    "%s\n%s\n%s"
    % (
        messages.TOKEN_HAS_EXPIRED,
        messages.TOKEN_IS_INVALID,
        messages.AUTHORISATION_TOKEN_IS_MISSING,
    ),
)
@users_ns.route("user/change_password")
class ChangeUserPassword(Resource):
    @classmethod
    @jwt_required
    @users_ns.doc("update_user_password")
    @users_ns.expect(
        auth_header_parser, change_password_request_data_model, validate=True
    )
    def put(cls):
        """
        Updates the user's password

        A user with valid access token can use this endpoint to change his/her own
        password. The endpoint takes current password and new password as input.
        The response contains a success message.
        """
        user_id = get_jwt_identity()
        data = request.json
        is_valid = validate_new_password(data)
        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST
        return DAO.change_password(user_id, data)


@users_ns.response(
    HTTPStatus.UNAUTHORIZED.value,
    "%s\n%s\n%s"
    % (
        messages.TOKEN_HAS_EXPIRED,
        messages.TOKEN_IS_INVALID,
        messages.AUTHORISATION_TOKEN_IS_MISSING,
    ),
)
@users_ns.route("users/verified")
class VerifiedUser(Resource):
    @classmethod
    @jwt_required
    @users_ns.doc(
        "get_verified_users",
        params={
            "search": "Search query",
            "page": "specify page of users",
            "per_page": "specify number of users per page",
        },
    )
    @users_ns.response(
        HTTPStatus.OK.value,
        f"{messages.GENERAL_SUCCESS_MESSAGE}",
        public_user_api_model,
    )
    @users_ns.doc(
        responses={
            HTTPStatus.UNAUTHORIZED.value: f"{messages.TOKEN_HAS_EXPIRED}<br>"
            f"{messages.TOKEN_IS_INVALID}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING}"
        }
    )
    @users_ns.marshal_list_with(
        public_user_api_model, code=HTTPStatus.OK.value, description="Success"
    )  # , skip_none=True
    @users_ns.expect(auth_header_parser)
    def get(cls):
        """
        Returns all verified users whose names contain the given query.

        A user with valid access token can view the list of verified users. The endpoint
        doesn't take any other input. A JSON array having an object for each user is
        returned. The array contains id, username, name, slack_username, bio,
        location, occupation, current_organization, interests, skills, need_mentoring,
        available_to_mentor. The current user's details are not returned.
        """

        page = request.args.get("page", default=UserDAO.DEFAULT_PAGE, type=int)
        per_page = request.args.get(
            "per_page", default=UserDAO.DEFAULT_USERS_PER_PAGE, type=int
        )

        user_id = get_jwt_identity()
        return DAO.list_users(
            user_id, request.args.get("search", ""), page, per_page, is_verified=True
        )


@users_ns.route("register")
class UserRegister(Resource):
    @classmethod
    @users_ns.doc("create_user")
    @users_ns.response(
        HTTPStatus.CREATED.value, "%s" % messages.USER_WAS_CREATED_SUCCESSFULLY
    )
    @users_ns.response(
        HTTPStatus.BAD_REQUEST.value,
        f"{messages.NAME_FIELD_IS_MISSING}\n"
        f"{messages.USERNAME_FIELD_IS_MISSING}\n"
        f"{messages.PASSWORD_FIELD_IS_MISSING}\n"
        f"{messages.EMAIL_FIELD_IS_MISSING}\n"
        f"{messages.TERMS_AND_CONDITIONS_FIELD_IS_MISSING}\n"
        f"{messages.NAME_USERNAME_AND_PASSWORD_NOT_IN_STRING_FORMAT}\n"
        f"{messages.TERMS_AND_CONDITIONS_ARE_NOT_CHECKED}\n"
        f"{messages.NAME_INPUT_BY_USER_IS_INVALID}\n"
        f"{messages.EMAIL_INPUT_BY_USER_IS_INVALID}\n"
        f"{messages.USERNAME_INPUT_BY_USER_IS_INVALID}\n"
        f"{messages.USER_INPUTS_SPACE_IN_PASSWORD}\n"
        f"{messages.USERNAME_HAS_INVALID_LENGTH}\n"
        f"{messages.PASSWORD_INPUT_BY_USER_HAS_INVALID_LENGTH}",
    )
    @users_ns.response(
        HTTPStatus.CONFLICT,
        "%s\n%s"
        % (
            messages.USER_USES_A_USERNAME_THAT_ALREADY_EXISTS,
            messages.USER_USES_AN_EMAIL_ID_THAT_ALREADY_EXISTS,
        ),
    )
    @users_ns.expect(register_user_api_model, validate=True)
    def post(cls):
        """
        Creates a new user.

        The endpoint accepts details like name, username, password, email,
        terms_and_conditions_checked(true/false), need_mentoring(true/false),
        available_to_mentor(true/false). A success message is displayed and
        verification email is sent to the user's email ID.
        """

        data = request.json

        is_valid = validate_user_registration_request_data(data)

        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST

        result = DAO.create_user(data)

        if result[1] is HTTPStatus.CREATED:
            send_email_verification_message(data["name"], data["email"])
        print(result[0])
        return result


@users_ns.route("user/confirm_email/<string:token>")
@users_ns.response(
    HTTPStatus.CREATED.value,
    "%s\n%s"
    % (
        messages.USER_SUCCESSFULLY_CREATED,
        messages.ACCOUNT_ALREADY_CONFIRMED_AND_THANKS,
    ),
)
@users_ns.response(
    HTTPStatus.CONFLICT.value, "%s" % messages.EMAIL_EXPIRED_OR_TOKEN_IS_INVALID
)
@users_ns.param("token", "Token sent to the user's email")
class UserEmailConfirmation(Resource):
    @classmethod
    def get(cls, token):
        """Confirms the user's account.

        This endpoint is called when a new user clicks the verification link
        sent on the users' email. It takes the verification token through URL
        as input parameter.The verification token is valid for 30 days. A success or
        failure response is returned by the API.
        """

        return DAO.confirm_registration(token)


@users_ns.route("user/resend_email")
@users_ns.response(HTTPStatus.OK.value, f"{messages.EMAIL_VERIFICATION_MESSAGE}")
@users_ns.response(HTTPStatus.BAD_REQUEST.value, f"{messages.INVALID_INPUT}")
@users_ns.response(
    HTTPStatus.FORBIDDEN.value, f"{messages.USER_ALREADY_CONFIRMED_ACCOUNT}"
)
@users_ns.response(
    HTTPStatus.NOT_FOUND.value, f"{messages.USER_IS_NOT_REGISTERED_IN_THE_SYSTEM}"
)
class UserResendEmailConfirmation(Resource):
    @classmethod
    @users_ns.expect(resend_email_request_body_model)
    def post(cls):
        """Sends the user a new verification email.

        This endpoint is called when a user wants the verification email to be
        resent. The verification token is valid for 30 days. A success or
        failure response is returned by the API.
        """

        data = request.json

        is_valid = validate_resend_email_request_data(data)

        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST

        user = DAO.get_user_by_email(data["email"])
        if user is None:
            return messages.USER_IS_NOT_REGISTERED_IN_THE_SYSTEM, HTTPStatus.NOT_FOUND

        if user.is_email_verified:
            return messages.USER_ALREADY_CONFIRMED_ACCOUNT, HTTPStatus.FORBIDDEN

        send_email_verification_message(user.name, data["email"])

        return messages.EMAIL_VERIFICATION_MESSAGE, HTTPStatus.OK


@users_ns.route("refresh")
class RefreshUser(Resource):
    @classmethod
    @jwt_refresh_token_required
    @users_ns.doc("refresh")
    @users_ns.response(
        HTTPStatus.OK.value,
        f"{messages.SUCCESSFUL_REFRESH}",
        refresh_response_body_model,
    )
    @users_ns.response(
        HTTPStatus.UNAUTHORIZED.value,
        "%s\n%s\n%s"
        % (
            messages.TOKEN_HAS_EXPIRED,
            messages.TOKEN_IS_INVALID,
            messages.AUTHORISATION_TOKEN_IS_MISSING,
        ),
    )
    @users_ns.expect(refresh_auth_header_parser)
    def post(cls):
        """Refresh user's access

        The return value is an access token.
        The token is valid for 1 week.
        """
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)

        return (
            {"access_token": access_token},
            HTTPStatus.OK,
        )


@users_ns.route("login")
class LoginUser(Resource):
    @classmethod
    @users_ns.doc("login")
    @users_ns.response(
        HTTPStatus.OK.value, f"{messages.SUCCESSFUL_LOGIN}", login_response_body_model
    )
    @users_ns.response(
        HTTPStatus.BAD_REQUEST.value,
        "%s\n%s"
        % (messages.USERNAME_FIELD_IS_MISSING, messages.PASSWORD_FIELD_IS_MISSING),
    )
    @users_ns.response(
        HTTPStatus.FORBIDDEN.value,
        "%s" % messages.USER_HAS_NOT_VERIFIED_EMAIL_BEFORE_LOGIN,
    )
    @users_ns.response(
        HTTPStatus.UNAUTHORIZED.value, "%s" % messages.WRONG_USERNAME_OR_PASSWORD
    )
    @users_ns.expect(login_request_body_model)
    def post(cls):
        """
        Login user

        The user can login with (username or email) + password.
        Username field can be either the User's username or the email.
        The return value is an access token.
        The token is valid for 1 week.
        """
        # if not request.is_json:
        #     return {'msg': 'Missing JSON in request'}, 400

        username = request.json.get("username", None)
        password = request.json.get("password", None)

        if not username:
            return messages.USERNAME_FIELD_IS_MISSING, HTTPStatus.BAD_REQUEST
        if not password:
            return messages.PASSWORD_FIELD_IS_MISSING, HTTPStatus.BAD_REQUEST

        user = DAO.authenticate(username, password)

        if not user:
            return messages.WRONG_USERNAME_OR_PASSWORD, HTTPStatus.UNAUTHORIZED

        if not user.is_email_verified:
            return (
                messages.USER_HAS_NOT_VERIFIED_EMAIL_BEFORE_LOGIN,
                HTTPStatus.FORBIDDEN,
            )

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return (
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            HTTPStatus.OK,
        )


@users_ns.route("home")
@users_ns.doc("home")
@users_ns.expect(auth_header_parser, validate=True)
@users_ns.response(
    HTTPStatus.OK.value, f"{messages.SUCCESSFUL_RESPONSE}", home_response_body_model
)
@users_ns.response(
    HTTPStatus.UNAUTHORIZED.value,
    "%s\n%s\n%s"
    % (
        messages.TOKEN_HAS_EXPIRED,
        messages.TOKEN_IS_INVALID,
        messages.AUTHORISATION_TOKEN_IS_MISSING,
    ),
)
@users_ns.response(HTTPStatus.NOT_FOUND.value, "%s" % messages.USER_NOT_FOUND)
class UserHomeStatistics(Resource):
    @classmethod
    @jwt_required
    @users_ns.expect(auth_header_parser)
    def get(cls):
        """Get Statistics regarding the current user

        Returns:
            A dict containing user stats(name, pending_requests, accepted_requests,
            completed_relations, cancelled_relations, rejected_requests, achievements)
        """
        user_id = get_jwt_identity()
        stats = DAO.get_user_statistics(user_id)
        if not stats:
            return messages.USER_NOT_FOUND, HTTPStatus.NOT_FOUND

        return stats, HTTPStatus.OK


@users_ns.route("dashboard")
@users_ns.expect(auth_header_parser, validate=True)
@users_ns.response(
    HTTPStatus.OK.value,
    f"{messages.GENERAL_SUCCESS_MESSAGE}",
    dashboard_response_body_model,
)
@users_ns.response(HTTPStatus.NOT_FOUND.value, f"{messages.USER_NOT_FOUND}")
class UserDashboard(Resource):
    @classmethod
    @jwt_required
    @users_ns.expect(auth_header_parser)
    def get(cls):
        """Get current User's dashboard

        Returns:
            A dict containing user dashboard
        """
        user_id = get_jwt_identity()
        dashboard = DAO.get_user_dashboard(user_id)
        if not dashboard:
            return messages.USER_NOT_FOUND, HTTPStatus.NOT_FOUND

        return dashboard, HTTPStatus.OK
