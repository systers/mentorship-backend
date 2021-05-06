from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify, make_response, request

from app.rate_limits import GLOBAL_LIMIT

limiter = Limiter(key_func=get_remote_address, default_limits=GLOBAL_LIMIT)


def rate_limit_exceeded(e):
    return make_response(jsonify(error=f"rate limit exceeded: {e.description}"), 429)
