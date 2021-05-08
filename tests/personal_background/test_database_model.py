import unittest
from tests.base_test_case import BaseTestCase
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
from app.database.models.user import UserModel
from app.database.models.personal_background import PersonalBackgroundModel
from app.database.sqlalchemy_extension import db
from app.database.db_types.JsonCustomType import JsonCustomType
from tests.test_data import user1, user2

# Testing User's Personal background database model
class TestPersonalBackgroundModel(BaseTestCase):
    def setUp(self):
        super().setUp()

        # Add a user1 into the database
        user_1 = UserModel(
            name=user1["name"],
            email=user1["email"],
            username=user1["username"],
            password=user1["password"],
            terms_and_conditions_checked=user1["terms_and_conditions_checked"],
        )

        # Add a user2 into the database
        user_2 = UserModel(
            name=user2["name"],
            email=user2["email"],
            username=user2["username"],
            password=user2["password"],
            terms_and_conditions_checked=user2["terms_and_conditions_checked"],
        )

        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

        self.user1 = UserModel.query.filter_by(email=user_1.email).first()
        self.user2 = UserModel.query.filter_by(email=user_2.email).first()

        # add user2 personal_background
        self.user2_background = PersonalBackgroundModel(
            user_id=self.user2.id,
            gender=Gender.FEMALE,
            age=Age.AGE_25_TO_34,
            ethnicity=Ethnicity.CAUCASIAN,
            sexual_orientation=SexualOrientation.LGBTQIA,
            religion=Religion.OTHER,
            physical_ability=PhysicalAbility.WITHOUT_DISABILITY,
            mental_ability=MentalAbility.WITHOUT_DISORDER,
            socio_economic=SocioEconomic.LOWER_MIDDLE,
            highest_education=HighestEducation.BACHELOR,
            years_of_experience=YearsOfExperience.UP_TO_10,
        )
        self.user2_background.others = {"religion": "Daoism"}
        self.user2_background.is_public = True

        db.session.add(self.user2_background)
        db.session.commit()

    def test_user1_background_not_exist(self):

        user1_background = PersonalBackgroundModel.query.filter_by(
            user_id=self.user1.id
        ).first()
        self.assertIsNone(user1_background)

    def test_user2_background_creation(self):
        background = PersonalBackgroundModel.query.filter_by(
            user_id=self.user2.id
        ).first()
        self.assertIsNotNone(background)
        self.assertIsNotNone(background.id)
        self.assertTrue(background.user_id, self.user2_background.user_id)
        self.assertTrue(background.gender == self.user2_background.gender)
        self.assertTrue(background.age == self.user2_background.age)
        self.assertTrue(background.ethnicity == self.user2_background.ethnicity)
        self.assertTrue(
            background.sexual_orientation == self.user2_background.sexual_orientation
        )
        self.assertTrue(background.religion == self.user2_background.religion)
        self.assertTrue(
            background.physical_ability == self.user2_background.physical_ability
        )
        self.assertTrue(
            background.mental_ability == self.user2_background.mental_ability
        )
        self.assertTrue(
            background.socio_economic == self.user2_background.socio_economic
        )
        self.assertTrue(
            background.highest_education == self.user2_background.highest_education
        )
        self.assertTrue(
            background.years_of_experience == self.user2_background.years_of_experience
        )
        self.assertTrue(background.others == self.user2_background.others)
        self.assertTrue(background.is_public == self.user2_background.is_public)

    def test_personal_background_update(self):
        # user change their personal background info
        self.user2_background.gender = Gender.OTHER

        db.session.add(self.user2_background)
        db.session.commit()

        background = PersonalBackgroundModel.query.filter_by(
            user_id=self.user2.id
        ).first()

        self.assertTrue(background.gender, Gender.OTHER)

    def test_personal_background_json_representation(self):
        expected_json = {
            "id": self.user2_background.id,
            "user_id": self.user2_background.user_id,
            "age": self.user2_background.age,
            "ethnicity": self.user2_background.ethnicity,
            "sexual_orientation": self.user2_background.sexual_orientation,
            "religion": self.user2_background.religion,
            "physical_ability": self.user2_background.physical_ability,
            "mental_ability": self.user2_background.mental_ability,
            "socio_economic": self.user2_background.socio_economic,
            "highest_education": self.user2_background.highest_education,
            "years_of_experience": self.user2_background.years_of_experience,
            "others": self.user2_background.others,
            "is_public": self.user2_background.is_public,
        }
        self.assertEqual(expected_json, self.user2_background.json())

    def test_find_personal_background_by_user_id(self):
        query_personal_background = PersonalBackgroundModel.query.filter_by(
            user_id=self.user2_background.user_id
        ).first()
        find_by_user_id_result = PersonalBackgroundModel.find_by_user_id(
            query_personal_background.user_id
        )
        self.assertEqual(query_personal_background, find_by_user_id_result)

    def test_find_personal_background_by_id(self):
        query_personal_background = PersonalBackgroundModel.query.first()
        find_by_id_result = PersonalBackgroundModel.find_by_id(
            query_personal_background.id
        )
        self.assertEqual(query_personal_background, find_by_id_result)


if __name__ == "__main__":
    unittest.main()
