import unittest
from random import SystemRandom
from string import ascii_lowercase

from app import messages
from app.api.validations.user import (
    validate_update_profile_request_data,
    OCCUPATION_MAX_LENGTH,
    ORGANIZATION_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)
from app.utils.validation_utils import get_length_validation_error_message


class TestUpdateUserApiRequestDataValidation(unittest.TestCase):
    def test_update_user_request_data_validation_with_no_data(self):
        request_body = dict()
        expected_result = messages.NO_DATA_FOR_UPDATING_PROFILE_WAS_SENT
        actual_result = validate_update_profile_request_data(request_body)

        self.assertDictEqual(expected_result, actual_result)

    def test_update_user_occupation_request_data_validation(self):
        secure_random = SystemRandom()
        random_generated_occupation = "".join(
            secure_random.choice(ascii_lowercase)
            for x in range(OCCUPATION_MAX_LENGTH + 1)
        )
        field_name = "occupation"
        request_body = dict(occupation=random_generated_occupation)

        expected_result = {
            "message": get_length_validation_error_message(
                field_name, None, OCCUPATION_MAX_LENGTH
            )
        }
        actual_result = validate_update_profile_request_data(request_body)

        self.assertEqual(expected_result, actual_result)

    def test_update_user_organization_request_data_validation(self):
        secure_random = SystemRandom()
        random_generated_organization = "".join(
            secure_random.choice(ascii_lowercase)
            for x in range(ORGANIZATION_MAX_LENGTH + 1)
        )
        field_name = "current_organization"
        request_body = dict(current_organization=random_generated_organization)

        expected_result = {
            "message": get_length_validation_error_message(
                field_name, None, ORGANIZATION_MAX_LENGTH
            )
        }
        actual_result = validate_update_profile_request_data(request_body)

        self.assertEqual(expected_result, actual_result)

    def test_update_user_username_request_data_validation(self):
        secure_random = SystemRandom()
        random_generated_username = "".join(
            secure_random.choice(ascii_lowercase)
            for x in range(USERNAME_MAX_LENGTH + 1)
        )
        field_name = "username"
        request_body = dict(username=random_generated_username)

        expected_result = {
            "message": get_length_validation_error_message(
                field_name, USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH
            )
        }
        actual_result = validate_update_profile_request_data(request_body)

        self.assertEqual(expected_result, actual_result)

    # todo test other fields


if __name__ == "__main__":
    unittest.main()
