from flask_restplus import fields, Model
from app.run import api
#from app.api.resources.user import ns


def add_models_to_namespace(api_namespace):
    api.models[public_user_api_model.name] = public_user_api_model
    api.models[full_user_api_model.name] = full_user_api_model
    api.models[register_user_api_model.name] = register_user_api_model

public_user_api_model = Model('User list model', {
    'id': fields.Integer(
        readOnly=True,
        description='The unique identifier of a user'
    ),
    'name': fields.String(
        required=True,
        description='User name'
    ),
    'username': fields.String(
        required=True,
        description='User username'
    ),
    'email': fields.String(
        required=True,
        description='User email'
    )
})

full_user_api_model = Model('User Complete model used in listing', {
    'id': fields.Integer(
        readOnly=True,
        description='The unique identifier of a user'
    ),
    'name': fields.String(
        required=True,
        description='User name'
    ),
    'username': fields.String(
        required=True,
        description='User username'
    ),
    'password': fields.String(
        required=True,
        description='User password'
    ),
    'security_question': fields.String(
        required=True,
        description='User security question'
    ),
    'security_answer': fields.String(
        required=True,
        description='User security answer'
    ),
    'terms_and_conditions_checked': fields.Boolean(
        required=True,
        description='User Terms and Conditions check state'
    ),
    'is_admin': fields.Boolean(
        required=True,
        description='User admin status'
    ),
    'registration_date': fields.DateTime(
        required=True,
        description='User registration date'
    ),
    'is_email_verified': fields.Boolean(
        required=True,
        description='User email verification status'
    ),
    'email_verification_date': fields.DateTime(
        required=False,
        description='User email verification date'
    )
})

register_user_api_model = Model('User registration model', {
    'name': fields.String(required=True, description='User name'),
    'username': fields.String(required=True, description='User username'),
    'password': fields.String(required=True, description='User password'),
    'email': fields.String(required=True, description='User email'),
    'security_question': fields.String(required=True, description='User\' security question'),
    'security_answer': fields.String(required=True, description='User\' security answer'),
    'terms_and_conditions_checked': fields.Boolean(required=True, description='User check Terms and Conditions value'),
})
