from flask_jwt_extended import create_access_token, create_refresh_token


def get_test_request_header(user_identity, token_expiration_delta=None, refresh=False):
    """
    This function returns the header needed to access auth protected
    endpoints
    :param token_expiration_delta: time for the token to expire
    :param user_identity: identifier of the user
    :param refresh: True if refresh token
    :return: header dict with Authorization field
    """
    if refresh:
        token = create_refresh_token(
            identity={"userID": user_identity, "token_type": "refresh"},
            expires_delta=token_expiration_delta,
        )
    else:
        token = create_access_token(
            identity={"userID": user_identity, "token_type": "access"},
            expires_delta=token_expiration_delta,
        )
    header = {"Authorization": "Bearer {}".format(token)}
    return header
