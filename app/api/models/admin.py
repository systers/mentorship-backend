from flask_restx import fields, Model


def add_models_to_namespace(api_namespace):
    api_namespace.models[
        assign_and_revoke_user_admin_request_body.name
    ] = assign_and_revoke_user_admin_request_body
    api_namespace.models[public_admin_user_api_model.name] = public_admin_user_api_model


assign_and_revoke_user_admin_request_body = Model(
    "Assign User model",
    {
        "user_id": fields.Integer(
            required=True, description="The unique identifier of a user"
        )
    },
)


public_admin_user_api_model = Model(
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
        "current_organization": fields.String(required=True, description="User current organization"),
        "skills": fields.String(required=True, description="User skills"),
    },
)
