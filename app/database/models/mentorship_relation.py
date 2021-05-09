from datetime import date

from app.database.models.tasks_list import TasksListModel
from app.database.models.user import UserModel
from app.database.sqlalchemy_extension import db
from sqlalchemy.orm import validates
from app.utils.enum_utils import MentorshipRelationState


class MentorshipRelationModel(db.Model):
    """Data Model representation of a mentorship relation.

    Attributes:
        id: integer primary key that defines the mentorships.
        mentor_id: integer indicates the id of the mentor.
        mentee_id: integer indicates the id of the mentee.
        action_user_id: integer indicates id of action user.
        mentor: relationship between UserModel and mentorship_relation.
        mentee: relationship between UserModel and mentorship_relation.
        creation_date: float that defines the date of creation of the mentorship.
        accept_date: float that indicates the date of acceptance of mentorship.
        start_date: float that indicates the starting date of mentorship.
        end_date: float that indicates the ending date of mentorship.
        state: enumeration that indicates state of mentorship.
        notes: string that indicates any notes.
        tasks_list_id: integer indicates the id of the tasks_list
        tasks_list: relationship between TasksListModel and mentorship_relation.
    """

    # Specifying database table used for MentorshipRelationModel
    __tablename__ = "mentorship_relations"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    # personal data
    mentor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    mentee_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action_user_id = db.Column(db.Integer, nullable=False)
    mentor = db.relationship(
        UserModel,
        backref="mentor_relations",
        primaryjoin="MentorshipRelationModel.mentor_id == UserModel.id",
    )
    mentee = db.relationship(
        UserModel,
        backref="mentee_relations",
        primaryjoin="MentorshipRelationModel.mentee_id == UserModel.id",
    )

    creation_date = db.Column(db.Float, nullable=False)
    accept_date = db.Column(db.Float)
    start_date = db.Column(db.Float)
    end_date = db.Column(db.Float)

    state = db.Column(db.Enum(MentorshipRelationState), nullable=False)
    notes = db.Column(db.String(400))

    tasks_list_id = db.Column(db.Integer, db.ForeignKey("tasks_list.id"))
    tasks_list = db.relationship(
        TasksListModel, uselist=False, backref="mentorship_relation"
    )

    def __init__(
        self,
        action_user_id,
        mentor_user,
        mentee_user,
        creation_date,
        end_date,
        state,
        notes,
        tasks_list,
    ):

        self.action_user_id = action_user_id
        self.mentor = mentor_user
        self.mentee = mentee_user  # same as mentee_user.mentee_relations.append(self)
        self.creation_date = creation_date
        self.end_date = end_date
        self.state = state
        self.notes = notes
        self.tasks_list = tasks_list

    def json(self):
        """Returns information of mentorship as a json object."""
        return {
            "id": self.id,
            "action_user_id": self.action_user_id,
            "mentor_id": self.mentor_id,
            "mentee_id": self.mentee_id,
            "creation_date": self.creation_date,
            "accept_date": self.accept_date,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "state": self.state,
            "notes": self.notes,
        }

    # def __repr__(self):
    #     return f"Mentorship Relation with id = {self.id}, Mentor has id = {self.mentor_id} and Mentee has id = {self.mentee_id}"

    @classmethod
    def find_by_id(cls, _id) -> "MentorshipRelationModel":

        """Returns the mentorship that has the passed id.
        Args:
             _id: The id of a mentorship.
        """
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def is_empty(cls) -> bool:
        """Returns True if the mentorship model is empty, and False otherwise."""
        return cls.query.first() is None

    def save_to_db(self) -> None:
        """Saves the model to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """Deletes the record of mentorship relation from the database."""
        self.tasks_list.delete_from_db()
        db.session.delete(self)
        db.session.commit()

    @validates("notes")
    def validate(self, key, value):
        if key == "notes":
            if value is not None:
                value = str(value).strip()
                assert len(value.strip()) > 2
        return value
