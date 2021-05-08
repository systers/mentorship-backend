from flask import Flask
from config import get_env_config
from flask_migrate import Migrate, MigrateCommand


def create_app(config_filename: str) -> Flask:
    app = Flask(__name__)

    # setup application environment
    app.config.from_object(config_filename)
    app.url_map.strict_slashes = False

    from app.database.sqlalchemy_extension import db

    db.init_app(app)

    # mentorship backend models
    from app.database.models.user import UserModel
    from app.database.models.mentorship_relation import (
        MentorshipRelationModel,
    )
    from app.database.models.tasks_list import TasksListModel
    from app.database.models.task_comment import TaskCommentModel

    # bridge-in-tech backend models
    from app.database.models.personal_background import (
        PersonalBackgroundModel,
    )

    migrate = Migrate(app, db, render_as_batch=True)

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

    # mentoship backend models
    from app.database.models.user import UserModel
    from app.database.models.mentorship_relation import (
        MentorshipRelationModel,
    )
    from app.database.models.tasks_list import TasksListModel
    from app.database.models.task_comment import TaskCommentModel

    # bridge-in-tech backend models
    from app.database.models.personal_background import (
        PersonalBackgroundModel,
    )

    db.create_all()

    @application.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            # mentorship backend models
            "UserModel": UserModel,
            "MentorshipRelationModel": MentorshipRelationModel,
            "TaskListModel": TasksListModel,
            "TaskCommentModel": TaskCommentModel,
            # bridge-in-tech backend models
            "PersonalBackgroundModel": PersonalBackgroundModel,
        }


if __name__ == "__main__":
    application.run(port=5000)
