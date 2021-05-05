from app.api.validations.user import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
)

# Invalid fields
NAME_INPUT_BY_USER_IS_INVALID = {"message": "Your name is invalid."}
EMAIL_INPUT_BY_USER_IS_INVALID = {"message": "Your email is invalid."}
USERNAME_INPUT_BY_USER_IS_INVALID = {"message": "Your username is invalid."}
NEW_USERNAME_INPUT_BY_USER_IS_INVALID = {"message": "Your new username is" " invalid."}
TOKEN_IS_INVALID = {"message": "The token is invalid!"}
USER_ID_IS_NOT_VALID = {"message": "User id is not valid."}
FIELD_NEED_MENTORING_IS_NOT_VALID = {"message": "Field need_mentoring is" " not valid."}
FIELD_AVAILABLE_TO_MENTOR_IS_INVALID = {
    "message": "Field available_to_mentor" " is not valid."
}
INVALID_INPUT = {"message": "Invalid input."}
PASSWORD_INPUT_BY_USER_HAS_INVALID_LENGTH = {
    "message": f"The password field has to be longer than {PASSWORD_MIN_LENGTH - 1} characters and shorter than {PASSWORD_MAX_LENGTH + 1} characters."
}

# Not found
MENTORSHIP_RELATION_REQUEST_DOES_NOT_EXIST = {
    "message": "This mentorship" " relation request does not" " exist."
}
MENTORSHIP_RELATION_DOES_NOT_EXIST = {
    "message": "Mentorship relation does not" " exist."
}
USER_NOT_FOUND = {"message": "User not found."}
MENTOR_DOES_NOT_EXIST = {"message": "Mentor user does not exist."}
MENTEE_DOES_NOT_EXIST = {"message": "Mentee user does not exist."}
TASK_DOES_NOT_EXIST = {"message": "Task does not exist."}
USER_DOES_NOT_EXIST = {"message": "User does not exist."}
TASK_COMMENT_DOES_NOT_EXIST = {"message": "Task comment does not exist."}
TASK_COMMENT_WITH_GIVEN_TASK_ID_DOES_NOT_EXIST = {
    "message": "Task comment with given task id does not exist."
}

# Missing fields
MENTOR_ID_FIELD_IS_MISSING = {"message": "Mentor ID field is missing."}
MENTEE_ID_FIELD_IS_MISSING = {"message": "Mentee ID field is missing."}
END_DATE_FIELD_IS_MISSING = {"message": "End date field is missing."}
NOTES_FIELD_IS_MISSING = {"message": "Notes field is missing."}
USERNAME_FIELD_IS_MISSING = {"message": "The field username is missing."}
PASSWORD_FIELD_IS_MISSING = {"message": "Password field is missing."}
NAME_FIELD_IS_MISSING = {"message": "Name field is missing."}
EMAIL_FIELD_IS_MISSING = {"message": "Email field is missing."}
TERMS_AND_CONDITIONS_FIELD_IS_MISSING = {
    "message": "Terms and conditions" " field is missing."
}
CURRENT_PASSWORD_FIELD_IS_MISSING = {"message": "Current password field is" " missing."}
NEW_PASSWORD_FIELD_IS_MISSING = {"message": "New password field is missing."}
AUTHORISATION_TOKEN_IS_MISSING = {"message": "The authorization token is" " missing!"}
DESCRIPTION_FIELD_IS_MISSING = {"message": "Description field is missing."}
COMMENT_FIELD_IS_MISSING = {"message": "Comment field is missing."}
USERNAME_HAS_INVALID_LENGTH = {
    "message": f"The username field has to be longer than {USERNAME_MIN_LENGTH - 1} characters and shorter than {USERNAME_MAX_LENGTH + 1} characters."
}

# Admin
USER_IS_ALREADY_AN_ADMIN = {"message": "User is already an Admin."}
USER_CANNOT_BE_ASSIGNED_ADMIN_BY_USER = {
    "message": "You cannot assign" " yourself as an Admin."
}
USER_IS_NOT_AN_ADMIN = {"message": "User is not an Admin."}
USER_ADMIN_STATUS_WAS_REVOKED = {"message": "User admin status was revoked."}
USER_CANT_DELETE = {
    "message": "You cannot delete your account, since you are" " the only Admin left."
}
USER_CANNOT_REVOKE_ADMIN_STATUS = {"message": "You cannot revoke your admin" "status."}
USER_ASSIGN_NOT_ADMIN = {
    "message": "You don't have admin status. You can't" " assign other user as admin."
}
USER_REVOKE_NOT_ADMIN = {
    "message": "You don't have admin status. You can't" " revoke other admin user."
}
USER_IS_NOW_AN_ADMIN = {"message": "User is now an Admin."}

# Mentor availability
MENTOR_NOT_AVAILABLE_TO_MENTOR = {
    "message": "Mentor user is not available to" " mentor."
}
MENTOR_ALREADY_IN_A_RELATION = {"message": "Mentor user is already in a relationship."}

