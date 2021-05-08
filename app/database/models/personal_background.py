### This is BridgeInTech backend extension ###
from sqlalchemy import null
from app.database.sqlalchemy_extension import db
from app.database.db_types.JsonCustomType import JsonCustomType
from app.utils.bitschema_utils import (
    Gender,
    Age,
    Ethnicity,
    SexualOrientation,
    Religion,
    PhysicalAbility,
    MentalAbility,
    SocioEconomic,
    HighestEducation,
    YearsOfExperience,
)


class PersonalBackgroundModel(db.Model):
    """Defines attributes for user's personal background.

    Attributes:
    user_id: An integer for storing the user's id.
    gender: A string for storing the user's gender.
    age: A string for storing the user's age.
    ethnicity: A string for storing the user's wthnicity.
    sexual_orientation: A string for storing the user's sexual orientation.
    religion: A string for storing the user's religion.
    physical_ability: A string for storing the user's physical ability.
    mental_ability: A string for storing the user's mental ability.
    socio_economic: A string for storing the user's socio economic level.
    highest_education: A string for storing the user's highest education level.
    years_of_experience: A string for storing the user's length of expeprience in the It related area.
    others: A JSON data type for storing users descriptions of 'other' fields.
    is_public: A boolean indicating if user has agreed to display their personal background information publicly to other members.
    """

    # Specifying database table used for PersonalBackgroundModel
    __tablename__ = "personal_backgrounds"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    # User's personal background data
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    gender = db.Column(db.Enum(Gender))
    age = db.Column(db.Enum(Age))
    ethnicity = db.Column(db.Enum(Ethnicity))
    sexual_orientation = db.Column(db.Enum(SexualOrientation))
    religion = db.Column(db.Enum(Religion))
    physical_ability = db.Column(db.Enum(PhysicalAbility))
    mental_ability = db.Column(db.Enum(MentalAbility))
    socio_economic = db.Column(db.Enum(SocioEconomic))
    highest_education = db.Column(db.Enum(HighestEducation))
    years_of_experience = db.Column(db.Enum(YearsOfExperience))
    others = db.Column(JsonCustomType)
    is_public = db.Column(db.Boolean)

    def __init__(
        self,
        user_id,
        gender,
        age,
        ethnicity,
        sexual_orientation,
        religion,
        physical_ability,
        mental_ability,
        socio_economic,
        highest_education,
        years_of_experience,
    ):
        """Initialises PersonalBackgroundModel class."""
        ## required fields
        self.user_id = user_id
        self.gender = gender
        self.age = age
        self.ethnicity = ethnicity
        self.sexual_orientation = sexual_orientation
        self.religion = religion
        self.physical_ability = physical_ability
        self.mental_ability = mental_ability
        self.socio_economic = socio_economic
        self.highest_education = highest_education
        self.years_of_experience = years_of_experience

        # default values
        self.others = None
        self.is_public = False

    def json(self):
        """Returns PersonalBackgroundModel object in json format."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "ethnicity": self.ethnicity,
            "sexual_orientation": self.sexual_orientation,
            "religion": self.religion,
            "physical_ability": self.physical_ability,
            "mental_ability": self.mental_ability,
            "socio_economic": self.socio_economic,
            "highest_education": self.highest_education,
            "years_of_experience": self.years_of_experience,
            "others": self.others,
            "is_public": self.is_public,
        }

    def __repr__(self):
        """Returns user's background."""

        return (
            f"User's id is {self.user_id}.\n"
            f"User's age is: {self.age}\n"
            f"User's ethnicity is: {self.ethnicity}\n"
            f"User's sexual orientation is: {self.sexual_orientation}\n"
            f"User's religion is: {self.religion}\n"
            f"User's physical ability is: {self.physical_ability}\n"
            f"User's mental ability is: {self.mental_ability}\n"
            f"User's socio economic category is: {self.socio_economic}\n"
            f"User's highest level of education is: {self.highest_education}\n"
            f"User's length of experience is: {self.years_of_experience}\n"
        )

    @classmethod
    def find_by_id(cls, _id: int) -> "PersonalBackgroundModel":
        """Returns the user's personal background that has the id we searched for."""
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_user_id(cls, user_id) -> "PersonalBackgroundModel":

        """Returns the user's background that has the passed user id.
        Args:
             _id: The id of a user.
        """
        return cls.query.filter_by(user_id=user_id).first()

    def save_to_db(self) -> None:
        """Adds user's personal background to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        """Deletes user's personal background from the database."""
        db.session.delete(self)
        db.session.commit()
