from datetime import datetime

from app.api.validations.task_comment import COMMENT_MAX_LENGTH
from app.database.sqlalchemy_extension import db
from sqlalchemy.orm import validates


class TaskCommentModel(db.Model):
    """Defines attributes for the task comment.

    Attributes:
        task_id: An integer for storing the task's id.
        user_id: An integer for storing the user's id.
        relation_id: An integer for storing the relation's id.
        creation_date: A float indicating comment's creation date.
        modification_date: A float indicating the modification date.
        comment: A string indicating the comment.
    """

    # Specifying database table used for TaskCommentModel
    __tablename__ = "tasks_comments"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    task_id = db.Column(db.Integer, db.ForeignKey("tasks_list.id"))
    relation_id = db.Column(db.Integer, db.ForeignKey("mentorship_relations.id"))
    creation_date = db.Column(db.Float, nullable=False)
    modification_date = db.Column(db.Float)
    comment = db.Column(db.String(COMMENT_MAX_LENGTH), nullable=False)

    def __init__(self, user_id, task_id, relation_id, comment):
        # required fields
        self.user_id = user_id
        self.task_id = task_id
        self.relation_id = relation_id
        self.comment = comment

        # default fields
        self.creation_date = datetime.utcnow().timestamp()

    def json(self):
        """Returns information of task comment as a JSON object."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "relation_id": self.relation_id,
            "creation_date": self.creation_date,
            "modification_date": self.modification_date,
            "comment": self.comment,
        }

    def __repr__(self):
        """Returns the task and user ids, creation date and the comment."""
        return (
            f"User's id is {self.user_id}. Task's id is {self.task_id}. "
            f"Comment was created on: {self.creation_date}\n"
            f"Comment: {self.comment}"
        )

    @classmethod
    def find_by_id(cls, _id):
        """Returns the task comment that has the passed id.
        Args:
             _id: The id of the task comment.
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all_by_task_id(cls, task_id, relation_id):
        """Returns all task comments that has the passed task id.
        Args:
             task_id: The id of the task.
             relation_id: The id of the relation.
        """
        return cls.query.filter_by(task_id=task_id, relation_id=relation_id).all()

    @classmethod
    def find_all_by_user_id(cls, user_id):
        """Returns all task comments that has the passed user id.
        Args:
             user_id: The id of the user.
        """
        return cls.query.filter_by(user_id=user_id).all()

    def modify_comment(self, comment):
        """Changes the comment and the modification date.
        Args:
             comment: New comment.
        """
        self.comment = comment
        self.modification_date = datetime.utcnow().timestamp()

    @classmethod
    def is_empty(cls):
        """Returns a boolean if the TaskCommentModel is empty or not."""
        return cls.query.first() is None

    def save_to_db(self):
        """Adds a comment task to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """Deletes a comment task from the database."""
        db.session.delete(self)
        db.session.commit()

    @validates("comment")
    def validate(self, key, value):
        if key == "comment":
            assert value is not None
            value = str(value).strip()
            assert len(value) > 2
        return value
