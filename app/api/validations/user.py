from app import messages
from app.utils.validation_utils import (
    is_name_valid,
    is_email_valid,
    is_username_valid,
    validate_length,
    get_stripped_string,
)

# Field character limit

NAME_MAX_LENGTH = 30
NAME_MIN_LENGTH = 2
USERNAME_MAX_LENGTH = 25
USERNAME_MIN_LENGTH = 5
PASSWORD_MAX_LENGTH = 64
PASSWORD_MIN_LENGTH = 8

BIO_MAX_LENGTH = 450
LOCATION_MAX_LENGTH = 60
OCCUPATION_MAX_LENGTH = 60
ORGANIZATION_MAX_LENGTH = 60
SLACK_USERNAME_MAX_LENGTH = 60
SKILLS_MAX_LENGTH = 450
INTERESTS_MAX_LENGTH = 150
SOCIALS_MAX_LENGTH = 400


def validate_user_registration_request_data(data):
    # Verify if request body has required fields
    if "name" not in data:
        return messages.NAME_FIELD_IS_MISSING
    if "username" not in data:
        return messages.USERNAME_FIELD_IS_MISSING
    if "password" not in data:
        return messages.PASSWORD_FIELD_IS_MISSING
    if "email" not in data:
        return messages.EMAIL_FIELD_IS_MISSING
    if "terms_and_conditions_checked" not in data:
        return messages.TERMS_AND_CONDITIONS_FIELD_IS_MISSING

    name = data["name"]
    username = data["username"]
    password = data["password"]
    email = data["email"]
    terms_and_conditions_checked = data["terms_and_conditions_checked"]

    if not (
        isinstance(name, str)
        and isinstance(username, str)
        and isinstance(password, str)
    ):
        return messages.NAME_USERNAME_AND_PASSWORD_NOT_IN_STRING_FORMAT

    if " " in password:
        return messages.USER_INPUTS_SPACE_IN_PASSWORD

    is_valid = validate_length(
        len(get_stripped_string(name)), NAME_MIN_LENGTH, NAME_MAX_LENGTH, "name"
    )
    if not is_valid[0]:
        return is_valid[1]

    is_valid = validate_length(
        len(get_stripped_string(username)),
        USERNAME_MIN_LENGTH,
        USERNAME_MAX_LENGTH,
        "username",
    )
    if not is_valid[0]:
        return is_valid[1]

    is_valid = validate_length(
        len(get_stripped_string(password)),
        PASSWORD_MIN_LENGTH,
        PASSWORD_MAX_LENGTH,
        "password",
    )
    if not is_valid[0]:
        return is_valid[1]

    # Verify business logic of request body
    if not terms_and_conditions_checked:
        return messages.TERMS_AND_CONDITIONS_ARE_NOT_CHECKED

    if not is_name_valid(name):
        return messages.NAME_INPUT_BY_USER_IS_INVALID

    if not is_email_valid(email):
        return messages.EMAIL_INPUT_BY_USER_IS_INVALID

    if not is_username_valid(username):
        return messages.USERNAME_INPUT_BY_USER_IS_INVALID

    return {}


def validate_resend_email_request_data(data):
    # Verify if request body has required fields
    if "email" not in data:
        return messages.EMAIL_FIELD_IS_MISSING

    email = data["email"]
    if not is_email_valid(email):
        return messages.EMAIL_INPUT_BY_USER_IS_INVALID

    return {}


def validate_update_profile_request_data(data):
    # todo this does not check if non expected fields are being sent

    if not data:
        return messages.NO_DATA_FOR_UPDATING_PROFILE_WAS_SENT

    username = data.get("username", None)
    if username:
        is_valid = validate_length(
            len(get_stripped_string(username)),
            USERNAME_MIN_LENGTH,
            USERNAME_MAX_LENGTH,
            "username",
        )
        if not is_valid[0]:
            return is_valid[1]

        if not is_username_valid(username):
            return messages.NEW_USERNAME_INPUT_BY_USER_IS_INVALID

    name = data.get("name", None)
    if name:
        is_valid = validate_length(
            len(get_stripped_string(name)), NAME_MIN_LENGTH, NAME_MAX_LENGTH, "name"
        )
        if not is_valid[0]:
            return is_valid[1]

        if not is_name_valid(name):
            return messages.NAME_INPUT_BY_USER_IS_INVALID

    bio = data.get("bio", None)
    if bio:
        is_valid = validate_length(
            len(get_stripped_string(bio)), 0, BIO_MAX_LENGTH, "bio"
        )
        if not is_valid[0]:
            return is_valid[1]

    location = data.get("location", None)
    if location:
        is_valid = validate_length(
            len(get_stripped_string(location)), 0, LOCATION_MAX_LENGTH, "location"
        )
        if not is_valid[0]:
            return is_valid[1]

    occupation = data.get("occupation", None)
    if occupation:
        is_valid = validate_length(
            len(get_stripped_string(occupation)), 0, OCCUPATION_MAX_LENGTH, "occupation"
        )
        if not is_valid[0]:
            return is_valid[1]

    current_organization = data.get("current_organization", None)
    if current_organization:
        is_valid = validate_length(
            len(get_stripped_string(current_organization)),
            0,
            ORGANIZATION_MAX_LENGTH,
            "current_organization",
        )
        if not is_valid[0]:
            return is_valid[1]

    slack_username = data.get("slack_username", None)
    if slack_username:
        is_valid = validate_length(
            len(get_stripped_string(slack_username)),
            0,
            SLACK_USERNAME_MAX_LENGTH,
            "slack_username",
        )
        if not is_valid[0]:
            return is_valid[1]

    social_media_links = data.get("social_media_links", None)
    if social_media_links:
        is_valid = validate_length(
            len(get_stripped_string(social_media_links)),
            0,
            SOCIALS_MAX_LENGTH,
            "social_media_links",
        )
        if not is_valid[0]:
            return is_valid[1]

    skills = data.get("skills", None)
    if skills:
        is_valid = validate_length(
            len(get_stripped_string(skills)), 0, SKILLS_MAX_LENGTH, "skills"
        )
        if not is_valid[0]:
            return is_valid[1]

    interests = data.get("interests", None)
    if interests:
        is_valid = validate_length(
            len(get_stripped_string(interests)), 0, INTERESTS_MAX_LENGTH, "interests"
        )
        if not is_valid[0]:
            return is_valid[1]

    if "need_mentoring" in data and data["need_mentoring"] is None:
        return messages.FIELD_NEED_MENTORING_IS_NOT_VALID

    if "available_to_mentor" in data and data["available_to_mentor"] is None:
        return messages.FIELD_AVAILABLE_TO_MENTOR_IS_INVALID

    return {}


def validate_new_password(data):
    if "current_password" not in data:
        return messages.CURRENT_PASSWORD_FIELD_IS_MISSING
    if "new_password" not in data:
        return messages.NEW_PASSWORD_FIELD_IS_MISSING

    current_password = data["current_password"]
    new_password = data["new_password"]

    if current_password == new_password:
        return messages.USER_ENTERED_CURRENT_PASSWORD

    if " " in new_password:
        return messages.USER_INPUTS_SPACE_IN_PASSWORD

    is_valid = validate_length(
        len(get_stripped_string(new_password)),
        PASSWORD_MIN_LENGTH,
        PASSWORD_MAX_LENGTH,
        "new_password",
    )
    if not is_valid[0]:
        return is_valid[1]

    return {}