# Mentee availability
MENTEE_NOT_AVAIL_TO_BE_MENTORED = {
    "message": "Mentee user is not available" " to be mentored."
}
MENTEE_ALREADY_IN_A_RELATION = {
    "message": "Mentee user is already in a" " relationship."
}

# Mismatch of fields
MATCH_EITHER_MENTOR_OR_MENTEE = {
    "message": "Your ID has to match either" " Mentor or Mentee IDs."
}
TASK_COMMENT_WAS_NOT_CREATED_BY_YOU = {
    "message": "You have not created the comment and therefore cannot " "modify it."
}
TASK_COMMENT_WAS_NOT_CREATED_BY_YOU_DELETE = {
    "message": "You have not created the comment and therefore cannot " "delete it."
}

# Update
NO_DATA_FOR_UPDATING_PROFILE_WAS_SENT = {
    "message": "No data for updating profile was sent."
}

# Relation constraints
MENTOR_ID_SAME_AS_MENTEE_ID = {
    "message": "You cannot have a mentorship" " relation with yourself."
}
END_TIME_BEFORE_PRESENT = {"message": "End date is invalid since date has" " passed."}
MENTOR_TIME_GREATER_THAN_MAX_TIME = {
    "message": "Mentorship relation maximum" " duration is 6 months."
}
MENTOR_TIME_LESS_THAN_MIN_TIME = {
    "message": "Mentorship relation minimum" " duration is 4 week."
}
CANT_ACCEPT_MENTOR_REQ_SENT_BY_USER = {
    "message": "You cannot accept a" " mentorship request sent by yourself."
}
CANT_ACCEPT_UNINVOLVED_MENTOR_RELATION = {
    "message": "You cannot accept a"
    " mentorship relation where you are"
    " not involved."
}
USER_CANT_REJECT_REQUEST_SENT_BY_USER = {
    "message": "You cannot reject a" " mentorship request sent by yourself."
}
CANT_REJECT_UNINVOLVED_RELATION_REQUEST = {
    "message": "You cannot reject a"
    " mentorship relation where you are"
    " not involved."
}
CANT_CANCEL_UNINVOLVED_REQUEST = {
    "message": "You cannot cancel a mentorship" " relation where you are not involved."
}
CANT_DELETE_REQUEST_YOU_DIDNT_CREATE = {
    "message": "You cannot delete a mentorship" " request that you did not create."
}
NOT_IN_MENTORED_RELATION_CURRENTLY = {
    "message": "You are not in a current" " mentorship relation."
}
USER_IS_INVOLVED_IN_A_MENTORSHIP_RELATION = {
    "message": "You are currently" " involved in a" " mentorship relation."
}
USER_NOT_INVOLVED_IN_THIS_MENTOR_RELATION = {
    "message": "You are not involved" " in this mentorship relation."
}
USER_USES_A_USERNAME_THAT_ALREADY_EXISTS = {
    "message": "A user with that" " username already exists."
}
USER_USES_AN_EMAIL_ID_THAT_ALREADY_EXISTS = {
    "message": "A user with that " "email already exists."
}
USER_IS_NOT_REGISTERED_IN_THE_SYSTEM = {
    "message": "You are not registered in the system."
}
NAME_LENGTH_GREATER_THAN_MAX_LIMIT = {
    "message": "The {field_name} field has"
    " to be shorter than {max_limit}"
    " characters."
}
NAME_LENGTH_LESSER_THAN_MAX_LIMIT = {
    "message": "The {field_name} field has to"
    " be longer than {min_limit} characters"
    " and shorter than {max_limit}"
    " characters."
}
USER_INPUTS_INCORRECT_CONFIGURATION_VALUE = {
    "message": "The environment"
    " config value has to be within"
    " these values: prod,"
    "dev, test."
}

# Mentorship state
NOT_PENDING_STATE_RELATION = {
    "message": "This mentorship relation is not in" " the pending state."
}
UNACCEPTED_STATE_RELATION = {
    "message": "This mentorship relation status is" " not in the accepted state."
}
MENTORSHIP_RELATION_NOT_IN_ACCEPT_STATE = {
    "message": "Mentorship relation is" " not in the accepted state."
}

# Login errors
USER_ENTERED_INCORRECT_PASSWORD = {"message": "Current password is incorrect."}
USER_ENTERED_CURRENT_PASSWORD = {
    "message": "New password should not be same " "as the current password."
}
EMAIL_EXPIRED_OR_TOKEN_IS_INVALID = {
    "message": "The confirmation link is" " invalid or the token has expired."
}
WRONG_USERNAME_OR_PASSWORD = {"message": "Username or password is wrong."}
USER_HAS_NOT_VERIFIED_EMAIL_BEFORE_LOGIN = {
    "message": "Please verify your" " email before login."
}
NAME_USERNAME_AND_PASSWORD_NOT_IN_STRING_FORMAT = {
    "message": "Name, username" " and password must be in" " string format."
}
COMMENT_NOT_IN_STRING_FORMAT = {"message": "Comment must be in string format."}
TERMS_AND_CONDITIONS_ARE_NOT_CHECKED = {
    "message": "Terms and conditions are" " not checked."
}
USER_INPUTS_SPACE_IN_PASSWORD = {"message": "Password shouldn't contain" " spaces."}
TOKEN_HAS_EXPIRED = {
    "message": "The token has expired! Please, login again or refresh it."
}
TOKEN_SENT_TO_EMAIL_OF_USER = {"message": "Token sent to the user's email."}
EMAIL_VERIFICATION_MESSAGE = {
    "message": "Check your email, a new verification" " email was sent."
}

