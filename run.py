from flask import Flask
from config import get_env_config
from flask_migrate import Migrate
from app.rate_limiter import limiter, rate_limit_exceeded


def create_app(config_filename: str) -> Flask:
    app = Flask(__name__)
    # initialize flask limiter
    limiter.init_app(app)
    # setup application environment
    app.config.from_object(config_filename)
    app.url_map.strict_slashes = False
    # error handler for when rate limit is exceeded
    app.register_error_handler(429, rate_limit_exceeded)
    from app.database.sqlalchemy_extension import db

    db.init_app(app)

    migrate = Migrate(app, db)

    from app.api.jwt_extension import jwt

    jwt.init_app(app)

    from app.api.api_extension import api

    api.init_app(app)

    from app.api.mail_extension import mail

    mail.init_app(app)

    from app.schedulers.background_scheduler import init_schedulers

    init_schedulers()

    return app


application = create_app(get_env_config())


@application.before_first_request
def create_tables():
    from app.database.sqlalchemy_extension import db

    db.create_all()


if __name__ == "__main__":
    application.run(port=5000)
