from flask import request
from flask_restx import Resource, Namespace, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from app import messages
from app.api.dao.user import UserDAO
from app.api.models.admin import *
from app.api.dao.admin import AdminDAO
from app.api.resources.common import auth_header_parser

admin_ns = Namespace("Admins", description="Operations related to Admin users")
add_models_to_namespace(admin_ns)


@admin_ns.route("admin/new")
@admin_ns.response(HTTPStatus.FORBIDDEN.value, f"{messages.USER_IS_NOW_AN_ADMIN}")
@admin_ns.response(HTTPStatus.BAD_REQUEST.value, f"{messages.USER_IS_ALREADY_AN_ADMIN}")
@admin_ns.response(
    HTTPStatus.UNAUTHORIZED.value,
    f"{messages.TOKEN_HAS_EXPIRED}\n{messages.TOKEN_IS_INVALID}\n{messages.AUTHORISATION_TOKEN_IS_MISSING}",
)
@admin_ns.response(HTTPStatus.FORBIDDEN.value, f"{messages.USER_ASSIGN_NOT_ADMIN}")
@admin_ns.response(HTTPStatus.NOT_FOUND.value, f"{messages.USER_DOES_NOT_EXIST}")
class AssignNewUserAdmin(Resource):
    @classmethod
    @jwt_required
    @admin_ns.expect(
        auth_header_parser, assign_and_revoke_user_admin_request_body, validate=True
    )
    def post(cls):
        """
        Assigns a User as a new Admin.

        An existing admin can use this endpoint to designate another user as an admin.
        This is done by passing "user_id" of that particular user.
        """
        user_id = get_jwt_identity()
        user = UserDAO.get_user(user_id)
        if user.is_admin:
            data = request.json
            return AdminDAO.assign_new_user(user.id, data)

        else:
            return messages.USER_ASSIGN_NOT_ADMIN, HTTPStatus.FORBIDDEN


@admin_ns.route("admin/remove")
@admin_ns.response(HTTPStatus.OK.value, f"{messages.USER_ADMIN_STATUS_WAS_REVOKED}")
@admin_ns.response(HTTPStatus.BAD_REQUEST.value, f"{messages.USER_IS_NOT_AN_ADMIN}")
@admin_ns.response(
    HTTPStatus.UNAUTHORIZED.value,
    f"{messages.TOKEN_HAS_EXPIRED}\n{messages.TOKEN_IS_INVALID}\n{messages.AUTHORISATION_TOKEN_IS_MISSING}",
)
@admin_ns.response(HTTPStatus.FORBIDDEN.value, f"{messages.USER_REVOKE_NOT_ADMIN}")
@admin_ns.response(HTTPStatus.NOT_FOUND.value, f"{messages.USER_DOES_NOT_EXIST}")
class RevokeUserAdmin(Resource):
    @classmethod
    @jwt_required
    @admin_ns.expect(
        auth_header_parser, assign_and_revoke_user_admin_request_body, validate=True
    )
    def post(cls):
        """
        Revoke admin status from another User Admin.

        An existing admin can use this endpoint to revoke admin status of another user.
        This is done by passing "user_id" of that particular user.
        """
        user_id = get_jwt_identity()
        user = UserDAO.get_user(user_id)
        if user.is_admin:
            data = request.json
            return AdminDAO.revoke_admin_user(user.id, data)

        else:
            return messages.USER_REVOKE_NOT_ADMIN, HTTPStatus.FORBIDDEN


@admin_ns.route("admins")
class ListAdmins(Resource):
    @classmethod
    @jwt_required
    @admin_ns.doc("get_list_of_admins")
    @admin_ns.response(
        HTTPStatus.OK.value,
        f"{messages.GENERAL_SUCCESS_MESSAGE}",
        public_admin_user_api_model,
    )
    @admin_ns.doc(
        responses={
            HTTPStatus.UNAUTHORIZED.value: f"{messages.TOKEN_HAS_EXPIRED}<br>"
            f"{messages.TOKEN_IS_INVALID}<br>"
            f"{messages.AUTHORISATION_TOKEN_IS_MISSING}"
        }
    )
    @admin_ns.response(HTTPStatus.FORBIDDEN.value, f"{messages.USER_IS_NOT_AN_ADMIN}")
    @admin_ns.expect(auth_header_parser)
    def get(cls):
        """
        Returns all admin users.

        A admin user with valid access token can view the list of all admins. The endpoint
        doesn't take any other input. A JSON array having an object for each admin user is
        returned. The array contains id, username, name, slack_username, bio,
        location, occupation, current_organization, skills. 
        The current admin user's details are not returned.
        """
        user_id = get_jwt_identity()
        user = UserDAO.get_user(user_id)

        if user.is_admin:
            list_of_admins = AdminDAO.list_admins(user_id)
            list_of_admins = [
                marshal(x, public_admin_user_api_model) for x in list_of_admins
            ]

            return list_of_admins, HTTPStatus.OK
        else:
            return messages.USER_IS_NOT_AN_ADMIN, HTTPStatus.FORBIDDEN
