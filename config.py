import os
from datetime import timedelta


def get_mock_email_config() -> bool:
    MOCK_EMAIL = os.getenv("MOCK_EMAIL")

    # if MOCK_EMAIL env variable is set
    if MOCK_EMAIL:
        # MOCK_EMAIL is case insensitive
        MOCK_EMAIL = MOCK_EMAIL.lower()

        if MOCK_EMAIL == "true":
            return True
        elif MOCK_EMAIL == "false":
            return False
        else:
            # if MOCK_EMAIL env variable is set a wrong value
            raise ValueError(
                "MOCK_EMAIL environment variable is optional if set, it has to be valued as either 'True' or 'False'"
            )
    else:
        # Default behaviour is to send the email if MOCK_EMAIL is not set
        return False


class BaseConfig(object):
    """Base configuration."""

    DEBUG = False
    TESTING = False

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = 3600

    # Example:
    # MySQL: mysql+pymysql://{db_user}:{db_password}@{db_endpoint}/{db_name}
    # SQLite: sqlite:///local_data.db
    DB_TYPE = os.getenv("DB_TYPE", "")
    DB_USERNAME = os.getenv("DB_USERNAME", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_ENDPOINT = os.getenv("DB_ENDPOINT", "")
    DB_NAME = os.getenv("DB_NAME", "")
    DB_TEST_NAME = os.getenv("DB_TEST_NAME", "")
    DB_TEST_ENDPOINT = os.getenv("DB_TEST_ENDPOINT", DB_ENDPOINT)
    UNVERIFIED_USER_THRESHOLD = 2592000  # 30 days

    # Flask JWT settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(weeks=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(weeks=4)

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", None)
    # if not SECRET_KEY:
    #     raise ValueError('You need to export SECRET_KEY set for Flask application')

    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")

    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True

    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # mail settings
    MOCK_EMAIL = get_mock_email_config()
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # email authentication
    MAIL_USERNAME = os.getenv("APP_MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("APP_MAIL_PASSWORD")

    # mail accounts
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    @staticmethod
    def build_db_uri(
        db_type_arg=DB_TYPE,
        db_user_arg=DB_USERNAME,
        db_password_arg=DB_PASSWORD,
        db_endpoint_arg=DB_ENDPOINT,
        db_name_arg=DB_NAME,
    ):
        """Build remote database uri using specific environment variables."""

        return "{db_type}://{db_user}:{db_password}@{db_endpoint}/{db_name}".format(
            db_type=db_type_arg,
            db_user=db_user_arg,
            db_password=db_password_arg,
            db_endpoint=db_endpoint_arg,
            db_name=db_name_arg,
        )


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = BaseConfig.build_db_uri()
    MOCK_EMAIL = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = BaseConfig.build_db_uri()


class StagingConfig(BaseConfig):
    """Staging configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = BaseConfig.build_db_uri()
    MOCK_EMAIL = False


class LocalConfig(BaseConfig):
    """Local configuration."""

    DEBUG = True

    # Using a local sqlite database
    SQLALCHEMY_DATABASE_URI = "sqlite:///local_data.db"


class TestingConfig(BaseConfig):
    """Testing configuration."""

    TESTING = True
    MOCK_EMAIL = True

    # Use in-memory SQLite database for testing
    # SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_DATABASE_URI = BaseConfig.build_db_uri(
        db_name_arg=BaseConfig.DB_TEST_NAME, db_endpoint_arg=BaseConfig.DB_TEST_ENDPOINT
    )


def get_env_config() -> str:
    flask_config_name = os.getenv("FLASK_ENVIRONMENT_CONFIG", "dev")
    if flask_config_name not in ["prod", "test", "dev", "local", "stag"]:
        raise ValueError(
            "The environment config value has to be within these values: prod, dev, test, local, stag."
        )
    return CONFIGURATION_MAPPER[flask_config_name]


CONFIGURATION_MAPPER = {
    "dev": "config.DevelopmentConfig",
    "prod": "config.ProductionConfig",
    "stag": "config.StagingConfig",
    "local": "config.LocalConfig",
    "test": "config.TestingConfig",
}