# Success messages
TASK_WAS_ALREADY_ACHIEVED = {"message": "Task was already achieved."}
MENTORSHIP_RELATION_WAS_SENT_SUCCESSFULLY = {
    "message": "Mentorship relation" " was sent successfully."
}
MENTORSHIP_RELATION_WAS_ACCEPTED_SUCCESSFULLY = {
    "message": "Mentorship" " relation was accepted" " successfully."
}
MENTORSHIP_RELATION_WAS_DELETED_SUCCESSFULLY = {
    "message": "Mentorship" " relation was deleted" " successfully."
}
MENTORSHIP_RELATION_WAS_REJECTED_SUCCESSFULLY = {
    "message": "Mentorship" " relation was" " rejected successfully."
}
MENTORSHIP_RELATION_WAS_CANCELLED_SUCCESSFULLY = {
    "message": "Mentorship relation was cancelled successfully."
}
TASK_WAS_CREATED_SUCCESSFULLY = {"message": "Task was created successfully."}
TASK_WAS_DELETED_SUCCESSFULLY = {"message": "Task was deleted successfully."}
TASK_WAS_ACHIEVED_SUCCESSFULLY = {"message": "Task was achieved" " successfully."}
USER_WAS_CREATED_SUCCESSFULLY = {
    "message": "User was created successfully."
    "A confirmation email has been sent via"
    " email. After confirming your email you "
    "can login."
}
ACCEPT_MENTORSHIP_RELATIONS_WITH_SUCCESS = {
    "message": "Accept mentorship" " relations with success."
}
REJECTED_MENTORSHIP_RELATIONS_WITH_SUCCESS = {
    "message": "Rejected mentorship" " relations with success."
}
CANCELLED_MENTORSHIP_RELATIONS_WITH_SUCCESS = {
    "message": "Cancelled" " mentorship" " relations with success."
}
DELETED_MENTORSHIP_RELATIONS_WITH_SUCCESS = {
    "message": "Deleted mentorship" " relations with success."
}
RETURNED_PAST_MENTORSHIP_RELATIONS_WITH_SUCCESS = {
    "message": "Returned " "past mentorship " "relations with success."
}
RETURNED_CURRENT_MENTORSHIP_RELATIONS_WITH_SUCCESS = {
    "message": "Returned" " current mentorship" " relation" " with success."
}
RETURNED_PENDING_MENTORSHIP_RELATIONS_WITH_SUCCESS = {
    "message": "Returned" " pending mentorship" " relations" " with success."
}
DELETE_TASK_WITH_SUCCESS = {"message": "Delete task with success."}
UPDATED_TASK_WITH_SUCCESS = {"message": "Updated task with success."}
USER_SUCCESSFULLY_CREATED = {"message": "User successfully created."}
USER_SUCCESSFULLY_DELETED = {"message": "User was deleted successfully."}
USER_SUCCESSFULLY_UPDATED = {"message": "User was updated successfully."}
PASSWORD_SUCCESSFULLY_UPDATED = {"message": "Password was updated " "successfully."}
TASK_COMMENT_WAS_CREATED_SUCCESSFULLY = {
    "message": "Task comment was created successfully."
}
TASK_COMMENT_WAS_UPDATED_SUCCESSFULLY = {
    "message": "Task comment was updated successfully."
}
TASK_COMMENT_WAS_DELETED_SUCCESSFULLY = {
    "message": "Task comment was deleted successfully."
}
LIST_TASK_COMMENTS_WITH_SUCCESS = {
    "message": "List task comments from a mentorship relation with success."
}
GENERAL_SUCCESS_MESSAGE = {"message": "Success."}

SUCCESSFUL_REFRESH = {"message": "Successful refresh."}

SUCCESSFUL_RESPONSE = {"message": "Successful response."}

SUCCESSFUL_LOGIN = {"message": "Successful login"}
# confimation
ACCOUNT_ALREADY_CONFIRMED = {"message": "Account already confirmed."}
USER_ALREADY_CONFIRMED_ACCOUNT = {"message": "You already confirm your email."}
ACCOUNT_ALREADY_CONFIRMED_AND_THANKS = {
    "message": "You have confirmed your" " account. Thanks!"
}

# Miscellaneous
VALIDATION_ERROR = {"message": "Validation error."}
INVALID_END_DATE = {
    "message": "Validation error. End date represented by the timestamp is invalid."
}
NOT_IMPLEMENTED = {"message": "Not implemented."}
