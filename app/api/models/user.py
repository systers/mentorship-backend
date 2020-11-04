from flask_restx import fields, Model
from app.api.models.mentorship_relation import (
    list_tasks_response_body,
    mentorship_request_response_body_for_user_dashboard_body,
)


def add_models_to_namespace(api_namespace):
    api_namespace.models[public_user_api_model.name] = public_user_api_model
    api_namespace.models[full_user_api_model.name] = full_user_api_model
    api_namespace.models[register_user_api_model.name] = register_user_api_model
    api_namespace.models[
        change_password_request_data_model.name
    ] = change_password_request_data_model
    api_namespace.models[
        update_user_request_body_model.name
    ] = update_user_request_body_model
    api_namespace.models[login_request_body_model.name] = login_request_body_model
    api_namespace.models[login_response_body_model.name] = login_response_body_model
    api_namespace.models[refresh_response_body_model.name] = refresh_response_body_model
    api_namespace.models[
        resend_email_request_body_model.name
    ] = resend_email_request_body_model
    api_namespace.models[home_response_body_model.name] = home_response_body_model
    api_namespace.models[
        dashboard_response_body_model.name
    ] = dashboard_response_body_model
    api_namespace.models[
        dashboard_relations_by_state_model.name
    ] = dashboard_relations_by_state_model
    api_namespace.models[
        dashboard_sent_received_model.name
    ] = dashboard_sent_received_model
    api_namespace.models[
        forgot_password_change_request_data_model.name
        ] = forgot_password_change_request_data_model
    api_namespace.models[
        reset_password_forgot_request_data_model.name
        ] = reset_password_forgot_request_data_model



public_user_api_model = Model(
    "User list model",
    {
        "id": fields.Integer(
            readOnly=True, description="The unique identifier of a user"
        ),
        "username": fields.String(required=True, description="User username"),
        "name": fields.String(required=True, description="User name"),
        "slack_username": fields.String(
            required=True, description="User Slack username"
        ),
        "bio": fields.String(required=True, description="User bio"),
        "location": fields.String(required=True, description="User location"),
        "occupation": fields.String(required=True, description="User occupation"),
        "organization": fields.String(required=True, description="User organization"),
        "interests": fields.String(required=True, description="User interests"),
        "skills": fields.String(required=True, description="User skills"),
        "need_mentoring": fields.Boolean(
            required=True, description="User need to be mentored indication"
        ),
        "available_to_mentor": fields.Boolean(
            required=True, description="User availability to mentor indication"
        ),
        "is_available": fields.Boolean(
            required=True,
            description="User availability to mentor or to be mentored indication",
        ),
    },
)

full_user_api_model = Model(
    "User Complete model used in listing",
    {
        "id": fields.Integer(
            readOnly=True, description="The unique identifier of a user"
        ),
        "name": fields.String(required=True, description="User name"),
        "username": fields.String(required=True, description="User username"),
        "email": fields.String(required=True, description="User email"),
        "terms_and_conditions_checked": fields.Boolean(
            required=True, description="User Terms and Conditions check state"
        ),
        "is_admin": fields.Boolean(required=True, description="User admin status"),
        "registration_date": fields.Float(
            required=True, description="User registration date"
        ),
        "is_email_verified": fields.Boolean(
            required=True, description="User email verification status"
        ),
        "email_verification_date": fields.DateTime(
            required=False, description="User email verification date"
        ),
        "bio": fields.String(required=False, description="User bio"),
        "location": fields.String(required=False, description="User location"),
        "occupation": fields.String(required=False, description="User occupation"),
        "organization": fields.String(required=False, description="User organization"),
        "slack_username": fields.String(
            required=False, description="User slack username"
        ),
        "social_media_links": fields.String(
            required=False, description="User social media links"
        ),
        "skills": fields.String(required=False, description="User skills"),
        "interests": fields.String(required=False, description="User interests"),
        "resume_url": fields.String(required=False, description="User resume url"),
        "photo_url": fields.String(required=False, description="User photo url"),
        "need_mentoring": fields.Boolean(
            required=False, description="User need mentoring indication"
        ),
        "available_to_mentor": fields.Boolean(
            required=False, description="User availability to mentor indication"
        ),
        "current_mentorship_role": fields.Integer(
            required=False, description="User current role"
        ),
        "membership_status": fields.Integer(
            required=False, description="User membershipstatus"
        ),
    },
)

register_user_api_model = Model(
    "User registration model",
    {
        "name": fields.String(required=True, description="User name"),
        "username": fields.String(required=True, description="User username"),
        "password": fields.String(required=True, description="User password"),
        "email": fields.String(required=True, description="User email"),
        "terms_and_conditions_checked": fields.Boolean(
            required=True, description="User check Terms and Conditions value"
        ),
        "need_mentoring": fields.Boolean(
            required=False, description="User need mentoring indication"
        ),
        "available_to_mentor": fields.Boolean(
            required=False, description="User availability to mentor indication"
        ),
    },
)

