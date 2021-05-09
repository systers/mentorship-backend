import time

from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

from app.database.sqlalchemy_extension import db
from app.utils.validation_utils import (
    is_name_valid,
    is_email_valid,
    is_username_valid,
)


class UserModel(db.Model):
    """Defines attributes for the user.

    Attributes:
        name: A string for storing the user's name.
        username: A string for storing the user's username.
        password: A string for storing the user's password.
        email: A string for storing user email.
        terms_and_conditions_checked: A boolean indicating if user has agreed to terms and conditions or not.
    """

    # Specifying database table used for UserModel
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    # personal data
    name = db.Column(db.String(30))
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(254), unique=True)

    # security
    password_hash = db.Column(db.String(100))

    # registration
    registration_date = db.Column(db.Float)
    terms_and_conditions_checked = db.Column(db.Boolean)

    # admin
    is_admin = db.Column(db.Boolean)

    # email verification
    is_email_verified = db.Column(db.Boolean)
    email_verification_date = db.Column(db.DateTime)

    # other info
    current_mentorship_role = db.Column(db.Integer)
    membership_status = db.Column(db.Integer)

    bio = db.Column(db.String(500))
    location = db.Column(db.String(80))
    occupation = db.Column(db.String(80))
    organization = db.Column(db.String(80))
    slack_username = db.Column(db.String(80))
    social_media_links = db.Column(db.String(500))
    skills = db.Column(db.String(500))
    interests = db.Column(db.String(200))
    resume_url = db.Column(db.String(200))
    photo_url = db.Column(db.String(200))

    need_mentoring = db.Column(db.Boolean)
    available_to_mentor = db.Column(db.Boolean)

    def __init__(self, name, username, password, email, terms_and_conditions_checked):
        """Initialises userModel class with name, username, password, email, and terms_and_conditions_checked."""
        ## required fields

        self.name = name
        self.username = username
        self.email = email
        self.terms_and_conditions_checked = terms_and_conditions_checked

        # saving hash instead of saving password in plain text
        self.set_password(password)

        # default values
        self.is_admin = True if self.is_empty() else False  # first user is admin
        self.is_email_verified = False
        self.registration_date = time.time()

        ## optional fields

        self.need_mentoring = False
        self.available_to_mentor = False

    def json(self):
        """Returns Usermodel object in json format."""
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "password_hash": self.password_hash,
            "email": self.email,
            "terms_and_conditions_checked": self.terms_and_conditions_checked,
            "registration_date": self.registration_date,
            "is_admin": self.is_admin,
            "is_email_verified": self.is_email_verified,
            "email_verification_date": self.email_verification_date,
            "current_mentorship_role": self.current_mentorship_role,
            "membership_status": self.membership_status,
            "bio": self.bio,
            "location": self.location,
            "occupation": self.occupation,
            "organization": self.organization,
            "slack_username": self.slack_username,
            "social_media_links": self.social_media_links,
            "skills": self.skills,
            "interests": self.interests,
            "resume_url": self.resume_url,
            "photo_url": self.photo_url,
            "need_mentoring": self.need_mentoring,
            "available_to_mentor": self.available_to_mentor,
        }

    def __repr__(self):
        """Returns the user's name and username."""
        return f"User name {self.name} . Username is {self.username} ."

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        """Returns the user that has the username we searched for."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        """Returns the user that has the email we searched for."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        """Returns the user that has the id we searched for."""
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_all_admins(cls, is_admin=True):
        """Returns all the admins."""
        return cls.query.filter_by(is_admin=is_admin).all()

    @classmethod
    def is_empty(cls) -> bool:
        """Returns a boolean if the Usermodel is empty or not."""
        return cls.query.first() is None

    def set_password(self, password_plain_text: str) -> None:
        """Sets user password when they create an account or when they are changing their password."""
        self.password_hash = generate_password_hash(password_plain_text)

    # checks if password is the same, using its hash
    def check_password(self, password_plain_text: str) -> bool:
        """Returns a boolean if password is the same as it hash or not."""
        return check_password_hash(self.password_hash, password_plain_text)

    def save_to_db(self) -> None:
        """Adds a user to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """Deletes a user from the database."""
        db.session.delete(self)
        db.session.commit()

    @validates("username", "name", "email", "terms_and_conditions_checked")
    def validate(self, key, value):
        if key == "username":
            assert is_username_valid(value)
        elif key == "name":
            assert is_name_valid(value)
        elif key == "email":
            assert is_email_valid(value)
        elif key == "terms_and_conditions_checked":
            assert value is True
        return value
