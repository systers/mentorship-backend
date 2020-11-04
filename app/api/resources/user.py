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
from app.api.email_utils import send_email_verification_message, send_email_reset_password_message
from app.api.models.user import *
from app.api.dao.user import UserDAO
from app.api.resources.common import auth_header_parser
from app.utils.validation_utils import is_email_valid

users_ns = Namespace("Users", description="Operations related to users")
add_models_to_namespace(users_ns)

DAO = UserDAO()  # User data access object


@users_ns.route("users")
@users_ns.response(
    HTTPStatus.UNAUTHORIZED,
    "%s\n%s\n%s"
    % (
        messages.TOKEN_HAS_EXPIRED,
        messages.TOKEN_IS_INVALID,
        messages.AUTHORISATION_TOKEN_IS_MISSING
    ),
)
# TODO: @users_ns.response(404, 'User does not exist.')
class UserList(Resource):
    @classmethod
    @jwt_required
    @users_ns.doc("list_users", params={"search": "Search query", "page": "specify page of users", "per_page": "specify number of users per page"})
    @users_ns.doc(
        responses={
            HTTPStatus.UNAUTHORIZED: f"{messages.TOKEN_HAS_EXPIRED['message']}<br>"
            f"{messages.TOKEN_IS_INVALID['message']}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING['message']}"
        }
    )
    @users_ns.marshal_list_with(public_user_api_model)
    @users_ns.expect(auth_header_parser)
    def get(cls):
        """
        Returns list of all the users whose names contain the given query.

        A user with valid access token can view the list of users. The endpoint
        doesn't take any other input. A JSON array having an object for each user is
        returned. The array contains id, username, name, slack_username, bio,
        location, occupation, organization, interests, skills, need_mentoring,
        available_to_mentor. The current user's details are not returned.
        """

        page = request.args.get("page", default=UserDAO.DEFAULT_PAGE, type=int)
        per_page = request.args.get("per_page", default=UserDAO.DEFAULT_USERS_PER_PAGE, type=int)

        user_id = get_jwt_identity()
        return DAO.list_users(user_id, request.args.get("search", ""), page, per_page)


@users_ns.route("users/<int:user_id>")
@users_ns.param("user_id", "The user identifier")
class OtherUser(Resource):
    @classmethod
    @jwt_required
    @users_ns.doc("get_user")
    @users_ns.expect(auth_header_parser)
    @users_ns.response(HTTPStatus.OK, "Success.", public_user_api_model)
    @users_ns.response(
        HTTPStatus.UNAUTHORIZED,
        "%s\n%s\n%s"
        % (
            messages.TOKEN_HAS_EXPIRED,
            messages.TOKEN_IS_INVALID,
            messages.AUTHORISATION_TOKEN_IS_MISSING,
        ),
    )
    @users_ns.response(HTTPStatus.NOT_FOUND, "%s" % messages.USER_DOES_NOT_EXIST)
    def get(cls, user_id):
        """
        Returns a user.

        A user with valid access token can view the details of another user. The endpoint
        takes "user_id" of such user has input.
        """
        requested_user = DAO.get_user(user_id)
        if requested_user is None:
            return messages.USER_DOES_NOT_EXIST, HTTPStatus.NOT_FOUND
        else:
            return marshal(requested_user, public_user_api_model), HTTPStatus.OK


