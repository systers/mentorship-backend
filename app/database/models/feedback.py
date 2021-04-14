from app.database.models.user import UserModel
from app.database.sqlalchemy_extension import db
from enum import IntEnum,unique
from app.utils.enum_utils import Rating

class FeedbackModel(db.model):

    __tablename__ = 'Feedback'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    relation_id = db.Column(db.Integer,
                            db.ForeignKey('mentorship_relations.id'))
    feedback = db.Column(db.String(1000))
    rating = db.Column(db.Enum(Rating), nullable=False)
    submission_date = db.Column(db.Float, nullable=False)

    def __init__(self, feedback, rating):
        feedback = self.feedback
        rating = self.rating

    def add_feedback(self, feedback, rating, created_at):
        """ Adds feedback by mentee """

        self.feedback = feedback
        self.rating = rating
        self.submission_date = created_at

    @classmethod
    def find_by_id(cls, _id):
        """Returns the feedback that has the passed id.
           Args:
                _id: The id of a feedback.
        """

        return cls.query.filter_by(id=_id).first()

    @classmethod
    def is_empty(cls):
        """Returns True if the feedback model is empty, and False otherwise."""

        return cls.query.first() is None

    def save_to_db(self):
        """Saves the model to the database."""

        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """Deletes the record of mentorship relation from the database."""

        self.tasks_list.delete_from_db()
        db.session.delete(self)
        db.session.commit()