change_password_request_data_model = Model(
    "Change password request data model",
    {
        "current_password": fields.String(
            required=True, description="User's current password"
        ),
        "new_password": fields.String(required=True, description="User's new password"),
    },
)

login_request_body_model = Model(
    "Login request data model",
    {
        "username": fields.String(required=True, description="User's username"),
        "password": fields.String(required=True, description="User's password"),
    },
)

login_response_body_model = Model(
    "Login response data model",
    {
        "access_token": fields.String(
            required=True, description="User's access token"
        ),
        "access_expiry": fields.Float(
            required=True, description="Access token expiry UNIX timestamp"
        ),
        "refresh_token": fields.String(
            required=True, description="User's refresh token"
        ),
        "refresh_expiry": fields.Float(
            required=True, description="Refresh token expiry UNIX timestamp"
        ),
    },
)

refresh_response_body_model = Model(
    "Refresh response data model",
    {
        "access_token": fields.String(required=True, description="User's access token"),
        "access_expiry": fields.Float(
            required=True, description="Access token expiry UNIX timestamp"
        ),
    },
)

update_user_request_body_model = Model(
    "Update User request data model",
    {
        "name": fields.String(required=False, description="User name"),
        "username": fields.String(required=False, description="User username"),
        "bio": fields.String(required=False, description="User bio"),
        "location": fields.String(required=False, description="User location"),
        "occupation": fields.String(required=False, description="User occupation"),
        "organization": fields.String(required=False, description="User organization"),
        "slack_username": fields.String(
            required=False, description="User slack username"
        ),
        "social_media_links": fields.String(
            required=False, description="User social media links"
        ),
        "skills": fields.String(required=False, description="User skills"),
        "interests": fields.String(required=False, description="User interests"),
        # TODO: This url is generated by the backend
        "resume_url": fields.String(required=False, description="User resume url"),
        # TODO: This url is generated by the backend
        "photo_url": fields.String(required=False, description="User photo url"),
        "need_mentoring": fields.Boolean(
            required=False, description="User need mentoring indication"
        ),
        "available_to_mentor": fields.Boolean(
            required=False, description="User availability to mentor indication"
        ),
    },
)

resend_email_request_body_model = Model(
    "Resend email request data model",
    {"email": fields.String(required=True, description="User's email")},
)

home_response_body_model = Model(
    "Get statistics on the app usage of the current user",
    {
        "name": fields.String(required=True, description="The name of the user"),
        "pending_requests": fields.Integer(
            required=True, description="Number of pending requests"
        ),
        "accepted_requests": fields.Integer(
            required=True, description="Number of accepted requests"
        ),
        "completed_relations": fields.Integer(
            required=True, description="Number of completed relations"
        ),
        "cancelled_relations": fields.Integer(
            required=True, description="Number of cancelled relations"
        ),
        "rejected_requests": fields.Integer(
            required=True, description="Number of rejected relations"
        ),
        "achievements": fields.List(fields.Nested(list_tasks_response_body)),
    },
)

dashboard_relations_by_state_model = Model(
    "relations by state",
    {
        "accepted": fields.List(
            fields.Nested(mentorship_request_response_body_for_user_dashboard_body)
        ),
        "rejected": fields.List(
            fields.Nested(mentorship_request_response_body_for_user_dashboard_body)
        ),
        "completed": fields.List(
            fields.Nested(mentorship_request_response_body_for_user_dashboard_body)
        ),
        "cancelled": fields.List(
            fields.Nested(mentorship_request_response_body_for_user_dashboard_body)
        ),
        "pending": fields.List(
            fields.Nested(mentorship_request_response_body_for_user_dashboard_body)
        ),
    },
)

dashboard_sent_received_model = Model(
    "Get received and sent relations",
    {
        "sent": fields.Nested(dashboard_relations_by_state_model),
        "received": fields.Nested(dashboard_relations_by_state_model),
    },
)

dashboard_response_body_model = Model(
    "Get user dashboard",
    {
        "as_mentor": fields.Nested(dashboard_sent_received_model),
        "as_mentee": fields.Nested(dashboard_sent_received_model),
        "tasks_todo": fields.List(fields.Nested(list_tasks_response_body)),
        "tasks_done": fields.List(fields.Nested(list_tasks_response_body)),
    },
)

forgot_password_change_request_data_model = Model(
    "Forgot password change request data model",
    {
        "email": fields.String(required=True, description="User's email"),
    },
)
 
reset_password_forgot_request_data_model = Model(
    "Reset password forgot request data model",
    {
        "token": fields.String(required=True, description="User's access token to reset password"),
        "new_password": fields.String(required=True, description="Users's new password"),
    },
)