@users_ns.route("user")
@users_ns.response(
    HTTPStatus.UNAUTHORIZED,
    "%s\n%s\n%s"
    % (
        messages.TOKEN_HAS_EXPIRED,
        messages.TOKEN_IS_INVALID,
        messages.AUTHORISATION_TOKEN_IS_MISSING,
    ),
)
@users_ns.response(HTTPStatus.NOT_FOUND, "%s" % messages.USER_DOES_NOT_EXIST)
class MyUserProfile(Resource):
    @classmethod
    @jwt_required
    @users_ns.doc("get_user")
    @users_ns.expect(auth_header_parser, validate=True)
    @users_ns.marshal_with(full_user_api_model)  # , skip_none=True
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
    @users_ns.response(HTTPStatus.OK, "%s" % messages.USER_SUCCESSFULLY_UPDATED)
    @users_ns.response(HTTPStatus.BAD_REQUEST, "%s" % messages.NAME_INPUT_BY_USER_IS_INVALID)
    def put(cls):
        """
        Updates user profile

        A user with valid access token can use this endpoint to edit his/her own
        user details. The endpoint takes any of the given parameters (name, username,
        bio, location, occupation, organization, slack_username, social_media_links,
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
    @users_ns.response(HTTPStatus.OK, "%s" % messages.USER_SUCCESSFULLY_DELETED)
    def delete(cls):
        """
        Deletes user.

        A user with valid access token can use this endpoint to delete his/her own
        user details. The endpoint doesn't take any other input. The response contains
        a success message.
        """
        user_id = get_jwt_identity()
        return DAO.delete_user(user_id)


@users_ns.response(HTTPStatus.CREATED, "%s" % messages.PASSWORD_SUCCESSFULLY_UPDATED)
@users_ns.response(HTTPStatus.BAD_REQUEST, "%s" % messages.USER_ENTERED_INCORRECT_PASSWORD)
@users_ns.response(
    HTTPStatus.UNAUTHORIZED,
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
    HTTPStatus.UNAUTHORIZED,
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
    @users_ns.doc("get_verified_users", params={"search": "Search query", "page": "specify page of users", "per_page": "specify number of users per page"})
    @users_ns.doc(
        responses={
            HTTPStatus.UNAUTHORIZED: f"{messages.TOKEN_HAS_EXPIRED['message']}<br>"
            f"{messages.TOKEN_IS_INVALID['message']}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING['message']}"
        }
    )
    @users_ns.marshal_list_with(public_user_api_model)  # , skip_none=True
    @users_ns.expect(auth_header_parser)
    def get(cls):
        """
        Returns all verified users whose names contain the given query.

        A user with valid access token can view the list of verified users. The endpoint
        doesn't take any other input. A JSON array having an object for each user is
        returned. The array contains id, username, name, slack_username, bio,
        location, occupation, organization, interests, skills, need_mentoring,
        available_to_mentor. The current user's details are not returned.
        """

        page = request.args.get("page", default=UserDAO.DEFAULT_PAGE, type=int)
        per_page = request.args.get("per_page", default=UserDAO.DEFAULT_USERS_PER_PAGE, type=int)

        user_id = get_jwt_identity()
        return DAO.list_users(user_id, request.args.get("search", ""), page, per_page, is_verified=True)


@users_ns.route("register")
class UserRegister(Resource):
    @classmethod
    @users_ns.doc("create_user")
    @users_ns.response(HTTPStatus.CREATED, "%s" % messages.USER_WAS_CREATED_SUCCESSFULLY)
    @users_ns.response(
        HTTPStatus.BAD_REQUEST,
        "%s\n%s\n%s"
        % (
            messages.USERNAME_FIELD_IS_EMPTY,
            messages.PASSWORD_INPUT_BY_USER_HAS_INVALID_LENGTH,
            messages.EMAIL_INPUT_BY_USER_IS_INVALID
        ),
    )
    @users_ns.response(
        HTTPStatus.CONFLICT,
        "%s\n%s"
        % (
            messages.USER_USES_A_USERNAME_THAT_ALREADY_EXISTS,
            messages.USER_USES_AN_EMAIL_ID_THAT_ALREADY_EXISTS
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
            return is_valid, HTTPStatus.CONFLICT


        result = DAO.create_user(data)

        if result[1] is HTTPStatus.CREATED:
            send_email_verification_message(data["name"], data["email"])

        return result


@users_ns.route("user/confirm_email/<string:token>")
@users_ns.response(
    HTTPStatus.CREATED,
    "%s\n%s"
    % (
        messages.USER_SUCCESSFULLY_CREATED,
        messages.ACCOUNT_ALREADY_CONFIRMED_AND_THANKS,
    ),
)
@users_ns.response(HTTPStatus.CONFLICT, "%s" % messages.EMAIL_EXPIRED_OR_TOKEN_IS_INVALID)
@users_ns.param("token", "Token sent to the user's email")
class UserEmailConfirmation(Resource):
    @classmethod
    def get(cls, token):
        """Confirms the user's account.

        This endpoint is called when a new user clicks the verification link
        sent on the users' email. It takes the verification token through URL
        as input parameter.The verification token is valid for 24 hours. A success or
        failure response is returned by the API.
        """

        return DAO.confirm_registration(token)


@users_ns.route("user/resend_email")
@users_ns.response(HTTPStatus.OK, "%s" % messages.EMAIL_VERIFICATION_MESSAGE)
@users_ns.response(HTTPStatus.BAD_REQUEST, "Invalid input.")
@users_ns.response(HTTPStatus.FORBIDDEN, "%s" % messages.USER_ALREADY_CONFIRMED_ACCOUNT)
@users_ns.response(HTTPStatus.NOT_FOUND, "%s" % messages.USER_IS_NOT_REGISTERED_IN_THE_SYSTEM)
class UserResendEmailConfirmation(Resource):
    @classmethod
    @users_ns.expect(resend_email_request_body_model)
    def post(cls):
        """Sends the user a new verification email.

        This endpoint is called when a user wants the verification email to be
        resent. The verification token is valid for 24 hours. A success or
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
    @users_ns.response(HTTPStatus.OK, "Successful refresh", refresh_response_body_model)
    @users_ns.response(
        HTTPStatus.UNAUTHORIZED,
        "%s\n%s\n%s"
        % (
            messages.TOKEN_HAS_EXPIRED,
            messages.TOKEN_IS_INVALID,
            messages.AUTHORISATION_TOKEN_IS_MISSING,
        ),
    )
    @users_ns.expect(auth_header_parser)
    def post(cls):
        """Refresh user's access

        The return value is an access token and the expiry timestamp.
        The token is valid for 1 week.
        """
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)

        from run import application

        access_expiry = datetime.utcnow() + application.config.get(
            "JWT_ACCESS_TOKEN_EXPIRES"
        )

        return (
            {"access_token": access_token, "access_expiry": access_expiry.timestamp()},
            HTTPStatus.OK,
        )


