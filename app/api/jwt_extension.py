from flask_jwt_extended import JWTManager
from http import HTTPStatus
from app import messages
from app.api.api_extension import api
import os

from app.api.dao.user import UserDAO

jwt = JWTManager()

# This is needed for the error handlers to work with flask-restplus
jwt._set_error_handler_callbacks(api)


@jwt.expired_token_loader
def my_expired_token_callback():
    return messages.TOKEN_HAS_EXPIRED, HTTPStatus.UNAUTHORIZED


@jwt.invalid_token_loader
def my_invalid_token_callback(error_message):
    return messages.TOKEN_IS_INVALID, HTTPStatus.UNAUTHORIZED


@jwt.unauthorized_loader
def my_unauthorized_request_callback(error_message):
    return messages.AUTHORISATION_TOKEN_IS_MISSING, HTTPStatus.UNAUTHORIZED


@jwt.user_identity_loader
def user_identity_lookup(identity):
    return identity["userID"]

    """Since there is no way of knowing in the encode_key_loader 
    if we are returning the key for the refresh token or the 
    access token we can modify the value we pass as identity 
    to the create_access_token and create_refresh_token methods"""


@jwt.encode_key_loader
def custom_encode_key(identity):
    secret = str(os.getenv("SECRET_KEY"))
    if identity["token_type"] == "access":
        return secret
    password_hash = UserDAO.get_user(identity["userID"]).password_hash
    return str(secret) + str(password_hash)


@jwt.decode_key_loader
def custom_decode_key(jwt_payload, jwt_headers):
    secret = str(os.getenv("SECRET_KEY"))
    if jwt_payload["type"] == "access":
        return secret
    else:
        password_hash = UserDAO.get_user(jwt_payload["identity"]).password_hash
        return str(secret) + str(password_hash)