@users_ns.route("login")
class LoginUser(Resource):
    @classmethod
    @users_ns.doc("login")
    @users_ns.response(HTTPStatus.OK, "Successful login", login_response_body_model)
    @users_ns.response(
        HTTPStatus.BAD_REQUEST,
        "%s\n%s"
        % (messages.USERNAME_FIELD_IS_MISSING, messages.PASSWORD_FIELD_IS_MISSING),
    )
    @users_ns.response(HTTPStatus.FORBIDDEN, "%s" % messages.USER_HAS_NOT_VERIFIED_EMAIL_BEFORE_LOGIN)
    @users_ns.response(HTTPStatus.UNAUTHORIZED, "%s" % messages.WRONG_USERNAME_OR_PASSWORD)
    @users_ns.expect(login_request_body_model)
    def post(cls):
        """
        Login user

        The user can login with (username or email) + password.
        Username field can be either the User's username or the email.
        The return value is an access token and the expiry timestamp.
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
            return messages.USER_HAS_NOT_VERIFIED_EMAIL_BEFORE_LOGIN, HTTPStatus.FORBIDDEN

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        from run import application

        access_expiry = datetime.utcnow() + application.config.get(
            "JWT_ACCESS_TOKEN_EXPIRES"
        )
        refresh_expiry = datetime.utcnow() + application.config.get(
            "JWT_REFRESH_TOKEN_EXPIRES"
        )

        return (
            {
                "access_token": access_token,
                "access_expiry": access_expiry.timestamp(),
                "refresh_token": refresh_token,
                "refresh_expiry": refresh_expiry.timestamp(),
            },
            HTTPStatus.OK,
        )


@users_ns.route("home")
@users_ns.doc("home")
@users_ns.expect(auth_header_parser, validate=True)
@users_ns.response(HTTPStatus.OK, "Successful response", home_response_body_model)
@users_ns.response(
    HTTPStatus.UNAUTHORIZED,
    "%s\n%s\n%s"
    % (
        messages.TOKEN_HAS_EXPIRED,
        messages.TOKEN_IS_INVALID,
        messages.AUTHORISATION_TOKEN_IS_MISSING,
    ),
)
@users_ns.response(HTTPStatus.NOT_FOUND, "%s" % messages.USER_NOT_FOUND)
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
@users_ns.response(HTTPStatus.OK, "Successful response", dashboard_response_body_model)
@users_ns.response(HTTPStatus.NOT_FOUND, "User not found")
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

@users_ns.route("user/forgot_password")
class ForgotPassword(Resource):
    @classmethod
    @users_ns.doc("forgot password")
    @users_ns.response(HTTPStatus.OK, f"{messages.PASSWORD_RESET_MAIL_MESSAGE}")
    @users_ns.response(HTTPStatus.BAD_REQUEST, f"{messages.EMAIL_FIELD_IS_MISSING}\n{messages.EMAIL_INPUT_BY_USER_IS_INVALID}")
    @users_ns.response(HTTPStatus.FORBIDDEN, f"{messages.USER_HAS_NOT_VERIFIED_EMAIL_BEFORE_LOGIN}")
    @users_ns.response(HTTPStatus.NOT_FOUND, f"{messages.USER_IS_NOT_REGISTERED_IN_THE_SYSTEM}")
    @users_ns.expect(forgot_password_change_request_data_model, validate=True)
    def post(self):
        """ Updates User's password by sending reset link to email
 
        Args: 
          email: Verified email of the user
 
        Return:
          token: a token link/reset link will be shared on verified mail of user
        """
 
        data = request.json
 
        if not data["email"]:
            return messages.EMAIL_FIELD_IS_MISSING, HTTPStatus.BAD_REQUEST
 
        if not is_email_valid(email):
            return messages.EMAIL_INPUT_BY_USER_IS_INVALID, HTTPStatus.BAD_REQUEST
 
        user = DAO.get_user_by_email(data["email"])
 
        if user is None:
            return messages.USER_IS_NOT_REGISTERED_IN_THE_SYSTEM, HTTPStatus.NOT_FOUND
 
        if not user.is_email_verified:
            return messages.USER_HAS_NOT_VERIFIED_EMAIL_BEFORE_LOGIN, HTTPStatus.FORBIDDEN
 
        send_email_reset_password_message(user.name, user.email)
 
        return messages.PASSWORD_RESET_MAIL_MESSAGE, HTTPStatus.OK
 
@users_ns.route("user/reset_password")
@users_ns.response(HTTPStatus.OK, f"{messages.PASSWORD_SUCCESSFULLY_UPDATED}")
@users_ns.response(
    HTTPStatus.UNAUTHORIZED,
    f"{messages.RESET_PASSWORD_TOKEN_HAS_EXPIRED}\n{messages.AUTHORISATION_TOKEN_IS_MISSING}"
)
@users_ns.response(HTTPStatus.BAD_REQUEST, f"{messages.PASSWORD_FIELD_IS_MISSING}")
class ResetPassword(Resource):
    @classmethod
    @users_ns.doc("reset")
    @users_ns.expect(reset_password_forgot_request_data_model, validate=True)
    def post(self):
        """ Updates User's password
 
        This will allow the user to change/create a new password 
        In case they forgot it.
 
        Args:
            token: token of reset link sent on verified mail
            new_password: take the new validated password to login
 
        Return:
            Password Updated successfully
        """
        data = request.json
        token = data["token"]
        new_password = data["new_password"]
 
        if not token:
            return messages.AUTHORISATION_TOKEN_IS_MISSING, HTTPStatus.UNAUTHORIZED
 
        if not new_password:
            return messages.PASSWORD_FIELD_IS_MISSING, HTTPStatus.BAD_REQUEST
 
        is_valid = validate_reset_password(data)
 
        if is_valid != {}:
            return is_valid, HTTPStatus.BAD_REQUEST
 
        email_from_token = DAO.reset_password_token(token)
 
        if not email_from_token:
            return messages.RESET_PASSWORD_TOKEN_HAS_EXPIRED, HTTPStatus.UNAUTHORIZED
 
        user = DAO.get_user_by_email(email_from_token)
 
        user.set_password(new_password)
        user.save_to_db()
 
        return messages.PASSWORD_SUCCESSFULLY_UPDATED, HTTPStatus.OK

